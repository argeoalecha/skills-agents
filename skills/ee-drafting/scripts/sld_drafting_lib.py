"""
Electrical drafting engine — single-line (one-line) and riser diagrams from structured
topology data, written to DXF (via ezdxf) and SVG from one shared geometry list.

Every drawing carries an ISO sheet border, a title block with a DRAFT FOR PEE REVIEW
stamp, an empty RA 7920 seal box, a revision block, a legend of the symbols actually
used, and line types that encode data status (solid = field-verified, dashed =
assumed, dotted = unknown). Geometry is deterministic: the same input JSON always
produces the same primitive list (see geometry_digest()).

Symbols follow the ANSI/IEEE one-line conventions (IEEE Std 315 / ANSI Y32.2 style);
layers follow the US National CAD Standard discipline-major-minor pattern (E-ONEL-*).
This engine draws what the topology says. It does not size, rate, or infer anything:
ratings shown on the drawing are copied verbatim from the input.
"""
import hashlib
import json
import textwrap
import xml.sax.saxutils as saxutils
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

SHEETS_MM = {"A3": (420.0, 297.0), "A2": (594.0, 420.0), "A1": (841.0, 594.0), "A0": (1189.0, 841.0)}

LAYERS = {
    "E-ONEL-EQPM": {"color": 7, "svg": "#111111"},
    "E-ONEL-DEVC": {"color": 5, "svg": "#1f4fbf"},
    "E-ONEL-COND": {"color": 7, "svg": "#111111"},
    "E-ONEL-GRND": {"color": 3, "svg": "#1d7a2e"},
    "E-ANNO-TEXT": {"color": 7, "svg": "#111111"},
    "E-ANNO-RISR": {"color": 8, "svg": "#888888"},
    "E-ANNO-LGND": {"color": 7, "svg": "#111111"},
    "E-ANNO-STMP": {"color": 1, "svg": "#c62828"},
    "G-ANNO-TTLB": {"color": 7, "svg": "#111111"},
    "G-ANNO-BRDR": {"color": 7, "svg": "#111111"},
}

STATUS_LINETYPE = {"verified": "CONTINUOUS", "assumed": "DASHED", "unknown": "DOT"}
SVG_DASH = {"CONTINUOUS": None, "DASHED": "4 2", "DOT": "0.8 1.6"}

NODE_TYPES = ("utility", "generator", "transformer", "meter", "ct", "bus", "panel", "ats",
              "breaker", "fuse", "disconnect", "motor", "load", "ground")
DEVICE_TYPES = ("breaker", "fuse", "disconnect", "meter", "ct")
SYMBOL_LABEL = {
    "utility": "UTILITY SOURCE", "generator": "GENERATOR", "transformer": "TRANSFORMER",
    "meter": "KWH METER", "ct": "CURRENT TRANSFORMER", "bus": "BUS", "panel": "PANELBOARD",
    "ats": "AUTOMATIC TRANSFER SWITCH", "breaker": "CIRCUIT BREAKER", "fuse": "FUSE",
    "disconnect": "DISCONNECT SWITCH", "motor": "MOTOR", "load": "LOAD", "ground": "GROUND",
}

TXT = 2.5
TXT_SMALL = 1.8
CHAR_W = 0.72
LEVEL_H = 48.0
NODE_GAP = 14.0
SYM = 10.0


@dataclass
class Prim:
    kind: str
    layer: str
    pts: Tuple[float, ...]
    text: str = ""
    height: float = TXT
    align: str = "left"
    linetype: str = "CONTINUOUS"
    closed: bool = False

    def key(self):
        return (self.kind, self.layer, tuple(round(p, 3) for p in self.pts), self.text,
                round(self.height, 3), self.align, self.linetype, self.closed)


@dataclass
class Drawing:
    sheet: str
    width: float
    height: float
    prims: List[Prim] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def text_width(s: str, h: float) -> float:
    return len(s) * h * CHAR_W


def _status(value: Optional[str]) -> str:
    v = (value or "verified").strip().lower()
    for key in ("verified", "assumed", "unknown"):
        if v.startswith(key):
            return key
    if v.startswith("field"):
        return "verified"
    raise ValueError(f"unknown data status {value!r}; use verified, assumed, or unknown")


# ---------------------------------------------------------------- symbols (local coords)

def _circle(x, y, r, layer, lt):
    return [Prim("circle", layer, (x, y, r), linetype=lt)]


def _line(x1, y1, x2, y2, layer, lt="CONTINUOUS"):
    return [Prim("line", layer, (x1, y1, x2, y2), linetype=lt)]


def _poly(points, layer, lt="CONTINUOUS", closed=True):
    flat = tuple(c for p in points for c in p)
    return [Prim("poly", layer, flat, linetype=lt, closed=closed)]


def _label(x, y, s, h=TXT, layer="E-ANNO-TEXT", align="center"):
    return [Prim("text", layer, (x, y), text=s, height=h, align=align)]


def symbol(kind: str, x: float, y: float, lt: str = "CONTINUOUS") -> Tuple[List[Prim], float, float]:
    """Primitives for one symbol centred at (x, y). Returns (prims, top_y, bottom_y) — the
    connection points for the conductor above and below."""
    L, h = "E-ONEL-EQPM", SYM / 2
    if kind in DEVICE_TYPES:
        L = "E-ONEL-DEVC"
    p: List[Prim] = []
    if kind == "utility":
        p += _circle(x, y, h, L, lt) + _label(x, y - 0.9, "U", TXT, L)
        return p, y + h, y - h
    if kind == "generator":
        p += _circle(x, y, h, L, lt) + _label(x, y - 0.9, "G", TXT, L)
        return p, y + h, y - h
    if kind == "motor":
        p += _circle(x, y, h, L, lt) + _label(x, y - 0.9, "M", TXT, L)
        return p, y + h, y - h
    if kind == "meter":
        p += _circle(x, y, h * 0.8, L, lt) + _label(x, y - 0.6, "kWh", TXT_SMALL, L)
        return p, y + h * 0.8, y - h * 0.8
    if kind == "transformer":
        r = h * 0.75
        p += _circle(x, y + r * 0.6, r, L, lt) + _circle(x, y - r * 0.6, r, L, lt)
        return p, y + r * 1.6, y - r * 1.6
    if kind == "ct":
        p += _circle(x, y, h * 0.45, L, lt) + _line(x - h, y, x + h, y, L, lt)
        return p, y + h * 0.45, y - h * 0.45
    if kind == "breaker":
        s = h * 0.7
        p += _poly([(x - s, y - s), (x + s, y - s), (x + s, y + s), (x - s, y + s)], L, lt)
        return p, y + s, y - s
    if kind == "fuse":
        w, t = h * 0.4, h * 0.9
        p += _poly([(x - w, y - t), (x + w, y - t), (x + w, y + t), (x - w, y + t)], L, lt)
        p += _line(x, y - t, x, y + t, L, lt)
        return p, y + t, y - t
    if kind == "disconnect":
        t = h * 0.9
        p += _circle(x, y - t, 0.6, L, lt) + _circle(x, y + t, 0.6, L, lt)
        p += _line(x, y - t, x + t * 0.9, y + t * 0.7, L, lt)
        return p, y + t, y - t
    if kind == "ats":
        p += _poly([(x - h * 1.3, y - h), (x + h * 1.3, y - h), (x + h * 1.3, y + h), (x - h * 1.3, y + h)], L, lt)
        p += _label(x, y - 0.9, "ATS", TXT, L)
        return p, y + h, y - h
    if kind == "panel":
        p += _poly([(x - h * 1.4, y - h * 0.8), (x + h * 1.4, y - h * 0.8), (x + h * 1.4, y + h * 0.8), (x - h * 1.4, y + h * 0.8)], L, lt)
        p += _line(x - h * 1.4, y - h * 0.8, x + h * 1.4, y + h * 0.8, L, lt)
        return p, y + h * 0.8, y - h * 0.8
    if kind == "load":
        p += _poly([(x - h * 0.7, y + h * 0.4), (x + h * 0.7, y + h * 0.4), (x, y - h * 0.8)], L, lt)
        return p, y + h * 0.4, y - h * 0.8
    if kind == "ground":
        L = "E-ONEL-GRND"
        p += _line(x - h, y, x + h, y, L, lt) + _line(x - h * 0.6, y - 1.5, x + h * 0.6, y - 1.5, L, lt)
        p += _line(x - h * 0.25, y - 3.0, x + h * 0.25, y - 3.0, L, lt)
        return p, y, y - 3.0
    if kind == "bus":
        return p, y, y
    raise ValueError(f"no symbol for node type {kind!r}; supported: {', '.join(NODE_TYPES)}")


# ---------------------------------------------------------------- input model

def load_drawing_spec(spec: dict) -> dict:
    """Validate and normalise a drawing spec (see skill.md for the schema)."""
    nodes = {}
    for n in spec.get("nodes", []):
        if n["type"] not in NODE_TYPES:
            raise ValueError(f"node {n['id']}: unknown type {n['type']!r}")
        if n["id"] in nodes:
            raise ValueError(f"duplicate node id {n['id']!r}")
        nodes[n["id"]] = {**n, "status": _status(n.get("status")), "lines": list(n.get("lines", []))}
    edges = []
    for e in spec.get("edges", []):
        for end in ("from", "to"):
            if e[end] not in nodes:
                raise ValueError(f"edge {e['from']}->{e['to']}: unknown node {e[end]!r}")
        dev = e.get("device")
        if dev and dev["type"] not in DEVICE_TYPES:
            raise ValueError(f"edge {e['from']}->{e['to']}: unknown device {dev['type']!r}")
        edges.append({**e, "status": _status(e.get("status")),
                      "kind": e.get("kind", "feeder")})
    if not nodes:
        raise ValueError("drawing spec has no nodes")
    tb = dict(spec.get("title_block", {}))
    for req in ("project", "drawing_title", "drawing_no", "revision", "date"):
        if not tb.get(req):
            raise ValueError(f"title_block.{req} is required")
    return {"nodes": nodes, "edges": edges, "title_block": tb,
            "revisions": spec.get("revisions", []), "notes": spec.get("notes", []),
            "layout": spec.get("layout", "sld"), "floors": spec.get("floors"),
            "sheet": spec.get("sheet")}


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
        node = {"id": n["id"], "type": t, "lines": lines,
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
            "notes": [meta["survey_basis"]] if meta.get("survey_basis") else [],
            "layout": "sld"}


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


def _node_text_w(n):
    texts = [n["id"]] + n["lines"]
    return max(text_width(texts[0], TXT), *(text_width(t, TXT_SMALL) for t in texts[1:])) if len(texts) > 1 else text_width(texts[0], TXT)


def _layout_positions(spec):
    nodes = spec["nodes"]
    parent, children, roots, secondary = _tree(spec)
    widths: Dict[str, float] = {}

    def width(n):
        own = SYM * 2 + _node_text_w(nodes[n]) + 4
        kids = children[n]
        total = sum(width(c) for c in kids) + NODE_GAP * max(0, len(kids) - 1)
        widths[n] = max(own, total)
        return widths[n]

    depth: Dict[str, int] = {}
    xpos: Dict[str, float] = {}

    def place(n, left, d):
        depth[n] = d
        kids = children[n]
        if not kids:
            xpos[n] = left + widths[n] / 2
            return
        cur = left + (widths[n] - (sum(widths[c] for c in kids) + NODE_GAP * (len(kids) - 1))) / 2
        for c in kids:
            place(c, cur, d + 1)
            cur += widths[c] + NODE_GAP
        xpos[n] = (xpos[kids[0]] + xpos[kids[-1]]) / 2 if nodes[n]["type"] == "bus" or len(kids) > 1 else xpos[kids[0]]

    tree_roots = [r for r in roots if children[r]]
    side_roots = [r for r in roots if not children[r]]
    cursor = 0.0
    for r in tree_roots:
        width(r)
        place(r, cursor, 0)
        cursor += widths[r] + NODE_GAP * 2
    for r in side_roots:
        width(r)
        targets = [e["to"] for e in secondary if e["from"] == r]
        if not targets:
            place(r, cursor, 0)
            cursor += widths[r] + NODE_GAP * 2
            continue
        depth[r] = max(0, min(depth[t] for t in targets) - 1)
        xpos[r] = cursor + widths[r] / 2
        cursor += widths[r] + NODE_GAP * 2

    if spec["layout"] == "riser":
        floors = spec["floors"] or sorted({n.get("floor") for n in nodes.values() if n.get("floor")})
        if not floors:
            raise ValueError("riser layout needs 'floor' on nodes or a 'floors' list")
        level = {f: i for i, f in enumerate(floors)}
        for nid, n in nodes.items():
            f = n.get("floor")
            if f is not None and f not in level:
                raise ValueError(f"node {nid}: floor {f!r} not in floors list {floors}")
        ypos = {}
        for nid, n in nodes.items():
            f = n.get("floor")
            ypos[nid] = (level[f] if f is not None else -1) * LEVEL_H
        return xpos, ypos, parent, children, secondary, cursor - NODE_GAP * 2, floors
    maxd = max(depth.values())
    ypos = {nid: (maxd - d) * LEVEL_H for nid, d in depth.items()}
    return xpos, ypos, parent, children, secondary, cursor - NODE_GAP * 2, None


# ---------------------------------------------------------------- drawing assembly

def _bus_label_prims(n, x_left, y):
    out: List[Prim] = []
    texts = [(n["id"], TXT)] + [(t, TXT_SMALL) for t in n["lines"]]
    if n["status"] != "verified":
        texts.append((f"({n['status'].upper()})", TXT_SMALL))
    ty = y + 2.0
    for s, h in reversed(texts):
        layer = "E-ANNO-STMP" if s.startswith("(") and s.endswith(")") else "E-ANNO-TEXT"
        out += _label(x_left, ty, s, h, layer=layer, align="left")
        ty += h * 1.5
    return out


def _node_prims(n, x, y):
    lt = STATUS_LINETYPE[n["status"]]
    prims, top, bot = symbol(n["type"], x, y, lt)
    if n["type"] == "bus":
        return prims, top, bot
    tx = x + SYM * 1.6
    prims += _label(tx, y + 1.0, n["id"], TXT, align="left")
    ty = y - 2.4
    for line in n["lines"]:
        prims += _label(tx, ty, line, TXT_SMALL, align="left")
        ty -= TXT_SMALL * 1.5
    if n["status"] != "verified":
        prims += _label(tx, ty, f"({n['status'].upper()})", TXT_SMALL, layer="E-ANNO-STMP", align="left")
    return prims, top, bot


def _secondary_edge_prims(e, x1, y_from, x2, y_to, same_level=False, y_floor=0.0):
    """Second feed into a node that already has a primary feed (e.g. the emergency side
    of an ATS). The device sits at the source, where an SLD shows the source breaker;
    the conductor then runs across and drops into the target beside the primary feed.
    Between two nodes on the same level (a cross-branch tie), the run goes underneath
    both so it cannot be mistaken for the feeder junction above them."""
    layer = "E-ONEL-GRND" if e["kind"] == "ground" else "E-ONEL-COND"
    lt = STATUS_LINETYPE[e["status"]]
    out: List[Prim] = []
    if same_level:
        y_run = y_floor - 10.0
        out += _poly([(x1, y_from), (x1, y_run), (x2, y_run), (x2, y_to)], layer, lt, closed=False)
        if e.get("label"):
            out += _label((x1 + x2) / 2, y_run + 1.2, e["label"], TXT_SMALL, align="center")
        return out
    y_run = y_to + 8.0
    x_drop = x2 + SYM * 0.6
    y_cur = y_from
    dev = e.get("device")
    if dev:
        dy = y_from - 10.0
        dprims, dtop, dbot = symbol(dev["type"], x1, dy, lt)
        out += _line(x1, y_from, x1, dtop, layer, lt) + dprims
        if dev.get("label"):
            out += _label(x1 + SYM * 0.9, dy - 0.8, dev["label"], TXT_SMALL, align="left")
        y_cur = dbot
    out += _poly([(x1, y_cur), (x1, y_run), (x_drop, y_run), (x_drop, y_to)], layer, lt, closed=False)
    if e.get("label"):
        out += _label(x1 + 1.5, (y_cur + y_run) / 2, e["label"], TXT_SMALL, align="left")
    return out


def _edge_prims(e, x1, y_from, x2, y_to, spec):
    layer = "E-ONEL-GRND" if e["kind"] == "ground" else "E-ONEL-COND"
    lt = STATUS_LINETYPE[e["status"]]
    out: List[Prim] = []
    ymid = y_from - (y_from - y_to) * 0.35
    if abs(x1 - x2) < 0.01:
        seg = [(x1, y_from), (x2, y_to)]
    else:
        seg = [(x1, y_from), (x1, ymid), (x2, ymid), (x2, y_to)]
    dev = e.get("device")
    if dev:
        dy = (ymid + y_to) / 2 if len(seg) == 4 else (y_from + y_to) / 2
        dprims, dtop, dbot = symbol(dev["type"], x2, dy, lt)
        if len(seg) == 4:
            out += _poly(seg[:3] + [(x2, dtop)], layer, lt, closed=False)
        else:
            out += _line(x1, y_from, x2, dtop, layer, lt)
        out += _line(x2, dbot, x2, y_to, layer, lt)
        out += dprims
        if dev.get("label"):
            out += _label(x2 + SYM * 0.9, dy - 0.8, dev["label"], TXT_SMALL, align="left")
    else:
        out += _poly(seg, layer, lt, closed=False) if len(seg) == 4 else _line(*seg[0], *seg[1], layer, lt)
    if e.get("label"):
        ly = (y_to + dy) / 2 if dev else (ymid + y_to) / 2
        out += _label(x2 - 1.5, ly, e["label"], TXT_SMALL, align="right")
    return out


def _bbox(prims):
    xs, ys = [], []
    for p in prims:
        if p.kind == "circle":
            x, y, r = p.pts
            xs += [x - r, x + r]
            ys += [y - r, y + r]
        elif p.kind == "text":
            x, y = p.pts
            w = text_width(p.text, p.height)
            x0 = x - w if p.align == "right" else (x - w / 2 if p.align == "center" else x)
            xs += [x0, x0 + w]
            ys += [y, y + p.height]
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
        out.append(Prim(p.kind, p.layer, pts, p.text, p.height, p.align, p.linetype, p.closed))
    return out


def build_drawing(spec_in: dict) -> Drawing:
    spec = load_drawing_spec(spec_in)
    nodes = spec["nodes"]
    xpos, ypos, parent, children, secondary, _, floors = _layout_positions(spec)
    body: List[Prim] = []
    ports = {}
    for nid, n in nodes.items():
        prims, top, bot = _node_prims(n, xpos[nid], ypos[nid])
        body += prims
        ports[nid] = (top, bot)
    for nid, n in nodes.items():
        if n["type"] == "bus":
            kids = children[nid] + [e["to"] for e in secondary if e["from"] == nid]
            xs = [xpos[nid]] + [xpos[k] for k in kids]
            y = ypos[nid]
            body += [Prim("line", "E-ONEL-EQPM", (min(xs) - 6, y, max(xs) + 6, y), linetype=STATUS_LINETYPE[n["status"]])]
            body += [Prim("line", "E-ONEL-EQPM", (min(xs) - 6, y + 0.6, max(xs) + 6, y + 0.6), linetype=STATUS_LINETYPE[n["status"]])]
            body += _bus_label_prims(n, min(xs) - 6, y)
    for child, e in parent.items():
        src = e["from"]
        y_from = ypos[src] if nodes[src]["type"] == "bus" else ports[src][1]
        x_from = xpos[child] if nodes[src]["type"] == "bus" else xpos[src]
        body += _edge_prims(e, x_from, y_from, xpos[child], ports[child][0], spec)
    for e in secondary:
        src, dst = e["from"], e["to"]
        y_from = ports[src][1] if nodes[src]["type"] != "bus" else ypos[src]
        if abs(ypos[src] - ypos[dst]) < 0.01:
            text_floor = min(ypos[src], ypos[dst]) - 2.4 - TXT_SMALL * 1.5 * (max(len(nodes[src]["lines"]), len(nodes[dst]["lines"])) + 1)
            y_floor = min(ports[src][1], ports[dst][1], text_floor)
            body += _secondary_edge_prims(e, xpos[src], ports[src][1], xpos[dst], ports[dst][1],
                                          same_level=True, y_floor=y_floor)
        else:
            body += _secondary_edge_prims(e, xpos[src], y_from, xpos[dst], ports[dst][0])
    if floors:
        bx0, _, bx1, _ = _bbox(body)
        for i, f in enumerate(floors):
            yl = i * LEVEL_H - LEVEL_H * 0.45
            body += [Prim("line", "E-ANNO-RISR", (bx0 - 20, yl, bx1 + 10, yl), linetype="DASHED")]
            body += _label(bx0 - 20, yl + 1.5, f"FLOOR {f}", TXT, layer="E-ANNO-RISR", align="left")

    bx0, by0, bx1, by1 = _bbox(body)
    need_w, need_h = bx1 - bx0 + 20, by1 - by0 + 20
    sheet = spec["sheet"]
    warnings: List[str] = []
    if sheet is None:
        for name in ("A3", "A2", "A1", "A0"):
            w, h = SHEETS_MM[name]
            if need_w <= w - 30 and need_h <= h - 30 - 70:
                sheet = name
                break
        else:
            sheet = "A0"
            warnings.append("diagram exceeds A0 at 1:1 drafting scale; split it into sheets")
    W, H = SHEETS_MM[sheet]
    area_x0, area_y0 = 20.0, 10.0 + 70.0
    area_w, area_h = W - 30.0, H - 20.0 - 70.0
    dx = area_x0 + (area_w - (bx1 - bx0)) / 2 - bx0
    dy = area_y0 + (area_h - (by1 - by0)) / 2 - by0
    d = Drawing(sheet=sheet, width=W, height=H, warnings=warnings)
    d.prims += _translate(body, dx, dy)
    d.prims += _sheet_frame(spec, W, H, d)
    return d


def _cell(x, y, w, h, label, value, layer="G-ANNO-TTLB"):
    p = _poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], layer)
    p += [Prim("text", layer, (x + 1.2, y + h - 2.2), text=label, height=1.4)]
    p += [Prim("text", layer, (x + 1.2, y + 1.3), text=str(value), height=2.2)]
    return p


def _sheet_frame(spec, W, H, d: Drawing) -> List[Prim]:
    tb = spec["title_block"]
    p: List[Prim] = []
    p += _poly([(0, 0), (W, 0), (W, H), (0, H)], "G-ANNO-BRDR")
    p += _poly([(20, 10), (W - 10, 10), (W - 10, H - 10), (20, H - 10)], "G-ANNO-BRDR")
    stamp = "DRAFT FOR PEE REVIEW - NOT FOR CONSTRUCTION"
    p += [Prim("text", "E-ANNO-STMP", (W / 2, H - 18), text=stamp, height=5.0, align="center")]

    tx, ty, tw = W - 10 - 180, 10.0, 180.0
    rh = 8.0
    survey = tb.get("survey_date") or "NONE - NOT FIELD-VERIFIED"
    if not tb.get("survey_date"):
        d.warnings.append("no survey_date: drawing is not versioned against a field survey")
    p += _cell(tx, ty + rh * 5, tw, rh, "PROJECT", tb["project"])
    p += _cell(tx, ty + rh * 4, tw, rh, "CLIENT", tb.get("client", "-"))
    p += _cell(tx, ty + rh * 3, tw, rh, "DRAWING TITLE", tb["drawing_title"])
    p += _cell(tx, ty + rh * 2, 80, rh, "DRAWING NO.", tb["drawing_no"])
    p += _cell(tx + 80, ty + rh * 2, 40, rh, "REVISION", tb["revision"])
    p += _cell(tx + 120, ty + rh * 2, 60, rh, "SHEET", tb.get("sheet", "1 OF 1"))
    p += _cell(tx, ty + rh, 60, rh, "DATE", tb["date"])
    p += _cell(tx + 60, ty + rh, 70, rh, "SURVEY DATE", survey)
    p += _cell(tx + 130, ty + rh, 50, rh, "SCALE", tb.get("scale", "NTS"))
    p += _cell(tx, ty, 90, rh, "DRAWN BY", tb.get("drawn_by", "-"))
    p += _cell(tx + 90, ty, 90, rh, "CHECKED / SEALED BY (PEE)", tb.get("checked_by", "UNSIGNED"))
    p += [Prim("text", "E-ANNO-STMP", (tx + tw / 2, ty + rh * 6 + 2.0), text=stamp, height=2.6, align="center")]

    sx = tx - 52
    p += _poly([(sx, ty), (sx + 50, ty), (sx + 50, ty + rh * 6), (sx, ty + rh * 6)], "G-ANNO-TTLB")
    p += [Prim("text", "G-ANNO-TTLB", (sx + 25, ty + rh * 6 - 4), text="PEE SEAL AND SIGNATURE", height=1.8, align="center")]
    p += [Prim("text", "G-ANNO-TTLB", (sx + 25, ty + rh * 6 - 7), text="(RA 7920)", height=1.8, align="center")]
    p += [Prim("text", "E-ANNO-STMP", (sx + 25, ty + rh * 3), text="NOT SEALED", height=3.0, align="center")]

    revs = spec["revisions"] or [{"rev": tb["revision"], "date": tb["date"], "description": "DRAFT FOR PEE REVIEW", "by": tb.get("drawn_by", "-")}]
    ry = ty + rh * 6 + 6
    p += [Prim("text", "G-ANNO-TTLB", (tx + 1, ry + 1 + len(revs) * 5 + 5), text="REVISIONS", height=2.0)]
    for i, r in enumerate(reversed(revs)):
        y = ry + i * 5
        p += [Prim("text", "G-ANNO-TTLB", (tx + 1, y + 1.3), text=str(r.get("rev", "")), height=1.8)]
        p += [Prim("text", "G-ANNO-TTLB", (tx + 12, y + 1.3), text=str(r.get("date", "")), height=1.8)]
        p += [Prim("text", "G-ANNO-TTLB", (tx + 40, y + 1.3), text=str(r.get("description", ""))[:70], height=1.8)]
        p += [Prim("text", "G-ANNO-TTLB", (tx + 160, y + 1.3), text=str(r.get("by", "")), height=1.8)]
        p += _line(tx, y, tx + tw, y, "G-ANNO-TTLB")
    p += _line(tx, ry + len(revs) * 5, tx + tw, ry + len(revs) * 5, "G-ANNO-TTLB")

    used = sorted({n["type"] for n in spec["nodes"].values() if n["type"] != "bus"} |
                  {e["device"]["type"] for e in spec["edges"] if e.get("device")})
    lx, ly = 24.0, 10.0 + 70.0 - 6
    p += [Prim("text", "E-ANNO-LGND", (lx, ly), text="LEGEND", height=2.5)]
    col_w, row_h, per_col = 62.0, 12.0, 4
    for i, kind in enumerate(used):
        cx = lx + 6 + (i // per_col) * col_w
        cy = ly - 8 - (i % per_col) * row_h
        sp, _, _ = symbol(kind, cx, cy)
        p += [Prim(s.kind, "E-ANNO-LGND", s.pts, s.text, s.height, s.align, s.linetype, s.closed) for s in sp]
        p += [Prim("text", "E-ANNO-LGND", (cx + 9, cy - 0.8), text=SYMBOL_LABEL[kind], height=1.8)]
    sx0 = lx + (len(used) // per_col + 1) * col_w
    for i, (status, lt) in enumerate(STATUS_LINETYPE.items()):
        y = ly - 8 - i * row_h
        p += [Prim("line", "E-ANNO-LGND", (sx0, y, sx0 + 14, y), linetype=lt)]
        p += [Prim("text", "E-ANNO-LGND", (sx0 + 17, y - 0.8), text=f"{status.upper()} DATA", height=1.8)]
    notes = list(spec["notes"]) + ["ALL RATINGS ARE COPIED FROM THE SOURCE TOPOLOGY; THIS DRAWING DOES NOT SIZE OR VERIFY EQUIPMENT."]
    nx = sx0 + 60
    if nx + 60 < tx - 56:
        p += [Prim("text", "E-ANNO-LGND", (nx, ly), text="GENERAL NOTES", height=2.5)]
        max_chars = int((tx - 56 - nx) / (1.8 * CHAR_W))
        y = ly - 6
        truncated = False
        for i, note in enumerate(notes, 1):
            for line in textwrap.wrap(f"{i}. {note}", width=max_chars, subsequent_indent="   "):
                if y < 14:
                    truncated = True
                    break
                p += [Prim("text", "E-ANNO-LGND", (nx, y), text=line, height=1.8)]
                y -= 2.8
            y -= 0.8
            if truncated:
                d.warnings.append("general notes truncated; move long notes to a notes sheet")
                break
    else:
        d.warnings.append("no room for general notes on this sheet size")
    return p


# ---------------------------------------------------------------- writers

def geometry_digest(d: Drawing) -> str:
    h = hashlib.sha256()
    h.update(json.dumps([d.sheet] + [p.key() for p in d.prims], default=str).encode())
    return h.hexdigest()


def write_svg(d: Drawing, path: str) -> None:
    W, H = d.width, d.height
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
           f'viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">',
           f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>']
    for p in d.prims:
        col = LAYERS[p.layer]["svg"]
        dash = SVG_DASH[p.linetype]
        da = f' stroke-dasharray="{dash}"' if dash else ""
        sw = 0.5 if p.layer in ("E-ONEL-EQPM", "E-ONEL-DEVC", "E-ONEL-COND", "E-ONEL-GRND") else 0.3
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
            out.append(f'<text x="{x:.2f}" y="{H - y:.2f}" font-size="{p.height * 1.3:.2f}" fill="{col}" '
                       f'text-anchor="{anchor}">{saxutils.escape(p.text)}</text>')
    out.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


def write_dxf(d: Drawing, path: str) -> None:
    import ezdxf
    from ezdxf.enums import TextEntityAlignment

    doc = ezdxf.new("R2010", setup=True, units=4)
    doc.header["$LTSCALE"] = 0.25
    for name, attrs in LAYERS.items():
        doc.layers.add(name, color=attrs["color"])
    msp = doc.modelspace()
    align = {"left": TextEntityAlignment.LEFT, "center": TextEntityAlignment.CENTER,
             "right": TextEntityAlignment.RIGHT}
    for p in d.prims:
        da = {"layer": p.layer}
        if p.linetype != "CONTINUOUS":
            da["linetype"] = p.linetype
        if p.kind == "line":
            msp.add_line(p.pts[0:2], p.pts[2:4], dxfattribs=da)
        elif p.kind == "circle":
            msp.add_circle(p.pts[0:2], p.pts[2], dxfattribs=da)
        elif p.kind == "poly":
            pts = [(p.pts[i], p.pts[i + 1]) for i in range(0, len(p.pts), 2)]
            msp.add_lwpolyline(pts, close=p.closed, dxfattribs=da)
        elif p.kind == "text":
            t = msp.add_text(p.text, height=p.height, dxfattribs=da)
            t.set_placement(p.pts, align=align[p.align])
    doc.saveas(path)
