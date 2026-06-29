#!/usr/bin/env python3
"""Audit a repository or directory for agent-usability signals.

This is a heuristic scanner. It is designed to help agents and engineers triage
large projects quickly; it does not replace manual review of real workflows.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

EXCLUDED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "env", ".tox",
    "dist", "build", "target", ".next", ".nuxt", ".cache", "__pycache__",
    "coverage", ".pytest_cache", ".mypy_cache", ".ruff_cache", "vendor",
}
ALLOWED_HIDDEN_DIRS = {".well-known", ".github", ".devcontainer", ".cursor", ".vscode"}
GENERATED_REPORT_HINTS = (
    "agent-use-report", "self-audit", "skill-validation", "web-agent-readiness",
    "generated-llms", "action-parity-inventory", "self-parity-map"
)
TEMPLATE_HINTS = ("/assets/templates/", ".template", ".tmpl", ".tpl", ".sample", ".example")

TEXT_EXTENSIONS = {
    ".md", ".mdx", ".txt", ".rst", ".py", ".js", ".jsx", ".ts", ".tsx",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".sh", ".bash",
    ".zsh", ".go", ".rs", ".java", ".kt", ".swift", ".rb", ".php", ".cs",
    ".html", ".htm", ".css", ".scss", ".graphql", ".proto", ".sql", ".xml",
    ".csv", ".dockerfile",
}
TEXT_NAMES = {
    "dockerfile", "makefile", "justfile", "rakefile", "gemfile", "procfile",
    "license", "notice", "readme", "changelog", "contributing", "agents.md",
}
MAX_READ_BYTES = 250_000


@dataclass
class Evidence:
    signal: str
    path: str
    line: Optional[int] = None
    snippet: Optional[str] = None
    kind: str = "implementation"

    def to_dict(self) -> Dict[str, object]:
        out: Dict[str, object] = {"signal": self.signal, "path": self.path, "kind": self.kind}
        if self.line is not None:
            out["line"] = self.line
        if self.snippet:
            out["snippet"] = self.snippet[:240]
        return out


@dataclass
class DimensionResult:
    name: str
    applicable: bool
    score: Optional[float]
    evidence: List[Evidence] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "applicable": self.applicable,
            "score": self.score,
            "evidence": [e.to_dict() for e in self.evidence],
            "gaps": self.gaps,
            "recommendations": self.recommendations,
            "notes": self.notes,
        }


class Inventory:
    def __init__(self, root: Path, max_files: int = 12_000, include_hidden: bool = False, include_generated: bool = False):
        self.root = root.resolve()
        self.max_files = max_files
        self.include_hidden = include_hidden
        self.include_generated = include_generated
        self.files: List[Path] = []
        self.too_many_files = False
        self._text_cache: Dict[Path, str] = {}
        self._scan()

    def _scan(self) -> None:
        count = 0
        for dirpath, dirnames, filenames in os.walk(self.root):
            current = Path(dirpath)
            filtered = []
            for dirname in dirnames:
                if dirname in EXCLUDED_DIRS:
                    continue
                if not self.include_hidden and dirname.startswith(".") and dirname not in ALLOWED_HIDDEN_DIRS:
                    continue
                filtered.append(dirname)
            dirnames[:] = filtered
            for filename in filenames:
                if count >= self.max_files:
                    self.too_many_files = True
                    return
                if not self.include_hidden and filename.startswith("."):
                    continue
                path = current / filename
                rel_low = path.relative_to(self.root).as_posix().lower()
                if not self.include_generated and any(h in rel_low for h in GENERATED_REPORT_HINTS):
                    continue
                if path.is_file():
                    self.files.append(path)
                    count += 1

    def rel(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return path.as_posix()

    def all_rel(self) -> List[str]:
        return [self.rel(p) for p in self.files]

    def is_text(self, path: Path) -> bool:
        if path.suffix.lower() in TEXT_EXTENSIONS:
            return True
        if path.name.lower() in TEXT_NAMES:
            return True
        return False

    def read_text(self, path: Path) -> str:
        if path in self._text_cache:
            return self._text_cache[path]
        try:
            if path.stat().st_size > MAX_READ_BYTES:
                return ""
            data = path.read_bytes()
            text = data.decode("utf-8", errors="replace")
        except OSError:
            text = ""
        self._text_cache[path] = text
        return text

    def evidence_kind(self, path: Path) -> str:
        rel = self.rel(path).lower()
        name = path.name.lower()
        if any(h in rel for h in GENERATED_REPORT_HINTS) or "/examples/generated-" in "/" + rel:
            return "generated"
        if any(h in "/" + rel for h in TEMPLATE_HINTS):
            return "template"
        if name in {
            "agent_use_audit.py", "audit_agent_use.py", "web_agent_readiness.py",
            "validate_skill.py", "validate_agent_assets.py", "test_agent_use_scanners.py",
            "action_parity_inventory.py", "generate_agent_assets.py", "generate_llms_txt.py",
        }:
            return "scanner"
        if rel.startswith((".well-known/", "evals/")) or name in {"agents.md", "llms.txt", "llms-full.txt"}:
            return "contract"
        if any(fnmatch.fnmatch(rel, pat) for pat in ["**/openapi.*", "openapi.*", "**/swagger.*", "swagger.*", "**/*schema*.json", "*.graphql", "**/*.proto"]):
            return "contract"
        if name in {"license", "notice", "readme", "changelog", "contributing"} or name.startswith(("readme", "changelog", "contributing")):
            return "docs"
        if rel.startswith("references/"):
            return "docs"
        if rel.startswith(("docs/", "doc/", "website/docs/", "content/docs/")) or path.suffix.lower() in {".md", ".mdx", ".rst"}:
            return "docs"
        return "implementation"

    def find_paths(self, patterns: Sequence[str], max_hits: int = 8) -> List[Evidence]:
        hits: List[Evidence] = []
        lowered = [(p, p.lower()) for p in patterns]
        for path in self.files:
            rel = self.rel(path)
            low = rel.lower()
            name_low = path.name.lower()
            for pattern, pattern_low in lowered:
                if fnmatch.fnmatch(low, pattern_low) or fnmatch.fnmatch(name_low, pattern_low):
                    hits.append(Evidence(signal=f"file matches {pattern}", path=rel, kind=self.evidence_kind(path)))
                    break
            if len(hits) >= max_hits:
                break
        return hits

    def search(self, patterns: Sequence[str], *, max_hits: int = 8, file_globs: Optional[Sequence[str]] = None, include_templates: bool = False) -> List[Evidence]:
        compiled = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in patterns]
        hits: List[Evidence] = []
        for path in self.files:
            rel = self.rel(path)
            if file_globs and not any(fnmatch.fnmatch(rel.lower(), g.lower()) for g in file_globs):
                continue
            rel_slash = "/" + rel.lower()
            if not include_templates and any(h in rel_slash for h in TEMPLATE_HINTS):
                continue
            if not self.is_text(path):
                continue
            text = self.read_text(path)
            if not text:
                continue
            lines = text.splitlines()
            for i, line in enumerate(lines, start=1):
                for regex in compiled:
                    if regex.search(line):
                        snippet = re.sub(r"\s+", " ", line.strip())
                        hits.append(Evidence(signal=regex.pattern, path=rel, line=i, snippet=snippet, kind=self.evidence_kind(path)))
                        break
                if len(hits) >= max_hits:
                    return hits
        return hits


def unique_evidence(*groups: Sequence[Evidence], limit: int = 10) -> List[Evidence]:
    seen = set()
    out: List[Evidence] = []
    for group in groups:
        for ev in group:
            key = (ev.path, ev.line, ev.signal)
            if key in seen:
                continue
            seen.add(key)
            out.append(ev)
            if len(out) >= limit:
                return out
    return out

def evidence_with_kinds(group: Sequence[Evidence], *kinds: str) -> List[Evidence]:
    allowed=set(kinds)
    return [ev for ev in group if ev.kind in allowed]

def has_kind(group: Sequence[Evidence], *kinds: str) -> bool:
    return bool(evidence_with_kinds(group, *kinds))


def clamp(score: float) -> float:
    return round(max(0.0, min(10.0, score)), 1)


def bool_score(value: bool, points: float) -> float:
    return points if value else 0.0


class Audit:
    def __init__(self, inventory: Inventory):
        self.inv = inventory
        self.signals: Dict[str, List[Evidence]] = {}
        self._collect_signals()

    def _collect_signals(self) -> None:
        inv = self.inv
        s = self.signals
        s["readme"] = inv.find_paths(["README*", "readme*"])
        s["agents"] = inv.find_paths(["AGENTS.md", "agents.md", ".github/copilot-instructions.md"])
        s["docs"] = inv.find_paths(["docs/**", "doc/**", "website/docs/**", "content/docs/**", "*.md", "*.mdx"], max_hits=12)
        s["examples"] = inv.find_paths(["examples/**", "example/**", "samples/**", "sample/**", "demo/**"], max_hits=8)
        s["contributing"] = inv.find_paths(["CONTRIBUTING*", "DEVELOPMENT*", "HACKING*", "ARCHITECTURE*"], max_hits=8)
        s["changelog"] = inv.find_paths(["CHANGELOG*", "RELEASES*", "MIGRATIONS*", "UPGRADING*"], max_hits=8)
        s["llms"] = inv.find_paths(["llms.txt", "llms-full.txt", "**/llms.txt", "**/llms-full.txt"], max_hits=8)
        s["web_discovery"] = inv.find_paths(["robots.txt", "sitemap.xml", "public/robots.txt", "public/sitemap.xml", ".well-known/**"], max_hits=12)
        s["api_specs"] = inv.find_paths([
            "openapi.*", "swagger.*", "asyncapi.*", "**/openapi.*", "**/swagger.*", "**/asyncapi.*",
            "*.graphql", "schema.graphql", "**/*.proto", "**/*.smithy", "**/*.tsp", "**/*schema*.json",
        ], max_hits=12)
        s["json_schema"] = inv.search([r'"\$schema"\s*:', r'jsonschema', r'JSON Schema'], max_hits=8)
        s["cli_markers"] = unique_evidence(
            inv.find_paths(["bin/**", "cli/**", "cmd/**", "commands/**", "src/cli*", "**/cli.*"], max_hits=8),
            inv.search([
                r"argparse", r"click\.command", r"typer\.Typer", r"commander", r"yargs", r"oclif",
                r"cobra\.Command", r"clap::Parser", r"picocli", r"console_scripts", r"\[project\.scripts\]",
                r'"bin"\s*:', r"process\.argv", r"subcommands?",
            ], max_hits=12),
            limit=14,
        )
        s["tui_markers"] = inv.search([
            r"curses", r"prompt_toolkit", r"textual", r"rich\.prompt", r"Inquirer", r"inquirer",
            r"clack", r"spinner", r"Bubble Tea", r"bubbletea", r"ratatui", r"tview", r"blessed", r"Ink",
        ], max_hits=10)
        s["api_markers"] = inv.search([
            r"@(app|router)\.(get|post|put|patch|delete)", r"app\.(get|post|put|patch|delete)\s*\(",
            r"router\.(get|post|put|patch|delete)\s*\(", r"@.*route\(", r"FastAPI\(", r"APIRouter\(",
            r"GraphQL", r"REST", r"Controller\(", r"Route\(", r"http\.HandleFunc", r"NextResponse",
            r"export\s+(async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)",
        ], max_hits=12)
        s["ui_actions"] = inv.search([
            r"onClick\s*=", r"onSubmit\s*=", r"addEventListener\(['\"]click", r"<button\b", r"<Button\b",
            r"onPressed\s*:", r"onTapGesture", r"TouchableOpacity", r"Pressable", r"button_to", r"form_with",
            r"submitButton", r"MenuItem", r"DropdownMenuItem",
        ], max_hits=14)
        s["tool_markers"] = inv.search([
            r"input_schema", r"server\.tool\(", r"\.tool\(", r"@tool", r"function_tool",
            r"StructuredTool", r"Tool\(", r"tools\s*[:=]", r"tool_choice", r"function_call",
            r"ModelContextProtocol", r"MCP", r"mcp", r"callTool", r"listTools",
        ], max_hits=14)
        s["sdk_markers"] = inv.search([
            r"class\s+.*Client", r"export\s+class\s+.*Client", r"SDK", r"client\.", r"ApiClient",
            r"package .*sdk", r"lib/.*client", r"src/.*client",
        ], max_hits=10)
        s["json_output"] = inv.search([
            r"--output", r"--format", r"--json", r"format\s*[:=].*json", r"output\s*[:=].*json",
            r"json\.dumps", r"JSON\.stringify", r"serde_json", r"application/json", r"Content-Type.*json",
        ], max_hits=12)
        s["stdout_stderr"] = inv.search([r"stderr", r"console\.error", r"eprintln!", r"sys\.stderr", r"process\.stderr"], max_hits=8)
        s["bounded_output"] = inv.search([
            r"pagination", r"paginate", r"cursor", r"next_page", r"page_size", r"per_page", r"limit\b", r"offset\b",
            r"max_results", r"fields\b", r"pageToken",
        ], max_hits=12)
        s["errors"] = inv.search([
            r"error_code", r"ErrorCode", r"correlation[_-]?id", r"request[_-]?id", r"retryable", r"retry_after",
            r"remediation", r"exit code", r"exit_code", r"status_code",
        ], max_hits=12)
        s["auth"] = inv.search([
            r"OAuth", r"OIDC", r"JWT", r"api[_ -]?key", r"token", r"scope", r"permission", r"RBAC", r"authorize",
            r"authenticated", r"authorization", r"least privilege",
        ], max_hits=12)
        s["safety"] = inv.search([
            r"dry[-_ ]?run", r"preview", r"confirm", r"approval", r"approve", r"rollback", r"undo", r"soft delete",
            r"audit log", r"audit_log", r"read[-_ ]?only", r"--yes", r"--force", r"danger", r"destructive",
        ], max_hits=14)
        s["recovery"] = inv.search([
            r"idempotenc", r"retry", r"resume", r"checkpoint", r"rollback", r"transaction", r"conflict", r"optimistic",
            r"job_id", r"status endpoint", r"partial_success", r"cursor", r"pagination", r"timeout",
        ], max_hits=14)
        s["evals_tests"] = unique_evidence(
            inv.find_paths(["tests/**", "test/**", "e2e/**", "evals/**", "fixtures/**", "goldens/**", ".github/workflows/**"], max_hits=12),
            inv.search([r"pytest", r"vitest", r"jest", r"unittest", r"playwright", r"cypress", r"eval", r"assert", r"golden"], max_hits=12),
            limit=16,
        )
        s["observability"] = inv.search([
            r"OpenTelemetry", r"otel", r"metrics", r"telemetry", r"audit", r"logging", r"logger", r"trace", r"span",
            r"correlation", r"analytics", r"event log",
        ], max_hits=12)
        s["capability_map"] = unique_evidence(
            inv.find_paths(["*capability*", "*action-parity*", "*agent*contract*", "*agent*map*"], max_hits=8),
            inv.search([r"action parity", r"context parity", r"capability map", r"agent contract", r"agent[- ]use"], max_hits=8),
            limit=10,
        )
        s["skill_markers"] = unique_evidence(
            inv.find_paths(["SKILL.md", "*/SKILL.md", "skills/**", "assets/templates/**", "references/**", "scripts/**"], max_hits=12),
            inv.search([r"^name:\s*", r"^description:\s*", r"Agent Skill", r"progressive disclosure"], max_hits=8),
            limit=12,
        )

    def build(self) -> Dict[str, object]:
        dimensions = [
            self._discoverability(),
            self._content_readability(),
            self._capability_contracts(),
            self._action_parity(),
            self._context_parity(),
            self._composability(),
            self._parseable_outputs(),
            self._safety_permissions(),
            self._recovery_resilience(),
            self._evals_observability(),
        ]
        applicable_scores = [d.score for d in dimensions if d.applicable and d.score is not None]
        overall = round(sum(applicable_scores) / len(applicable_scores) * 10) if applicable_scores else None
        score_basis = self._score_basis()
        return {
            "target": str(self.inv.root),
            "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "files_scanned": len(self.inv.files),
            "too_many_files": self.inv.too_many_files,
            "overall_score": overall,
            "grade": grade(overall),
            "confidence": self._confidence(score_basis),
            "score_basis": score_basis,
            "dimensions": [d.to_dict() for d in dimensions],
            "top_recommendations": self._top_recommendations(dimensions),
            "surface_signals": {k: len(v) for k, v in sorted(self.signals.items())},
            "notes": [
                "Heuristic scan only. Confirm findings by walking through real agent tasks.",
                "Scores omit dimensions marked not applicable.",
                "Evidence kind separates implemented/contract signals from docs, templates, generated reports, and scanner internals.",
            ],
        }

    def _score_basis(self) -> Dict[str, int]:
        counts = {"implementation": 0, "contract": 0, "docs": 0, "template": 0, "generated": 0, "scanner": 0}
        seen=set()
        for group in self.signals.values():
            for ev in group:
                key=(ev.path, ev.line, ev.signal)
                if key in seen:
                    continue
                seen.add(key)
                counts[ev.kind]=counts.get(ev.kind,0)+1
        return counts

    def _confidence(self, basis: Dict[str, int]) -> str:
        solid=basis.get("implementation",0)+basis.get("contract",0)
        weak=basis.get("docs",0)+basis.get("template",0)+basis.get("generated",0)+basis.get("scanner",0)
        if solid >= 12 and solid >= weak // 2:
            return "high"
        if solid >= 5:
            return "medium"
        return "low"

    def _discoverability(self) -> DimensionResult:
        s = self.signals
        score = 1.0
        score += bool_score(bool(s["readme"]), 2.0)
        score += bool_score(bool(s["agents"]), 1.5)
        score += bool_score(bool(s["docs"]), 1.2)
        score += bool_score(bool(s["examples"]), 1.0)
        score += bool_score(bool(s["contributing"]), 0.8)
        score += bool_score(bool(s["changelog"]), 0.7)
        score += bool_score(bool(s["llms"]), 1.0)
        score += bool_score(bool(s["web_discovery"]), 0.8)
        score += bool_score(bool(s["api_specs"] or s["cli_markers"] or s["tool_markers"]), 1.0)
        gaps: List[str] = []
        recs: List[str] = []
        if not s["agents"]:
            gaps.append("No AGENTS.md or equivalent agent-facing entry point found.")
            recs.append("Add AGENTS.md with setup, safe commands, validation, known traps, and links to machine contracts.")
        if not s["llms"] and bool(s["docs"]):
            gaps.append("Docs exist but no llms.txt was found.")
            recs.append("Add llms.txt for docs-heavy projects or websites, linking canonical guides, references, examples, auth, errors, and changelog.")
        if not s["api_specs"] and (s["api_markers"] or s["sdk_markers"]):
            gaps.append("API/SDK-like code detected but no obvious machine-readable API schema found.")
            recs.append("Publish or link OpenAPI/GraphQL/JSON Schema or equivalent capability contracts.")
        return DimensionResult(
            name="Discoverability",
            applicable=True,
            score=clamp(score),
            evidence=unique_evidence(s["readme"], s["agents"], s["docs"], s["llms"], s["api_specs"], s["cli_markers"], s["tool_markers"], limit=12),
            gaps=gaps,
            recommendations=recs,
        )

    def _content_readability(self) -> DimensionResult:
        s = self.signals
        applicable = bool(s["docs"] or s["readme"])
        if not applicable:
            return DimensionResult("Content readability", False, None, gaps=["No obvious docs or README content found."])
        score = 2.0
        score += bool_score(bool(s["readme"]), 1.5)
        score += bool_score(bool(s["docs"]), 1.5)
        score += bool_score(bool(s["examples"]), 1.3)
        score += bool_score(bool(s["changelog"]), 0.8)
        score += bool_score(bool(s["llms"]), 1.2)
        score += bool_score(bool(s["errors"]), 0.8)
        score += bool_score(bool(s["auth"]), 0.6)
        md_count = sum(1 for p in self.inv.files if p.suffix.lower() in {".md", ".mdx", ".rst"})
        score += min(1.0, md_count / 8.0)
        gaps: List[str] = []
        recs: List[str] = []
        if not s["examples"]:
            gaps.append("No examples/samples directory found.")
            recs.append("Add small runnable examples with realistic inputs and outputs.")
        if not s["errors"]:
            gaps.append("No obvious error-code, retryability, or remediation documentation found.")
            recs.append("Document error envelopes with stable codes, retryability, and remediation.")
        if not s["auth"] and (s["api_markers"] or s["tool_markers"]):
            gaps.append("Automation/API surfaces detected but auth/scopes were not obvious in docs/code signals.")
            recs.append("Document auth setup, scopes, least-privilege examples, and permission failures.")
        return DimensionResult("Content readability", True, clamp(score), unique_evidence(s["readme"], s["docs"], s["examples"], s["errors"], s["auth"], limit=12), gaps, recs)

    def _capability_contracts(self) -> DimensionResult:
        s = self.signals
        api_impl=has_kind(s["api_markers"], "implementation")
        cli_impl=has_kind(s["cli_markers"], "implementation")
        tool_impl=has_kind(s["tool_markers"], "implementation")
        sdk_impl=has_kind(s["sdk_markers"], "implementation")
        applicable = bool(api_impl or cli_impl or tool_impl or sdk_impl or s["api_specs"] or s["skill_markers"])
        if not applicable:
            return DimensionResult("Capability contracts", False, None, notes=["No obvious API/CLI/SDK/tool/skill surface detected."])
        score = 1.0
        score += bool_score(bool(s["api_specs"]), 2.2)
        score += bool_score(bool(s["json_schema"]), 1.0)
        score += bool_score(bool(cli_impl and s["json_output"]), 1.2)
        score += bool_score(bool(tool_impl), 1.4)
        score += bool_score(bool(s["skill_markers"]), 1.0)
        score += bool_score(bool(s["examples"]), 0.9)
        score += bool_score(bool(s["errors"]), 1.0)
        score += bool_score(bool(s["capability_map"]), 1.0)
        gaps: List[str] = []
        recs: List[str] = []
        if (api_impl or sdk_impl) and not s["api_specs"]:
            gaps.append("API/SDK markers exist but OpenAPI/GraphQL/protobuf/JSON Schema was not found.")
            recs.append("Add or generate a canonical API schema and link it from README/docs/llms.txt.")
        if cli_impl and not s["json_output"]:
            gaps.append("CLI markers exist but JSON/schema output signals are weak.")
            recs.append("Add --output json or --format json to data-producing CLI commands and document the response schema.")
        if tool_impl and not s["json_schema"]:
            gaps.append("Tool markers exist but explicit schema signals are limited.")
            recs.append("Add precise input schemas, response schemas, and examples for every tool.")
        return DimensionResult("Capability contracts", True, clamp(score), unique_evidence(s["api_specs"], s["json_schema"], s["cli_markers"], s["tool_markers"], s["skill_markers"], s["capability_map"], limit=14), gaps, recs)

    def _action_parity(self) -> DimensionResult:
        s = self.signals
        ui_impl=has_kind(s["ui_actions"], "implementation")
        api_impl=has_kind(s["api_markers"], "implementation")
        cli_impl=has_kind(s["cli_markers"], "implementation")
        tool_impl=has_kind(s["tool_markers"], "implementation")
        sdk_impl=has_kind(s["sdk_markers"], "implementation")
        applicable = bool(ui_impl or api_impl or cli_impl or tool_impl or sdk_impl)
        if not applicable:
            return DimensionResult("Action parity", False, None, notes=["No obvious user action or automation surface detected."])
        agent_paths = bool(api_impl or cli_impl or tool_impl or sdk_impl)
        score = 2.0 if agent_paths else 0.5
        score += bool_score(api_impl, 1.5)
        score += bool_score(cli_impl, 1.2)
        score += bool_score(tool_impl, 1.5)
        score += bool_score(sdk_impl, 0.8)
        score += bool_score(bool(s["capability_map"]), 1.3)
        score += bool_score(bool(s["safety"]), 0.8)
        score += bool_score(bool(s["recovery"]), 0.7)
        gaps: List[str] = []
        recs: List[str] = []
        if ui_impl and not agent_paths:
            gaps.append("UI action markers found, but no obvious API/CLI/SDK/tool action path was detected.")
            recs.append("Create an action parity map and expose stable agent paths for important UI workflows.")
        if agent_paths and not s["capability_map"]:
            gaps.append("Automation surfaces exist, but no capability/action-parity map was found.")
            recs.append("Add a capability map linking human workflows to agent context, actions, safety level, and recovery path.")
        return DimensionResult("Action parity", True, clamp(score), unique_evidence(s["ui_actions"], s["api_markers"], s["cli_markers"], s["tool_markers"], s["sdk_markers"], s["capability_map"], limit=14), gaps, recs)

    def _context_parity(self) -> DimensionResult:
        s = self.signals
        api_impl=has_kind(s["api_markers"], "implementation")
        cli_impl=has_kind(s["cli_markers"], "implementation")
        tool_impl=has_kind(s["tool_markers"], "implementation")
        applicable = bool(has_kind(s["ui_actions"], "implementation") or api_impl or cli_impl or tool_impl or has_kind(s["sdk_markers"], "implementation"))
        if not applicable:
            return DimensionResult("Context parity", False, None, notes=["No obvious workflow surface detected."])
        context_signals = unique_evidence(s["api_markers"], s["bounded_output"], s["auth"], s["json_schema"], s["capability_map"], s["docs"], limit=12)
        score = 1.5
        score += bool_score(bool(api_impl or tool_impl or cli_impl), 1.5)
        score += bool_score(bool(s["bounded_output"]), 1.2)
        score += bool_score(bool(s["auth"]), 1.0)
        score += bool_score(bool(s["json_schema"] or s["api_specs"]), 1.2)
        score += bool_score(bool(s["capability_map"]), 1.5)
        score += bool_score(bool(s["docs"]), 0.8)
        score += bool_score(bool(s["errors"]), 0.8)
        gaps: List[str] = []
        recs: List[str] = []
        if not s["bounded_output"]:
            gaps.append("No strong signals for pagination, limits, cursors, or field selection.")
            recs.append("Expose bounded list/search operations with pagination, filtering, and field selection.")
        if not s["capability_map"]:
            gaps.append("No explicit mapping of human-visible state to agent-readable context was found.")
            recs.append("Document where agents obtain workspace, permissions, object IDs, active filters, validation rules, and related records.")
        return DimensionResult("Context parity", True, clamp(score), context_signals, gaps, recs)

    def _composability(self) -> DimensionResult:
        s = self.signals
        api_impl=has_kind(s["api_markers"], "implementation")
        cli_impl=has_kind(s["cli_markers"], "implementation")
        tool_impl=has_kind(s["tool_markers"], "implementation")
        sdk_impl=has_kind(s["sdk_markers"], "implementation")
        applicable = bool(api_impl or cli_impl or tool_impl or sdk_impl)
        if not applicable:
            return DimensionResult("Composability and primitive quality", False, None, notes=["No obvious API/CLI/SDK/tool primitives detected."])
        score = 2.0
        score += bool_score(bool(s["api_specs"]), 1.5)
        score += bool_score(tool_impl, 1.5)
        score += bool_score(cli_impl, 1.0)
        score += bool_score(sdk_impl, 0.8)
        score += bool_score(bool(s["json_schema"]), 1.0)
        score += bool_score(bool(s["examples"]), 1.0)
        score += bool_score(bool(s["errors"]), 0.7)
        score += bool_score(bool(s["capability_map"]), 0.8)
        gaps: List[str] = []
        recs: List[str] = []
        if not s["examples"]:
            gaps.append("No examples found to show how primitives compose into workflows.")
            recs.append("Add recipes that compose small API/CLI/tool primitives for common tasks.")
        if tool_impl and not s["json_schema"]:
            gaps.append("Tool markers exist but schema signals are weak; primitives may be underspecified.")
            recs.append("Tighten tool input schemas, required fields, enums, and examples.")
        return DimensionResult("Composability and primitive quality", True, clamp(score), unique_evidence(s["api_specs"], s["tool_markers"], s["cli_markers"], s["sdk_markers"], s["examples"], limit=12), gaps, recs)

    def _parseable_outputs(self) -> DimensionResult:
        s = self.signals
        cli_impl=has_kind(s["cli_markers"], "implementation")
        applicable = bool(cli_impl or has_kind(s["api_markers"], "implementation") or has_kind(s["tool_markers"], "implementation") or has_kind(s["sdk_markers"], "implementation"))
        if not applicable:
            return DimensionResult("Parseable, bounded outputs", False, None, notes=["No obvious machine execution surface detected."])
        score = 1.0
        score += bool_score(bool(s["json_output"]), 2.0)
        score += bool_score(bool(s["stdout_stderr"]), 1.0)
        score += bool_score(bool(s["bounded_output"]), 1.5)
        score += bool_score(bool(s["errors"]), 1.5)
        score += bool_score(bool(s["json_schema"] or s["api_specs"]), 1.2)
        score += bool_score(bool(s["examples"]), 0.8)
        gaps: List[str] = []
        recs: List[str] = []
        if not s["json_output"]:
            gaps.append("No strong JSON/structured-output signal found.")
            recs.append("Add stable JSON output for CLIs/tools and response schemas for APIs.")
        if cli_impl and not s["stdout_stderr"]:
            gaps.append("CLI markers found but stdout/stderr separation signals are weak.")
            recs.append("Ensure machine data goes to stdout and diagnostics/progress/errors go to stderr.")
        if not s["errors"]:
            gaps.append("No stable error envelope/code signal found.")
            recs.append("Standardize errors with code, message, retryable, remediation, details, and correlation_id.")
        return DimensionResult("Parseable, bounded outputs", True, clamp(score), unique_evidence(s["json_output"], s["stdout_stderr"], s["bounded_output"], s["errors"], s["json_schema"], limit=14), gaps, recs)

    def _safety_permissions(self) -> DimensionResult:
        s = self.signals
        applicable = bool(has_kind(s["api_markers"], "implementation") or has_kind(s["cli_markers"], "implementation") or has_kind(s["tool_markers"], "implementation") or has_kind(s["ui_actions"], "implementation") or has_kind(s["sdk_markers"], "implementation"))
        if not applicable:
            return DimensionResult("Safety, permissions, and governance", False, None, notes=["No obvious side-effecting surface detected."])
        score = 1.0
        score += bool_score(bool(s["auth"]), 2.0)
        score += bool_score(bool(s["safety"]), 2.2)
        score += bool_score(bool(s["errors"]), 1.0)
        score += bool_score(bool(s["recovery"]), 1.0)
        score += bool_score(bool(s["docs"]), 0.8)
        score += bool_score(bool(s["observability"]), 1.0)
        gaps: List[str] = []
        recs: List[str] = []
        if not s["auth"]:
            gaps.append("No strong auth/scope/permission signal found.")
            recs.append("Document and enforce scoped credentials, read-only mode, write scopes, and permission errors.")
        if not s["safety"]:
            gaps.append("No strong dry-run, preview, approval, rollback, or audit-log signal found.")
            recs.append("Add dry-run/preview for risky actions, explicit approval gates, rollback/undo where possible, and actor audit logs.")
        return DimensionResult("Safety, permissions, and governance", True, clamp(score), unique_evidence(s["auth"], s["safety"], s["errors"], s["recovery"], s["observability"], limit=14), gaps, recs)

    def _recovery_resilience(self) -> DimensionResult:
        s = self.signals
        applicable = bool(has_kind(s["api_markers"], "implementation") or has_kind(s["cli_markers"], "implementation") or has_kind(s["tool_markers"], "implementation") or has_kind(s["sdk_markers"], "implementation"))
        if not applicable:
            return DimensionResult("Recovery and resilience", False, None, notes=["No obvious execution surface detected."])
        score = 1.0
        score += bool_score(bool(s["recovery"]), 2.5)
        score += bool_score(bool(s["bounded_output"]), 1.2)
        score += bool_score(bool(s["errors"]), 1.5)
        score += bool_score(bool(s["safety"]), 1.0)
        score += bool_score(bool(s["evals_tests"]), 1.0)
        score += bool_score(bool(s["observability"]), 0.8)
        gaps: List[str] = []
        recs: List[str] = []
        if not s["recovery"]:
            gaps.append("No strong idempotency/retry/resume/rollback/job-status signal found.")
            recs.append("Add idempotency keys for mutations, retryable error classification, job status for long operations, and rollback/resume paths.")
        if not s["bounded_output"]:
            gaps.append("No strong pagination/cursor/limit signal found.")
            recs.append("Add pagination, cursors, limits, and partial-progress information to large operations.")
        return DimensionResult("Recovery and resilience", True, clamp(score), unique_evidence(s["recovery"], s["bounded_output"], s["errors"], s["safety"], s["evals_tests"], limit=14), gaps, recs)

    def _evals_observability(self) -> DimensionResult:
        s = self.signals
        applicable = True
        score = 1.0
        score += bool_score(bool(s["evals_tests"]), 2.5)
        score += bool_score(bool(s["examples"]), 1.2)
        score += bool_score(bool(s["observability"]), 1.5)
        score += bool_score(bool(s["errors"]), 0.8)
        score += bool_score(bool(s["capability_map"]), 0.8)
        score += bool_score(bool(s["skill_markers"] and self.inv.find_paths(["evals/**"], max_hits=2)), 1.0)
        gaps: List[str] = []
        recs: List[str] = []
        if not s["evals_tests"]:
            gaps.append("No tests/evals/fixtures/CI signals found.")
            recs.append("Add task-level evals and regression tests for discovery, structured output, safety, and recovery.")
        if not s["observability"]:
            gaps.append("No strong observability/audit/telemetry signal found.")
            recs.append("Track invalid calls, errors, retries, approval requests, latency, token/context use, and final-state verification failures.")
        return DimensionResult("Evals and observability", applicable, clamp(score), unique_evidence(s["evals_tests"], s["examples"], s["observability"], s["capability_map"], limit=14), gaps, recs)

    def _top_recommendations(self, dimensions: Sequence[DimensionResult]) -> List[Dict[str, object]]:
        items: List[Dict[str, object]] = []
        for d in dimensions:
            if not d.applicable:
                continue
            severity = "low"
            if d.score is not None:
                if d.score < 4:
                    severity = "critical"
                elif d.score < 6:
                    severity = "high"
                elif d.score < 8:
                    severity = "medium"
            for rec in d.recommendations[:3]:
                items.append({"dimension": d.name, "severity": severity, "recommendation": rec, "score": d.score})
        if not self.signals["examples"]:
            items.append({"dimension": "Content readability", "severity": "medium", "recommendation": "Add at least one small runnable example or task recipe.", "score": 7})
        if not self.signals["web_discovery"] and self.signals["llms"]:
            items.append({"dimension": "Discoverability", "severity": "low", "recommendation": "llms.txt exists but no local web discovery files were found; add .well-known, robots, or sitemap when this package is published as web docs.", "score": 8})
        if self.signals["api_specs"] and not self.signals["evals_tests"]:
            items.append({"dimension": "Evals and observability", "severity": "medium", "recommendation": "API contracts exist but no tests/evals signal was found; add a drift or schema coverage check.", "score": 7})
        rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        items.sort(key=lambda x: (rank.get(str(x["severity"]), 9), float(x["score"] if x["score"] is not None else 10)))
        return items[:12]


def grade(score: Optional[int]) -> Optional[str]:
    if score is None:
        return None
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def render_markdown(report: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append(f"# Agent-use audit: `{report['target']}`")
    lines.append("")
    overall = report.get("overall_score")
    grade_value = report.get("grade")
    lines.append(f"Overall: **{overall}/100** ({grade_value})" if overall is not None else "Overall: not scored")
    if report.get("confidence"):
        lines.append(f"Confidence: **{report['confidence']}**")
    lines.append(f"Files scanned: {report['files_scanned']}")
    if report.get("too_many_files"):
        lines.append("Note: scan stopped at the maximum file limit; results are partial.")
    lines.append("")
    lines.append("## Scores")
    lines.append("")
    lines.append("| Dimension | Applicable | Score | Main gaps |")
    lines.append("| --- | --- | ---: | --- |")
    for dim in report["dimensions"]:  # type: ignore[index]
        score = "—" if dim["score"] is None else str(dim["score"])
        gaps = "; ".join(dim["gaps"][:2]) if dim["gaps"] else "—"
        lines.append(f"| {dim['name']} | {dim['applicable']} | {score} | {gaps} |")
    lines.append("")
    lines.append("## Top recommendations")
    lines.append("")
    top = report.get("top_recommendations", [])
    if top:
        for i, rec in enumerate(top, start=1):
            lines.append(f"{i}. **{rec['severity']} / {rec['dimension']}**: {rec['recommendation']}")
    else:
        lines.append("No recommendations generated by the heuristic scan.")
    lines.append("")
    lines.append("## Evidence by dimension")
    for dim in report["dimensions"]:  # type: ignore[index]
        lines.append("")
        lines.append(f"### {dim['name']}")
        if not dim["applicable"]:
            notes = "; ".join(dim.get("notes", [])) or "Not applicable."
            lines.append(notes)
            continue
        if dim["evidence"]:
            lines.append("Evidence:")
            for ev in dim["evidence"][:8]:
                loc = ev["path"]
                if "line" in ev:
                    loc += f":{ev['line']}"
                snippet = f" — {ev['snippet']}" if ev.get("snippet") else ""
                lines.append(f"- `{loc}` ({ev['kind']}; {ev['signal']}){snippet}")
        else:
            lines.append("No strong evidence found by the scanner.")
        if dim["recommendations"]:
            lines.append("Recommendations:")
            for rec in dim["recommendations"]:
                lines.append(f"- {rec}")
    lines.append("")
    lines.append("## Surface signal counts")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(report.get("surface_signals", {}), indent=2, sort_keys=True))
    lines.append("```")
    if report.get("score_basis"):
        lines.append("")
        lines.append("## Score basis")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(report.get("score_basis", {}), indent=2, sort_keys=True))
        lines.append("```")
    lines.append("")
    lines.append("Heuristic scan only. Confirm findings by walking through real agent tasks and the action/context parity map.")
    return "\n".join(lines) + "\n"


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit a repository/directory for agent-usefulness signals.")
    parser.add_argument("path", nargs="?", help="Repository or directory to scan. You can also use --root.")
    parser.add_argument("--root", help="Repository or directory to scan; alias for positional path.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format for stdout or --output.")
    parser.add_argument("--output", help="Write report to this path instead of stdout.")
    parser.add_argument("--json-output", help="Also write the raw JSON report to this path.")
    parser.add_argument("--max-files", type=int, default=12_000, help="Maximum files to scan before stopping. Default: 12000.")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden files and directories except excluded build/dependency dirs. Common agent dirs such as .well-known and .github are scanned by default.")
    parser.add_argument("--include-generated", action="store_true", help="Include generated reports/examples that are skipped by default to avoid circular self-scoring.")
    parser.add_argument("--markdown", action="store_true", help="Alias for --format markdown.")
    parser.add_argument("--json", action="store_true", dest="json_format", help="Alias for --format json.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    chosen = args.root or args.path
    if not chosen:
        print(json.dumps({"error": {"code": "missing_path", "message": "provide a positional path or --root"}}), file=sys.stderr)
        return 2
    root = Path(chosen)
    if not root.exists():
        print(json.dumps({"error": {"code": "path_not_found", "message": f"Path does not exist: {root}"}}), file=sys.stderr)
        return 2
    if not root.is_dir():
        print(json.dumps({"error": {"code": "not_a_directory", "message": f"Expected a directory: {root}"}}), file=sys.stderr)
        return 2

    inv = Inventory(root, max_files=args.max_files, include_hidden=args.include_hidden, include_generated=args.include_generated)
    report = Audit(inv).build()
    output_format = "json" if args.json_format else "markdown" if args.markdown else args.format
    rendered = json.dumps(report, indent=2, sort_keys=False) + "\n" if output_format == "json" else render_markdown(report)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    if args.json_output:
        Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_output).write_text(json.dumps(report, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
