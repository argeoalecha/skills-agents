# Drafting Conventions Implemented by ee-drafting

These are the conventions the engine draws. `elektra-sld-audit` checks drawings
against the same list, so a drawing from this engine should pass the drafting half of
that audit by construction.

## Symbols (ANSI/IEEE one-line style, IEEE Std 315 / ANSI Y32.2)

Every symbol is a block named `E-SYM-<TYPE>` (transformers `E-SYM-TRANSFORMER-<VECTOR
GROUP>`), geometry on layer 0 with BYBLOCK colour, linetype, and lineweight, so the
insert's layer and status linetype govern it. Attributes: `TAG`, `DESC1`–`DESC10`
(description lines wrapped at 20 characters), `STATUS`. Invisible attributes (flag 1)
carry the feeder tag and protection on inline devices in tagged mode.

| Type | Symbol |
|---|---|
| utility | Circle marked U |
| generator | Circle marked G |
| motor | Circle marked M |
| meter | Small circle marked kWh |
| transformer | Two overlapping circles; delta / wye glyphs and grounded-neutral mark from the vector group (e.g. Dyn11) |
| ct | Small circle on the conductor |
| breaker | Square (inline device) |
| fuse | Rectangle with a centre line |
| disconnect | Open blade between two contacts |
| ats | Rectangle marked ATS |
| bus | Heavy line on layer E-ONEL-BUSS (1.00 mm) |
| panel | Rectangle with a diagonal |
| load | Downward triangle |
| ground | Three diminishing bars |

IEC 60617 symbols are not implemented. If a client mandates IEC symbology, say so
before drafting rather than mixing conventions on one sheet.

## Layers (US National CAD Standard pattern: discipline-major-minor)

Lineweights are full-size pens. The A3 column is what each one prints on the 55.1%
reduction of a 20 x 30 in sheet. Every plotting pen stays at or above 0.13 mm.

| Layer | Content | ACI | Lineweight | On A3 |
|---|---|---|---|---|
| E-ONEL-EQPM | Equipment symbol inserts | 7 | 0.50 | 0.28 |
| E-ONEL-DEVC | Inline protective/metering devices | 5 | 0.50 | 0.28 |
| E-ONEL-COND | Conductors | 7 | 0.50 | 0.28 |
| E-ONEL-BUSS | Buses | 7 | 1.00 | 0.55 |
| E-ONEL-GRND | Grounding conductors and electrodes | 3 | 0.35 | 0.19 |
| E-ANNO-TEXT | Labels, feeder tag bubbles | 7 | 0.35 | 0.19 |
| E-ANNO-RISR | Riser floor lines and labels | 8 | 0.25 | 0.14 |
| E-ANNO-LGND | Legend, general notes, feeder schedule text | 7 | 0.35 | 0.19 |
| E-ANNO-STMP | Draft stamp, status tags, NOT SEALED, schedule STATUS cells | 1 | 0.50 | 0.28 |
| G-ANNO-TTLB | Title strip, revision block, seal, schedule grid | 7 | 0.35 | 0.19 |
| G-ANNO-BRDR | Sheet border | 7 | 1.00 | 0.55 |
| G-ANNO-VPRT | Viewport frame (does not plot) | 8 | 0.18 | — |

ACI 7 displays white on a dark model space and plots black. Plot with
`monochrome.ctb`; lineweights come from the layers.

## Line types encode data status (defined in millimetres, LTSCALE 1)

| Status | Linetype | Pattern (full size) | On A3 | Meaning |
|---|---|---|---|---|
| verified | CONTINUOUS | — | — | Field-verified against the installation |
| assumed | E-ASSUMED | 6 mm dash, 3 mm gap | 3.3 / 1.7 mm | Given as stated data, not observed |
| unknown | E-UNKNOWN | 1 mm dash, 2 mm gap | 0.55 / 1.1 mm | Not known; requires a site visit or document |

True zero-length dots are avoided: some renderers and plotters drop them. Every linetype
element prints at least 0.5 mm on the A3 reduction. Non-verified equipment also carries
an (ASSUMED) / (UNKNOWN) STATUS attribute on E-ANNO-STMP, so status survives a
monochrome plot.

## Sheet size and reduction

- Default sheet 20 x 30 in (762 x 508 mm) landscape; ISO A3–A0 on request.
- `reduce_to` defaults to A3 for 20 x 30 in and to none for ISO sheets. The smallest
  plot governs: a 20 x 30 in sheet on A3 plots at min(420/762, 297/508) = 55.1%.
- The sheet is laid out at the smallest plot size and scaled up exactly. Every height
  and margin below is the printed size on that plot. The full-size value is that
  divided by the plot scale.
- A general note records the original sheet size and the reduction it is lettered for.
- When the diagram or the feeder schedule cannot fit at legible size on the smallest
  plot, the engine raises DoesNotFit (CLI exit 5). It never shrinks text. The fix is
  to split the diagram, shorten labels, use a larger sheet, or confirm with the client
  that there will be no reduction.

## Feeder tags and schedule

- Label mode `auto` draws inline labels when they fit without collisions, otherwise
  tags. `inline` and `tagged` force a mode; a forced `inline` that cannot be legible
  raises DoesNotFit.
- Tags are `F1`, `F2`, ... in spec edge order, assigned to every edge with a device or
  a conductor label; an edge's own `tag` overrides. Each tag is a circle (2.6 mm radius
  on the smallest plot) beside the feeder's device, or at mid-run on a feeder with no
  device.
- FEEDER SCHEDULE columns: TAG, FROM, TO, PROTECTION, CONDUCTOR, STATUS. A row with no
  device or label shows `-`. STATUS is blank for verified data and ASSUMED / UNKNOWN
  (on E-ANNO-STMP) otherwise.
- Placement order: beside the diagram, below it, then on a second layout
  `<drawing no.>-FS` with its own title strip and revision block (sheet `2 OF 2`, title
  `FEEDER SCHEDULE - <drawing title>`, no legend) while the diagram sheet becomes
  `1 OF 2`.
- In tagged mode, leaf equipment labels are centred below the symbol on a one-line and
  above it on a riser, where the feeder enters from below.

## Riser and ground routing

- A breaker on a long straight vertical feeder (in practice a riser feeder spanning
  floors) is drawn 12 mm (smallest plot) off the source switchboard, where it is
  mounted, not at mid-height.
- Ground conductors bend on their own track, 3 mm off the feeder bend line.

## Sheet and title strip (paper space)

- Layout named after the drawing number; 20 mm binding margin and 10 mm elsewhere on
  the smallest plot (36 mm and 18 mm on a full-size 20 x 30 in sheet); 1:1 viewport
  onto model space.
- Right-hand title strip, bottom to top: drawing no. and sheet; revision and scale;
  date and survey date; drawn and checked by; sheet contents / drawing title; location;
  owner; project; PEE name; PRC Reg. No. / validity; PTR No. / date / place issued;
  TIN; seal circle (NOT SEALED); draft stamp; revision block.
- Survey date absent: shown as "NONE - NOT FIELD-VERIFIED" and raised as a warning.
- Fields follow common Philippine electrical permit forms (PRC, PTR, TIN of the
  signing PEE). LGU model title blocks vary — confirm against the local Office of the
  Building Official before a permit submission.

## Text

Style `E-TEXT`, Arial (`arial.ttf`). DXF height is cap height. Printed heights on the
smallest plot (A3 for the default sheet), with full size on a 20 x 30 in sheet:

| Text | On A3 | Full size 20 x 30 |
|---|---|---|
| Equipment IDs, FEEDER SCHEDULE heading | 2.5 mm | 4.5 mm |
| Ratings, descriptions, notes, schedule rows, feeder tags | 1.8 mm | 3.3 mm |
| Title-strip and schedule column captions | 1.6 mm | 2.9 mm |
| Sheet stamp | 5.0 mm | 9.1 mm |

Nothing printed is smaller than 1.6 mm on the smallest plot, and no diagram text is
smaller than 1.8 mm (ISO 3098 practice). With `reduce_to: []`, the A3 column is the
full-size height. Layout spacing, word wrap, truncation, and the collision check use real
Arial glyph widths. Invisible attributes are excluded from the collision check. The
engine never rewrites source text, except to wrap description lines at 20 characters.
