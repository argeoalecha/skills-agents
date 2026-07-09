#!/usr/bin/env bash
# web-perf-audit: host-agnostic curl-based website performance audit
# Usage: bash audit.sh https://example.com
set -uo pipefail

URL="${1:?Usage: audit.sh https://example.com}"
HOST=$(echo "$URL" | sed -E 's#https?://##; s#/.*##')
TMP=$(mktemp -d)

echo "==================================================================="
echo " WEB PERF AUDIT: $URL  ($(date -u '+%Y-%m-%d %H:%M UTC'))"
echo "==================================================================="

echo ""
echo "=== 0. Host platform detection ==="
curl -sI --max-time 15 "$URL" -o "$TMP/headers.txt"
HDRS=$(tr -d '\r' < "$TMP/headers.txt" | tr '[:upper:]' '[:lower:]')
PLATFORMS=""
echo "$HDRS" | grep -qE "x-vercel-id|x-vercel-cache|^server: vercel" && PLATFORMS="$PLATFORMS Vercel"
echo "$HDRS" | grep -qE "x-nf-request-id|netlify" && PLATFORMS="$PLATFORMS Netlify"
echo "$HDRS" | grep -qE "^server: cloudflare|cf-ray" && PLATFORMS="$PLATFORMS Cloudflare"
echo "$HDRS" | grep -qE "x-amz-cf-id|cloudfront" && PLATFORMS="$PLATFORMS CloudFront"
echo "$HDRS" | grep -qE "x-served-by.*cache-|fastly" && PLATFORMS="$PLATFORMS Fastly"
echo "$HDRS" | grep -qE "x-github-request-id" && PLATFORMS="$PLATFORMS GitHub-Pages"
N=$(echo $PLATFORMS | wc -w)
echo "  Detected:${PLATFORMS:- unknown}"
if [ "$N" -gt 1 ]; then
  echo "  [CRITICAL] Multiple CDN vendors in one response → DOUBLE-PROXY."
  echo "             Likely Cloudflare orange-cloud in front of the host CDN."
  echo "             This is the #1 cause of multi-second TTFB. See host-cloudflare.md."
fi

echo ""
echo "=== 1. TTFB — 5 samples (watch for bimodal warm/cold split) ==="
for i in 1 2 3 4 5; do
  curl -s --max-time 20 -w "Run $i — DNS: %{time_namelookup}s | TLS: %{time_appconnect}s | TTFB: %{time_starttransfer}s | HTTP: %{http_code}\n" \
    -o /dev/null -D "$TMP/h$i.txt" "$URL"
  grep -iE "cache-status|cf-cache-status|x-vercel-cache|x-cache" "$TMP/h$i.txt" | sed 's/^/         /' | tr -d '\r'
  sleep 1
done
echo "  Cache state meanings: Vercel x-vercel-cache HIT/STALE ok, MISS/PRERENDER cold."
echo "  Netlify cache-status 'fwd=miss' = edge eviction. CF cf-cache-status DYNAMIC = not caching."

echo ""
echo "=== 2. Response headers (security + cache) ==="
grep -iE "^(server|cache-control|cdn-cache-control|vercel-cdn-cache-control|netlify-cdn-cache-control|cache-status|age|cf-cache-status|x-vercel-cache|x-nextjs|strict-transport|x-frame|x-content-type|content-security|permissions-policy|referrer-policy|content-encoding|alt-svc):" "$TMP/headers.txt" | tr -d '\r'

echo ""
echo "=== 3. Security header gaps ==="
for h in content-security-policy strict-transport-security x-frame-options x-content-type-options referrer-policy permissions-policy; do
  grep -qi "^$h:" "$TMP/headers.txt" && echo "  [OK]      $h" || echo "  [MISSING] $h"
done

echo ""
echo "=== 4. Redirects (www ↔ apex, http → https) ==="
APEX=${HOST#www.}
curl -sIL --max-time 10 -w "  www  → status %{http_code}, final: %{url_effective}\n" "https://www.$APEX" -o /dev/null 2>/dev/null || echo "  www  → FAILED (DNS gap?)"
curl -sIL --max-time 10 -w "  apex → status %{http_code}, final: %{url_effective}\n" "https://$APEX" -o /dev/null 2>/dev/null || echo "  apex → FAILED (DNS gap?)"
curl -sI  --max-time 10 -w "  http → status %{http_code}\n" "http://$APEX" -o /dev/null

echo ""
echo "=== 5. HTML payload ==="
curl -sL --max-time 20 "$URL" -o "$TMP/index.html"
BYTES=$(wc -c < "$TMP/index.html")
echo "  HTML size: $BYTES bytes ($((BYTES/1024)) KB)  [<50KB good, >150KB fix]"

echo ""
echo "=== 6. Asset inventory ==="
python3 - "$TMP/index.html" "$URL" <<'PYEOF'
import re, sys, subprocess

html_path, base = sys.argv[1], sys.argv[2].rstrip('/')
html = open(html_path, encoding='utf-8', errors='replace').read()

scripts = re.findall(r'<script[^>]*src=["\'](.*?)["\']', html)
fonts   = re.findall(r'href=["\']([^"\']*\.woff2?[^"\']*)["\']', html)
css     = re.findall(r'<link[^>]*stylesheet[^>]*>', html)
imgs    = re.findall(r'<img[^>]*src=["\'](.*?)["\']', html)

# Build tool fingerprint
tool = "unknown"
if '/_next/' in html: tool = "Next.js" + (" (Turbopack)" if 'turbopack' in html else "")
elif '/assets/' in html and re.search(r'assets/index-[\w-]+\.js', html): tool = "Vite"
elif '/_nuxt/' in html: tool = "Nuxt"
elif 'astro' in html[:3000].lower(): tool = "Astro (check)"
print(f"  Build tool fingerprint: {tool}")

def size_of(path):
    url = path if path.startswith('http') else base + ('' if path.startswith('/') else '/') + path
    try:
        out = subprocess.run(['curl','-s','-w','%{size_download}','-o','/dev/null','--max-time','15',url],
                             capture_output=True, text=True, timeout=20)
        return int(out.stdout.strip() or 0)
    except Exception:
        return 0

print(f"  JS chunks: {len(scripts)} | CSS: {len(css)} | Fonts: {len(fonts)} | Imgs in HTML: {len(imgs)}")

print("\n  JS chunk sizes (raw):")
js_total = 0
sized = []
for s in scripts:
    b = size_of(s)
    js_total += b
    sized.append((b, s.split('/')[-1][:50]))
for b, name in sorted(sized, reverse=True):
    flag = ' <-- LARGE' if b > 150000 else ''
    print(f"    {b:>9,} B  {name}{flag}")
print(f"    TOTAL JS: {js_total:,} B ({js_total//1024} KB)  [<300KB good, >600KB fix]")
if js_total > 600000:
    print("    → If repo available, run local build audit (references/local-build-audit.md)")

print("\n  Font sizes:")
f_total = 0
for f in fonts:
    b = size_of(f)
    f_total += b
    print(f"    {b:>9,} B  {f.split('/')[-1][:60]}")
print(f"    TOTAL fonts: {f_total:,} B ({f_total//1024} KB)  [<60KB good, >100KB fix]")

m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
if m:
    print(f"\n  __NEXT_DATA__ (Next.js Pages Router): {len(m.group(1)):,} B  [>80KB = review]")
else:
    rsc = re.findall(r'self\.__next_f\.push\(\[(.*?)\]\)', html, re.DOTALL)
    if rsc:
        total = sum(len(x) for x in rsc)
        print(f"\n  RSC inline payload (Next.js App Router): {total:,} B ({total//1024} KB) in {len(rsc)} pushes  [>80KB = review]")
PYEOF

echo ""
echo "=== 7. SEO essentials ==="
python3 - "$TMP/index.html" <<'PYEOF'
import re, sys
html = open(sys.argv[1], encoding='utf-8', errors='replace').read()
checks = {
    'title': r'<title[^>]*>(.+?)</title>',
    'meta description': r'name=["\']description["\']',
    'canonical': r'rel=["\']canonical["\']',
    'og:title': r'property=["\']og:title["\']',
    'og:image': r'property=["\']og:image["\']',
    'twitter:card': r'name=["\']twitter:card["\']',
    'viewport': r'name=["\']viewport["\']',
}
for name, pat in checks.items():
    print(f"  [{'OK' if re.search(pat, html) else 'MISSING'}] {name}")
PYEOF

echo ""
echo "=== 8. robots.txt & sitemap ==="
ROBOTS=$(curl -s --max-time 10 "https://$HOST/robots.txt")
if [ -n "$ROBOTS" ]; then
  echo "  robots.txt: present"
  echo "$ROBOTS" | grep -qi "sitemap:" && echo "  sitemap declared in robots.txt" || echo "  [WARN] no sitemap in robots.txt"
  for bot in ClaudeBot GPTBot Google-Extended CCBot; do
    echo "$ROBOTS" | grep -qi "$bot" && echo "  [NOTE] $bot referenced — check intent (affects AI search visibility)"
  done
else
  echo "  [MISSING] robots.txt"
fi
SM=$(curl -sI --max-time 10 -w "%{http_code}" "https://$HOST/sitemap.xml" -o /dev/null)
echo "  sitemap.xml: HTTP $SM"

echo ""
echo "==================================================================="
echo " Done. Next: read references/host-<detected-platform>.md for fixes."
echo " Bimodal TTFB? Check cold-cache markers in section 1."
echo " JS over budget + repo available? → references/local-build-audit.md"
echo "==================================================================="
rm -rf "$TMP"
