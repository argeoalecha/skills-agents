---
name: theme-sisc
description: Southville International School and Colleges (SISC) brand system — applies the client's extracted palette, typography, and logo to two output shapes. Slide decks (PowerPoint) get the full theme (palette, sharp radii, shadows, kicker/numeral/divider conventions). Standard documents (reports, design docs — Word/PDF) get a minimal treatment — logo + white background + text color only. Use for any deliverable on the Southville Electric Campus Electrical Network Integration and Smart Energy Management Project engagement. Triggers on /theme-sisc, "brand this for SISC", "Southville deck", "SISC report", "apply the SISC theme", "put the SISC logo on this".
user-invocable: true
---

# Theme-SISC — Southville International School and Colleges

The client brand for the **Southville Electric** engagement (Campus Electrical Network Integration and Smart Energy Management Project). Promoted out of `/theme-client` into its own skill on 2026-09-04 because SISC deliverables recur — reports, design docs, and slide decks — and the two output shapes need different rules, not one generic brand dump.

**Read `assets/BRAND.md` first for the full rationale** (extraction method, accessibility verification, deviations from the generic `/theme-client` flow). This file is the *application* guide — how to use the brand, not how it was derived.

---

## Skill root

All paths relative to `~/.claude/skills/theme-sisc/`:

| Path | What it is |
|---|---|
| `assets/theme.json` | Canonical token set — 11-token core `colors` block + `brandExtended`, `a11ySafeText`, `palette`, `typography`, `radii`, `shadows` |
| `assets/tokens.css` | CSS custom properties + `.sisc-*` utility classes (kicker, numeral, section-head, divider, card, cta) |
| `assets/tailwind.config.js` | Tailwind `theme.extend` block, same values as `theme.json` |
| `assets/logo.png` | **Primary logo** — real horizontal lockup (badge + wordmark), 1966×186, light backgrounds |
| `assets/logo-dark.png` | Same lockup, recolored for dark backgrounds |
| `assets/logo.svg` / `assets/logo-dark.svg` | Redrawn vector approximations — **not** the official crest, do not present as final client-facing vector art without a real `.ai`/`.eps` from SISC marketing |
| `assets/logo-original.png` | Bare crest only (no wordmark), 250×306, low-res — last resort |
| `assets/BRAND.md` | Full extraction writeup: palette rationale, WCAG contrast table, typography rationale, logo provenance, change log |

---

## Two application modes — pick one before starting

Ask yourself what the deliverable *is*. Don't apply deck styling to a memo, and don't strip a slide deck down to logo-only.

### Mode A — Slide decks (PowerPoint, via `document-skills:pptx`)

Full theme applies. Everything below is **measured from the source deck** (`Project_Plan_Details.pptx`, 24 slides) — not derived from web-theme defaults. Match it and a new deck sits beside the existing one without looking foreign.

**Stage:** 20.00 × 11.25 in (16:9). All coordinates below are inches on that stage — scale proportionally for a 13.33in stage.

#### The grid

| Rule | Value |
|---|---|
| Left margin | `x = 1.08` — every element starts here, without exception |
| Content width | `17.83` (rules, bands, card rows) → right edge `18.91`, mirroring the left margin |
| Full-width text boxes | `19.62` wide (text has its own internal inset; the optical margin still reads as 1.08) |
| Vertical rhythm | kicker `y=1.00` (h 0.33) → title `y=1.43` (h 0.80) → divider `y≈2.47` → content `y≈2.91` → footer band `y=9.53` |

#### Type scale — the deck is Arial, not Georgia

**1,272 of 1,290 runs are Arial.** Georgia appears in exactly **5 runs across slides 4–6** and nowhere else. Treat Arial as the deck face and Georgia as a rare, deliberate accent for a section's opening statement — *not* as the display font for every title.

| Role | Size | Actual treatment |
|---|---|---|
| Title-slide headline | 54pt | Arial bold |
| Slide title / display numeral | 48pt | Arial bold, letter-spacing −0.48pt, `#410BDB` (19 runs — the dominant title treatment) |
| Statement title | 42pt | Georgia bold, white, on a filled ground (slide 6 only) |
| Secondary title | 33pt | Arial, regular or bold, `#1E181B` |
| Section head / kicker | 24pt | Arial bold — `#D2650F` letterspaced +0.96pt, or `#1E181B` plain |
| Subhead | 20.25pt | Arial regular `#1E181B`, bold `#D2650F`, or regular muted |
| Body | 18pt | Arial — 502 runs, the workhorse |

**18pt is a hard floor.** The deck contains **zero** type below 18pt. Don't introduce 12pt captions or footnotes; if content doesn't fit at 18pt, cut it or add a slide.

#### Named elements

- **Kicker** — uppercase eyebrow at `y=1.00`, present on **17 of 24 slides**. Two variants, both Arial bold 18pt: muted `#7C6F75` letterspaced +2.88pt (the most common — 18 runs), and accent `#D2650F` letterspaced +1.8pt for emphasis. The muted variant is the default; orange is for slides that need to shout.
- **Numeral** — Arial bold 48pt, letter-spacing −0.48pt, display indigo `#410BDB`. Used both as oversized section numbers and as the slide-title treatment itself.
- **Divider rule** — `w=17.83`, `h=0.02` (≈1.5pt), fill `primaryLit #6A3D9E`, sitting directly under the title. Section-statement slides swap it for the lighter `#B589D6`. The title slide uses a **short** rule instead: `w=2.92`, `h=0.04` (double weight).
- **Footer band** — `x=1.08 y=9.53 w=17.83 h=0.89`, fill `tintBlush #F6D6DC`, on 8 slides. This is a *summary callout*, not a page-number footer: a short uppercase label ("DELIVERABLES") plus a `·`-separated list of items. Use it to compress a list that would otherwise need its own slide.
- **Nested-square motif** — three concentric unfilled squares in the top-right corner, on 9 slides: `2.43` at `(16.90, 0.58)`, `1.70` at `(17.27, 0.95)`, `0.97` at `(17.63, 1.31)` — concentric, 0.37 inset per step. The deck's only decorative flourish.
- **Cards** — 3-up row, each `5.69 × 3.53`, gutter `0.38`, starting at `x = 1.08 / 7.15 / 13.22`, `y = 2.91`. Fill is `background #FFF8F9` (**not** the `card` token), with a `0.05`-tall accent bar across the top in a **different color per card** — the deck uses `#AE1029`, `#D2650F`, `#6A3D9E` left to right. **No border, no shadow.** Card title is an uppercase 18pt label, body below at 18pt.
- **Agenda layout** — two columns at `x=1.83` and `x=11.27`, each row preceded by a numeral box (`0.54 × 0.37`) at `x=1.08` / `x=10.52`, row pitch `0.92`.

#### Hard constraints

- **No shadows.** The deck has **zero** shadow or effect declarations — it is deliberately flat. The `shadows` block in `theme.json` is for *web* output only; never apply it to a slide. Depth comes from fill contrast and the colored top bars, not blur.
- **Sharp corners only.** 506 `rect` + 27 `ellipse`, **zero** `roundRect`. Don't introduce rounded corners.
- **Strokes, not shadows** — 532 line declarations. Use hairline rules and bars to separate content.
- **Logo appears on the title slide only** (`1.44 × 1.75` at `x=1.08, y=1.00`). Interior slides carry the kicker instead of a repeated logo — don't stamp the crest on every slide. Never stretch or recolor beyond the two sanctioned variants.
- **Extended brand colors** (`brandExtended` in `theme.json`) carry status and chart series: laurel `#3C875A` (on-track), maroon `#8D2725` (heritage), alert `#AE1029` (critical findings), `#410BDB` (display numerals), violet/blush tints for fills.

#### Slide archetypes

Compose new decks from these six, in this order of preference:

1. **Title** — logo top-left, client name in a `#FCEEF3` band, 54pt headline at `y=4.63`, short double-weight rule, subtitle, preparer credit at `y=9.57`.
2. **Agenda** — two numbered columns (see above).
3. **Content** — kicker + title + divider + two-column body at `x=1.08 / 10.37`, each column `9.40` wide. The workhorse; most slides are this.
4. **Statement** — kicker + oversized Georgia headline + lighter `#B589D6` rule + two asymmetric columns. Use sparingly, for a section's thesis.
5. **Three cards** — the colored-top-bar row above.
6. **Dense table** — the deck goes up to 127 shapes on one slide for a schedule matrix. Acceptable at 18pt; use hairline `#E2C3CA` rules between rows.

### Mode B — Standard documents (reports, design docs — Word/PDF, via `document-skills:docx` or `document-skills:pdf`)

Minimal treatment. Do not import the full palette, shadow system, or deck-style kickers/numerals into a report — it reads as slide-deck styling pasted into a document and undermines the "serious" institutional mood the brand is built on.

Apply only:
- **Logo:** `logo.png` in the header (or first-page letterhead position), modest size — this is the one non-negotiable brand touch on every document.
- **Background:** white (`#FFFFFF`, the `surface` token) — not the deck's blush `background` tint. Documents are read on-screen and printed; the tint doesn't survive print and isn't a document convention in the source material.
- **Text:** body copy in `text #1E181B` on white. Headings may use `primary #4B2F70` for H1/H2 only, never for body text or long passages (contrast is fine — 10.33:1 on background — but institutional reports read the color as a section marker, not a copy color).
- **Typography:** Arial (or its metric-compatible fallback, Arimo) throughout — headings and body. This mirrors the deck, which is 99% Arial. Georgia (Gelasio) is permitted for the **document title only**, matching the deck's use of it as a rare statement face; don't set every heading in it.
- **Optional restraint:** a single 2–3px `primaryLit #6A3D9E` rule under the document title is acceptable (it's the deck's own divider convention, and reads as intentional rather than decorative) — but that's the ceiling. No cards, no shadows, no accent-orange kickers, no oversized numerals in a report.
- **Footer:** page number + document title in `muted #7C6F75` (small text — use the AA-safe `mutedText #71656B` since footers are small type on white).

If in doubt, err toward *less* branding in documents. The client-facing signal that matters in a report is legibility and the crest, not palette fidelity.

---

## Accessibility — read before using accent or muted on small text

Three tokens fail 4.5:1 (WCAG AA small-text) against this palette's backgrounds and must not be used for small body copy — see `assets/BRAND.md` for the full contrast table:

| Display value | Use instead for small/body text |
|---|---|
| Accent `#D2650F` | `#AB520C` (`accentText` / `.sisc-kicker` already uses the safe swap where needed — for body-size CTAs or links use `#AB520C`) |
| Muted `#7C6F75` | `#71656B` |
| Laurel `#3C875A` | `#357850` |

Accent orange is safe at 18pt bold and above (3:1 threshold for large text) — that's exactly how the source deck uses it (kickers, never small copy). Never set small white text on the accent fill (3.74:1, fails small-text AA).

---

## Workflow

1. **Identify the deliverable type** (deck vs. document) — ask the user if it's ambiguous from the request.
2. **Load the relevant skill for the file format**: `document-skills:pptx` for decks, `document-skills:docx` for Word reports, `document-skills:pdf` if the deliverable is PDF-native.
3. **Pull tokens from `assets/theme.json`** (or the CSS/Tailwind equivalents if the deliverable is web-rendered before export, e.g. an HTML-to-PDF report).
4. **Apply Mode A or Mode B rules above** — resist copying deck styling into documents or vice versa.
5. **Place the logo** per the placement rules for that mode.
6. **Check accessibility** for any small text using accent, muted, or laurel colors — swap to the AA-safe values above.
7. **Sharp corners everywhere** — this is a brand-wide constraint, not deck-only (the source material never uses rounded corners, and 0/2/4px radii read as "institutional" not "accidentally unstyled").

---

## Quality gates before declaring done

- [ ] Correct mode applied (full theme for decks, logo + white + text-color-only for documents) — no cross-contamination
- [ ] Logo placed per size/clear-space rules, using `logo.png` (or `logo-dark.png` only on a dark ground)
- [ ] No small text set in accent `#D2650F`, muted `#7C6F75`, or laurel `#3C875A` — AA-safe swaps used instead
- [ ] No rounded corners beyond `radii.md` (2px) — check any generated shapes/cards
- [ ] Arial/Arimo throughout; Georgia/Gelasio only as a statement face (deck: section-opening titles; docs: document title) — no substitute typefaces introduced
- [ ] Decks: nothing below 18pt, and **no shadows** — the source deck has zero
- [ ] Decks: left margin `x=1.08`, content width `17.83`, divider under every titled slide
- [ ] Documents: no deck-style kickers, numerals, shadows, footer bands, or blush background tint leaked in

---

## Source material

`assets/BRAND.md` documents the palette/logo extraction from `Project_Plan_Details.pptx` (24 slides, 16:9, PptxGenJS-authored, "Campus Electrical Network Integration and Smart Energy Management Project", prepared by Argeo T. Alecha).

The **layout system in Mode A above was measured on 2026-09-04** from the current revision at `/Volumes/1TB_SSD/projects-mvp-ext/southville-electric-docs/Plans and Deliverables/Project_Plan_Details.pptx` (created 2026-09-03) — shape geometry census, per-run typeface/size/color/letter-spacing census, and per-slide coordinate analysis. Figures cited (506 rect, 27 ellipse, 0 roundRect, 1,272 Arial runs vs 5 Georgia runs, 502 runs at 18pt, 0 shadow declarations, 532 line declarations) are from that pass and supersede the approximate counts in the original extraction.

The deck remains the reference for anything not captured here — chart styling and the dense schedule matrices in particular. Re-measure rather than guess if a new pattern is needed.

`ppt/theme/theme1.xml` inside the pptx is stock PptxGenJS boilerplate (Calibri, `#4472C4`) and carries no client signal — ignore it if re-inspecting the source file.

---

## Relationship with sibling skills

| Skill | Role |
|---|---|
| `/theme-client` | Generic per-client brand intake for *other* clients. SISC's assets were extracted there originally, then promoted here — `/theme-client` no longer holds SISC-specific files. |
| `document-skills:pptx` | Executes the actual slide-deck creation/editing; this skill supplies the tokens and placement rules it should follow. |
| `document-skills:docx` / `document-skills:pdf` | Executes report/design-doc creation; this skill supplies Mode B rules. |
| `/company-site`, `/ui-builder`, `/auth-page-scaffold` | Only relevant if SISC ever needs a web deliverable (e.g. a digital-twin dashboard for the electrical project) — copy `assets/` into `<project-root>/brand/` per the instructions in `assets/BRAND.md` if that comes up. Out of scope for this skill's primary use (documents + decks). |

---

## Out of scope

- **Voice / copy rules** — SISC is an academic institution; no tone-of-voice rules generated. Request their style guide if copy needs review.
- **Re-deriving the palette or logo** — done once, documented in `assets/BRAND.md`. Don't re-extract from the pptx unless the client supplies a materially different brand asset (e.g. an official vector crest) — if that happens, update `assets/BRAND.md`'s change log and the affected asset files, don't silently overwrite.
- **Web/product UI theming** — this skill is scoped to documents and decks; see the sibling-skills table above for the web path if it's ever needed.
