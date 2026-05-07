# Hayah-AI Typography Reference

Each theme variant has its own font pairing. Never use a generic system. The **canonical source** is `claudedesign/hayah-ai-design-system/project/colors_and_type.css` — it imports all fonts at once and defines the type scale + semantic classes.

---

## Quick Path

If you're using `colors_and_type.css`, you don't need to manage font imports — it does that. Just write:

```html
<link rel="stylesheet" href="path/to/colors_and_type.css">
<html data-theme="classic">
```

The rest of this doc is for the case where you're hand-rolling fonts in a one-off artifact.

---

## Font Imports by Variant

### Hayah Classic — DM Serif Display + Plus Jakarta Sans
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

### Hayah Midnight — Syne + Inter
```html
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

### Hayah Coral — Fraunces + Outfit
```html
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,700;1,9..144,400&family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

### Hayah Editorial — Clash Display + Satoshi (Fontshare, NOT Google)
```html
<link href="https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&f[]=satoshi@400,500,700&display=swap" rel="stylesheet" />
<!-- Plus JetBrains Mono from Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

**Fallback if Fontshare unreachable:** Space Grotesk + Plus Jakarta Sans.

### Hayah Bento — Space Grotesk + Inter
```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

### All five at once (matches `colors_and_type.css`)
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,700;1,9..144,400&family=Outfit:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&family=Syne:wght@600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

---

## Universal Type Scale

These are the default values — Classic. Other themes override `--t-hero-*` and `--t-h1-*` per their personality.

| Token | Size | Line-height | Weight | Tracking |
|---|---|---|---|---|
| `--t-hero-*` | 72px | 1.1 | 400 | -0.03em |
| `--t-display-*` | 56px | 1.15 | 400 | -0.025em |
| `--t-h1-*` | 40px | 1.2 | 400 | -0.02em |
| `--t-h2-*` | 28px | 1.3 | 400 | -0.015em |
| `--t-h3-*` | 20px | 1.4 | 600 | — |
| `--t-h4-*` | 16px | 1.5 | 600 | — |
| `--t-body-lg-*` | 18px | 1.7 | 400 | — |
| `--t-body-*` | 16px | 1.7 | 400 | — |
| `--t-body-sm-*` | 14px | 1.6 | 400 | — |
| `--t-caption-*` | 12px | 1.5 | 400 | 0.02em |
| `--t-label-*` | 13px | 1.4 | 600 | 0.06em |
| `--t-code-*` | 14px | 1.5 | 400 | — |

---

## Per-Theme Hero Overrides

Each theme overrides the hero size and weight to match its personality. These are the **canonical values** in `colors_and_type.css`:

| Variant | Hero Size | LH | Weight | Tracking | H1 Weight |
|---|---|---|---|---|---|
| Classic | 72px | 1.1 | 400 | -0.03em | 400 |
| Coral | 76px | 1.1 | 700 | -0.03em | 400 (h2 is 700) |
| Editorial | **96px** | **0.95** | 700 | **-0.045em** | 700 |
| Bento | 80px | 1.0 | 700 | -0.04em | 700 |
| Midnight | 80px | 1.0 | 800 | -0.04em | 700 |

**Critical:** display fonts always pair with **negative letter-spacing**. Looser tracking would feel weak. Range: `-0.025em` (subtle) to `-0.045em` (Editorial, max compression).

---

## Semantic Classes

`colors_and_type.css` ships these — use them instead of styling raw tags when consistency matters.

| Class | Maps to | Use for |
|---|---|---|
| `.t-hero` / `h1.hero` | hero scale + display font + balanced text | Page hero |
| `.t-display` | display scale + display font | Section openers |
| `.t-h1` / `h1` | h1 scale + display font | Page titles |
| `.t-h2` / `h2` | h2 scale + display font | Section titles |
| `.t-h3` / `h3` | h3 scale + body font | Subsections |
| `.t-h4` / `h4` | h4 scale + body font | Tertiary headings |
| `.t-body` / `p` | body scale + body font, color `--fg-2` | Default paragraph |
| `.t-body-lg` | 18px / 1.7 | Lead paragraphs |
| `.t-body-sm` | 14px / 1.6 | Captions, secondary copy |
| `.t-caption` | 12px / 1.5 / `+0.02em` | Image captions, fine print |
| `.t-label` / `.eyebrow` | 13px / 600 / **uppercase** / `+0.06em` / teal-600 | Section labels |
| `.t-code` / `code` | 14px / mono | Inline code |

`text-wrap: balance` is applied to hero/h1/h2 by default. `text-wrap: pretty` to body. **Don't override these unless you have reason.**

---

## Eyebrow / Label Rules

Eyebrows are structural cues — not sentences.

```css
.eyebrow {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.06em;   /* range: 0.06em to 0.12em */
  text-transform: uppercase;
  color: var(--teal-600);   /* or coral in Coral theme */
}
```

**Examples:** `PRODUCT` · `WHAT'S NEW` · `FOR DEVELOPERS` · `2026 RELEASE` · `FOR TEAMS`

**Never** make an eyebrow into a sentence. **Never** put a period on it.

---

## Theme-Specific Patterns

### Editorial — typographic-first
- Hero up to 96px. Tracking `-0.045em`. Always weight 700.
- Pure white background `#ffffff` (only theme that uses white).
- Sharp `0px` corners on every component.
- 2–3px horizontal rules act as structural devices: `<hr style="border:0;border-top:2px solid #0F3836">`.
- Eyebrow tracking can stretch to `+0.12em` for masthead-style labels.

### Midnight — dark mode, geometric serif
- Display Syne at weight 800 for hero, 700 for H1.
- All text uses `--cream` (#faf7f5), never white.
- Glass cards `rgba(28,87,83,0.5)` + `backdrop-filter: blur(16px)`.
- Glow effects only on CTAs and accents (`--glow-teal`, `--glow-coral`).

### Coral — warm humanist
- Hero in Fraunces, often italic for the emotional anchor word.
- Body Outfit at slightly heavier 500 weight feels softer than 400.
- Coral leads, teal supports.

### Bento — technical-precise
- Display Space Grotesk at 700, very tight `-0.04em`.
- Metrics use Space Grotesk at 48px / weight 700 / -0.03em / line-height 1.0.
- Asymmetric grid means H1s often live inside cards, not full-width.

### Classic — the default
- DM Serif Display brings sophistication; pairs with Plus Jakarta Sans for clean body.
- Italic Display variant occasionally for emphasis ("*everything* you need").

---

## Common Recipes

### Body baseline (every theme)
```css
body {
  font-family: var(--font-body);
  font-size: 16px;
  line-height: 1.7;
  color: var(--fg-2);
  background: var(--bg-page);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
```

### Mono — JetBrains Mono everywhere
```css
code, .t-code {
  font-family: 'JetBrains Mono', ui-monospace, 'SF Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
}
```

Use mono for: code blocks, data/metric labels, inline code, API endpoints, badges in Midnight/Bento.

### Bento metric
```css
.metric {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 48px;
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.0;
  color: var(--fg-1);
}
```

### Link
```css
a {
  color: var(--teal-600);
  text-decoration: none;
  transition: color 150ms ease;
}
a:hover { color: var(--coral-500); }  /* reverse in Coral theme */
```

---

## Voice & Casing in Type

These rules are about copy, not pixels — but they live in typography because they shape how type renders.

- **Sentence case** for all UI text. `Get started` not `Get Started`.
- **No exclamation points** in marketing copy.
- **Em-dashes welcome** (`—`), short fragments fine, periods optional on display lines.
- **Numbers as numerals** in metrics: `12k+`, `2.4M`, `99.9%`.
- **Hero headlines** under ~10 words. Single-clause. No questions.
- **Labels** are always uppercase, brief, no punctuation.

See `references/color-palette.md` and the main `SKILL.md` for full content/voice rules.

---

## Accessibility

- **Min body size:** 14px (`--t-body-sm-size`). Use 12px (`--t-caption-size`) only for captions.
- **Body line-height:** 1.7 (we run generous; never below 1.6).
- **Max line length:** 720px (`--content` variable in CSS) — readability over screen-fill.
- **Hierarchy via weight + size**, not color alone. A heavier weight + larger size carries the structure.
- **Negative tracking on display** must not collapse letterforms — verify legibility at every size.
- See `references/color-palette.md` for contrast ratios.
