"""
Validation suite for sld_drafting_lib. Run after any change to the engine:

  python3 validate.py

All checks must pass before a drawing from this engine goes to PEE review. Output files
are written to a temporary directory and removed afterwards.
"""
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
STAMP = "DRAFT FOR PEE REVIEW - NOT FOR CONSTRUCTION"


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  ok  {msg}")


def dxf_texts(path):
    import ezdxf
    doc = ezdxf.readfile(path)
    auditor = doc.audit()
    return doc, auditor, [e.dxf.text for e in doc.modelspace().query("TEXT")]


def validate_example(tmp):
    print("[1] Example SLD renders to valid DXF and SVG")
    spec = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    d = lib.build_drawing(spec)
    lib.write_dxf(d, str(tmp / "ex.dxf"))
    lib.write_svg(d, str(tmp / "ex.svg"))
    doc, auditor, texts = dxf_texts(str(tmp / "ex.dxf"))
    check(not auditor.has_errors, "DXF passes ezdxf audit with no errors")
    check(doc.header["$INSUNITS"] == 4, "DXF units are millimetres")
    check(set(lib.LAYERS) <= {layer.dxf.name for layer in doc.layers}, "all standard layers defined")
    for n in spec["nodes"]:
        check(n["id"] in texts, f"node {n['id']} labelled in DXF")
    check(texts.count(STAMP) >= 2, "draft stamp on sheet and in title block")
    check("NOT SEALED" in texts and "(RA 7920)" in texts, "empty RA 7920 seal box present")
    check("NONE - NOT FIELD-VERIFIED" in texts, "missing survey date shown as not field-verified")
    check(any("survey_date" in w for w in d.warnings), "missing survey date raised as a warning")
    root = ET.parse(str(tmp / "ex.svg")).getroot()
    svg_texts = [t.text for t in root.iter("{http://www.w3.org/2000/svg}text")]
    check(sorted(svg_texts) == sorted(texts), "SVG and DXF carry identical text")
    dashed = [e for e in doc.modelspace() if e.dxf.hasattr("linetype") and e.dxf.linetype == "DASHED"]
    check(len(dashed) > 0, "assumed data drawn with DASHED linetype")
    for lt in ("DASHED", "DOT"):
        check(lt in doc.linetypes, f"linetype {lt} defined in DXF")


def validate_determinism():
    print("[2] Geometry is deterministic")
    spec = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    a = lib.geometry_digest(lib.build_drawing(copy.deepcopy(spec)))
    b = lib.geometry_digest(lib.build_drawing(copy.deepcopy(spec)))
    check(a == b, "same input gives the same geometry digest")
    spec["nodes"][0]["lines"].append("CHANGED")
    check(lib.geometry_digest(lib.build_drawing(spec)) != a, "changed input changes the digest")


def validate_topology_adapter(tmp):
    print("[3] as-built topology.json adapter (worked example)")
    topo = json.loads(TOPOLOGY.read_text(encoding="utf-8"))
    tb = json.loads(TITLE_BLOCK.read_text(encoding="utf-8"))
    spec = lib.from_topology(topo, tb)
    d = lib.build_drawing(spec)
    lib.write_dxf(d, str(tmp / "topo.dxf"))
    _, auditor, texts = dxf_texts(str(tmp / "topo.dxf"))
    check(not auditor.has_errors, "adapter DXF passes audit")
    for n in topo["nodes"]:
        check(n["id"] in texts, f"topology node {n['id']} drawn")
    statuses = {n["status"] for n in lib.load_drawing_spec(spec)["nodes"].values()}
    check("verified" not in statuses, "no topology node silently promoted to verified")
    bad = copy.deepcopy(topo)
    bad["nodes"][0]["type"] = "mystery_box"
    try:
        lib.from_topology(bad, tb)
        raise AssertionError("unmapped topology type was accepted")
    except ValueError:
        check(True, "unmapped topology node type is rejected, not drawn as a generic box")


def validate_riser(tmp):
    print("[4] Riser layout groups nodes by floor")
    spec = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    floors = {"UTIL": "GF", "TX-1": "GF", "MSB": "GF", "GEN-1": "GF", "ATS-1": "GF", "EMB": "GF",
              "GND-1": "GF", "LP-1": "2F", "PP-1": "2F", "ACU-1": "RF", "ELP-1": "3F", "FP-1": "GF"}
    for n in spec["nodes"]:
        n["floor"] = floors[n["id"]]
    spec["layout"] = "riser"
    spec["floors"] = ["GF", "2F", "3F", "RF"]
    d = lib.build_drawing(spec)
    lib.write_dxf(d, str(tmp / "riser.dxf"))
    _, auditor, texts = dxf_texts(str(tmp / "riser.dxf"))
    check(not auditor.has_errors, "riser DXF passes audit")
    for f in spec["floors"]:
        check(f"FLOOR {f}" in texts, f"floor line {f} drawn")


def validate_rejections():
    print("[5] Invalid specs are rejected, never partially drawn")
    base = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    cases = {
        "unknown node type": lambda s: s["nodes"][0].update(type="widget"),
        "edge to missing node": lambda s: s["edges"].append({"from": "MSB", "to": "NOPE"}),
        "duplicate node id": lambda s: s["nodes"].append(dict(s["nodes"][0])),
        "missing drawing number": lambda s: s["title_block"].pop("drawing_no"),
        "unknown data status": lambda s: s["nodes"][0].update(status="probably"),
        "cycle": lambda s: s["edges"].append({"from": "LP-1", "to": "UTIL"}),
        "unknown inline device": lambda s: s["edges"][0].update(device={"type": "relay"}),
    }
    for name, mutate in cases.items():
        s = copy.deepcopy(base)
        mutate(s)
        try:
            lib.build_drawing(s)
            raise AssertionError(f"{name} was accepted")
        except ValueError:
            check(True, f"rejects {name}")


def main():
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        validate_example(tmp)
        validate_determinism()
        validate_topology_adapter(tmp)
        validate_riser(tmp)
        validate_rejections()
    print("\nALL VALIDATIONS PASSED")


if __name__ == "__main__":
    main()
