---
name: ui-builder
description: Orchestration skill for building branded UIs. Routes between /theme-hayahai (Hayah-AI brand family — 6 variants), document-skills:theme-factory (10 generic presets, one-off artifacts), and custom themes. Covers theme selector clarification, logo + tagline composition (Hayah-AI sub-brand or external), layout selection (landing, dashboard, auth, marketing, app shell), component patterns, iconography, spacing, motion, imagery direction, and copy voice. Outputs HTML artifacts, production React/Next.js code, or Tailwind configs. Use when the user says "build a UI", "design a page", "create a landing page", "build the dashboard", "design system for", "brand this", "compose a logo", "what theme should I use", "pick a theme", "wireframe", "UI for the X feature". Triggers on /ui-builder, "ui builder", "design the UI".
---

# UI Builder — Branded UI Orchestration

The entry point for any UI work. Decides between `/theme-hayahai`, `document-skills:theme-factory`, and custom themes; composes logo + tagline; selects a layout; assembles components; outputs the right artifact.

This skill does NOT redefine the Hayah-AI design system — that lives in `/theme-hayahai`. This skill calls into it.

---

## Workflow Summary

```
Phase 0 — Project Context     (audience, brand family, output format)
Phase 1 — Theme System        (Hayah-AI / theme-factory / custom)
Phase 2 — Theme Variant       (clarify which one and why)
Phase 3 — Logo + Tagline      (canonical / sub-brand / external)
Phase 4 — Layout              (landing / app / auth / marketing / artifact)
Phase 5 — Components          (which patterns the layout needs)
Phase 6 — Generation          (HTML / React / Tailwind config)
Phase 7 — Verification        (preview + adjust)
```

---

## Phase 0 — Project Context

Detect or ask in a single block:

| Question | Default |
|---|---|
| What surface? | Landing / Dashboard / Auth / Marketing site / App shell / Single component / Slide deck / Document |
| What brand? | Hayah-AI (parent) / Hayah-AI sub-product (e.g. TripIntell) / External client / Generic prototype |
| Audience | B2B / Consumer / Developer / Internal / Mixed |
| Mood priority | Sophisticated · Powerful · Warm · Authoritative · Innovative |
| Output format | HTML artifact / Production React/Next.js / Tailwind config / Slide / Static design |

These five answers determine every downstream choice.

---

## Phase 1 — Theme System Selection

**Decision matrix:**

| Signal | System | Why |
|---|---|---|
| Hayah-AI product or sub-product | `/theme-hayahai` | Brand consistency required |
| **External client / non-Hayah-AI project** | **`/theme-client`** | Per-client brand spec, full auto-fill, stored at `<project-root>/brand/` |
| Personal artifact (slide deck, demo doc, internal report) | `document-skills:theme-factory` | 10 fast presets, no brand commitment |
| Quick prototype, will be replaced | `theme-factory` | Lowest friction |
| Production app for paying users | `/theme-hayahai` (if Hayah-AI portfolio) or `/theme-client` (if client work) | Brand consistency matters when money is involved |
| Slide deck, presentation, or static export | `theme-factory` (10 presets, optimized for slides/docs) | Better preset coverage for that format |
| HTML artifact for review-only | Match the intended brand (Hayah / client / generic) | — |

**Theme system one-liners:**

- **`/theme-hayahai`** — opinionated, brand-locked, 6 variants of one palette (teal + coral). For any product in your portfolio. Marketing surfaces pick by mood (Classic/Midnight/Coral/Editorial/Bento); **logged-in app surfaces (dashboards, CRM, admin) always use hayah-console** — the dense app-UI variant with status colors, data-viz, and table tokens.
- **`/theme-client`** — parameterised intake. Takes a client brand brief (logo + 1–3 colors + optional fonts + mood), auto-fills the rest, writes `theme.json`, `tokens.css`, `tailwind.config.js`, `logo.svg`, `BRAND.md` to `<project-root>/brand/`. Drop-in compatible with `/company-site` templates and `/auth-page-scaffold`. **The default for any paying client engagement.**
- **`document-skills:theme-factory`** — 10 generic presets for slides, docs, one-off artifacts. Not for client deliverables.

After selection, state the choice + why in one sentence.

---

## Phase 2 — Theme Variant Selection

### If Hayah-AI: pick a variant

Read each variant's "best for" mood signal:

| Variant | Pick when |
|---|---|
| **Classic** | SaaS dashboards, professional services, premium B2B, anything that needs to feel sophisticated and refined. Default if uncertain. |
| **Midnight** | AI products, fintech, dev tools, or anything where "powerful / cutting-edge" beats "approachable". Dark surface. |
| **Coral** | Marketplaces, consumer apps, wellness, hospitality, travel — anywhere warmth and accessibility matter most. |
| **Editorial** | Thought-leadership content, premium launches, B2B with confidence. Sharp 0px corners — most distinctive. |
| **Bento** | AI/tech SaaS with multi-feature surface (3+ featured capabilities), developer tools, anything with a dashboard-style hero. |

**Rules of thumb:**
- One display font per page. Don't mix variants on the same surface.
- Default to **Classic** for unknown SaaS, **Midnight** for AI-first products, **Coral** for consumer-facing, **Bento** for feature-dense.
- If the user picked a mood in Phase 0, map it: Sophisticated → Classic, Powerful → Midnight, Warm → Coral, Authoritative → Editorial, Innovative → Bento.

### If theme-factory: pick a preset

Defer to that skill's preset list. Match the project's mood and format. State the preset name in the artifact for traceability.

### If `/theme-client` (client work): invoke it first

Do not improvise client branding inside this skill. Hand over to `/theme-client`:

1. Check whether `<project-root>/brand/theme.json` already exists.
2. If yes → read it and continue with the layout/component phases below using its tokens.
3. If no → invoke `/theme-client`, let it run its Phase 0 intake (client name, slug, logo, primary color, optional secondary/fonts/mood/radius), and let it generate the full `<project-root>/brand/` folder.
4. Then return here for layout selection (Phase 4).

The output of `/theme-client` has the **same shape** as a Hayah variant JSON — all downstream `/ui-builder` logic (component picks, layout rules, motion, hover states) reads tokens identically.

---

## Phase 3 — Logo + Tagline Composition

### Three composition modes

| Mode | When | Source of logo |
|---|---|---|
| **Canonical** | Hayah-AI parent brand surface | Inline SVG from `/theme-hayahai` skill, tagline = `business automation` |
| **Sub-brand** | Hayah-AI sub-product (TripIntell, Hayah-AI SEO, etc.) | Compose new wordmark using DM Serif Display + Hayah-AI palette + custom tagline |
| **External** | Non-Hayah-AI brand | Generate wordmark + symbol concepts; tagline + palette per the brand guide |

### Canonical (Hayah-AI parent)

Use the SVG snippets in `/theme-hayahai/skill.md` directly. Two display modes:
- **Compact nav** — `viewBox 0 0 344 68`, no tagline. Top navs.
- **Panel / hero** — `viewBox 0 0 344 96`, with tagline `business automation`. Auth panels, hero sections.

Light vs. dark variants are pre-defined in that skill. Pull, do not redraw.

### Sub-brand (Hayah-AI portfolio)

Compose a new wordmark that:
- Uses DM Serif Display (matches parent) OR a complementary serif from the variant being used (e.g. Fraunces for Coral-themed sub-brand)
- Sub-brand name in `#0a3d3a` (deep teal)
- Optional accent character in `#ff6b47` (coral) — e.g. the dot on `i`, or a single italic letter
- Optional Hayah-AI parent endorsement: small `by hayah-ai` in `#7a9b96` muted color below the wordmark

**Tagline composition rules** (apply to all sub-brands and external):
- ≤ 6 words, ideally 3–5
- Sentence case, no period at the end (display lines are period-optional)
- No exclamation points
- Action-oriented or benefit-stated, not feature-listed
- Pair with the wordmark visually: half the wordmark's font-size, lighter weight, more letter-spacing

**Tagline rubric — judge before finalizing:**

| Test | Pass | Fail |
|---|---|---|
| Specificity | "Booking that doesn't suck" | "The best platform" |
| Verb-led or noun-led with weight | "Plan trips that flow" | "Travel solutions" |
| Memorable | "Real-time. End-to-end." | "Powerful, easy-to-use, scalable" |
| Brand-true | Reflects category and tone | Generic SaaS-speak |
| Sub-9-word | Easy to read in one glance | Long, multi-clause |

Examples for Hayah-AI sub-brands:
- **TripIntell** — "Itineraries that flow." or "Plan trips that work."
- **Hayah-AI SEO** — "Outrank with intent." or "SEO leads, automated."
- **levelup-crm** — "Sales without the sludge."

Generate 3 tagline options, recommend one, explain why.

### External (non-Hayah-AI)

Apply the same tagline rubric. Generate wordmark concepts at three weight levels (display serif, geometric sans, modern grotesque). Document the chosen mark in `BRAND.md`.

For symbols/icons: keep geometric. Lucide-style or single-stroke abstractions. Avoid:
- Stock icon emoji aesthetics
- Three-letter monogram clichés (unless requested)
- Gradient meshes (rarely production-grade)

---

## Phase 4 — Layout Selection

Pick one or compose multiple. When using Hayah-AI, each layout maps to real assets in `/theme-hayahai`: `auth-pages/` (6 auth variants), `assets/showcase.html` (component showcase), `hayahai-design/project/colors_and_type.css` (tokens), and `references/` (palette + typography). Otherwise use generic patterns.

### Route to `/company-site` first if the request is "full company website"

Before picking a Phase 4 layout, check whether the user actually wants a **deployable company website** (artifact + Next.js scaffold + Supabase + RLS + security gates) rather than a mockup.

| Signal | Route |
|---|---|
| "Build a website for client X" / "Scaffold a company site" / "I need a landing + contact form + database" | **Stop. Route to `/company-site`.** It owns the artifact-then-Next.js-scaffold pipeline with Supabase, RLS, rate limiting, DPA consent, and 3 production-grade reference templates (industrial, SaaS, local business). |
| "Design / mock up a landing page" / "Show me how the hero would look" / "Wireframe the landing" | **Stay in `/ui-builder`** — produce an HTML artifact mockup, no DB wiring. |
| "Design the dashboard / app shell / auth screen / single component" | **Stay in `/ui-builder`** — `/company-site` does not cover these. |

When routing to `/company-site`, hand over the Phase 0–3 decisions (theme variant, logo composition, tagline) so `/company-site` doesn't re-ask.

### Landing page

Sections in order:
1. Nav (logo + 3–5 links + CTA)
2. Hero (headline ≤ 10 words as the page's only `<h1>`, sub ≤ 25 words, primary CTA + secondary)
3. Logo strip / social proof (5–8 logos or testimonial snippet)
4. Feature grid (3 or 6 features — never 4 or 5)
5. Long-form feature (one feature, full image + copy)
6. Pricing OR conversion CTA section
7. FAQ (4–8 collapsible)
8. Footer (logo, link columns, legal links, copyright)

### Dashboard / app

- **App shell:** sidebar (or top nav), main content, optional right panel
- **Top bar:** breadcrumbs, search, user menu, notifications
- **Content area:** page header, primary action, content grid or table
- **Empty states** for every list and detail view (rule, not optional)
- **Loading skeletons** for every fetch boundary

### Auth pages

Use `/theme-hayahai`'s `auth-pages/` as starting templates. Match the variant chosen in Phase 2. Never build auth from scratch when these exist.

### Marketing site (multi-page)

Routes: `/`, `/pricing`, `/features`, `/about`, `/blog`, `/contact`, plus legal `/legal/{terms,privacy,cookies}`. Compose Landing layout for `/`, simpler hero + content for the rest.

### App shell only

When the user already has design and just needs the chrome:
- Sidebar with nav items
- Top bar with logo + actions
- Content slot with consistent padding
- Optional right rail for context-sensitive panels

### Single component

For an isolated request like "design a pricing card" or "build a settings panel":
- Skip layout phase
- Apply theme tokens directly
- Output the component in isolation
- Note where it would live in the larger system

### Slide deck / artifact

Defer to `document-skills:theme-factory` or `document-skills:pptx`. UI Builder is for screen-based UIs — not slide composition.

---

## Phase 5 — Component Selection

For the chosen layout, list the components needed. Pull defaults from the selected theme. Common components:

| Category | Components |
|---|---|
| Navigation | Top nav, sidebar, breadcrumbs, tabs, footer |
| Forms | Input, textarea, select, multi-select, radio, checkbox, switch, file upload, slider |
| Buttons | Primary, secondary, ghost, destructive, icon-only, button group |
| Display | Card (light/soft/warm/dark/glass/editorial), stat, table, list, badge, tag, chip |
| Feedback | Toast, alert, banner, modal, drawer, popover, tooltip, dialog |
| Loading | Skeleton, spinner, progress bar, shimmer |
| Data | Empty state, error state, success state, no-results state |
| Layout | Container, grid, divider, section, stack |

For each, specify which variant of the component is needed (e.g. "Card — soft variant for the feature grid" not just "Card").

### Required-by-default components

Every UI surface needs:
- Loading states for every async operation
- Empty states for every list
- Error states for every fetch
- Success / confirmation states for every destructive or important action
- Focus-visible styles for keyboard users
- Touch targets ≥ 44×44 px on mobile

If any of these are absent in the generated UI, flag it before declaring the build done.

---

## Phase 6 — Generation

### Output format → action

| Output | What to produce |
|---|---|
| **HTML artifact** | Single self-contained `index.html` with inline `<style>` and `<script>`. Pull theme CSS from `/theme-hayahai/hayahai-design/project/colors_and_type.css`. |
| **Production React/Next.js** | TypeScript components, Tailwind classes, Hayah-AI tokens via `tailwind.config.js`. Place under `app/(marketing)/` or `components/<feature>/`. |
| **Tailwind config only** | Generate or update `tailwind.config.js` with Hayah-AI tokens. See snippet in `/theme-hayahai`. |
| **Slide / static** | Defer to `document-skills:theme-factory` or `pptx`. |

### Production code rules

- TypeScript strict — no `any`, no implicit `any` in props
- Components named `PascalCase`, hooks `use*`, utilities `camelCase`
- Files match the export name
- Components colocated with their route (`app/(marketing)/landing/page.tsx`) or under `components/<feature>/` for shared
- All copy in JSX; no hardcoded English strings if i18n is set up
- Use `next/image` for images (with `width`/`height` or `fill` — unsized media causes CLS), never `<img>` in Next.js
- Fonts via `next/font`, never render-blocking font `<link>` tags
- Semantic landmarks (`<header>`, `<nav>`, `<main>`, `<footer>`), exactly one `<h1>` per page, headings nest without skipped levels
- Shipped marketing pages get a per-route Metadata API entry (unique title/description, canonical, OG image) and JSON-LD where content matches — `/ux-review` Phase 5.5 grades exactly this; build it in rather than fixing it after review
- Lucide icons via `lucide-react`, not emoji
- All forms use React Hook Form + Zod (per CLAUDE.md)

### What to NOT generate

- Don't add framer-motion, gsap, or animation libraries unless the user explicitly wants animation beyond hover transitions
- Don't add backwards-compat stubs for unused variants
- Don't generate placeholder content longer than what the user provided — keep slots short ("Replace with your headline")
- Don't add SEO `<meta>` tags to mockups and HTML artifacts — but production marketing pages DO get their Metadata API entry (see Production code rules); the exemption is for throwaway previews only

---

## Phase 7 — Verification

Before declaring done:

- [ ] Theme tokens applied consistently (no hardcoded hex colors outside the theme file)
- [ ] Logo and tagline render correctly at all viewport sizes
- [ ] Touch targets ≥ 44px on mobile (per /ux-review rule)
- [ ] No horizontal scroll at 320px width
- [ ] Loading / empty / error states present where applicable
- [ ] Voice and copy follow the rules (sentence case, no exclamation points, no emoji in product UI)
- [ ] Iconography from Lucide only (no mixed icon families)
- [ ] If HTML artifact: opens cleanly in a browser
- [ ] If production code: TypeScript compiles, no ESLint errors
- [ ] If production marketing page: one `<h1>`, semantic landmarks, Metadata API entry, sized images — pre-empts `/ux-review` Phase 5.5

This checklist is a smoke check, not a review. For anything shipping, run `/ux-review` on the built surface.

If the user wants to iterate: open the artifact or dev server, point them at specific sections to adjust, take guided edits.

---

## Output Files

For HTML artifact:
```
ui/<surface-name>.html
```

For production:
```
app/<route>/page.tsx
components/<feature>/<Component>.tsx
tailwind.config.js (updated)
BRAND.md (only if custom theme used)
```

For sub-brand asset deliverable:
```
brand/
├── logo.svg              # primary mark
├── logo-compact.svg      # compact nav variant
├── logo-dark.svg         # dark-background variant
├── BRAND.md              # palette, type, voice, tagline rationale
```

---

## Integration Points

- **Hands off to `/theme-hayahai`** — for canonical Hayah-AI brand assets, palette, typography, component patterns
- **Hands off to `/theme-client`** — at the start of any client engagement to generate `<project-root>/brand/theme.json` + `logo.svg` + `tailwind.config.js` + `BRAND.md`. Then `/ui-builder` reads `brand/theme.json` for all subsequent decisions.
- **Hands off to `/company-site`** — when the user wants a **deployable company website** (artifact → Next.js scaffold → Supabase + RLS + DPA + security gates). `/company-site` owns the full pipeline and the 3 reference templates (industrial, SaaS, local business). It calls back into `/ui-builder` Phase 3 for tagline composition.
- **Hands off to `document-skills:theme-factory`** — for one-off generic artifacts, slide decks
- **Hands off to `/auth-page-scaffold`** — when the user wants auth pages with verification tests, not just static UI
- **Hands off to `frontend-design:frontend-design`** — for distinctive, high-craft frontend code beyond standard component patterns
- **Hands off to `/feature-dev`** — when the UI build needs to be wired to data, auth, and tested
- **Feeds `/ux-review`** — once UI is built, run heuristic review before publication; on marketing surfaces its Phase 5.5 also grades the SEO & marketing surface (headings, metadata, structured data, CLS causes, value prop). `/ux-review` findings tagged `[UX]`/`[SEO]`/`[MKT]` that are purely visual/theme-level route back here for the fix; findings needing data or logic go to `/feature-dev`.

---

## Sub-Brand Composition Examples (for reference)

**TripIntell** (under hayah-ai-travels):
- Wordmark: `TripIntell` in DM Serif Display, `#0a3d3a`, `-1.2` letter-spacing. Coral italic on `i` of "Intell".
- Tagline: "Itineraries that flow."
- Endorsement: `by hayah-ai` in `#7a9b96`, 11px, weight 400, below wordmark.
- Recommended variant: **Coral** (warm, consumer travel) or **Bento** (data-rich itineraries).

**Hayah-AI SEO**:
- Wordmark: `Hayah-AI SEO` — same as parent + `SEO` in coral italic
- Tagline: "Outrank with intent."
- Recommended variant: **Classic** (B2B agency feel) or **Midnight** (data/automation feel).

**levelup-crm**:
- Wordmark: `LevelUp CRM` in DM Serif Display, the `↑` in coral
- Tagline: "Sales without the sludge."
- Recommended variant: **Classic** (CRM is professional B2B).

---

## Rules

- **Always pick a theme system before designing** — never build with ad-hoc colors
- **Never mix variants on the same surface** — one display font per page
- **Logo: pull canonical SVG from `/theme-hayahai` for Hayah-AI parent surfaces** — do not redraw
- **Tagline: 3 options + recommendation** — never propose a single tagline
- **Voice rules from CLAUDE.md apply** — sentence case, no emoji, no exclamation points in marketing
- **Required states are not optional** — loading, empty, error, success states for every interactive surface
- **PH-market context auto-applies** when project is PH-targeted: peso formatting, mobile-first, Filipino-friendly copy, COD/GCash payment options
- **Defer to existing assets** — don't recreate auth pages, theme tokens, or component kits when they exist in `/theme-hayahai`
- **Custom themes must be documented** in `BRAND.md` before code generation begins

---

## Out of Scope

- **Deployable company websites with Supabase + RLS + security checklist** — use `/company-site`. UI-builder produces mockups; `/company-site` ships production sites.
- Slide deck / presentation composition — use `document-skills:theme-factory` or `document-skills:pptx`
- Static print design (posters, flyers) — use `document-skills:canvas-design`
- Algorithmic / generative art — use `document-skills:algorithmic-art`
- Brand strategy / positioning workshops (vs. tactical wordmark composition) — needs human strategist
- Trademark search and registration — counsel
- Photography direction / asset commissioning
- Full motion design (animations beyond hover transitions) — defer to specialist
- Implementation that requires data wiring — use `/feature-dev` after UI is approved
