---
name: web-perf-audit
description: Audit and improve website performance, security headers, caching, and SEO for any live HTTPS site using curl-based online measurements — no Lighthouse or browser required. Host-agnostic with deep fixes for Vercel, Netlify, and Cloudflare Pages, plus local build auditing for Vite and Next.js projects. Use this skill whenever the user asks to check, audit, re-check, or improve the performance/speed of a website or URL, mentions TTFB, Core Web Vitals, slow loading, bundle size, caching, CDN, or edge issues, asks "what needs to improve" about a site, wants to verify a fix after a deploy, or wants to analyze a Vite/Next.js bundle locally before deploying.
---

# Web Performance Audit

Audit a live website's performance from the command line, identify the hosting platform, and deliver a prioritized fix list with platform-specific code. Also supports pre-deploy local bundle audits for Vite and Next.js projects.

## Two audit modes

| Mode | When | Entry point |
|---|---|---|
| **Online audit** | Live URL to check | `scripts/audit.sh <url>` |
| **Local build audit** | Repo available, pre-deploy check, or online audit found JS bloat | `references/local-build-audit.md` |

Run both when a repo is available — online finds delivery problems (TTFB, caching, headers), local finds build problems (bundle composition, chunk splitting) that online measurements can only flag, not explain.

## Online audit workflow

1. Run `scripts/audit.sh <url>` — collects timing samples, headers, payload, assets, SEO, robots in one pass. The script auto-detects the host platform and prints it.
2. Interpret against the thresholds below.
3. Read the host-specific reference for exact fixes:
   - `references/host-vercel.md`
   - `references/host-netlify.md`
   - `references/host-cloudflare.md`
   - Unknown host → use `references/host-generic.md` (standard Cache-Control, framework-level fixes)
4. If JS totals exceed thresholds and the repo is available, continue to `references/local-build-audit.md`.
5. Deliver the report in the standard format (below).

### Host detection signals (the script does this; verify manually if ambiguous)

| Header signal | Platform |
|---|---|
| `server: Vercel`, `x-vercel-id`, `x-vercel-cache` | Vercel |
| `cache-status: "Netlify Edge"`, `x-nf-request-id`, `netlify-vary` | Netlify |
| `server: cloudflare` + `cf-ray` ONLY (no Netlify/Vercel headers) | Cloudflare Pages/Workers |
| `server: cloudflare` + Netlify or Vercel headers both present | **Double-proxy — critical finding, see below** |
| `x-amz-cf-id`, `x-cache: ... cloudfront` | CloudFront (S3/Amplify) |
| `x-served-by`, `x-cache` with Fastly POPs | Fastly (often Netlify legacy) |
| `x-github-request-id` | GitHub Pages |

**Critical pattern — double-proxy:** Two CDN vendors in the same response (e.g. `server: cloudflare` + Netlify/Vercel headers) means DNS is proxied through Cloudflare in front of the host's own CDN. This adds seconds of TTFB for zero benefit (`cf-cache-status: DYNAMIC` confirms Cloudflare isn't caching). Fix: gray-cloud the DNS record so the host CDN serves directly, or consolidate onto one platform. This is the #1 root cause of multi-second TTFB on otherwise-fine sites.

**Critical pattern — bimodal TTFB:** Samples split into fast (~150ms) and slow (1.5s+) clusters = edge cache eviction; cold requests fall to origin. Confirm via cache headers (`fwd=miss` on Netlify, `x-vercel-cache: MISS/STALE` on Vercel, `cf-cache-status: MISS/EXPIRED` on Cloudflare). Never report TTFB as a single average — report the warm/cold split. Fix is platform-specific CDN cache configuration (see host references).

## Thresholds

| Metric | Good | Acceptable | Fix needed |
|---|---|---|---|
| TTFB (warm) | <200ms | <600ms | >600ms |
| TTFB (any cold sample) | <600ms | <1s | >1.5s |
| TLS handshake | <100ms | <300ms | >300ms |
| HTML payload | <50KB | <120KB | >150KB |
| Total JS (raw) | <300KB | <500KB | >600KB |
| Largest single JS chunk | <100KB | <150KB | >200KB |
| Fonts total | <60KB | <100KB | >100KB or >4 files |
| Inline hydration payload (RSC / `__NEXT_DATA__`) | <30KB | <60KB | >80KB |

For SEA/Philippine mobile audiences (a common target market), translate JS weight into real impact: ~600KB raw JS ≈ 2–4s parse+execute on mid-range Android over 4G. State this in reports — raw KB numbers don't land with business stakeholders.

## Security & SEO checklist (every audit, every report)

| Check | Pass condition |
|---|---|
| Content-Security-Policy | Present (most commonly missing header — flag every audit until fixed) |
| Strict-Transport-Security | max-age ≥ 31536000, includeSubDomains |
| X-Frame-Options | DENY or SAMEORIGIN (or CSP frame-ancestors) |
| X-Content-Type-Options | nosniff |
| Referrer-Policy | Present |
| Permissions-Policy | Present, restrictive |
| HTTP → HTTPS | 301 |
| www ↔ apex | Both resolve, redirect to one canonical (broken www DNS is a real observed failure) |
| Canonical, OG, Twitter meta | Present in HTML |
| sitemap.xml | 200, declared in robots.txt |
| robots.txt AI-crawler policy | Cloudflare's managed robots blocks ClaudeBot/GPTBot/Google-Extended by default — surface it as a deliberate decision, not a default: blocking removes the site from AI search surfaces (Perplexity, ChatGPT browsing, AI Overviews) |
| HTML cache-control | Flag `max-age=0, must-revalidate` on SSG/static pages; recommend `s-maxage` + `stale-while-revalidate` |

This checklist verifies **presence** at the HTTP layer. On-page SEO **quality** — unique per-route titles/descriptions, heading hierarchy, structured data (JSON-LD), alt text, CLS-causing markup, above-the-fold value proposition — is `/ux-review` Phase 5.5. Run both on marketing sites; don't duplicate its checks here.

## Tooling fallbacks

- **PageSpeed Insights API** is frequently quota-exhausted from shared environments (HTTP 429 with `quota_limit_value: 0`). Don't retry — the curl methodology gives equivalent actionable data.
- **web_fetch on the site** may 403 (bot blocking). Plain curl usually still works. If `audit.sh` itself gets 403s, re-run the failing curl with a browser User-Agent (`-A "Mozilla/5.0 ..."`) before concluding the site is down.
- **Lighthouse/headless Chrome** is unavailable in most sandboxes; this skill exists because of that. If the user has a browser, point them to PageSpeed Insights web UI for lab CWV to complement the curl data — but never block the audit on it.

## Report format

ALWAYS use this exact structure:

```
## Current State
(TTFB samples with warm/cold split, detected host, key metrics vs thresholds)

## What Needs to Improve — Prioritized
(numbered, biggest impact first; each item = concrete fix + code/config snippet for the detected host)

## Passing
(compact table — don't pad)

## Quick-Win Order
| # | Fix | Effort | Impact |
```

Rules:
- Lead with the single biggest problem. Don't bury multi-second TTFB under font nitpicks.
- Every fix gets the exact snippet for the **detected host** — not generic advice and not the wrong platform's config.
- Re-checks: always show before→after deltas, explicitly call out regressions and unfixed items ("flagged N times now").
- One audit history exists as a worked example: `references/case-study.md` (hayah-ai.com, 3 audits, Netlify+Cloudflare double-proxy → fix → cold-edge discovery). Read it when auditing sites built by the same developer/process, or as a template for tracking audit history on any site.

## TODO writeback (project repos only)

When the audited site's repo is the working directory (or the user owns it), append fix-needed findings to `TODO.md` as a new phase — same closure loop as `/audit`, `/load-test`, and `/ux-review`:

```markdown
## Phase X: Perf Remediation (YYYY-MM-DD)
Source: web-perf-audit — <url>
- [ ] [PERF] <finding> — <host-specific fix, one line>
- [ ] [SEC-HEADER] <missing header> — add via <platform config file>
```

Skip writeback when auditing an external site you don't control (client intake, competitor) — the report is the deliverable there.

## Integration points

- **Fed by `/company-site`, `/vercel-deploy`, `/netlify-deploy`** — run against the live URL after first production deploy
- **Pairs with `/ux-review`** — this skill measures the HTTP layer; its Phase 5.5 reviews the rendered markup/content. Findings here that need code changes (bundle bloat, unsized images found in local build audit) route to `/feature-dev` or `/ui-builder`
- **Pairs with `/load-test`** — this skill measures single-request delivery; `/load-test` measures behavior under concurrency. TTFB fine here but slow in production → load problem, not delivery problem
- **Feeds `/web-research`** — prospect-site audits become sales evidence in client intake reports

## Reference files

| File | Read when |
|---|---|
| `references/host-vercel.md` | Vercel detected — cache headers, vercel.json, ISR, x-vercel-cache states |
| `references/host-netlify.md` | Netlify detected — Netlify-CDN-Cache-Control durable, _headers, edge eviction |
| `references/host-cloudflare.md` | CF Pages/Workers detected, or double-proxy found — cache rules, _headers, gray-clouding |
| `references/host-generic.md` | Unknown/other host — standard headers, framework-level fixes |
| `references/local-build-audit.md` | Repo available — Vite (incl. Rolldown/Vite 8) + Next.js bundle analysis, vite preview testing, framework-agnostic budgets |
| `references/case-study.md` | Auditing a site from the same build process, or starting an audit-history log |
