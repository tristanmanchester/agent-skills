#!/usr/bin/env python3
"""Scaffold common agent-facing files from bundled templates."""
from __future__ import annotations
import argparse, datetime as dt, re, sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
@dataclass(frozen=True)
class Asset:
    source:str; target:str; surface:str; description:str
ASSETS=[
 Asset("AGENTS.md.template","AGENTS.md","core","Repository instructions for coding agents"),
 Asset("LLMS_TXT.template","llms.txt","web","Concise LLM/agent docs index"),
 Asset("WEB_DISCOVERY_HEADERS.txt","docs/agent-use/web-discovery-headers.txt","web","HTTP Link header examples"),
 Asset("CAPABILITY_MAP.csv","docs/agent-use/capability-map.csv","core","Capability map worksheet"),
 Asset("ACTION_PARITY_REVIEW.md.template","docs/agent-use/action-parity-review.md","app","Action/context parity worksheet"),
 Asset("CONTEXT_INJECTION.md.template","docs/agent-use/context-injection-contract.md","app","Dynamic context injection contract"),
 Asset("permission-matrix.csv","docs/agent-use/permission-matrix.csv","security","Permission/approval matrix"),
 Asset("API_AGENT_CONTRACT.md.template","docs/agent-use/api-agent-contract.md","api","API agent contract"),
 Asset("CLI_AGENT_CONTRACT.md.template","docs/agent-use/cli-agent-contract.md","cli","CLI/TUI agent contract"),
 Asset("EVALS.json","evals/agent-use-evals.json","evals","Agent task eval seed file"),
 Asset("api-catalog.linkset.json",".well-known/api-catalog","web","RFC 9727 API catalog Linkset draft"),
 Asset("mcp-server-card.json",".well-known/mcp.json","mcp","MCP server-card draft"),
 Asset("a2a-agent-card.json",".well-known/agent-card.json","a2a","A2A-style agent card draft"),
 Asset("agent-skills-index.json",".well-known/agent-skills/index.json","skills","Agent skills index draft"),
]
def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-") or "project"
def render(t, name, base):
    vals={"<Project name>":name,"<project>":name,"<Product or docs name>":name,"<target>":name,"<date>":dt.date.today().isoformat(),"https://example.com":base,"https://api.example.com":base.rstrip('/')+"/api","<api-name>":name,"<cli-name>":slug(name)}
    for k,v in vals.items(): t=t.replace(k,v)
    return t

def main(argv: Sequence[str]|None=None)->int:
    p=argparse.ArgumentParser(description="Scaffold agent-use assets from templates.")
    p.add_argument("--root", required=True); p.add_argument("--project-name", required=True); p.add_argument("--base-url", default="https://example.com"); p.add_argument("--surface", choices=["all","core","web","app","api","cli","mcp","a2a","skills","security","evals"], default="all"); p.add_argument("--force", action="store_true"); p.add_argument("--dry-run", action="store_true")
    a=p.parse_args(argv); root=Path(a.root); tmpl=Path(__file__).resolve().parents[1]/"assets"/"templates"; root.mkdir(parents=True,exist_ok=True)
    rows=[]
    for asset in ASSETS:
        if a.surface!="all" and asset.surface!=a.surface and not (a.surface=="core" and asset.surface=="core"): continue
        src=tmpl/asset.source; dst=root/asset.target
        if not src.exists(): rows.append({"status":"error","path":asset.target,"message":"missing template"}); continue
        status="would_write" if a.dry_run else "written"
        if dst.exists() and not a.force: status="exists"
        elif not a.dry_run:
            dst.parent.mkdir(parents=True,exist_ok=True); dst.write_text(render(src.read_text(encoding="utf-8"),a.project_name,a.base_url),encoding="utf-8")
        rows.append({"status":status,"path":asset.target,"description":asset.description})
    for r in rows: print(f"{r['status']}\t{r['path']}\t{r.get('description',r.get('message',''))}")
    return 1 if any(r["status"]=="error" for r in rows) else 0
if __name__=="__main__": raise SystemExit(main())
