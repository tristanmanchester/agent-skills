#!/usr/bin/env python3
"""Render a Markdown report from collected OpenClaw audit artefacts.

This script is intentionally schema-tolerant: it looks for common fields in the
`openclaw security audit --json` output and generates a report skeleton that a
human (or the agent) can refine.

Usage:
  python3 scripts/render_report.py --input ./openclaw-audit/openclaw-audit-<ts> --output ./openclaw-security-report.md
"""

from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

SEV_ORDER = {"critical": 0, "high": 1, "warn": 2, "warning": 2, "medium": 3, "low": 4, "info": 5}

def load_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def find_first(existing: List[Path]) -> Path | None:
    for p in existing:
        if p.exists():
            return p
    return None

def normalise_sev(s: str) -> str:
    s = (s or "").strip().lower()
    if s in ("warn", "warning"):
        return "medium"
    if s in ("crit",):
        return "critical"
    return s or "unknown"

def extract_findings(obj: Any) -> List[Dict[str, Any]]:
    # We don't know exact schema; try a few.
    if obj is None:
        return []
    if isinstance(obj, dict):
        for key in ("findings", "checks", "results", "issues"):
            if key in obj and isinstance(obj[key], list):
                return [x for x in obj[key] if isinstance(x, dict)]
        # some formats may be a dict of checkId -> detail
        # convert to list
        if all(isinstance(v, dict) for v in obj.values()):
            out = []
            for k, v in obj.items():
                v = dict(v)
                v.setdefault("checkId", k)
                out.append(v)
            return out
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []

def sort_key(f: Dict[str, Any]) -> Tuple[int, str]:
    sev = normalise_sev(str(f.get("severity") or f.get("level") or f.get("risk") or "unknown"))
    return (SEV_ORDER.get(sev, 99), str(f.get("checkId") or f.get("id") or ""))

def pick_text(f: Dict[str, Any]) -> str:
    for k in ("title", "summary", "message", "description"):
        v = f.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return "(no summary provided)"

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Folder produced by collect_openclaw_audit.sh")
    ap.add_argument("--output", required=True, help="Markdown report path")
    args = ap.parse_args()

    in_dir = Path(args.input)
    out_path = Path(args.output)

    audit_json = find_first([
        in_dir / "openclaw_security_audit_deep_json.txt",
        in_dir / "openclaw_security_audit_json.txt",
    ])

    findings: List[Dict[str, Any]] = []
    raw_obj = None

    if audit_json and audit_json.exists():
        txt = audit_json.read_text(encoding="utf-8", errors="replace")
        # The file includes a leading "$ cmd" line; try to find first JSON char.
        idx = txt.find("{")
        if idx == -1:
            idx = txt.find("[")
        if idx != -1:
            raw_obj = load_json_file(Path("/dev/null"))  # placeholder
            try:
                raw_obj = json.loads(txt[idx:])
            except Exception:
                raw_obj = None
        findings = extract_findings(raw_obj)

    findings_sorted = sorted(findings, key=sort_key)

    # Basic context
    version_file = in_dir / "openclaw_version.txt"
    version = "(unknown)"
    if version_file.exists():
        version = version_file.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-1]

    report_lines: List[str] = []
    report_lines.append("# OpenClaw Security Audit Report\n")
    report_lines.append("## Executive summary\n")
    report_lines.append(f"- **OpenClaw version:** {version}\n")
    report_lines.append("- **Overall risk rating:** (fill in)\n")
    report_lines.append("- **Most urgent issues:** (fill in)\n\n")

    report_lines.append("## Findings (from `openclaw security audit --json`)\n")
    if not findings_sorted:
        report_lines.append("No findings were parsed from the JSON output. Attach `openclaw_security_audit_json.txt` and review manually.\n\n")
    else:
        report_lines.append("| Severity | Check ID | Summary | Recommended fix (fill in) | Verify (fill in) |\n")
        report_lines.append("|---|---|---|---|---|\n")
        for f in findings_sorted[:200]:
            sev = normalise_sev(str(f.get("severity") or f.get("level") or f.get("risk") or "unknown"))
            check_id = str(f.get("checkId") or f.get("id") or "").strip() or "(unknown)"
            summary = pick_text(f).replace("\n", " ").replace("|", "\\|")
            report_lines.append(f"| {sev} | {check_id} | {summary} |  |  |\n")
        report_lines.append("\n")

    report_lines.append("## Remediation plan\n\n")
    report_lines.append("### Phase 1 — Critical fixes (same day)\n\n1. \n\n")
    report_lines.append("### Phase 2 — Hardening (this week)\n\n1. \n\n")
    report_lines.append("### Phase 3 — Operational practices (ongoing)\n\n- Update cadence\n- Token rotation\n- Log/transcript retention\n\n")
    report_lines.append("## Appendix\n\n- Collected artefacts live in the input folder.\n")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(report_lines), encoding="utf-8")

if __name__ == "__main__":
    main()
