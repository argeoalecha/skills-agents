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

## Step 8 — Post-Deploy Verification (production deploys)

After a `--prod` deploy, verify what is actually being served — config presence is not delivery:

```bash
bash ~/.claude/skills/web-perf-audit/scripts/audit.sh https://<production-domain>
```

Report against `/web-perf-audit` thresholds: TTFB (warm/cold split — watch for `"Netlify Edge"; fwd=miss` edge eviction), security header gaps, cache-control on HTML and `/assets/*`, payload budgets. For fixes, read `~/.claude/skills/web-perf-audit/references/host-netlify.md`.

**Custom domain on Cloudflare DNS:** records MUST be gray-clouded (DNS-only). Orange-cloud in front of Netlify creates a double-proxy — observed adding 3+ seconds of TTFB with `cf-cache-status: DYNAMIC` (Cloudflare not caching anything). The audit script detects this automatically. Also verify BOTH `https://www.<domain>` and apex resolve — a missing www DNS record is a real observed failure.

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

**Always ship a `_headers` file in the publish directory** (caching + security — the bare toml above is not enough):

```
/assets/*
  Cache-Control: public, max-age=31536000, immutable

/*
  Netlify-CDN-Cache-Control: public, durable, s-maxage=31536000, stale-while-revalidate=86400
  Cache-Control: public, max-age=0, s-maxage=86400, stale-while-revalidate=300
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  Permissions-Policy: camera=(), microphone=(), geolocation=()
```

`durable` pins objects in Netlify's persistent cache across PoPs — eliminates the cold-edge eviction path (bimodal TTFB). For Next.js, set the same via `headers()` in `next.config.js` — see `~/.claude/skills/web-perf-audit/references/host-netlify.md`.
