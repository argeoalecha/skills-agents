"""
dtk_common.py — shared layout, theming, and drawing helpers for diagram-toolkit.

Not meant to be run directly. Imported by render_mindmap.py, render_orgchart.py,
render_critical_path.py, and render_sketch.py.
"""
import json
import math
import textwrap
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse, Polygon, Rectangle

# ---------------------------------------------------------------------------
# Themes
# ---------------------------------------------------------------------------
THEMES = {
    # Neutral, works for any client deliverable.
    "default": {
        "bg": "#ffffff",
        "node_fill": "#eef2f7",
        "node_edge": "#334155",
        "node_text": "#1e293b",
        "line": "#64748b",
        "critical": "#dc2626",
        "accent": "#2563eb",
        "palette": ["#2563eb", "#0891b2", "#7c3aed", "#d97706", "#16a34a", "#db2777"],
    },
    # Hayah-AI Classic — teal / coral / mint accents.
    "hayah": {
        "bg": "#ffffff",
        "node_fill": "#e6fbf7",
        "node_edge": "#0f766e",
        "node_text": "#134e4a",
        "line": "#5b7b78",
        "critical": "#f97316",
        "accent": "#0f766e",
        "palette": ["#0f766e", "#0ea5a5", "#f97316", "#7c3aed", "#16a34a", "#db2777"],
    },
}


def get_theme(name):
    return THEMES.get(name, THEMES["default"])


def wrap_text(text, width=18):
    return "\n".join(textwrap.wrap(str(text), width=width)) or str(text)


def new_figure(bg="#ffffff", width=11, height=8, aspect="equal"):
    """Node diagrams want aspect="equal" so shapes aren't skewed (a diamond must
    read as a diamond). Charts whose axes carry different units — the CPM gantt,
    where x is time and y is a task index — must pass aspect="auto", or the
    figure gets stretched to the arbitrary ratio between those units."""
    fig, ax = plt.subplots(figsize=(width, height))
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.axis("off")
    if aspect and aspect != "auto":
        ax.set_aspect(aspect, adjustable="box")
    return fig, ax


def draw_box(ax, x, y, w, h, text, theme, fill=None, edge=None, fontsize=9,
             fontweight="normal", text_color=None, zorder=3, linestyle="-",
             alpha=1.0, fontstyle="normal"):
    fill = fill or theme["node_fill"]
    edge = edge or theme["node_edge"]
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.4, edgecolor=edge, facecolor=fill, zorder=zorder,
        linestyle=linestyle, alpha=alpha,
    )
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
             fontweight=fontweight, fontstyle=fontstyle,
             color=text_color or theme["node_text"], zorder=zorder + 1, alpha=alpha)
    return box


def draw_ellipse(ax, x, y, w, h, text, theme, fill=None, edge=None, fontsize=9, zorder=3):
    fill = fill or theme["node_fill"]
    edge = edge or theme["node_edge"]
    e = Ellipse((x, y), w, h, linewidth=1.4, edgecolor=edge, facecolor=fill, zorder=zorder)
    ax.add_patch(e)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
             color=theme["node_text"], zorder=zorder + 1)
    return e


def draw_diamond(ax, x, y, w, h, text, theme, fill=None, edge=None, fontsize=8.5, zorder=3):
    fill = fill or theme["node_fill"]
    edge = edge or theme["node_edge"]
    pts = [(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)]
    d = Polygon(pts, closed=True, linewidth=1.4, edgecolor=edge, facecolor=fill, zorder=zorder)
    ax.add_patch(d)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
             color=theme["node_text"], zorder=zorder + 1)
    return d


def draw_rect(ax, x, y, w, h, text, theme, fill=None, edge=None, fontsize=9,
              fontweight="normal", text_color=None, zorder=3, linestyle="-"):
    """Sharp-cornered rectangle — ISO 5807 'process' box (distinct from draw_box's rounded corners)."""
    fill = fill or theme["node_fill"]
    edge = edge or theme["node_edge"]
    r = Rectangle((x - w / 2, y - h / 2), w, h, linewidth=1.4, edgecolor=edge,
                  facecolor=fill, zorder=zorder, linestyle=linestyle)
    ax.add_patch(r)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, fontweight=fontweight,
             color=text_color or theme["node_text"], zorder=zorder + 1)
    return r


def draw_parallelogram(ax, x, y, w, h, text, theme, fill=None, edge=None, fontsize=8.5,
                        zorder=3, skew=0.3):
    """ISO 5807 'input/output' shape."""
    fill = fill or theme["node_fill"]
    edge = edge or theme["node_edge"]
    pts = [(x - w / 2 + skew, y + h / 2), (x + w / 2 + skew, y + h / 2),
           (x + w / 2 - skew, y - h / 2), (x - w / 2 - skew, y - h / 2)]
    p = Polygon(pts, closed=True, linewidth=1.4, edgecolor=edge, facecolor=fill, zorder=zorder)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
             color=theme["node_text"], zorder=zorder + 1)
    return p


def draw_document(ax, x, y, w, h, text, theme, fill=None, edge=None, fontsize=8.5, zorder=3):
    """ISO 5807 'document' shape — rectangle with a wavy bottom edge."""
    fill = fill or theme["node_fill"]
    edge = edge or theme["node_edge"]
    left, right, top, bot = x - w / 2, x + w / 2, y + h / 2, y - h / 2
    n = 24
    bottom_pts = []
    for i in range(n + 1):
        t = i / n
        bx = left + t * w
        by = bot + 0.07 * math.sin(t * 2 * math.pi)
        bottom_pts.append((bx, by))
    verts = [(left, top), (right, top)] + bottom_pts[::-1]
    poly = Polygon(verts, closed=True, linewidth=1.4, edgecolor=edge, facecolor=fill, zorder=zorder)
    ax.add_patch(poly)
    ax.text(x, y + 0.06, text, ha="center", va="center", fontsize=fontsize,
             color=theme["node_text"], zorder=zorder + 1)
    return poly


def draw_predefined_process(ax, x, y, w, h, text, theme, fill=None, edge=None, fontsize=8.5, zorder=3):
    """ISO 5807 'predefined process' (subroutine) — rectangle with a bar near each edge."""
    fill = fill or theme["node_fill"]
    edge = edge or theme["node_edge"]
    draw_rect(ax, x, y, w, h, "", theme, fill=fill, edge=edge, zorder=zorder)
    bar_x = w * 0.15
    ax.plot([x - w / 2 + bar_x, x - w / 2 + bar_x], [y - h / 2, y + h / 2],
             color=edge, lw=1.2, zorder=zorder + 1)
    ax.plot([x + w / 2 - bar_x, x + w / 2 - bar_x], [y - h / 2, y + h / 2],
             color=edge, lw=1.2, zorder=zorder + 1)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
             color=theme["node_text"], zorder=zorder + 2)


def draw_connector(ax, x1, y1, x2, y2, theme, color=None, lw=1.3, style="-",
                    curved=False, rad=0.15, arrow=False, zorder=1):
    color = color or theme["line"]
    style_kw = dict(arrowstyle="-|>" if arrow else "-", color=color, lw=lw,
                     linestyle=style, zorder=zorder, mutation_scale=14)
    if curved:
        a = FancyArrowPatch((x1, y1), (x2, y2), connectionstyle=f"arc3,rad={rad}", **style_kw)
    else:
        a = FancyArrowPatch((x1, y1), (x2, y2), **style_kw)
    ax.add_patch(a)
    return a


def draw_elbow(ax, x1, y1, x2, y2, theme, color=None, lw=1.3, zorder=1):
    """Right-angle connector: down from parent, across, down into child. Classic org-chart style."""
    color = color or theme["line"]
    my = (y1 + y2) / 2
    ax.plot([x1, x1], [y1, my], color=color, lw=lw, zorder=zorder)
    ax.plot([x1, x2], [my, my], color=color, lw=lw, zorder=zorder)
    ax.plot([x2, x2], [my, y2], color=color, lw=lw, zorder=zorder)


def draw_elbow_arrow(ax, x1, y1, x2, y2, theme, color=None, lw=1.3, zorder=1,
                      linestyle="-", direction="TD"):
    """Directional right-angle connector with an arrowhead into the child. Flowchart style."""
    color = color or theme["line"]
    if direction == "LR":
        mx = (x1 + x2) / 2
        ax.plot([x1, mx], [y1, y1], color=color, lw=lw, linestyle=linestyle, zorder=zorder)
        ax.plot([mx, mx], [y1, y2], color=color, lw=lw, linestyle=linestyle, zorder=zorder)
        ax.annotate("", xy=(x2, y2), xytext=(mx, y2),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, linestyle=linestyle),
                    zorder=zorder)
    else:
        my = (y1 + y2) / 2
        ax.plot([x1, x1], [y1, my], color=color, lw=lw, linestyle=linestyle, zorder=zorder)
        ax.plot([x1, x2], [my, my], color=color, lw=lw, linestyle=linestyle, zorder=zorder)
        ax.annotate("", xy=(x2, y2), xytext=(x2, my),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, linestyle=linestyle),
                    zorder=zorder)


def save_fig(fig, out_path, dpi=180):
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)


def load_json(path):
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Layered (topological) layout — shared by sketch flowcharts and CPM networks
# ---------------------------------------------------------------------------
def topo_levels(node_ids, edges):
    """Return {node_id: level} where level = longest path length from any source.
    Raises ValueError on a true cycle rather than silently mislabeling it as
    level 0 — for a flowchart, mark intentional loop-back edges separately
    (excluded from this call) instead of feeding them in here."""
    preds = {n: [] for n in node_ids}
    for s, d in edges:
        if d in preds:
            preds[d].append(s)
    level = {}

    def get_level(n, stack):
        if n in level:
            return level[n]
        if n in stack:
            raise ValueError(f"Cycle detected at node '{n}' — mark loop-back edges "
                              'with "loop": true so they are excluded from layering')
        if not preds[n]:
            level[n] = 0
            return 0
        stack = stack | {n}
        lv = 1 + max(get_level(p, stack) for p in preds[n])
        level[n] = lv
        return lv

    for n in node_ids:
        get_level(n, frozenset())
    return level


def layered_positions(node_ids, edges, x_gap=2.6, y_gap=1.8):
    """Assign (x, y) per node using topo_levels, centering each level horizontally."""
    level = topo_levels(node_ids, edges)
    by_level = {}
    for n in node_ids:
        by_level.setdefault(level[n], []).append(n)
    pos = {}
    max_width = max(len(v) for v in by_level.values())
    for lv, members in by_level.items():
        n = len(members)
        offset = (n - 1) / 2.0
        for i, node in enumerate(members):
            x = (i - offset) * x_gap
            y = -lv * y_gap
            pos[node] = (x, y)
    return pos, level
