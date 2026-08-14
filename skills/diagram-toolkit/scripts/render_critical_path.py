#!/usr/bin/env python3
"""
render_critical_path.py — Critical Path Method (CPM) calculator + renderer.

Input JSON shape (durations in whatever unit you want — days, weeks, hours):
{
  "tasks": [
    {"id": "A", "name": "Site survey",        "duration": 3, "deps": []},
    {"id": "B", "name": "Permit application",  "duration": 10, "deps": ["A"]},
    {"id": "C", "name": "Procurement",         "duration": 14, "deps": ["A"]},
    {"id": "D", "name": "Installation",        "duration": 7, "deps": ["B", "C"]},
    {"id": "E", "name": "Commissioning",       "duration": 4, "deps": ["D"]}
  ]
}

This performs an actual forward pass (ES/EF) and backward pass (LS/LF) —
not a decorative gantt bar — and marks zero-float tasks as critical.

Usage:
  python3 render_critical_path.py input.json -o schedule.svg \
      [--theme default|hayah] [--network network.svg] [--json cpm.json]

--network additionally renders a dependency network (AON) diagram with the
critical path highlighted. --json dumps the computed ES/EF/LS/LF/float table.
"""
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from dtk_common import (get_theme, wrap_text, new_figure, draw_box, draw_connector,
                         save_fig, load_json, layered_positions)

NODE_W, NODE_H = 2.2, 1.0


def compute_cpm(tasks):
    by_id = {t["id"]: dict(t) for t in tasks}
    order = topo_sort(by_id)

    # Forward pass
    for tid in order:
        t = by_id[tid]
        deps = t.get("deps", [])
        t["ES"] = max((by_id[d]["EF"] for d in deps), default=0)
        t["EF"] = t["ES"] + t["duration"]

    project_end = max(t["EF"] for t in by_id.values())

    # Successor map for backward pass
    succs = {tid: [] for tid in by_id}
    for tid, t in by_id.items():
        for d in t.get("deps", []):
            succs[d].append(tid)

    for tid in reversed(order):
        t = by_id[tid]
        if not succs[tid]:
            t["LF"] = project_end
        else:
            t["LF"] = min(by_id[s]["LS"] for s in succs[tid])
        t["LS"] = t["LF"] - t["duration"]

    for t in by_id.values():
        t["float"] = t["LS"] - t["ES"]
        t["critical"] = abs(t["float"]) < 1e-9

    return by_id, order, project_end


def topo_sort(by_id):
    visited, order = set(), []

    def visit(tid, stack):
        if tid in visited:
            return
        if tid in stack:
            raise ValueError(f"Dependency cycle detected involving task '{tid}'")
        for d in by_id[tid].get("deps", []):
            if d not in by_id:
                raise ValueError(f"Task '{tid}' depends on unknown task '{d}'")
            visit(d, stack | {tid})
        visited.add(tid)
        order.append(tid)

    for tid in by_id:
        visit(tid, frozenset())
    return order


def task_label(tid, name, width=26, max_lines=2):
    """Axis label for one task. Rows are one unit apart, so the label is capped
    at two lines to stay off its neighbours — but a name that doesn't fit ends
    in an ellipsis rather than being silently cut at the first line."""
    lines = wrap_text(name, width).split("\n")
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:width - 1].rstrip() + "…"
    return f"{tid} — " + "\n".join(lines)


def render_gantt(by_id, order, theme, out_path):
    fig, ax = new_figure(theme["bg"], aspect="auto")
    ax.axis("on")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_facecolor(theme["bg"])

    order_by_es = sorted(order, key=lambda tid: (by_id[tid]["ES"], tid))
    y_labels = []
    for i, tid in enumerate(reversed(order_by_es)):
        t = by_id[tid]
        y = i
        color = theme["critical"] if t["critical"] else theme["accent"]
        ax.barh(y, t["duration"], left=t["ES"], height=0.55, color=color,
                edgecolor="#00000030", zorder=3)
        if t["float"] > 1e-9:
            ax.barh(y, t["float"], left=t["EF"], height=0.22,
                    color=theme["line"], alpha=0.35, zorder=2)
        ax.text(t["ES"] + t["duration"] / 2, y, f'{tid} ({t["duration"]})',
                 ha="center", va="center", fontsize=8.5, color="#ffffff",
                 fontweight="bold", zorder=4)
        y_labels.append(task_label(tid, t["name"]))

    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels, fontsize=8.5)
    ax.set_xlabel("Time")
    # Worded without naming the colour: the previous version picked the wording
    # by comparing the theme's critical colour to a hex literal, so a palette
    # change would have left the title asserting the wrong colour.
    ax.set_title("Project schedule — critical path highlighted, float in grey",
                  fontsize=11, loc="left")
    ax.grid(axis="x", color="#00000015", zorder=0)
    save_fig(fig, out_path)
    print(f"Wrote {out_path}")


def render_network(by_id, order, theme, out_path):
    edges = []
    for tid, t in by_id.items():
        for d in t.get("deps", []):
            edges.append((d, tid))
    pos, _ = layered_positions(list(by_id.keys()), edges, x_gap=2.8, y_gap=1.6)

    fig, ax = new_figure(theme["bg"])
    # Stop each connector at the box border, not the box centre — the nodes are
    # drawn at a higher zorder, so a centre-to-centre arrow has its head buried
    # under the target box and the graph reads as undirected. Predecessors are
    # always a level above their successors, hence bottom edge -> top edge.
    for s, d in edges:
        crit = by_id[s]["critical"] and by_id[d]["critical"] and \
               abs(by_id[s]["EF"] - by_id[d]["ES"]) < 1e-9
        x1, y1 = pos[s]; x2, y2 = pos[d]
        draw_connector(ax, x1, y1 - NODE_H / 2, x2, y2 + NODE_H / 2, theme,
                        color=theme["critical"] if crit else theme["line"],
                        lw=2.4 if crit else 1.3, arrow=True)

    for tid, (x, y) in pos.items():
        t = by_id[tid]
        label = f'{tid}\n{wrap_text(t["name"], 16)}\nES{t["ES"]} EF{t["EF"]}  float {t["float"]}'
        fill = theme["critical"] if t["critical"] else theme["node_fill"]
        text_color = "#ffffff" if t["critical"] else theme["node_text"]
        draw_box(ax, x, y, NODE_W, NODE_H, label, theme, fill=fill, fontsize=7.5,
                  text_color=text_color, zorder=4)

    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs) - 2, max(xs) + 2)
    ax.set_ylim(min(ys) - 1.5, max(ys) + 1.5)
    save_fig(fig, out_path)
    print(f"Wrote {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Path to task list JSON")
    ap.add_argument("-o", "--output", default="schedule.svg", help="Gantt chart output path")
    ap.add_argument("--network", help="Optional AON network diagram output path")
    ap.add_argument("--json", help="Optional path to dump computed CPM table as JSON")
    ap.add_argument("--theme", default="default", choices=["default", "hayah"])
    args = ap.parse_args()

    data = load_json(args.input)
    theme = get_theme(args.theme)
    by_id, order, project_end = compute_cpm(data["tasks"])

    render_gantt(by_id, order, theme, args.output)
    if args.network:
        render_network(by_id, order, theme, args.network)

    crit_path = [tid for tid in sorted(by_id, key=lambda t: by_id[t]["ES"]) if by_id[tid]["critical"]]
    print(f"Project duration: {project_end}")
    print(f"Critical path ({len(crit_path)} tasks): {' -> '.join(crit_path)}")

    if args.json:
        with open(args.json, "w") as f:
            json.dump({"project_duration": project_end,
                       "critical_path": crit_path,
                       "tasks": by_id}, f, indent=2)
        print(f"Wrote {args.json}")


if __name__ == "__main__":
    main()
