---
name: web-rebuild
description: Orchestrator for rebuilding a poor-performing website into a high-performance one. Runs the full pipeline — measured baseline of the old site (/web-perf-audit + /ux-review + optional /web-research), rebuild spec with performance budget, brand/theme setup (/theme-client or /theme-hayahai via /ui-builder), rebuild (/company-site for marketing sites, /feature-dev for apps), quality gates (/ux-review, /audit, /e2e-test), deploy (/vercel-deploy or /netlify-deploy), and a measured before/after verification against the baseline. Preserves SEO equity across the cutover (URL map, 301 redirects, metadata parity). Produces REBUILD.md with the before/after scorecard. Use when the user says "rebuild this site", "this site is slow, redo it", "modernize this website", "migrate this site to Next.js", "replatform", "site revamp", "make this site fast", or invokes /web-rebuild. NOT for auditing without rebuilding (use /web-perf-audit or /ux-review alone), NOT for building a brand-new site with no predecessor (use /company-site or /init).
---

# Web Rebuild — Poor-Performer to High-Performer Orchestrator

The entry point for replacing an existing, underperforming website with a fast rebuild. This skill does not implement anything itself — it sequences the specialist skills, carries a performance budget through every phase, and refuses to declare success without measured before/after numbers.

Core contract: **no rebuild ships unless it beats the baseline on every budget line.**

---

## Workflow Summary

```
Phase 0 — Intake            (URL, repo access, site type, brand, goals)
Phase 1 — Baseline          (/web-perf-audit + /ux-review on OLD site → locked numbers)
Phase 2 — Content & SEO Map (crawl old site: pages, copy, ranking URLs, metadata)
Phase 3 — Rebuild Spec      (performance budget + scope; /prd-tdd-writer if app-class)
Phase 4 — Brand & Theme     (/theme-client or /theme-hayahai, routed via /ui-builder)
Phase 5 — Rebuild           (/company-site OR /feature-dev; budget enforced during build)
Phase 6 — Quality Gates     (/ux-review → /audit GO/NO-GO → /e2e-test)
Phase 7 — Deploy Preview    (/vercel-deploy or /netlify-deploy — preview, not prod)
Phase 8 — Verify            (/web-perf-audit on preview vs Phase 1 baseline)
Phase 9 — Cutover           (redirect map live, DNS, prod deploy, post-cutover re-audit)
Phase 10 — Report           (REBUILD.md before/after scorecard)
```

Approval checkpoints (stop and confirm with the user): end of Phase 3 (spec + budget), end of Phase 6 (audit GO/NO-GO), before Phase 9 (cutover is outward-facing and hard to reverse).

---

## Phase 0 — Intake

Collect in one block; detect what you can before asking:

| Question | Why it matters |
|---|---|
| Live URL of the old site | Baseline target |
| Do we have the old site's repo / hosting access? | Enables local build audit + content export + redirect deployment |
| Site type: marketing/company site · content site · web app · e-commerce | Routes Phase 5 to /company-site vs /feature-dev |
| Brand: Hayah-AI (sub)brand · external client · keep old site's brand | Routes Phase 4 |
| Does the old site have search traffic worth keeping? | Gates the SEO-preservation work in Phases 2 and 9 |
| Deploy target | Vercel default; Netlify or other if user says so |
| PH market? | PH-mobile budget tier, ₱ formatting, COD/WhatsApp patterns downstream |

If the user only has a URL and a complaint ("this site is slow and ugly"), that is enough to start — everything else has a default.

Optional: if this is a client engagement and background is thin, run `/web-research <url>` (standard depth) first — its REPORT.md feeds the spec and the brand intake.

---

## Phase 1 — Baseline (the OLD site)

Lock the numbers you will be judged against later. Both run against the live old site:

1. `/web-perf-audit <old-url>` — TTFB warm/cold split, JS weight, payload, headers, caching, host detection. If the old repo is available, also run its local build audit.
2. `/ux-review` in Page or Full mode against the live URL — heuristic findings + Phase 5.5 SEO surface.

Record the baseline table in REBUILD.md immediately (Phase 10 template below). These numbers are frozen — later phases compare against them, never re-measure the old site after work starts.

Skip neither. Perf numbers without UX findings produce a fast site that still doesn't convert; UX findings without numbers produce an unfalsifiable "it feels better."

---

## Phase 2 — Content & SEO Map

A rebuild fails silently when it loses content or rankings. Before writing any new code:

1. **Page inventory** — enumerate every indexable URL: sitemap.xml if present, else crawl (agent-browser or Chrome tools). Record URL, title, meta description, H1, and word count per page.
2. **Keep/kill/merge decision per page** — with the user for anything ambiguous.
3. **Ranking-URL protection** — if the site has search traffic (Phase 0), flag URLs that must keep their exact path or get a 301. Build the redirect map now: `old-path → new-path` for every kept page whose URL changes.
4. **Content export** — pull the copy worth keeping (get_page_text per page) into `content/` in the new project. Rebuilds rewrite design, not necessarily copy; losing working copy is a regression.
5. **Asset inventory** — logos, product photos, PDFs that must survive.

Output: `REBUILD_CONTENT_MAP.md` in the new project root — page inventory, decisions, redirect map, asset list.

---

## Phase 3 — Rebuild Spec & Performance Budget

Set the budget from the baseline: every "Fix needed" line in the Phase 1 audit becomes a target at the "Good" threshold from /web-perf-audit's table. Minimum budget:

| Metric | Target | Baseline (from Phase 1) |
|---|---|---|
| TTFB (warm) | <200ms | _measured_ |
| TTFB (cold) | <600ms | _measured_ |
| Total JS (raw) | <300KB | _measured_ |
| Largest JS chunk | <100KB | _measured_ |
| HTML payload | <50KB | _measured_ |
| Fonts | <60KB, ≤3 files | _measured_ |
| Security headers | full checklist pass | _measured_ |

PH-market sites: state the budget in real terms too (target JS weight ≈ parse time on mid-range Android over 4G).

Scope by site type:
- **Marketing/company/content site** — a short spec section inside REBUILD.md is enough; do not invoke /prd-tdd-writer for a 5-page brochure rebuild.
- **Web app / e-commerce / anything with auth, data, or payments** — run `/prd-tdd-writer` (PRD light, TDD full), then `/plan-todo` to generate TODO.md. The rebuild becomes a normal project from here, with this skill supervising the gates.

**Checkpoint: present spec + budget + content map summary to the user before building.**

---

## Phase 4 — Brand & Theme

Route through `/ui-builder` Phase 0–2 logic:

| Situation | Skill |
|---|---|
| Hayah-AI property or sub-brand | `/theme-hayahai` (pick variant by audience/mood) |
| External client — new or existing brand | `/theme-client` (intake their logo/colors; if "keep old site's brand", extract palette + logo from the old site as the brief) |
| Throwaway prototype to sell the rebuild first | theme-factory artifact, then redo properly on approval |

"Keep the old brand" is the common case for rebuilds: pull the logo, extract the 2–3 real brand colors from the old CSS, and feed those to `/theme-client` — do not freelance a palette.

---

## Phase 5 — Rebuild

| Site type | Skill | Notes |
|---|---|---|
| Marketing / company / brochure | `/company-site` | Phase A artifact for user approval, Phase B Next.js scaffold. Feed it the content from Phase 2 — the interview answers come from the content map, not from scratch. |
| Web app / dashboard / e-commerce | `/feature-dev` per TODO.md phase | Auth via `/auth-page-scaffold`, DB via `/db-migrate`, endpoints via `/api-new` as needed |
| Single tricky pages within either | `/ui-builder` | |

Budget enforcement during build, not after: after the scaffold builds, run /web-perf-audit's local build audit (`references/local-build-audit.md`) on every significant addition of dependencies. Catching a 200KB chart library at install time is cheap; at Phase 8 it is a rework loop.

Wire the redirect map from Phase 2 into the project now (`next.config.js` redirects / `vercel.json` / `_redirects`) so it ships with the first deploy, not as a cutover-day scramble.

---

## Phase 6 — Quality Gates

In order, each gating the next:

1. `/ux-review` — Full mode against the local dev server. Fix Critical/High findings before proceeding (visual fixes → /ui-builder, logic fixes → /feature-dev).
2. `/audit` — the hard gate. NO-GO blocks Phase 7 until remediated.
3. `/e2e-test` — user journeys, forms actually submit, screenshots. For marketing sites this is small (nav + every form + mobile widths); do not skip the forms — a beautiful contact form that drops leads is a failed rebuild.

---

## Phase 7 — Deploy Preview

`/vercel-deploy` or `/netlify-deploy` — **preview deployment, never production.** Production is Phase 9, after verification and explicit user approval.

---

## Phase 8 — Verify (the whole point)

Run `/web-perf-audit <preview-url>` and fill the budget table's third column. Three outcomes:

- **All budget lines met and beat baseline** → proceed to Phase 9.
- **Budget miss on a build-side metric** (JS, chunks, fonts, payload) → back to Phase 5 with the local build audit; do not rationalize the miss.
- **Budget miss on a delivery-side metric** (TTFB, caching, headers) → apply the host-specific fixes from /web-perf-audit's references; redeploy preview; re-verify.

Note: preview URLs on Vercel/Netlify are uncached and un-CDN-warmed relative to prod — TTFB on preview may read worse than prod will. Judge build-side metrics strictly on preview; confirm delivery-side metrics again post-cutover.

---

## Phase 9 — Cutover

**Confirm with the user before anything in this phase — DNS and production deploys are outward-facing.**

1. Production deploy.
2. Verify the redirect map live: curl every `old-path` → expect 301 to `new-path`.
3. DNS switch (user usually does this; provide exact records). Warn against Cloudflare-proxying in front of Vercel/Netlify — /web-perf-audit's #1 double-proxy finding.
4. Post-cutover: re-run `/web-perf-audit` on the production domain. This is the number that goes in the final report.
5. Submit new sitemap in Search Console if the site had rankings (user action; provide steps).

---

## Phase 10 — Report

Write `REBUILD.md` in the project root:

```markdown
# Rebuild Report — <site>

## Scorecard
| Metric | Old site | Target | New site | Verdict |
|---|---|---|---|---|
| TTFB warm/cold | | | | |
| Total JS | | | | |
| Largest chunk | | | | |
| HTML payload | | | | |
| Fonts | | | | |
| Security headers | x/y pass | all | | |
| UX Critical findings | n | 0 | | |

## What changed (one paragraph, business language)
## SEO continuity (redirect map status, sitemap, metadata parity)
## Follow-ups (deferred items → TODO.md)
```

Suggested follow-ups by situation: `/load-test` if traffic is expected to spike post-relaunch; `/legal-docs` + `/ph-dpa-compliance` if the old site had no privacy/terms pages; `/checkpoint` to end the session.

---

## Relationship to Other Skills

- **Wraps `/web-perf-audit`** — baseline (Phase 1), build-time budget checks (Phase 5), verification (Phases 8–9). This skill never measures anything itself.
- **Wraps `/ux-review`** — baseline findings (Phase 1) and pre-ship gate (Phase 6).
- **Routes to `/company-site` or `/feature-dev`** for the actual build — this skill writes no product code.
- **Routes brand through `/ui-builder`** → `/theme-hayahai` / `/theme-client`.
- **Defers the hard gate to `/audit`** — its GO/NO-GO stands; this skill does not override it.
- **Optional intake via `/web-research`**, optional post-launch `/load-test`.

## Boundaries

- Not an audit-only skill — if the user wants findings without a rebuild, hand off to /web-perf-audit or /ux-review and stop.
- Not for greenfield sites — no predecessor means no baseline; use /company-site or /init.
- Never cut over (Phase 9) without explicit user approval, a passing /audit, and a verified budget table.
- Never drop the redirect map "to clean up later" — SEO loss from a rebuild is usually permanent.
