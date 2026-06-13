# Host Fixes: Generic / Unknown Platform

When the platform isn't Vercel/Netlify/Cloudflare, fixes apply at three levels: standard HTTP headers, the framework, and DNS.

## Standard cache headers (work everywhere)

| Asset type | Cache-Control |
|---|---|
| Hashed/fingerprinted assets (`app.3f2a1b.js`, Vite `/assets/*`) | `public, max-age=31536000, immutable` |
| HTML (SSG/static) | `public, max-age=0, s-maxage=86400, stale-while-revalidate=300` |
| HTML (truly dynamic, personalized) | `private, no-cache` |
| Images (stable) | `public, max-age=86400, stale-while-revalidate=604800` |
| Fonts | `public, max-age=31536000, immutable` |

`CDN-Cache-Control` is the cross-CDN standard for CDN-only directives (supported by Vercel, Cloudflare, Fastly; Netlify uses its prefixed variant). Set it alongside `Cache-Control` when you want long CDN TTL but short browser TTL.

## Security headers (set wherever headers are configurable: nginx, Apache, CDN rules, framework)

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

nginx example:

```nginx
location /assets/ {
  add_header Cache-Control "public, max-age=31536000, immutable";
}
location / {
  add_header Cache-Control "public, max-age=0, s-maxage=86400, stale-while-revalidate=300";
  add_header Content-Security-Policy "default-src 'self'; ..." always;
  add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
}
gzip on; gzip_types text/html text/css application/javascript application/json image/svg+xml;
# or better: brotli on;
```

## TTFB causes outside CDN config

- No CDN at all (single origin server far from users) → put any CDN in front, or move static output to one
- Origin compute on every request (no page caching in WordPress/Django/etc.) → enable full-page caching
- Slow TLS (no session resumption, RSA-only certs) → enable TLS 1.3, OCSP stapling
- DNS slow (>150ms lookups) → use a major DNS provider

## Always verify regardless of host

- HTTP→HTTPS 301, www↔apex canonical redirect
- Compression active (`content-encoding: br` or `gzip`) — missing compression on a 600KB JS bundle is a 3–4× transfer penalty
- HTTP/2 or HTTP/3 (`alt-svc: h3`)
