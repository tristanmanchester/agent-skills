# Production hardening checklist for Expo + Convex

Use this before preview or production release.

## Environment and deployment

- [ ] `EXPO_PUBLIC_CONVEX_URL` exists locally and in the correct EAS environments.
- [ ] Preview and production builds point at the intended Convex deployments.
- [ ] Team members know which deployment maps to each build profile.
- [ ] `npx convex dev` is not the only place the deployment URL is documented.

## Provider and generated code

- [ ] Exactly one `ConvexReactClient` exists.
- [ ] The provider is mounted at the real app root.
- [ ] `convex/_generated/` is current and committed or ignored according to the team’s workflow.
- [ ] All frontend calls import from generated API references.

## Backend safety

- [ ] Public functions define `args`.
- [ ] Public functions expose deliberate `returns` where practical.
- [ ] Protected resources enforce authorization on the backend.
- [ ] Internal-only workflows use internal functions.
- [ ] All promises are awaited.
- [ ] External APIs or Node-only packages live in actions, not mutations or queries.

## Performance

- [ ] Large or growing lists use pagination.
- [ ] Heavy lookups use indexes rather than full scans.
- [ ] Queries do not rely on `Date.now()` or other nondeterministic time checks.
- [ ] Unbounded `.collect()` calls have been replaced where needed.
- [ ] Common ownership or tenant filters have matching indexes.

## Developer experience and maintainability

- [ ] TypeScript strict mode is enabled or there is a documented reason it is not.
- [ ] `@convex-dev/eslint-plugin` is installed and configured.
- [ ] The project runs lint and typecheck successfully.
- [ ] Repeated auth or tenancy logic has been centralised.
- [ ] Runtime boundaries are obvious: normal files vs `"use node"` action files.

## Expo UX

- [ ] Loading, empty, and error states exist for Convex-backed screens.
- [ ] Mutation pending states are acceptable on slow mobile networks.
- [ ] Offline or reconnect behaviour has been tested on device where relevant.
- [ ] Screens do not assume `useQuery` is immediately loaded.

## Files and media

- [ ] Uploads use upload URLs instead of forcing bytes through standard mutations.
- [ ] Metadata writes are awaited after uploads.
- [ ] Protected media queries and serving URLs are authorized.
- [ ] Large asset libraries paginate.

## Migration readiness

- [ ] Pending schema changes are additive or staged.
- [ ] Old clients will not break if they run against the new backend.
- [ ] Backfills are resumable and safe to re-run.

## Suggested commands

```bash
python scripts/validate_project.py --root <project-root> --fail-on-warning
cd <project-root> && npm run lint
cd <project-root> && npm run typecheck
```

Adjust the npm scripts to match the project.

## Final gut check

If someone new cloned the app and followed the documented setup, would they end up with:

- a working provider,
- a working deployment URL,
- a generated API folder,
- secure backend access patterns,
- and no obvious scaling traps?

If not, tighten the docs or the code before release.
