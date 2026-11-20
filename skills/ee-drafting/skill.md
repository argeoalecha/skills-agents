---
name: ee-drafting
description: >-
  Electrical drafting engine — renders single-line (one-line) and floor-banded riser
  diagrams from structured topology data to CAD-issue DWG/DXF (blocks with attributes,
  paper-space layout with a 1:1 viewport, E-ONEL-* layers with lineweights, mm
  linetypes, Arial text style) and SVG. Sheet carries a Philippine permit title strip
  (owner, location, PEE name, PRC Reg. No., PTR No., TIN), an empty RA 7920 seal,
  revision block, legend, and a DRAFT FOR PEE REVIEW stamp. Line type encodes data
  status (solid verified, dashed assumed, short-dash unknown). Draws only what the
  topology says — never sizes, rates, or infers equipment. Accepts as-built-agent's
  topology.json directly. Use when a one-line diagram, SLD, riser diagram, or electrical
  DWG/DXF needs to be produced or regenerated. Triggers on /ee-drafting, "draw the
  single-line diagram", "draft the SLD", "one-line drawing", "riser diagram",
  "electrical drawing", "DWG of the one-line", "CAD drawing", "regenerate the as-built
  drawing".
---

# Electrical Drafting — One-Line and Riser Diagrams

Deterministic drafting procedure. Never hand-place drawing coordinates or describe a
drawing in prose as a substitute — build the drawing spec, run
`scripts/render_sld.py`, and deliver the files it writes. The same spec always produces
the same geometry (the CLI prints a geometry digest; record it with the revision so a
re-render can be proven identical).

## Jurisdiction

| Skill / agent | Owns |
|---|---|
| `as-built-agent` | What exists in the field: topology, IDs, ratings, verification status — written to topology JSON |
| `/ee-load-calc`, `/ee-short-circuit` | Every number on a replacement drawing (breaker, conductor, AIC) |
| **`/ee-drafting` (this skill)** | Turning that data into a CAD drawing. Copies values verbatim; computes nothing |
| `elektra-sld-audit` | Auditing a finished drawing for code and drafting-convention gaps |
| `/ee-audit` | Cross-checking the drawing against calcs, specs, and the dashboard mimic |
| `/diagram-toolkit` | Non-electrical diagrams (flowcharts, org charts, CPM). Not one-lines |

A rating missing from the input goes on the drawing as UNKNOWN. Never fill it from a
typical value — a plausible rating on a sealed drawing is read as fact by everyone
downstream.

## Procedure

1. **Get the data, not a description.** Use `as-built-agent`'s topology JSON
   (`--from-topology`) or build a drawing spec (schema below). Replacement-design
   ratings come from `/ee-load-calc` / `/ee-short-circuit` output, copied verbatim.
2. **Confirm the deliverable format and sheet.** DWG for issue (needs the ODA File
   Converter — see "DWG"), DXF always, SVG as a review copy. Sheet is auto-picked
   (A3 → A0) at 1:1; pass `"sheet"` (`A3`–`A0`, `20X30IN`) when the LGU or client
   mandates a size. Confirm the local Office of the Building Official's model title
   block if the drawing goes to a permit — LGUs differ.
3. **Render:**
   ```bash
   python3 ~/.claude/skills/ee-drafting/scripts/render_sld.py spec.json \
       --out deliverables/drawings/E-001 --format dwg,dxf,svg
   python3 ~/.claude/skills/ee-drafting/scripts/render_sld.py topology.json --from-topology \
       --title-block tb.json --out deliverables/drawings/E-AB-001
   ```
   `--layout riser` for a riser (every node needs a `floor`).
   Exit codes: 2 invalid spec, 3 DWG requested without the converter, 4 label
   collision. Nothing partial is written on a non-zero exit.
4. **Fix collisions in the spec, not the engine.** Exit 4 lists every label that hits
   another label or a conductor. Shorten the colliding `lines`/labels, move detail to
   general notes, or choose a larger sheet. `--allow-overlaps` exists for inspection
   only — never issue a drawing rendered with it.
5. **Review it in a CAD renderer, not only the SVG.** The SVG cannot show CAD-only
   failures (linetype scale, text style, lineweights, layout). Open the DWG/DXF in
   AutoCAD/BricsCAD/DraftSight, or on macOS render the layout headless with QCAD:
   ```bash
   /Applications/QCAD.app/Contents/Resources/dwg2bmp -f -a -n -b white \
       -block=E-001 -x 2400 -y 1700 -o review.png E-001.dxf
   ```
   (QCAD's command-line tools are a Pro feature; the trial adds a watermark and is for
   evaluation, not production.) Read the image before handing over.
6. **Report every WARNING** the CLI prints. A missing survey date is not cosmetic: the
   title strip shows NONE - NOT FIELD-VERIFIED.
7. **Hand off:** `elektra-sld-audit` (drafting/compliance audit), then `/ee-audit`
   (IDs and ratings vs panel schedule, spec, mimic), then the PEE.

## DWG

DWG is written through the free ODA File Converter (opendesign.com), via ezdxf's
`odafc` add-on; the engine finds it on PATH or at
`/Applications/ODAFileConverter.app`. If it is absent, `--format dwg` fails with exit
3 and an explanation — it never renames a DXF to `.dwg`. Alternative: open the DXF in
AutoCAD/BricsCAD/DraftSight and `SAVEAS` DWG (the DXF is R2018 and complete).

## What the PEE receives (CAD structure)

- **Model space:** the diagram only, 1:1 in millimetres.
- **Blocks:** every symbol is a block (`E-SYM-*`, geometry on layer 0, BYBLOCK) with
  attributes `TAG`, `DESC1`–`DESC6`, `STATUS` — editable with ATTEDIT, extractable with
  DATAEXTRACTION. Transformer blocks carry the vector-group winding glyphs
  (`"connection": "Dyn11"`).
- **Layout** named after the drawing number: border, title strip, revision block,
  legend, general notes, and a 1:1 viewport on the non-plotting `G-ANNO-VPRT` layer.
- **Layers** with ACI colour and lineweight (heavy bus 0.70 mm). Plot with
  `monochrome.ctb`. **Linetypes** `E-ASSUMED` / `E-UNKNOWN` defined in mm, LTSCALE 1.
- **Text style** `E-TEXT` (Arial). DXF text height = cap height (2.5 mm IDs, 1.8 mm
  ratings).
- **Title strip** fields for PEE name, PRC Reg. No./validity, PTR No./date/place, TIN,
  owner, location — blank underscores unless supplied in `title_block.pee`. The seal
  circle is empty and marked NOT SEALED. The draft stamp is on layer `E-ANNO-STMP`.

Removing the draft stamp, filling the PEE fields, and sealing are the PEE's acts on
their own copy after review. This pipeline never does them.

## Drawing spec schema

```json
{
  "title_block": {"project": "...", "owner": "...", "location": "...", "client": "...",
                  "drawing_title": "...", "drawing_no": "E-001", "revision": "A",
                  "date": "YYYY-MM-DD", "survey_date": "YYYY-MM-DD or null",
                  "scale": "NTS", "drawn_by": "...", "checked_by": "...", "sheet": "1 OF 1",
                  "pee": {"name": "", "prc": "", "ptr": "", "tin": ""}},
  "revisions": [{"rev": "A", "date": "...", "description": "...", "by": "..."}],
  "nodes": [{"id": "TX-1", "type": "transformer", "connection": "Dyn11",
             "lines": ["750 kVA, 13.8 kV - 400/230 V"],
             "status": "verified|assumed|unknown", "floor": "GF"}],
  "edges": [{"from": "MSB", "to": "LP-1", "kind": "feeder|service|ground",
             "label": "4-1/C 100 mm2", "status": "verified|assumed|unknown",
             "device": {"type": "breaker|fuse|disconnect|meter|ct", "label": "225AF/200AT 3P"}}],
  "notes": ["..."], "layout": "sld|riser", "floors": ["GF", "2F"],
  "sheet": "A3|A2|A1|A0|20X30IN"
}
```

Required: `title_block.project`, `drawing_title`, `drawing_no` (letters, digits, `.`
`_` `-` — it names the layout), `revision`, `date`. Node types: `utility, generator,
transformer, meter, ct, bus, panel, ats, breaker, fuse, disconnect, motor, load,
ground`. At most 6 description lines per node. Every node must be fed from a source; a
second feed (ATS emergency side, a tie) is routed from the source side.

## What it does not do

- No panel schedule tables on the sheet — use `document-skills:xlsx` or
  `/python-office-builds`.
- No plan-view layouts, conduit routing, tray fill, grounding grid geometry, or TCCs.
- No IEC 60617 symbology (ANSI/IEEE one-line style only).
- No sizing or validation of anything drawn.

## Files

- `scripts/sld_drafting_lib.py` — symbols as blocks, layout (packed tree / riser floor
  bands), title strip, legend, DXF/DWG/SVG writers, `from_topology()`,
  `text_overlaps()`, `geometry_digest()`.
- `scripts/render_sld.py` — CLI.
- `scripts/validate.py` — run after any engine change; every check must pass (CAD
  structure, layers/lineweights, mm linetypes, text style, blocks and attributes,
  paper-space layout and viewport, permit title fields, SVG/DXF text parity, no label
  collisions, determinism, topology adapter, riser, invalid-spec rejection, DWG
  round-trip when the converter is installed).
- `examples/sld_example.json`, `examples/riser_example.json`,
  `examples/title_block_example.json`.
- `reference/drafting-conventions.md` — symbols, layers, linetypes, title strip.

## Licensure boundary

Every sheet is **draft for PEE review**, never issued-for-construction. Under RA 7920 a
licensed Professional Electrical Engineer reviews, completes, signs, and seals the
drawing set. The seal is drawn empty and marked NOT SEALED, and nothing in this
pipeline fills it.
