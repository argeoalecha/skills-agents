# Web Research Report — {{company-name}}

**Target URL:** {{target-url}}
**Retrieved:** {{iso-date}}
**Depth:** {{depth-level}}
**Slug:** `{{slug}}`
**Project context:** {{project-context}}

---

## Executive summary

- {{summary-bullet-1}}
- {{summary-bullet-2}}
- {{summary-bullet-3}}
- {{summary-bullet-4}}
- {{summary-bullet-5}}

**Headline take:** {{one-line-take}}

---

## 1. Company overview

| Field | Value |
|---|---|
| Legal / brand name | {{company-name}} |
| Tagline | {{tagline}} |
| Industry | {{industry}} |
| Founded | {{founded}} |
| HQ location | {{hq-location}} |
| Estimated size | {{size-band}} (e.g. 1–10, 11–50, 51–200) |
| Languages on site | {{languages}} |
| Primary CTA | {{primary-cta}} |

**Company story (from About page):**

{{about-summary}}

---

## 2. Tech, hosting & infrastructure

### Domain name provider (registrar)

| Field | Value |
|---|---|
| Registrar | **{{registrar}}** (IANA ID {{iana-id}}) |
| Registered | {{domain-registered}} ({{domain-age}}) |
| Expiry | {{domain-expiry}} {{expiry-flag}} |
| Privacy protection | {{privacy-protected}} |
| Abuse contact | {{abuse-contact}} |
| WHOIS server | {{whois-server}} |

### DNS provider

| Field | Value |
|---|---|
| Provider | **{{dns-provider}}** |
| Name servers | {{name-servers}} |

### Web hosting platform

| Field | Value |
|---|---|
| Platform | **{{hosting-provider}}** ({{hosting-confidence}} confidence) |
| Origin IP | {{origin-ip}} |
| ASN | {{asn}} |
| Country | {{hosting-country}} |
| Evidence | {{hosting-evidence}} |

### Email provider

| Field | Value |
|---|---|
| Provider | **{{mail-provider}}** |
| MX records | {{mx-records}} |
| SPF / DMARC | {{spf-dmarc-status}} |

### CDN

| Field | Value |
|---|---|
| Provider | {{cdn}} |
| Evidence | {{cdn-evidence}} |

### CMS / framework

| Field | Value |
|---|---|
| Framework / CMS | **{{tech-stack}}** (version: {{tech-version}}) |
| Analytics detected | {{analytics-tools}} |
| SSL issuer + expiry | {{ssl-info}} |

---

## 3. Web presence

| Page | Status | Notes |
|---|---|---|
| `/` | {{home-status}} | {{home-notes}} |
| `/about` | {{about-status}} | {{about-notes}} |
| `/services` or `/products` | {{services-status}} | {{services-notes}} |
| `/pricing` | {{pricing-status}} | {{pricing-notes}} |
| `/contact` | {{contact-status}} | {{contact-notes}} |
| `/blog` or `/news` | {{blog-status}} | {{blog-notes}} |

**Sitemap summary:** {{sitemap-summary}} (approx {{indexed-page-count}} pages)

**Content freshness:** {{content-freshness}}

**Contact captured:**
- Email: {{email}}
- Phone: {{phone}}
- Address: {{address}}

**Services / products listed:**

{{services-list}}

**Pricing visible:** {{pricing-visible}}

---

## 4. Brand assets — feed into `/theme-client`

| Asset | Value / Path |
|---|---|
| Logo | `~/projects-mvp/web-researches/{{slug}}/assets/logo.{{logo-ext}}` |
| Favicon | `~/projects-mvp/web-researches/{{slug}}/assets/favicon.ico` |
| OG image | `~/projects-mvp/web-researches/{{slug}}/assets/og-image.{{og-ext}}` |
| Primary color (most-used) | `{{primary-color}}` |
| Secondary color | `{{secondary-color}}` |
| Accent color | `{{accent-color}}` |
| Display font | {{display-font}} |
| Body font | {{body-font}} |
| Voice / tone | {{voice-adjective}} |

**Ready to seed `/theme-client`?** Run `/theme-client` and pass these values as the intake inputs. The logo SVG/PNG is already saved locally.

---

## 5. Social footprint

| Platform | Handle | Followers | Posts / activity | Last active | URL |
|---|---|---|---|---|---|
| LinkedIn | {{linkedin-handle}} | {{linkedin-followers}} | {{linkedin-posts}} | {{linkedin-last}} | {{linkedin-url}} |
| Facebook | {{fb-handle}} | {{fb-followers}} | {{fb-posts}} | {{fb-last}} | {{fb-url}} |
| Instagram | {{ig-handle}} | {{ig-followers}} | {{ig-posts}} | {{ig-last}} | {{ig-url}} |
| X / Twitter | {{x-handle}} | {{x-followers}} | {{x-posts}} | {{x-last}} | {{x-url}} |
| TikTok | {{tiktok-handle}} | {{tiktok-followers}} | {{tiktok-posts}} | {{tiktok-last}} | {{tiktok-url}} |
| YouTube | {{yt-handle}} | {{yt-subscribers}} | {{yt-videos}} | {{yt-last}} | {{yt-url}} |
| GitHub | {{gh-handle}} | {{gh-repos}} | {{gh-activity}} | {{gh-last}} | {{gh-url}} |

**Social strategy read:** {{social-summary}} (e.g. "LinkedIn-led for B2B, dormant on consumer channels")

---

## 6. Google Maps / physical presence

{{maps-applicable-or-na}}

| Field | Value |
|---|---|
| Google Maps URL | {{maps-url}} |
| Name (as listed) | {{maps-name}} |
| Address | {{maps-address}} |
| Phone | {{maps-phone}} |
| Hours | {{maps-hours}} |
| Category | {{maps-category}} |
| Rating | {{maps-rating}} ★ ({{maps-review-count}} reviews) |
| Price level | {{maps-price}} |
| Claimed | {{maps-claimed}} |
| Photo count | {{maps-photo-count}} |
| Nearby competitors | {{maps-also-search-for}} |

**Review sentiment summary:** {{maps-sentiment}}

---

## 7. SEO — performance, on-page health & authority

### 7a. SEO performance (Core Web Vitals + PageSpeed)

| Metric | Mobile | Desktop | Verdict |
|---|---|---|---|
| **Performance score** | {{psi-perf-mobile}} | {{psi-perf-desktop}} | {{psi-perf-verdict}} |
| **SEO score** | {{psi-seo-mobile}} | {{psi-seo-desktop}} | {{psi-seo-verdict}} |
| **Accessibility score** | {{psi-a11y-mobile}} | {{psi-a11y-desktop}} | {{psi-a11y-verdict}} |
| **Best Practices score** | {{psi-bp-mobile}} | {{psi-bp-desktop}} | {{psi-bp-verdict}} |
| LCP (Largest Contentful Paint) | {{lcp-mobile}} | {{lcp-desktop}} | {{lcp-verdict}} |
| INP (Interaction to Next Paint) | {{inp-mobile}} | {{inp-desktop}} | {{inp-verdict}} |
| CLS (Cumulative Layout Shift) | {{cls-mobile}} | {{cls-desktop}} | {{cls-verdict}} |
| FCP (First Contentful Paint) | {{fcp-mobile}} | {{fcp-desktop}} | {{fcp-verdict}} |
| TBT (Total Blocking Time) | {{tbt-mobile}} | {{tbt-desktop}} | {{tbt-verdict}} |

**Top 3 performance opportunities (mobile):**

1. {{psi-opp-1}} — savings: {{psi-opp-1-savings}}
2. {{psi-opp-2}} — savings: {{psi-opp-2-savings}}
3. {{psi-opp-3}} — savings: {{psi-opp-3-savings}}

**PageSpeed report URL:** {{psi-report-url}}

### 7b. On-page SEO health

| Check | Homepage | {{key-page-2-name}} | {{key-page-3-name}} |
|---|---|---|---|
| Title tag length | {{title-len-1}} | {{title-len-2}} | {{title-len-3}} |
| Meta description length | {{meta-len-1}} | {{meta-len-2}} | {{meta-len-3}} |
| H1 count | {{h1-count-1}} | {{h1-count-2}} | {{h1-count-3}} |
| Image alt coverage | {{alt-cov-1}}% | {{alt-cov-2}}% | {{alt-cov-3}}% |
| Canonical tag | {{canonical-1}} | {{canonical-2}} | {{canonical-3}} |
| Robots meta | {{robots-meta-1}} | {{robots-meta-2}} | {{robots-meta-3}} |
| OG tags complete | {{og-1}} | {{og-2}} | {{og-3}} |
| Twitter Card complete | {{tw-1}} | {{tw-2}} | {{tw-3}} |
| Viewport meta | {{vp-1}} | {{vp-2}} | {{vp-3}} |
| Internal links count | {{intlinks-1}} | {{intlinks-2}} | {{intlinks-3}} |

**Structured data (JSON-LD) detected:** {{schema-types}}

**On-page summary:** {{onpage-summary}}

### 7c. Crawlability & technical SEO

| Check | Status |
|---|---|
| `robots.txt` valid + sitemap referenced | {{robots-status}} |
| `sitemap.xml` present + URL count | {{sitemap-status}} ({{sitemap-url-count}} URLs) |
| Most recent `<lastmod>` date | {{sitemap-freshness}} |
| HTTP → HTTPS redirect | {{http-redirect}} |
| WWW vs non-WWW canonical | {{www-canonical}} |
| 404 page returns proper status | {{four-oh-four-status}} |
| HTTP/2 support | {{http2}} |
| HTTP/3 support | {{http3}} |
| Compression (gzip / brotli) | {{compression}} |
| HSTS header | {{hsts}} |

### 7d. SEO authority signals

| Signal | Value |
|---|---|
| Indexed pages (Google `site:` query) | ~{{indexed-pages}} |
| Total external mentions visible | {{mention-count}} |
| Wikipedia entry | {{wikipedia}} |
| Crunchbase profile | {{crunchbase-url}} |
| Industry directories | {{directory-listings}} |
| PH gov registrations (DTI / SEC) | {{ph-gov-status}} |
| Visible backlink count (thorough) | {{backlinks-count}} |
| Top 3 referring domains (thorough) | {{top-referrers}} |

**Top non-site mentions (last 24 months):**

1. {{mention-1}}
2. {{mention-2}}
3. {{mention-3}}

**Authority summary:** {{authority-summary}}

---

## 8. People

| Role | Name | LinkedIn | Notes |
|---|---|---|---|
| Founder / CEO | {{ceo-name}} | {{ceo-linkedin}} | {{ceo-notes}} |
| {{key-role-1}} | {{key-name-1}} | {{key-linkedin-1}} | {{key-notes-1}} |
| {{key-role-2}} | {{key-name-2}} | {{key-linkedin-2}} | {{key-notes-2}} |
| {{key-role-3}} | {{key-name-3}} | {{key-linkedin-3}} | {{key-notes-3}} |

**Decision-maker hypothesis (for this pitch):** {{decision-maker}}

---

## 9. News & reviews

### Recent news mentions (last 24 months)

| Date | Source | Headline | URL |
|---|---|---|---|
| {{news-date-1}} | {{news-source-1}} | {{news-headline-1}} | {{news-url-1}} |
| {{news-date-2}} | {{news-source-2}} | {{news-headline-2}} | {{news-url-2}} |
| {{news-date-3}} | {{news-source-3}} | {{news-headline-3}} | {{news-url-3}} |

### Review aggregators

| Platform | Rating | Count | Sentiment summary |
|---|---|---|---|
| Google | {{google-rating}} | {{google-count}} | {{google-sentiment}} |
| Trustpilot | {{tp-rating}} | {{tp-count}} | {{tp-sentiment}} |
| Glassdoor | {{gd-rating}} | {{gd-count}} | {{gd-sentiment}} |
| G2 / Capterra | {{g2-rating}} | {{g2-count}} | {{g2-sentiment}} |
| Reddit mentions | — | {{reddit-count}} | {{reddit-sentiment}} |

---

## 10. Competitive landscape

{{competitive-applicable-or-na}}

| Criterion | {{company-name}} | {{competitor-a}} | {{competitor-b}} | {{competitor-c}} |
|---|---|---|---|---|
| Tagline | {{target-tagline}} | {{a-tagline}} | {{b-tagline}} | {{c-tagline}} |
| Primary CTA | {{target-cta}} | {{a-cta}} | {{b-cta}} | {{c-cta}} |
| Pricing visible | {{target-pricing}} | {{a-pricing}} | {{b-pricing}} | {{c-pricing}} |
| Tech stack | {{target-tech}} | {{a-tech}} | {{b-tech}} | {{c-tech}} |
| Social presence | {{target-social-level}} | {{a-social}} | {{b-social}} | {{c-social}} |
| Unique positioning | {{target-positioning}} | {{a-positioning}} | {{b-positioning}} | {{c-positioning}} |

**Competitive read:** {{competitive-summary}}

---

## 11. Risk flags

{{risk-flags-or-clean}}

- [ ] **SSL** — {{ssl-flag}}
- [ ] **Domain expiry** — {{expiry-flag}}
- [ ] **Contact information** — {{contact-flag}}
- [ ] **Social presence** — {{social-flag}}
- [ ] **Review reputation** — {{review-flag}}
- [ ] **Content freshness** — {{freshness-flag}}
- [ ] **Compliance (DPA / GDPR)** — {{compliance-flag}}

---

## 12. Recommended next steps

Given the project context (**{{project-context}}**), the following sibling skills could consume this report:

| Skill | What it would do with this data |
|---|---|
| `/theme-client` | Seed Section 4 (Brand assets) directly into the intake — saves re-asking for logo, colors, fonts |
| `/proposal-comm` | Pre-fill client name, location, industry, and contact for the commercial proposal |
| `/proposal-tech` | Pre-fill technical context (existing tech stack, page count) for scope estimation |
| `/company-site` | Use the existing-site analysis to scope a rebuild — same content sections, same brand |
| `/ph-dpa-compliance` | If the target is PH-based, run compliance review on the existing site |
| `/seo-leads-gen` | Add this prospect to the SEO leads pipeline for follow-up |

**Suggested action:** {{suggested-action}}

---

## 13. Sources

Every URL fetched in this report, with retrieval timestamps. See `sources.md` for the full log.

**Primary site pages:**
{{site-sources}}

**Social profiles:**
{{social-sources}}

**External (Maps, news, reviews, directories):**
{{external-sources}}

---

*Report generated by `/web-research` skill. Re-run on the same slug to refresh — the skill will detect cached data and ask whether to update.*
