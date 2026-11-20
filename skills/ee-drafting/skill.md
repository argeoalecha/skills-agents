---
name: ee-drafting
description: >-
  Electrical drafting engine — renders single-line (one-line) and floor-banded riser
  diagrams from structured topology data to CAD-issue DWG/DXF (blocks with attributes,
  paper-space layout with a 1:1 viewport, E-ONEL-* layers with lineweights, mm
  linetypes, Arial text style) and SVG. Default sheet is 20 x 30 in, lettered to stay
  legible when reduced to A3; when inline labels will not fit legibly, feeders get tags
  (F1, F2, ...) and a FEEDER SCHEDULE. Sheet carries a Philippine permit title strip
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
   Converter — see "DWG"), DXF always, SVG as a review copy. The sheet defaults to
   `20X30IN` (762 x 508 mm), lettered to stay legible on an A3 reduction (see "Sheet
   size and reduction"). Pass `"sheet"` (`20X30IN`, `A3`–`A0`) when the LGU or client
   mandates a size, and `"reduce_to"` for the reduced prints they will make. Confirm
   the local Office of the Building Official's model title block if the drawing goes
   to a permit — LGUs differ.
3. **Render:**
   ```bash
   python3 ~/.claude/skills/ee-drafting/scripts/render_sld.py spec.json \
       --out deliverables/drawings/E-001 --format dwg,dxf,svg
   python3 ~/.claude/skills/ee-drafting/scripts/render_sld.py topology.json --from-topology \
       --title-block tb.json --out deliverables/drawings/E-AB-001
   ```
   `--layout riser` for a riser (every node needs a `floor`). The CLI prints the
   sheet and its layouts, the label mode (`inline`, or `tagged` with the number of
   feeders in the schedule), and the reduction it was lettered for. A tagged drawing
   whose schedule needs its own sheet writes a second layout `<drawing_no>-FS`; its
   SVG is `<drawing_no>-FS.svg` in the `--out` directory.
   Exit codes: 2 invalid spec, 3 DWG requested without the converter, 4 label
   collision, 5 does not fit legibly. Nothing partial is written on a non-zero exit.
4. **Fix collisions and fit in the spec, not the engine.** Exit 4 lists every label
   that hits another label or a conductor. Shorten the colliding `lines`/labels, move
   detail to general notes, or let `label_mode` fall back to tags. `--allow-overlaps`
   exists for inspection only — never issue a drawing rendered with it. Exit 5 means
   the diagram, or its feeder schedule, cannot fit the drawing area at legible size on
   the smallest plot. The engine never shrinks text to make it fit. Split the diagram
   into sheets (for example one per bus), shorten labels, use a larger sheet, or drop
   the reduction with `"reduce_to": []` when the client confirms no reduced prints.
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

## Sheet size and reduction

The default is a 20 x 30 in sheet (762 x 508 mm) that the client will also print
reduced to A3, which is a 55.1% plot (`min(420/762, 297/508)`). The engine lays the
whole sheet out at the size of its smallest plot and scales it up exactly, so every
text height is a guaranteed printed height on that reduction: at least 1.8 mm for
drawing text and 1.6 mm for title-strip captions (ISO 3098 practice). On the full
20 x 30 sheet the same text is 3.3 mm and 2.9 mm. Pens and dash lengths are full-size
values chosen so they still print on the 55% reduction.

- `"reduce_to"` lists the reduced sizes to stay legible on. It defaults to `["A3"]`
  for `20X30IN` and to `[]` for ISO sheets. The smallest plot governs.
- `"reduce_to": []` letters the sheet for its full size only. Use it only when the
  client confirms there will be no reduced prints.
- A general note states the original sheet size and the reduction it was lettered for.

## Labels: inline or tagged

`"label_mode"` is `auto` (default), `inline`, or `tagged`.

- **inline**: equipment descriptions to the right of each symbol, protection and
  conductor labels on each feeder.
- **tagged**: each feeder that has a device or a conductor label gets a numbered
  bubble (`F1`, `F2`, ... in spec edge order, or the edge's own `"tag"`). A FEEDER
  SCHEDULE lists TAG, FROM, TO, PROTECTION, CONDUCTOR, and STATUS. Leaf equipment labels
  sit centred below the symbol (above it on a riser) and levels are packed tighter.
  Device protection labels stay on the device block as invisible attributes, so
  DATAEXTRACTION still finds them.
- **auto**: inline when it fits legibly with no collisions, otherwise tagged.

The schedule goes beside the diagram, then below it, then on a second layout
`<drawing_no>-FS` (title strip `2 OF 2`, title prefixed `FEEDER SCHEDULE -`; the
diagram sheet becomes `1 OF 2`). Forcing `inline` where it cannot be legible exits 5
instead of falling back.

## What the PEE receives (CAD structure)

- **Model space:** the diagram only, 1:1 in millimetres at full sheet size.
- **Blocks:** every symbol is a block (`E-SYM-*`, geometry on layer 0, BYBLOCK) with
  attributes `TAG`, `DESC1`–`DESC10`, `STATUS` — editable with ATTEDIT, extractable with
  DATAEXTRACTION. Description lines are wrapped at 20 characters. Transformer blocks
  carry the vector-group winding glyphs (`"connection": "Dyn11"`). In tagged mode,
  inline devices carry the feeder tag and protection as invisible `TAG` / `DESC1`.
- **Layouts:** one named after the drawing number (border, title strip, revision
  block, legend, general notes, any same-sheet feeder schedule, and a 1:1 viewport on
  the non-plotting `G-ANNO-VPRT` layer), plus `<drawing_no>-FS` when the schedule
  needs its own sheet. Page setup is the full sheet size.
- **Layers** with ACI colour and full-size lineweight (heavy bus and border 1.00 mm).
  Plot with `monochrome.ctb`. **Linetypes** `E-ASSUMED` / `E-UNKNOWN` defined in mm,
  LTSCALE 1.
- **Text style** `E-TEXT` (Arial). DXF text height = cap height, sized for the
  smallest plot (see "Sheet size and reduction").
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
             "label": "4-1/C 100 mm2", "status": "verified|assumed|unknown", "tag": "F3",
             "device": {"type": "breaker|fuse|disconnect|meter|ct", "label": "225AF/200AT 3P"}}],
  "notes": ["..."], "layout": "sld|riser", "floors": ["GF", "2F"],
  "sheet": "20X30IN|A3|A2|A1|A0", "reduce_to": ["A3"],
  "label_mode": "auto|inline|tagged"
}
```

Required: `title_block.project`, `drawing_title`, `drawing_no` (letters, digits, `.`
`_` `-` — it names the layout), `revision`, `date`. Node types: `utility, generator,
transformer, meter, ct, bus, panel, ats, breaker, fuse, disconnect, motor, load,
ground`. At most 6 description lines per node, and at most 10 once wrapped at 20
characters. Edge `tag` is optional and overrides the generated `F<n>`. Every node must
be fed from a source; a second feed (ATS emergency side, a tie) is routed from the
source side. On a riser, a breaker on a long vertical feeder sits just off the
switchboard, where it is physically mounted, not halfway up the riser. Ground conductors
bend on their own track, clear of feeder bends.

## What it does not do

- No panel schedule tables on the sheet (the FEEDER SCHEDULE lists feeders only) —
  use `document-skills:xlsx` or `/python-office-builds`.
- Never shrinks text below the legibility floor to make a diagram fit; it exits 5.
- No plan-view layouts, conduit routing, tray fill, grounding grid geometry, or TCCs.
- No IEC 60617 symbology (ANSI/IEEE one-line style only).
- No sizing or validation of anything drawn.

## Files

- `scripts/sld_drafting_lib.py` — symbols as blocks, layout (packed tree / riser floor
  bands), inline or tagged labels, feeder schedule, title strip, legend, DXF/DWG/SVG
  writers, `from_topology()`, `plot_scale()`, `text_overlaps()`, `geometry_digest()`,
  `DoesNotFit`.
- `scripts/render_sld.py` — CLI.
- `scripts/validate.py` — run after any engine change; every check must pass (20 x 30
  default and CAD structure, layers/lineweights, text style, blocks and attributes,
  layouts and viewport, permit title fields, every printed text/pen/dash legible on the
  A3 reduction, feeder tags and schedule with hidden protection attributes, SVG/DXF
  text parity, inline path and DoesNotFit, no label collisions, determinism, topology
  adapter, riser, invalid-spec rejection, DWG round-trip when the converter is
  installed).
- `examples/sld_example.json`, `examples/riser_example.json`,
  `examples/title_block_example.json`.
- `reference/drafting-conventions.md` — symbols, layers, linetypes, sheet and
  reduction, feeder tags and schedule, title strip, text heights.

## Licensure boundary

Every sheet is **draft for PEE review**, never issued-for-construction. Under RA 7920 a
licensed Professional Electrical Engineer reviews, completes, signs, and seals the
drawing set. The seal is drawn empty and marked NOT SEALED, and nothing in this
pipeline fills it.
