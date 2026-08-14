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
    {"from": "trip", "to": "q1", "label": "recheck", "loop": true},
    {"from": "trip", "to": "end"}
  ]
}

shape is one of: box, diamond, oval. Defaults to box.
edge "loop": true — a retry/recheck going back to an earlier step. Drawn as a
  dashed curve off to the side and excluded from the layering. Any edge running
  backwards must be marked this way, or it counts as a genuine cycle and the
  script errors out instead of drawing something misleading.

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


# Half-heights per shape, so a connector stops just outside the shape it meets.
# A flat 0.5 offset put arrowheads *inside* the taller diamond, where the node
# (higher zorder) painted over them and the edge lost its direction.
SHAPE_HALF_H = {"box": 0.45, "oval": 0.45, "diamond": 0.65}
EDGE_MARGIN = 0.1


def half_h(n):
    return SHAPE_HALF_H.get(n.get("shape", "box"), 0.45) + EDGE_MARGIN


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

    for e in data["edges"]:
        if e["from"] not in by_id or e["to"] not in by_id:
            raise ValueError(f"Edge {e} references a node id that isn't in 'nodes'")

    # Retries/rechecks are marked "loop": true and kept out of the layering,
    # exactly as in render_flowchart.py — otherwise they read as a genuine
    # cycle and topo_levels raises telling you to mark them.
    forward = [(e["from"], e["to"]) for e in data["edges"] if not e.get("loop")]
    loops = [e for e in data["edges"] if e.get("loop")]
    pos, _ = layered_positions(node_ids, forward, x_gap=3.0, y_gap=2.0)

    with plt.xkcd(scale=1, length=100, randomness=2):
        fig, ax = plt.subplots(figsize=(11, 8))
        fig.patch.set_facecolor(theme["bg"])
        ax.set_facecolor(theme["bg"])
        ax.axis("off")

        for e in data["edges"]:
            if e.get("loop"):
                continue
            x1, y1 = pos[e["from"]]
            x2, y2 = pos[e["to"]]
            draw_connector(ax, x1, y1 - half_h(by_id[e["from"]]),
                            x2, y2 + half_h(by_id[e["to"]]), theme, arrow=True, lw=1.6)
            if e.get("label"):
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                ax.text(mx + 0.15, my, e["label"], fontsize=8, color=theme["accent"])

        # Loop-backs bow out to the side, dashed, so they read as feedback
        # rather than as part of the main downward flow.
        # Bow each loop-back away from the diagram's centre line so it clears the
        # forward edges instead of cutting across them.
        cx = (min(p[0] for p in pos.values()) + max(p[0] for p in pos.values())) / 2
        for e in loops:
            x1, y1 = pos[e["from"]]
            x2, y2 = pos[e["to"]]
            outward = -1 if (x1 + x2) / 2 <= cx else 1
            rad = 0.5 * outward
            draw_connector(ax, x1, y1 + half_h(by_id[e["from"]]),
                            x2, y2 - half_h(by_id[e["to"]]), theme,
                            color=theme["critical"], lw=1.6, style="--",
                            curved=True, rad=rad, arrow=True)
            if e.get("label"):
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                ax.text(mx + 1.5 * outward, my, e["label"], fontsize=8,
                         color=theme["critical"], ha="right" if outward < 0 else "left")

        for nid, n in by_id.items():
            x, y = pos[nid]
            draw_node(ax, n, x, y, theme)

        xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
        ax.set_xlim(min(xs) - 2, max(xs) + (3.2 if loops else 2))
        ax.set_ylim(min(ys) - 1.5, max(ys) + 1.5)
        save_fig(fig, args.output)

    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
