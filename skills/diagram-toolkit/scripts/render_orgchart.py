#!/usr/bin/env python3
"""
render_orgchart.py — top-down organizational chart renderer.

Input JSON shape:
{
  "name": "Argeo Alecha",
  "title": "Owner's Technical Advisor",
  "children": [
    {"name": "Site Engineer", "title": "Field Lead",
     "children": [{"name": "Technician A", "title": "Instrumentation"}]},
    {"name": "Site Engineer 2", "title": "Field Lead"}
  ]
}

Usage:
  python3 render_orgchart.py input.json -o orgchart.svg [--theme default|hayah]
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from dtk_common import get_theme, wrap_text, new_figure, draw_box, draw_elbow, save_fig, load_json

BOX_W, BOX_H = 2.6, 0.9
X_GAP, Y_GAP = 0.6, 1.7


def compute_widths(node):
    children = node.get("children", [])
    if not children:
        node["_width"] = BOX_W
        return node["_width"]
    total = sum(compute_widths(c) for c in children) + X_GAP * (len(children) - 1)
    node["_width"] = max(total, BOX_W)
    return node["_width"]


def assign_positions(node, x_center, depth):
    node["x"] = x_center
    node["y"] = -depth * Y_GAP
    children = node.get("children", [])
    if not children:
        return
    total_w = sum(c["_width"] for c in children) + X_GAP * (len(children) - 1)
    cursor = x_center - total_w / 2
    for c in children:
        c_center = cursor + c["_width"] / 2
        assign_positions(c, c_center, depth + 1)
        cursor += c["_width"] + X_GAP


def draw(ax, node, theme, root=False):
    name = node.get("name") or node.get("label") or ""
    title = node.get("title", "")
    label = wrap_text(name, 20) + ("\n" + wrap_text(title, 22) if title else "")
    fill = theme["accent"] if root else theme["node_fill"]
    text_color = "#ffffff" if root else theme["node_text"]
    draw_box(ax, node["x"], node["y"], BOX_W, BOX_H, label, theme,
              fill=fill, fontsize=9.5, fontweight="bold" if root else "normal",
              text_color=text_color, zorder=4)
    for c in node.get("children", []):
        draw_elbow(ax, node["x"], node["y"] - BOX_H / 2, c["x"], c["y"] + BOX_H / 2, theme, lw=1.4)
        draw(ax, c, theme)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default="orgchart.svg")
    ap.add_argument("--theme", default="default", choices=["default", "hayah"])
    args = ap.parse_args()

    data = load_json(args.input)
    theme = get_theme(args.theme)

    compute_widths(data)
    assign_positions(data, 0, 0)

    fig, ax = new_figure(theme["bg"])
    draw(ax, data, theme, root=True)

    xs, ys = _collect_xy(data, [], [])
    pad_x, pad_y = 1.6, 1.0
    ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
    ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)
    ax.set_aspect("equal")

    save_fig(fig, args.output)
    print(f"Wrote {args.output}")


def _collect_xy(node, xs, ys):
    xs.append(node["x"]); ys.append(node["y"])
    for c in node.get("children", []):
        _collect_xy(c, xs, ys)
    return xs, ys


if __name__ == "__main__":
    main()
