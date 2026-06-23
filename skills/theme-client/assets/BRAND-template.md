# {{client-name}} — Brand System

Generated: {{iso-date}}
Slug: `{{client-slug}}`
Mood: {{mood}} · Industry: {{industry}}

This document captures every decision baked into the theme assets at `./brand/`. Edit here if any decision changes — the agent will re-derive the assets from this source of truth.

---

## Palette

| Token | Hex | Usage |
|---|---|---|
| Primary | `{{primary-500}}` | Buttons, links, headlines, key accents |
| Primary Light | `{{primary-400}}` | Hover states, secondary highlights |
| Primary Dark | `{{primary-700}}` | Pressed states, deep emphasis |
| Accent | `{{accent}}` | CTAs only — never compete with primary for hierarchy |
| Background | `{{bg}}` | Page background |
| Surface | `{{surface}}` | Section backgrounds, raised areas |
| Card | `{{card}}` | Card / panel backgrounds |
| Border | `{{border}}` | 1px dividers and outlines |
| Text | `{{text}}` | Primary copy |
| Muted | `{{muted}}` | Secondary copy, captions |
| Subtle | `{{subtle}}` | Placeholders, disabled state |

**Full palette scale (for design tokens):**

| 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 |
|---|---|---|---|---|---|---|---|---|
| `{{p100}}` | `{{p200}}` | `{{p300}}` | `{{p400}}` | `{{p500}}` | `{{p600}}` | `{{p700}}` | `{{p800}}` | `{{p900}}` |

**Rationale.** Primary `{{primary-500}}` was provided by the client. The 9-step scale was derived by lightening/darkening in HSL space ({{palette-rationale}}). Accent `{{accent}}` was {{accent-rationale}}. Background `{{bg}}` was {{bg-rationale}}. All text/background combinations were verified at WCAG AA 4.5:1 minimum.

---

## Typography

| Role | Font | Source |
|---|---|---|
| Display | **{{display-font}}** | {{display-source}} |
| Body | **{{body-font}}** | {{body-source}} |
| Mono (optional) | JetBrains Mono | Google Fonts |

**Google Fonts URL** (load once in the page head):
```
{{fonts-url}}
```

**Type scale:**

| Token | Value |
|---|---|
| H1 | `clamp(2.5rem, 6vw, 5rem)` — display font, weight 700, letter-spacing -0.025em |
| H2 | `clamp(2rem, 4.5vw, 3.5rem)` — display font, weight 700 |
| H3 | `1.5rem` — display font, weight 600 |
| Body | `1rem` (16px) — body font, line-height 1.7 |
| Small | `0.875rem` (14px) — body font |
| Label | `0.72rem` — body font, uppercase, letter-spacing 0.12em, weight 600 |

**Rationale.** {{type-rationale}}

---

## Corner Radii ({{radius-preference}})

| Token | Value | Usage |
|---|---|---|
| `--r-xs` | `{{r-xs}}` | Tags, chips |
| `--r-sm` | `{{r-sm}}` | Inputs, small buttons |
| `--r-md` | `{{r-md}}` | Cards, panels |
| `--r-lg` | `{{r-lg}}` | Hero cards, large surfaces |
| `--r-xl` | `{{r-xl}}` | Feature blocks |
| `--r-full` | `9999px` | Pills, avatars |

---

## Shadows

Tinted to the primary color. Subtle on light backgrounds, glow-style on dark.

```css
--shadow-xs:  {{shadow-xs}};
--shadow-sm:  {{shadow-sm}};
--shadow-md:  {{shadow-md}};
--shadow-lg:  {{shadow-lg}};
--shadow-cta: {{shadow-cta}};
```

**Rule.** CTA buttons get the tinted `--shadow-cta`. All other surfaces use neutral shadows (xs–lg). Never use harsh black shadows — keep the tint of the brand primary.

---

## Logo

| File | Use |
|---|---|
| `brand/logo.svg` | Light-background variant — nav, hero, marketing |
| `brand/logo-dark.svg` | Dark-background variant — footers, dark hero, inverse sections |

**Source:** {{logo-source}}
**Aspect:** {{logo-aspect}}

**Usage rules:**
- Minimum size: 24px tall in nav, 48px tall in hero.
- Clear space around the mark: equal to the x-height of the wordmark on all sides.
- Don't stretch, recolor, or apply effects. If the client supplies a colored variant for a marketing campaign, save it as `logo-{campaign}.svg` alongside.

---

## Voice & Copy

Out of scope for v1 brand intake. Use the client's existing brand guide if available, or write per-project. The agent will not auto-generate voice rules.

**Reasonable defaults when nothing is specified:**
- Sentence case for headlines and buttons (no Title Case).
- No exclamation points in marketing copy.
- Numbers as numerals in metrics (`12k+`, `2.4M`, `99.9%`).
- Em-dashes welcome. Short fragments fine.

---

## How this brand is consumed

| Skill | What it reads |
|---|---|
| `/company-site` | `brand/theme.json` → injected as `SITE_CONFIG.theme` block in templates; `brand/logo.svg` referenced in nav + footer |
| `/ui-builder` | All of `brand/` — uses for layout, components, and logo placement |
| `/auth-page-scaffold` | `brand/theme.json` + `brand/logo.svg` → applied to the matching Hayah variant skeleton |
| Direct Tailwind use | `brand/tailwind.config.js` extends Tailwind theme |
| Direct CSS use | `brand/tokens.css` provides CSS variables |

---

## Change log

| Date | Change | By |
|---|---|---|
| {{iso-date}} | Initial brand intake — auto-fill mode | /theme-client |
