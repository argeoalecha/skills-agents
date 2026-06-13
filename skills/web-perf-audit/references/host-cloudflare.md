# Host Fixes: Cloudflare (Pages / Workers / proxy-only)

Three distinct roles Cloudflare plays — diagnose which before fixing:

1. **Cloudflare Pages/Workers hosts the site** — only CF headers present, assets under `*.pages.dev` or custom domain
2. **Cloudflare proxies another host** (orange-cloud) — CF headers + Netlify/Vercel headers → **double-proxy, see below**
3. **Cloudflare is DNS-only** (gray-cloud) — no CF headers in responses; CF irrelevant to perf

## Double-proxy (role 2) — the critical fix

Symptom: `server: cloudflare` + another platform's headers, multi-second TTFB, `cf-cache-status: DYNAMIC` (CF not caching anything).

Fix — gray-cloud in Cloudflare DNS:
- Dashboard → DNS → click the orange cloud on apex and www records → "DNS only"
- Host platform (Netlify/Vercel) then terminates TLS and serves from its own CDN directly
- Keep Cloudflare for DNS/registrar; you lose CF's WAF/bot features on that hostname — acceptable for marketing sites, the host CDNs have their own protections

Only keep orange-cloud if you specifically need CF WAF/rate-limiting, and then configure CF Cache Rules to actually cache (otherwise it's pure added latency).

## Cloudflare Pages (role 1) fixes

Static assets are cached automatically and aggressively. HTML caching:

`_headers` file in build output:

```
/assets/*
  Cache-Control: public, max-age=31536000, immutable

/*
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  Permissions-Policy: camera=(), microphone=(), geolocation=()
```

`cf-cache-status` diagnosis:

| Value | Meaning |
|---|---|
| HIT | Edge served |
| MISS / EXPIRED | Origin/Pages hit — fine for first request per PoP |
| DYNAMIC | CF decided not to cache (default for HTML) — use Cache Rules to override for static HTML |
| BYPASS | Cookie/header forced bypass |

To cache HTML on CF: Dashboard → Caching → Cache Rules → match hostname, "Eligible for cache", Edge TTL e.g. 1 day. Pair with `stale-while-revalidate` semantics via Browser TTL settings.

## Managed robots.txt / AI bot blocking

Cloudflare's "block AI bots" feature injects `Disallow: /` for ClaudeBot, GPTBot, Google-Extended, CCBot, Bytespider, etc., on top of the site's own robots.txt. Consequences:
- Site disappears from AI search surfaces (Perplexity, ChatGPT browsing, Google AI Overviews)
- For businesses whose clients discover them via AI tools — or AI companies themselves — this is usually the wrong default

Toggle: Dashboard → Security → Bots → "Block AI bots" + managed robots.txt setting. Make it a deliberate decision; report it on every audit where found.

## Workers-specific

Cold starts are negligible (<5ms isolates) — Workers is not a cold-TTFB suspect. Slow Workers TTFB = slow upstream fetch or KV/D1 latency inside the worker. Use `caches.default` API to cache upstream responses at the edge.
