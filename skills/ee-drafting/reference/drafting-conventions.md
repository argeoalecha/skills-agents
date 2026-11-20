# Drafting Conventions Implemented by ee-drafting

These are the conventions the engine draws. `elektra-sld-audit` checks drawings
against the same list, so a drawing from this engine should pass the drafting half of
that audit by construction.

## Symbols (ANSI/IEEE one-line style, IEEE Std 315 / ANSI Y32.2)

| Type | Symbol |
|---|---|
| utility | Circle marked U |
| generator | Circle marked G |
| motor | Circle marked M |
| meter | Small circle marked kWh |
| transformer | Two overlapping circles (two-winding) |
| ct | Small circle on the conductor |
| breaker | Square (inline device) |
| fuse | Rectangle with a centre line |
| disconnect | Open blade between two contacts |
| ats | Rectangle marked ATS |
| bus | Double heavy horizontal bar |
| panel | Rectangle with a diagonal |
| load | Downward triangle |
| ground | Three diminishing bars |

IEC 60617 symbols are not implemented. If a client mandates IEC symbology, say so
before drafting rather than mixing conventions on one sheet.

## Layers (US National CAD Standard pattern: discipline-major-minor)

| Layer | Content | Colour (ACI) |
|---|---|---|
| E-ONEL-EQPM | Equipment symbols, bus bars | 7 |
| E-ONEL-DEVC | Inline protective/metering devices | 5 |
| E-ONEL-COND | Conductors | 7 |
| E-ONEL-GRND | Grounding conductors and electrodes | 3 |
| E-ANNO-TEXT | Equipment IDs and ratings | 7 |
| E-ANNO-RISR | Riser floor lines and labels | 8 |
| E-ANNO-LGND | Legend and general notes | 7 |
| E-ANNO-STMP | Draft stamp, status tags, NOT SEALED | 1 |
| G-ANNO-TTLB | Title, revision and seal blocks | 7 |
| G-ANNO-BRDR | Sheet border | 7 |

## Line types encode data status

| Status | Linetype | Meaning |
|---|---|---|
| verified | CONTINUOUS | Field-verified against the installation |
| assumed | DASHED | Given as stated data, not observed |
| unknown | DOT | Not known; requires a site visit or document |

Non-verified equipment also carries a red (ASSUMED) or (UNKNOWN) tag under its label,
so status survives a monochrome plot where linetypes may be hard to tell apart.

## Sheet and title block

- ISO A-series landscape (A3 420x297 to A0 1189x841 mm), 20 mm binding margin, 10 mm
  elsewhere.
- Title block fields: project, client, drawing title, drawing no., revision, sheet,
  date, survey date, scale (NTS for one-lines), drawn by, checked/sealed by (PEE).
- Survey date absent: shown as "NONE - NOT FIELD-VERIFIED" and raised as a warning.
- Revision block above the title block, newest revision on top.
- PEE seal box (RA 7920), drawn empty and marked NOT SEALED.
- Draft stamp at the top of the sheet and in the title block.

## Text

DXF text heights: 2.5 mm for IDs, 1.8 mm for ratings and notes, 5.0 mm for the sheet
stamp. Text is upper case where the source data is upper case; the engine never
rewrites source text.
