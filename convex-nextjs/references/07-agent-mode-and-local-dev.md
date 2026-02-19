# Agent Mode & local development

## When to use these
- You're running Convex CLI in a cloud agent that **can't log in**.
- You need isolated development environments (no conflicts with your local dev deployment).
- You want faster dev loops without syncing to the cloud.

## Agent Mode (anonymous)
Set:
```bash
CONVEX_AGENT_MODE=anonymous npx convex dev
```

This makes the CLI use an anonymous development deployment in the agent environment.

## Local deployments
Run a local backend:
```bash
npx convex dev --local --once
```

Notes:
- The local backend runs as a subprocess of `npx convex dev` and stops when the command stops.
- Local deployments are for development, not production.

## Suggested “agent bootstrap script”
```bash
npm i
CONVEX_AGENT_MODE=anonymous npx convex dev --once
npm test
```
