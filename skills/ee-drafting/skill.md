---
name: ee-drafting
description: >-
  Electrical drafting engine — renders single-line (one-line) diagrams and floor-banded
  riser diagrams from structured topology data to CAD-ready DXF (ezdxf, mm units,
  E-ONEL-* layers) and SVG, with ANSI/IEEE one-line symbols, an ISO A3-A0 sheet,
  title block, revision block, empty RA 7920 PEE seal box, symbol legend, and a
  DRAFT FOR PEE REVIEW stamp. Line type encodes data status (solid verified, dashed
  assumed, dotted unknown). Draws only what the topology says — never sizes, rates,
  or infers equipment. Accepts as-built-agent's topology.json directly. Use when a
  one-line diagram, SLD, riser diagram, or electrical DXF/CAD drawing needs to be
  produced or regenerated. Triggers on /ee-drafting, "draw the single-line diagram",
  "draft the SLD", "one-line drawing", "riser diagram", "electrical drawing", "DXF of
  the one-line", "CAD drawing of the panel layout", "regenerate the as-built drawing".
---

# Electrical Drafting — One-Line and Riser Diagrams

Deterministic drafting procedure. Never hand-place SVG coordinates or describe a
drawing in prose as a substitute — build the drawing spec, run
`scripts/render_sld.py`, and deliver the files it writes. The same spec always
produces the same geometry (the CLI prints a geometry digest; record it with the
revision so a re-render can be proven identical).

## Jurisdiction

| Skill / agent | Owns |
|---|---|
| `as-built-agent` | What exists in the field: topology, IDs, ratings, verification status — written to topology JSON |
| `/ee-load-calc`, `/ee-short-circuit` | Every number that goes on a replacement drawing (breaker, conductor, AIC) |
| **`/ee-drafting` (this skill)** | Turning that data into a drawing. Copies values verbatim; computes nothing |
| `elektra-sld-audit` | Auditing a finished drawing for code and drafting-convention gaps |
| `/ee-audit` | Cross-checking the drawing against calcs, specs, and the dashboard mimic |
| `/diagram-toolkit` | Non-electrical diagrams (flowcharts, org charts, CPM). Not one-lines |

If a rating needed on the drawing is missing from the input, it goes on the drawing as
UNKNOWN. Do not fill it from a typical value — a plausible-looking rating on a
drawing is read as a fact by everyone downstream.

## Procedure

1. **Get the data, not a description.** Use `as-built-agent`'s topology JSON when it
   exists (`--from-topology`), or build a drawing spec (schema below). Ratings for a
   *replacement* design come from `/ee-load-calc` / `/ee-short-circuit` output files,
   copied verbatim.
2. **Ask which format the client needs** — DXF (opens in AutoCAD, DraftSight,
   BricsCAD, LibreCAD) and/or SVG (review copy). Both by default. Native .dwg cannot be
   produced; say so if asked.
3. **Run the renderer:**
   ```bash
   python3 ~/.claude/skills/ee-drafting/scripts/render_sld.py spec.json --out deliverables/drawings/E-001
   python3 ~/.claude/skills/ee-drafting/scripts/render_sld.py topology.json --from-topology \
       --title-block tb.json --out deliverables/drawings/E-AB-001
   ```
   Add `--layout riser` (with `floor` on nodes, optional `floors` order list) for a
   riser diagram.
4. **Report every WARNING the CLI prints** (missing survey date, oversize diagram,
   truncated notes). A missing survey date is not cosmetic: the drawing is undated
   evidence and the title block says so.
5. **Look at it.** Render the SVG to PNG (`qlmanage -t -s 2400 -o <dir> file.svg` on
   macOS) and read it before handing over. Check for overlapping labels and crossing
   runs; fix the spec (shorter `lines`, split into sheets) rather than the engine.
6. **Hand off:** `elektra-sld-audit` for the drafting/compliance audit, then `/ee-audit`
   to confirm panel/feeder IDs and ratings match the panel schedule, spec, and mimic.

## Drawing spec schema

```json
{
  "title_block": {"project": "...", "client": "...", "drawing_title": "...",
                  "drawing_no": "E-001", "revision": "A", "date": "YYYY-MM-DD",
                  "survey_date": "YYYY-MM-DD or null", "scale": "NTS",
                  "drawn_by": "...", "checked_by": "UNSIGNED", "sheet": "1 OF 1"},
  "revisions": [{"rev": "A", "date": "...", "description": "...", "by": "..."}],
  "nodes": [{"id": "MSB", "type": "bus", "lines": ["400/230 V, 1600 A"],
             "status": "verified|assumed|unknown", "floor": "GF"}],
  "edges": [{"from": "MSB", "to": "LP-1", "kind": "feeder|service|ground",
             "label": "4-1/C 100 mm2", "status": "verified|assumed|unknown",
             "device": {"type": "breaker|fuse|disconnect|meter|ct", "label": "225AF/200AT 3P"}}],
  "notes": ["..."], "layout": "sld|riser", "floors": ["GF", "2F"], "sheet": "A3|A2|A1|A0"
}
```

Required: `title_block.project`, `drawing_title`, `drawing_no`, `revision`, `date`.
Node types: `utility, generator, transformer, meter, ct, bus, panel, ats, breaker,
fuse, disconnect, motor, load, ground`. Every node must be fed from a source; a node
with two feeds (ATS normal + emergency, a tie) is drawn with the second feed routed
from the source side. Invalid specs exit non-zero — nothing partial is written.

## What the engine guarantees

- DXF R2010, millimetre units, layers `E-ONEL-EQPM / -DEVC / -COND / -GRND`,
  `E-ANNO-TEXT / -RISR / -LGND / -STMP`, `G-ANNO-TTLB / -BRDR`; linetypes `DASHED`
  (assumed) and `DOT` (unknown). See `reference/drafting-conventions.md`.
- Sheet chosen automatically (smallest of A3 to A0 that fits at 1:1 drafting scale) or
  fixed by `sheet`.
- Stamp, empty seal box marked NOT SEALED, revision block, and a legend of only the
  symbols actually used are always drawn — they cannot be turned off.
- Topology status text is mapped conservatively: only an explicit VERIFIED prefix is
  drawn solid; ASSUMED is dashed; anything else is dotted UNKNOWN.

## What it does not do

- No panel schedule tables on the sheet — schedules go to `document-skills:xlsx` (or
  `/python-office-builds` for formula-driven, re-issued schedules).
- No plan-view layouts, conduit routing, cable tray fill, or grounding grid geometry.
- No protection coordination curves (TCCs) — those come from the study tool.
- No sizing or validation of anything drawn.

## Files

- `scripts/sld_drafting_lib.py` — symbols, layout (tidy tree / floor bands), title
  block, legend, DXF and SVG writers, `from_topology()` adapter, `geometry_digest()`.
- `scripts/render_sld.py` — CLI.
- `scripts/validate.py` — run after any engine change; all checks must pass (DXF audit,
  labels, stamp and seal box, SVG/DXF text parity, determinism, topology adapter on the
  `electrical-engineer` worked example, riser layout, rejection of invalid specs).
- `examples/sld_example.json` — synthetic utility + standby generator + ATS one-line.
- `examples/title_block_example.json` — title block for the `--from-topology` path.
- `reference/drafting-conventions.md` — symbol, layer, line-type, and title-block
  conventions this engine implements.

## Licensure boundary

Every sheet is **draft for PEE review**, never issued-for-construction. Under RA 7920 a
licensed Professional Electrical Engineer seals the drawing set; the seal box is drawn
empty and marked NOT SEALED, and nothing in this pipeline fills it.
