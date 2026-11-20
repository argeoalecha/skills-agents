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
TITLE_BLOCK = SKILL / "examples" / "title_block_example.json"
TOPOLOGY = SKILL.parent / "electrical-engineer" / "references" / "example-panel-upgrade-synthetic" / "topology.json"
PERMIT_FIELDS = ("PROFESSIONAL ELECTRICAL ENGINEER", "PRC REG. NO. / VALIDITY",
                 "PTR NO. / DATE / PLACE ISSUED", "TIN", "OWNER", "LOCATION", "PROJECT",
                 "SHEET CONTENTS / DRAWING TITLE", "DRAWING NO.", "REVISION", "SURVEY DATE")


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  ok  {msg}")


def all_texts(doc):
    """Every rendered string: model and paper TEXT, ATTRIBs, and TEXT inside inserted
    blocks (once per insert)."""
    out = []
    spaces = [doc.modelspace()] + [doc.layouts.get(n) for n in doc.layouts.names() if n != "Model"]
    for space in spaces:
        for e in space:
            if e.dxftype() == "TEXT":
                out.append(e.dxf.text)
            elif e.dxftype() == "INSERT":
                out += [a.dxf.text for a in e.attribs]
                out += [b.dxf.text for b in doc.blocks.get(e.dxf.name) if b.dxftype() == "TEXT"]
    return out


def validate_cad_structure(tmp):
    print("[1] DXF is CAD-issue structured: layout, blocks, layers, linetypes, text style")
    import ezdxf
    spec = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    d = lib.build_drawing(spec)
    lib.write_dxf(d, str(tmp / "ex.dxf"))
    doc = ezdxf.readfile(str(tmp / "ex.dxf"))
    check(not doc.audit().has_errors, "DXF passes ezdxf audit with no errors")
    check(doc.header["$INSUNITS"] == 4 and doc.header["$MEASUREMENT"] == 1, "units are metric millimetres")
    for name, (aci, lw, plots) in lib.LAYERS.items():
        layer = doc.layers.get(name)
        check(layer.dxf.lineweight == lw and layer.dxf.color == aci and bool(layer.dxf.plot) == plots,
              f"layer {name}: colour {aci}, lineweight {lw / 100:.2f} mm, plot={plots}")
    for name, (pattern, _, _) in lib.LINETYPES.items():
        check(name in doc.linetypes and max(abs(v) for v in pattern[1:]) >= 1.0,
              f"linetype {name} defined in mm with visible elements ({pattern})")
    check(doc.header["$LTSCALE"] == 1.0, "LTSCALE is 1 (linetypes are already in mm)")
    style = doc.styles.get(lib.TEXT_STYLE)
    check(style.dxf.font.lower() == lib.TEXT_FONT, f"text style {lib.TEXT_STYLE} uses {lib.TEXT_FONT}")
    texts = [e for e in doc.query("TEXT ATTRIB")]
    check(all(t.dxf.style == lib.TEXT_STYLE for t in texts), "every TEXT/ATTRIB uses the drawing text style")

    msp = doc.modelspace()
    inserts = msp.query("INSERT")
    tags = {a.dxf.text for i in inserts for a in i.attribs if a.dxf.tag == "TAG"}
    for n in spec["nodes"]:
        if n["type"] != "bus":
            check(n["id"] in tags, f"{n['id']} is a block insert with a TAG attribute")
    for i in inserts:
        blk = doc.blocks.get(i.dxf.name)
        check(all(e.dxf.layer == "0" for e in blk if e.dxftype() != "ATTDEF"),
              f"block {i.dxf.name} geometry on layer 0 (inherits insert layer)")
        break
    check(any(a.dxf.tag == "STATUS" for i in inserts for a in i.attribs), "non-verified nodes carry a STATUS attribute")

    layout = doc.layouts.get(d.layout_name)
    check(layout is not None, f"paper-space layout named {d.layout_name}")
    ps_texts = [e.dxf.text for e in layout if e.dxftype() == "TEXT"]
    ms_texts = [e.dxf.text for e in msp if e.dxftype() == "TEXT"]
    check(lib.STAMP in ps_texts and lib.STAMP not in ms_texts, "stamp and title block live in paper space only")
    for f in PERMIT_FIELDS:
        check(f in ps_texts, f"title strip field: {f}")
    check("NOT SEALED" in ps_texts, "seal box drawn empty and marked NOT SEALED")
    vps = [e for e in layout if e.dxftype() == "VIEWPORT" and e.dxf.layer == "G-ANNO-VPRT"]
    check(len(vps) == 1, "one diagram viewport on the non-plotting G-ANNO-VPRT layer")
    check(abs(vps[0].dxf.view_height - vps[0].dxf.height) < 0.01, "viewport scale is 1:1")
    check(any(e.dxf.get("linetype") == "E-ASSUMED" for e in msp), "assumed data drawn with E-ASSUMED")
    check(any(e.dxf.get("linetype") == "E-UNKNOWN" for e in msp), "unknown data drawn with E-UNKNOWN")
    bus = [e for e in msp if e.dxf.layer == "E-ONEL-BUSS"]
    check(len(bus) >= 2, "buses drawn on the heavy E-ONEL-BUSS layer")
    tx = [b for b in doc.blocks if b.name.startswith("E-SYM-TRANSFORMER-DYN11")]
    check(len(tx) == 1, "transformer block carries its Dyn11 winding glyphs")

    lib.write_svg(d, str(tmp / "ex.svg"))
    root = ET.parse(str(tmp / "ex.svg")).getroot()
    svg_texts = [t.text for t in root.iter("{http://www.w3.org/2000/svg}text")]
    check(collections.Counter(svg_texts) == collections.Counter(all_texts(doc)), "SVG and DXF carry identical text")
    check(lib.text_overlaps(d) == [], "no overlapping labels in model space")
    check(any("survey_date" in w for w in d.warnings), "missing survey date raised as a warning")


def validate_determinism():
    print("[2] Geometry is deterministic")
    spec = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    a = lib.geometry_digest(lib.build_drawing(copy.deepcopy(spec)))
    check(a == lib.geometry_digest(lib.build_drawing(copy.deepcopy(spec))), "same input gives the same geometry digest")
    spec["nodes"][0]["lines"].append("CHANGED")
    check(lib.geometry_digest(lib.build_drawing(spec)) != a, "changed input changes the digest")


def validate_topology_adapter(tmp):
    print("[3] as-built topology.json adapter (worked example)")
    import ezdxf
    topo = json.loads(TOPOLOGY.read_text(encoding="utf-8"))
    tb = json.loads(TITLE_BLOCK.read_text(encoding="utf-8"))
    spec = lib.from_topology(topo, tb)
    d = lib.build_drawing(spec)
    lib.write_dxf(d, str(tmp / "topo.dxf"))
    doc = ezdxf.readfile(str(tmp / "topo.dxf"))
    check(not doc.audit().has_errors, "adapter DXF passes audit")
    texts = all_texts(doc)
    for n in topo["nodes"]:
        check(n["id"] in texts, f"topology node {n['id']} drawn")
    statuses = {n["status"] for n in lib.load_drawing_spec(spec)["nodes"].values()}
    check("verified" not in statuses, "no topology node silently promoted to verified")
    check(lib.text_overlaps(d) == [], "no overlapping labels")
    bad = copy.deepcopy(topo)
    bad["nodes"][0]["type"] = "mystery_box"
    try:
        lib.from_topology(bad, tb)
        raise AssertionError("unmapped topology type was accepted")
    except ValueError:
        check(True, "unmapped topology node type is rejected, not drawn as a generic box")


def validate_riser(tmp):
    print("[4] Riser layout groups nodes by floor")
    import ezdxf
    spec = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    floors = {"UTIL": "GF", "TX-1": "GF", "MSB": "GF", "GEN-1": "GF", "ATS-1": "GF", "EMB": "GF",
              "GND-1": "GF", "LP-1": "2F", "PP-1": "2F", "ACU-1": "RF", "ELP-1": "3F", "FP-1": "GF"}
    for n in spec["nodes"]:
        n["floor"] = floors[n["id"]]
    spec["layout"] = "riser"
    spec["floors"] = ["GF", "2F", "3F", "RF"]
    d = lib.build_drawing(spec)
    lib.write_dxf(d, str(tmp / "riser.dxf"))
    doc = ezdxf.readfile(str(tmp / "riser.dxf"))
    check(not doc.audit().has_errors, "riser DXF passes audit")
    texts = all_texts(doc)
    for f in spec["floors"]:
        check(f"FLOOR {f}" in texts, f"floor line {f} drawn")
    check(lib.text_overlaps(d) == [], "no label collisions (text or conductor) in the riser")
    try:
        bad = copy.deepcopy(spec)
        bad["nodes"][0].pop("floor")
        lib.build_drawing(bad)
        raise AssertionError("riser node without a floor was accepted")
    except ValueError:
        check(True, "riser rejects a node with no floor instead of guessing one")


def validate_rejections():
    print("[5] Invalid specs are rejected, never partially drawn")
    base = json.loads(EXAMPLE.read_text(encoding="utf-8"))
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
    print("[6] DWG export through the ODA File Converter")
    if lib.oda_converter() is None:
        print("  SKIPPED  ODA File Converter not installed — DWG not verified on this machine")
        return
    from ezdxf.addons import odafc
    d = lib.build_drawing(json.loads(EXAMPLE.read_text(encoding="utf-8")))
    lib.write_dwg(d, str(tmp / "ex.dwg"))
    doc = odafc.readfile(str(tmp / "ex.dwg"))
    check(d.layout_name in doc.layouts.names(), "DWG round-trips with its paper-space layout")
    check(len(doc.modelspace().query("INSERT")) > 0, "DWG round-trips with block inserts")


def main():
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        validate_cad_structure(tmp)
        validate_determinism()
        validate_topology_adapter(tmp)
        validate_riser(tmp)
        validate_rejections()
        validate_dwg(tmp)
    print("\nALL VALIDATIONS PASSED")


if __name__ == "__main__":
    main()
