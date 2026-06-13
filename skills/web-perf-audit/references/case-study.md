# Case Study: hayah-ai.com (May–June 2026)

Worked example of the audit→fix→re-audit loop. Stack: Next.js App Router (Turbopack) on Netlify, Cloudflare DNS. Sites built with the same process tend to repeat these exact defects — treat this as the expected-defect checklist for sibling sites, and as the template for keeping audit history on any site.

## Audit 1 (initial)
| Finding | Value | Root cause |
|---|---|---|
| TTFB 3.44s on cache HIT | CRITICAL | **Double-proxy**: Cloudflare orange-cloud in front of Netlify (`server: cloudflare` + Netlify headers, `cf-cache-status: DYNAMIC`) |
| www broken | No resolution | Missing DNS record |
| CSP missing | Gap | Never configured |
| HTML `max-age=0, must-revalidate` | Browser can't cache | Framework default left in place |
| HTML 181KB, 13 JS chunks, 5 font preloads | Heavy | Unanalyzed Turbopack output |
| robots.txt blocks ClaudeBot/GPTBot/Google-Extended | Strategic flag | Cloudflare managed robots default |

## Audit 2 (~2 weeks later, after fixes)
- TTFB **3.44s → 0.13–0.17s (−96%)** — double-proxy resolved
- www fixed
- CSP **still missing** (flagged 2×)
- 3 samples all looked warm — *insufficient sampling masked a remaining problem*

## Audit 3 (12 days later, 8 samples)
- TTFB revealed as **bimodal**: 0.13–0.17s warm, **1.4–2.4s cold** with `"Netlify Edge"; fwd=miss` — edge eviction, fixable with durable CDN caching (one header)
- JS measured properly: **656KB raw**, dominant chunk 232KB → bundle analysis required
- Fonts: 108KB / 5 files → subsetting needed
- RSC inline payload: 80KB (structural, deferred)
- CSP **still missing** (flagged 3×)

## Lessons (apply to every audit)

1. **≥5 TTFB samples always.** 3 samples declared victory in audit 2; 8 samples in audit 3 exposed the cold path.
2. **Check for double-proxy first** on any multi-second TTFB — it's the highest-impact, lowest-effort fix (one DNS toggle).
3. **Cold-cache markers** (`fwd=miss`, `x-vercel-cache: MISS`, `cf-cache-status: MISS`) mean CDN cache persistence isn't configured — one header fixes it per platform.
4. **CSP doesn't ship unless escalated.** Count and report repeat findings.
5. **Bundle analysis is mandatory** on every new site from a shared codebase/process — the same dominant-chunk pattern recurs.
6. **AI-crawler robots blocks** are surfaced every audit as a deliberate business decision, never accepted silently.

## Standing priority order for new sites from this process

1. No double-proxy (DNS check)
2. CDN durable/persistent cache header for the platform
3. CSP
4. Bundle analysis → trim dominant chunk
5. Font subsetting (≤4 files, latin subset)
6. Inline hydration payload (only during restructures)
