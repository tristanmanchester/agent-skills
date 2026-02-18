# Command cheat sheet (audit focus)

Run these on the OpenClaw host:

## Core

```bash
openclaw --version
openclaw status --all
openclaw doctor
openclaw gateway status
openclaw security audit
openclaw security audit --deep
openclaw security audit --json
```

## Safe sharing

Prefer `openclaw status --all` and `openclaw security audit --json`. Avoid sharing raw config/credentials.

If you must share a config for review, redact it:

```bash
python3 scripts/redact_openclaw_config.py ~/.openclaw/openclaw.json > openclaw.json.redacted
```

## Network exposure checks

macOS:
```bash
lsof -nP -iTCP -sTCP:LISTEN
```

Linux:
```bash
ss -ltnp
```

## After remediation

```bash
openclaw security audit --deep
openclaw doctor
```
