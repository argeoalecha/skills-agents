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

Full theme applies. This is what the source deck (`Project_Plan_Details.pptx`) itself demonstrates — treat it as the living style reference, not just a token source.

- **Palette:** primary `#4B2F70` for headlines/shield fills, `primaryLit #6A3D9E` for divider rules and hover, accent `#D2650F` for CTAs and uppercase kickers **only** (never small body text — see accessibility below). Background `#FFF8F9`, cards `#FDEEF0`, borders `#E2C3CA`.
- **Typography (deck pt scale, 20in-wide 16:9 stage):**
  | Role | Size | Treatment |
  |---|---|---|
  | Hero title | 54pt | Georgia bold |
  | Display numeral | 48pt | Arial bold, letter-spacing −0.48pt, `#410BDB` |
  | Slide title | 33pt | Georgia bold |
  | Section head | 24pt | Georgia bold, `#1E181B` |
  | Subhead | 20.25pt | Arial |
  | Body | 18pt | Arial (the deck's workhorse size — 504 runs) |
- **Named conventions** (see `.sisc-kicker`, `.sisc-numeral`, `.sisc-divider` in `tokens.css` for the CSS-side equivalents, translate to pptx shape/text props):
  - **Kicker** — Arial bold 18pt, letterspaced +1.8pt, uppercase, accent orange `#D2650F`
  - **Numeral** — Arial bold 48pt, tight tracking, display indigo `#410BDB`, used for oversized section numbers ("01", "02")
  - **Divider** — 2–3px solid bar in `primaryLit #6A3D9E` under titles
- **Shapes:** sharp corners only. The source deck is 509 `rect` + 27 `ellipse`, **zero** `roundRect` — don't introduce rounded corners. Use `radii` from `theme.json` (`xs`/`sm` = 0px, `md` = 2px max) if a border-radius value is unavoidable.
- **Shadows:** tint to primary violet for panels/cards, tint to accent for CTA emphasis. Values in `theme.json` → `shadows`.
- **Logo placement:** `logo.png` top-left or centered on title/section slides, minimum 24px tall equivalent, clear space equal to the wordmark's x-height. Never stretch or recolor beyond the two sanctioned variants.
- **Extended brand colors** (`brandExtended` in `theme.json`) are available for chart series, status states, and fills: laurel green `#3C875A` (success/on-track), maroon `#8D2725` (heritage/heading accent), alert red `#AE1029` (critical findings), violet/blush tints for chart fills.

### Mode B — Standard documents (reports, design docs — Word/PDF, via `document-skills:docx` or `document-skills:pdf`)

Minimal treatment. Do not import the full palette, shadow system, or deck-style kickers/numerals into a report — it reads as slide-deck styling pasted into a document and undermines the "serious" institutional mood the brand is built on.

Apply only:
- **Logo:** `logo.png` in the header (or first-page letterhead position), modest size — this is the one non-negotiable brand touch on every document.
- **Background:** white (`#FFFFFF`, the `surface` token) — not the deck's blush `background` tint. Documents are read on-screen and printed; the tint doesn't survive print and isn't a document convention in the source material.
- **Text:** body copy in `text #1E181B` on white. Headings may use `primary #4B2F70` for H1/H2 only, never for body text or long passages (contrast is fine — 10.33:1 on background — but institutional reports read the color as a section marker, not a copy color).
- **Typography:** Georgia (or its Google-Fonts metric-compatible fallback, Gelasio) for headings, Arial (or Arimo) for body — same pairing as the deck, since it's the client's actual system-font choice, not a deck-only affectation.
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
- [ ] Georgia/Gelasio for headings, Arial/Arimo for body — no substitute typefaces introduced
- [ ] Documents: no deck-style kickers, numerals, shadows, or blush background tint leaked in

---

## Source material

`assets/BRAND.md` documents extraction from `Project_Plan_Details.pptx` (24 slides, 16:9, PptxGenJS-authored, "Campus Electrical Network Integration and Smart Energy Management Project", prepared by Argeo T. Alecha). The extraction was re-confirmed on 2026-09-04 against a later revision of the same deck at `/Volumes/1TB_SSD/projects-mvp-ext/southville-electric-docs/Plans and Deliverables/Project_Plan_Details.pptx` (created 2026-09-03) — same slide count, authorship, and font census, so no token changes were needed. Treat that file as the canonical design-philosophy reference for deck layout patterns (title/section slide structure, kicker/numeral/divider placement, chart color usage) beyond what the tokens alone capture.

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
