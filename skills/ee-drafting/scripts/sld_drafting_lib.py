"""
Electrical drafting engine — single-line (one-line) and riser diagrams from structured
topology data, written to DXF/DWG (via ezdxf, DWG through the ODA File Converter) and
SVG from one shared geometry model.

CAD structure follows ordinary AutoCAD sheet practice:
- Model space holds only the diagram, at 1:1 in millimetres.
- Every equipment and device symbol is a BLOCK (geometry on layer 0, BYBLOCK linetype,
  colour and lineweight) inserted with ATTRIBs: TAG, DESC1..DESCn, STATUS — so symbols
  edit as blocks and data extracts with DATAEXTRACTION/ATTEXT.
- A paper-space layout named after the drawing number carries the sheet border, the
  title strip (Philippine permit fields: PEE name, PRC Reg. No. and validity, PTR No.,
  TIN, seal box), the revision block, legend, and general notes, with a non-plotting
  viewport onto model space at 1:1.
- Layers carry ACI colour and lineweight (plot with monochrome.ctb); linetypes are
  defined in millimetres so dashes survive any plot.

Line type encodes data status: CONTINUOUS = field-verified, E-ASSUMED (dashed) =
assumed, E-UNKNOWN (dotted) = unknown. Geometry is deterministic (geometry_digest()).
This engine draws what the topology says; it never sizes, rates, or infers equipment.
"""
import hashlib
import json
import re
import shutil
import textwrap
import xml.sax.saxutils as saxutils
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SHEETS_MM = {"20X30IN": (762.0, 508.0), "A3": (420.0, 297.0), "A2": (594.0, 420.0),
             "A1": (841.0, 594.0), "A0": (1189.0, 841.0)}
DEFAULT_SHEET = "20X30IN"
DEFAULT_REDUCTIONS = {"20X30IN": ["A3"]}

# Legibility floor on the SMALLEST plot (the A3 reduction of a 20x30 sheet): drawing
# text >= 1.8 mm (ISO 3098 practice), title-strip captions >= 1.6 mm. The sheet is laid
# out at that smallest size and scaled up exactly, so the full-size plot is larger
# still. Lineweights below are full-size pens chosen so they survive a ~55% reduction.

# name: (ACI colour, full-size lineweight in 1/100 mm, plots)
LAYERS = {
    "E-ONEL-EQPM": (7, 50, True),
    "E-ONEL-DEVC": (5, 50, True),
    "E-ONEL-COND": (7, 50, True),
    "E-ONEL-BUSS": (7, 100, True),
    "E-ONEL-GRND": (3, 35, True),
    "E-ANNO-TEXT": (7, 35, True),
    "E-ANNO-RISR": (8, 25, True),
    "E-ANNO-LGND": (7, 35, True),
    "E-ANNO-STMP": (1, 50, True),
    "G-ANNO-TTLB": (7, 35, True),
    "G-ANNO-BRDR": (7, 100, True),
    "G-ANNO-VPRT": (8, 18, False),
}
SVG_COLOR = {1: "#c62828", 3: "#1d7a2e", 5: "#1f4fbf", 7: "#111111", 8: "#888888"}

# Linetypes in full-size millimetres: (DXF pattern [total, dash, gap...], SVG dasharray).
# At a 55% reduction the assumed dash prints ~3.3 mm and the unknown dash ~0.55 mm.
LINETYPES = {
    "E-ASSUMED": ([9.0, 6.0, -3.0], "6 3", "Assumed data ____  ____  ____"),
    "E-UNKNOWN": ([3.0, 1.0, -2.0], "1 2", "Unknown data - - - - - - - -"),
}
STATUS_LINETYPE = {"verified": "CONTINUOUS", "assumed": "E-ASSUMED", "unknown": "E-UNKNOWN"}
TEXT_STYLE = "E-TEXT"
TEXT_FONT = "arial.ttf"

NODE_TYPES = ("utility", "generator", "transformer", "meter", "ct", "bus", "panel", "ats",
              "breaker", "fuse", "disconnect", "motor", "load", "ground")
DEVICE_TYPES = ("breaker", "fuse", "disconnect", "meter", "ct")
SYMBOL_LABEL = {
    "utility": "UTILITY SOURCE", "generator": "GENERATOR", "transformer": "TRANSFORMER",
    "meter": "KWH METER", "ct": "CURRENT TRANSFORMER", "panel": "PANELBOARD",
    "ats": "AUTOMATIC TRANSFER SWITCH", "breaker": "CIRCUIT BREAKER", "fuse": "FUSE",
    "disconnect": "DISCONNECT SWITCH", "motor": "MOTOR", "load": "LOAD", "ground": "GROUND",
}
MAX_DESC = 6
MAX_WRAPPED = 10
DESC_WRAP = 20
LEVEL_H_TAGGED = 30.0
TAG_R = 2.6

TXT = 2.5
TXT_SMALL = 1.8
TXT_CAPTION = 1.6
CHAR_W = 0.72
LEVEL_H = 48.0
NODE_GAP = 6.0
SYM = 10.0
TITLE_W = 80.0
FOOT_H = 58.0
STAMP_H = 14.0
STAMP = "DRAFT FOR PEE REVIEW - NOT FOR CONSTRUCTION"
VECTOR_GROUP = re.compile(r"^(D|Y|YN|Z|ZN)(d|y|yn|z|zn)(\d{1,2})?$")


@dataclass(frozen=True)
class Attr:
    tag: str
    text: str
    x: float
    y: float
    height: float
    layer: str
    align: str = "left"
    invisible: bool = False

    def moved(self, f=1.0, dx=0.0, dy=0.0):
        return Attr(self.tag, self.text, self.x * f + dx, self.y * f + dy, self.height * f,
                    self.layer, self.align, self.invisible)


@dataclass
class Prim:
    kind: str                      # line | circle | poly | text | insert
    layer: str
    pts: Tuple[float, ...]
    text: str = ""
    height: float = TXT
    align: str = "left"
    linetype: str = "BYLAYER"
    closed: bool = False
    block: str = ""
    attribs: Tuple[Attr, ...] = ()
    space: str = "model"

    def key(self):
        return (self.kind, self.layer, tuple(round(p, 3) for p in self.pts), self.text,
                round(self.height, 3), self.align, self.linetype, self.closed, self.block,
                tuple((a.tag, a.text, round(a.x, 3), round(a.y, 3), round(a.height, 3), a.layer,
                       a.align, a.invisible) for a in self.attribs), self.space)


@dataclass
class Drawing:
    sheet: str
    width: float
    height: float
    layout_name: str
    viewport: Tuple[float, float, float, float]
    prims: List[Prim] = field(default_factory=list)
    blocks: Dict[str, List[Prim]] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    reductions: Tuple[str, ...] = ()
    min_plot_scale: float = 1.0
    label_mode: str = "inline"
    sheets: Tuple[str, ...] = ()          # layout names; prims with space "paper<i>" belong to sheets[i]
    schedule_rows: int = 0


class DoesNotFit(ValueError):
    """The diagram cannot be drawn legibly on the requested sheet and reductions."""


_FONT_CACHE: Dict[float, object] = {}


def text_width(s: str, h: float) -> float:
    """Rendered width of s at cap height h in the drawing font, from real glyph metrics
    (ezdxf font manager). Falls back to a conservative estimate if the font is absent."""
    font = _FONT_CACHE.get(h)
    if font is None:
        try:
            from ezdxf.fonts import fonts
            font = fonts.make_font(TEXT_FONT, h)
        except Exception:
            font = False
        _FONT_CACHE[h] = font
    if font:
        return font.text_width(s)
    return len(s) * h * CHAR_W * 1.1


def _status(value: Optional[str]) -> str:
    v = (value or "verified").strip().lower()
    for key in ("verified", "assumed", "unknown"):
        if v.startswith(key):
            return key
    raise ValueError(f"unknown data status {value!r}; use verified, assumed, or unknown")


# ---------------------------------------------------------------- primitives

def _line(x1, y1, x2, y2, layer, lt="BYLAYER", space="model"):
    return [Prim("line", layer, (x1, y1, x2, y2), linetype=lt, space=space)]


def _circle(x, y, r, layer, lt="BYLAYER", space="model"):
    return [Prim("circle", layer, (x, y, r), linetype=lt, space=space)]


def _poly(points, layer, lt="BYLAYER", closed=True, space="model"):
    return [Prim("poly", layer, tuple(c for p in points for c in p), linetype=lt,
                 closed=closed, space=space)]


def _text(x, y, s, h=TXT, layer="E-ANNO-TEXT", align="left", space="model"):
    return [Prim("text", layer, (x, y), text=s, height=h, align=align, space=space)]


# ---------------------------------------------------------------- symbol blocks

def _block_name(kind: str, variant: str = "") -> str:
    return f"E-SYM-{kind.upper()}" + (f"-{variant.upper()}" if variant else "")


def _symbol_geometry(kind: str, variant: str = "") -> Tuple[List[Prim], float, float]:
    """Block geometry at the origin on layer 0. Returns (prims, top, bottom) — the
    connection offsets above and below the insertion point."""
    L, h = "0", SYM / 2
    p: List[Prim] = []
    if kind in ("utility", "generator", "motor"):
        letter = {"utility": "U", "generator": "G", "motor": "M"}[kind]
        return _circle(0, 0, h, L) + _text(0, -0.9, letter, TXT, L, "center"), h, -h
    if kind == "meter":
        return _circle(0, 0, h * 0.8, L) + _text(0, -0.6, "kWh", TXT_SMALL, L, "center"), h * 0.8, -h * 0.8
    if kind == "transformer":
        r = h * 0.75
        p += _circle(0, r * 0.6, r, L) + _circle(0, -r * 0.6, r, L)
        m = VECTOR_GROUP.match(variant) if variant else None
        if m:
            glyph = _winding_glyph(m.group(1), 0, r * 0.95) + _winding_glyph(m.group(2), 0, -r * 0.95)
            if m.group(2).endswith("n"):
                gx, gy = r * 1.35, -r * 0.95
                glyph += _line(0, gy, gx, gy, L) + _line(gx, gy, gx, gy - 2.0, L)
                glyph += _line(gx - 1.2, gy - 2.0, gx + 1.2, gy - 2.0, L)
                glyph += _line(gx - 0.7, gy - 2.6, gx + 0.7, gy - 2.6, L)
                glyph += _line(gx - 0.25, gy - 3.2, gx + 0.25, gy - 3.2, L)
            for g in glyph:
                g.linetype = "CONTINUOUS"
            p += glyph
        return p, r * 1.6, -r * 1.6
    if kind == "ct":
        return _circle(0, 0, h * 0.45, L) + _line(-h, 0, h, 0, L), h * 0.45, -h * 0.45
    if kind == "breaker":
        s = h * 0.7
        return _poly([(-s, -s), (s, -s), (s, s), (-s, s)], L), s, -s
    if kind == "fuse":
        w, t = h * 0.4, h * 0.9
        return _poly([(-w, -t), (w, -t), (w, t), (-w, t)], L) + _line(0, -t, 0, t, L), t, -t
    if kind == "disconnect":
        t = h * 0.9
        p += _circle(0, -t, 0.6, L) + _circle(0, t, 0.6, L) + _line(0, -t, t * 0.9, t * 0.7, L)
        return p, t, -t
    if kind == "ats":
        p += _poly([(-h * 1.3, -h), (h * 1.3, -h), (h * 1.3, h), (-h * 1.3, h)], L)
        return p + _text(0, -0.9, "ATS", TXT, L, "center"), h, -h
    if kind == "panel":
        w, t = h * 1.4, h * 0.8
        return _poly([(-w, -t), (w, -t), (w, t), (-w, t)], L) + _line(-w, -t, w, t, L), t, -t
    if kind == "load":
        return _poly([(-h * 0.7, h * 0.4), (h * 0.7, h * 0.4), (0, -h * 0.8)], L), h * 0.4, -h * 0.8
    if kind == "ground":
        p += _line(-h, 0, h, 0, L) + _line(-h * 0.6, -1.5, h * 0.6, -1.5, L)
        return p + _line(-h * 0.25, -3.0, h * 0.25, -3.0, L), 0.0, -3.0
    raise ValueError(f"no symbol for node type {kind!r}; supported: {', '.join(NODE_TYPES)}")


def _winding_glyph(code: str, cx: float, cy: float) -> List[Prim]:
    s = 1.3
    if code.upper().startswith("D"):
        return _poly([(cx - s, cy - s * 0.75), (cx + s, cy - s * 0.75), (cx, cy + s * 0.95)], "0")
    if code.upper().startswith("Y"):
        return (_line(cx, cy, cx, cy + s, "0") + _line(cx, cy, cx - s * 0.87, cy - s * 0.5, "0")
                + _line(cx, cy, cx + s * 0.87, cy - s * 0.5, "0"))
    return _poly([(cx - s, cy + s * 0.6), (cx, cy + s * 0.6), (cx, cy - s * 0.6), (cx + s, cy - s * 0.6)], "0", closed=False)


class _Symbols:
    def __init__(self):
        self.blocks: Dict[str, List[Prim]] = {}
        self.ports: Dict[str, Tuple[float, float]] = {}

    def get(self, kind: str, variant: str = "") -> Tuple[str, float, float]:
        name = _block_name(kind, variant)
        if name not in self.blocks:
            prims, top, bot = _symbol_geometry(kind, variant)
            self.blocks[name] = prims
            self.ports[name] = (top, bot)
        top, bot = self.ports[name]
        return name, top, bot


# ---------------------------------------------------------------- input model

def load_drawing_spec(spec: dict) -> dict:
    """Validate and normalise a drawing spec (see skill.md for the schema)."""
    nodes = {}
    for n in spec.get("nodes", []):
        if n["type"] not in NODE_TYPES:
            raise ValueError(f"node {n['id']}: unknown type {n['type']!r}")
        if n["id"] in nodes:
            raise ValueError(f"duplicate node id {n['id']!r}")
        raw = list(n.get("lines", []))
        if len(raw) > MAX_DESC:
            raise ValueError(f"node {n['id']}: {len(raw)} description lines; max {MAX_DESC}")
        lines = [w for line in raw for w in (textwrap.wrap(str(line), DESC_WRAP) or [""])]
        if len(lines) > MAX_WRAPPED:
            raise ValueError(f"node {n['id']}: description wraps to {len(lines)} lines; shorten it "
                             f"(max {MAX_WRAPPED} at {DESC_WRAP} characters)")
        conn = n.get("connection", "")
        if conn and (n["type"] != "transformer" or not VECTOR_GROUP.match(conn)):
            raise ValueError(f"node {n['id']}: connection {conn!r} must be an IEC vector group "
                             "(e.g. Dyn11, YNd1) on a transformer")
        nodes[n["id"]] = {**n, "status": _status(n.get("status")), "lines": lines, "connection": conn}
    edges = []
    for e in spec.get("edges", []):
        for end in ("from", "to"):
            if e[end] not in nodes:
                raise ValueError(f"edge {e['from']}->{e['to']}: unknown node {e[end]!r}")
        dev = e.get("device")
        if dev and dev["type"] not in DEVICE_TYPES:
            raise ValueError(f"edge {e['from']}->{e['to']}: unknown device {dev['type']!r}")
        edges.append({**e, "status": _status(e.get("status")), "kind": e.get("kind", "feeder")})
    if not nodes:
        raise ValueError("drawing spec has no nodes")
    tb = dict(spec.get("title_block", {}))
    for req in ("project", "drawing_title", "drawing_no", "revision", "date"):
        if not tb.get(req):
            raise ValueError(f"title_block.{req} is required")
    if not re.match(r"^[A-Za-z0-9._-]+$", tb["drawing_no"]):
        raise ValueError("title_block.drawing_no may contain only letters, digits, '.', '_', '-' "
                         "(it names the paper-space layout)")
    sheet = spec.get("sheet") or DEFAULT_SHEET
    if sheet not in SHEETS_MM:
        raise ValueError(f"sheet {sheet!r}; use one of {', '.join(SHEETS_MM)}")
    reductions = spec.get("reduce_to", DEFAULT_REDUCTIONS.get(sheet, []))
    for r in reductions:
        if r not in SHEETS_MM:
            raise ValueError(f"reduce_to {r!r}; use one of {', '.join(SHEETS_MM)}")
    return {"nodes": nodes, "edges": edges, "title_block": tb,
            "revisions": spec.get("revisions", []), "notes": spec.get("notes", []),
            "layout": spec.get("layout", "sld"), "floors": spec.get("floors"), "sheet": sheet,
            "reductions": list(reductions), "label_mode": _label_mode(spec.get("label_mode", "auto"))}


def _label_mode(mode: str) -> str:
    if mode not in ("auto", "inline", "tagged"):
        raise ValueError(f"label_mode {mode!r}; use auto, inline, or tagged")
    return mode


def plot_scale(sheet: str, reductions) -> float:
    """Smallest plot scale across the reductions (1.0 if none). A 20x30 in sheet reduced
    to A3 plots at min(420/762, 297/508) = 0.551."""
    W, H = SHEETS_MM[sheet]
    scales = [min(SHEETS_MM[r][0] / W, SHEETS_MM[r][1] / H) for r in reductions]
    return min([1.0] + scales)


TOPOLOGY_TYPE_MAP = {
    "utility_service_point": "utility", "main_panel": "panel", "tenant_subpanel": "panel",
    "subpanel": "panel", "panelboard": "panel", "grounding_electrode_system": "ground",
    "house_load_uncertain": "load", "load": "load", "transformer": "transformer",
    "generator": "generator", "ats": "ats", "meter": "meter", "motor": "motor", "bus": "bus",
}


def topology_status(text: Optional[str]) -> str:
    """Map as-built-agent's free-text field_verification_status to a drawing status.
    Only an explicit VERIFIED / FIELD-VERIFIED prefix counts as verified; an ASSUMED
    prefix is assumed; everything else (UNKNOWN, unconfirmed, not surveyed, missing)
    is unknown. Never promotes ambiguous text to verified."""
    t = (text or "").strip().upper()
    if t.startswith("VERIFIED") or t.startswith("FIELD-VERIFIED") or t.startswith("FIELD VERIFIED"):
        return "verified"
    if t.startswith("ASSUMED"):
        return "assumed"
    return "unknown"


def from_topology(topo: dict, title_block: dict) -> dict:
    """Adapter from as-built-agent's topology JSON (nodes/edges with
    field_verification_status) to a drawing spec. Unmapped node types raise — they are
    not silently drawn as a generic box."""
    nodes, edges = [], []
    for n in topo["nodes"]:
        t = TOPOLOGY_TYPE_MAP.get(n["type"])
        if t is None:
            raise ValueError(f"topology node {n['id']}: no drafting symbol mapped for type "
                             f"{n['type']!r}; add it to TOPOLOGY_TYPE_MAP")
        a = n.get("attributes", {})
        lines = []
        for k in ("rating_amps", "panel_rating_amps", "voltage", "phase", "floor", "metering"):
            if a.get(k) not in (None, ""):
                lines.append(f"{k.replace('_', ' ').upper()}: {a[k]}")
        node = {"id": n["id"], "type": t, "lines": lines[:MAX_DESC],
                "status": topology_status(n.get("field_verification_status"))}
        if a.get("floor"):
            node["floor"] = str(a["floor"])
        nodes.append(node)
    for e in topo["edges"]:
        et = e.get("type", "feeder")
        kind = "ground" if "ground" in et else "feeder"
        status = topology_status(e.get("field_verification_status"))
        if status == "verified" and ("possible" in et or "uncertain" in et):
            status = "assumed"
        edges.append({"from": e["from"], "to": e["to"], "kind": kind, "status": status,
                      "label": et.replace("_", " ") if kind == "feeder" and et != "feeder" else ""})
    meta = topo.get("_meta", {})
    tb = {**title_block}
    tb.setdefault("survey_date", meta.get("survey_date"))
    return {"title_block": tb, "nodes": nodes, "edges": edges,
            "notes": [meta["survey_basis"]] if meta.get("survey_basis") else [], "layout": "sld"}


# ---------------------------------------------------------------- layout

def _tree(spec):
    nodes, edges = spec["nodes"], spec["edges"]
    parent: Dict[str, dict] = {}
    secondary: List[dict] = []
    for e in edges:
        if e["to"] in parent or e["to"] == e["from"]:
            secondary.append(e)
        else:
            parent[e["to"]] = e
    children: Dict[str, List[str]] = {nid: [] for nid in nodes}
    for child, e in parent.items():
        children[e["from"]].append(child)
    fed_twice = {e["to"] for e in secondary}
    for nid in children:
        children[nid].sort(key=lambda c: c in fed_twice)
    roots = [nid for nid in nodes if nid not in parent]
    seen, cyc = set(), []

    def walk(n, stack):
        if n in stack:
            cyc.append(n)
            return
        if n in seen:
            return
        seen.add(n)
        for c in children[n]:
            walk(c, stack | {n})
    for r in roots:
        walk(r, frozenset())
    if cyc or len(seen) != len(nodes):
        raise ValueError("topology has a cycle or nodes unreachable from any source; "
                         "an SLD needs every node fed from a root")
    return parent, children, roots, secondary


def _label_texts(n):
    texts = [(n["id"], TXT)] + [(t, TXT_SMALL) for t in n["lines"]]
    if n["status"] != "verified":
        texts.append((f"({n['status'].upper()})", TXT_SMALL))
    return texts


def _label_place(n, has_children, has_sec_out, tagged, riser):
    """Where a node's label block goes. Inline mode keeps every label to the right.
    Tagged mode centres a leaf's label below it on a one-line (above it on a riser,
    where the feeder enters from below), so a column is only as wide as its label."""
    if n["type"] == "bus" or not tagged or has_children or has_sec_out:
        return "right"
    return "above" if riser else "below"


def _extents(n, in_edge, out_secondary, place, tagged):
    """(left, right) space a node column needs around its conductor centreline, so
    neighbouring columns never collide."""
    if n["type"] == "bus":
        return 6.0, 6.0
    label_w = max(text_width(s, h) for s, h in _label_texts(n))
    tag_w = SYM * 0.9 + 2 * TAG_R + 1.0
    min_left = SYM * 0.8 if tagged else SYM * 1.4
    if place in ("below", "above"):
        half = label_w / 2 + 1.0
        left, right = max(min_left, half), max(min_left, half)
    else:
        left, right = min_left, SYM * 1.6 + label_w
    edges = ([in_edge] if in_edge else []) + out_secondary
    if tagged:
        if any(e.get("device") or e.get("label") for e in edges):
            right = max(right, tag_w)
        return left + 1.0, right + 1.0
    for e in edges:
        dev = e.get("device")
        if dev and dev.get("label"):
            right = max(right, SYM * 0.9 + text_width(dev["label"], TXT_SMALL))
    if in_edge and in_edge.get("label"):
        left = max(left, 1.5 + text_width(in_edge["label"], TXT_SMALL))
    for e in out_secondary:
        if e.get("label"):
            right = max(right, 1.5 + text_width(e["label"], TXT_SMALL))
    return left + 1.0, right + 1.0


def _layout_positions(spec, tagged):
    nodes = spec["nodes"]
    riser = spec["layout"] == "riser"
    level_h = LEVEL_H_TAGGED if tagged else LEVEL_H
    parent, children, roots, secondary = _tree(spec)
    sec_out = {nid: [e for e in secondary if e["from"] == nid] for nid in nodes}
    sec_in = {e["to"] for e in secondary}
    place_of = {nid: _label_place(nodes[nid], bool(children[nid]), bool(sec_out[nid]) or nid in sec_in,
                                  tagged, riser)
                for nid in nodes}
    rel: Dict[str, float] = {}
    depth: Dict[str, int] = {}

    def measure(n, d):
        """Pack children left to right using their real extents; centre the parent over
        them. Returns the subtree's (left, right) extents relative to n."""
        depth[n] = d
        own_l, own_r = _extents(nodes[n], parent.get(n), sec_out[n], place_of[n], tagged)
        kids = children[n]
        if not kids:
            return own_l, own_r
        kid_ext = [measure(c, d + 1) for c in kids]
        pos = [0.0]
        for i in range(1, len(kids)):
            pos.append(pos[-1] + kid_ext[i - 1][1] + NODE_GAP + kid_ext[i][0])
        centre = (pos[0] + pos[-1]) / 2 if nodes[n]["type"] == "bus" or len(kids) > 1 else pos[0]
        for c, p in zip(kids, pos):
            rel[c] = p - centre
        left = max([own_l] + [kl - rel[c] for c, (kl, _) in zip(kids, kid_ext)])
        right = max([own_r] + [kr + rel[c] for c, (_, kr) in zip(kids, kid_ext)])
        return left, right

    xpos: Dict[str, float] = {}

    def place(n, x):
        xpos[n] = x
        for c in children[n]:
            place(c, x + rel[c])

    tree_roots = [r for r in roots if children[r]]
    side_roots = [r for r in roots if not children[r]]
    cursor = 0.0
    for r in tree_roots:
        left, right = measure(r, 0)
        place(r, cursor + left)
        cursor += left + right + NODE_GAP * 2
    for r in side_roots:
        left, right = measure(r, 0)
        targets = [e["to"] for e in sec_out[r]]
        if targets:
            depth[r] = max(0, min(depth[t] for t in targets) - 1)
        xpos[r] = cursor + left
        cursor += left + right + NODE_GAP * 2

    floor_y = None
    if riser:
        floors = spec["floors"] or sorted({n.get("floor") for n in nodes.values() if n.get("floor")})
        if not floors:
            raise ValueError("riser layout needs 'floor' on nodes or a 'floors' list")
        for nid, n in nodes.items():
            if n.get("floor") not in floors:
                raise ValueError(f"node {nid}: riser layout needs a floor from {floors}, got {n.get('floor')!r}")
        ypos, floor_y, base = {}, {}, 0.0
        for f in floors:
            members = [nid for nid, n in nodes.items() if n["floor"] == f]
            ranks = {d: i for i, d in enumerate(sorted({depth[m] for m in members}))}
            floor_y[f] = base - level_h * 0.4
            for m in members:
                ypos[m] = base + ranks[depth[m]] * level_h
            base += max(1, len(ranks)) * level_h
    else:
        maxd = max(depth.values())
        ypos = {nid: (maxd - d) * level_h for nid, d in depth.items()}
    return xpos, ypos, parent, children, secondary, floor_y, place_of


# ---------------------------------------------------------------- diagram assembly

def _insert(sym: _Symbols, kind, variant, x, y, layer, lt, attrs):
    name, top, bot = sym.get(kind, variant)
    return [Prim("insert", layer, (x, y), block=name, linetype=lt, attribs=tuple(attrs))], y + top, y + bot


def _node_attrs(n, x, y, place="right", top=0.0, bot=0.0, bus_left=None):
    texts = [("TAG", n["id"], TXT, "E-ANNO-TEXT")]
    texts += [(f"DESC{i}", line, TXT_SMALL, "E-ANNO-TEXT") for i, line in enumerate(n["lines"], 1)]
    if n["status"] != "verified":
        texts.append(("STATUS", f"({n['status'].upper()})", TXT_SMALL, "E-ANNO-STMP"))
    if bus_left is not None:
        tx, ty, align = bus_left - 2.0, y + 1.0, "right"
    elif place == "below":
        tx, ty, align = x, bot - 1.5 - TXT, "center"
    elif place == "above":
        tx, align = x, "center"
        ty = top + 1.5 + sum(h * 1.5 for _, _, h, _ in texts[1:])
    else:
        tx, ty, align = x + SYM * 1.6, y + 1.0, "left"
    attrs = []
    for i, (tag, s, h, layer) in enumerate(texts):
        if i == 1:
            ty -= 3.4 if align != "center" else TXT_SMALL * 1.6
        elif i > 1:
            ty -= TXT_SMALL * 1.5
        attrs.append(Attr(tag, s, tx, ty, h, layer, align))
    return attrs


def _tag_bubble(tag, x, y):
    return (_circle(x, y, TAG_R, "E-ANNO-TEXT")
            + _text(x, y - TXT_SMALL / 2, tag, TXT_SMALL, align="center"))


def _edge_prims(sym, e, x1, y_from, x2, y_to, tag=None):
    layer = "E-ONEL-GRND" if e["kind"] == "ground" else "E-ONEL-COND"
    lt = STATUS_LINETYPE[e["status"]]
    out: List[Prim] = []
    sgn = 1.0 if y_to > y_from else -1.0
    ymid = y_from + (y_to - y_from) * 0.35
    if e["kind"] == "ground":
        ymid += sgn * 3.0
    bend = abs(x1 - x2) >= 0.01
    dev = e.get("device")
    dy = None
    if dev:
        if not bend and abs(y_to - y_from) > LEVEL_H_TAGGED * 1.2:
            dy = y_from + sgn * 12.0
        else:
            dy = (ymid + y_to) / 2 if bend else (y_from + y_to) / 2
        lx = x2 + SYM * 0.9
        attrs = [Attr("TAG", tag or dev.get("tag", ""), lx, dy + 1.0, TXT_SMALL, "E-ANNO-TEXT",
                      invisible=True)] if (tag or dev.get("tag")) else []
        if dev.get("label"):
            attrs.append(Attr("DESC1", dev["label"], lx, dy - 0.8, TXT_SMALL, "E-ANNO-TEXT",
                              invisible=bool(tag)))
        ins, dtop, dbot = _insert(sym, dev["type"], "", x2, dy, "E-ONEL-DEVC", lt, attrs)
        near, far = (dbot, dtop) if y_to > y_from else (dtop, dbot)
        seg = [(x1, y_from), (x1, ymid), (x2, ymid), (x2, near)] if bend else [(x2, y_from), (x2, near)]
        out += _poly(seg, layer, lt, closed=False) + _line(x2, far, x2, y_to, layer, lt) + ins
    else:
        seg = [(x1, y_from), (x1, ymid), (x2, ymid), (x2, y_to)] if bend else [(x1, y_from), (x2, y_to)]
        out += _poly(seg, layer, lt, closed=False)
    if tag:
        by = dy if dev else ((ymid + y_to) / 2 if bend else (y_from + y_to) / 2)
        out += _tag_bubble(tag, x2 + SYM * 0.9 + TAG_R, by)
    elif e.get("label"):
        ly = (y_to + dy) / 2 if dev else (ymid + y_to) / 2
        out += _text(x2 - 1.5, ly, e["label"], TXT_SMALL, align="right")
    return out


def _secondary_edge_prims(sym, e, x1, y_from, x2, y_to, same_level=False, y_floor=0.0, tag=None):
    """Second feed into a node that already has a primary feed (ATS emergency side, a
    tie). The device sits at the source, where an SLD shows the source breaker; a tie
    between two nodes on one level runs clear of the feeder junction."""
    layer = "E-ONEL-GRND" if e["kind"] == "ground" else "E-ONEL-COND"
    lt = STATUS_LINETYPE[e["status"]]
    out: List[Prim] = []
    if same_level:
        y_run = y_floor - 10.0 if y_floor <= y_from else y_floor + 10.0
        out += _poly([(x1, y_from), (x1, y_run), (x2, y_run), (x2, y_to)], layer, lt, closed=False)
        if tag:
            out += _tag_bubble(tag, (x1 + x2) / 2, y_run + TAG_R + 0.8)
        elif e.get("label"):
            out += _text((x1 + x2) / 2, y_run + 1.2, e["label"], TXT_SMALL, align="center")
        return out
    up = y_to > y_from
    sgn = 1.0 if up else -1.0
    y_run = y_to - sgn * 6.0
    x_drop = x2 + SYM * 0.6
    y_cur = y_from
    dev = e.get("device")
    dy = (y_from + y_run) / 2
    if dev:
        lx = x1 + SYM * 0.9
        attrs = [Attr("TAG", tag, lx, dy + 1.0, TXT_SMALL, "E-ANNO-TEXT", invisible=True)] if tag else []
        if dev.get("label"):
            attrs.append(Attr("DESC1", dev["label"], lx, dy - 0.8, TXT_SMALL, "E-ANNO-TEXT",
                              invisible=bool(tag)))
        ins, dtop, dbot = _insert(sym, dev["type"], "", x1, dy, "E-ONEL-DEVC", lt, attrs)
        near, far = (dbot, dtop) if up else (dtop, dbot)
        out += _line(x1, y_from, x1, near, layer, lt) + ins
        y_cur = far
    out += _poly([(x1, y_cur), (x1, y_run), (x_drop, y_run), (x_drop, y_to)], layer, lt, closed=False)
    if tag:
        out += _tag_bubble(tag, x1 + SYM * 0.9 + TAG_R, dy)
    elif e.get("label"):
        out += _text(x1 + 1.5, (y_cur + y_run) / 2, e["label"], TXT_SMALL, align="left")
    return out


def _text_box(x, y, s, h, align):
    w = text_width(s, h)
    x0 = x - w if align == "right" else (x - w / 2 if align == "center" else x)
    return x0, y - h * 0.25, x0 + w, y + h


def _bbox(prims, blocks):
    xs, ys = [], []
    for p in prims:
        if p.kind == "circle":
            x, y, r = p.pts
            xs += [x - r, x + r]
            ys += [y - r, y + r]
        elif p.kind == "text":
            b = _text_box(p.pts[0], p.pts[1], p.text, p.height, p.align)
            xs += [b[0], b[2]]
            ys += [b[1], b[3]]
        elif p.kind == "insert":
            bx0, by0, bx1, by1 = _bbox(blocks[p.block], blocks)
            xs += [p.pts[0] + bx0, p.pts[0] + bx1]
            ys += [p.pts[1] + by0, p.pts[1] + by1]
            for a in p.attribs:
                if a.invisible:
                    continue
                b = _text_box(a.x, a.y, a.text, a.height, a.align)
                xs += [b[0], b[2]]
                ys += [b[1], b[3]]
        else:
            xs += list(p.pts[0::2])
            ys += list(p.pts[1::2])
    return min(xs), min(ys), max(xs), max(ys)


def _translate(prims, dx, dy):
    out = []
    for p in prims:
        if p.kind == "circle":
            pts = (p.pts[0] + dx, p.pts[1] + dy, p.pts[2])
        else:
            pts = tuple(v + (dx if i % 2 == 0 else dy) for i, v in enumerate(p.pts))
        out.append(Prim(p.kind, p.layer, pts, p.text, p.height, p.align, p.linetype, p.closed,
                        p.block, tuple(a.moved(1.0, dx, dy) for a in p.attribs), p.space))
    return out


def _scale(prims, f):
    """Uniform scale about the origin: coordinates, radii, text and attribute heights."""
    if f == 1.0:
        return list(prims)
    out = []
    for p in prims:
        if p.kind == "circle":
            pts = (p.pts[0] * f, p.pts[1] * f, p.pts[2] * f)
        else:
            pts = tuple(v * f for v in p.pts)
        out.append(Prim(p.kind, p.layer, pts, p.text, p.height * f, p.align, p.linetype, p.closed,
                        p.block, tuple(a.moved(f) for a in p.attribs), p.space))
    return out


def _respace(prims, space):
    return [Prim(p.kind, p.layer, p.pts, p.text, p.height, p.align, p.linetype, p.closed,
                 p.block, p.attribs, space) for p in prims]


def _feeder_tags(spec, parent, secondary):
    """Stable feeder tags (F1, F2, ...) in spec edge order, for every edge that carries a
    device or a conductor label. An explicit edge 'tag' wins."""
    tags, i = {}, 0
    for e in spec["edges"]:
        if e.get("device") or e.get("label"):
            i += 1
            tags[id(e)] = e.get("tag") or f"F{i}"
    return tags


def _schedule_rows(spec, tags):
    rows = []
    for e in spec["edges"]:
        if id(e) not in tags:
            continue
        dev = e.get("device") or {}
        prot = dev.get("label") or (dev.get("type", "").upper() if dev else "-")
        rows.append((tags[id(e)], e["from"], e["to"], prot, e.get("label") or "-",
                     "" if e["status"] == "verified" else e["status"].upper()))
    return rows


SCHEDULE_HEAD = ("TAG", "FROM", "TO", "PROTECTION", "CONDUCTOR", "STATUS")


def _schedule_size(rows):
    cols = [max([text_width(h, TXT_CAPTION)] + [text_width(r[i], TXT_SMALL) for r in rows]) + 3.0
            for i, h in enumerate(SCHEDULE_HEAD)]
    return cols, sum(cols), 6.0 + 5.0 * (len(rows) + 1)


def _schedule_prims(rows, x0, ytop, space):
    """FEEDER SCHEDULE table with its top-left corner at (x0, ytop)."""
    cols, w, h = _schedule_size(rows)
    p = _text(x0, ytop - 4.0, "FEEDER SCHEDULE", TXT, "E-ANNO-LGND", space=space)
    y = ytop - 6.0
    row_h = 5.0
    p += _poly([(x0, y), (x0 + w, y), (x0 + w, y - row_h * (len(rows) + 1)), (x0, y - row_h * (len(rows) + 1))],
               "G-ANNO-TTLB", space=space)
    for r_i, row in enumerate([SCHEDULE_HEAD] + rows):
        ry = y - row_h * (r_i + 1)
        if r_i:
            p += _line(x0, ry + row_h, x0 + w, ry + row_h, "G-ANNO-TTLB", space=space)
        cx = x0
        for c_i, v in enumerate(row):
            layer = "E-ANNO-STMP" if (c_i == 5 and r_i and v) else "E-ANNO-LGND"
            p += _text(cx + 1.5, ry + 1.5, v, TXT_CAPTION if r_i == 0 else TXT_SMALL, layer, space=space)
            cx += cols[c_i]
    cx = x0
    for c in cols[:-1]:
        cx += c
        p += _line(cx, y, cx, y - row_h * (len(rows) + 1), "G-ANNO-TTLB", space=space)
    return p


def _assemble(spec, tagged) -> Tuple[List[Prim], Dict[str, List[Prim]], dict]:
    """Model-space diagram at design (smallest-plot) size, origin arbitrary."""
    nodes = spec["nodes"]
    riser = spec["layout"] == "riser"
    xpos, ypos, parent, children, secondary, floor_y, place_of = _layout_positions(spec, tagged)
    tags = _feeder_tags(spec, parent, secondary) if tagged else {}
    sym = _Symbols()
    body: List[Prim] = []
    ports = {}
    for nid, n in nodes.items():
        lt = STATUS_LINETYPE[n["status"]]
        if n["type"] == "bus":
            kids = children[nid] + [e["to"] for e in secondary if e["from"] == nid]
            xs = [xpos[nid]] + [xpos[k] for k in kids]
            x0, x1, y = min(xs) - 6, max(xs) + 6, ypos[nid]
            body += _line(x0, y, x1, y, "E-ONEL-BUSS", lt)
            body += [Prim("text", a.layer, (a.x, a.y), text=a.text, height=a.height, align=a.align)
                     for a in _node_attrs(n, 0, y, bus_left=x0)]
            ports[nid] = (y, y)
            continue
        layer = "E-ONEL-GRND" if n["type"] == "ground" else "E-ONEL-EQPM"
        _, top_off, bot_off = sym.get(n["type"], n["connection"])
        y = ypos[nid]
        ins, top, bot = _insert(sym, n["type"], n["connection"], xpos[nid], y, layer, lt,
                                _node_attrs(n, xpos[nid], y, place_of[nid], y + top_off, y + bot_off))
        body += ins
        ports[nid] = (top, bot)

    def out_port(nid):
        if nodes[nid]["type"] == "bus":
            return ypos[nid]
        return ports[nid][0] if riser else ports[nid][1]

    def in_port(nid):
        return ports[nid][1] if riser else ports[nid][0]

    for child, e in parent.items():
        src = e["from"]
        x_from = xpos[child] if nodes[src]["type"] == "bus" else xpos[src]
        body += _edge_prims(sym, e, x_from, out_port(src), xpos[child], in_port(child), tags.get(id(e)))
    for e in secondary:
        src, dst = e["from"], e["to"]
        tag = tags.get(id(e))
        if abs(ypos[src] - ypos[dst]) < 0.01:
            if riser:
                y_edge = max(ports[src][0], ports[dst][0], ypos[src] + TXT + 2.0)
                body += _secondary_edge_prims(sym, e, xpos[src], ports[src][0], xpos[dst], ports[dst][0],
                                              same_level=True, y_floor=y_edge, tag=tag)
            else:
                n_lines = max(len(_label_texts(nodes[src])), len(_label_texts(nodes[dst])))
                text_floor = ypos[src] - 2.4 - TXT_SMALL * 1.5 * n_lines
                y_edge = min(ports[src][1], ports[dst][1], text_floor)
                body += _secondary_edge_prims(sym, e, xpos[src], ports[src][1], xpos[dst], ports[dst][1],
                                              same_level=True, y_floor=y_edge, tag=tag)
        else:
            body += _secondary_edge_prims(sym, e, xpos[src], out_port(src), xpos[dst], in_port(dst), tag=tag)
    if riser:
        bx0, _, bx1, _ = _bbox(body, sym.blocks)
        for f, yl in floor_y.items():
            body += _line(bx0 - 24, yl, bx1 + 10, yl, "E-ANNO-RISR", "E-ASSUMED")
            body += _text(bx0 - 24, yl + 1.5, f"FLOOR {f}", TXT, layer="E-ANNO-RISR")
    return body, sym.blocks, {"rows": _schedule_rows(spec, tags), "sym": sym}


def _place(spec, tagged):
    """Assemble at design size and fit it, with any feeder schedule, onto the smallest
    plot. Returns (Drawing at full size) or raises DoesNotFit."""
    sheet, reductions = spec["sheet"], tuple(spec["reductions"])
    W, H = SHEETS_MM[sheet]
    s = plot_scale(sheet, reductions)
    Wd, Hd = W * s, H * s
    body, blocks, extra = _assemble(spec, tagged)
    rows, sym = extra["rows"], extra["sym"]
    bx0, by0, bx1, by1 = _bbox(body, blocks)
    dw, dh = bx1 - bx0 + 8, by1 - by0 + 8
    ax0, ay0 = 20.0, 10.0 + FOOT_H
    ax1, ay1 = Wd - 10.0 - TITLE_W, Hd - 10.0 - STAMP_H
    aw, ah = ax1 - ax0, ay1 - ay0
    smallest = reductions[-1] if reductions else sheet
    if dw > aw or dh > ah:
        raise DoesNotFit(
            f"diagram needs {dw:.0f} x {dh:.0f} mm at legible size on the {smallest} plot, "
            f"but that plot's drawing area is {aw:.0f} x {ah:.0f} mm. Split it into sheets "
            "(e.g. one per bus), shorten labels, or drop the reduction with \"reduce_to\": [].")

    schedule_at, second_sheet = None, False
    if rows:
        _, sw, sh = _schedule_size(rows)
        if sw > aw - 6 or sh > ah - 6:
            raise DoesNotFit(f"feeder schedule ({sw:.0f} x {sh:.0f} mm) does not fit the {smallest} "
                             "plot's drawing area; split the diagram into sheets")
        if dw + 6 + sw <= aw:
            vp = (ax0, ay0, ax1 - sw - 6, ay1)
            schedule_at = (ax1 - sw - 3, ay1 - 3)
        elif dh + 6 + sh <= ah:
            vp = (ax0, ay0, ax1, ay1 - sh - 6)
            schedule_at = (ax0 + 3, ay1 - 3)
        else:
            vp = (ax0, ay0, ax1, ay1)
            schedule_at, second_sheet = (ax0 + 3, ay1 - 3), True
    else:
        vp = (ax0, ay0, ax1, ay1)
    vx0, vy0, vx1, vy1 = vp
    dx = vx0 + ((vx1 - vx0) - (bx1 - bx0)) / 2 - bx0
    dy = vy0 + ((vy1 - vy0) - (by1 - by0)) / 2 - by0

    name = spec["title_block"]["drawing_no"]
    sheets = (name, f"{name}-FS") if second_sheet else (name,)
    d = Drawing(sheet=sheet, width=W, height=H, layout_name=name,
                viewport=(vx0 / s, vy0 / s, vx1 / s, vy1 / s), reductions=reductions, min_plot_scale=s,
                label_mode="tagged" if tagged else "inline", sheets=sheets, schedule_rows=len(rows))
    paper: List[Prim] = []
    if second_sheet:
        tb = spec["title_block"]
        s1 = {**spec, "title_block": {**tb, "sheet": "1 OF 2"}}
        s2 = {**spec, "title_block": {**tb, "sheet": "2 OF 2", "drawing_no": f"{name}-FS",
                                       "drawing_title": f"FEEDER SCHEDULE - {tb['drawing_title']}"}}
        paper += _sheet_frame(s1, sym, Wd, Hd, d)
        paper += _respace(_sheet_frame(s2, sym, Wd, Hd, d, legend=False)
                          + _schedule_prims(rows, *schedule_at, space="paper"), "paper1")
    else:
        paper += _sheet_frame(spec, sym, Wd, Hd, d)
        if rows:
            paper += _schedule_prims(rows, *schedule_at, space="paper")
    d.prims = _scale(_translate(body, dx, dy) + paper, 1 / s)
    d.blocks = {k: _scale(v, 1 / s) for k, v in sym.blocks.items()}
    d.warnings = list(dict.fromkeys(d.warnings))
    return d


def build_drawing(spec_in: dict) -> Drawing:
    """Lay the sheet out at its smallest plotted size (every text height is its printed
    height on the reduction), then scale it up exactly to the sheet. label_mode 'auto'
    uses inline labels when they fit without collisions, else feeder tags + schedule."""
    spec = load_drawing_spec(spec_in)
    mode = spec["label_mode"]
    if mode in ("auto", "inline"):
        try:
            d = _place(spec, tagged=False)
            if mode == "inline" or not text_overlaps(d):
                return d
        except DoesNotFit:
            if mode == "inline":
                raise
    return _place(spec, tagged=True)


# ---------------------------------------------------------------- sheet (paper space)

def _ptext(x, y, s, h, layer="G-ANNO-TTLB", align="left"):
    return _text(x, y, s, h, layer, align, space="paper")


def _box(x0, y0, x1, y1, layer="G-ANNO-TTLB"):
    return _poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer, space="paper")


def _wrap_width(s: str, width: float, h: float, indent: str = "") -> List[str]:
    """Greedy word wrap by real glyph width (not character count)."""
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}" if cur else (indent + word if lines else word)
        if cur and text_width(trial, h) > width:
            lines.append(cur)
            cur = indent + word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def _fit(s: str, width: float, h: float) -> str:
    """Truncate s so it fits width at text height h (real glyph widths)."""
    while s and text_width(s, h) > width:
        s = s[:-1]
    return s


def _field(x0, y0, w, h, label, value):
    """One title-strip cell: small label top-left, value wrapped below. Returns prims."""
    p = _box(x0, y0, x0 + w, y0 + h) + _ptext(x0 + 1.2, y0 + h - 2.2, label, TXT_CAPTION)
    max_chars = max(8, int((w - 2.4) / (2.0 * CHAR_W)))
    lines = textwrap.wrap(str(value), max_chars) or [""]
    ty = y0 + h - 5.2
    for line in lines[: max(1, int((h - 3.5) // 2.8))]:
        p += _ptext(x0 + 1.2, ty, line, 2.0)
        ty -= 2.8
    return p


def _sheet_frame(spec, sym: _Symbols, W, H, d: Drawing, legend: bool = True) -> List[Prim]:
    tb = spec["title_block"]
    pee = tb.get("pee", {}) or {}
    blank = "_______________________"
    p: List[Prim] = []
    p += _box(0, 0, W, H, "G-ANNO-BRDR") + _box(20, 10, W - 10, H - 10, "G-ANNO-BRDR")
    p += _ptext((20 + W - 10 - TITLE_W) / 2, H - 10 - STAMP_H + 4.5, STAMP, 5.0, "E-ANNO-STMP", "center")

    x0, x1 = W - 10 - TITLE_W, W - 10
    tw = x1 - x0
    p += _line(x0, 10, x0, H - 10, "G-ANNO-BRDR", space="paper")
    survey = tb.get("survey_date") or "NONE - NOT FIELD-VERIFIED"
    if not tb.get("survey_date"):
        d.warnings.append("no survey_date: drawing is not versioned against a field survey")

    y = 10.0
    p += _field(x0, y, tw * 0.62, 14, "DRAWING NO.", tb["drawing_no"])
    p += _field(x0 + tw * 0.62, y, tw * 0.38, 14, "SHEET", tb.get("sheet", "1 OF 1"))
    y += 14
    p += _field(x0, y, tw / 2, 8, "REVISION", tb["revision"])
    p += _field(x0 + tw / 2, y, tw / 2, 8, "SCALE", tb.get("scale", "NTS"))
    y += 8
    p += _field(x0, y, tw / 2, 8, "DATE", tb["date"])
    p += _field(x0 + tw / 2, y, tw / 2, 8, "SURVEY DATE", survey)
    y += 8
    p += _field(x0, y, tw / 2, 8, "DRAWN BY", tb.get("drawn_by", "-"))
    p += _field(x0 + tw / 2, y, tw / 2, 8, "CHECKED BY", tb.get("checked_by", "-"))
    y += 8
    p += _field(x0, y, tw, 14, "SHEET CONTENTS / DRAWING TITLE", tb["drawing_title"])
    y += 14
    p += _field(x0, y, tw, 11, "LOCATION", tb.get("location") or blank)
    y += 11
    p += _field(x0, y, tw, 11, "OWNER", tb.get("owner") or tb.get("client") or blank)
    y += 11
    p += _field(x0, y, tw, 14, "PROJECT", tb["project"])
    y += 14

    pee_rows = [("TIN", pee.get("tin") or blank),
                ("PTR NO. / DATE / PLACE ISSUED", pee.get("ptr") or blank),
                ("PRC REG. NO. / VALIDITY", pee.get("prc") or blank),
                ("PROFESSIONAL ELECTRICAL ENGINEER", pee.get("name") or blank)]
    for label, value in pee_rows:
        p += _field(x0, y, tw, 8, label, value)
        y += 8
    seal_h = 52.0
    p += _box(x0, y, x1, y + seal_h)
    p += _ptext(x0 + tw / 2, y + seal_h - 4, "SIGNED AND SEALED BY", 1.8, align="center")
    p += _ptext(x0 + tw / 2, y + seal_h - 6.8, "PROFESSIONAL ELECTRICAL ENGINEER (RA 7920)", TXT_CAPTION, align="center")
    p += _circle(x0 + tw / 2, y + seal_h / 2 - 3, 18, "G-ANNO-TTLB", space="paper")
    p += _ptext(x0 + tw / 2, y + seal_h / 2 - 4, "NOT SEALED", 3.0, "E-ANNO-STMP", "center")
    y += seal_h

    p += _box(x0, y, x1, y + 10, "E-ANNO-STMP")
    p += _ptext(x0 + tw / 2, y + 5.6, "DRAFT FOR PEE REVIEW", 2.4, "E-ANNO-STMP", "center")
    p += _ptext(x0 + tw / 2, y + 2.2, "NOT FOR CONSTRUCTION", 2.4, "E-ANNO-STMP", "center")
    y += 10

    revs = spec["revisions"] or [{"rev": tb["revision"], "date": tb["date"],
                                  "description": "DRAFT FOR PEE REVIEW", "by": tb.get("drawn_by", "-")}]
    row = 5.0
    top_limit = H - 10 - 6
    max_rows = int((top_limit - y - row) // row)
    if len(revs) > max_rows:
        d.warnings.append(f"{len(revs)} revisions; only the latest {max_rows} fit in the revision block")
        revs = revs[-max_rows:]
    cols = (x0, x0 + 9, x0 + 27, x0 + tw - 12)
    p += _box(x0, y, x1, y + row * (len(revs) + 1))
    for i, r in enumerate(revs):
        ry = y + i * row
        p += _line(x0, ry + row, x1, ry + row, "G-ANNO-TTLB", space="paper")
        vals = (str(r.get("rev", "")), str(r.get("date", "")),
                _fit(str(r.get("description", "")), cols[3] - cols[2] - 2, TXT_SMALL),
                _fit(str(r.get("by", "")), tw - (cols[3] - x0) - 2, TXT_SMALL))
        for cx, v in zip(cols, vals):
            p += _ptext(cx + 1, ry + 1.4, v, TXT_SMALL)
    hy = y + row * len(revs)
    for cx, v in zip(cols, ("REV", "DATE", "DESCRIPTION", "BY")):
        p += _ptext(cx + 1, hy + 1.4, v, TXT_CAPTION)
    for cx in cols[1:]:
        p += _line(cx, y, cx, hy + row, "G-ANNO-TTLB", space="paper")
    p += _ptext(x0 + 1, hy + row + 1.5, "REVISIONS", 2.0)
    if not legend:
        return p

    fx1 = x0
    p += _line(20, 10 + FOOT_H, fx1, 10 + FOOT_H, "G-ANNO-BRDR", space="paper")
    used = sorted({n["type"] for n in spec["nodes"].values() if n["type"] != "bus"} |
                  {e["device"]["type"] for e in spec["edges"] if e.get("device")})
    lx, ly = 24.0, 10 + FOOT_H - 6
    p += _ptext(lx, ly, "LEGEND", 2.5, "E-ANNO-LGND")
    col_w, row_h, per_col = 58.0, 11.0, 4
    for i, kind in enumerate(used):
        cx = lx + 6 + (i // per_col) * col_w
        cy = ly - 9 - (i % per_col) * row_h
        name, _, _ = sym.get(kind)
        p += [Prim("insert", "E-ANNO-LGND", (cx, cy), block=name, space="paper")]
        p += _ptext(cx + 9, cy - 0.8, SYMBOL_LABEL[kind], 1.8, "E-ANNO-LGND")
    sx0 = lx + ((len(used) - 1) // per_col + 1) * col_w
    for i, (status, lt) in enumerate(STATUS_LINETYPE.items()):
        yy = ly - 9 - i * row_h
        p += _line(sx0, yy, sx0 + 16, yy, "E-ANNO-LGND", lt, space="paper")
        p += _ptext(sx0 + 19, yy - 0.8, f"{status.upper()} DATA", 1.8, "E-ANNO-LGND")
    yy = ly - 9 - 3 * row_h
    p += _line(sx0, yy, sx0 + 16, yy, "E-ONEL-BUSS", space="paper")
    p += _ptext(sx0 + 19, yy - 0.8, "BUS", 1.8, "E-ANNO-LGND")

    W_full, H_full = SHEETS_MM[spec["sheet"]]
    size = "20 X 30 IN" if spec["sheet"] == "20X30IN" else spec["sheet"]
    plot_note = f"ORIGINAL SHEET SIZE {size} ({W_full:.0f} X {H_full:.0f} MM)."
    if spec["reductions"]:
        plot_note += (f" LETTERING SIZED TO REMAIN LEGIBLE WHEN REDUCED TO "
                      f"{', '.join(spec['reductions'])} ({d.min_plot_scale * 100:.0f}%).")
    notes = list(spec["notes"]) + [
        "ALL RATINGS ARE COPIED FROM THE SOURCE TOPOLOGY; THIS DRAWING DOES NOT SIZE OR VERIFY EQUIPMENT.",
        plot_note + " PLOT WITH MONOCHROME.CTB; LAYER LINEWEIGHTS APPLY."]
    nx = sx0 + 52
    if nx + 60 <= fx1 - 4:
        p += _ptext(nx, ly, "GENERAL NOTES", 2.5, "E-ANNO-LGND")
        ty, truncated = ly - 6, False
        for i, note in enumerate(notes, 1):
            for line in _wrap_width(f"{i}. {note}", fx1 - 4 - nx, TXT_SMALL, "   "):
                if ty < 13:
                    truncated = True
                    break
                p += _ptext(nx, ty, line, 1.8, "E-ANNO-LGND")
                ty -= 2.8
            ty -= 0.8
            if truncated:
                d.warnings.append("general notes truncated; move long notes to a notes sheet")
                break
    else:
        d.warnings.append("no room for general notes on this sheet size")
    return p


# ---------------------------------------------------------------- checks

CONDUCTOR_LAYERS = ("E-ONEL-COND", "E-ONEL-BUSS", "E-ONEL-GRND")


def _segments(d: Drawing):
    for p in d.prims:
        if p.space != "model" or p.layer not in CONDUCTOR_LAYERS:
            continue
        if p.kind == "line":
            yield p.pts
        elif p.kind == "poly":
            pts = list(zip(p.pts[0::2], p.pts[1::2]))
            for a, b in zip(pts, pts[1:]):
                yield (a[0], a[1], b[0], b[1])


def _segment_hits_box(seg, box):
    """Orthogonal conductor segment vs text box (SLD routing is orthogonal)."""
    x1, y1, x2, y2 = seg
    bx0, by0, bx1, by1 = box
    if abs(x1 - x2) < 0.01:
        return bx0 < x1 < bx1 and min(y1, y2) < by1 and max(y1, y2) > by0
    if abs(y1 - y2) < 0.01:
        return by0 < y1 < by1 and min(x1, x2) < bx1 and max(x1, x2) > bx0
    return False


def text_overlaps(d: Drawing) -> List[Tuple[str, str]]:
    """Model-space label collisions: text against text, and text crossed by a conductor
    or bus. Must be empty for a drawing to go to review."""
    boxes = []
    for p in d.prims:
        if p.space != "model":
            continue
        if p.kind == "text":
            boxes.append((p.text, _text_box(p.pts[0], p.pts[1], p.text, p.height, p.align)))
        for a in p.attribs:
            if not a.invisible:
                boxes.append((a.text, _text_box(a.x, a.y, a.text, a.height, a.align)))
    hits = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (s1, a), (s2, b) = boxes[i], boxes[j]
            if a[0] < b[2] - 0.05 and b[0] < a[2] - 0.05 and a[1] < b[3] - 0.05 and b[1] < a[3] - 0.05:
                hits.append((s1, s2))
    segs = list(_segments(d))
    for s, box in boxes:
        shrunk = (box[0] + 0.2, box[1] + 0.2, box[2] - 0.2, box[3] - 0.2)
        if any(_segment_hits_box(seg, shrunk) for seg in segs):
            hits.append((s, "<conductor>"))
    return hits


def geometry_digest(d: Drawing) -> str:
    h = hashlib.sha256()
    payload = [d.sheet, d.layout_name, [p.key() for p in d.prims],
               {k: [p.key() for p in v] for k, v in sorted(d.blocks.items())}]
    h.update(json.dumps(payload, default=str).encode())
    return h.hexdigest()


# ---------------------------------------------------------------- writers

def _expand(p: Prim, blocks) -> List[Prim]:
    if p.kind != "insert":
        return [p]
    out = []
    for b in blocks[p.block]:
        q = _translate([b], p.pts[0], p.pts[1])[0]
        out.append(Prim(q.kind, p.layer, q.pts, q.text, q.height, q.align,
                        p.linetype if q.linetype == "BYLAYER" else q.linetype, q.closed, space=p.space))
    for a in p.attribs:
        if not a.invisible:
            out.append(Prim("text", a.layer, (a.x, a.y), text=a.text, height=a.height, align=a.align, space=p.space))
    return out


def _space_name(sheet_index: int) -> str:
    return "paper" if sheet_index == 0 else f"paper{sheet_index}"


def write_svg(d: Drawing, path: str, sheet_index: int = 0) -> None:
    """One SVG per sheet: sheet 0 is the diagram sheet (model + its paper space); later
    sheets (e.g. the feeder schedule) are paper space only."""
    W, H = d.width, d.height
    wanted = {_space_name(sheet_index)} | ({"model"} if sheet_index == 0 else set())
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
           f'viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">',
           f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>']
    for prim in d.prims:
        if prim.space not in wanted:
            continue
        for p in _expand(prim, d.blocks):
            aci, lw, plots = LAYERS[p.layer]
            if not plots:
                continue
            col = SVG_COLOR[aci]
            dash = LINETYPES[p.linetype][1] if p.linetype in LINETYPES else None
            da = f' stroke-dasharray="{dash}" stroke-linecap="round"' if dash else ""
            sw = lw / 100
            if p.kind == "line":
                x1, y1, x2, y2 = p.pts
                out.append(f'<line x1="{x1:.2f}" y1="{H - y1:.2f}" x2="{x2:.2f}" y2="{H - y2:.2f}" stroke="{col}" stroke-width="{sw}"{da}/>')
            elif p.kind == "circle":
                x, y, r = p.pts
                out.append(f'<circle cx="{x:.2f}" cy="{H - y:.2f}" r="{r:.2f}" fill="none" stroke="{col}" stroke-width="{sw}"{da}/>')
            elif p.kind == "poly":
                pts = " ".join(f"{p.pts[i]:.2f},{H - p.pts[i + 1]:.2f}" for i in range(0, len(p.pts), 2))
                tag = "polygon" if p.closed else "polyline"
                out.append(f'<{tag} points="{pts}" fill="none" stroke="{col}" stroke-width="{sw}"{da}/>')
            elif p.kind == "text":
                x, y = p.pts
                anchor = {"left": "start", "center": "middle", "right": "end"}[p.align]
                out.append(f'<text x="{x:.2f}" y="{H - y:.2f}" font-size="{p.height / 0.716:.2f}" fill="{col}" '
                           f'text-anchor="{anchor}">{saxutils.escape(p.text)}</text>')
    out.append("</svg>")
    Path(path).write_text("\n".join(out) + "\n", encoding="utf-8")


def build_cad_document(d: Drawing):
    """The ezdxf document: blocks with attribute definitions, model-space diagram,
    paper-space sheet with a viewport. Shared by the DXF and DWG writers."""
    import ezdxf
    from ezdxf.enums import TextEntityAlignment

    doc = ezdxf.new("R2018", setup=False, units=4)
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LTSCALE"] = 1.0
    doc.header["$PSLTSCALE"] = 1
    doc.header["$LWDISPLAY"] = 1
    doc.header["$TEXTSTYLE"] = TEXT_STYLE
    doc.styles.add(TEXT_STYLE, font=TEXT_FONT)
    for name, (pattern, _, desc) in LINETYPES.items():
        doc.linetypes.add(name, pattern=pattern, description=desc)
    for name, (aci, lw, plots) in LAYERS.items():
        doc.layers.add(name, color=aci, lineweight=lw, plot=plots)
    align = {"left": TextEntityAlignment.LEFT, "center": TextEntityAlignment.CENTER,
             "right": TextEntityAlignment.RIGHT}

    def emit(space, p: Prim, in_block=False):
        da = {"layer": p.layer}
        if in_block:
            da.update(layer="0", color=0, lineweight=-2,
                      linetype="CONTINUOUS" if p.linetype == "CONTINUOUS" else "BYBLOCK")
        elif p.linetype not in ("BYLAYER", "CONTINUOUS"):
            da["linetype"] = p.linetype
        if p.kind == "line":
            space.add_line(p.pts[0:2], p.pts[2:4], dxfattribs=da)
        elif p.kind == "circle":
            space.add_circle(p.pts[0:2], p.pts[2], dxfattribs=da)
        elif p.kind == "poly":
            pts = [(p.pts[i], p.pts[i + 1]) for i in range(0, len(p.pts), 2)]
            space.add_lwpolyline(pts, close=p.closed, dxfattribs=da)
        elif p.kind == "text":
            da["style"] = TEXT_STYLE
            if in_block:
                da.pop("linetype")
            t = space.add_text(p.text, height=p.height, dxfattribs=da)
            t.set_placement(p.pts, align=align[p.align])
        elif p.kind == "insert":
            if p.linetype not in ("BYLAYER", "CONTINUOUS"):
                da["linetype"] = p.linetype
            ref = space.add_blockref(p.block, p.pts, dxfattribs=da)
            for a in p.attribs:
                at = ref.add_attrib(a.tag, a.text, insert=(a.x, a.y),
                                    dxfattribs={"layer": a.layer, "height": a.height, "style": TEXT_STYLE,
                                                "flags": 1 if a.invisible else 0})
                at.set_placement((a.x, a.y), align=align[a.align])

    s = 1 / d.min_plot_scale
    for name, prims in sorted(d.blocks.items()):
        blk = doc.blocks.new(name)
        for p in prims:
            emit(blk, p, in_block=True)
        tags = ["TAG"] + [f"DESC{i}" for i in range(1, MAX_WRAPPED + 1)] + ["STATUS"]
        for i, tag in enumerate(tags):
            blk.add_attdef(tag, insert=(SYM * 1.6 * s, (1.0 - i * 2.7) * s), text="", height=TXT_SMALL * s,
                           dxfattribs={"layer": "0", "style": TEXT_STYLE, "prompt": tag})

    msp = doc.modelspace()
    sheets = d.sheets or (d.layout_name,)
    layout = doc.layouts.get("Layout1")
    doc.layouts.rename("Layout1", sheets[0])
    targets = {"model": msp, "paper": layout}
    for i, name in enumerate(sheets[1:], 1):
        targets[_space_name(i)] = doc.layouts.new(name)
    for t in targets.values():
        if t is not msp:
            t.page_setup(size=(d.width, d.height), margins=(0, 0, 0, 0), units="mm")
    for p in d.prims:
        emit(targets[p.space], p)
    vx0, vy0, vx1, vy1 = d.viewport
    cx, cy, w, h = (vx0 + vx1) / 2, (vy0 + vy1) / 2, vx1 - vx0, vy1 - vy0
    layout.add_viewport(center=(cx, cy), size=(w, h), view_center_point=(cx, cy), view_height=h,
                        dxfattribs={"layer": "G-ANNO-VPRT"})
    doc.set_modelspace_vport(height=h * 1.05, center=(cx, cy))
    return doc


def write_dxf(d: Drawing, path: str) -> None:
    build_cad_document(d).saveas(path)


ODA_MAC_PATHS = ("/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter",)


def oda_converter() -> Optional[str]:
    found = shutil.which("ODAFileConverter")
    if found:
        return found
    for p in ODA_MAC_PATHS:
        if Path(p).exists():
            return p
    return None


def write_dwg(d: Drawing, path: str, version: str = "R2018") -> None:
    """DWG through the ODA File Converter (free, opendesign.com). Raises with install
    instructions when it is missing — never falls back to a renamed DXF."""
    exe = oda_converter()
    if exe is None:
        raise RuntimeError(
            "DWG output needs the ODA File Converter (free: https://www.opendesign.com/guestfiles/oda_file_converter). "
            "Install it to /Applications, or open the DXF in AutoCAD / BricsCAD / DraftSight and "
            "SAVEAS DWG. The DXF written alongside is complete and opens in any of them.")
    import ezdxf
    from ezdxf.addons import odafc
    if not shutil.which("ODAFileConverter"):
        ezdxf.options.set("odafc-addon", "unix_exec_path", exe)
    odafc.export_dwg(build_cad_document(d), path, version=version, replace=True)
