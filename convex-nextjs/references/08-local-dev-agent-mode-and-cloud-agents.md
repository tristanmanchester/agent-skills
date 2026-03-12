# Local dev, Agent Mode, and cloud agents

## Normal local development
For work on your own machine, start with:
```bash
npx convex dev
```

That is the default path unless the environment cannot log in or you explicitly want a local-only backend.

## Local deployments
For a local backend process:
```bash
npx convex dev --local --once
```

Notes:
- the local backend runs as a subprocess of `npx convex dev`
- if the command stops, the backend stops too
- this is for development, not production

## Remote or background coding agents
When the agent cannot log in interactively, use Agent Mode:
```bash
CONVEX_AGENT_MODE=anonymous npx convex dev --once
```

A common setup script in cloud agents is:
```bash
npm i
CONVEX_AGENT_MODE=anonymous npx convex dev --once
npm test
```

## Local coding agents on your own machine
If the agent runs locally on your machine, standard `npx convex dev` is usually enough because it can use your existing local credentials and dev environment.

## Choosing between the modes
- **Your laptop / local editor agent**: `npx convex dev`
- **Remote agent with no login**: Agent Mode
- **Need a local-only backend**: `npx convex dev --local`
