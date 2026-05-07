# Hayah Design System

> Five themes. One brand. The Hayah palette stays constant — only the personality changes.

**Hayah-ai Design** is a brand language built around a consistent core palette (deep teal, aqua, coral, cream) that flexes across **five thematic personalities**. Pick the theme that matches the product surface — or compose them across a multi-product portfolio.

---

## The five themes

| Theme | Mood | Use for | Display / Body |
|---|---|---|---|
| **Classic** | Sophisticated, trustworthy | SaaS landing pages, professional services | DM Serif Display + Plus Jakarta Sans |
| **Coral** | Warm, approachable, energetic | Consumer, marketplaces, wellness, e-comm | Fraunces + Outfit |
| **Editorial** | Bold, authoritative, type-led | Thought leadership, premium launches | Clash Display + Satoshi |
| **Bento** | Innovative, dynamic, technical | AI products, dev tools, modern SaaS | Space Grotesk + Inter |
| **Midnight** | Powerful, cutting-edge | Dark dashboards, AI/fintech, platforms | Syne + Inter |

All five share these brand colors:

- **Teal anchor** `#0a3d3a` / `#0F3836` — primary text + dark surfaces
- **Aqua primary** `#25A497` — links, focus, technical accent
- **Mint** `#A1E4DB` / `#e8f4f1` — soft surfaces, borders
- **Coral accent** `#ff6b47` — CTAs, energy, the "warm" voice
- **Cream page** `#faf7f5` — never stark white in the light themes

---

## Sources

- **Source codebase:** mounted at `themes/` (5 theme JSON files, version 2.0).
  - `themes/hayah-classic.json`
  - `themes/hayah-coral.json`
  - `themes/hayah-editorial.json`
  - `themes/hayah-bento.json`
  - `themes/hayah-midnight.json`

The theme JSONs are the canonical source of truth. They've been copied into this project at the same paths.

---

## Index

- `README.md` — this file
- `SKILL.md` — instructions for use as a Claude Code skill
- `colors_and_type.css` — single source CSS variables + theme overrides + semantic type classes
- `themes/` — original 5 theme JSON definitions (v2.0)
- `assets/` — logos, marks, brand imagery placeholders
- `preview/` — design system review cards (rendered in the Design System tab)
- `ui_kits/` — high-fidelity component kits per product surface
  - `ui_kits/landing/` — the marketing site (theme-switchable)
  - `ui_kits/app/` — a product app shell (dashboard / chat)
- `slides/` — slide deck templates using the brand language

---

## CONTENT FUNDAMENTALS

The brand voice is **calm, confident, and contemporary** — never shouty, never ironic, never overly casual. The themes share copy DNA but adjust register slightly:

- **Classic / Editorial** lean editorial-confident: declarative sentences, sparing adjectives, the occasional rhetorical pivot.
- **Coral** is warmer and more human — uses "you," softens edges with everyday language.
- **Bento / Midnight** take a technical-precise voice: shorter, more product-led, more verbs.

### Tone & casing

- **Sentence case** for headings and buttons. **Never** Title Case in UI. ("Get started" not "Get Started").
- **Hero headlines** are short, declarative, and often single-clause — under ~10 words. No question-form headlines.
- **No exclamation points** in marketing copy. Confidence comes from the words, not the punctuation.
- **No emoji** in product UI or marketing copy. The brand is restrained; warmth comes from color and typography.
- **Em-dashes** are welcome — for emphasis or dependent clauses. So are short fragments. Periods optional on standalone display lines.
- **Numbers as numerals** in metrics (`12k+`, `2.4M`, `99.9%`).
- **Technical terms** stay precise; no euphemisms ("AI" not "intelligence layer").

### "I" vs "you"

- Marketing copy uses **"you"** ("Ship faster", "Your team's…").
- Product copy uses **second-person commands** ("Connect a source", "Invite teammates"), occasional first-person from the user POV in chat-style UIs ("My workspace").

### Voice examples

| Good | Avoid |
|---|---|
| Built for teams that ship. | Empower your team to unleash productivity 🚀 |
| Connect a source. | Let's get you set up! |
| Real-time. End-to-end. | Best-in-class enterprise-grade synergy |
| Pricing that scales with you. | Plans for every size and shape! |
| New: live previews | NEW! Live previews are here! |

### Eyebrow / label voice

Eyebrows are **uppercase, tracked-out, brief** — usually a section label or a category, not a sentence. Examples: `PRODUCT`, `WHAT'S NEW`, `FOR DEVELOPERS`, `2026 RELEASE`.

---

## VISUAL FOUNDATIONS

### Color usage

The four-color core palette is fixed. **Coral and aqua never appear in the same hierarchy at the same weight** — one leads, the other supports. In Coral theme, coral leads and teal is text + footer. In Bento/Midnight, teal/aqua leads and coral is the "energy" accent. In Classic and Editorial, teal anchors and coral is the CTA.

- **Page bg** is always cream `#faf7f5` (light themes) or deep teal `#0F3836` (Midnight). **Never pure white** for the page surface in light themes — always cream — except Editorial, which intentionally uses pure white to amplify the typographic focus.
- **Text on light** is `#0a3d3a` (teal-900), not black. Black is too cold against cream.
- **Text on dark** is `#faf7f5` (cream), not white. Same warmth principle inverted.

### Typography

Hayah pairs a **distinctive display face** with a **neutral, humanist body**. The display does the personality lift; the body stays out of the way.

- Display sizes go big (hero up to **96px** in Editorial). Always pair with **negative letter-spacing** (`-0.025em` to `-0.045em`) — looser tracking would feel weak.
- Body type runs at **16px / line-height 1.7** for breathability — this is a generous, editorial body rhythm, not a dense product-doc rhythm.
- Labels / eyebrows are **all-caps, tracked +0.06–0.12em**, weight 600–700. They function as small structural cues.
- **Don't mix multiple display fonts** in one page. Pick a theme and commit.

### Backgrounds

- Page background: cream `#faf7f5` (or dark `#0F3836`). Subtle radial gradients are common in hero sections (`radial-gradient(ellipse 100% 80% at 50% -20%, rgba(37,164,151,0.15) 0%, transparent 60%)`).
- **No grain, no textures, no hand-drawn illustrations.** The look is digital-clean.
- **Mesh gradients** appear in Bento (subtle teal + coral wash). **Glassmorphism** appears in Bento and Midnight (`rgba(28, 87, 83, 0.4)` + `backdrop-filter: blur(16px)`). Never combine glass + heavy shadow on the same element — pick one.
- **Full-bleed images:** rare. The brand prefers structured, editorial layouts over photography-led pages. When images appear, they're warm-toned and high-contrast — never washed out, never overly saturated.
- Editorial uses **horizontal rules** as structural devices (`1px` teal, `3px` coral for emphasis). Other themes do not.

### Animation

- **Subtle and functional only.** Easing: `cubic-bezier(0.4, 0, 0.2, 1)` (ease-in-out). Standard duration: 150ms (micro-interactions), 250ms (hover/expand), 400ms (page-level transitions).
- **No bounces. No springs over 1.0 overshoot. No spinning loaders with personality** — use a clean teal progress bar or a quiet pulse.
- Fades and small (~4px) translates only. Hero elements may stagger-fade-up on load (`opacity 0→1, translateY 8px→0`, 60ms stagger).
- Hover transitions: `transition: color 150ms, background 150ms, transform 200ms`.

### Hover & press states

- **Buttons (primary, coral):** hover darkens to `#e55a38`. No size change. Subtle shadow strengthens.
- **Buttons (primary, teal):** hover darkens to `#1E6E66`.
- **Secondary buttons:** hover fills with `rgba(37,164,151,0.1)` or inverts to dark fill.
- **Links:** hover swaps from teal `#1E6E66` to coral `#ff6b47`. (Or coral → teal in Coral theme.)
- **Cards:** hover lifts shadow from `--shadow-sm` to `--shadow-md`. Never scale; never tilt.
- **Press state:** brief darken (~6%) + 50ms transition. No `transform: scale(0.98)`.

### Borders

- Default border: `1px solid rgba(161, 228, 219, 0.4)` — the brand's signature soft mint-tinted border.
- Strong border: `1px solid #A1E4DB` (mint), or `2px solid #0F3836` in Editorial.
- Editorial uses **3px or 4px top borders** as accents on cards (`border-top: 3px solid #0F3836`).
- On dark surfaces (Midnight): `rgba(161, 228, 219, 0.15)` for default, `0.4` for strong.

### Shadow system

Soft, teal-tinted, never harsh black:

```
--shadow-xs: 0 1px 2px rgba(10, 61, 58, 0.05);
--shadow-sm: 0 2px 8px rgba(10, 61, 58, 0.06);
--shadow-md: 0 4px 16px rgba(10, 61, 58, 0.08);
--shadow-lg: 0 8px 32px rgba(10, 61, 58, 0.10), 0 2px 8px rgba(10, 61, 58, 0.06);
--shadow-coral: 0 4px 20px rgba(255, 107, 71, 0.4);   /* coral CTAs only */
--shadow-teal:  0 4px 16px rgba(37, 164, 151, 0.35);  /* aqua CTAs only */
--glow-teal:    0 0 40px rgba(37, 164, 151, 0.2);     /* Midnight only */
--glow-coral:   0 0 40px rgba(255, 107, 71, 0.3);     /* Midnight only */
```

CTAs **always** get a colored shadow (coral or teal). Cards never do — cards use neutral shadows.

### Corner radii

- Default: `--r-md: 16px`, `--r-lg: 20px` for cards, `--r-xl: 28px` for hero cards.
- Buttons: `10–12px` (most themes), `0px` (Editorial only).
- Inputs: `10–12px`.
- **Pills** (badges, navs in Bento): `9999px` or `16px` capsule.
- **Editorial overrides everything to `0px`** — sharp corners are core to its identity.

### Layout rules

- **Container max-width** ranges 1200–1280px depending on theme.
- **Content max-width** for prose: 680–800px (never wider — readability over screen-fill).
- **Section padding** vertical: `96–120px` per theme. Generous.
- **Card gap** in grids: 16–24px. Editorial uses **2px** for hairline-divided block grids.
- **Bento** is the only theme with asymmetric grid (cards spanning 1×1, 2×1, 2×2 cells).
- Navs are **fixed top, glass-blurred** in Bento/Midnight; solid white in Classic/Editorial.

### Transparency & blur

- Glass surfaces only on Bento + Midnight: `rgba(28,87,83,0.4–0.5)` + `backdrop-filter: blur(16–20px)`.
- Light themes use **opaque cards**. No glass on cream — it muddies.
- Nav blur: `backdrop-filter: blur(12–20px)` with semi-transparent bg.

### Imagery vibe

- Warm-leaning, editorial photography. Natural light. No HDR drama, no overlays, no duotone treatments.
- Product screenshots: shown on a soft cream backplate (`#faf7f5`) with a subtle shadow, often rotated slightly (1–2deg) when used in marketing — never in product UI.
- Avoid stock-feeling imagery. Avoid bluish-purple gradients (off-brand).

### Cards

- **Light card (default):** white bg, `1px` mint border, `--r-lg` (20px), `--shadow-sm`, `28–32px` padding.
- **Soft card:** mint-tinted bg `#e8f4f1`, no shadow, optional `1px` mint border.
- **Warm card:** `#fff5f2`, coral-subtle border.
- **Dark feature card:** deep teal gradient or solid `#0a3d3a`, cream text.
- **Glass card** (Bento/Midnight only): semi-transparent + blur.
- **Editorial card:** sharp `0px` corners, `3px` solid teal top-border accent.

---

## ICONOGRAPHY

The Hayah codebase **does not ship a custom icon set**. Theme JSONs do not reference any icon assets, sprites, or icon fonts. So the recommended approach is:

- **Primary icon library: [Lucide](https://lucide.dev)** — clean, geometric, 1.5px stroke (sometimes 2px), rounded line caps. Pairs perfectly with all five themes. Available via CDN: `https://unpkg.com/lucide@latest`.
- **Stroke width:** 1.5px default, 2px for emphasis. Never mix weights.
- **Icon sizes:** 16, 20, 24px in UI; 32–48px for feature cards; 64–96px for hero illustrations.
- **Icon color:** inherits text color (`currentColor`). Aqua `#25A497` for primary action icons; coral `#ff6b47` reserved for warnings/highlights/CTAs only.

Lucide is the confirmed icon library for this design system.

### Emoji usage

- **Never** in product UI.
- **Never** in marketing copy or buttons.
- Acceptable in social/blog content only (not in this design system's scope).

### Unicode characters

- **Arrows** are common: `→` `↗` `↑` are used inline with body text and on link hovers (e.g. "Read more →").
- **Bullets** in lists: `•` (middle dot) for inline series, regular disc for vertical lists.
- **Em dash** `—` and **en dash** `–` follow standard editorial rules.

### Logo

The canonical logo is `assets/HayahaiLogo.jsx` — an inline SVG with arc mark, coral dot, and "hayah-ai" wordmark (DM Serif Display). Two variants: light bg (teal stroke, teal wordmark) and dark bg (cream stroke, cream wordmark). Always include the tagline — default is "business automation" but it is variable per project. See the root `SKILL.md` for inline SVG snippets to use in HTML pages.

---

## How to use this system

1. **Pick a theme** by setting `<html data-theme="classic|coral|editorial|bento|midnight">`.
2. **Import** `colors_and_type.css` — it sets all CSS variables and overrides per-theme.
3. **Use semantic classes** (`.t-hero`, `.t-h1`, `.eyebrow`, `.t-body`) or just `<h1>`, `<h2>`, `<p>` — both work.
4. **Reference variables** directly: `color: var(--fg-1)`, `background: var(--bg-card)`, `border-radius: var(--r-lg)`.
5. **For new themes,** add a `[data-theme="..."]` block in `colors_and_type.css` that overrides only what changes (typically font + a couple of sizes).

---

## Notes

- **Clash Display + Satoshi** (Editorial theme) load from Fontshare CDN. Fallback: Space Grotesk + Plus Jakarta Sans.
