---
name: vercel-deploy
description: Deploy applications to Vercel. Use when the user says "deploy to Vercel", "vercel deploy", "publish to Vercel", "go live on Vercel", or "host on Vercel".
---

# Deploy to Vercel

Automates the full Vercel deployment workflow — from CLI check through live production URL.

---

## Step 1 — Check Vercel CLI

```bash
vercel --version 2>/dev/null || npm install -g vercel
```

---

## Step 2 — Authenticate (first time)

```bash
vercel whoami 2>/dev/null || vercel login
```

---

## Step 3 — Link Project (first time)

```bash
# Check if already linked
cat .vercel/project.json 2>/dev/null

# If not linked:
vercel link
```

---

## Step 4 — Set Environment Variables

Before deploying, ensure all required env vars are set on Vercel:

```bash
# List current env vars
vercel env ls

# Add a variable (prompts for value and environment)
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
vercel env add SUPABASE_SERVICE_ROLE_KEY

# Pull env vars to local .env.local for reference
vercel env pull .env.local
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
vercel
```

Reports a preview URL for review before going live.

### Production deployment

```bash
vercel --prod
```

---

## Step 7 — Verify and Report

After deploy completes, report to the user:
- Deploy URL (preview or production)
- Whether the deploy succeeded or failed
- Any build warnings to be aware of

```bash
vercel inspect <deploy-url>
```

If the deploy fails, show the build log output and suggest fixes.

---

## Step 8 — Post-Deploy Verification (production deploys)

After a `--prod` deploy, verify what is actually being served — config presence is not delivery:

```bash
bash ~/.claude/skills/web-perf-audit/scripts/audit.sh https://<production-domain>
```

Report against `/web-perf-audit` thresholds: TTFB (warm/cold split), security header gaps, cache-control on HTML and `/assets/*`, payload budgets. For fixes, read `~/.claude/skills/web-perf-audit/references/host-vercel.md`.

**Custom domain on Cloudflare DNS:** records MUST be gray-clouded (DNS-only). Orange-cloud in front of Vercel creates a double-proxy (multi-second TTFB, `cf-cache-status: DYNAMIC`) and intermittently breaks Vercel's TLS issuance. The audit script detects this automatically.

---

## Common Issues

| Issue | Fix |
|---|---|
| Build fails with missing env var | Add it with `vercel env add` and redeploy |
| "No project linked" | Run `vercel link` to connect to the correct project |
| Functions timing out | Check if API routes exceed Vercel's function timeout (default 10s, max 60s on Pro) |
| `next/image` not optimizing | Ensure `images.domains` or `images.remotePatterns` is set in `next.config.js` |
| Wrong Node.js version | Set `engines.node` in `package.json` or configure in Vercel project settings |
| Env var not available at build time | Use `NEXT_PUBLIC_` prefix for client-side vars; confirm it's added to the Build environment |

---

## vercel.json Reference

For Next.js projects (Vercel auto-detects, usually no config needed):

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "devCommand": "npm run dev"
}
```

For React + Vite (with caching + security headers — do not ship the bare version):

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
    },
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Content-Security-Policy", "value": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload" },
        { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()" }
      ]
    }
  ]
}
```

Vite's hashed `/assets/*` is content-addressed — always `immutable`. `index.html` must NOT be long-cached (it points at the hashes). Full caching rationale and Next.js `headers()` equivalent: `~/.claude/skills/web-perf-audit/references/host-vercel.md`.

For Express/Node API:

```json
{
  "builds": [{ "src": "src/index.ts", "use": "@vercel/node" }],
  "routes": [{ "src": "/(.*)", "dest": "src/index.ts" }]
}
```
