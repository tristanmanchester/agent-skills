# Deploy, CI, and Vercel

## Development vs production
- Use `npx convex dev` while building features.
- Use `npx convex deploy` for production or CI pushes.

## Standard production deploy
```bash
npx convex deploy
```

## Vercel pattern
A common build command is:
```bash
npx convex deploy --cmd "npm run build"
```

Set:
- `CONVEX_DEPLOY_KEY` in Vercel environment variables
- production key for production builds
- preview key for preview builds if you want isolated preview deployments

## Useful deploy options
Run a preview setup function:
```bash
npx convex deploy --cmd "npm run build" --preview-run "seed.preview"
```

Use a different env var name for the build step:
```bash
npx convex deploy   --cmd-url-env-var-name CUSTOM_CONVEX_URL   --cmd "npm run build"
```

## CI checklist
- install dependencies
- run typecheck or lint
- run `npx convex deploy`
- build the frontend through `--cmd` when the platform expects it
- confirm required runtime env vars exist for auth providers and third-party APIs

## Practical reminder
Deploying Convex and building Next.js are linked in production. Treat them as one pipeline, not two unrelated steps.
