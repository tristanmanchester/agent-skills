# OpenClaw secure baseline config (starting point)

This file contains a conservative baseline derived from OpenClaw’s own security guidance.

## Baseline goal

- Keep the Gateway **private** (loopback)
- Require strong **Gateway auth**
- Isolate DMs and require **pairing**
- Require explicit **mention gating** in groups
- Default tools to least privilege

## Minimal “secure baseline” (copy/paste)

> Paste into your OpenClaw config (usually `~/.openclaw/openclaw.json`) *after* making a backup.
> Replace the token with a long random secret.

```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "port": 18789,
    "auth": { "mode": "token", "token": "your-long-random-token" }
  },
  "channels": {
    "whatsapp": {
      "dmPolicy": "pairing",
      "groups": { "*": { "requireMention": true } }
    }
  }
}
```

## Hardened baseline including tool restrictions

```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "auth": { "mode": "token", "token": "replace-with-long-random-token" }
  },
  "session": {
    "dmScope": "per-channel-peer"
  },
  "tools": {
    "profile": "messaging",
    "deny": ["group:automation", "group:runtime", "group:fs", "sessions_spawn", "sessions_send"],
    "fs": { "workspaceOnly": true },
    "exec": { "security": "deny", "ask": "always" },
    "elevated": { "enabled": false }
  },
  "channels": {
    "whatsapp": { "dmPolicy": "pairing", "groups": { "*": { "requireMention": true } } }
  }
}
```

## Notes

- If you need remote access, prefer **SSH tunnelling** or **Tailscale Serve** rather than binding the Gateway to LAN/0.0.0.0.
- After changes, rerun: `openclaw security audit --deep`.
