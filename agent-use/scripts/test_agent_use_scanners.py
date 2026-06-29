#!/usr/bin/env python3
"""Regression checks for the heuristic scanners."""
from __future__ import annotations

import tempfile
import argparse
from pathlib import Path

import agent_use_audit
import web_agent_readiness


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def audit(root: Path) -> dict:
    inv = agent_use_audit.Inventory(root)
    return agent_use_audit.Audit(inv).build()


def test_keyword_docs_do_not_count_as_implementation() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        write(root / "README.md", "This project talks about OpenAPI, OAuth, MCP, GraphQL, REST, onClick, and JSON output.\n")
        report = audit(root)
        dims = {d["name"]: d for d in report["dimensions"]}
        assert report["confidence"] == "low"
        assert not dims["Action parity"]["applicable"]
        assert not dims["Context parity"]["applicable"]


def test_real_contracts_and_cli_raise_confidence() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        write(root / "AGENTS.md", "Run `python src/cli.py --json --limit 20`.\n")
        write(root / "openapi.json", '{"openapi":"3.1.0","paths":{"/v1/items":{"get":{}}}}\n')
        write(root / "src" / "cli.py", "import argparse, json, sys\nprint(json.dumps({'items': []}))\n")
        write(root / "tests" / "test_cli.py", "assert True\n")
        report = audit(root)
        assert report["confidence"] in {"medium", "high"}
        assert report["score_basis"]["implementation"] >= 1
        assert report["score_basis"]["contract"] >= 2


def make_fake_fetch(pages: dict[str, tuple[int, str | None, str | None, str]]):
    def fake_fetch(label: str, url: str, accept: str | None, timeout: float, max_bytes: int):
        status, ctype, link, body = pages.get(url, (404, "text/plain", None, "missing"))
        result = web_agent_readiness.EndpointResult(
            label=label,
            url=url,
            status=status,
            ok=200 <= status < 300,
            content_type=ctype,
            bytes_read=len(body.encode("utf-8")),
            notes=[],
            link_header=link,
        )
        if result.ok:
            result.notes.extend(web_agent_readiness.analyze_body(label, url, ctype, body))
        else:
            result.notes.append(f"HTTP error {status}")
        return result, body
    return fake_fetch


def test_web_scanner_follows_link_header_and_linkset() -> None:
    original_fetch = web_agent_readiness.fetch
    pages = {
        "https://docs.example.com/docs": (
            200,
            "text/html",
            '<https://api.example.com/.well-known/api-catalog>; rel="api-catalog"; type="application/linkset+json"',
            "<html><title>Docs</title><h1>API docs</h1>Use OAuth scopes.</html>",
        ),
        "https://docs.example.com/llms.txt": (200, "text/markdown", None, "# Docs\n[API](https://api.example.com/openapi.json)\n"),
        "https://docs.example.com/robots.txt": (200, "text/plain", None, "User-agent: *\nAllow: /\n"),
        "https://api.example.com/.well-known/api-catalog": (
            200,
            "application/linkset+json",
            None,
            '{"linkset":[{"service-desc":[{"href":"https://api.example.com/openapi.json"}],"oauth-protected-resource":[{"href":"https://api.example.com/.well-known/oauth-protected-resource"}]}]}',
        ),
        "https://api.example.com/openapi.json": (200, "application/vnd.oai.openapi+json", None, '{"openapi":"3.1.0","paths":{}}'),
        "https://api.example.com/.well-known/oauth-protected-resource": (200, "application/json", None, '{"resource":"https://api.example.com","authorization_servers":["https://api.example.com"]}'),
    }
    try:
        web_agent_readiness.fetch = make_fake_fetch(pages)  # type: ignore[assignment]
        report = web_agent_readiness.build_report("https://docs.example.com/docs", 1, 400000, "auto")
    finally:
        web_agent_readiness.fetch = original_fetch  # type: ignore[assignment]
    labels = [e["label"] for e in report["endpoints"] if e["ok"]]
    assert report["applicability"]["profile"] == "docs-api"
    assert "linked OpenAPI" in labels
    assert "linked OAuth protected resource metadata" in labels
    assert not any("OAuth/OIDC" in rec for rec in report["recommendations"])
    assert not any("MCP server card" in rec for rec in report["recommendations"])


def main() -> int:
    test_keyword_docs_do_not_count_as_implementation()
    test_real_contracts_and_cli_raise_confidence()
    test_web_scanner_follows_link_header_and_linkset()
    print("scanner regression tests passed")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run agent-use scanner regression checks.")
    return parser.parse_args()


if __name__ == "__main__":
    parse_args()
    raise SystemExit(main())
