# Drafting Conventions Implemented by ee-drafting

These are the conventions the engine draws. `elektra-sld-audit` checks drawings
against the same list, so a drawing from this engine should pass the drafting half of
that audit by construction.

## Symbols (ANSI/IEEE one-line style, IEEE Std 315 / ANSI Y32.2)

Every symbol is a block named `E-SYM-<TYPE>` (transformers `E-SYM-TRANSFORMER-<VECTOR
GROUP>`), geometry on layer 0 with BYBLOCK colour, linetype, and lineweight, so the
insert's layer and status linetype govern it. Attributes: `TAG`, `DESC1`–`DESC6`,
`STATUS`.

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
| bus | Heavy line on layer E-ONEL-BUSS (0.70 mm) |
| panel | Rectangle with a diagonal |
| load | Downward triangle |
| ground | Three diminishing bars |

IEC 60617 symbols are not implemented. If a client mandates IEC symbology, say so
before drafting rather than mixing conventions on one sheet.

## Layers (US National CAD Standard pattern: discipline-major-minor)

| Layer | Content | ACI | Lineweight |
|---|---|---|---|
| E-ONEL-EQPM | Equipment symbol inserts | 7 | 0.35 |
| E-ONEL-DEVC | Inline protective/metering devices | 5 | 0.35 |
| E-ONEL-COND | Conductors | 7 | 0.35 |
| E-ONEL-BUSS | Buses | 7 | 0.70 |
| E-ONEL-GRND | Grounding conductors and electrodes | 3 | 0.25 |
| E-ANNO-TEXT | Labels | 7 | 0.25 |
| E-ANNO-RISR | Riser floor lines and labels | 8 | 0.18 |
| E-ANNO-LGND | Legend and general notes | 7 | 0.25 |
| E-ANNO-STMP | Draft stamp, status tags, NOT SEALED | 1 | 0.35 |
| G-ANNO-TTLB | Title strip, revision block, seal | 7 | 0.35 |
| G-ANNO-BRDR | Sheet border | 7 | 0.70 |
| G-ANNO-VPRT | Viewport frame (does not plot) | 8 | 0.18 |

ACI 7 displays white on a dark model space and plots black. Plot with
`monochrome.ctb`; lineweights come from the layers.

## Line types encode data status (defined in millimetres, LTSCALE 1)

| Status | Linetype | Pattern | Meaning |
|---|---|---|---|
| verified | CONTINUOUS | — | Field-verified against the installation |
| assumed | E-ASSUMED | 4 mm dash, 2 mm gap | Given as stated data, not observed |
| unknown | E-UNKNOWN | 0.4 mm dash, 1.2 mm gap | Not known; requires a site visit or document |

True zero-length dots are avoided: some renderers and plotters drop them. Non-verified
equipment also carries an (ASSUMED) / (UNKNOWN) STATUS attribute on E-ANNO-STMP, so
status survives a monochrome plot.

## Sheet and title strip (paper space)

- Layout named after the drawing number; ISO A3–A0 landscape or 20 x 30 in; 20 mm
  binding margin, 10 mm elsewhere; 1:1 viewport onto model space.
- Right-hand title strip, bottom to top: drawing no. and sheet; revision and scale;
  date and survey date; drawn and checked by; sheet contents / drawing title; location;
  owner; project; PEE name; PRC Reg. No. / validity; PTR No. / date / place issued;
  TIN; seal circle (NOT SEALED); draft stamp; revision block.
- Survey date absent: shown as "NONE - NOT FIELD-VERIFIED" and raised as a warning.
- Fields follow common Philippine electrical permit forms (PRC, PTR, TIN of the
  signing PEE). LGU model title blocks vary — confirm against the local Office of the
  Building Official before a permit submission.

## Text

Style `E-TEXT`, Arial (`arial.ttf`). DXF height is cap height: 2.5 mm for equipment
IDs, 1.8 mm for ratings and notes, 5.0 mm for the sheet stamp. Layout spacing and the
collision check use real Arial glyph widths. The engine never rewrites source text.
