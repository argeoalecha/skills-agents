"""
Validation suite for sld_drafting_lib. Run after any change to the engine:

  python3 validate.py

All checks must pass before a drawing from this engine goes to PEE review. Output files
are written to a temporary directory and removed afterwards. The DWG round-trip runs
only when the ODA File Converter is installed; it is reported as SKIPPED otherwise.
"""
import collections
import copy
import json
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sld_drafting_lib as lib

SKILL = HERE.parent
EXAMPLE = SKILL / "examples" / "sld_example.json"
RISER = SKILL / "examples" / "riser_example.json"
TITLE_BLOCK = SKILL / "examples" / "title_block_example.json"
TOPOLOGY = SKILL.parent / "electrical-engineer" / "references" / "example-panel-upgrade-synthetic" / "topology.json"
PERMIT_FIELDS = ("PROFESSIONAL ELECTRICAL ENGINEER", "PRC REG. NO. / VALIDITY",
                 "PTR NO. / DATE / PLACE ISSUED", "TIN", "OWNER", "LOCATION", "PROJECT",
                 "SHEET CONTENTS / DRAWING TITLE", "DRAWING NO.", "REVISION", "SURVEY DATE")
MIN_TEXT_ON_SMALLEST = 1.8
MIN_CAPTION_ON_SMALLEST = 1.6
MIN_PEN_ON_SMALLEST = 0.13
MIN_DASH_ON_SMALLEST = 0.5


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  ok  {msg}")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def spaces(doc):
    return [doc.modelspace()] + [doc.layouts.get(n) for n in doc.layouts.names() if n != "Model"]


def visible_texts(doc):
    """Every printed string with its height: TEXT in all spaces, visible ATTRIBs, and
    TEXT inside inserted blocks (once per insert)."""
    out = []
    for space in spaces(doc):
        for e in space:
            if e.dxftype() == "TEXT":
                out.append((e.dxf.text, e.dxf.height))
            elif e.dxftype() == "INSERT":
                out += [(a.dxf.text, a.dxf.height) for a in e.attribs if not a.dxf.flags & 1]
                out += [(b.dxf.text, b.dxf.height) for b in doc.blocks.get(e.dxf.name) if b.dxftype() == "TEXT"]
    return out


def svg_texts(path):
    root = ET.parse(str(path)).getroot()
    return [t.text or "" for t in root.iter("{http://www.w3.org/2000/svg}text")]


def render(spec, tmp, stem):
    import ezdxf
    d = lib.build_drawing(spec)
    lib.write_dxf(d, str(tmp / f"{stem}.dxf"))
    for i in range(len(d.sheets)):
        lib.write_svg(d, str(tmp / f"{stem}-{i}.svg"), i)
    return d, ezdxf.readfile(str(tmp / f"{stem}.dxf"))


def validate_cad_structure(tmp):
    print("[1] 20x30 in sheet, CAD structure: layouts, blocks, layers, linetypes, text style")
    spec = load(EXAMPLE)
    d, doc = render(spec, tmp, "ex")
    check(not doc.audit().has_errors, "DXF passes ezdxf audit with no errors")
    check(doc.header["$INSUNITS"] == 4 and doc.header["$MEASUREMENT"] == 1, "units are metric millimetres")
    check((d.sheet, d.width, d.height) == ("20X30IN", 762.0, 508.0), "default sheet is 20 x 30 in (762 x 508 mm)")
    check(d.reductions == ("A3",), "default reduction target is A3")
    for name, (aci, lw, plots) in lib.LAYERS.items():
        layer = doc.layers.get(name)
        check(layer.dxf.lineweight == lw and layer.dxf.color == aci and bool(layer.dxf.plot) == plots,
              f"layer {name}: colour {aci}, lineweight {lw / 100:.2f} mm, plot={plots}")
    check(doc.header["$LTSCALE"] == 1.0, "LTSCALE is 1 (linetypes are already in mm)")
    style = doc.styles.get(lib.TEXT_STYLE)
    check(style.dxf.font.lower() == lib.TEXT_FONT, f"text style {lib.TEXT_STYLE} uses {lib.TEXT_FONT}")
    check(all(t.dxf.style == lib.TEXT_STYLE for t in doc.query("TEXT ATTRIB")),
          "every TEXT/ATTRIB uses the drawing text style")

    msp = doc.modelspace()
    inserts = msp.query("INSERT")
    tags = {a.dxf.text for i in inserts for a in i.attribs if a.dxf.tag == "TAG"}
    for n in spec["nodes"]:
        if n["type"] != "bus":
            check(n["id"] in tags, f"{n['id']} is a block insert with a TAG attribute")
    blk = doc.blocks.get(inserts[0].dxf.name)
    check(all(e.dxf.layer == "0" for e in blk if e.dxftype() != "ATTDEF"), "block geometry on layer 0")
    check(any(a.dxf.tag == "STATUS" for i in inserts for a in i.attribs), "non-verified nodes carry a STATUS attribute")
    check(len([b for b in doc.blocks if b.name.startswith("E-SYM-TRANSFORMER-DYN11")]) == 1,
          "transformer block carries its Dyn11 winding glyphs")
    check(len(msp.query('LINE[layer=="E-ONEL-BUSS"]')) >= 2, "buses on the heavy E-ONEL-BUSS layer")
    check(any(e.dxf.get("linetype") == "E-ASSUMED" for e in msp), "assumed data drawn with E-ASSUMED")
    check(any(e.dxf.get("linetype") == "E-UNKNOWN" for e in msp), "unknown data drawn with E-UNKNOWN")

    layout = doc.layouts.get(d.sheets[0])
    ps_texts = [e.dxf.text for e in layout if e.dxftype() == "TEXT"]
    check(lib.STAMP in ps_texts and lib.STAMP not in [e.dxf.text for e in msp.query("TEXT")],
          "stamp and title strip live in paper space only")
    for f in PERMIT_FIELDS:
        check(f in ps_texts, f"title strip field: {f}")
    check("NOT SEALED" in ps_texts, "seal drawn empty and marked NOT SEALED")
    vps = [e for e in layout if e.dxftype() == "VIEWPORT" and e.dxf.layer == "G-ANNO-VPRT"]
    check(len(vps) == 1 and abs(vps[0].dxf.view_height - vps[0].dxf.height) < 0.01,
          "one 1:1 diagram viewport on the non-plotting G-ANNO-VPRT layer")
    psize = (layout.dxf_layout.dxf.paper_width, layout.dxf_layout.dxf.paper_height)
    check(tuple(round(v) for v in psize) == (762, 508), "layout page setup is 762 x 508 mm")
    check(lib.text_overlaps(d) == [], "no label collisions (text-text or text-conductor)")
    check(any("survey_date" in w for w in d.warnings), "missing survey date raised as a warning")
    check(len(d.warnings) == len(set(d.warnings)), "warnings are not duplicated")
    return d, doc


def validate_reduction_legibility(d, doc):
    print("[2] Legible on the A3 reduction (every printed text, pen, and dash)")
    s = d.min_plot_scale
    check(abs(s - min(420 / 762, 297 / 508)) < 1e-9, f"A3 reduction scale is {s * 100:.1f}%")
    texts = visible_texts(doc)
    smallest = min(h for _, h in texts) * s
    check(smallest >= MIN_CAPTION_ON_SMALLEST - 1e-6,
          f"smallest printed text is {smallest:.2f} mm on A3 (>= {MIN_CAPTION_ON_SMALLEST} captions)")
    model_min = min([a.dxf.height for i in doc.modelspace().query("INSERT") for a in i.attribs if not a.dxf.flags & 1]
                    + [t.dxf.height for t in doc.modelspace().query("TEXT")]) * s
    check(model_min >= MIN_TEXT_ON_SMALLEST - 1e-6,
          f"smallest diagram text is {model_min:.2f} mm on A3 (>= {MIN_TEXT_ON_SMALLEST})")
    for name, (_, lw, plots) in lib.LAYERS.items():
        if plots:
            check(lw / 100 * s >= MIN_PEN_ON_SMALLEST, f"{name} pen {lw / 100:.2f} mm prints {lw / 100 * s:.2f} mm on A3")
    for name, (pattern, _, _) in lib.LINETYPES.items():
        shortest = min(abs(v) for v in pattern[1:]) * s
        check(shortest >= MIN_DASH_ON_SMALLEST, f"{name} shortest element prints {shortest:.2f} mm on A3")
    joined = " ".join(" ".join(t.split()) for t, _ in texts)
    check("ORIGINAL SHEET SIZE 20 X 30 IN" in joined and "REDUCED TO A3" in joined,
          "sheet notes the original size and the A3 reduction")


def validate_tagged(d, doc, tmp):
    print("[3] Tagged labels: feeder bubbles, schedule sheet, protection kept as hidden attributes")
    spec = load(EXAMPLE)
    check(d.label_mode == "tagged", "auto mode chose feeder tags (inline does not fit legibly)")
    n_feeders = sum(1 for e in spec["edges"] if e.get("device") or e.get("label"))
    check(d.schedule_rows == n_feeders, f"feeder schedule lists all {n_feeders} labelled feeders")
    texts = [t for t, _ in visible_texts(doc)]
    for i in range(1, n_feeders + 1):
        check(texts.count(f"F{i}") >= 2, f"F{i} appears as a bubble on the diagram and a schedule row")
    hidden = {a.dxf.text for i in doc.modelspace().query("INSERT") for a in i.attribs if a.dxf.flags & 1}
    for e in spec["edges"]:
        if (e.get("device") or {}).get("label"):
            check(e["device"]["label"] in hidden, f"protection '{e['device']['label']}' kept as an invisible attribute")
    if len(d.sheets) > 1:
        fs = doc.layouts.get(d.sheets[1])
        fs_texts = [e.dxf.text for e in fs if e.dxftype() == "TEXT"]
        check("FEEDER SCHEDULE" in fs_texts and "2 OF 2" in fs_texts, f"schedule on its own sheet {d.sheets[1]} (2 OF 2)")
    svg = []
    for i in range(len(d.sheets)):
        svg += svg_texts(tmp / f"ex-{i}.svg")
    check(collections.Counter(svg) == collections.Counter(texts), "SVG sheets and DXF carry identical printed text")


def validate_inline_and_fit(tmp):
    print("[4] Inline path without reduction; DoesNotFit when a forced mode cannot be legible")
    spec = load(EXAMPLE)
    spec.update(sheet="A1", reduce_to=[])
    d, doc = render(spec, tmp, "inline")
    check(d.label_mode == "inline" and len(d.sheets) == 1 and d.schedule_rows == 0,
          "A1 with no reduction draws inline labels on one sheet")
    check(not doc.audit().has_errors and lib.text_overlaps(d) == [], "inline drawing audits clean, no collisions")
    forced = load(EXAMPLE)
    forced["label_mode"] = "inline"
    try:
        lib.build_drawing(forced)
        raise AssertionError("inline labels were forced onto an illegible A3 reduction")
    except lib.DoesNotFit:
        check(True, "inline labels that cannot be legible on A3 raise DoesNotFit, nothing drawn")


def validate_determinism():
    print("[5] Geometry is deterministic")
    spec = load(EXAMPLE)
    a = lib.geometry_digest(lib.build_drawing(copy.deepcopy(spec)))
    check(a == lib.geometry_digest(lib.build_drawing(copy.deepcopy(spec))), "same input gives the same geometry digest")
    spec["nodes"][0]["lines"].append("CHANGED")
    check(lib.geometry_digest(lib.build_drawing(spec)) != a, "changed input changes the digest")


def validate_topology_adapter(tmp):
    print("[6] as-built topology.json adapter (worked example)")
    topo = load(TOPOLOGY)
    tb = load(TITLE_BLOCK)
    spec = lib.from_topology(topo, tb)
    d, doc = render(spec, tmp, "topo")
    check(not doc.audit().has_errors, "adapter DXF passes audit")
    texts = [t for t, _ in visible_texts(doc)]
    for n in topo["nodes"]:
        check(n["id"] in texts, f"topology node {n['id']} drawn")
    statuses = {n["status"] for n in lib.load_drawing_spec(spec)["nodes"].values()}
    check("verified" not in statuses, "no topology node silently promoted to verified")
    check(lib.text_overlaps(d) == [], "no label collisions")
    bad = copy.deepcopy(topo)
    bad["nodes"][0]["type"] = "mystery_box"
    try:
        lib.from_topology(bad, tb)
        raise AssertionError("unmapped topology type was accepted")
    except ValueError:
        check(True, "unmapped topology node type is rejected, not drawn as a generic box")


def validate_riser(tmp):
    print("[7] Riser: floor bands, breakers at the switchboard")
    spec = load(RISER)
    d, doc = render(spec, tmp, "riser")
    check(not doc.audit().has_errors, "riser DXF passes audit")
    texts = [t for t, _ in visible_texts(doc)]
    for f in spec["floors"]:
        check(f"FLOOR {f}" in texts, f"floor line {f} drawn")
    check(lib.text_overlaps(d) == [], "no label collisions in the riser")
    bad = copy.deepcopy(spec)
    bad["nodes"][1].pop("floor")
    try:
        lib.build_drawing(bad)
        raise AssertionError("riser node without a floor was accepted")
    except ValueError:
        check(True, "riser rejects a node with no floor instead of guessing one")


def validate_rejections():
    print("[8] Invalid specs are rejected, never partially drawn")
    base = load(EXAMPLE)
    cases = {
        "unknown node type": lambda s: s["nodes"][0].update(type="widget"),
        "edge to missing node": lambda s: s["edges"].append({"from": "MSB", "to": "NOPE"}),
        "duplicate node id": lambda s: s["nodes"].append(dict(s["nodes"][0])),
        "missing drawing number": lambda s: s["title_block"].pop("drawing_no"),
        "drawing number unusable as a layout name": lambda s: s["title_block"].update(drawing_no="E 001/A"),
        "unknown data status": lambda s: s["nodes"][0].update(status="probably"),
        "cycle": lambda s: s["edges"].append({"from": "LP-1", "to": "UTIL"}),
        "unknown inline device": lambda s: s["edges"][0].update(device={"type": "relay"}),
        "invalid vector group": lambda s: s["nodes"][1].update(connection="delta-wye"),
        "unknown sheet size": lambda s: s.update(sheet="B4"),
        "unknown reduction size": lambda s: s.update(reduce_to=["LETTER"]),
        "unknown label mode": lambda s: s.update(label_mode="tiny"),
        "too many description lines": lambda s: s["nodes"][0].update(lines=["X"] * 7),
    }
    for name, mutate in cases.items():
        s = copy.deepcopy(base)
        mutate(s)
        try:
            lib.build_drawing(s)
            raise AssertionError(f"{name} was accepted")
        except ValueError:
            check(True, f"rejects {name}")


def validate_dwg(tmp):
    print("[9] DWG export through the ODA File Converter")
    if lib.oda_converter() is None:
        print("  SKIPPED  ODA File Converter not installed — DWG not verified on this machine")
        return
    from ezdxf.addons import odafc
    d = lib.build_drawing(load(EXAMPLE))
    lib.write_dwg(d, str(tmp / "ex.dwg"))
    doc = odafc.readfile(str(tmp / "ex.dwg"))
    check(all(n in doc.layouts.names() for n in d.sheets), "DWG round-trips with every layout")
    check(len(doc.modelspace().query("INSERT")) > 0, "DWG round-trips with block inserts")


def main():
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        d, doc = validate_cad_structure(tmp)
        validate_reduction_legibility(d, doc)
        validate_tagged(d, doc, tmp)
        validate_inline_and_fit(tmp)
        validate_determinism()
        validate_topology_adapter(tmp)
        validate_riser(tmp)
        validate_rejections()
        validate_dwg(tmp)
    print("\nALL VALIDATIONS PASSED")


if __name__ == "__main__":
    main()
