#!/usr/bin/env python3
"""
render_sketch.py — hand-drawn / whiteboard-style flowchart renderer.

Input JSON shape:
{
  "nodes": [
    {"id": "start", "label": "Start", "shape": "oval"},
    {"id": "q1",    "label": "Fault detected?", "shape": "diamond"},
    {"id": "trip",  "label": "Trip breaker", "shape": "box"},
    {"id": "end",   "label": "End", "shape": "oval"}
  ],
  "edges": [
    {"from": "start", "to": "q1"},
    {"from": "q1", "to": "trip", "label": "yes"},
    {"from": "q1", "to": "end", "label": "no"},
    {"from": "trip", "to": "end"}
  ]
}

shape is one of: box, diamond, oval. Defaults to box.

Usage:
  python3 render_sketch.py input.json -o sketch.svg [--theme default|hayah]
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import matplotlib.pyplot as plt
from dtk_common import (get_theme, wrap_text, draw_box, draw_diamond, draw_ellipse,
                         draw_connector, save_fig, load_json, layered_positions)


def draw_node(ax, n, x, y, theme):
    label = wrap_text(n.get("label", n["id"]), 16)
    shape = n.get("shape", "box")
    if shape == "diamond":
        draw_diamond(ax, x, y, 2.4, 1.3, label, theme, fontsize=8)
    elif shape == "oval":
        # Dark text stays legible under the xkcd wobble; white text turns to noise.
        draw_ellipse(ax, x, y, 2.0, 0.9, label, theme, fill=theme["node_fill"],
                     edge=theme["accent"], fontsize=8.5)
    else:
        draw_box(ax, x, y, 2.2, 0.9, label, theme)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default="sketch.svg")
    ap.add_argument("--theme", default="default", choices=["default", "hayah"])
    args = ap.parse_args()

    data = load_json(args.input)
    theme = get_theme(args.theme)

    node_ids = [n["id"] for n in data["nodes"]]
    by_id = {n["id"]: n for n in data["nodes"]}
    edges = [(e["from"], e["to"]) for e in data["edges"]]
    pos, _ = layered_positions(node_ids, edges, x_gap=3.0, y_gap=2.0)

    with plt.xkcd(scale=1, length=100, randomness=2):
        fig, ax = plt.subplots(figsize=(11, 8))
        fig.patch.set_facecolor(theme["bg"])
        ax.set_facecolor(theme["bg"])
        ax.axis("off")

        for e in data["edges"]:
            x1, y1 = pos[e["from"]]
            x2, y2 = pos[e["to"]]
            draw_connector(ax, x1, y1 - 0.5, x2, y2 + 0.5, theme, arrow=True, lw=1.6)
            if e.get("label"):
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                ax.text(mx + 0.15, my, e["label"], fontsize=8, color=theme["accent"])

        for nid, n in by_id.items():
            x, y = pos[nid]
            draw_node(ax, n, x, y, theme)

        xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
        ax.set_xlim(min(xs) - 2, max(xs) + 2)
        ax.set_ylim(min(ys) - 1.5, max(ys) + 1.5)
        save_fig(fig, args.output)

    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
