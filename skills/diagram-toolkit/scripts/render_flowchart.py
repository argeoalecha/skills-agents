#!/usr/bin/env python3
"""
render_flowchart.py — process flowchart renderer (ISO 5807-style shapes).

This is the "clean/professional" flowchart — distinct from render_sketch.py
(hand-drawn/whiteboard) and render_flowtree.py (brainstorm/issue trees, no
loops, no convergence). Use this one when the diagram represents an actual
procedure: an SOP, an alarm-response workflow, an approval process — anything
where steps can converge (two branches rejoin) or loop back (retry / recheck).

Input JSON shape:
{
  "title": "Alarm Response Procedure",
  "lanes": ["SCADA System", "Field Technician", "Campus Engineer"],
  "nodes": [
    {"id": "start", "label": "Alarm triggered", "shape": "terminator", "lane": "SCADA System"},
    {"id": "notify", "label": "Send SMS/email alert", "shape": "process", "lane": "SCADA System"},
    {"id": "ack", "label": "Acknowledged within 15 min?", "shape": "decision", "lane": "Field Technician"},
    {"id": "dispatch", "label": "Dispatch to site", "shape": "process", "lane": "Field Technician"},
    {"id": "escalate", "label": "Escalate to campus engineer", "shape": "process", "lane": "Campus Engineer"},
    {"id": "log", "label": "Log resolution in CMMS", "shape": "document", "lane": "Field Technician"},
    {"id": "end", "label": "Alarm cleared", "shape": "terminator", "lane": "SCADA System"}
  ],
  "edges": [
    {"from": "start", "to": "notify"},
    {"from": "notify", "to": "ack"},
    {"from": "ack", "to": "dispatch", "label": "Yes"},
    {"from": "ack", "to": "escalate", "label": "No"},
    {"from": "escalate", "to": "dispatch"},
    {"from": "dispatch", "to": "log"},
    {"from": "log", "to": "end"},
    {"from": "log", "to": "ack", "label": "Recurs in 24h", "loop": true}
  ]
}

shape: terminator | process | decision | io | document | predefined | connector
  - terminator: rounded oval, start/end
  - process: sharp-cornered rectangle, a step
  - decision: diamond, can branch to multiple children with edge "label"
  - io: parallelogram, input/output
  - document: rectangle with a wavy bottom, a report/log/record
  - predefined: rectangle with side bars, a subroutine/call-out to another procedure
  - connector: small circle, an on-page reference marker
edge "loop": true — routes the edge as a feedback loop around the right side
  of the diagram instead of straight down, and excludes it from level layout.
  Use for retries/rechecks. Without this, an edge that goes from a later step
  back to an earlier one is a genuine cycle and the script will error out
  rather than draw something misleading (see Troubleshooting in SKILL.md).
"lanes" (optional): activates swimlane mode — each node needs a "lane"
  matching one of the listed names. Omit "lanes" entirely for a plain
  (no-lane) flowchart.

Usage:
  python3 render_flowchart.py input.json -o flowchart.svg [--theme default|hayah]
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from dtk_common import (get_theme, wrap_text, new_figure, draw_rect, draw_ellipse, draw_diamond,
                         draw_parallelogram, draw_document, draw_predefined_process,
                         draw_elbow_arrow, save_fig, load_json, topo_levels)

SHAPE_SIZE = {
    "terminator": (2.5, 0.85),
    "process": (2.2, 0.8),
    "decision": (2.4, 1.3),
    "io": (2.2, 0.8),
    "document": (2.2, 0.85),
    "predefined": (2.2, 0.8),
    "connector": (0.55, 0.55),
}
WRAP_WIDTH = {"terminator": 15, "decision": 16}
DEFAULT_WRAP = 18
X_GAP, Y_GAP = 2.7, 1.9
LANE_WIDTH = 3.1          # minimum; widened when a lane holds siblings (see compute_layout)
NODE_SLOT = 2.7           # horizontal pitch between siblings sharing a lane + level
BYPASS_GAP = 0.85         # clearance from a node's edge to a bypass channel
LANE_PAD = 0.25           # keep contents off the lane divider


def draw_shape(ax, node, theme):
    shape = node.get("shape", "process")
    x, y = node["x"], node["y"]
    w, h = SHAPE_SIZE.get(shape, SHAPE_SIZE["process"])
    label = wrap_text(node.get("label", node["id"]), WRAP_WIDTH.get(shape, DEFAULT_WRAP))
    if shape == "terminator":
        draw_ellipse(ax, x, y, w, h, label, theme, fill=theme["accent"])
        ax.texts[-1].set_color("#ffffff")
        ax.texts[-1].set_fontweight("bold")
    elif shape == "decision":
        draw_diamond(ax, x, y, w, h, label, theme, fontsize=8)
    elif shape == "io":
        draw_parallelogram(ax, x, y, w, h, label, theme)
    elif shape == "document":
        draw_document(ax, x, y, w, h, label, theme)
    elif shape == "predefined":
        draw_predefined_process(ax, x, y, w, h, label, theme)
    elif shape == "connector":
        draw_ellipse(ax, x, y, w, h, node.get("id", ""), theme, fontsize=8)
    else:
        draw_rect(ax, x, y, w, h, label, theme)


def node_width(node):
    return SHAPE_SIZE.get(node.get("shape", "process"), SHAPE_SIZE["process"])[0]


def compute_layout(nodes, forward_edges, lanes):
    node_ids = [n["id"] for n in nodes]
    by_id = {n["id"]: n for n in nodes}
    levels = topo_levels(node_ids, forward_edges)  # raises on a true cycle

    preds = {n: [] for n in node_ids}
    for s, d in forward_edges:
        preds[d].append(s)

    by_level = {}
    for nid in node_ids:
        by_level.setdefault(levels[nid], []).append(nid)

    pos = {}
    lane_width = LANE_WIDTH
    bypass_offset = {}
    if lanes:
        # Offsets within a lane don't depend on how wide the lane ends up, so
        # settle them first and size the lane around them.
        offset_in_lane = {}
        for lv in sorted(by_level):
            by_lane_here = {}
            for nid in by_level[lv]:
                by_lane_here.setdefault(by_id[nid].get("lane"), []).append(nid)
            for lane, ids_here in by_lane_here.items():
                off = (len(ids_here) - 1) / 2.0
                for i, nid in enumerate(ids_here):
                    offset_in_lane[nid] = (i - off) * NODE_SLOT

        # A lane must hold its widest node stack...
        reach = 0.0
        for nid in node_ids:
            w = SHAPE_SIZE.get(by_id[nid].get("shape", "process"), SHAPE_SIZE["process"])[0]
            reach = max(reach, abs(offset_in_lane[nid]) + w / 2)

        # ...and, where a skip-level edge has to bypass intervening nodes, a
        # channel for that bypass too. Without the reserved channel the bypass
        # is routed outside the lane and reads as though the neighbouring actor
        # owns the transition. The channel has to clear the leftmost node it
        # passes, which is not necessarily the edge's own endpoints — a sibling
        # sitting further left in the same lane would otherwise be cut through.
        for s, d in forward_edges:
            if levels[d] - levels[s] > 1 and \
               by_id[s].get("lane") == by_id[d].get("lane") and \
               abs(offset_in_lane[s] - offset_in_lane[d]) < 1e-9:
                lane = by_id[s].get("lane")
                lo, hi = levels[s], levels[d]
                left_extent = min(
                    offset_in_lane[nid] - node_width(by_id[nid]) / 2
                    for nid in node_ids
                    if by_id[nid].get("lane") == lane and lo <= levels[nid] <= hi
                )
                off = left_extent - BYPASS_GAP
                bypass_offset[(s, d)] = off
                reach = max(reach, abs(off))

        lane_width = max(LANE_WIDTH, 2 * (reach + LANE_PAD))

        lane_x = {lane: i * lane_width for i, lane in enumerate(lanes)}
        for nid in node_ids:
            base_x = lane_x.get(by_id[nid].get("lane"), 0)
            pos[nid] = (base_x + offset_in_lane[nid], -levels[nid] * Y_GAP)
        for (s, d), off in bypass_offset.items():
            bypass_offset[(s, d)] = lane_x.get(by_id[s].get("lane"), 0) + off
    else:
        for lv in sorted(by_level):
            members = by_level[lv]
            if lv == 0:
                order = members
            else:
                def key(nid):
                    xs = [pos[p][0] for p in preds[nid] if p in pos]
                    return sum(xs) / len(xs) if xs else 0
                order = sorted(members, key=key)
            n = len(order)
            offset = (n - 1) / 2.0
            for i, nid in enumerate(order):
                pos[nid] = ((i - offset) * X_GAP, -lv * Y_GAP)

    for nid, (x, y) in pos.items():
        by_id[nid]["x"], by_id[nid]["y"] = x, y
    return by_id, levels, lane_width, bypass_offset


def draw_lanes(ax, lanes, y_min, y_max, theme, lane_width=LANE_WIDTH):
    if not lanes:
        return
    pad = 1.3
    for i, lane in enumerate(lanes):
        cx = i * lane_width
        left, right = cx - lane_width / 2, cx + lane_width / 2
        fill = "#f8fafc" if i % 2 == 0 else "#ffffff"
        ax.axvspan(left, right, ymin=0, ymax=1, color=fill, zorder=0)
        ax.plot([left, left], [y_min - pad, y_max + pad], color="#cbd5e1", lw=1, zorder=1)
        ax.text(cx, y_max + pad - 0.3, lane, ha="center", fontsize=9.5, fontweight="bold",
                 color=theme["node_text"], zorder=2)
    right_edge = (len(lanes) - 0.5) * lane_width
    ax.plot([right_edge, right_edge], [y_min - pad, y_max + pad], color="#cbd5e1", lw=1, zorder=1)


def draw_forward_edge(ax, by_id, edge, theme, levels, tight=False, bypass_x_override=None):
    s, d = by_id[edge["from"]], by_id[edge["to"]]
    sw, sh = SHAPE_SIZE.get(s.get("shape", "process"), SHAPE_SIZE["process"])
    dw, dh = SHAPE_SIZE.get(d.get("shape", "process"), SHAPE_SIZE["process"])
    level_gap = levels[edge["to"]] - levels[edge["from"]]

    if level_gap > 1 and abs(s["x"] - d["x"]) < 1e-9:
        # Same column, skipping over at least one intervening node: a straight
        # drop would cut through it. Bypass to the left instead, like the loop
        # routing but solid (this is still a normal forward edge). In swimlane
        # mode compute_layout has already reserved this channel inside the
        # lane, so the detour stays with the actor that owns the step.
        bypass_x = (bypass_x_override if bypass_x_override is not None
                    else s["x"] - max(sw, dw) / 2 - BYPASS_GAP)
        x1, y1 = s["x"] - sw / 2, s["y"]
        x2, y2 = d["x"] - dw / 2, d["y"]
        color = theme["line"]
        ax.plot([x1, bypass_x], [y1, y1], color=color, lw=1.3, zorder=2)
        ax.plot([bypass_x, bypass_x], [y1, y2], color=color, lw=1.3, zorder=2)
        ax.annotate("", xy=(x2, y2), xytext=(bypass_x, y2),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.3), zorder=2)
        if edge.get("label"):
            if tight:
                # Lane mode: a horizontal label would hang past the lane divider
                # even though the edge itself no longer does. Run it along the
                # channel instead, as the loop-back labels do.
                ax.text(bypass_x - 0.12, (y1 + y2) / 2, edge["label"], fontsize=7.5,
                         color=theme["accent"], fontweight="bold", rotation=90,
                         ha="center", va="center", zorder=4,
                         bbox=dict(boxstyle="round,pad=0.15", fc=theme["bg"], ec="none"))
            else:
                ax.text(bypass_x - 0.1, (y1 + y2) / 2, edge["label"], fontsize=7.5,
                         color=theme["accent"], fontweight="bold", ha="right", zorder=4,
                         bbox=dict(boxstyle="round,pad=0.15", fc=theme["bg"], ec="none"))
        return

    x1, y1 = s["x"], s["y"] - sh / 2
    x2, y2 = d["x"], d["y"] + dh / 2
    draw_elbow_arrow(ax, x1, y1, x2, y2, theme, direction="TD")
    if edge.get("label"):
        mx = x1 if x1 == x2 else (x1 + x2) / 2
        my = (y1 + y2) / 2
        ax.text(mx + 0.15, my, edge["label"], fontsize=7.5, color=theme["accent"],
                 fontweight="bold", zorder=4,
                 bbox=dict(boxstyle="round,pad=0.15", fc=theme["bg"], ec="none"))


def draw_loop_edge(ax, by_id, edge, theme, loop_x, color):
    s, d = by_id[edge["from"]], by_id[edge["to"]]
    sw, sh = SHAPE_SIZE.get(s.get("shape", "process"), SHAPE_SIZE["process"])
    dw, dh = SHAPE_SIZE.get(d.get("shape", "process"), SHAPE_SIZE["process"])
    x1, y1 = s["x"] + sw / 2, s["y"]
    x2, y2 = d["x"] + dw / 2, d["y"]
    ax.plot([x1, loop_x], [y1, y1], color=color, lw=1.4, linestyle="--", zorder=2)
    ax.plot([loop_x, loop_x], [y1, y2], color=color, lw=1.4, linestyle="--", zorder=2)
    ax.annotate("", xy=(x2, y2), xytext=(loop_x, y2),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.4, linestyle="--"), zorder=2)
    if edge.get("label"):
        ax.text(loop_x + 0.12, (y1 + y2) / 2, edge["label"], fontsize=7.5, color=color,
                 fontweight="bold", rotation=90, va="center", zorder=4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default="flowchart.svg")
    ap.add_argument("--theme", default="default", choices=["default", "hayah"])
    args = ap.parse_args()

    data = load_json(args.input)
    theme = get_theme(args.theme)
    nodes = data["nodes"]
    edges = data["edges"]
    lanes = data.get("lanes")

    node_ids = {n["id"] for n in nodes}
    for e in edges:
        if e["from"] not in node_ids or e["to"] not in node_ids:
            raise ValueError(f"Edge {e} references a node id that isn't in 'nodes'")
    if lanes:
        for n in nodes:
            if n.get("lane") not in lanes:
                raise ValueError(f"Node '{n['id']}' has lane '{n.get('lane')}' "
                                  f"not present in top-level 'lanes' list {lanes}")

    forward = [(e["from"], e["to"]) for e in edges if not e.get("loop")]
    loops = [e for e in edges if e.get("loop")]

    by_id, levels, lane_width, bypass_x = compute_layout(nodes, forward, lanes)

    xs = [n["x"] for n in nodes]
    ys = [n["y"] for n in nodes]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    # Long single-column chains (many levels, little horizontal spread) need a
    # taller figure, not smaller text — fixed figsize would let matplotlib's
    # fixed-point-size labels overflow narrow, deeply-stacked shapes.
    x_span = (x_max - x_min) + (lane_width * 2 if lanes else 4.5)
    y_span = (y_max - y_min) + 4
    fig_w = max(7.0, min(22.0, x_span * 0.85))
    fig_h = max(6.0, min(48.0, y_span * 0.6))

    fig, ax = new_figure(theme["bg"], width=fig_w, height=fig_h)

    draw_lanes(ax, lanes, y_min, y_max, theme, lane_width)

    has_bypass = any(
        (levels[e["to"]] - levels[e["from"]] > 1)
        and abs(by_id[e["from"]]["x"] - by_id[e["to"]]["x"]) < 1e-9
        for e in edges if not e.get("loop")
    )

    for e in edges:
        if not e.get("loop"):
            draw_forward_edge(ax, by_id, e, theme, levels, tight=bool(lanes),
                               bypass_x_override=bypass_x.get((e["from"], e["to"])))

    loop_base = (x_max if not lanes else (len(lanes) - 0.5) * lane_width) + 0.9
    for i, e in enumerate(loops):
        draw_loop_edge(ax, by_id, e, theme, loop_base + i * 0.55, theme["critical"])

    for n in nodes:
        draw_shape(ax, n, theme)

    pad = 1.6
    # In lane mode the bypass channel lives inside the lane, so no extra
    # left margin is needed to hold it.
    left_pad = pad + (1.6 if has_bypass and not lanes else 0)
    right_pad = pad + (len(loops) * 0.55 if loops else 0)
    ax.set_xlim(x_min - left_pad, x_max + right_pad + (lane_width if lanes else 0))
    ax.set_ylim(y_min - pad, y_max + pad + (0.6 if lanes else 0))

    if data.get("title"):
        ax.text((x_min + x_max) / 2, y_max + pad + (1.0 if lanes else 0.4), data["title"],
                 ha="center", fontsize=13, fontweight="bold", color=theme["node_text"], zorder=6)

    save_fig(fig, args.output)
    print(f"Wrote {args.output}")
    print(f"Levels: {max(levels.values()) + 1} | Loop-back edges: {len(loops)}"
          + (f" | Lanes: {lanes}" if lanes else ""))


if __name__ == "__main__":
    main()
