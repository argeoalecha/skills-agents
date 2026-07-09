---
name: theme-hayahai
description: Hayah-AI design system — six branded theme variants sharing one ocean-teal + coral palette. Use for landing pages, dashboards, SaaS, auth pages, presentations, or any branded UI. Variants — hayah-classic (refined SaaS, DM Serif), hayah-midnight (dark AI/fintech, Syne), hayah-coral (warm consumer/marketplace, Fraunces), hayah-editorial (bold B2B text-led, Clash Display), hayah-bento (modern grid AI, Space Grotesk), hayah-console (dense app UI — CRM/dashboard/admin, status colors + data-viz + tables). Outputs: HTML artifacts, production CSS/React, or Tailwind token configs.
user-invocable: true
---

# Hayah-AI Theme System

Six themes, one core palette (deep teal `#0a3d3a`, aqua `#25A497`, coral `#ff6b47`, cream `#faf7f5`). Switch via `<html data-theme="classic|coral|editorial|bento|midnight|console">`.

**The story:** "hayah" means *life*, and the palette is a coral reef — deep ocean teal, living coral, aqua shallows, cream sand. Each variant is a view of the same reef (roles in each JSON's `role` field).

**The signature device:** the logo's arc + coral dot work beyond the logo — arc as hero/section ornament (mint, 8–12% opacity, replaces generic gradient washes), dot as status/list marker, arc sweep as the system's circular progress/loader. Each variant JSON carries its own `signature` block — read it before generating.

This is the **asset and rules layer** — tokens, JSONs, logo SVG, ui_kits, auth-page templates, voice / animation / typography rules. It is the **single source of truth** for the Hayah-AI brand. Orchestration belongs in `/ui-builder`; full-stack site delivery belongs in `/company-site`.

---

## Relationship with `/ui-builder`, `/company-site`, and `/theme-client`

| If the user wants… | Skill that owns it |
|---|---|
| Palette, type scale, theme JSON, logo SVG, auth-page HTML, atomic component patterns — **Hayah-AI portfolio** | **`/theme-hayahai`** (this skill) — read the asset directly |
| Same shape, but **for a paying client** (not Hayah-AI) | **`/theme-client`** — the parallel intake skill. Generates `<project-root>/brand/theme.json` from a client brief, drop-in compatible with everything that reads Hayah variants. |
| Pick a theme variant, compose a logo + tagline, choose a layout, build a dashboard / app shell / single component | `/ui-builder` (calls into this skill for assets) |
| Build a deployable company website (artifact → Next.js + Supabase + RLS + DPA + security) | `/company-site` (calls into this skill for theme JSON + logo SVG) |
| `/login` route with verification tests | `/auth-page-scaffold` (uses `auth-pages/` here as a starting template) |

**Asset granularity reference:**

| Path | Purpose |
|---|---|
| `hayahai-design/project/ui_kits/landing/{Nav,Hero,Features,Sections}.jsx` | **Atomic** branded patterns. Use when composing a custom one-off page. |
| `hayahai-design/project/ui_kits/app/{Shell,Screens,Icon}.jsx` | App-shell atomic patterns. Use when building dashboards / app chrome. |
| `auth-pages/auth-{variant}.html` | Static auth-page starting points. Copy + wire to your auth provider. |
| `~/.claude/skills/company-site/references/template-*.jsx` | **Composed full-site templates** (industrial / SaaS / local business). Pre-wired with Supabase + DPA + 9 sections per vertical. Owned by `/company-site`. |

**Variant decision table:** the one in the **Theme Variants** section below is **canonical**. `/ui-builder` Phase 2 and `/company-site` Phase 0 reference it — do not maintain parallel "best for" wording elsewhere.

---

## Skill Root

All paths in this file are relative to the skill root: `~/.claude/skills/theme-hayahai/`

| Path | What it is |
|---|---|
| `hayahai-design/project/colors_and_type.css` | **Canonical CSS** — variables, theme overrides, semantic type classes |
| `hayahai-design/project/themes/*.json` | Canonical theme JSONs (v2.0) |
| `hayahai-design/project/ui_kits/landing/` | Marketing site kit — Nav, Hero, Features, Sections (JSX + index.html) |
| `hayahai-design/project/ui_kits/app/` | App shell kit — Shell, Screens, Icon (JSX + index.html) |
| `hayahai-design/project/preview/` | 15 review cards (colors, type, components, spacing, brand) |
| `hayahai-design/project/assets/` | Logo component (HayahaiLogo.jsx) and brand mark |
| `hayahai-design/project/README.md` | **Deep brand reference** — voice, visual foundations, imagery, animation, card types, layout rules |
| `auth-pages/` | 5 ready-to-use login/signup HTML pages, one per theme |
| `assets/showcase.html` | Full-page multi-theme showcase |
| `references/color-palette.md` | Complete color usage + WCAG contrast notes |
| `references/typography.md` | Font import URLs + per-variant type scale |

---

## When Invoked

### Route up first if the scope is bigger than assets

If the request goes beyond raw assets, route to the right orchestration skill before answering:

| Signal | Route |
|---|---|
| "Build a UI", "design a page", "compose a logo + tagline", "what theme should I use", "design the dashboard" | **`/ui-builder`** owns the orchestration. Hand over. |
| "Build a website", "scaffold a company site", "I need a landing + contact form + database" | **`/company-site`** owns the artifact → Next.js + Supabase pipeline. Hand over. |
| "I just need the palette / fonts / logo SVG / a theme JSON / an auth page template" | **Stay here** — read the asset and return it. |

### If staying — ask the three-question interview

1. **What asset?** Palette · Type scale · Theme JSON · Logo SVG · Auth page · UI kit pattern · Tailwind config
2. **Which theme variant?** Classic · Coral · Editorial · Bento · Midnight · Console (or "recommend one" — app screens always get Console)
3. **Output target?** HTML artifact · Production CSS / React / Vue · Tailwind config · Raw values

Then:
1. Read `hayahai-design/project/colors_and_type.css` for the canonical variables.
2. Read the relevant theme JSON for component / spacing specs.
3. For auth: copy the matching `auth-pages/auth-{theme}.html` as a starting point.
4. For UI kits: read the JSX / HTML in `ui_kits/landing/` or `ui_kits/app/`.

---

## Theme Variants

> **Canonical "Best For" table.** `/ui-builder` Phase 2 and `/company-site` Phase 0 defer to the wording below. If you need to change a variant's positioning, change it here — do not edit the parallel tables in the sibling skills.

| Variant | JSON | Best For | Display Font | Body Font | Mood |
|---|---|---|---|---|---|
| **Classic** | `hayah-classic.json` | SaaS, professional services, consulting, premium B2B. **Default if uncertain.** | DM Serif Display | Plus Jakarta Sans | Sophisticated, premium |
| **Midnight** | `hayah-midnight.json` | AI products, fintech, dev tools, dark-mode tech | Syne | Geist | Powerful, cutting-edge |
| **Coral** | `hayah-coral.json` | Marketplaces, consumer apps, wellness, hospitality, travel, local service businesses | Fraunces | Outfit | Warm, approachable |
| **Editorial** | `hayah-editorial.json` | B2B thought leadership, premium launches. Sharp 0px corners — most distinctive. | Clash Display | Satoshi | Bold, authoritative |
| **Bento** | `hayah-bento.json` | AI / tech SaaS with multi-feature surface (3+ featured capabilities), developer tools | Space Grotesk | Geist | Innovative, dynamic |
| **Console** | `hayah-console.json` | **App/product UI** — CRM, dashboards, admin panels, client portals, internal tools. The only variant with semantic status colors, data-viz palette, table + shell tokens, 4px grid. | none — Geist 600 titles (Space Grotesk metrics only) | Geist | Precise, calm, legible |

Mood → variant mapping for ambiguous requests: Sophisticated → Classic · Powerful → Midnight · Warm → Coral · Authoritative → Editorial · Innovative → Bento · **App screen (any mood) → Console**.

**Marketing page vs. product screen is the first routing question.** Landing/marketing → pick by mood. Logged-in app surface → Console, regardless of mood.

Each JSON contains: `colors`, `typography` (with `googleFontsUrl` and full scale), `components`, `landingPageSections`, `spacing`, and a `signature` block (the variant's ownable moves — read it before generating). Bento JSONs additionally contain `bentoGrid.cards` with layout types (`hero-large`, `feature`, `metric`, `highlight`, `glass`, `demo`, `integration`, `comparison`). Console additionally contains `colors.status` (semantic triplets), `colors.dataViz`, `components.table`, and `components.shell`.

---

## Color System

**Dark Teals** — Dark Forest `#0F3836` · Deep Teal `#0a3d3a` · Forest Green `#1a4d47` · Medium Teal `#1C5753`
**Coral** — Vibrant `#ff6b47` · Warm `#ff8f73` · Soft Peach `#ffb5a0` · Hover `#e55a38`
**Accents** — Aqua `#25A497` · Ocean `#1E6E66` · Mint `#A1E4DB` · Sage `#7a9b96`
**Backgrounds** — Cream `#faf7f5` · Pearl `#e8f4f1` · Mint Whisper `#F3FFF9`

**Semantic status** (Console-first; any variant rendering app states uses these) — success `#1E6E66` · info `#25A497` · warning `#c77b1e` · danger `#d63c2f` · neutral `#7a9b96` · live = coral dot `#ff6b47` with pulse. Full text/bg/border triplets in `hayah-console.json` `colors.status`. Status is never color alone — always dot + label.

**Data-viz** (charts anywhere in the suite) — categorical order fixed: `#25A497 #ff6b47 #1E6E66 #ffb5a0 #7a9b96 #A1E4DB`. Sequential and diverging ramps in `hayah-console.json` `colors.dataViz`.

**Rules:**
- Light themes: page bg cream `#faf7f5`. Editorial uses pure white. Midnight uses `#0F3836`. **Never pure white** elsewhere.
- Text on light: `#0a3d3a` (not black). Text on dark: `#faf7f5` (not white).
- Coral and aqua never share the same hierarchy weight — one leads, the other supports.
- CTAs always get a colored shadow (`--shadow-coral` or `--shadow-teal`). Cards use neutral shadows only.
- Danger is red-shifted coral, never the CTA coral itself — `#d63c2f` vs `#ff6b47`. The pure coral dot is reserved for live states (it is the logo dot).

Full guidelines and contrast ratios: `references/color-palette.md`.

---

## Typography

| Variant | Display | Body | Mono |
|---|---|---|---|
| Classic | DM Serif Display | Plus Jakarta Sans | JetBrains Mono |
| Midnight | Syne | Geist | JetBrains Mono |
| Coral | Fraunces | Outfit | JetBrains Mono |
| Editorial | Clash Display (Fontshare) | Satoshi (Fontshare) | JetBrains Mono |
| Bento | Space Grotesk | Geist | JetBrains Mono |
| Console | none — Geist 600 titles; Space Grotesk for metrics only | Geist | JetBrains Mono |

**Rules:**
- Display goes big — hero up to 96px (Editorial). Always pair with negative letter-spacing `-0.025em` to `-0.045em`.
- Body: 16px / line-height 1.7 (editorial rhythm, not dense product-doc rhythm).
- Labels/eyebrows: all-caps, weight 600–700, tracking `+0.06–0.12em`.
- Don't mix multiple display fonts on one page.
- Editorial fallback: Space Grotesk + Plus Jakarta Sans if Fontshare unreachable.

Per-variant type scale + Fontshare URLs: `references/typography.md`.

---

## Shadow System

Soft, teal-tinted — never harsh black:

```css
--shadow-xs:    0 1px 2px  rgba(10, 61, 58, 0.05);
--shadow-sm:    0 2px 8px  rgba(10, 61, 58, 0.06);
--shadow-md:    0 4px 16px rgba(10, 61, 58, 0.08);
--shadow-lg:    0 8px 32px rgba(10, 61, 58, 0.10), 0 2px 8px rgba(10, 61, 58, 0.06);
--shadow-xl:    0 16px 48px rgba(10, 61, 58, 0.14);
--shadow-coral: 0 4px 20px rgba(255, 107, 71, 0.4);   /* coral CTAs only */
--shadow-teal:  0 4px 16px rgba(37, 164, 151, 0.35);  /* aqua CTAs only */
--glow-teal:    0 0 40px   rgba(37, 164, 151, 0.2);   /* Midnight only */
--glow-coral:   0 0 40px   rgba(255, 107, 71, 0.3);   /* Midnight only */
```

---

## Corner Radii

```css
--r-xs: 6px;  --r-sm: 10px;  --r-md: 16px;  --r-lg: 20px;  --r-xl: 28px;  --r-full: 9999px;
```

- Cards: `--r-lg`. Hero cards: `--r-xl`. Buttons: 10–12px. Pills/badges: `--r-full`.
- **Editorial overrides every radius to `0px`** — sharp corners are core to its identity.

---

## Borders

- Default: `1px solid rgba(161, 228, 219, 0.4)` — the brand's signature mint-tinted border.
- Strong: `1px solid #A1E4DB` (mint) or `2px solid #0F3836` (Editorial).
- Editorial card accents: `border-top: 3px solid #0F3836`.
- Midnight: default `rgba(161, 228, 219, 0.15)`, strong `0.4`.

---

## Animation

- Easing: `cubic-bezier(0.4, 0, 0.2, 1)`. Durations: 150ms (micro), 250ms (hover/expand), 400ms (page).
- Fades and small (~4px) translates only. **No bounces. No springs over 1.0 overshoot. No personality loaders.**
- Hero stagger-fade-up on load: `opacity 0→1, translateY 8px→0`, 60ms stagger.
- Hover transition: `transition: color 150ms, background 150ms, transform 200ms`.

---

## Hover & Press States

- **Coral primary button:** hover → `#e55a38`. No size change. Shadow strengthens.
- **Teal primary button:** hover → `#1E6E66`.
- **Secondary button:** hover fills `rgba(37,164,151,0.1)` or inverts to dark fill.
- **Link:** hover swaps teal `#1E6E66` ↔ coral `#ff6b47` (direction depends on theme).
- **Card:** hover lifts shadow `--shadow-sm` → `--shadow-md`. **Never scale or tilt.**
- **Press:** brief darken ~6% + 50ms. **No** `transform: scale(0.98)`.

---

## Card Types

- **Light (default):** white bg, 1px mint border, `--r-lg`, `--shadow-sm`, 28–32px padding
- **Soft:** mint-tinted bg `#e8f4f1`, no shadow, optional 1px mint border
- **Warm:** `#fff5f2` bg, coral-subtle border
- **Dark feature:** deep teal gradient or solid `#0a3d3a`, cream text
- **Glass** (Bento/Midnight only): `rgba(28,87,83,0.4)` + `backdrop-filter: blur(16px)` — Midnight uses `0.5` for a denser feel
- **Editorial:** `0px` corners + `border-top: 3px solid #0F3836`

---

## Layout Rules

- Container max-width: 1200–1280px. Prose max-width: 680–800px.
- Section padding vertical: 96–120px. Card gap in grids: 16–24px (Editorial: 2px hairline).
- Bento is the only theme with **asymmetric grid** — cards spanning 1×1, 2×1, 2×2 cells. See `bentoGrid.cards` in `hayah-bento.json`.
- Navs: fixed top, glass-blurred (Bento/Midnight) or solid white (Classic/Editorial).
- **No glass on light themes** — muddies cream. Glass only on Bento + Midnight.

---

## Iconography

- **Library: Lucide** — geometric, 1.5px stroke (2px for emphasis). CDN: `https://unpkg.com/lucide@latest`.
- Sizes: 16/20/24px (UI), 32–48px (feature cards), 64–96px (hero).
- Color: `currentColor` default. Aqua `#25A497` for primary action icons. Coral `#ff6b47` only for warnings/CTAs.
- **Never mix stroke weights. Never use emoji in product UI or marketing copy.**

**Single-file artifact carve-out.** When generating a Phase A single-file React artifact (e.g. `/company-site` Phase A, Claude artifact viewer, anything that can't `import { ... } from "lucide-react"`), use geometric Unicode glyphs as a pragmatic stand-in: `◈ ◉ ◐ ◑ ◒ ◓ ⬡ ⬢ ⌬ ✦ ✧ ◎`. These match the geometric Lucide aesthetic without the import. **Phase B / production code must replace these with `lucide-react`.** Document the swap as a Phase B step.

---

## Content & Voice

- **Sentence case** for all headings and buttons. Never Title Case in UI.
- **Hero headlines:** short, declarative, single-clause, under ~10 words. No questions.
- **No exclamation points** in marketing copy. **No emoji** in product UI.
- **Em-dashes** welcome. Short fragments fine. Periods optional on display lines.
- **Numbers as numerals** in metrics: `12k+`, `2.4M`, `99.9%`.
- Marketing copy uses **"you"**. Product copy uses **second-person commands** ("Connect a source").
- Eyebrows/labels: **uppercase, tracked-out, brief** — `PRODUCT`, `WHAT'S NEW`, `FOR DEVELOPERS`.

| Good | Avoid |
|---|---|
| Built for teams that ship. | Empower your team to unleash productivity |
| Connect a source. | Let's get you set up! |
| Real-time. End-to-end. | Best-in-class enterprise-grade synergy |
| Pricing that scales with you. | Plans for every size and shape! |

---

## Logo SVG — Canonical Snippets

The canonical logo is defined in `hayahai-design/project/assets/HayahaiLogo.jsx`. Use the inline SVG equivalents below for HTML pages.

**Two display modes:**
- **Panel / hero** — full logo with tagline (`viewBox 0 0 344 96`, `width=258 height=72`). Use in left panels, hero sections, or anywhere with ≥80px vertical space.
- **Compact nav** — mark + wordmark only, no tagline (`viewBox 0 0 344 68`, `width=172 height=34`). Use in horizontal top nav bars.

**Light background (teal mark, teal wordmark):**
```html
<!-- Compact nav -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 344 68" width="172" height="34" role="img" aria-label="Hayah-AI">
  <path d="M 12 52 A 28 28 0 0 1 52 12" fill="none" stroke="#0a3d3a" stroke-width="8" stroke-linecap="round"/>
  <circle cx="52" cy="12" r="6" fill="#ff6b47"/>
  <text x="68" y="48" font-family="DM Serif Display, Georgia, serif" font-size="44" font-weight="400" fill="#0a3d3a" letter-spacing="-1.2">hayah<tspan fill="#7a9b96">-</tspan><tspan fill="#ff6b47" font-style="italic">ai</tspan></text>
</svg>

<!-- Panel / hero with tagline -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 344 96" width="258" height="72" role="img" aria-label="Hayah-AI — business automation">
  <path d="M 12 52 A 28 28 0 0 1 52 12" fill="none" stroke="#0a3d3a" stroke-width="8" stroke-linecap="round"/>
  <circle cx="52" cy="12" r="6" fill="#ff6b47"/>
  <text x="68" y="48" font-family="DM Serif Display, Georgia, serif" font-size="44" font-weight="400" fill="#0a3d3a" letter-spacing="-1.2">hayah<tspan fill="#7a9b96">-</tspan><tspan fill="#ff6b47" font-style="italic">ai</tspan></text>
  <text x="0" y="84" font-family="Geist, Helvetica Neue, sans-serif" font-size="15" font-weight="300" fill="#0a3d3a" textLength="230" lengthAdjust="spacing">business automation</text>
</svg>
```

**Dark background (cream mark, cream wordmark):**
```html
<!-- Compact nav -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 344 68" width="172" height="34" role="img" aria-label="Hayah-AI">
  <path d="M 12 52 A 28 28 0 0 1 52 12" fill="none" stroke="#faf7f5" stroke-width="8" stroke-linecap="round"/>
  <circle cx="52" cy="12" r="6" fill="#ff6b47"/>
  <text x="68" y="48" font-family="DM Serif Display, Georgia, serif" font-size="44" font-weight="400" fill="#faf7f5" letter-spacing="-1.2">hayah<tspan fill="#A1E4DB">-</tspan><tspan fill="#ff6b47" font-style="italic">ai</tspan></text>
</svg>

<!-- Panel / hero with tagline -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 344 96" width="258" height="72" role="img" aria-label="Hayah-AI — business automation">
  <path d="M 12 52 A 28 28 0 0 1 52 12" fill="none" stroke="#faf7f5" stroke-width="8" stroke-linecap="round"/>
  <circle cx="52" cy="12" r="6" fill="#ff6b47"/>
  <text x="68" y="48" font-family="DM Serif Display, Georgia, serif" font-size="44" font-weight="400" fill="#faf7f5" letter-spacing="-1.2">hayah<tspan fill="#A1E4DB">-</tspan><tspan fill="#ff6b47" font-style="italic">ai</tspan></text>
  <text x="0" y="84" font-family="Geist, Helvetica Neue, sans-serif" font-size="15" font-weight="300" fill="#faf7f5" textLength="230" lengthAdjust="spacing">business automation</text>
</svg>
```

**Nav separator pattern** — wrap the logo in a container with `border-bottom`:
- Light pages: `border-bottom: 1px solid rgba(161, 228, 219, 0.4)`
- Dark pages: `border-bottom: 1px solid rgba(161, 228, 219, 0.2)`
- Editorial (keeps its identity): `border-bottom: 4px solid #0F3836`

**Font requirement:** All pages using this logo must load `DM Serif Display` from Google Fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet" />
```

---

## Auth Pages

Pre-built login/sign-up pages at `auth-pages/` (relative to skill root). All forms are static — wire to Supabase Auth, NextAuth, or your provider.

| File | Variant | Layout |
|---|---|---|
| `auth-classic.html` | Classic | Split — teal left panel + cream form right |
| `auth-midnight.html` | Midnight | Centered glass card on dark background |
| `auth-coral.html` | Coral | Full layout with feature highlights |
| `auth-editorial.html` | Editorial | Bold newspaper grid |
| `auth-bento.html` | Bento | Bento grid left + auth card right |
| `auth-console.html` | Console | Quiet centered card — field errors, danger banner, arc-sweep loading button |
| `index.html` | Gallery | Links to all 6 auth pages |

---

## Tailwind Config

Map the CSS variables to Tailwind theme tokens:

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        teal: {
          950: '#0F3836', 900: '#0a3d3a', 800: '#1a4d47', 700: '#1C5753',
          600: '#1E6E66', 500: '#25A497', 400: '#A1E4DB', 200: '#e8f4f1', 100: '#F3FFF9',
        },
        coral: { 700: '#7d2d15', 600: '#e55a38', 500: '#ff6b47', 400: '#ff8f73', 300: '#ffb5a0', 200: '#fff5f2' },
        cream: '#faf7f5',
        muted: '#7a9b96',
      },
      fontFamily: {
        // override per [data-theme] in CSS — Tailwind defaults below are Classic
        display: ['"DM Serif Display"', 'Georgia', 'serif'],
        body: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: { xs: '6px', sm: '10px', md: '16px', lg: '20px', xl: '28px' },
      boxShadow: {
        xs: '0 1px 2px rgba(10,61,58,0.05)',
        sm: '0 2px 8px rgba(10,61,58,0.06)',
        md: '0 4px 16px rgba(10,61,58,0.08)',
        lg: '0 8px 32px rgba(10,61,58,0.10), 0 2px 8px rgba(10,61,58,0.06)',
        coral: '0 4px 20px rgba(255,107,71,0.4)',
        teal: '0 4px 16px rgba(37,164,151,0.35)',
      },
      maxWidth: { container: '1240px', content: '720px' },
    },
  },
};
```

For per-theme font swaps, keep `colors_and_type.css` imported and let `[data-theme]` overrides drive `--font-display` / `--font-body`. Tailwind handles tokens; CSS handles theme switching.

---

## Implementation Notes

- **Spacing:** 8px grid. Per-variant section/card padding in JSON `spacing` block.
- **Accessibility:** All combinations meet WCAG AA (4.5:1+). Deep Teal on Pearl is 9.5:1 (AAA). Always use visible focus indicators.
- **Midnight:** glass cards `rgba(28,87,83,0.5)` + `backdrop-filter: blur(16px)`. `--fg-1: #faf7f5`, `--fg-2: #A1E4DB`.
- **Logos:** canonical SVG component at `hayahai-design/project/assets/HayahaiLogo.jsx`. Use inline SVG snippets from the section above for HTML pages.
- **Don't render preview/auth HTML in a browser unless asked** — read the source directly.
