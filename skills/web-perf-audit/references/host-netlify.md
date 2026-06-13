# Host Fixes: Netlify

## Cache state diagnosis (`cache-status`)

Netlify returns a multi-layer cache-status, e.g.:
`"Netlify Durable"; hit; ttl=..., "Next.js"; hit, "Netlify Edge"; fwd=miss`

| Signal | Meaning |
|---|---|
| `"Netlify Edge"; hit` | Served from edge PoP — fast path |
| `"Netlify Edge"; fwd=miss` | **Edge evicted the page** — request fell back to Durable cache or origin. Cause of bimodal TTFB (~150ms warm / 1.5–2.5s cold) |
| `"Netlify Durable"; hit` | Persistent cache saved an origin hit, but added latency vs edge |
| `"Next.js"; hit` | Framework-level cache hit |

## Fix: durable CDN caching

`Netlify-CDN-Cache-Control` controls Netlify's CDN, stripped before the browser:

```js
// next.config.js
async headers() {
  return [
    {
      source: '/(.*)',
      headers: [
        { key: 'Netlify-CDN-Cache-Control', value: 'public, durable, s-maxage=31536000, stale-while-revalidate=86400' },
        { key: 'Cache-Control', value: 'public, max-age=0, s-maxage=86400, stale-while-revalidate=300' },
      ],
    },
  ];
}
```

`durable` pins the object in Netlify's persistent cache across PoPs — eliminates the cold-edge path. ISR/on-demand revalidation still busts correctly via cache tags.

For non-Next.js (Vite SPA etc.), use a `_headers` file in the publish directory:

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

Vite's hashed `/assets/*` → always `immutable`. `index.html` must stay revalidatable (it points at the hashes).

## Double-proxy with Cloudflare

If `server: cloudflare` appears alongside Netlify headers, Cloudflare DNS is orange-clouded in front of Netlify — every request hops CF edge → Netlify edge. Observed adding **3+ seconds** of TTFB. `cf-cache-status: DYNAMIC` confirms CF adds latency without caching.

Fix: Cloudflare DNS → gray-cloud (DNS-only) the apex and www records. Apex: ALIAS/A to Netlify's load balancer (`75.2.60.5` or the apex `<site>.netlify.app` flattening); www: CNAME `<site>.netlify.app`. Netlify then serves directly with its own TLS.

## Domains

Netlify dashboard → Domain management: set primary domain, the alias auto-301s. Verify both `https://www.<domain>` and apex resolve — a missing www record is a real observed failure (users typing www get nothing).
