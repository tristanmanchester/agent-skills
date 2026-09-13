# Maintaining agent-use

Read SKILL.md and the reference for the surface being changed. Preserve the
capability/parity audit method and existing MIT licence. Prefer a focused fix to
a new general framework or another copy of an upstream protocol catalogue.

Run from this skill directory with Python 3.10+ and PyYAML >=6.0.3,<7:

```bash
python scripts/validate_agent_assets.py --skill-dir .
python -m unittest discover -s tests -v
python scripts/test_agent_use_scanners.py
```

The validator reads YAML/JSON/Python/Markdown; it never runs inspected scripts or
writes bytecode. Test execution is separate and must be authorised for the code
under review. Network probes, generated files, installations, and output writes
are not passive reads. Use explicit target/output paths and do not replace an
existing project's instructions as an audit side effect.

The generator previews selected surfaces and writes only to a new draft directory
with --write. Do not restore universal .well-known claims or broad --force/default-all
behaviour. Validate the actual current A2A/MCP/API schema and runtime when making
protocol claims; local fixture checks establish only their stated subset.

Files in examples are historical heuristic scanner outputs unless explicitly
regenerated. Their scores are not present-day release evidence. Keep new regression
tests, supported command examples, source links/review dates, and runtime limitations
aligned. Use caller-provided installation paths; never embed a user's home path.
