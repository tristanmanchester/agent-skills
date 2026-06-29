#!/usr/bin/env python3
"""Extract candidate UI actions and agent action paths for parity review.

This does not prove parity. It creates a useful capability-map starter from
frontend action markers, backend/API routes, CLI commands, and tool definitions.
"""
from __future__ import annotations
import argparse, csv, fnmatch, os, re, sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

SKIP={".git","node_modules","dist","build","coverage","__pycache__",".venv","venv",".next","target"}
TEXT={".js",".jsx",".ts",".tsx",".vue",".svelte",".astro",".html",".py",".rb",".go",".rs",".php",".java",".kt",".cs",".swift",".dart",".md",".json",".yaml",".yml",".sh"}
PATTERNS={
 "ui_action":[r"\bonClick\b",r"\bonSubmit\b",r"<button\b",r"Button\(",r"addEventListener\(['\"]click",r"onPressed\b",r"onTap\b"],
 "api_route":[r"app\.(get|post|put|patch|delete)\s*\(",r"router\.(get|post|put|patch|delete)\s*\(",r"@(?:app|router)\.(get|post|put|patch|delete)",r"fetch\s*\(",r"axios\.(get|post|put|patch|delete)"],
 "cli_command":[r"argparse",r"click\.command",r"commander\(",r"cobra\.Command",r"yargs",r"clap::",r"process\.argv"],
 "tool_definition":[r"\btool\s*\(",r"StructuredTool",r"function_call",r"tools\s*[:=]",r"McpServer",r"server\.tool",r"input_schema",r"inputSchema"],
 "context_injection":[r"system prompt",r"systemPrompt",r"runtime context",r"context injection",r"available resources",r"workspace state",r"permissions"],
}
@dataclass
class Hit:
    category:str; path:str; line:int; snippet:str

def iter_files(root: Path):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP]
        for f in fns:
            p=Path(dp)/f
            if p.suffix.lower() in TEXT or p.name in {"Dockerfile","Makefile","AGENTS.md","SKILL.md"}: yield p

def scan(root: Path, max_hits: int) -> list[Hit]:
    out=[]; compiled={k:[re.compile(x,re.I) for x in v] for k,v in PATTERNS.items()}
    for p in iter_files(root):
        try: text=p.read_text(encoding="utf-8",errors="replace")
        except Exception: continue
        rel=p.relative_to(root).as_posix()
        if any(fnmatch.fnmatch(rel.lower(), pat) for pat in ["examples/self-audit*","examples/*validation*","*.pyc"]): continue
        for i,line in enumerate(text.splitlines(),1):
            for cat, regs in compiled.items():
                if any(r.search(line) for r in regs):
                    out.append(Hit(cat,rel,i,re.sub(r"\s+"," ",line.strip())[:180])); break
            if len(out) >= max_hits: return out
    return out

def render_md(root: Path, hits: list[Hit]) -> str:
    groups={k:[h for h in hits if h.category==k] for k in PATTERNS}
    lines=["# Action/context parity inventory","",f"Root: `{root.resolve()}`","","> Starter inventory only. Confirm important workflows manually and map human context to agent context/action/recovery.","","## Candidate capability map","","| Human capability | Evidence | Agent path candidate | Context needed | Safety/recovery | Status |","| --- | --- | --- | --- | --- | --- |"]
    for h in groups.get("ui_action",[])[:40]: lines.append(f"| UI action | `{h.path}:{h.line}` | TBD API/CLI/tool | visible state, IDs, permissions | preview/audit if mutating | needs review |")
    for h in (groups.get("api_route",[])+groups.get("cli_command",[])+groups.get("tool_definition",[]))[:40]: lines.append(f"| Agent/action surface | `{h.path}:{h.line}` | {h.category} | docs/schema/auth | errors/retry/idempotency | candidate |")
    lines += ["","## Evidence by category"]
    for cat in PATTERNS:
        lines += [f"\n### {cat}"]
        for h in groups[cat][:30]: lines.append(f"- `{h.path}:{h.line}` — {h.snippet}")
        if not groups[cat]: lines.append("- No hits from heuristic scan.")
    return "\n".join(lines).rstrip()+"\n"

def write_csv(path: Path, hits: list[Hit]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["category","path","line","snippet"])
        for h in hits: w.writerow([h.category,h.path,h.line,h.snippet])

def main(argv: Sequence[str]|None=None) -> int:
    p=argparse.ArgumentParser(description="Inventory candidate UI actions and agent action paths.")
    p.add_argument("path"); p.add_argument("--output"); p.add_argument("--csv-output"); p.add_argument("--max-hits",type=int,default=500)
    a=p.parse_args(argv); root=Path(a.path)
    if not root.is_dir(): print(f"not a directory: {root}", file=sys.stderr); return 2
    hits=scan(root,a.max_hits); md=render_md(root,hits)
    if a.output: Path(a.output).parent.mkdir(parents=True, exist_ok=True); Path(a.output).write_text(md,encoding="utf-8")
    else: sys.stdout.write(md)
    if a.csv_output: write_csv(Path(a.csv_output),hits)
    return 0
if __name__ == "__main__": raise SystemExit(main())
