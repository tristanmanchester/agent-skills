#!/usr/bin/env python3
"""Agent safety wrapper for Meta's official Ads CLI.

This wrapper is intentionally small. It does not implement the Meta Marketing API.
It helps AI agents use the official `meta ads ...` CLI safely by:

- classifying command risk;
- preferring JSON output;
- refusing writes without explicit approval;
- requiring extra flags for activation, budget, and destructive operations;
- linting and executing reviewable JSON plans;
- redacting obvious secrets in logs.

The installed Meta CLI remains the source of truth for command syntax.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

EXIT_OK = 0
EXIT_BAD_ARGS = 2
EXIT_AUTH = 3
EXIT_API = 4
EXIT_SAFETY = 6
EXIT_CLI_MISSING = 7
EXIT_PLAN = 8
EXIT_TIMEOUT = 9

READ_ACTIONS = {
    "list", "get", "show", "status", "inspect", "preview", "previews",
    "help", "search", "find", "info", "describe", "export",
}

WRITE_ACTIONS = {
    "create", "update", "delete", "remove", "connect", "disconnect", "upload",
    "pause", "activate", "archive", "set", "assign", "unassign", "import",
}

BUDGET_TOKENS = {
    "--daily-budget", "--lifetime-budget", "--budget", "--bid-amount",
    "--bid", "--spend-cap", "daily_budget", "lifetime_budget",
    "budget", "bid_amount", "spend_cap",
}

ACTIVE_VALUES = {"ACTIVE", "active"}
DESTRUCTIVE_ACTIONS = {"delete", "remove"}
SENSITIVE_FLAG_PATTERNS = [
    re.compile(r"(--?(?:access[-_]?token|token|app[-_]?secret|secret|password|cookie))(=)?(.+)?", re.I),
]
SENSITIVE_ENV_KEYS = ("TOKEN", "SECRET", "PASSWORD", "COOKIE", "APP_SECRET")

DEFAULT_LOG = Path(os.getenv("META_ADS_AGENT_LOG", ".meta-ads-agent/runs.jsonl"))


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def emit(payload: Dict[str, Any], exit_code: int = 0) -> int:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return exit_code


def redact_token(token: str) -> str:
    if not token:
        return token
    for pattern in SENSITIVE_FLAG_PATTERNS:
        m = pattern.match(token)
        if m:
            flag = m.group(1)
            if m.group(2):
                return f"{flag}=<REDACTED>"
            return flag
    if len(token) > 32 and re.search(r"[A-Za-z]", token) and re.search(r"\d", token):
        return token[:6] + "…<REDACTED>"
    return token


def redact_command(cmd: Sequence[str]) -> List[str]:
    redacted: List[str] = []
    skip_next = False
    sensitive_flags = {"--access-token", "--token", "--app-secret", "--secret", "--password", "--cookie"}
    for i, part in enumerate(cmd):
        if skip_next:
            redacted.append("<REDACTED>")
            skip_next = False
            continue
        lower = part.lower()
        if lower in sensitive_flags:
            redacted.append(part)
            skip_next = True
            continue
        redacted.append(redact_token(part))
    return redacted


def scrub_env(env: Dict[str, str]) -> Dict[str, str]:
    safe: Dict[str, str] = {}
    for key, value in env.items():
        if any(marker in key.upper() for marker in SENSITIVE_ENV_KEYS):
            safe[key] = "<SET>" if value else "<EMPTY>"
    return safe


def has_output_flag(cmd: Sequence[str]) -> bool:
    return "--output" in cmd or "-o" in cmd or any(x.startswith("--output=") for x in cmd)


def normalise_meta_command(cmd: Sequence[str], prefer_json: bool = True) -> List[str]:
    """Return a command with JSON output inserted when safe.

    Meta's public examples use `meta --output json ads ...`. If the installed CLI
    changes flag placement, users should follow `meta --help`.
    """
    cmd = list(cmd)
    if not cmd:
        raise ValueError("Empty command")
    if cmd[0] != "meta":
        return cmd
    lowered = [x.lower() for x in cmd]
    if "--help" in lowered or "-h" in lowered or "help" in lowered:
        return cmd
    if prefer_json and "ads" in cmd and not has_output_flag(cmd):
        return ["meta", "--output", "json", *cmd[1:]]
    return cmd


def split_command(raw: str) -> List[str]:
    try:
        return shlex.split(raw)
    except ValueError as exc:
        raise ValueError(f"Could not parse command string: {exc}") from exc


def strip_remainder_dash(cmd: Sequence[str]) -> List[str]:
    cmd = list(cmd)
    if cmd and cmd[0] == "--":
        return cmd[1:]
    return cmd


def command_from_any(value: Any) -> List[str]:
    if isinstance(value, list):
        if not all(isinstance(x, str) for x in value):
            raise ValueError("Command array must contain only strings")
        return list(value)
    if isinstance(value, str):
        return split_command(value)
    raise ValueError("Command must be a string or array of strings")


def find_ads_resource_action(cmd: Sequence[str]) -> Tuple[Optional[str], Optional[str]]:
    """Best-effort parse of `meta [global flags] ads [ads flags] resource action`.

    This parser is intentionally conservative. It ignores flag values and returns
    the first two non-flag tokens after `ads`.
    """
    if "ads" not in cmd:
        return None, None
    idx = list(cmd).index("ads") + 1
    positional: List[str] = []
    i = idx
    while i < len(cmd):
        part = cmd[i]
        if part == "--":
            i += 1
            continue
        if part.startswith("-"):
            # Skip likely flag value when provided as two tokens. This is imperfect,
            # but sufficient for risk classification.
            if "=" not in part and i + 1 < len(cmd) and not cmd[i + 1].startswith("-"):
                # Some flags are booleans; if we skip a positional accidentally,
                # command classification remains conservative via token scanning.
                flag = part.lower()
                if flag in {"--ad-account-id", "--account", "--business-id", "--output", "-o", "--limit"}:
                    i += 2
                    continue
            i += 1
            continue
        positional.append(part)
        if len(positional) >= 2:
            break
        i += 1
    resource = positional[0] if positional else None
    action = positional[1] if len(positional) > 1 else None
    return resource, action


def classify_command(cmd: Sequence[str]) -> Dict[str, Any]:
    cmd = list(cmd)
    lowered = [x.lower() for x in cmd]
    resource, action = find_ads_resource_action(cmd)
    action_lower = (action or "").lower()

    is_meta_ads = bool(cmd and cmd[0] == "meta" and "ads" in cmd)
    is_help = any(x in {"--help", "-h", "help"} for x in lowered)

    write_signals: List[str] = []
    high_risk: List[str] = []

    if action_lower in WRITE_ACTIONS:
        write_signals.append(f"action:{action_lower}")
    if action_lower in DESTRUCTIVE_ACTIONS:
        high_risk.append("destructive")
    if action_lower == "activate":
        high_risk.append("active")

    for i, token in enumerate(cmd):
        lower = token.lower()
        upper = token.upper()
        if lower in BUDGET_TOKENS or any(lower.startswith(x + "=") for x in BUDGET_TOKENS):
            write_signals.append(f"budget-token:{token}")
            high_risk.append("budget")
        if lower == "--status" and i + 1 < len(cmd):
            write_signals.append("status-update")
            if cmd[i + 1] in ACTIVE_VALUES:
                high_risk.append("active")
        if lower.startswith("--status="):
            write_signals.append("status-update")
            if lower.split("=", 1)[1].upper() == "ACTIVE":
                high_risk.append("active")
        if upper == "ACTIVE" and ("--status" in lowered or action_lower == "activate"):
            high_risk.append("active")
        if lower == "--force":
            high_risk.append("destructive")
        if lower in {"--targeting", "--targeting-countries", "--special-ad-category", "--special-ad-categories"}:
            write_signals.append(f"targeting-token:{token}")
        if lower in {"--image", "--video", "--catalog-id", "--dataset-id", "--pixel-id"}:
            write_signals.append(f"asset-or-tracking-token:{token}")

    allowed_meta_diagnostic = bool(
        cmd and cmd[0] == "meta" and (
            is_help
            or lowered in (["meta", "auth", "status"], ["meta", "auth", "--help"], ["meta", "--help"])
            or (len(lowered) >= 2 and lowered[1] in {"auth", "--help", "-h"})
        )
    )

    if not is_meta_ads and not allowed_meta_diagnostic:
        risk = "non_meta"
    elif is_help or allowed_meta_diagnostic:
        risk = "read"
    elif write_signals:
        risk = "write"
    elif action_lower in READ_ACTIONS or action_lower == "":
        risk = "read"
    else:
        # Unknown Meta Ads action: be conservative if it is not a known read.
        risk = "unknown"

    high_risk = sorted(set(high_risk))
    if high_risk and risk == "write":
        # Keep primary risk as write; include subtypes separately.
        pass

    return {
        "command": redact_command(cmd),
        "is_meta_ads": is_meta_ads,
        "resource": resource,
        "action": action,
        "risk": risk,
        "write_signals": sorted(set(write_signals)),
        "high_risk": high_risk,
        "requires_approval": risk in {"write", "unknown"},
        "requires_allow_active": "active" in high_risk,
        "requires_allow_budget": "budget" in high_risk,
        "requires_allow_destructive": "destructive" in high_risk,
    }


def check_safety(classification: Dict[str, Any], approved: Optional[str], allow_active: bool, allow_budget: bool, allow_destructive: bool, allow_unknown: bool) -> Optional[str]:
    risk = classification["risk"]
    if risk == "non_meta":
        return "Refusing to run non-`meta ads` command through this guard. Use --allow-unknown only for Meta help/diagnostic commands, or run outside the guard."
    if risk == "unknown" and not allow_unknown:
        return "Command action is unknown to the guard. Run `classify`, check `meta ... --help`, then rerun with --allow-unknown only if safe."
    if classification["requires_approval"] and not approved:
        return "Write or unknown-risk command requires --approved with a specific user approval string."
    if classification["requires_allow_active"] and not allow_active:
        return "Activation requires --allow-active plus explicit approval."
    if classification["requires_allow_budget"] and not allow_budget:
        return "Budget/bid/spend change requires --allow-budget plus explicit approval."
    if classification["requires_allow_destructive"] and not allow_destructive:
        return "Destructive command requires --allow-destructive plus explicit approval."
    return None


def parse_stdout(stdout: str) -> Tuple[Any, str]:
    text = stdout.strip()
    if not text:
        return None, "empty"
    try:
        return json.loads(text), "json"
    except json.JSONDecodeError:
        return text, "text"


def append_log(record: Dict[str, Any], log_path: Path = DEFAULT_LOG) -> None:
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
    except Exception:
        # Logging should never cause an ads operation to fail after it has run.
        pass


def run_subprocess(cmd: Sequence[str], timeout: int) -> Dict[str, Any]:
    started = time.time()
    try:
        proc = subprocess.run(
            list(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )
        parsed, output_type = parse_stdout(proc.stdout)
        return {
            "exit_code": proc.returncode,
            "stdout_type": output_type,
            "stdout": parsed,
            "stderr": proc.stderr.strip(),
            "duration_seconds": round(time.time() - started, 3),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "exit_code": EXIT_TIMEOUT,
            "stdout_type": "timeout",
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or f"Timed out after {timeout} seconds",
            "duration_seconds": round(time.time() - started, 3),
        }
    except FileNotFoundError:
        return {
            "exit_code": EXIT_CLI_MISSING,
            "stdout_type": "missing_cli",
            "stdout": None,
            "stderr": "`meta` executable was not found on PATH.",
            "duration_seconds": round(time.time() - started, 3),
        }


def command_doctor(args: argparse.Namespace) -> int:
    meta_path = shutil.which("meta")
    payload: Dict[str, Any] = {
        "ok": bool(meta_path),
        "meta_path": meta_path,
        "checked_at": now_iso(),
        "sensitive_env_presence": scrub_env(dict(os.environ)),
        "next_steps": [],
    }
    if not meta_path:
        payload["next_steps"].append("Install Meta Ads CLI: python3.12 -m pip install meta-ads")
        return emit(payload, EXIT_CLI_MISSING)

    for label, cmd in [
        ("meta_help", ["meta", "--help"]),
        ("ads_help", ["meta", "ads", "--help"]),
        ("auth_status", ["meta", "auth", "status"]),
    ]:
        result = run_subprocess(cmd, timeout=args.timeout)
        payload[label] = {
            "command": cmd,
            "exit_code": result["exit_code"],
            "stdout_type": result["stdout_type"],
            "stdout_preview": str(result["stdout"])[:800] if result["stdout"] is not None else None,
            "stderr_preview": str(result["stderr"])[:800] if result["stderr"] else "",
        }
    if payload.get("auth_status", {}).get("exit_code") not in (0, None):
        payload["next_steps"].append("Resolve auth before write operations. Run `meta auth status` and follow official setup/configuration docs.")
    return emit(payload, 0 if payload["ok"] else EXIT_CLI_MISSING)


def command_classify(args: argparse.Namespace) -> int:
    cmd = strip_remainder_dash(args.command)
    if not cmd:
        return emit({"ok": False, "error": "No command supplied after --"}, EXIT_BAD_ARGS)
    normalised = normalise_meta_command(cmd, prefer_json=not args.no_json)
    payload = classify_command(normalised)
    payload["ok"] = True
    payload["normalised_command"] = redact_command(normalised)
    return emit(payload)


def command_run(args: argparse.Namespace) -> int:
    cmd_raw = strip_remainder_dash(args.command)
    if not cmd_raw:
        return emit({"ok": False, "error": "No command supplied after --"}, EXIT_BAD_ARGS)
    cmd = normalise_meta_command(cmd_raw, prefer_json=not args.no_json)
    classification = classify_command(cmd)
    problem = check_safety(
        classification,
        approved=args.approved or os.getenv("META_ADS_AGENT_APPROVED"),
        allow_active=args.allow_active,
        allow_budget=args.allow_budget,
        allow_destructive=args.allow_destructive,
        allow_unknown=args.allow_unknown,
    )
    if problem:
        return emit({
            "ok": False,
            "error": problem,
            "classification": classification,
            "would_run": redact_command(cmd),
        }, EXIT_SAFETY)

    result = run_subprocess(cmd, timeout=args.timeout)
    payload = {
        "ok": result["exit_code"] == 0,
        "ran_at": now_iso(),
        "command": redact_command(cmd),
        "classification": classification,
        "result": result,
    }
    append_log({
        "ran_at": payload["ran_at"],
        "command": payload["command"],
        "classification": classification,
        "exit_code": result["exit_code"],
        "duration_seconds": result["duration_seconds"],
        "approved": bool(args.approved or os.getenv("META_ADS_AGENT_APPROVED")),
    })

    if args.output_file:
        out_path = Path(args.output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        payload["saved_to"] = str(out_path)
    return emit(payload, result["exit_code"] if result["exit_code"] else 0)


def load_plan(path: str) -> Dict[str, Any]:
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"Could not read JSON plan {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Plan must be a JSON object")
    if "commands" not in data or not isinstance(data["commands"], list):
        raise ValueError("Plan must contain a commands array")
    return data


def lint_plan_data(plan: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    commands_out: List[Dict[str, Any]] = []
    has_write = False
    high_risk: List[str] = []

    for idx, step in enumerate(plan.get("commands", [])):
        if not isinstance(step, dict):
            issues.append({"step": idx, "severity": "error", "message": "Each command step must be an object"})
            continue
        try:
            cmd = command_from_any(step.get("command"))
        except Exception as exc:
            issues.append({"step": idx, "severity": "error", "message": str(exc)})
            continue
        normalised = normalise_meta_command(cmd, prefer_json=step.get("prefer_json", True))
        cls = classify_command(normalised)
        if cls["risk"] in {"write", "unknown"}:
            has_write = True
        high_risk.extend(cls.get("high_risk", []))
        commands_out.append({
            "step": idx,
            "id": step.get("id", f"step-{idx}"),
            "intent": step.get("intent"),
            "command": redact_command(normalised),
            "classification": cls,
        })
        if cls["risk"] == "non_meta":
            issues.append({"step": idx, "severity": "error", "message": "Non-meta command in plan"})
        if cls["risk"] == "unknown" and not step.get("allow_unknown"):
            issues.append({"step": idx, "severity": "warning", "message": "Unknown action; verify with CLI help"})
        if cls["requires_allow_active"] and not plan.get("allow_active") and not step.get("allow_active"):
            issues.append({"step": idx, "severity": "error", "message": "Activation step needs allow_active"})
        if cls["requires_allow_budget"] and not plan.get("allow_budget") and not step.get("allow_budget"):
            issues.append({"step": idx, "severity": "error", "message": "Budget/bid step needs allow_budget"})
        if cls["requires_allow_destructive"] and not plan.get("allow_destructive") and not step.get("allow_destructive"):
            issues.append({"step": idx, "severity": "error", "message": "Destructive step needs allow_destructive"})

    if has_write and not plan.get("requires_user_approval", True):
        issues.append({"step": None, "severity": "error", "message": "Write plan cannot set requires_user_approval=false"})

    return {
        "ok": not any(i["severity"] == "error" for i in issues),
        "goal": plan.get("goal"),
        "risk_summary": {
            "has_write_or_unknown": has_write,
            "high_risk": sorted(set(high_risk)),
        },
        "issues": issues,
        "commands": commands_out,
    }


def command_lint_plan(args: argparse.Namespace) -> int:
    try:
        plan = load_plan(args.plan)
        result = lint_plan_data(plan)
    except Exception as exc:
        return emit({"ok": False, "error": str(exc)}, EXIT_PLAN)
    return emit(result, 0 if result["ok"] else EXIT_PLAN)


def command_run_plan(args: argparse.Namespace) -> int:
    try:
        plan = load_plan(args.plan)
        lint = lint_plan_data(plan)
    except Exception as exc:
        return emit({"ok": False, "error": str(exc)}, EXIT_PLAN)
    if not lint["ok"]:
        return emit({"ok": False, "error": "Plan failed lint", "lint": lint}, EXIT_PLAN)

    needs_approval = lint["risk_summary"]["has_write_or_unknown"]
    approved = args.approved or os.getenv("META_ADS_AGENT_APPROVED")
    if needs_approval and not approved:
        return emit({"ok": False, "error": "Plan contains write/unknown-risk commands and requires --approved", "lint": lint}, EXIT_SAFETY)

    results: List[Dict[str, Any]] = []
    overall_ok = True
    for idx, step in enumerate(plan.get("commands", [])):
        cmd = normalise_meta_command(command_from_any(step["command"]), prefer_json=step.get("prefer_json", True))
        cls = classify_command(cmd)
        problem = check_safety(
            cls,
            approved=approved,
            allow_active=args.allow_active or plan.get("allow_active", False) or step.get("allow_active", False),
            allow_budget=args.allow_budget or plan.get("allow_budget", False) or step.get("allow_budget", False),
            allow_destructive=args.allow_destructive or plan.get("allow_destructive", False) or step.get("allow_destructive", False),
            allow_unknown=args.allow_unknown or step.get("allow_unknown", False),
        )
        if problem:
            overall_ok = False
            results.append({"step": idx, "id": step.get("id"), "ok": False, "error": problem, "classification": cls})
            if args.stop_on_error:
                break
            continue
        result = run_subprocess(cmd, timeout=args.timeout)
        ok = result["exit_code"] == 0
        overall_ok = overall_ok and ok
        step_payload = {
            "step": idx,
            "id": step.get("id", f"step-{idx}"),
            "intent": step.get("intent"),
            "ok": ok,
            "command": redact_command(cmd),
            "classification": cls,
            "result": result,
        }
        results.append(step_payload)
        append_log({
            "ran_at": now_iso(),
            "plan": args.plan,
            "step": idx,
            "id": step_payload["id"],
            "command": step_payload["command"],
            "classification": cls,
            "exit_code": result["exit_code"],
            "duration_seconds": result["duration_seconds"],
            "approved": bool(approved),
        })
        if args.stop_on_error and not ok:
            break

    payload = {"ok": overall_ok, "plan": args.plan, "lint": lint, "results": results}
    if args.output_file:
        out_path = Path(args.output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        payload["saved_to"] = str(out_path)
    return emit(payload, 0 if overall_ok else EXIT_API)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safe agent wrapper for Meta Ads CLI")
    sub = parser.add_subparsers(dest="command_name", required=True)

    p = sub.add_parser("doctor", help="Check Meta CLI availability and auth status")
    p.add_argument("--timeout", type=int, default=20)
    p.set_defaults(func=command_doctor)

    p = sub.add_parser("classify", help="Classify risk of a meta ads command")
    p.add_argument("--no-json", action="store_true", help="Do not insert --output json")
    p.add_argument("command", nargs=argparse.REMAINDER, help="Command after --, e.g. -- meta ads campaign list")
    p.set_defaults(func=command_classify)

    p = sub.add_parser("run", help="Run one meta ads command with safety gates")
    p.add_argument("--approved", help="Specific user approval text required for writes")
    p.add_argument("--allow-active", action="store_true")
    p.add_argument("--allow-budget", action="store_true")
    p.add_argument("--allow-destructive", action="store_true")
    p.add_argument("--allow-unknown", action="store_true")
    p.add_argument("--no-json", action="store_true", help="Do not insert --output json")
    p.add_argument("--timeout", type=int, default=120)
    p.add_argument("--output-file", help="Save full wrapper result JSON to file")
    p.add_argument("command", nargs=argparse.REMAINDER, help="Command after --, e.g. -- meta ads campaign list")
    p.set_defaults(func=command_run)

    p = sub.add_parser("lint-plan", help="Lint a JSON command plan")
    p.add_argument("plan")
    p.set_defaults(func=command_lint_plan)

    p = sub.add_parser("run-plan", help="Run a JSON command plan")
    p.add_argument("plan")
    p.add_argument("--approved", help="Specific user approval text required for write plans")
    p.add_argument("--allow-active", action="store_true")
    p.add_argument("--allow-budget", action="store_true")
    p.add_argument("--allow-destructive", action="store_true")
    p.add_argument("--allow-unknown", action="store_true")
    p.add_argument("--timeout", type=int, default=120)
    p.add_argument("--output-file")
    p.add_argument("--stop-on-error", action=argparse.BooleanOptionalAction, default=True)
    p.set_defaults(func=command_run_plan)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        return emit({"ok": False, "error": "Interrupted"}, 130)
    except Exception as exc:
        return emit({"ok": False, "error": str(exc)}, EXIT_BAD_ARGS)


if __name__ == "__main__":
    raise SystemExit(main())
