---
name: netlify-deploy
description: Deploy applications to Netlify. Use when the user says "deploy to Netlify", "netlify deploy", "publish to Netlify", "go live on Netlify", or "host on Netlify".
---

# Deploy to Netlify

Automates the full Netlify deployment workflow — from CLI check through live production URL.

---

## Step 1 — Check Netlify CLI

```bash
netlify --version 2>/dev/null || npm install -g netlify-cli
```

---

## Step 2 — Authenticate (first time)

```bash
netlify status 2>/dev/null | grep "Logged in" || netlify login
```

---

## Step 3 — Link Site (first time)

```bash
# Check if already linked
netlify status | grep "Current site"

# If not linked:
netlify link
# or create a new site:
netlify sites:create --name <site-name>
```

---

## Step 4 — Set Environment Variables

Before deploying, ensure all required env vars are set on Netlify:

```bash
# List current env vars
netlify env:list

# Set a variable
netlify env:set NEXT_PUBLIC_SUPABASE_URL "https://xxx.supabase.co"
netlify env:set NEXT_PUBLIC_SUPABASE_ANON_KEY "xxx"
netlify env:set SUPABASE_SERVICE_ROLE_KEY "xxx"
# etc.
```

**Never hardcode secrets in code.** If env vars are missing, stop and tell the user which ones to set.

---

## Step 5 — Build Validation

Run the build locally before deploying to catch errors early:

```bash
npm run build   # or: pnpm build / bun build
```

Fix any build errors before proceeding.

---

## Step 6 — Deploy

### Preview deployment (default)

```bash
netlify deploy
```

Reports a draft URL for review before going live.

### Production deployment

```bash
netlify deploy --prod
```

---

## Step 7 — Verify and Report

After deploy completes:

```bash
netlify status
```

Report to the user:
- Deploy URL (preview or production)
- Whether the deploy succeeded or failed
- Any build warnings to be aware of

If the deploy fails, show the build log output and suggest fixes.

---

## Common Issues

| Issue | Fix |
|---|---|
| Build fails with missing env var | Set it with `netlify env:set` and redeploy |
| "Site not found" | Run `netlify link` to connect to the correct site |
| Functions timing out | Check if API routes exceed Netlify's 10-second function timeout |
| `next/image` not working | Ensure `@netlify/next` adapter is installed for Next.js sites |
| Redirects not working | Check `netlify.toml` or `_redirects` file for redirect rules |

---

## netlify.toml Reference

For Next.js projects:

```toml
[build]
  command = "npm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"

[build.environment]
  NODE_VERSION = "20"
```

For React + Vite:

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```
