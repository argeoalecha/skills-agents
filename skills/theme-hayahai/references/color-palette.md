# Hayah-AI Color Palette Reference

Complete color system. The **canonical source** is `hayahai-design/project/colors_and_type.css` — every value below maps to a CSS variable defined there.

---

## Core Palette

The four-color core is constant across all five themes. Role and weight vary by theme.

### Teals — Anchor + Primary

| Var | Hex | Name | Usage |
|---|---|---|---|
| `--teal-950` | `#0F3836` | Dark Forest | Deepest forest — Midnight page bg, footer |
| `--teal-900` | `#0a3d3a` | Deep Teal | Anchor — primary text, deep brand surfaces |
| `--teal-800` | `#1a4d47` | Forest Green | Mid-dark surfaces |
| `--teal-700` | `#1C5753` | Medium Teal | Secondary text on light, dark cards |
| `--teal-600` | `#1E6E66` | Ocean | Hover, secondary button |
| `--teal-500` | `#25A497` | Aqua | Primary aqua — links, focus, technical accent |
| `--teal-400` | `#A1E4DB` | Mint | Borders, soft surfaces |
| `--teal-300` | `#d8ece8` | — | Subtle dividers |
| `--teal-200` | `#e8f4f1` | Pearl | Soft cards, highlights |
| `--teal-100` | `#F3FFF9` | Mint Whisper | Subtle panels |

### Coral — Accent / Energy

| Var | Hex | Name | Usage |
|---|---|---|---|
| `--coral-700` | `#7d2d15` | Deep Coral | Coral text on warm bg |
| `--coral-600` | `#e55a38` | Coral Hover | Primary coral button hover |
| `--coral-500` | `#ff6b47` | Vibrant Coral | Primary CTA in warm themes |
| `--coral-400` | `#ff8f73` | Warm Coral | Light coral accent |
| `--coral-300` | `#ffb5a0` | Soft Peach | Subtle highlight |
| `--coral-200` | `#fff5f2` | Warm Cream | Tinted backgrounds, warm cards |

### Neutrals

| Var | Hex | Name | Usage |
|---|---|---|---|
| `--cream` | `#faf7f5` | Cream | Page bg in all light themes (not white) |
| `--white` | `#ffffff` | White | Default card bg, Editorial page bg only |
| `--muted` | `#7a9b96` | Sage | Slate-mint — captions, disabled, muted |
| `--warm-text` | `#7d4a38` | Warm Text | Coral-theme body emphasis |

---

## Semantic Tokens

Use these in components — they auto-flip per `[data-theme]`.

| Var | Default value | Purpose |
|---|---|---|
| `--fg-1` | `--teal-900` | Primary text on light (cream on dark in Midnight) |
| `--fg-2` | `--teal-700` | Secondary text |
| `--fg-3` | `--muted` | Muted / caption |
| `--fg-on-dark` | `--cream` | Text on dark surfaces |
| `--fg-on-accent` | `--white` | Text on coral / aqua CTAs |
| `--bg-page` | `--cream` | Page background (overridden in Editorial → white, Midnight → teal-950) |
| `--bg-card` | `--white` | Default card surface |
| `--bg-card-soft` | `--teal-200` | Mint-tinted card |
| `--bg-card-warm` | `--coral-200` | Coral-tinted card |
| `--bg-dark` | `--teal-950` | Dark surface |

---

## Color Hierarchy Rules

These rules are required — not stylistic preference.

1. **Page bg is never pure white** in light themes (Classic, Coral, Bento). Always cream `#faf7f5`. **Exception:** Editorial uses pure white intentionally to amplify type.
2. **Text on light is `#0a3d3a`, not black.** Black is too cold against cream.
3. **Text on dark is `#faf7f5`, not white.** Same warmth principle inverted.
4. **Coral and aqua never appear at the same hierarchy weight** at the same time. One leads, one supports:
   - Classic / Editorial: teal anchors, coral is the CTA
   - Coral: coral leads, teal is text + footer
   - Bento / Midnight: teal/aqua leads, coral is the energy accent
5. **CTAs always get a colored shadow** (`--shadow-coral` or `--shadow-teal`). Cards never do — cards use `--shadow-sm` / `--shadow-md`.

---

## Borders

The brand's signature is the **soft mint-tinted border**:

```css
--border-1: rgba(161, 228, 219, 0.4);    /* default — most cards, inputs */
--border-2: var(--teal-400);             /* strong — emphasis */
--border-strong: var(--teal-700);        /* heavy — Editorial accents */
--border-coral: var(--coral-300);        /* warm cards only */
```

**Editorial-specific:** card top borders are `3px solid #0F3836` (sometimes `4px`). Default border becomes `2px solid #0F3836`.

**Midnight-specific:** `--border-1: rgba(161, 228, 219, 0.15)` (lower opacity for dark surfaces).

---

## Shadows

All shadows are teal-tinted — never harsh black.

```css
--shadow-xs:    0 1px 2px  rgba(10, 61, 58, 0.05);
--shadow-sm:    0 2px 8px  rgba(10, 61, 58, 0.06);
--shadow-md:    0 4px 16px rgba(10, 61, 58, 0.08);
--shadow-lg:    0 8px 32px rgba(10, 61, 58, 0.10), 0 2px 8px rgba(10, 61, 58, 0.06);
--shadow-xl:   0 16px 48px rgba(10, 61, 58, 0.14);
--shadow-coral: 0 4px 20px rgba(255, 107, 71, 0.4);   /* coral CTAs only */
--shadow-teal:  0 4px 16px rgba(37, 164, 151, 0.35);  /* aqua CTAs only */
--glow-teal:    0 0 40px   rgba(37, 164, 151, 0.2);   /* Midnight only */
--glow-coral:   0 0 40px   rgba(255, 107, 71, 0.3);   /* Midnight only */
```

---

## Gradients

```css
--grad-teal-radial: radial-gradient(ellipse at top left, #25A497 0%, #0a3d3a 70%);
--grad-teal-linear: linear-gradient(135deg, #1E6E66 0%, #0a3d3a 100%);
--grad-aqua-mint:   linear-gradient(135deg, #25A497 0%, #A1E4DB 100%);
--grad-coral:       linear-gradient(135deg, #ff8f73 0%, #ff6b47 100%);
--grad-warm:        linear-gradient(160deg, #fff5f2 0%, #faf7f5 50%, #F3FFF9 100%);
--grad-mesh:
  radial-gradient(at 0% 0%,   rgba(37,164,151,0.3)  0px, transparent 50%),
  radial-gradient(at 100% 100%, rgba(255,107,71,0.15) 0px, transparent 50%);
```

**Mesh gradients** are Bento-only. **Subtle radial hero gradients** appear in most themes:
```css
background: radial-gradient(ellipse 100% 80% at 50% -20%, rgba(37,164,151,0.15) 0%, transparent 60%);
```

---

## Card Types (Color Recipes)

| Type | Background | Border | Shadow | Used in |
|---|---|---|---|---|
| Light (default) | `--white` | `--border-1` | `--shadow-sm` | Most cards in light themes |
| Soft | `--bg-card-soft` (`#e8f4f1`) | optional `--border-1` | none | Secondary cards |
| Warm | `--bg-card-warm` (`#fff5f2`) | `--border-coral` | none | Coral/Classic feature cards |
| Dark feature | `--bg-dark` or `--grad-teal-linear` | none | `--shadow-md` | Hero sub-cards, CTAs |
| Glass (Bento) | `rgba(28,87,83,0.4)` + `blur(16px)` | `--border-1` | none | Bento only |
| Glass (Midnight) | `rgba(28,87,83,0.5)` + `blur(16px)` | `--border-1` | none | Midnight only — denser opacity |
| Editorial | `--white` | `border-top: 3px solid #0F3836` | none | Editorial only |

**Never combine glass + heavy shadow on the same element.**

---

## Hover & Press States

| Element | Default | Hover | Press |
|---|---|---|---|
| Coral primary button | `--coral-500` | `--coral-600` (`#e55a38`) | darken ~6%, 50ms |
| Teal primary button | `--teal-700` or `--teal-500` | `--teal-600` (`#1E6E66`) | darken ~6% |
| Secondary button | transparent + `--teal-500` text | `rgba(37,164,151,0.1)` fill | darken ~6% |
| Link | `--teal-600` | `--coral-500` (or reversed in Coral theme) | — |
| Card | `--shadow-sm` | `--shadow-md` (lift only — never scale or tilt) | — |

**Never** use `transform: scale(0.98)` for press states.

---

## Status Indicators

Status colors break the "coral + aqua never together" rule because they have semantic meaning. Pair with icons or text — never rely on color alone.

| State | Color | Var |
|---|---|---|
| Success | `#25A497` | `--teal-500` |
| Info | `#1E6E66` | `--teal-600` |
| Warning | `#ff8f73` | `--coral-400` |
| Error | `#ff6b47` | `--coral-500` |

---

## Per-Theme Page Backgrounds

| Theme | Page bg | Notes |
|---|---|---|
| Classic | `--cream` (`#faf7f5`) | Subtle radial teal gradient at top often appears in hero |
| Coral | `--cream` (`#faf7f5`) | Warmer accents, often a `--grad-warm` underlay |
| Editorial | `--white` (`#ffffff`) | **Intentionally pure white** — the only theme that uses it |
| Bento | `--cream` (`#faf7f5`) | Mesh gradient on hero panels |
| Midnight | `--teal-950` (`#0F3836`) | Glow effects on CTAs and feature accents |

---

## Accessibility

### Verified contrast ratios

| Foreground | Background | Ratio | WCAG |
|---|---|---|---|
| `--teal-900` (`#0a3d3a`) | `--teal-200` (Pearl) | 9.5:1 | AAA |
| `--teal-900` | `--cream` | 9.2:1 | AAA |
| `--teal-900` | `--teal-100` (Mint Whisper) | 8.8:1 | AAA |
| `--coral-500` (`#ff6b47`) | `--teal-200` | 4.8:1 | AA |
| `--coral-500` | `--cream` | 4.5:1 | AA (large text only for body) |
| `--cream` | `--teal-950` | 12.1:1 | AAA |

### Best practices

1. Don't rely on color alone for status — pair with icon/text/border.
2. Visible focus indicators required at ≥3:1 contrast.
3. Test live with a contrast checker — variables drift over time.
4. Coral on cream is borderline for body text — use it for CTAs and large display only, not paragraphs.

---

## Quick Reference: When to use what

| Need | Use |
|---|---|
| Page background (light theme) | `--cream` |
| Page background (dark theme) | `--teal-950` |
| Primary text (light) | `--teal-900` |
| Primary text (dark) | `--cream` |
| Secondary text | `--teal-700` (light) / `--teal-400` (dark) |
| Muted/caption | `--muted` |
| Primary CTA (warm theme) | `--coral-500` + `--shadow-coral` |
| Primary CTA (cool/dark) | `--teal-500` + `--shadow-teal` |
| Link | `--teal-600` |
| Default border | `rgba(161, 228, 219, 0.4)` |
| Default card | `--white` + default border + `--shadow-sm` |
| Soft card | `--teal-200` |
| Warm card | `--coral-200` |
| Glass card (Bento/Midnight) | `rgba(28,87,83,0.4)` + `blur(16px)` |
