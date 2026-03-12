---
name: convex-nextjs
description: >-
  Build, refactor, debug, or review a Convex backend inside a Next.js app. Use
  when the user mentions Convex, `convex/nextjs`, `npx convex dev`,
  `NEXT_PUBLIC_CONVEX_URL`, `useQuery`, `useMutation`, `usePaginatedQuery`,
  schema/indexes, auth, App Router server components/actions, realtime data,
  chat, notifications, collaborative features, or deploying Convex with
  Vercel. Also use when deciding whether Convex is a good fit for a Next.js app
  that needs reactive shared state. Do not use for generic frontend-only
  Next.js work or non-Convex backends unless the task is specifically about
  adopting, migrating to, or evaluating Convex.
compatibility: >-
  Best for Next.js 13+ with the App Router and TypeScript, but works for Pages
  Router and mixed repos too. Assumes the Convex CLI is available via the
  `convex` npm package and the repo can run `npx convex ...`.
metadata:
  version: 2.0.0
  ecosystem: convex
  framework: nextjs
  focus:
    - progressive-disclosure
    - validation-first
    - realtime
    - current-convex-patterns
---

# Convex + Next.js

## Use this skill to
- Bootstrap Convex in a new or existing Next.js app.
- Add a feature end to end: schema, indexes, functions, UI hooks, auth, and deployment.
- Debug typical integration failures: missing provider, missing generated code, bad client/server boundaries, missing env vars.
- Review whether Convex is a good fit for a realtime or collaborative Next.js feature.

## Do not use this skill when
- The task is plain Next.js UI work with no Convex dependency.
- The backend is definitely not Convex and the user is not considering migration.
- The problem is generic database theory with no Next.js/Convex implementation work.

## Default posture
- Use `npx convex dev` for development.
- Keep reactive hooks in Client Components.
- Prefer indexed queries over `.filter(...)`.
- Treat unbounded lists as paginated by default.
- Put external I/O in actions; add `"use node"` only if Node APIs or unsupported packages are required.
- Require input validation on public functions; add return validation unless there is a good reason not to.
- Add explicit auth and ownership checks for user data.
- Prefer helper functions or custom wrappers when the same auth/tenant checks repeat.

## Starting questions to answer from the repo
1. Is this a new app, an existing Next.js app, or a migration?
2. App Router, Pages Router, or both?
3. Does the feature need reactivity, SSR, server actions, or all three?
4. Is the dataset bounded or should it paginate?
5. Is auth already present? If yes, is it client-only or needed on the server too?
6. Would a Convex component make this feature more reusable or isolated?

## Workflow 1 — Choose the right starting path

### A. Brand new project
Prefer:
```bash
npm create convex@latest
```

If the user already has a Next.js app structure they want to keep, use path B instead.

### B. Existing Next.js app
Install Convex and start dev sync:
```bash
npm install convex
npx convex dev
```

Expected outcomes:
- `convex/` exists, or the custom functions directory from `convex.json`
- generated files appear under `_generated/`
- a dev deployment or local deployment is connected
- `NEXT_PUBLIC_CONVEX_URL` is available for the frontend

See [references/01-setup-and-decision-tree.md](references/01-setup-and-decision-tree.md).

## Workflow 2 — Model data for query patterns, not screen shapes
Before writing UI, define:
- the tables
- the ownership fields
- the indexes needed for the main reads
- whether lists are bounded or paginated
- whether files should live in Convex File Storage instead of large documents

Rules:
- Prefer flat relational-style documents over deep nested blobs.
- Use `v.id("table")` for relationships.
- Add indexes for every repeated filter/sort path you know you need.
- If the query would scan an unbounded table, redesign the index or paginate it.

See [references/02-schema-and-indexes.md](references/02-schema-and-indexes.md).

## Workflow 3 — Pick the correct Convex function shape

### Query
Use for pure reads. Keep them small, indexed, and predictable.

### Mutation
Use for writes and transactional read-write logic.

### Action
Use for external APIs, long-running work, or non-transactional orchestration.
- Stay in the default Convex runtime if `fetch` is enough.
- Add `"use node"` only when you need Node-only APIs or unsupported packages.
- Files with `"use node"` should contain actions only.

Detailed patterns: [references/03-functions-and-safety.md](references/03-functions-and-safety.md)

## Workflow 4 — Enforce validation, auth, and ownership early
For public functions:
- define `args`
- usually define `returns`
- call `ctx.auth.getUserIdentity()` when the function is protected
- check ownership or team membership, not just authentication
- move repeated checks into helpers or custom wrappers once duplication starts to spread

If auth or tenant checks repeat in many functions, consider:
- `convex/lib/auth.ts` helpers
- thin wrappers/custom functions for `query`, `mutation`, or `action`
- shared policy helpers for tenant/resource checks

See [references/05-auth-and-access-control.md](references/05-auth-and-access-control.md).

## Workflow 5 — Respect Next.js boundaries
- `useQuery`, `useMutation`, `useAction`, `usePaginatedQuery`, and `usePreloadedQuery` belong in Client Components.
- For reactive-first pages with good first paint, use `preloadQuery` in a Server Component and `usePreloadedQuery` in a Client Component.
- For server-only reads, use `fetchQuery`.
- For Server Actions or Route Handlers, use `fetchMutation` or `fetchAction`.

Do not call React hooks from Server Components.

See [references/04-nextjs-client-and-server-boundaries.md](references/04-nextjs-client-and-server-boundaries.md).

## Workflow 6 — Treat large lists as a pagination problem
Use pagination by default when:
- the user says “all”, “feed”, “activity”, “history”, “messages”, “notifications”, “search results”, or “infinite scroll”
- the table can grow without a natural hard limit
- you would otherwise reach for `.collect()` on a user-facing list

Pattern:
- backend query uses `.paginate(paginationOpts)`
- React client uses `usePaginatedQuery`

See [references/06-pagination-performance-and-realtime.md](references/06-pagination-performance-and-realtime.md).

## Workflow 7 — Consider components when the feature wants isolation
A Convex component is often worth it when the feature:
- has its own schema, functions, and internal jobs
- should be reusable across apps
- would otherwise pollute the root `convex/` folder with tightly-coupled code

Use normal app code when the feature is small and specific to one app.

See [references/07-components-migrations-and-reuse.md](references/07-components-migrations-and-reuse.md).

## Workflow 8 — Choose the right development mode
- On your own machine or in a local coding agent, standard `npx convex dev` is usually right.
- In remote or background agents that cannot log in, use Agent Mode.
- For isolated local-only development, use local deployments.

See [references/08-local-dev-agent-mode-and-cloud-agents.md](references/08-local-dev-agent-mode-and-cloud-agents.md).

## Workflow 9 — Validate before you stop
Run:
```bash
python {baseDir}/scripts/validate_project.py --root .
```

Useful flags:
```bash
python {baseDir}/scripts/validate_project.py --root . --strict
python {baseDir}/scripts/validate_project.py --root . --json
```

The validator checks for the common failures this skill is designed to catch:
- missing Convex installation or generated code
- missing provider or env wiring
- hook usage in non-client components
- implicit table access
- `.collect()` or `.filter()` smells in queries
- missing validators on Convex functions
- risky `"use node"` file mixes
- scheduler calls aimed at public functions
- missing TypeScript strictness or missing Convex ESLint plugin

## Workflow 10 — Deploy cleanly
During normal development, keep using:
```bash
npx convex dev
```

For production or CI:
```bash
npx convex deploy
```

For Vercel builds, the common pattern is:
```bash
npx convex deploy --cmd "npm run build"
```

See [references/09-deploy-ci-and-vercel.md](references/09-deploy-ci-and-vercel.md).

## What a strong final implementation usually includes
- updated `convex/schema.ts`
- new or updated indexes
- public functions with `args` and usually `returns`
- auth or ownership checks where needed
- UI wired through the generated `api`
- `"use client"` only where it is actually needed
- paginated lists instead of unbounded collects
- a note about required env vars
- commands the user should run to verify the change

## Response shape to prefer when making code changes
1. State the files to add or edit.
2. Explain the architectural choice in one sentence.
3. Apply the code changes.
4. Run the validator or describe the exact checks to run.
5. Call out any follow-up env vars, auth setup, deploy steps, or migration concerns.

## Reference map
- Setup and choosing a path: [references/01-setup-and-decision-tree.md](references/01-setup-and-decision-tree.md)
- Schema and index design: [references/02-schema-and-indexes.md](references/02-schema-and-indexes.md)
- Functions, validation, Node actions, scheduler safety: [references/03-functions-and-safety.md](references/03-functions-and-safety.md)
- Next.js client/server boundaries and SSR: [references/04-nextjs-client-and-server-boundaries.md](references/04-nextjs-client-and-server-boundaries.md)
- Auth and access control: [references/05-auth-and-access-control.md](references/05-auth-and-access-control.md)
- Pagination, performance, and realtime: [references/06-pagination-performance-and-realtime.md](references/06-pagination-performance-and-realtime.md)
- Components, migrations, and reuse: [references/07-components-migrations-and-reuse.md](references/07-components-migrations-and-reuse.md)
- Local dev, Agent Mode, and local deployments: [references/08-local-dev-agent-mode-and-cloud-agents.md](references/08-local-dev-agent-mode-and-cloud-agents.md)
- Deploy and CI: [references/09-deploy-ci-and-vercel.md](references/09-deploy-ci-and-vercel.md)
- Troubleshooting and smoke tests: [references/10-troubleshooting-and-smoke-tests.md](references/10-troubleshooting-and-smoke-tests.md)
