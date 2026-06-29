# CLI and TUI readiness

Use this when the agent surface is a command-line app, terminal UI, developer tool, build/deploy command, package manager, or local automation script.

## Agent contract

A good CLI gives agents a stable machine mode without making humans suffer.

Required patterns:

- `--help` and subcommand `--help` are complete and stable.
- `--version` returns the tool version and optionally API/schema version.
- Non-interactive mode exists: `--yes`, `--no-input`, `--non-interactive`, or safe defaults.
- JSON or schema-backed output exists: `--output json`, `--json`, or `--format json`.
- Data goes to stdout; progress, diagnostics, prompts, and errors go to stderr.
- Exit codes are documented and stable.
- Color, spinners, pagers, cursor controls, and TTY-only UI can be disabled automatically in machine mode.
- Large lists are bounded by default and support `--limit`, `--cursor`, `--page`, `--fields`, or equivalent.
- Mutations support dry-run/preview, idempotency, and clear verification output.

## TUI-specific patterns

TUIs are often hostile to agents unless they expose an alternate control plane.

Good options:

- A CLI subcommand that performs every important TUI action.
- A local HTTP/API/socket control plane with schemas.
- Scriptable command palette entries.
- Exportable state snapshots.
- Log files and artifact directories with stable paths.
- No reliance on pixel coordinates, terminal dimensions, animation timing, or hidden hover text.

## Error envelope

In JSON mode, errors should be parseable.

```json
{
  "error": {
    "code": "validation_failed",
    "message": "Name is required.",
    "retryable": false,
    "remediation": "Pass --name.",
    "details": {"field": "name"},
    "correlation_id": "req_123"
  }
}
```

## Design checklist

- Can an agent discover all commands without reading source code?
- Can it run a read-only command safely?
- Can it preview a mutation?
- Can it verify final state from structured output?
- Can it resume or retry without duplicate side effects?
- Can it run in CI without a TTY?
- Are secrets redacted from stdout/stderr/logs?
