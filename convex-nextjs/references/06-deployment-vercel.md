# Deployment (with Vercel focus)

## Core CLI commands
- Dev sync: `npx convex dev`
- Deploy to production: `npx convex deploy`
- Regenerate generated code: `npx convex codegen`

## Vercel recommended setup (typical)
1) In Vercel project settings, override Build Command to:
```bash
npx convex deploy --cmd 'npm run build'
```

2) Set the `CONVEX_DEPLOY_KEY` environment variable in Vercel:
- Production deploy key for Production builds.
- Preview deploy key for Preview builds (optional but recommended).

3) `npx convex deploy` will:
- Push Convex functions + schema/indexes
- Provide/set a `CONVEX_URL` (or similar) for the build step
- Run your frontend build via `--cmd`

## Preview deployments
- Create a new backend per preview by using preview deploy keys.
- Optional: run a setup function on preview deploy via:
  `npx convex deploy --cmd 'npm run build' --preview-run 'functionName'`

## Custom env var names
If your frontend expects a differently named env var, use:
```bash
npx convex deploy --cmd-url-env-var-name CUSTOM_CONVEX_URL --cmd 'npm run build'
```
