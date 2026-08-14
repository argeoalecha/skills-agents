#!/usr/bin/env python3
"""
render_flowtree.py — directional flow-tree renderer for brainstorm/issue-tree output.

Unlike render_mindmap.py (radial, free association) or render_orgchart.py
(people/roles, undirected lines), this is for a structured branching argument —
a "how might we" tree, MECE issue tree, or decision tree — with an arrowed,
directional flow and a per-node status so you can visually mark which branches
were kept, dropped, or parked for later. This is the natural output shape for
the brainstorm-ideas skill: root question -> approaches -> ideas -> verdict.

Input JSON shape:
{
  "direction": "TD",
  "root": {
    "label": "How might we cut alarm fatigue on the SISC dashboard?",
    "status": "root",
    "children": [
      {"label": "Alarm rationalization pass", "status": "selected",
       "children": [
         {"label": "ISA-18.2 priority tiers", "status": "selected"},
         {"label": "Suppress nuisance duplicates", "status": "default"}
       ]},
      {"label": "Full SCADA replatform", "status": "discarded",
       "children": [{"label": "6-mo timeline, out of budget", "status": "discarded"}]},
      {"label": "Add a second monitor", "status": "parked"}
    ]
  }
}

direction: "TD" (top-down, default) or "LR" (left-to-right, good for wide trees).
status per node: "root" | "default" | "selected" | "discarded" | "parked".
  - selected: kept / recommended  (green fill, bold)
  - discarded: ruled out          (greyed out, dashed border, faded text)
  - parked: worth revisiting      (dotted border)
  - default / omitted: plain node

Usage:
  python3 render_flowtree.py input.json -o flowtree.svg [--theme default|hayah]
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from dtk_common import (get_theme, wrap_text, new_figure, draw_box, draw_elbow_arrow,
                         save_fig, load_json)

BOX_W, BOX_H = 2.6, 0.85
ROOT_W, ROOT_H = 3.2, 1.0
GAP_DEPTH = 1.8
# Breadth is the axis siblings spread along: horizontal for TD, vertical for LR.
# Measuring it in box widths regardless of direction made LR trees enormously
# tall, since it reserved 2.6 units of vertical room for a 0.85-tall box.
GAP_BREADTH = {"TD": 0.6, "LR": 0.5}

STATUS_LABELS = {
    "selected": "Selected / recommended",
    "discarded": "Discarded",
    "parked": "Parked for later",
}


def status_style(theme, status):
    if status == "root":
        return dict(fill=theme["accent"], edge=theme["accent"], text_color="#ffffff",
                     fontweight="bold", linestyle="-", alpha=1.0, fontstyle="normal")
    if status == "selected":
        return dict(fill="#dcfce7", edge="#16a34a", text_color="#14532d",
                     fontweight="bold", linestyle="-", alpha=1.0, fontstyle="normal")
    if status == "discarded":
        return dict(fill="#f1f5f9", edge="#94a3b8", text_color="#94a3b8",
                     fontweight="normal", linestyle="--", alpha=0.75, fontstyle="normal")
    if status == "parked":
        return dict(fill=theme["node_fill"], edge=theme["node_edge"], text_color=theme["node_text"],
                     fontweight="normal", linestyle=":", alpha=1.0, fontstyle="italic")
    return dict(fill=theme["node_fill"], edge=theme["node_edge"], text_color=theme["node_text"],
                 fontweight="normal", linestyle="-", alpha=1.0, fontstyle="normal")


def box_size(node, depth):
    return (ROOT_W, ROOT_H) if depth == 0 else (BOX_W, BOX_H)


def box_breadth(node, depth, direction):
    """Extent of a box along the axis siblings are spread on."""
    w, h = box_size(node, depth)
    return h if direction == "LR" else w


def compute_widths(node, direction, depth=0):
    own = box_breadth(node, depth, direction)
    gap = GAP_BREADTH[direction]
    children = node.get("children", [])
    if not children:
        node["_breadth"] = own
        return node["_breadth"]
    total = sum(compute_widths(c, direction, depth + 1) for c in children) + gap * (len(children) - 1)
    node["_breadth"] = max(total, own)
    return node["_breadth"]


def assign_positions(node, center, direction, depth=0):
    node["u"] = center
    node["depth"] = depth
    children = node.get("children", [])
    if not children:
        return
    gap = GAP_BREADTH[direction]
    total_w = sum(c["_breadth"] for c in children) + gap * (len(children) - 1)
    cursor = center - total_w / 2
    for c in children:
        c_center = cursor + c["_breadth"] / 2
        assign_positions(c, c_center, direction, depth + 1)
        cursor += c["_breadth"] + gap


def to_xy(node, direction):
    if direction == "LR":
        node["x"] = node["depth"] * GAP_DEPTH * 2.4
        node["y"] = -node["u"]
    else:
        node["x"] = node["u"]
        node["y"] = -node["depth"] * GAP_DEPTH
    for c in node.get("children", []):
        to_xy(c, direction)


def collect_statuses(node, found):
    st = node.get("status")
    if st in STATUS_LABELS:
        found.add(st)
    for c in node.get("children", []):
        collect_statuses(c, found)
    return found


def draw(ax, node, theme, direction, depth=0):
    label = node.get("label", "")
    w, h = box_size(node, depth)
    style = status_style(theme, node.get("status", "root" if depth == 0 else "default"))
    draw_box(ax, node["x"], node["y"], w, h, wrap_text(label, 20), theme,
              fill=style["fill"], edge=style["edge"], text_color=style["text_color"],
              fontweight=style["fontweight"], linestyle=style["linestyle"],
              alpha=style["alpha"], fontstyle=style["fontstyle"],
              fontsize=10.5 if depth == 0 else 9, zorder=4)
    for c in node.get("children", []):
        child_style = status_style(theme, c.get("status", "default"))
        edge_x1 = node["x"] + (w / 2 if direction == "LR" else 0)
        edge_y1 = node["y"] if direction == "LR" else node["y"] - h / 2
        edge_x2 = c["x"] - (box_size(c, depth + 1)[0] / 2 if direction == "LR" else 0)
        edge_y2 = c["y"] if direction == "LR" else c["y"] + box_size(c, depth + 1)[1] / 2
        draw_elbow_arrow(ax, edge_x1, edge_y1, edge_x2, edge_y2, theme,
                          color=child_style["edge"] if c.get("status") in ("selected", "discarded") else theme["line"],
                          lw=2.0 if c.get("status") == "selected" else 1.3,
                          linestyle=child_style["linestyle"] if c.get("status") == "discarded" else "-",
                          direction=direction)
        draw(ax, c, theme, direction, depth + 1)


def draw_legend(ax, theme, statuses_used, x0, y0):
    if not statuses_used:
        return
    for i, st in enumerate(sorted(statuses_used, key=list(STATUS_LABELS).index)):
        style = status_style(theme, st)
        y = y0 - i * 0.45
        draw_box(ax, x0, y, 0.35, 0.25, "", theme, fill=style["fill"], edge=style["edge"],
                  linestyle=style["linestyle"], alpha=style["alpha"], zorder=5)
        ax.text(x0 + 0.35, y, STATUS_LABELS[st], ha="left", va="center", fontsize=8.5,
                 color=theme["node_text"], zorder=5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default="flowtree.svg")
    ap.add_argument("--theme", default="default", choices=["default", "hayah"])
    args = ap.parse_args()

    data = load_json(args.input)
    direction = data.get("direction", "TD").upper()
    root = data["root"]
    theme = get_theme(args.theme)

    if direction not in GAP_BREADTH:
        raise ValueError(f'direction must be "TD" or "LR", got {direction!r}')

    compute_widths(root, direction)
    assign_positions(root, 0, direction)
    to_xy(root, direction)

    fig, ax = new_figure(theme["bg"])
    draw(ax, root, theme, direction)

    xs, ys = [], []
    _collect_xy(root, xs, ys)
    pad = 1.6
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - pad, max(ys) + pad)

    statuses_used = collect_statuses(root, set())
    draw_legend(ax, theme, statuses_used, min(xs) - pad + 0.2, min(ys) - pad + 0.9)

    save_fig(fig, args.output)
    print(f"Wrote {args.output}")


def _collect_xy(node, xs, ys):
    xs.append(node["x"]); ys.append(node["y"])
    for c in node.get("children", []):
        _collect_xy(c, xs, ys)


if __name__ == "__main__":
    main()
