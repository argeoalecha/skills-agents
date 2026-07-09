---
name: theme-client
description: Client brand intake skill. Converts a client brand brief (logo + 1–3 colors + optional fonts + mood) into a complete, project-scoped theme spec (theme.json, tokens.css, tailwind.config.js, logo SVGs, BRAND.md) stored under `<project-root>/brand/`. The output plugs into /company-site, /ui-builder, and /auth-page-scaffold the same way /theme-hayahai does — same shape, different palette. Use at the start of any client engagement where the project must follow the client's brand instead of Hayah-AI's. Triggers on /theme-client, "set up the brand for this client", "we're building a site for X, here's their logo", "import client brand", "configure brand for project".
user-invocable: true
---

# Theme-Client — Client Brand Intake

The parallel of `/theme-hayahai` for **client work**. Hayah-AI is your portfolio brand (5 fixed variants). This skill handles every other brand: one run per client engagement, output dropped into the project's `brand/` folder, consumed by the same downstream skills.

**Default mode:** full auto-fill. The agent generates everything the user didn't specify using defensible rules (see "Auto-fill rules" below). User confirms once at the end. Visual identity only — no voice/copy rules in v1.

---

## Skill Root

All paths relative to: `~/.claude/skills/theme-client/`

| Path | What it is |
|---|---|
| `assets/theme-template.json` | Skeleton client theme JSON — mirrors the shape of `theme-hayahai/.../themes/hayah-*.json` |
| `assets/BRAND-template.md` | Skeleton `BRAND.md` for the project root |

Output is written to **`<project-root>/brand/`**, not into this skill folder.

---

## Relationship with sibling skills

| Skill | Role |
|---|---|
| `/theme-hayahai` | **Hayah-AI portfolio brand only.** Five fixed variants. Do not modify per client. |
| **`/theme-client`** (this) | **Per-client brand intake.** Generates a project-scoped theme spec. |
| `document-skills:theme-factory` | One-off generic artifacts (slides, demos, internal docs). **Not** for client deliverables. |
| `/ui-builder` Phase 1 | Routes "External client" requests here instead of an ad-hoc "Custom" path. |
| `/company-site` Phase 0 | Reads `<project-root>/brand/theme.json` instead of a Hayah variant when the project is client work. |
| `/auth-page-scaffold` | Reads the same brand spec when generating auth pages. |

---

## Phase 0 — Intake (single block, never split)

Ask all questions at once. Mark `[required]` and `[optional — auto-filled if blank]`:

| Field | Required? | Notes |
|---|---|---|
| Client name | **Required** | Full legal / brand name |
| Slug | **Required** | kebab-case identifier, used in file paths |
| Primary brand color | **Required** | Hex (`#0066ff`) or named — anchor of the palette |
| Logo | Strongly recommended | Paste SVG markup, give a file path, or upload. If absent, generate a wordmark using the chosen typography + primary color. |
| Secondary color | Optional | If absent, generated as analog or complement of primary |
| Accent / CTA color | Optional | If absent, generated for WCAG AA contrast against background |
| Background preference | Optional | Light / Dark / "match the brand mood". Default: light |
| Display font | Optional | If absent, picked from mood + industry |
| Body font | Optional | If absent, picked to pair with display |
| Mood (one word) | Optional | refined · bold · warm · modern · playful · serious · technical · luxe. Default: refined |
| Corner radius | Optional | sharp (0–4px) · medium (8–16px) · rounded (20–28px). Default: medium |
| Industry | Optional | Informs voice/font picks. Default: "general" |
| Logo aspect | Optional | wordmark · mark-only · combination. Default: combination |

After receiving answers, **state the auto-fills you will apply** (palette shades, accent, fonts, radii) in one block, then ask for a single confirmation before writing files.

---

## Phase 1 — Auto-fill rules (full-auto mode)

When the user leaves a field blank, apply these rules.

### Palette generation from primary

Given a primary hex `P` (e.g. `#0066ff`), derive in HSL space:

| Token | Rule |
|---|---|
| `primary-500` | `P` exactly |
| `primary-400` | Lighten `P` by 12% lightness, keep hue/saturation |
| `primary-300` | Lighten `P` by 25% lightness |
| `primary-200` | Lighten `P` to ~90% lightness, drop saturation to ~30% |
| `primary-100` | Lighten `P` to ~95% lightness, drop saturation to ~15% |
| `primary-600` | Darken `P` by 12% lightness |
| `primary-700` | Darken `P` by 25% lightness |
| `primary-800` | Darken `P` to ~20% lightness |
| `primary-900` | Darken `P` to ~12% lightness — used for text on light bg |

### Accent / CTA color

If the user didn't give a secondary or accent:
1. Compute the HSL complement of `P` (rotate hue by 180°). Call it `C`.
2. If `C` has WCAG 3:1+ contrast vs the chosen background → use `C` at 50% saturation.
3. Else rotate `P` by +60° (analog) and adjust lightness for AA contrast.
4. Never pick a hue inside ±15° of `P` — collisions look like a bug.

### Background

| Pref | Light | Dark |
|---|---|---|
| `bg` | Tinted near-white using `primary-100` mixed 50/50 with `#ffffff`, capped at 98% lightness | `primary-900` mixed 70/30 with `#0a0a0a` |
| `surface` | Pure white `#ffffff` (or `primary-100` if user wants warmth) | `primary-800` |
| `card` | `primary-100` at very low saturation | `primary-700` at 60% saturation |

Never use pure `#000000`. Never use pure `#ffffff` if the brand mood is warm — use the tint.

### Text colors

| Token | Light bg | Dark bg |
|---|---|---|
| `text` | `primary-900` (or near-black `#0f1115` if primary is too desaturated) | `bg` mixed with 95% white |
| `muted` | `primary-700` at 50% saturation | `bg` mixed with 70% white |
| `subtle` | `primary-600` at 30% saturation | `bg` mixed with 45% white |

Verify text contrast hits **WCAG AA 4.5:1** minimum. If it fails, darken/lighten by 5% steps until it passes.

### Typography pairing by mood

| Mood | Display | Body | Notes |
|---|---|---|---|
| **Refined** | DM Serif Display | Inter | Default, premium SaaS feel |
| **Bold** | Space Grotesk | Inter | Tech / startup |
| **Warm** | Fraunces | Outfit | Hospitality / wellness / F&B |
| **Modern** | Inter | Inter | Single-family minimal |
| **Playful** | Fraunces (italic accents) | Outfit | Consumer / creative |
| **Serious** | Plus Jakarta Sans (700+) | Plus Jakarta Sans | Legal / finance / professional services |
| **Technical** | JetBrains Mono (display) | Inter | Dev tools / engineering |
| **Luxe** | Cormorant Garamond | Inter | Real estate / jewellery / luxury services |

Pull Google Fonts URLs from Google's font CDN and include in the generated `tokens.css` head block.

### Corner radius

| Pref | xs | sm | md | lg | xl | full |
|---|---|---|---|---|---|---|
| Sharp | 0 | 0 | 2 | 4 | 8 | 9999 |
| Medium (default) | 6 | 10 | 16 | 20 | 28 | 9999 |
| Rounded | 10 | 16 | 24 | 32 | 40 | 9999 |

### Shadow system

Tinted to the primary color (same pattern as `/theme-hayahai`):

```css
--shadow-xs: 0 1px 2px rgba({primary-rgb}, 0.05);
--shadow-sm: 0 2px 8px rgba({primary-rgb}, 0.06);
--shadow-md: 0 4px 16px rgba({primary-rgb}, 0.08);
--shadow-lg: 0 8px 32px rgba({primary-rgb}, 0.10);
--shadow-cta: 0 4px 20px rgba({accent-rgb}, 0.4);
```

### Spacing

Always 8px grid. Same as Hayah. Don't customise per client unless they explicitly request it.

---

## Phase 2 — Output

Write all files into `<project-root>/brand/`. Read the templates at `assets/theme-template.json` and `assets/BRAND-template.md` — substitute every `{{placeholder}}` with the resolved value.

```
<project-root>/brand/
├── theme.json           # Same shape as theme-hayahai/.../hayah-classic.json
├── tokens.css           # CSS variables (palette, type, radii, shadows)
├── tailwind.config.js   # Tailwind theme.extend map
├── logo.svg             # Light-bg variant — provided or generated wordmark
├── logo-dark.svg        # Dark-bg variant — recolored for dark surfaces
└── BRAND.md             # Palette rationale, type, decisions log
```

### theme.json shape (must match Hayah variant JSONs)

```json
{
  "name": "{{client-slug}}",
  "client": "{{client-name}}",
  "colors": {
    "primary":     "{{primary-500}}",
    "primaryLit":  "{{primary-400}}",
    "primaryDark": "{{primary-700}}",
    "accent":      "{{accent}}",
    "background":  "{{bg}}",
    "surface":     "{{surface}}",
    "card":        "{{card}}",
    "border":      "{{border}}",
    "text":        "{{text}}",
    "textMuted":   "{{muted}}",
    "textSubtle":  "{{subtle}}"
  },
  "typography": {
    "googleFontsUrl": "{{fonts-url}}",
    "displayFont": "{{display-font}}",
    "bodyFont": "{{body-font}}",
    "scale": { "h1": "clamp(2.5rem, 6vw, 5rem)", "h2": "clamp(2rem, 4.5vw, 3.5rem)", "h3": "1.5rem", "body": "1rem", "small": "0.875rem" }
  },
  "radii": { "xs": "{{r-xs}}", "sm": "{{r-sm}}", "md": "{{r-md}}", "lg": "{{r-lg}}", "xl": "{{r-xl}}", "full": "9999px" },
  "shadows": { "xs": "{{shadow-xs}}", "sm": "{{shadow-sm}}", "md": "{{shadow-md}}", "lg": "{{shadow-lg}}", "cta": "{{shadow-cta}}" },
  "spacing": "8px"
}
```

This is the **same shape** `/company-site` reads from `hayah-*.json` — drop-in compatible.

### Logo handling

| User provided | Action |
|---|---|
| SVG markup or .svg file | Optimise (strip metadata), ensure `viewBox` is set, ensure colors use `currentColor` or explicit hex. Save as `logo.svg`. Generate `logo-dark.svg` by swapping fill colors to light variants. |
| PNG / JPG / WEBP | Save the raster at `brand/logo-original.{ext}`. Generate a simple SVG wordmark using the display font + primary color as `logo.svg`. Note in `BRAND.md` that vectorisation is needed. |
| Nothing | Generate a wordmark SVG: `<text>` element with display font, primary color, kebab-case label. Compact + panel variants like `/theme-hayahai`. |

### `tokens.css` skeleton

```css
@import url('{{fonts-url}}');

:root {
  --color-primary: {{primary-500}};
  --color-primary-lit: {{primary-400}};
  --color-primary-dark: {{primary-700}};
  --color-accent: {{accent}};
  --color-bg: {{bg}};
  --color-surface: {{surface}};
  --color-card: {{card}};
  --color-border: {{border}};
  --color-text: {{text}};
  --color-muted: {{muted}};
  --color-subtle: {{subtle}};

  --font-display: '{{display-font}}', system-ui, sans-serif;
  --font-body: '{{body-font}}', system-ui, sans-serif;

  --r-xs: {{r-xs}}; --r-sm: {{r-sm}}; --r-md: {{r-md}};
  --r-lg: {{r-lg}}; --r-xl: {{r-xl}}; --r-full: 9999px;

  --shadow-xs: {{shadow-xs}};
  --shadow-sm: {{shadow-sm}};
  --shadow-md: {{shadow-md}};
  --shadow-lg: {{shadow-lg}};
  --shadow-cta: {{shadow-cta}};
}

html { scroll-behavior: smooth; }
body { background: var(--color-bg); color: var(--color-text); font-family: var(--font-body); -webkit-font-smoothing: antialiased; }
::selection { background: var(--color-primary); color: #fff; }
```

### `tailwind.config.js` skeleton

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: { 100: '{{p100}}', 200: '{{p200}}', 300: '{{p300}}', 400: '{{p400}}', 500: '{{p500}}', 600: '{{p600}}', 700: '{{p700}}', 800: '{{p800}}', 900: '{{p900}}' },
        accent: '{{accent}}',
        bg: '{{bg}}', surface: '{{surface}}', card: '{{card}}',
        text: '{{text}}', muted: '{{muted}}', subtle: '{{subtle}}',
      },
      fontFamily: {
        display: ['{{display-font}}', 'system-ui', 'sans-serif'],
        body: ['{{body-font}}', 'system-ui', 'sans-serif'],
      },
      borderRadius: { xs: '{{r-xs}}', sm: '{{r-sm}}', md: '{{r-md}}', lg: '{{r-lg}}', xl: '{{r-xl}}' },
      boxShadow: {
        xs: '{{shadow-xs}}', sm: '{{shadow-sm}}', md: '{{shadow-md}}', lg: '{{shadow-lg}}', cta: '{{shadow-cta}}',
      },
    },
  },
};
```

---

## Phase 3 — Wire into downstream skills

After files are written:

### For `/company-site`

The reference templates (`template-industrial.jsx`, `template-saas.jsx`, `template-local-business.jsx`) all read from a `SITE_CONFIG.theme` block. Replace that block by reading `<project-root>/brand/theme.json`:

```js
import brandTheme from "../brand/theme.json";

const SITE_CONFIG = {
  brand: { ...client brand fields... },
  theme: {
    bg:        brandTheme.colors.background,
    surface:   brandTheme.colors.surface,
    card:      brandTheme.colors.card,
    border:    brandTheme.colors.border,
    accent:    brandTheme.colors.primary,
    accentLit: brandTheme.colors.primaryLit,
    cyan:      brandTheme.colors.accent,
    text:      brandTheme.colors.text,
    muted:     brandTheme.colors.textMuted,
    subtle:    brandTheme.colors.textSubtle,
  },
  // ... rest unchanged
};
```

Also swap `SITE_CONFIG.brand.shortName` source to the client wordmark, and reference `<project-root>/brand/logo.svg` instead of redrawing.

### For `/ui-builder`

When Phase 1 detects "External client", call `/theme-client` first to produce `<project-root>/brand/`, then read it for all subsequent layout / component decisions. No more ad-hoc "Custom" path.

### For `/auth-page-scaffold`

Same pattern — read `<project-root>/brand/theme.json` and `brand/logo.svg`, apply to the auth-page template that matches the closest Hayah variant (Classic / Coral / Midnight by mood).

---

## Quality gates before declaring done

- [ ] `brand/theme.json` validates against the canonical shape (run a quick mental shape check)
- [ ] All 11 color tokens resolved to real hex values (no `undefined`, no placeholder strings)
- [ ] WCAG AA contrast verified for text-on-bg, text-on-surface, text-on-card, accent-on-bg
- [ ] Display + body fonts both have valid Google Fonts URLs
- [ ] `logo.svg` exists and renders (open in browser or check `viewBox` + paint instructions)
- [ ] `logo-dark.svg` exists with swapped colors for dark surfaces
- [ ] `BRAND.md` documents: client name, palette rationale, type rationale, source of logo (provided / vectorised / generated), date
- [ ] `tailwind.config.js` is valid JS that exports a config object

---

## Reusing a client brand later

Even though storage is per-project, you can copy `brand/` between projects for the same client:

```bash
cp -r /path/to/old-project/brand /path/to/new-project/brand
```

For frequent repeat clients, consider promoting `brand/` to `~/.claude/brands/<slug>/` manually after a few engagements — the skill won't manage that automatically (per design decision), but the file shape is identical.

---

## Out of scope (v1)

- **Voice / copy rules** — clients' tone-of-voice guidelines are not generated; use their existing brand guide or write per-project
- **Brand strategy / positioning** — this is asset intake, not strategy
- **Logo design from a verbal description** — we wrap, vectorise, or generate a wordmark only; full logo design needs a designer
- **Trademark / legal checks** — counsel
- **Multi-variant brand systems** (e.g. parent + sub-brand) — generate each separately
- **Cross-project brand library** (`~/.claude/brands/`) — deliberately out of scope; per-project storage only
