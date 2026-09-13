# agent-use

Audit and design products around tasks an agent can actually discover, perform,
verify, and recover. Start at [SKILL.md](SKILL.md); load the domain references only
when they match the product surface.

The collection retains its action/context parity methods, capability maps,
heuristic scanners, templates, and evaluation seeds. Heuristic scores and old
outputs in `examples/` are not protocol conformance or agent-success evidence.

## Current helper interfaces

Run from this installed skill directory, with Python 3.10+ and PyYAML >=6.0.3,<7
available for validation:

```bash
python scripts/validate_agent_assets.py --skill-dir .
python -m unittest discover -s tests -v
python scripts/generate_agent_assets.py --output /private/existing-parent/new-drafts \
  --project-name "Example" --base-url https://example.com --surface a2a
```

Validation is static and does not execute inspected scripts or produce bytecode.
Scaffolding previews by default. Add `--write` to create only the selected drafts
in a new private directory; review and separately publish them when appropriate.
No old `--run-help`, `--py-compile`, `--surface all`, `--root`, `--force`, or
`--dry-run` alias is supported by these updated helpers.

The current A2A card targets 1.0. Local MCP/skills-index templates remain proposals,
not universal discovery standards. The example's security declaration must match
real server enforcement before publication. Full protocol/client runtime tests
are separate from the bundled structural/scaffold regressions.

The existing scanner test entrypoint remains `python scripts/test_agent_use_scanners.py`.
It tests heuristic signals with synthetic inputs, not live interoperability.
