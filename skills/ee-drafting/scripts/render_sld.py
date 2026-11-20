"""
Render a single-line or riser diagram to DXF, DWG, and/or SVG.

  python3 render_sld.py spec.json --out drawings/E-001 [--format dxf,dwg,svg]
  python3 render_sld.py topology.json --from-topology --title-block tb.json --out drawings/E-001

--out is a path stem; the format extension is appended. DWG needs the ODA File
Converter (see sld_drafting_lib.write_dwg). Prints the sheet size, paper-space layout
name, geometry digest, and any drafting warnings. Exits non-zero on an invalid spec, on
overlapping labels, or when a requested DWG cannot be written — nothing partial is
issued. --allow-overlaps renders anyway for inspection.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sld_drafting_lib as lib


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--out", required=True)
    ap.add_argument("--format", default="dxf,svg")
    ap.add_argument("--from-topology", action="store_true")
    ap.add_argument("--title-block")
    ap.add_argument("--layout", choices=("sld", "riser"))
    ap.add_argument("--allow-overlaps", action="store_true")
    args = ap.parse_args(argv)

    formats = {f.strip() for f in args.format.split(",") if f.strip()}
    unknown = formats - {"dxf", "dwg", "svg"}
    if unknown:
        ap.error(f"unknown format(s): {', '.join(sorted(unknown))}")
    if "dwg" in formats and lib.oda_converter() is None:
        print("DWG requested but the ODA File Converter is not installed "
              "(https://www.opendesign.com/guestfiles/oda_file_converter). "
              "Re-run with --format dxf,svg and SAVEAS DWG from AutoCAD/BricsCAD/DraftSight, "
              "or install the converter.", file=sys.stderr)
        return 3

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if args.from_topology:
        if not args.title_block:
            ap.error("--from-topology needs --title-block (project, drawing_title, drawing_no, revision, date)")
        tb = json.loads(Path(args.title_block).read_text(encoding="utf-8"))
        data = lib.from_topology(data, tb)
    if args.layout:
        data["layout"] = args.layout
    try:
        drawing = lib.build_drawing(data)
    except ValueError as exc:
        print(f"invalid drawing spec: {exc}", file=sys.stderr)
        return 2

    overlaps = lib.text_overlaps(drawing)
    for a, b in overlaps:
        print(f"OVERLAP: {a!r} collides with {b!r}", file=sys.stderr)
    if overlaps and not args.allow_overlaps:
        print("labels overlap; shorten the colliding lines or split the sheet "
              "(--allow-overlaps renders anyway for inspection only)", file=sys.stderr)
        return 4

    stem = Path(args.out)
    stem.parent.mkdir(parents=True, exist_ok=True)
    writers = {"dxf": lib.write_dxf, "dwg": lib.write_dwg, "svg": lib.write_svg}
    for f in sorted(formats):
        writers[f](drawing, str(stem.with_suffix("." + f)))
    print(f"sheet: {drawing.sheet} ({drawing.width:.0f} x {drawing.height:.0f} mm), layout: {drawing.layout_name}")
    print(f"blocks: {len(drawing.blocks)}, primitives: {len(drawing.prims)}")
    print(f"geometry digest: {lib.geometry_digest(drawing)}")
    for w in drawing.warnings:
        print(f"WARNING: {w}")
    for f in sorted(formats):
        print(f"wrote {stem.with_suffix('.' + f)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
