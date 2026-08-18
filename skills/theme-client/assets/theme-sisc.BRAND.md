# Southville International School and Colleges — Brand System

Generated: 2026-08-19
Slug: `sisc` · Theme name: `theme-sisc`
Mood: serious · Industry: education (private international school and college)

Derived by **extraction**, not intake. Source of truth is the client deck:
`/Volumes/1TB_SSD/projects-mvp-ext/southville-electric/post-mtg-08072026/Project_Plan_Details.pptx`
(24 slides, 16:9, PptxGenJS-authored, dated 2026-08-10 — "Campus Electrical Network Integration and Smart Energy Management Project", prepared by Argeo T. Alecha).

---

## Extraction method

The deck carries **two independent color sources**, and they are not the same thing:

1. **The crest** (`ppt/media/image-1-1.png`) — the client's actual institutional identity. Quantised in HSL, chromatic pixels isolated (saturation > 30%, lightness 12–75%) so the near-white field didn't dominate.
2. **The slide palette** — `srgbClr` values ranked by frequency across all 24 slides, then each mapped to its role by reading the surrounding `rPr`/`spPr` context (font size, weight, letter-spacing, shape fill).

`ppt/theme/theme1.xml` was **discarded**. It is stock Microsoft Office boilerplate emitted by PptxGenJS (`accent1 #4472C4`, Calibri / Calibri Light) and carries no client signal. Anything claiming Calibri or `#4472C4` for SISC is reading the wrong file.

---

## Palette

| Token | Hex | Usage |
|---|---|---|
| Primary | `#4B2F70` | Crest violet — headlines, key accents, shield field |
| Primary Light | `#6A3D9E` | Divider rules, hover states |
| Primary Dark | `#301D49` | Pressed states, deep emphasis |
| Accent | `#D2650F` | CTAs and uppercase kickers only |
| Background | `#FFF8F9` | Page background |
| Surface | `#FFFFFF` | Section backgrounds, raised areas |
| Card | `#FDEEF0` | Card / panel backgrounds |
| Border | `#E2C3CA` | 1px dividers and outlines |
| Text | `#1E181B` | Primary copy |
| Muted | `#7C6F75` | Secondary copy, captions |
| Subtle | `#958389` | Placeholders, disabled state |

**Primary scale:**

| 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 |
|---|---|---|---|---|---|---|---|---|
| `#F5F3F6` | `#E4DEED` | `#B49ED1` | `#7449AB` | `#4B2F70` | `#3C255B` | `#301D49` | `#221433` | `#160D21` |

**Extended brand colors** (present in the source, outside the 11-token core):

| Hex | Origin | Usage |
|---|---|---|
| `#3C875A` | Crest laurel wreath | Success, growth, "on track" states |
| `#60B158` | Crest figures / globe | Lighter green accent |
| `#8D2725` | Crest heart quarter | Heritage maroon |
| `#410BDB` | Deck, 48pt bold numerals | Oversized section numbers only |
| `#AE1029` | Deck | Alerts, critical findings |
| `#D9B9EE` `#C79FE4` `#F6D6DC` | Deck | Fills, chart series, tints |

### Rationale

Primary `#4B2F70` is the crest's shield field — 8.07% of all opaque pixels, the single largest chromatic mass, and stable across the whole shield (every sampled violet lands within hue 265.8–266.7°). That makes it the defensible brand anchor rather than anything chosen from the slides.

The 9-step scale **deviates from the skill's default rule**, deliberately. The documented rule ("darken by 25% lightness" for 700, "lighten to 20%" for 800) assumes a mid-lightness primary around L=50%. SISC violet sits at **L=31.2%**, so applying the rule literally produces `700` darker than `800` and `900` — a non-monotonic ramp. The scale here interpolates lightness monotonically (96 → 9%) while pinning `500` to the exact source hex and easing saturation from 15% up to 45% across the ramp.

Accent `#D2650F` was **not generated** — it is the deck's own kicker color, already in front of this client on 19 of 24 slides. It also satisfies the skill's collision rule independently: hue 26.5° sits 239° from the primary, far outside the ±15° exclusion band. The complement-rotation fallback was therefore never needed.

Background `#FFF8F9` and card `#FDEEF0` are the deck's warm blush tints, kept as-is. A neutral white would have been the generated default, but the extracted values are what the client has actually seen.

---

## Accessibility

Contrast measured against background `#FFF8F9`, surface `#FFFFFF`, and card `#FDEEF0`.

| Token | on bg | on surface | on card | Verdict |
|---|---|---|---|---|
| Text `#1E181B` | 16.68 | 17.48 | 15.53 | AA / AAA |
| Primary `#4B2F70` | 10.33 | 10.83 | 9.62 | AA / AAA |
| Display indigo `#410BDB` | 8.73 | 9.15 | 8.13 | AA / AAA |
| Primary Light `#6A3D9E` | 7.23 | 7.57 | 6.73 | AA / AAA |
| Alert `#AE1029` | 6.90 | 7.23 | 6.42 | AA / AAA |
| Muted `#7C6F75` | 4.57 | 4.79 | **4.25** | AA on bg/surface, **fails on card** |
| Laurel `#3C875A` | 4.17 | 4.37 | 3.88 | **Large text only** |
| Accent `#D2650F` | 3.57 | 3.74 | 3.33 | **Large text only** |

Three tokens do not clear 4.5:1 for small text. That is not a defect in the source — the deck uses accent orange exclusively at 18pt bold (large text, 3:1 threshold, passes) and never sets small body copy in it. For web use, where that discipline is easy to lose, AA-safe substitutes are provided:

| Display value | Small-text substitute | on bg / card |
|---|---|---|
| Accent `#D2650F` | `#AB520C` | 5.08 / 4.73 |
| Muted `#7C6F75` | `#71656B` | 5.31 / 4.94 |
| Laurel `#3C875A` | `#357850` | 5.07 / 4.72 |

**White on solid fills:** primary 10.83 ✓ · primaryLit 7.57 ✓ · indigo 9.15 ✓ · alert 7.23 ✓ · laurel 4.37 (large only) · **accent 3.74 (large/bold only — never small white text on the orange)**.

---

## Typography

| Role | Font | Source |
|---|---|---|
| Display | **Georgia** | Extracted — used for section heads on slides 4–6 |
| Body | **Arial** | Extracted — 1,290 runs, the dominant typeface |
| Mono | **Courier New** | Extracted — 3 runs |

Both are system fonts, not webfonts. The metric-compatible Google-hosted equivalents have identical advance widths, so substitution does not reflow layout:

| System font | Google Fonts equivalent |
|---|---|
| Georgia | **Gelasio** |
| Arial | **Arimo** |
| Courier New | **Cousine** |

```
https://fonts.googleapis.com/css2?family=Arimo:ital,wght@0,400..700;1,400..700&family=Gelasio:ital,wght@0,400..700;1,400..700&family=Cousine:ital,wght@0,400;0,700;1,400;1,700&display=swap
```

Load the stacks as `Georgia, Gelasio, serif` and `Arial, Arimo, sans-serif` — system font first, so most visitors render with zero webfont download. Worth keeping for the PH-mobile audience.

**Deck type scale (pt, on a 20in-wide 16:9 stage):**

| Role | Size | Treatment |
|---|---|---|
| Hero title | 54 | Georgia bold |
| Display numeral | 48 | Arial bold, letter-spacing −0.48pt, `#410BDB` |
| Slide title | 33 | Georgia bold |
| Section head | 24 | Georgia bold, `#1E181B` |
| Subhead | 20.25 | Arial |
| Body | 18 | Arial (504 runs — the workhorse size) |

**Rationale.** The Georgia/Arial split is a serif-display + grotesque-body pairing, which maps to the skill's **serious** mood row rather than *refined* or *technical*. That fits: an institutional education client receiving an engineering proposal. The pairing was not chosen from the mood table — it was read off the deck and the mood inferred backwards from it.

**Named conventions** (carried into `theme-sisc.tokens.css` as `.sisc-*` classes):

- **Kicker** — Arial bold 18pt, letterspaced +1.8pt, uppercase, accent orange
- **Numeral** — Arial bold 48pt, tight tracking, display indigo
- **Divider** — 3px solid bar in `#6A3D9E` under titles

---

## Corner Radii (sharp)

| Token | Value | Usage |
|---|---|---|
| `--r-xs` | `0px` | Tags, chips |
| `--r-sm` | `0px` | Inputs, small buttons |
| `--r-md` | `2px` | Cards, panels |
| `--r-lg` | `4px` | Hero cards, large surfaces |
| `--r-xl` | `8px` | Feature blocks |
| `--r-full` | `9999px` | Pills, avatars |

**Rationale.** Not a default — measured. The deck's geometry census is 509 `rect` and 27 `ellipse`, with **zero** `roundRect`. The visual language is genuinely square.

---

## Shadows

```css
--shadow-xs:  0 1px 2px rgba(75, 47, 112, 0.05);
--shadow-sm:  0 2px 8px rgba(75, 47, 112, 0.06);
--shadow-md:  0 4px 16px rgba(75, 47, 112, 0.08);
--shadow-lg:  0 8px 32px rgba(75, 47, 112, 0.10);
--shadow-cta: 0 4px 20px rgba(210, 101, 15, 0.40);
```

Tinted to crest violet; CTA shadow tinted to accent orange. No black shadows.

---

## Logo

| File | Use |
|---|---|
| `theme-sisc-logo.png` | **Primary — the real horizontal lockup** (badge + single-line wordmark), light backgrounds |
| `theme-sisc-logo-dark.png` | Same real lockup, programmatically recolored for dark backgrounds |
| `theme-sisc-logo.svg` | Redrawn vector approximation of the real lockup, light backgrounds |
| `theme-sisc-logo-dark.svg` | Redrawn vector approximation, dark backgrounds |
| `theme-sisc-logo-original.png` | The bare crest (no wordmark), extracted at 250×306 from the deck |

**Source of the primary asset.** `theme-sisc-logo.png` was supplied directly by the user on 2026-08-19 as a screenshot of the client's actual horizontal lockup — a badge-with-name-banner plus a separate single-line serif wordmark on a blush ground. This is a materially better source than the pptx-embedded crest alone (`theme-sisc-logo-original.png`), which carries the badge but not the wordmark pairing, at lower resolution. **This screenshot is now the authoritative logo reference**, superseding the initial extraction pass's generated stacked-wordmark SVG.

**Dark variant is a recolor, not a client asset.** `theme-sisc-logo-dark.png` was produced by HSL-masking the real PNG: pixels in the flat blush background cluster (hue ≈355°, sat >35%, lightness >90%) were blended toward `primary-800 #221433`; pixels in the wordmark's violet cluster (hue 250–280°, sat >22%, lightness 38–58%) were blended toward `primary-300 #B49ED1`. The lightness window on the text rule was deliberately cut at 38% precisely to exclude the badge's own name-banner and star-canton violet, which sit at l≈31% — an early pass with a wider window (30–58%) accidentally recolored the badge itself, caught by visual diff before shipping. The badge's pixels are otherwise **untouched**; it keeps its own white card, which is why it reads fine floated on a dark ground without a full internal recolor.

**Vectorisation status.** The two SVGs are hand-redrawn to match the real lockup's *layout* (badge left, single-line wordmark right, motto relocated inside the badge at the diamond seam where it actually sits) but are still an approximation — simplified star/laurel geometry, not a trace. They are **not** the official crest and must not be presented to the client as their logo. Request the vector original (`.ai`/`.eps`/`.svg`) from SISC marketing before any client-facing deliverable ships; when it arrives, replace both SVGs and keep the PNGs as the fallback raster.

**Crest description.** Heraldic shield: violet field, purple name-banner across the top in white type, white inner field, quartered diamond at centre (violet star canton — 5 stars, maroon heart canton, green globe-with-walking-figures base), tiny motto text across the diamond seam, green laurel wreath, founding year at the base.

- Motto: **FACITE DIFFERENTIAM** ("make a difference") — confirmed legible in the 4×-upscaled crest crop; small enough to be easy to miss at native resolution.
- Founded: **1990**
- Correction from the first extraction pass: the diamond's star quarter was described as reading "blue at a glance." Re-sampled at 4× and again from this new screenshot — it is the **same violet `#4B2F70`** as the shield and banner in both sources, confirmed by exact hex match. There is no blue in this logo; that was a perceptual read of a small, anti-aliased thumbnail, not a pixel fact.

**Usage rules:** minimum 24px tall in nav, 48px in hero. Clear space equal to the wordmark's x-height on all sides. Never stretch, recolor, or apply effects — the one sanctioned exception is the documented dark-mode recolor above, which exists because no client-supplied dark variant exists yet.

---

## Voice & Copy

Out of scope — no voice rules generated. SISC is an academic institution; if copy is needed, request their style guide rather than inventing one.

---

## How this brand is consumed

These assets live in the **skill's** `assets/` folder rather than a project `brand/` folder, at the user's instruction. Downstream skills expect `<project-root>/brand/`, so to use this on a real build, copy and rename:

```bash
mkdir -p <project-root>/brand
cd ~/.claude/skills/theme-client/assets
cp theme-sisc.json              <project-root>/brand/theme.json
cp theme-sisc.tokens.css        <project-root>/brand/tokens.css
cp theme-sisc.tailwind.js       <project-root>/brand/tailwind.config.js
cp theme-sisc-logo.png          <project-root>/brand/logo.png
cp theme-sisc-logo-dark.png     <project-root>/brand/logo-dark.png
cp theme-sisc-logo.svg          <project-root>/brand/logo.svg
cp theme-sisc-logo-dark.svg     <project-root>/brand/logo-dark.svg
cp theme-sisc-logo-original.png <project-root>/brand/logo-original.png
cp theme-sisc.BRAND.md          <project-root>/brand/BRAND.md
```

| Skill | What it reads |
|---|---|
| `/company-site` | `brand/theme.json` → `SITE_CONFIG.theme`; `brand/logo.svg` in nav + footer |
| `/ui-builder` | All of `brand/` |
| `/auth-page-scaffold` | `brand/theme.json` + `brand/logo.svg` |
| Direct Tailwind | `brand/tailwind.config.js` |
| Direct CSS | `brand/tokens.css` |

`theme-sisc.json` keeps the canonical 11-token `colors` block, so it is drop-in compatible with the `hayah-*.json` shape. The `brandExtended`, `a11ySafeText`, `palette`, and `source` blocks are additive and ignored by consumers that don't know about them.

---

## Deviations from the skill's default flow

| Default | What happened here | Why |
|---|---|---|
| Phase 0 interactive intake | Skipped — every field extracted from the deck | User supplied a source file instead of answers |
| Output to `<project-root>/brand/` | Written to `skills/theme-client/assets/` as `theme-sisc*` | Explicit user instruction |
| Palette scale by fixed ±% lightness | Monotonic interpolation, `500` pinned to source | Default rule inverts on a primary at L=31% |
| Accent generated by hue rotation | Taken from the deck's existing kicker orange | Real usage beats derivation; collision rule passes anyway |
| Fonts chosen from mood table | Read from the deck (Georgia/Arial), mood inferred backwards | Extraction, not generation |
| Google Fonts for display + body | System fonts primary, metric-compatible Google equivalents as fallback | Source fonts are system fonts; keeps webfont cost at zero |

---

## Change log

| Date | Change | By |
|---|---|---|
| 2026-08-19 | Initial extraction from `Project_Plan_Details.pptx` | /theme-client |
| 2026-08-19 | User supplied the real horizontal lockup (screenshot). Promoted it to primary logo asset (`theme-sisc-logo.png`), generated a dark recolor via HSL masking, redrew both SVGs to match the real single-line layout, fixed a "blue star canton" description error (confirmed violet), and corrected the badge description (globe-with-figures base, banner name text) | /theme-client |
