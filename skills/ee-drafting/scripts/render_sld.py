"""
Render a single-line or riser diagram to DXF and/or SVG.

  python3 render_sld.py spec.json --out drawings/E-001 [--format dxf,svg]
  python3 render_sld.py topology.json --from-topology --title-block tb.json --out drawings/E-001

--out is a path stem; .dxf and .svg are appended. Prints the sheet size, the geometry
digest, and any drafting warnings (missing survey date, oversize diagram, truncated
notes). Exits non-zero on an invalid spec instead of drawing a partial diagram.
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
    args = ap.parse_args(argv)

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

    stem = Path(args.out)
    stem.parent.mkdir(parents=True, exist_ok=True)
    formats = {f.strip() for f in args.format.split(",") if f.strip()}
    unknown = formats - {"dxf", "svg"}
    if unknown:
        ap.error(f"unknown format(s): {', '.join(sorted(unknown))}")
    if "dxf" in formats:
        lib.write_dxf(drawing, str(stem.with_suffix(".dxf")))
    if "svg" in formats:
        lib.write_svg(drawing, str(stem.with_suffix(".svg")))
    print(f"sheet: {drawing.sheet} ({drawing.width:.0f} x {drawing.height:.0f} mm)")
    print(f"primitives: {len(drawing.prims)}")
    print(f"geometry digest: {lib.geometry_digest(drawing)}")
    for w in drawing.warnings:
        print(f"WARNING: {w}")
    for f in sorted(formats):
        print(f"wrote {stem.with_suffix('.' + f)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
