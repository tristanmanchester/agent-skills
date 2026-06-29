#!/usr/bin/env python3
"""Validate an Agent Skill package and bundled agent-use assets."""
from __future__ import annotations

import argparse, json, py_compile, re, subprocess, sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

NAME_RE=re.compile(r"^(?!.*--)[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
MAX_DESCRIPTION=1024; MAX_COMPATIBILITY=500; WARN_SKILL_LINES=500; WARN_SKILL_BYTES=50000
IGNORED_DIR_NAMES={"__pycache__",".git",".hg",".svn",".pytest_cache",".mypy_cache",".ruff_cache"}
IGNORED_SUFFIXES={".pyc",".pyo"}

@dataclass
class Check:
    id:str; status:str; message:str; severity:str="medium"
    def to_dict(self)->Dict[str,str]: return {"id":self.id,"status":self.status,"severity":self.severity,"message":self.message}

def is_ignored_file(path: Path, base: Path) -> bool:
    try: rel=path.relative_to(base)
    except ValueError: rel=path
    return any(part in IGNORED_DIR_NAMES for part in rel.parts) or path.suffix in IGNORED_SUFFIXES or path.name.startswith(".")

def count_files(path: Path) -> int:
    return sum(1 for p in path.rglob("*") if p.is_file() and not is_ignored_file(p,path))

def parse_frontmatter(text: str) -> Tuple[Dict[str,str],List[str]]:
    if not text.startswith("---\n"): return {}, ["SKILL.md must start with YAML frontmatter delimited by ---"]
    end=text.find("\n---",4)
    if end==-1: return {}, ["SKILL.md frontmatter is missing closing --- delimiter"]
    data={}; errors=[]
    for raw in text[4:end].splitlines():
        line=raw.strip()
        if not line or line.startswith("#") or raw.startswith((" ","\t","- ")): continue
        if ":" not in line: errors.append(f"frontmatter line is not key: value: {raw}"); continue
        k,v=line.split(":",1); data[k.strip()]=v.strip().strip('"\'')
    return data, errors

def referenced_paths(text: str) -> List[str]:
    candidates=[]
    candidates += [m.group(1) for m in re.finditer(r"`((?:references|scripts|assets|evals|examples)/[A-Za-z0-9_./-]+)`", text)]
    candidates += [m.group(1) for m in re.finditer(r"\[[^\]]+\]\(((?:references|scripts|assets|evals|examples)/[^)\s]+)\)", text)]
    out=[]
    for rel in candidates:
        rel=rel.strip().rstrip(".,);]")
        if rel and rel not in out: out.append(rel)
    return out

def load_json(path: Path):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return None

def validate_trigger_queries(path: Path) -> Tuple[bool,str]:
    data=load_json(path)
    if data is None: return False, "trigger query file is not valid JSON"
    pos=neg=0
    if isinstance(data,dict): pos=len(data.get("trigger_queries",[]) or data.get("should_trigger",[]) or []); neg=len(data.get("non_trigger_queries",[]) or data.get("should_not_trigger",[]) or [])
    elif isinstance(data,list):
        for item in data:
            if isinstance(item,dict) and "should_trigger" in item:
                if item["should_trigger"]: pos+=1
                else: neg+=1
    ok=pos>=5 and neg>=5
    return ok, f"{pos} should-trigger and {neg} should-not-trigger queries"

def validate(skill_dir: Path, run_help: bool=False, do_py_compile: bool=False) -> Dict[str,object]:
    original=Path(skill_dir).expanduser()
    if not original.exists() or not original.is_dir(): return {"skill_dir":str(original),"valid":False,"checks":[Check("skill-dir","fail","Skill directory does not exist or is not a directory","critical").to_dict()]}
    skill_dir=original.resolve(); checks=[]; skill_md=skill_dir/"SKILL.md"
    if not skill_md.exists(): return {"skill_dir":str(skill_dir),"valid":False,"checks":[Check("skill-md","fail","Missing SKILL.md","critical").to_dict()]}
    text=skill_md.read_text(encoding="utf-8", errors="replace"); fm, errs=parse_frontmatter(text)
    checks.extend([Check("frontmatter","fail",e,"critical") for e in errs] or [Check("frontmatter","pass","SKILL.md frontmatter delimiters found","low")])
    name=fm.get("name",""); desc=fm.get("description",""); compat=fm.get("compatibility","")
    if not name: checks.append(Check("name","fail","Frontmatter is missing required name","critical"))
    elif not NAME_RE.match(name) or len(name)>64: checks.append(Check("name","fail","name must be lowercase letters/numbers/hyphens, no leading/trailing/consecutive hyphen, and <=64 chars","critical"))
    elif name != skill_dir.name: checks.append(Check("name","fail",f"name '{name}' does not match parent directory '{skill_dir.name}'","critical"))
    else: checks.append(Check("name","pass","Skill name is valid and matches parent directory","low"))
    if not desc: checks.append(Check("description","fail","Frontmatter is missing required description","critical"))
    elif len(desc)>MAX_DESCRIPTION: checks.append(Check("description","fail",f"Description is {len(desc)} chars; keep it under {MAX_DESCRIPTION}","critical"))
    else:
        sig=sum(1 for w in ["audit","design","create","when","use","website","cli","api","sdk","docs","agent"] if w in desc.lower())
        checks.append(Check("description","pass" if sig>=3 else "warn",f"Description is {len(desc)} chars and has {sig} intent/context signals","low" if sig>=3 else "medium"))
    if compat and len(compat)>MAX_COMPATIBILITY: checks.append(Check("compatibility","fail",f"compatibility is {len(compat)} chars; keep it under {MAX_COMPATIBILITY}","critical"))
    elif compat: checks.append(Check("compatibility","pass","compatibility field is within size limit","low"))
    line_count=len(text.splitlines()); byte_count=len(text.encode("utf-8",errors="ignore"))
    checks.append(Check("progressive-disclosure","warn" if line_count>WARN_SKILL_LINES or byte_count>WARN_SKILL_BYTES else "pass",f"SKILL.md is {line_count} lines / {byte_count} bytes" if line_count>WARN_SKILL_LINES or byte_count>WARN_SKILL_BYTES else f"SKILL.md size is reasonable: {line_count} lines / {byte_count} bytes","medium" if line_count>WARN_SKILL_LINES or byte_count>WARN_SKILL_BYTES else "low"))
    for dirname in ["references","scripts","assets"]:
        p=skill_dir/dirname; checks.append(Check(f"dir-{dirname}","pass" if p.exists() else "warn",f"{dirname}/ exists with {count_files(p)} files" if p.exists() else f"{dirname}/ not present; okay only if unnecessary","low"))
    refs=referenced_paths(text); missing=[rel for rel in refs if not (skill_dir/rel).exists()]
    checks.append(Check("referenced-paths","fail" if missing else "pass","Missing referenced paths: "+", ".join(missing[:10]) if missing else f"All {len(refs)} referenced bundled paths exist","critical" if missing else "low"))
    json_files=[p for p in skill_dir.rglob("*.json") if not is_ignored_file(p,skill_dir)]; json_errors=[]
    for jf in json_files:
        try: json.loads(jf.read_text(encoding="utf-8"))
        except Exception as e: json_errors.append(f"{jf.relative_to(skill_dir)}: {type(e).__name__}: {e}")
    checks.append(Check("json-resources","fail" if json_errors else "pass","Invalid JSON resources: "+"; ".join(json_errors[:5]) if json_errors else f"All {len(json_files)} JSON resources parse","critical" if json_errors else "low"))
    trig=[p for p in (skill_dir/"evals").glob("*trigger*queries*.json")] if (skill_dir/"evals").exists() else []
    if trig:
        details=[]; ok_any=False
        for p in trig:
            ok,msg=validate_trigger_queries(p); ok_any=ok_any or ok; details.append(f"{p.name}: {msg}")
        checks.append(Check("trigger-evals","pass" if ok_any else "warn","; ".join(details),"low" if ok_any else "medium"))
    else: checks.append(Check("trigger-evals","warn","No trigger query eval file found","medium"))
    eval_files=[p for p in (skill_dir/"evals").glob("*") if p.is_file() and not is_ignored_file(p,skill_dir)] if (skill_dir/"evals").exists() else []
    checks.append(Check("evals","pass" if eval_files else "warn",f"evals/ contains {len(eval_files)} files" if eval_files else "No evals/ files found; add trigger and output-quality evals","low" if eval_files else "medium"))
    scripts=sorted((skill_dir/"scripts").glob("*.py")) if (skill_dir/"scripts").exists() else []
    for script in scripts:
        content=script.read_text(encoding="utf-8", errors="replace"); helpful="argparse" in content or "from validate_skill import main" in content or "from agent_use_audit import main" in content
        checks.append(Check(f"script-{script.name}","pass" if helpful else "warn","script uses argparse/help patterns or delegates to a validated CLI" if helpful else "script may not expose a standard --help interface","low" if helpful else "medium"))
        if do_py_compile:
            try: py_compile.compile(str(script), doraise=True); checks.append(Check(f"script-pycompile-{script.name}","pass","script compiles","low"))
            except Exception as e: checks.append(Check(f"script-pycompile-{script.name}","fail",f"py_compile failed: {type(e).__name__}: {e}","critical"))
        if run_help:
            try:
                rc=subprocess.call([sys.executable,str(script),"--help"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=10)
                checks.append(Check(f"script-help-{script.name}","pass" if rc==0 else "warn","--help exited zero" if rc==0 else f"--help exit={rc}","low" if rc==0 else "medium"))
            except Exception as e: checks.append(Check(f"script-help-{script.name}","warn",f"Could not run --help: {type(e).__name__}: {e}","medium"))
    failed=[c for c in checks if c.status=="fail"]; warned=[c for c in checks if c.status=="warn"]
    return {"skill_dir":str(skill_dir),"valid":not failed,"summary":{"pass":sum(c.status=="pass" for c in checks),"warn":len(warned),"fail":len(failed)},"frontmatter":fm,"checks":[c.to_dict() for c in checks]}

def render_markdown(report: Dict[str,object]) -> str:
    lines=[f"# Skill validation: `{report['skill_dir']}`","",f"Valid: **{report['valid']}**"]
    if "summary" in report: lines.append(f"Summary: {report['summary']}")
    lines += ["","| Check | Status | Severity | Message |","| --- | --- | --- | --- |"]
    for c in report["checks"]: lines.append(f"| {c['id']} | {c['status']} | {c['severity']} | {str(c['message']).replace('|','\\|')} |")
    return "\n".join(lines)+"\n"

def parse_args(argv: Optional[Sequence[str]]=None) -> argparse.Namespace:
    p=argparse.ArgumentParser(description="Validate an Agent Skill package structure and common agent-use assets.")
    p.add_argument("path", nargs="?", help="Skill directory containing SKILL.md; optional when --skill-dir is supplied"); p.add_argument("--skill-dir", help="Skill directory containing SKILL.md")
    p.add_argument("--format", choices=["markdown","json"], default="markdown"); p.add_argument("--markdown", action="store_true"); p.add_argument("--json", action="store_true", dest="json_format"); p.add_argument("--output"); p.add_argument("--run-help", action="store_true"); p.add_argument("--py-compile", action="store_true")
    return p.parse_args(argv)

def main(argv: Optional[Sequence[str]]=None) -> int:
    a=parse_args(argv); sd=a.path or a.skill_dir
    if not sd: print('{"error":{"code":"missing_skill_dir","message":"provide a positional path or --skill-dir"}}', file=sys.stderr); return 2
    report=validate(Path(sd),run_help=a.run_help,do_py_compile=a.py_compile); fmt="json" if a.json_format else "markdown" if a.markdown else a.format; rendered=json.dumps(report,indent=2)+"\n" if fmt=="json" else render_markdown(report)
    if a.output:
        Path(a.output).parent.mkdir(parents=True, exist_ok=True); Path(a.output).write_text(rendered,encoding="utf-8")
    else: sys.stdout.write(rendered)
    return 0 if report.get("valid") else 1

if __name__ == "__main__": raise SystemExit(main())
