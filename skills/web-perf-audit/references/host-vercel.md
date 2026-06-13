# Host Fixes: Vercel

## Cache state diagnosis (`x-vercel-cache`)

| Value | Meaning | Action |
|---|---|---|
| HIT | Edge cache served | Good |
| STALE | Served stale while revalidating | Good (SWR working) |
| MISS | Not in cache, origin hit | Fine occasionally; frequent = caching misconfigured |
| PRERENDER | Static file from build | Good |
| REVALIDATED | ISR revalidation served fresh | Good |
| BYPASS | Cache deliberately skipped | Check why — cookies/headers forcing dynamic? |

Frequent MISS on a page that should be static usually means the route is accidentally dynamic — a `cookies()`, `headers()`, or `searchParams` access in a Next.js Server Component opts the whole route out of static rendering. Check the build output: routes marked `ƒ (Dynamic)` that should be `○ (Static)`.

## CDN caching headers

Vercel respects `Vercel-CDN-Cache-Control` (Vercel edge only) and `CDN-Cache-Control` (all CDNs), stripped before reaching the browser:

```js
// next.config.js
async headers() {
  return [
    {
      source: '/(.*)',
      headers: [
        { key: 'Vercel-CDN-Cache-Control', value: 'public, s-maxage=31536000, stale-while-revalidate=86400' },
        { key: 'Cache-Control', value: 'public, max-age=0, s-maxage=86400, stale-while-revalidate=300' },
      ],
    },
  ];
}
```

For non-Next.js (Vite SPA etc.), use `vercel.json`:

```json
{
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

Vite's hashed `/assets/*` output is content-addressed — always `immutable, max-age=31536000`. The `index.html` must NOT be long-cached (it's the pointer to the hashes): `max-age=0, s-maxage=86400, stale-while-revalidate`.

## Cold TTFB on Vercel

- Serverless function cold starts: visible as occasional 1–3s TTFB with `x-vercel-cache: MISS`. Mitigate by making routes static/ISR so the function rarely runs, or use Edge Runtime (`export const runtime = 'edge'`) for latency-sensitive dynamic routes.
- Region mismatch: functions default to `iad1` (US East). For SEA audiences set `regions: ["sin1"]` in vercel.json or `export const preferredRegion = 'sin1'`. Static/edge-cached content is global regardless — this only matters for dynamic routes.

## Domains

Vercel dashboard → Domains: add both apex and www, mark one primary — Vercel auto-307/308s the other. If DNS is on Cloudflare, records must be **gray-clouded (DNS-only)**; orange-cloud in front of Vercel creates the double-proxy pattern AND breaks Vercel's TLS issuance intermittently.
