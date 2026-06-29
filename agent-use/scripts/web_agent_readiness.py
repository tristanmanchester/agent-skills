#!/usr/bin/env python3
"""Check a website/docs URL for agent-readiness discovery signals."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen

VERSION = "2.0.0"
USER_AGENT = "agent-use-skill/2.0 (+https://agentskills.io/)"

@dataclass
class EndpointResult:
    label: str
    url: str
    status: int | None
    ok: bool
    content_type: str | None
    bytes_read: int
    notes: list[str]
    link_header: str | None = None
    discovered_from: str | None = None
    discovery_rel: str | None = None

class HeadingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.in_title=False; self.in_h1=False; self.title=""; self.h1=""
    def handle_starttag(self, tag: str, attrs):
        t=tag.lower(); self.in_title = self.in_title or t=="title"; self.in_h1 = self.in_h1 or t=="h1"
    def handle_endtag(self, tag: str):
        t=tag.lower()
        if t=="title": self.in_title=False
        if t=="h1": self.in_h1=False
    def handle_data(self, data: str):
        if self.in_title: self.title += data.strip() + " "
        if self.in_h1: self.h1 += data.strip() + " "

def normalize_url(url: str) -> str:
    return url if re.match(r"^https?://", url) else "https://" + url

def origin_for(url: str) -> str:
    p = urlparse(normalize_url(url))
    return urlunparse((p.scheme, p.netloc, "", "", "", ""))

def label_for_rel(rel: str, url: str) -> str:
    low = (rel + " " + url).lower()
    if "api-catalog" in low: return "linked API catalog"
    if "openid" in low: return "linked OpenID configuration"
    if "oauth-protected-resource" in low or "resource_metadata" in low: return "linked OAuth protected resource metadata"
    if "oauth-authorization-server" in low or "authorization-server" in low: return "linked OAuth authorization server metadata"
    if "openapi" in low or "swagger" in low or "service-desc" in low: return "linked OpenAPI"
    if "mcp" in low: return "linked MCP server card"
    if "agent-card" in low or "agent.json" in low: return "linked A2A agent card"
    if "agent-skills" in low: return "linked Agent skills index"
    if "llms" in low: return "linked llms.txt"
    if "canonical" in low: return "linked canonical"
    return f"linked {rel or 'alternate'}"

def accept_for_label(label: str) -> str:
    low = label.lower()
    if "openapi" in low: return "application/vnd.oai.openapi+json,application/json,*/*;q=0.5"
    if any(k in low for k in ["api catalog", "oauth", "openid", "mcp", "agent card", "agent skills"]):
        return "application/linkset+json,application/json,*/*;q=0.5"
    if "llms" in low or "canonical" in low: return "text/markdown,text/plain,text/html,*/*;q=0.5"
    return "application/json,text/markdown,text/plain,text/html,*/*;q=0.5"

def analyze_json(label: str, data: object) -> list[str]:
    notes=["valid JSON"]
    lower=label.lower()
    if "api catalog" in lower:
        if isinstance(data, dict) and "linkset" in data:
            notes.append("looks like RFC 9727 Linkset JSON")
        elif isinstance(data, list):
            notes.append("legacy/list API catalog shape")
    if "mcp" in lower and isinstance(data, dict) and any(k in data for k in ["capabilities","tools","resources","prompts","servers"]):
        notes.append("has MCP capability fields")
    if "agent card" in lower and isinstance(data, dict) and any(k in data for k in ["name","description","capabilities","skills"]):
        notes.append("has agent card fields")
    if ("oauth" in lower or "openid" in lower) and isinstance(data, dict) and any(k in data for k in ["issuer","resource","authorization_servers","authorization_endpoint","jwks_uri"]):
        notes.append("has auth metadata fields")
    if "openapi" in lower and isinstance(data, dict) and ("openapi" in data or "swagger" in data):
        notes.append("looks like OpenAPI/Swagger")
    return notes

def split_link_header(header: str) -> list[str]:
    parts=[]; buf=[]; in_quote=False
    for ch in header:
        if ch == '"': in_quote = not in_quote
        if ch == "," and not in_quote:
            part="".join(buf).strip()
            if part: parts.append(part)
            buf=[]
        else:
            buf.append(ch)
    part="".join(buf).strip()
    if part: parts.append(part)
    return parts

def parse_link_header(header: str | None, base_url: str) -> list[tuple[str,str]]:
    if not header: return []
    useful = {
        "service-desc", "service-doc", "api-catalog", "authorization-server",
        "oauth-protected-resource", "openid-configuration", "mcp", "agent-card",
        "canonical", "alternate", "llms", "describedby",
    }
    out=[]
    for part in split_link_header(header):
        m=re.match(r"\s*<([^>]+)>", part)
        if not m: continue
        href=urljoin(base_url, m.group(1).strip())
        attrs={}
        for key, value in re.findall(r";\s*([A-Za-z0-9_-]+)=?\"?([^\";]*)\"?", part):
            attrs[key.lower()] = value.strip()
        rels={r.strip().lower() for r in attrs.get("rel","").split() if r.strip()}
        typ=attrs.get("type","").lower()
        if not rels & useful and not any(t in typ for t in ["json","markdown","openapi","linkset"]):
            continue
        if "alternate" in rels and not any(t in typ for t in ["json","markdown","openapi","linkset","text/plain"]):
            continue
        rel="/".join(sorted(rels & useful)) or "typed-link"
        out.append((label_for_rel(rel, href), href))
    return out

def linkset_values(data: object) -> list[dict]:
    if isinstance(data, dict):
        if isinstance(data.get("linkset"), list):
            return [x for x in data["linkset"] if isinstance(x, dict)]
        if any(k in data for k in ("anchor", "href", "rel")):
            return [data]
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    return []

def parse_linkset_json(text: str, base_url: str) -> list[tuple[str,str]]:
    try:
        data=json.loads(text)
    except Exception:
        return []
    out=[]
    for item in linkset_values(data):
        for key, value in item.items():
            if key == "anchor": continue
            values=value if isinstance(value, list) else [value]
            for entry in values:
                if isinstance(entry, str):
                    href=entry; rel=key
                elif isinstance(entry, dict):
                    href=str(entry.get("href") or entry.get("uri") or "")
                    rel=str(entry.get("rel") or key)
                else:
                    continue
                if href:
                    out.append((label_for_rel(rel, href), urljoin(base_url, href)))
    return out

def analyze_body(label: str, url: str, content_type: str | None, text: str) -> list[str]:
    notes=[]; lower=label.lower(); ct=(content_type or "").lower()
    jsonish = "json" in ct or url.endswith(".json") or any(k in lower for k in ["api catalog","agent card","mcp","oauth","openid","openapi","swagger","agent skills"])
    if jsonish:
        try: notes.extend(analyze_json(label, json.loads(text)))
        except Exception as exc: notes.append(f"JSON-like endpoint did not parse as JSON: {exc}")
    if "llms" in lower:
        if re.search(r"^#\s+", text, re.M): notes.append("has markdown heading")
        if re.search(r"\[[^\]]+\]\([^)]+\)", text): notes.append("has markdown links")
    if "markdown" in lower or "text/markdown" in ct or url.endswith((".md",".mdx",".txt")):
        if re.search(r"^#\s+", text, re.M): notes.append("markdown-like headings found")
    if "html" in ct:
        parser=HeadingParser()
        try:
            parser.feed(text[:100000])
            if parser.title.strip(): notes.append("title: "+parser.title.strip()[:120])
            if parser.h1.strip(): notes.append("h1: "+parser.h1.strip()[:120])
        except Exception: pass
    if re.search(r"deprecated|deprecation|changelog|version|last updated", text, re.I): notes.append("freshness/versioning terms found")
    if len(text) > 250000: notes.append("large page; consider smaller agent-readable pages")
    return notes

def fetch(label: str, url: str, accept: str | None, timeout: float, max_bytes: int) -> tuple[EndpointResult, str]:
    headers={"User-Agent":USER_AGENT}
    if accept: headers["Accept"]=accept
    status=None; ctype=None; link=None; body=b""; notes=[]
    try:
        with urlopen(Request(url,headers=headers), timeout=timeout) as resp:  # nosec: explicit user requested URL check
            status=int(getattr(resp,"status",200)); ctype=resp.headers.get("content-type"); link=resp.headers.get("link")
            body=resp.read(max_bytes+1)
            if len(body)>max_bytes: notes.append(f"truncated after {max_bytes} bytes"); body=body[:max_bytes]
    except HTTPError as exc:
        status=exc.code; ctype=exc.headers.get("content-type") if exc.headers else None; link=exc.headers.get("link") if exc.headers else None
        try: body=exc.read(min(max_bytes,20000))
        except Exception: body=b""
        notes.append(f"HTTP error {exc.code}")
    except URLError as exc: notes.append(f"URL error: {exc.reason}")
    except Exception as exc: notes.append(f"fetch failed: {exc}")
    text=body.decode("utf-8", errors="replace")
    ok=status is not None and 200 <= status < 300
    if ok: notes.extend(analyze_body(label,url,ctype,text))
    return EndpointResult(label,url,status,ok,ctype,len(body),notes,link), text

def candidate_endpoints(url: str) -> list[tuple[str,str,str|None]]:
    url=normalize_url(url); origin=origin_for(url); p=urlparse(url); path=p.path or "/"
    items=[
        ("input page", url, "text/html,application/xhtml+xml,*/*;q=0.8"),
        ("input page markdown negotiation", url, "text/markdown,text/plain;q=0.9,text/html;q=0.6,*/*;q=0.1"),
        ("llms.txt", urljoin(origin,"/llms.txt"), "text/markdown,text/plain,*/*;q=0.5"),
        ("llms-full.txt", urljoin(origin,"/llms-full.txt"), "text/markdown,text/plain,*/*;q=0.5"),
        ("robots.txt", urljoin(origin,"/robots.txt"), "text/plain,*/*;q=0.5"),
        ("sitemap.xml", urljoin(origin,"/sitemap.xml"), "application/xml,text/xml,*/*;q=0.5"),
        ("API catalog", urljoin(origin,"/.well-known/api-catalog"), "application/linkset+json,application/json,*/*;q=0.5"),
        ("API catalog JSON", urljoin(origin,"/.well-known/api-catalog.json"), "application/linkset+json,application/json,*/*;q=0.5"),
        ("OpenAPI root", urljoin(origin,"/openapi.json"), "application/vnd.oai.openapi+json,application/json,*/*;q=0.5"),
        ("Swagger root", urljoin(origin,"/swagger.json"), "application/json,*/*;q=0.5"),
        ("OAuth protected resource metadata", urljoin(origin,"/.well-known/oauth-protected-resource"), "application/json,*/*;q=0.5"),
        ("OAuth authorization server metadata", urljoin(origin,"/.well-known/oauth-authorization-server"), "application/json,*/*;q=0.5"),
        ("OpenID configuration", urljoin(origin,"/.well-known/openid-configuration"), "application/json,*/*;q=0.5"),
        ("MCP server card", urljoin(origin,"/.well-known/mcp.json"), "application/json,*/*;q=0.5"),
        ("MCP server card alternate", urljoin(origin,"/.well-known/mcp/server-card.json"), "application/json,*/*;q=0.5"),
        ("A2A agent card", urljoin(origin,"/.well-known/agent-card.json"), "application/json,*/*;q=0.5"),
        ("A2A agent card alternate", urljoin(origin,"/.well-known/agent.json"), "application/json,*/*;q=0.5"),
        ("Agent skills index", urljoin(origin,"/.well-known/agent-skills/index.json"), "application/json,*/*;q=0.5"),
    ]
    if path and not path.endswith("/") and not path.endswith((".md",".txt",".html")):
        items.append(("path markdown variant", urlunparse((p.scheme,p.netloc,path+".md","","","")), "text/markdown,text/plain,*/*;q=0.5"))
    if path.endswith("/") or path=="/": items.append(("index markdown variant", urljoin(url,"index.md"), "text/markdown,text/plain,*/*;q=0.5"))
    seen=set(); out=[]
    for item in items:
        key=(item[0],item[1])
        if key not in seen: out.append(item); seen.add(key)
    return out

def infer_profile(results: list[EndpointResult], bodies: dict[str,str], requested: str) -> tuple[str,str]:
    if requested != "auto": return requested, "explicit"
    corpus="\n".join(bodies.values()).lower()
    input_doc=any(r.label.startswith("input page") and r.ok and (("html" in (r.content_type or "").lower()) or "markdown-like" in " ".join(r.notes).lower()) for r in results)
    linked_api=any(r.discovered_from and r.ok and any(k in r.label.lower() for k in ["openapi","api catalog","oauth","openid"]) for r in results)
    same_origin_api=any(not r.discovered_from and r.ok and any(k in r.label.lower() for k in ["openapi","api catalog"]) for r in results)
    if same_origin_api: return "api", "inferred from same-origin API discovery"
    if input_doc and linked_api: return "docs-api", "inferred from docs page with linked API discovery"
    if re.search(r"\b(openapi|swagger|graphql|sdk|webhook|api key|oauth|developer platform)\b", corpus): return "api", "inferred from API/developer signals"
    if any(r.ok and any(k in r.label.lower() for k in ["mcp", "a2a", "agent skills"]) for r in results): return "tool", "inferred from tool/agent discovery endpoints"
    if re.search(r"\b(dashboard|workspace|project|settings|deploy|billing)\b", corpus): return "app", "inferred from app workflow signals"
    if input_doc: return "docs", "inferred from documentation page signals"
    return "content", "inferred from content/docs signals"

def score(results: list[EndpointResult], bodies: dict[str,str], profile: str) -> tuple[float,list[dict],dict[str,object]]:
    prof, reason = infer_profile(results,bodies,profile)
    needs_cap=prof in {"api","app","tool","docs-api"}
    needs_auth=needs_cap and bool(re.search(r"\b(auth|oauth|oidc|token|api key|scope|permission|login)\b", "\n".join(bodies.values()), re.I))
    needs_tool=prof == "tool"
    def ok(sub): return any(sub.lower() in r.label.lower() and r.ok for r in results)
    def note(sub,n): return any(sub.lower() in r.label.lower() and any(n.lower() in x.lower() for x in r.notes) for r in results)
    def header(term): return any(r.link_header and term.lower() in r.link_header.lower() for r in results)
    def dim(name,score,maxs,app=True,why="applicable"):
        return {"name":name,"score":round(min(maxs,score),1) if app else None,"max_score":maxs if app else None,"applicable":app,"reason":why if app else why}
    dims=[]
    discover=(4 if ok("llms.txt") else 0)+(2 if ok("robots") else 0)+(2 if ok("sitemap") else 0)+(2 if header("llms") or header("canonical") or ok("linked canonical") else 0)+(3 if needs_cap and ok("API catalog") else 0)+(2 if needs_tool and (ok("MCP") or ok("A2A") or ok("Agent skills")) else 0)+(2 if needs_cap and (header("service-desc") or header("api-catalog") or header("mcp") or any(r.discovered_from and r.ok for r in results)) else 0)
    dims.append(dim("discoverability", discover, 20))
    content=(4 if note("input page","h1") or note("input page","title") else 0)+(4 if note("llms","markdown heading") or note("markdown","markdown-like") else 0)+(3 if note("llms","markdown links") else 0)+(3 if any("freshness/versioning" in " ".join(r.notes).lower() for r in results if r.ok) else 0)+(2 if not any("large page" in " ".join(r.notes).lower() for r in results if r.label=="input page") else 0)+(2 if ok("sitemap") or ok("llms.txt") else 0)
    dims.append(dim("content", content, 20))
    capabilities=(6 if ok("API catalog") or ok("OpenAPI") or any("openapi" in b.lower() for b in bodies.values()) else 0)+(4 if needs_tool and note("MCP","capability") else 0)+(4 if needs_tool and (note("A2A","agent card") or ok("A2A")) else 0)+(3 if needs_tool and ok("Agent skills") else 0)+(3 if header("service-doc") or header("service-desc") or any(r.discovered_from and r.ok for r in results) else 0)
    dims.append(dim("capabilities", capabilities, 20, needs_cap, "API/app/tool/docs-api surfaces need machine capability discovery" if needs_cap else "content/docs profile does not require API/MCP/A2A capability endpoints"))
    access=(5 if needs_auth and (ok("OAuth protected") or ok("OAuth authorization") or ok("OpenID")) else 0)+(3 if needs_auth and (note("OAuth","auth metadata") or note("OpenID","auth metadata")) else 0)+(3 if ok("robots") else 0)+(2 if "allow" in bodies.get("robots.txt","").lower() or "disallow" in bodies.get("robots.txt","").lower() else 0)+(2 if any("terms" in (r.link_header or "").lower() for r in results) else 0)+(2 if not needs_auth else 0)
    dims.append(dim("access and safety", access, 15 if not needs_auth else 20))
    all_text="\n".join(bodies.values()).lower(); maintenance=(5 if re.search(r"changelog|release notes|version|deprecated|deprecation",all_text) else 0)+(3 if re.search(r"last updated|updated|date",all_text) else 0)+(3 if ok("sitemap") else 0)+(3 if ok("API catalog") or ok("llms.txt") else 0)+(2 if not any("json-like endpoint did not parse" in " ".join(r.notes).lower() for r in results if r.ok) else 0)
    dims.append(dim("maintenance", maintenance, 20))
    applicable=[d for d in dims if d["applicable"]]
    overall=round(sum((d["score"] or 0)/(d["max_score"] or 1) for d in applicable)/len(applicable)*100,1) if applicable else 0.0
    return overall,dims,{"profile":prof,"profile_reason":reason,"needs_capability_endpoints":needs_cap,"needs_auth_metadata":needs_auth,"needs_tool_metadata":needs_tool}

def grade(v: float) -> str:
    return "strong" if v>=80 else "agent-ready foundation" if v>=60 else "partial" if v>=40 else "thin" if v>=20 else "low signal"

def build_report(url: str, timeout: float, max_bytes: int, profile: str) -> dict:
    results=[]; bodies={}; seen=set(); queue=[]
    for label, endpoint, accept in candidate_endpoints(url):
        queue.append((label, endpoint, accept, None, None))
    while queue:
        label, endpoint, accept, discovered_from, discovery_rel = queue.pop(0)
        key=(label, endpoint)
        if key in seen: continue
        seen.add(key)
        r,b=fetch(label, endpoint, accept, timeout, max_bytes)
        r.discovered_from=discovered_from; r.discovery_rel=discovery_rel
        results.append(r)
        if not r.ok: continue
        bodies[label]=b
        if not discovered_from:
            for dlabel, durl in parse_link_header(r.link_header, endpoint):
                if (dlabel, durl) not in seen:
                    queue.append((dlabel, durl, accept_for_label(dlabel), endpoint, dlabel.removeprefix("linked ")))
        if "api catalog" in label.lower() or "linkset+json" in (r.content_type or "").lower():
            for dlabel, durl in parse_linkset_json(b, endpoint):
                if (dlabel, durl) not in seen:
                    queue.append((dlabel, durl, accept_for_label(dlabel), endpoint, dlabel.removeprefix("linked ")))
    overall,dims,app=score(results,bodies,profile)
    recs=[]
    if not any(r.label=="llms.txt" and r.ok for r in results): recs.append("Publish `/llms.txt` with a concise markdown map of canonical docs, APIs, changelogs, and agent-specific guidance.")
    if app["needs_capability_endpoints"] and not any("API catalog" in r.label and r.ok for r in results): recs.append("For API/app profiles, publish `/.well-known/api-catalog` as Linkset JSON or link to a machine-readable API inventory.")
    if app["needs_auth_metadata"] and not any(("OAuth" in r.label or "OpenID" in r.label) and r.ok for r in results): recs.append("Auth appears relevant; publish OAuth/OIDC protected-resource or authorization-server metadata and document scopes.")
    if app.get("needs_tool_metadata") and not any(("MCP" in r.label or "A2A" in r.label) and r.ok for r in results): recs.append("Tool/agent surfaces should publish an MCP server card at `/.well-known/mcp.json` and/or an A2A agent card.")
    if not any("markdown" in " ".join(r.notes).lower() for r in results if r.ok): recs.append("Provide markdown or markdown-negotiated docs for canonical task pages.")
    return {"scanner_version":VERSION,"target":normalize_url(url),"overall_score":overall,"grade":grade(overall),"applicability":app,"dimensions":dims,"endpoints":[asdict(r) for r in results],"recommendations":recs}

def render_markdown(report: dict) -> str:
    lines=[f"# Web agent-readiness: {report['target']}","",f"Overall: **{report['overall_score']}/100** ({report['grade']})"]
    app=report.get("applicability",{}); lines.append(f"Profile: **{app.get('profile')}** ({app.get('profile_reason')})"); lines += ["","## Scores"]
    for d in report["dimensions"]:
        lines.append(f"- {d['name']}: {d['score']}/{d['max_score']}" if d.get("applicable") else f"- {d['name']}: N/A — {d.get('reason','not applicable')}")
    lines += ["","## Endpoint checks","| Endpoint | Status | Notes |","|---|---:|---|"]
    for e in report["endpoints"]:
        status=e["status"] if e["status"] is not None else "n/a"; notes="; ".join(e["notes"][:4]).replace("|","\\|"); ok="ok" if e["ok"] else "missing/blocked"
        if e.get("discovered_from"): notes=(notes+"; " if notes else "")+f"discovered from {e['discovered_from']}"
        lines.append(f"| [{e['label']}]({e['url']}) ({ok}) | {status} | {notes} |")
    lines += ["","## Recommendations"]
    lines += [f"- {r}" for r in report["recommendations"]] or ["- No broad missing-endpoint recommendations from the heuristic scan. Review content quality, auth flows, and task-level examples manually."]
    return "\n".join(lines).rstrip()+"\n"

def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace:
    p=argparse.ArgumentParser(description="Check web/docs agent-readiness discovery endpoints.")
    p.add_argument("url"); p.add_argument("--json", action="store_true", help="Emit JSON instead of markdown."); p.add_argument("--markdown", action="store_true", help="Emit markdown. This is the default."); p.add_argument("--output", help="Write output to a file instead of stdout."); p.add_argument("--timeout", type=float, default=5.0); p.add_argument("--max-bytes", type=int, default=400000); p.add_argument("--profile", choices=["auto","content","docs","docs-api","api","app","tool"], default="auto", help="Applicability profile. Default: auto.")
    return p.parse_args(argv)

def main(argv: Sequence[str] | None=None) -> int:
    a=parse_args(argv); report=build_report(a.url, a.timeout, a.max_bytes, a.profile); text=json.dumps(report,indent=2)+"\n" if a.json and not a.markdown else render_markdown(report)
    if a.output:
        Path(a.output).parent.mkdir(parents=True, exist_ok=True); Path(a.output).write_text(text,encoding="utf-8")
    else: print(text,end="")
    return 0

if __name__ == "__main__": raise SystemExit(main())
