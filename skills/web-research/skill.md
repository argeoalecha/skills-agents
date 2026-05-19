---
name: web-research
description: Single-URL deep-dive investigation skill for client intake and pre-sales. Given a website URL, runs a phased investigation across the target site, domain/hosting, brand assets, social media (Facebook, Instagram, LinkedIn, X, TikTok, YouTube), Google Maps, SEO/authority signals, key people, news & reviews, and (optionally) competitive landscape. Produces a structured REPORT.md plus machine-readable data.json and screenshots/ under `~/projects-mvp/web-researches/<slug>/`. Three depth levels — quick · standard · thorough. Use when the user says "research this site", "do a deep dive on this URL", "investigate this company", "what can you tell me about example.com", "background on this prospect", "intake research for [client]", or "/web-research <url>".
user-invocable: true
---

# Web-Research — Single-URL Investigation

Deep, focused, structured intel on **one target URL** — for new client intake, prospect qualification, or proposal preparation. Not bulk scraping (see `/leads-scraper` for that). Not SEO pipeline (see `/seo-leads-gen` for that). One target, full picture, written report.

**Default framing:** client intake / pre-sales. The output is shaped to feed `/theme-client`, `/proposal-comm`, `/proposal-tech`, and `/web-dev` — but does not auto-invoke them. You decide the next step.

---

## Skill Root

All paths relative to: `~/.claude/skills/web-research/`

| Path | What it is |
|---|---|
| `assets/report-template.md` | `REPORT.md` skeleton with all sections + placeholders |
| `assets/data-template.json` | `data.json` schema for machine-readable findings |

**Output location:** `~/projects-mvp/web-researches/<slug>/` — never inside this skill folder.

---

## Relationship with sibling skills

| Skill | Boundary |
|---|---|
| **`/web-research`** (this) | **Single URL, deep dive, structured report.** Pre-sales / intake / proposal prep. |
| `/leads-scraper` | **Bulk** lead scraping by category + location. Many shallow records, no deep dive. |
| `/seo-leads-gen` | **Pipeline** that scrapes directories (Clutch, DesignRush, Legiit) for PH SEO agency leads, scores, enriches. Bulk pipeline, not single-target. |
| `/agent-browser` | **Browser automation primitive.** This skill uses it for JS-heavy pages and social profiles. |
| `/theme-client` | **Consumer** of `/web-research` output (brand colors, logo URL, fonts hint). Not auto-invoked — agent can copy fields manually. |
| `/proposal-comm` / `/proposal-tech` | **Consumer** of company profile, contact, location, industry. Not auto-invoked. |
| `/web-dev` | **Consumer** of tech stack, existing pages, content, contact for rebuild scoping. Not auto-invoked. |

---

## Phase 0 — Intake

Ask in one block:

1. **Target URL** (required) — full URL with scheme (e.g. `https://example.com`). If user gives a bare domain, prepend `https://`.
2. **Depth level** — `quick` · `standard` (default) · `thorough`.
3. **Project context** (optional) — "I'm pitching them", "client onboarding", "competitor analysis", "general curiosity". Shapes the executive summary framing.
4. **Slug** — kebab-case identifier for the output folder. Default: derive from domain (e.g. `acme-corp` from `acme-corp.com`).

After answers, **print a one-paragraph plan** of which phases will run for the chosen depth, then proceed without further confirmation **unless** the user picked `thorough` — in that case, confirm before Phase 9 (Competitive landscape).

### Depth → phases

| Phase | Quick | Standard | Thorough |
|---|---|---|---|
| 1. Target site | ✓ | ✓ | ✓ |
| 2. Domain, hosting & infrastructure | registrar + hosting only | full 5-bucket capture | + multi-page Lighthouse |
| 3. Brand assets | ✓ | ✓ | ✓ |
| 4. Social footprint | discover only | discover + fetch each profile | + deep metrics |
| 5. Google Maps | if applicable | ✓ | ✓ + photos + recent reviews |
| 6a. SEO performance (PageSpeed / Core Web Vitals) | mobile only | mobile + desktop | + 3 key pages, raw Lighthouse JSON |
| 6b. On-page SEO health | title + meta + H1 only | full audit on homepage | + audit on 2 more key pages |
| 6c. Crawlability & technical SEO | robots.txt + sitemap | full check | + HTTP/2 + compression + HSTS |
| 6d. SEO authority signals | — | search queries + directories | + backlinks teaser + DA estimate + broken-link sample |
| 7. People | — | founders + 2–3 key roles | + LinkedIn enrichment |
| 8. News & reviews | — | 3–5 recent mentions | + Trustpilot/Glassdoor/Reddit |
| 9. Competitive landscape | — | — | ✓ (3–5 similar sites, confirm first) |
| 10. Compile | ✓ | ✓ | ✓ |

---

## Phase 1 — Target site

Fetch and parse:

| Asset | How |
|---|---|
| `/` (homepage) | `WebFetch` → extract title, meta description, OG tags, canonical URL, primary H1, primary CTA copy, visible nav links |
| `/about`, `/about-us`, `/company`, `/team` | Try each; capture company story, founding year, mission, team list |
| `/contact`, `/contact-us` | Capture email, phone, address, contact-form fields |
| `/services`, `/products`, `/solutions`, `/pricing` | Capture service/product list with descriptions; pricing if visible |
| `/blog`, `/news`, `/insights` | Recent post count + 3 most recent titles + dates |
| `/robots.txt` | Note disallows, sitemap reference |
| `/sitemap.xml` (and `/sitemap_index.xml`) | Page count, top-level structure |
| Footer | Phone, address, social links, copyright year, legal links |

**Extract structured data:** any `<script type="application/ld+json">` blocks — these often contain Organization, LocalBusiness, Product schema.

**If the site is JS-rendered (React/Vue/Angular SPA with empty HTML body):** switch to `/agent-browser` to render and re-extract. Detect this when the homepage HTML has `<div id="root"></div>` or `<div id="__next"></div>` with no other content.

---

## Phase 2 — Domain, hosting & infrastructure

Run in parallel:

```bash
whois <domain>                       # registrar, registration date, expiry, name servers, abuse contact
dig +short <domain>                  # A records → IP
dig +short AAAA <domain>             # IPv6
dig +short NS <domain>               # name servers → DNS provider
dig +short MX <domain>               # mail provider (Google Workspace, M365, etc.)
dig +short TXT <domain>              # SPF, DMARC, verification tokens
curl -sI https://<domain> | head     # response headers — Server, CF-Ray, X-Powered-By
curl -s https://ipinfo.io/<ip>/json  # ASN → web hosting platform
```

### Capture in five distinct buckets

**1. Domain name provider (registrar)** — from `whois`:
- Registrar name (e.g. `GoDaddy.com, LLC`, `NameCheap, Inc.`, `Cloudflare, Inc.`, `Dynadot`, `Hostinger`)
- IANA registrar ID
- Registration date + expiry date (flag if expiry < 6 months out)
- WHOIS server
- Abuse contact email
- Privacy protection enabled (Y/N)

**2. DNS provider** — from `dig NS`:
- Name servers → infer provider. Examples:
  - `*.cloudflare.com` → Cloudflare DNS
  - `*.awsdns-*.com` → AWS Route 53
  - `*.googledomains.com` / `*.google.com` → Google Cloud DNS
  - `*.namecheap.com` → Namecheap Basic DNS
  - `*.godaddy.com` → GoDaddy DNS
  - `*.vercel-dns.com` → Vercel DNS
  - `*.netlify.com` → Netlify DNS

**3. Web hosting platform** — combine signals from response headers, A-record IP → ASN, and HTML fingerprints:

| Signal | Hosting platform |
|---|---|
| `x-vercel-id` or `x-vercel-cache` header | **Vercel** |
| `x-nf-request-id` or `server: Netlify` | **Netlify** |
| `x-amz-cf-pop` + `x-cache: ...CloudFront` | **AWS CloudFront / S3** |
| `x-served-by: cache-*.fastly` | **Fastly + origin** |
| `cf-ray` header but no other host signal | **Cloudflare Pages or Cloudflare in front of unknown** |
| ASN `AS16509 AMAZON` | **AWS (EC2 / Lightsail / Amplify)** |
| ASN `AS15169 GOOGLE` | **Google Cloud / Firebase Hosting** |
| ASN `AS8075 MICROSOFT` | **Azure Static Web Apps / App Service** |
| ASN `AS14061 DIGITALOCEAN` | **DigitalOcean** |
| `wpengine.com` or `wp-content/themes` + WPE headers | **WP Engine** |
| `kinsta.cloud` or Kinsta headers | **Kinsta** |
| `siteground.com` name server or `sgcdn.net` | **SiteGround** |
| `bluehost.com` name server | **Bluehost** |
| `hostinger.com` name server or `hstgr.io` | **Hostinger** |
| `wix.com` in OG image / CSS URL | **Wix** |
| `squarespace.com` in CSS URL | **Squarespace** |
| `__webflow` in HTML | **Webflow** |
| `framer-` class names + `framer.com` references | **Framer** |
| `myshopify.com` in URLs or `x-shopid` header | **Shopify** |
| `static.shopify.com` referenced | **Shopify** |

State **confidence level**: `High` (multiple signals agree) · `Medium` (one strong signal) · `Low` (heuristic guess from ASN only).

**4. Email provider** — from `dig MX`:

| MX record pattern | Provider |
|---|---|
| `*.google.com` / `aspmx.l.google.com` | **Google Workspace** |
| `*.outlook.com` / `*.mail.protection.outlook.com` | **Microsoft 365** |
| `*.zoho.com` / `*.zohomail.com` | **Zoho Mail** |
| `*.icloud.com` | **iCloud Mail (custom domain)** |
| `*.mailgun.org` | **Mailgun** (often transactional only) |
| `*.amazonses.com` | **AWS SES** (often transactional only) |
| `*.protonmail.ch` | **Proton Mail** |
| `mx.<domain>` self-hosted | **Self-hosted / unknown** |

**5. CDN** — from response headers (separate from hosting):

| Header | CDN |
|---|---|
| `cf-ray`, `cf-cache-status` | Cloudflare |
| `x-amz-cf-pop` | AWS CloudFront |
| `x-fastly-*`, `via: 1.1 varnish` | Fastly |
| `x-akamai-*`, `akamai-*` | Akamai |
| `x-bunny-cdn-cache` | Bunny CDN |
| `x-cdn: keycdn` | KeyCDN |

### CMS / framework fingerprint (separate from hosting)

| Signal | Stack |
|---|---|
| `<meta name="generator" content="WordPress …">` | WordPress |
| `wp-content/`, `wp-json/`, `wp-includes/` paths | WordPress |
| `<meta name="generator" content="Shopify">` | Shopify |
| `<script src=".../_next/static/...">` | Next.js |
| `<script src=".../_nuxt/...">` | Nuxt |
| `<script src=".../assets/index-*.js">` + Vite manifest | Vite (React/Vue) |
| `<div id="__next">` | Next.js |
| `<div id="__nuxt">` | Nuxt |
| `data-hk` / `data-server-rendered` | Vue SSR |
| Webflow data attributes | Webflow |

### Summary capture (write to data.json)

```
domain_provider:   { name, iana_id, registered, expiry, expiry_flag, abuse_contact, privacy_protected }
dns_provider:      { provider, name_servers[] }
hosting:           { platform, confidence, asn, ip, country }
email_provider:    { provider, mx_records[] }
cdn:               { provider, evidence }
cms_framework:     { name, version_hint }
ssl:               { issuer, expiry, valid }
```

---

## Phase 3 — Brand assets

Pull from the site:

| Asset | How |
|---|---|
| **Logo** | `<link rel="icon">`, `<img>` in nav/header (look for `logo` in src/alt). Save to `~/projects-mvp/web-researches/<slug>/assets/logo.{ext}`. If SVG inline, save as `logo.svg`. |
| **Favicon** | `/favicon.ico` or `<link rel="icon">` — save as `favicon.{ext}` |
| **OG image** | `<meta property="og:image">` — save as `og-image.{ext}` |
| **Primary colors** | Parse top 3 colors from CSS: scan `<style>` blocks + first linked stylesheet for `color`, `background`, `background-color`, `border-color` values. Report most-frequent 3 hex codes. |
| **Fonts** | Parse `font-family` declarations + `<link href="...fonts.googleapis.com...">` Google Fonts imports. List display + body font names. |
| **Tone signal** | Quick read of homepage H1 + first paragraph — note voice (formal / casual / technical / warm / bold). One adjective. |

This block is **directly feedable to `/theme-client`** — note that in the report's "Brand intake feed" section.

---

## Phase 4 — Social footprint

### Discover handles from the site

Scan footer, header, and `/contact` for outbound links to known social domains:

| Platform | Patterns |
|---|---|
| Facebook | `facebook.com/<handle>`, `fb.com/<handle>`, `m.facebook.com/<handle>` |
| Instagram | `instagram.com/<handle>` |
| LinkedIn | `linkedin.com/company/<handle>`, `linkedin.com/in/<handle>` |
| X / Twitter | `twitter.com/<handle>`, `x.com/<handle>` |
| TikTok | `tiktok.com/@<handle>` |
| YouTube | `youtube.com/@<handle>`, `youtube.com/c/<handle>`, `youtube.com/channel/<id>` |
| GitHub | `github.com/<handle>` |
| Threads | `threads.net/@<handle>` |

### Fetch each handle (standard + thorough)

For each handle found, in priority order **LinkedIn → Facebook → Instagram → X → TikTok → YouTube → GitHub**:

- **LinkedIn (company page):** name, headline, industry, size band, HQ location, follower count, recent post count if visible — use `WebFetch`. If gated, note "auth wall" and skip.
- **Facebook Page:** name, category, follower count, page-likes, contact info, hours, last-post date — use `/agent-browser` if the static page is empty.
- **Instagram:** handle, follower count, post count, bio, last-post date — JSON-LD often exposes this. Use `/agent-browser` if blocked.
- **X / Twitter:** handle, follower count, recent activity — note that X often requires auth; skip gracefully.
- **TikTok:** handle, follower count, like count — use `/agent-browser`.
- **YouTube:** channel name, subscribers, video count — typically scrapable.
- **GitHub:** username, repo count, public activity — JSON via `https://api.github.com/users/<handle>`.

**Thorough mode adds:** engagement rate estimate (follower count / last-3-posts likes if visible), posting cadence (last 5 post dates).

**Hard rule:** never attempt auth bypass. Public data only. If a profile is private, note "private" and move on.

---

## Phase 5 — Google Maps / physical presence

Only if the target appears to be a physical business (has visible address, is a local-business category, or `LocalBusiness` schema is present).

### Discovery

Search Google Maps for: `<business name> <city>` or `<business name> <visible address>`.

### Capture

- Canonical Google Maps URL (`maps.google.com/?cid=...` or `/place/...`)
- Name (as listed on Maps — may differ from website)
- Full address
- Phone (note if different from website's phone)
- Hours (full weekly schedule)
- Category (primary + secondary)
- Star rating (1–5 to one decimal)
- Review count
- Price level (`$`–`$$$$` if applicable)
- Website link (confirm it matches the target URL)
- Claimed status — note if "this business has not been claimed"
- Photo count
- "People also search for" — 3–5 nearby competitors

**Thorough mode adds:** 5 most recent reviews (date, rating, snippet — never quote full text without attribution), photos count by category.

Use `/agent-browser` (Maps is heavily JS-rendered). Note: rate limits exist; one search per target.

---

## Phase 6 — SEO: performance, on-page health & authority

Three sub-phases. All three run in Standard mode; thorough mode adds the deeper checks below.

### 6a. SEO performance (Core Web Vitals + PageSpeed)

Run Google PageSpeed Insights for **mobile and desktop** on the homepage (and 2 key pages in thorough mode):

```bash
# Public results URL — captures the full report
curl -sL "https://pagespeed.web.dev/api/run-pagespeed-insights?url=https%3A%2F%2F<domain>&strategy=mobile"
curl -sL "https://pagespeed.web.dev/api/run-pagespeed-insights?url=https%3A%2F%2F<domain>&strategy=desktop"

# Or via Google PSI API (free, no key for ≤25/day):
curl -sL "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https%3A%2F%2F<domain>&strategy=mobile&category=performance&category=seo&category=accessibility&category=best-practices"
```

**Capture per device (mobile + desktop):**

| Metric | Target | What it measures |
|---|---|---|
| **Performance score** | 90+ green, 50–89 orange, <50 red | Overall Lighthouse perf |
| **SEO score** | 90+ green | Lighthouse SEO category |
| **Accessibility score** | 90+ green | Lighthouse a11y category |
| **Best Practices score** | 90+ green | Lighthouse best practices |
| **LCP** (Largest Contentful Paint) | ≤ 2.5s good | Load speed |
| **INP** (Interaction to Next Paint) | ≤ 200ms good | Responsiveness (replaced FID in 2024) |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 good | Visual stability |
| **FCP** (First Contentful Paint) | ≤ 1.8s good | First paint |
| **TBT** (Total Blocking Time) | ≤ 200ms good | Main-thread blocking |
| **SI** (Speed Index) | ≤ 3.4s good | Above-fold visual progress |

**Verdict:** classify each Web Vital as `Good` / `Needs Improvement` / `Poor` per the Google thresholds above. Note the **3 biggest performance opportunities** PageSpeed flags (e.g. "Eliminate render-blocking resources — 1.2s savings").

**Thorough mode adds:** save raw Lighthouse JSON to `~/projects-mvp/web-researches/<slug>/lighthouse/{homepage,about,services}.{mobile,desktop}.json` via `npx lighthouse <url> --output=json --output-path=...` (if Node is available). Also runs PageSpeed against the 2 most-trafficked pages identified in Phase 1.

### 6b. On-page SEO health

Audit the homepage and 2 key pages (services / pricing / about — whichever exist):

| Check | What to capture | Pass threshold |
|---|---|---|
| **Title tag** | Present, length, contains brand | 30–60 chars |
| **Meta description** | Present, length, action verb | 120–160 chars |
| **H1 count** | Exactly 1 per page | =1 |
| **H1 content** | Includes primary keyword / value prop | qualitative |
| **Heading hierarchy** | H1 → H2 → H3 in order (no skips) | qualitative |
| **Image alt coverage** | % of `<img>` with non-empty `alt` | ≥ 90% |
| **Canonical tag** | `<link rel="canonical">` present, self-referencing | present |
| **Robots meta** | Not `noindex` on key pages | not `noindex` |
| **OG tags** | `og:title`, `og:description`, `og:image`, `og:url` | all 4 present |
| **Twitter Card** | `twitter:card`, `twitter:title`, `twitter:image` | all 3 present |
| **Viewport meta** | `<meta name="viewport" content="width=device-width...">` | present |
| **Structured data (JSON-LD)** | Types present (Organization, LocalBusiness, Product, Article, FAQPage, BreadcrumbList) | list types found |
| **Internal links** | Count from homepage | ≥ 10 |
| **External links** | Count + `rel="nofollow"` on sponsored | qualitative |
| **HTTPS only** | No `http://` resources loaded | no mixed content |
| **Hreflang** | If multilingual — `<link rel="alternate" hreflang="..." />` | applicable only |
| **Favicon** | Present | present |

### 6c. Crawlability & technical SEO

| Check | How |
|---|---|
| **robots.txt** | Fetch `/robots.txt` — valid syntax, sitemap reference present, doesn't block important paths |
| **Sitemap.xml** | Fetch `/sitemap.xml` and `/sitemap_index.xml` — valid XML, lastmod dates fresh, URL count |
| **Sitemap freshness** | Most recent `<lastmod>` date — flag if > 6 months stale |
| **HTTP → HTTPS redirect** | `curl -sI http://<domain>` should 301 → https |
| **WWW vs non-WWW canonicalization** | Both should resolve to one canonical (301 redirect) |
| **404 page** | Hit a known-bad URL — verify proper 404 status (not 200) |
| **HTTP/2 or HTTP/3** | From `curl -sI --http2` and `--http3` |
| **Compression** | `accept-encoding: gzip, br` honored |
| **HSTS** | `strict-transport-security` header present |

### 6d. SEO authority signals

| Source | What to capture |
|---|---|
| `site:<domain>` Google search | Indexed page count |
| `"<exact company name>"` | External mentions across the web |
| `"<domain>" -site:<domain>` | External mentions excluding the site itself |
| `"<company name>" review` | Review aggregator presence — Trustpilot, Yelp, G2 |
| `"<company name>" news` | Press mentions |
| `"<company name>" linkedin` | LinkedIn company + key employees |
| Wikipedia | `en.wikipedia.org/wiki/<company>` — does an entry exist? |
| Crunchbase | `crunchbase.com/organization/<slug>` — funding, founding, competitors |
| Clutch.co | If the target is an agency |
| AngelList / Wellfound | For startups |
| **PH directories** | `dti.gov.ph` business search, `securitiesandexchangecommission.ph` (for PH targets) |
| **PH-specific** | `bnews.ph`, `inquirer.net`, `rappler.com`, `bworldonline.com` mentions for PH-targeted brands |

### Thorough mode adds

- **Backlink teaser:** search Ahrefs Backlink Checker free tool, Moz Link Explorer free tier, or `link:<domain>` (deprecated but sometimes returns hits). Capture: visible backlink count, top 3 referring domains.
- **Domain authority proxy:** rough composite of indexed pages + domain age + visible mentions count. Note this is a heuristic, not a Moz/Ahrefs DA score.
- **Internal linking graph:** crawl up to 50 internal links from homepage, count inbound-link frequency per URL. Top 10 pages by inbound internal links.
- **Broken link sample:** check 20 random internal links — report HTTP status of each; flag any 4xx / 5xx.
- **Schema completeness:** for the detected `LocalBusiness` / `Organization` / `Product` schemas, note which recommended properties are missing per schema.org spec.

---

## Phase 7 — People

From the About / Team page (Phase 1) and LinkedIn discovery (Phase 4):

| Field | How |
|---|---|
| Founders / CEO | About page + LinkedIn "Founded by" / "Leadership" / Crunchbase founder field |
| Key roles | Look for CTO, COO, Head of Sales, Head of Engineering, Head of Marketing — note name + LinkedIn URL if available |
| Recent hires | Optional — LinkedIn "People at <company>" sorted by tenure |
| Decision-maker for the pitch | For client-intake framing: who would sign off on a website project? Usually CEO/founder (SMB), CMO (mid-market), CTO (tech-led) |

**Thorough mode adds:** background check on each named person — quick search for "<name> <company>" to surface notable past roles, interviews, articles.

**Never collect:** personal email addresses, phone numbers, home addresses, family info, or anything not voluntarily made public by the person in a professional context.

---

## Phase 8 — News & reviews

### News mentions

`WebSearch` queries:
- `"<company name>" news`
- `"<company name>" announcement`
- `"<company name>" funding` (for startups)
- `"<company name>" acquisition`

Capture: top 5 results in last 2 years. For each: source, date, headline, one-sentence summary.

### Review aggregators

| Platform | Relevance |
|---|---|
| **Google Reviews** | Already from Phase 5 (Maps) |
| **Trustpilot** | E-commerce, SaaS, consumer services |
| **Yelp** | Local businesses, restaurants (less relevant for PH) |
| **Glassdoor** | Employer reputation — useful intel for company culture |
| **G2 / Capterra** | B2B SaaS reviews |
| **Reddit** | Search `site:reddit.com "<company name>"` for unfiltered customer sentiment |

Capture: rating, review count, 3 most recent positive + 3 most recent negative review summaries. **Note unverified or astroturfing risk** if review volume spiked recently.

---

## Phase 9 — Competitive landscape (thorough mode only)

**Confirm with user before running** — this phase does the most external requests.

### Find competitors

- "People also search for" from Google Maps (Phase 5)
- Crunchbase "Competitors" list
- Search: `"<industry>" "<city or country>" companies`
- Manual: ask user "do you already know 2–3 direct competitors?"

### For each competitor (3–5 total)

Run a **mini Phase 1 + Phase 2** only: site title, tagline, primary CTA, visible pricing, tech stack, last-updated estimate. Do not go deeper.

### Output

Comparison table in REPORT.md:

| Criterion | Target | Competitor A | Competitor B | Competitor C |
|---|---|---|---|---|
| Tagline | … | … | … | … |
| Primary CTA | … | … | … | … |
| Pricing visible | Yes/No | Yes/No | Yes/No | Yes/No |
| Tech stack | … | … | … | … |
| Social presence | High/Med/Low | … | … | … |
| Unique positioning | … | … | … | … |

---

## Phase 10 — Compile

Write to `~/projects-mvp/web-researches/<slug>/`:

```
~/projects-mvp/web-researches/<slug>/
├── REPORT.md              # Human-readable report (use assets/report-template.md)
├── data.json              # Machine-readable findings (use assets/data-template.json)
├── sources.md             # Every URL fetched + timestamp — for verification & re-runs
├── assets/
│   ├── logo.{svg|png}     # Downloaded from target site
│   ├── favicon.ico
│   ├── og-image.{jpg|png}
│   └── screenshots/
│       ├── homepage.png   # Use /agent-browser to capture
│       ├── about.png
│       ├── pricing.png    # If exists
│       └── google-maps.png # If Phase 5 ran
└── lighthouse/            # Thorough mode only — raw PageSpeed / Lighthouse JSON + HTML
    ├── homepage.mobile.json
    ├── homepage.desktop.json
    ├── homepage.report.html
    ├── about.mobile.json
    └── services.mobile.json
```

**REPORT.md structure** (read `assets/report-template.md` for the full skeleton):

1. **Executive summary** — 5 bullets max. Most important findings up top.
2. **Company overview** — name, tagline, founded, location, industry, size estimate.
3. **Tech & hosting** — stack, host, CDN, mail, SSL, domain age, expiry flag.
4. **Web presence** — sitemap summary, key pages, content freshness.
5. **Brand assets** — logo URL, favicon, OG image, top 3 colors, fonts, voice. **Marked "feed into /theme-client".**
6. **Social footprint** — per-platform table with handle, follower count, last-active date.
7. **Google Maps / physical presence** — if applicable.
8. **SEO & authority** — indexed pages, key mentions, directory listings.
9. **People** — founders, key roles, decision-maker hypothesis.
10. **News & reviews** — recent mentions + reputation summary.
11. **Competitive landscape** — thorough mode only.
12. **Risk flags** — broken SSL, expiring domain, no contact info, dead social, negative review volume, etc.
13. **Recommended next steps** — for the chosen project context. Mentions which sibling skills could consume this report (no auto-invoke).
14. **Sources** — links to every page fetched, with retrieval timestamps.

---

## Tool selection per phase

| Phase | Primary tool | Fallback |
|---|---|---|
| 1. Target site | `WebFetch` | `/agent-browser` if SPA / empty HTML |
| 2. Domain, hosting & infrastructure | `Bash` (`whois`, `dig NS / MX / TXT`, `curl -sI`, `curl ipinfo.io/<ip>/json`) | `WebSearch` for "whois <domain>", "<domain> hosted on" |
| 3. Brand assets | `WebFetch` + `Bash` (`curl -O` for image download) | `/agent-browser` to screenshot brand sections |
| 4. Social footprint | `WebFetch` for static profiles | `/agent-browser` for JS-rendered profiles |
| 5. Google Maps | `/agent-browser` (always — Maps is JS-only) | — |
| 6a. SEO performance | `WebFetch` to `googleapis.com/pagespeedonline/v5/runPagespeed` | `Bash` (`npx lighthouse <url> --output=json`) for offline runs |
| 6b. On-page SEO health | Direct HTML parse from Phase 1 fetch | `/agent-browser` for JS-rendered pages |
| 6c. Crawlability | `WebFetch` for `/robots.txt`, `/sitemap.xml`; `Bash` (`curl -sI --http2`) | — |
| 6d. SEO authority | `WebSearch` | — |
| 7. People | `WebFetch` + `WebSearch` | `/agent-browser` for LinkedIn |
| 8. News & reviews | `WebSearch` | — |
| 9. Competitive landscape | Same as Phase 1+2 per competitor | — |
| 10. Compile | `Write` for files, `Bash` for `curl` of assets | — |

---

## Ethical & legal guardrails

- **Public data only.** Never attempt auth bypass, captcha defeat, or scraping behind paywalls.
- **Respect rate limits.** Default cadence: ≥ 1 second between requests to the same host. Don't parallelise requests to the same domain.
- **`robots.txt` is informational.** This skill is not bulk-crawling, so robots.txt blocks are noted in the report but don't necessarily halt research. If `robots.txt` explicitly forbids the path being requested, skip that path and note it.
- **No PII beyond business-public.** Founders' professional info (LinkedIn, About page) — OK. Personal phone, home address, family — not OK.
- **PH RA 10173 / GDPR awareness.** If the target is in the EU, UK, or PH and the research includes any individual's personal data beyond business-card-equivalent, note in the report that downstream use must comply with the applicable privacy law. For PH targets, flag `/ph-dpa-compliance` as relevant.
- **No competitive intel for malicious use.** Refuse if the framing implies sabotage, doxing, harassment, or unfair competition (price-fixing intel, employee poaching campaigns, etc.).
- **Attribution.** Every quoted line in the report has a source link. No paraphrased claims without a citation.

---

## Quality gates before declaring done

- [ ] `~/projects-mvp/web-researches/<slug>/REPORT.md` exists and renders cleanly
- [ ] `data.json` is valid JSON and matches the template schema
- [ ] At minimum, Phase 1 + 2 + 3 produced real data (no placeholders left in)
- [ ] **Phase 2:** registrar, DNS provider, hosting platform, email provider, CDN are all populated (state "Not detected" if no signal — never leave blank)
- [ ] **Phase 6a:** Core Web Vitals (LCP, INP, CLS) captured for mobile + Performance score + SEO score
- [ ] **Phase 6b:** On-page audit table filled — title, meta, H1, alt coverage, canonical, OG/Twitter, schema types
- [ ] **Phase 6c:** robots.txt + sitemap.xml status noted; HTTP→HTTPS redirect verified
- [ ] Every claim in REPORT.md has a source URL in the "Sources" section
- [ ] Risk flags section is filled out — even if empty, write "No flags detected"
- [ ] Logo + favicon + OG image saved locally (if available)
- [ ] At least 1 homepage screenshot saved
- [ ] No PII collected beyond business-public
- [ ] If Phase 9 ran, competitive comparison table is complete (no blank cells)

---

## Re-runs and freshness

Web research goes stale fast. The skill writes a `last_updated` field into `data.json`. When invoked on the same slug a second time:

- If `last_updated` is < 7 days old → ask the user if they want to re-fetch or use cached.
- If < 30 days → recommend incremental update (re-run Phase 1, 4, 8 only — those change most).
- If > 30 days → full re-run.

---

## Out of scope

- **Bulk lead scraping** — use `/leads-scraper`
- **PH SEO agency lead pipeline** — use `/seo-leads-gen`
- **Wikipedia editing** or any wiki-style contribution
- **Personal background checks** on private individuals — only business-public people
- **Financial deep dives** (P&L, balance sheet) — those need paid sources (Crunchbase Pro, PitchBook); we only capture the free signals
- **Trademark searches** — counsel
- **Source code analysis** of the target's web app — not part of intake research; that's a security engagement
- **Active scanning** (port scans, vuln scans, OSINT-tool runs against IP) — strictly out; this is read-only browsing
- **Generating outreach copy / cold emails** — produce the intel, hand off to user or `/proposal-comm`
