#!/usr/bin/env python3
"""
render_mindmap.py — radial mind map renderer.

Input JSON shape:
{
  "title": "Central Topic",
  "children": [
    {"label": "Branch A", "children": [{"label": "Sub A1"}, {"label": "Sub A2"}]},
    {"label": "Branch B", "children": [{"label": "Sub B1"}]}
  ]
}

Usage:
  python3 render_mindmap.py input.json -o mindmap.svg [--theme default|hayah]
"""
import argparse
import math
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from dtk_common import get_theme, wrap_text, new_figure, draw_box, draw_connector, save_fig, load_json


def count_leaves(node):
    children = node.get("children", [])
    if not children:
        node["_leaves"] = 1
        return 1
    total = sum(count_leaves(c) for c in children)
    node["_leaves"] = max(total, 1)
    return node["_leaves"]


def assign_polar(node, a0, a1, depth, radius_step):
    node["angle"] = (a0 + a1) / 2
    node["radius"] = depth * radius_step
    node["depth"] = depth
    children = node.get("children", [])
    if not children:
        return
    span = a1 - a0
    cursor = a0
    for c in children:
        frac = c["_leaves"] / node["_leaves"]
        c0, c1 = cursor, cursor + span * frac
        assign_polar(c, c0, c1, depth + 1, radius_step)
        cursor = c1


def to_xy(node):
    r, a = node["radius"], node["angle"]
    node["x"] = r * math.cos(a)
    node["y"] = r * math.sin(a)
    for c in node.get("children", []):
        to_xy(c)


WRAP_AT = 16
# Data units per point of font size, calibrated against the rendered output.
# CHAR_W is deliberately above the average glyph width — labels are short and
# often capitalised ("HTML command", "CT/PT"), which runs wider than lowercase.
CHAR_W = 0.0108
LINE_H = 0.026


def fit_box(label, fontsize, wrap_at=WRAP_AT):
    """Size a box to the text *after* wrapping.

    Sizing off the raw label length with a fixed 0.42 height meant anything
    wrapping to three lines overflowed its box vertically, while long labels
    got over-wide boxes for text the wrapper had already broken up.
    """
    wrapped = wrap_text(label, wrap_at)
    lines = wrapped.split("\n")
    longest = max((len(line) for line in lines), default=1)
    w = CHAR_W * fontsize * longest + 0.5
    h = LINE_H * fontsize * len(lines) + 0.22
    return wrapped, w, h


def draw(ax, node, theme, branch_color=None, depth=0):
    label = node.get("label") or node.get("title") or ""
    x, y = node.get("x", 0), node.get("y", 0)
    fill = branch_color or theme["node_fill"]
    fontsize = 12 if depth == 0 else max(11 - depth, 7)
    wrapped, w, h = fit_box(label, fontsize)
    if depth == 0:
        draw_box(ax, x, y, w + 0.5, h, wrapped, theme,
                  fill=theme["accent"], edge=theme["accent"], fontsize=fontsize,
                  fontweight="bold", text_color="#ffffff", zorder=5)
    else:
        draw_box(ax, x, y, w, h, wrapped, theme,
                  fill=fill, edge=branch_color or theme["node_edge"],
                  fontsize=fontsize, zorder=4)

    children = node.get("children", [])
    for i, c in enumerate(children):
        cx, cy = c.get("x", 0), c.get("y", 0)
        color = branch_color
        if depth == 0 and color is None:
            palette = theme["palette"]
            color = palette[i % len(palette)]
        draw_connector(ax, x, y, cx, cy, theme, color=color or theme["line"],
                        lw=2.2 if depth == 0 else 1.4, curved=True, rad=0.12)
        draw(ax, c, theme, branch_color=color, depth=depth + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Path to mind map JSON")
    ap.add_argument("-o", "--output", default="mindmap.svg")
    ap.add_argument("--theme", default="default", choices=["default", "hayah"])
    ap.add_argument("--radius-step", type=float, default=2.4)
    args = ap.parse_args()

    data = load_json(args.input)
    theme = get_theme(args.theme)

    count_leaves(data)
    assign_polar(data, 0, 2 * math.pi, depth=0, radius_step=args.radius_step)
    to_xy(data)

    fig, ax = new_figure(theme["bg"])
    draw(ax, data, theme)

    max_r = data["_leaves"] and _max_radius(data)
    pad = 1.2
    ax.set_xlim(-max_r - pad, max_r + pad)
    ax.set_ylim(-max_r - pad, max_r + pad)
    ax.set_aspect("equal")

    save_fig(fig, args.output)
    print(f"Wrote {args.output}")


def _max_radius(node):
    r = node.get("radius", 0)
    for c in node.get("children", []):
        r = max(r, _max_radius(c))
    return r


if __name__ == "__main__":
    main()
