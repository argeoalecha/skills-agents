---
name: diagram-toolkit
description: >-
  Renders mind maps, org charts, project schedules with real Critical Path
  Method (CPM) analysis, flow-tree/issue-tree diagrams for brainstorm
  output, ISO 5807-style process flowcharts (swimlanes, branching,
  convergence, loop-backs), and hand-drawn flowcharts as clean SVG/PNG
  files. Use whenever the user wants to map out ideas, show reporting
  lines/team structure, lay out a project timeline or critical path, turn
  a brainstorm into a branching diagram, or diagram a procedure/SOP/
  workflow including retries or cross-functional handoffs — even without
  those exact words ("map out the team", "diagram this approval process",
  "what happens if the check fails"). Prefer this over freehand
  SVG/matplotlib for these six types — it does real layout math (radial
  tree, hierarchical tree, layered/topological, forward/backward CPM,
  DAG layering with loop-back routing) instead of guessing coordinates.
  NOT for electrical one-lines or CAD/DXF — use short-circuit-study,
  electrical-sld, or the QCAD/FreeCAD pipeline instead.
---

# Diagram Toolkit

Six renderers, each doing real layout computation (not just decorative boxes) and
producing a standalone SVG or PNG file:

| Script | Diagram type | Layout algorithm |
|---|---|---|
| `scripts/render_mindmap.py` | Mind map | Radial tree, angle allocated proportional to leaf count |
| `scripts/render_orgchart.py` | Org chart | Top-down hierarchical tree, elbow connectors |
| `scripts/render_flowtree.py` | Flow tree / brainstorm & issue tree | Directional layered tree (TD or LR), arrowed connectors, per-node status (selected/discarded/parked) |
| `scripts/render_flowchart.py` | Process flowchart / SOP / procedure | DAG layering (longest-path levels) with barycenter ordering, optional swimlanes, bypass-routed skip-level edges, side-routed loop-backs |
| `scripts/render_critical_path.py` | Project schedule / Gantt / critical path | **Real CPM**: forward pass (ES/EF), backward pass (LS/LF), float, critical path — plus optional AON network diagram |
| `scripts/render_sketch.py` | Hand-drawn flowchart / process sketch | Layered (topological-rank) layout, rendered in matplotlib's xkcd hand-drawn mode |

All six share `scripts/dtk_common.py` for theming, box/connector drawing, and layout helpers — read it once if you need to add a new node shape or theme.

## Workflow

1. **Build the input JSON** from what the user described (see schemas below). Do this yourself — don't ask the user to write JSON unless they want to.
2. **Run the script** with `bash_tool`, e.g.:
   ```bash
   python3 scripts/render_mindmap.py input.json -o /mnt/user-data/outputs/mindmap.svg --theme default
   ```
3. **View the output** with the `view` tool before presenting it — check for label overlap or a cramped layout (very wide trees or long labels are the main failure mode; see Troubleshooting).
4. Save to `/mnt/user-data/outputs/` and call `present_files`.

Output format is inferred from the `-o` extension — use `.svg` for anything that will be edited or embedded (scales cleanly, small file size), `.png` for a quick chat preview or when the user just wants an image.

Two themes are built in: `default` (neutral slate/blue, safe for any client) and `hayah` (teal/coral, matches the user's Hayah-AI Classic brand — use this when the deliverable is client-facing Hayah-AI material, not by default for generic requests).

## Input schemas

### Mind map (`render_mindmap.py`)
```json
{
  "title": "Central Topic",
  "children": [
    {"label": "Branch A", "children": [{"label": "Sub A1"}, {"label": "Sub A2"}]},
    {"label": "Branch B", "children": [{"label": "Sub B1"}]}
  ]
}
```
Each top-level branch under `title` gets its own color, inherited by its descendants. Nest `children` as deep as needed — leaf count drives angular spacing automatically.

### Org chart (`render_orgchart.py`)
```json
{
  "name": "Person or Role",
  "title": "Job title / function",
  "children": [ { "name": "...", "title": "...", "children": [...] } ]
}
```
`title` is optional per node. Box widths auto-size to fit subtrees so siblings never overlap.

### Flow tree / brainstorm output (`render_flowtree.py`)
```json
{
  "direction": "TD",
  "root": {
    "label": "How might we reduce onboarding time?",
    "status": "root",
    "children": [
      {"label": "Automate document collection", "status": "selected", "children": [
        {"label": "OCR intake form", "status": "selected"}
      ]},
      {"label": "Full system replatform", "status": "discarded"},
      {"label": "Hire a coordinator", "status": "parked"}
    ]
  }
}
```
This is the shape a brainstorm session actually produces: a root question/problem, branching approaches, and a verdict on each. It's distinct from the mind map (radial, free association, no notion of "kept vs. dropped") and the org chart (people, undirected lines) — this one has **directional arrows** and a **status per node**:
- `selected` → green fill, bold — the kept/recommended path
- `discarded` → greyed out, dashed border, faded text — ruled out but visible for context
- `parked` → dotted border, italic text — worth revisiting later
- omitted or `default` → plain node
- `root` is set automatically on the top node's style even if you don't tag it

`direction` is `"TD"` (top-down, default) or `"LR"` (left-to-right — use this for wide/bushy trees so labels don't get cramped horizontally). A small legend renders automatically in the corner whenever any non-default status is used, so don't add your own.

If you're rendering the direct output of the `brainstorm-ideas` skill, this is almost always the right renderer — map the McKinsey/IDEO-style structure straight into `root`/`children`, and use `status` to capture whatever the session converged on.

### Process flowchart / SOP (`render_flowchart.py`)
```json
{
  "title": "Alarm Response Procedure",
  "lanes": ["SCADA System", "Field Technician", "Campus Engineer"],
  "nodes": [
    {"id": "start", "label": "Alarm triggered", "shape": "terminator", "lane": "SCADA System"},
    {"id": "notify", "label": "Send alert", "shape": "process", "lane": "SCADA System"},
    {"id": "ack", "label": "Acknowledged in 15 min?", "shape": "decision", "lane": "Field Technician"},
    {"id": "dispatch", "label": "Dispatch to site", "shape": "process", "lane": "Field Technician"},
    {"id": "log", "label": "Log resolution", "shape": "document", "lane": "Field Technician"},
    {"id": "end", "label": "Alarm cleared", "shape": "terminator", "lane": "SCADA System"}
  ],
  "edges": [
    {"from": "start", "to": "notify"},
    {"from": "notify", "to": "ack"},
    {"from": "ack", "to": "dispatch", "label": "Yes"},
    {"from": "dispatch", "to": "log"},
    {"from": "log", "to": "end"},
    {"from": "log", "to": "ack", "label": "Recurs within 24h", "loop": true}
  ]
}
```
This is the one for an actual procedure — an SOP, an alarm-response workflow, an approval process — where the other tree-based renderers fall short because they can't represent **convergence** (two branches rejoining a common step) or **loops** (retry/recheck going back to an earlier step). `render_flowtree.py` is a pure tree (one parent per node, no loops); this one is a general DAG.

`shape` per node: `terminator` (start/end, rounded), `process` (a step, sharp rectangle), `decision` (diamond, branches with edge `label`s like "Yes"/"No"), `io` (parallelogram, input/output), `document` (wavy-bottom rectangle, a report/log/record), `predefined` (rectangle with side bars, a call-out to another procedure), `connector` (small circle, an on-page reference marker).

`edge.loop: true` marks an intentional loop-back (e.g. "recheck if it recurs") — it's excluded from the top-down layering and instead routed as a dashed line around the right side of the diagram, so it reads as "feedback," not as the main flow. **Any edge that goes from a later step back to an earlier one must be marked `loop: true`** — otherwise the script treats it as an actual cycle and raises an error rather than silently drawing something misleading (see Troubleshooting).

`lanes` (optional, top-level list) turns on swimlanes: give each node a `lane` matching one of the listed names, and the diagram organizes into vertical columns (cross-functional flowchart convention — "who does what," reading top-to-bottom for sequence and left-to-right for ownership). Omit `lanes` entirely for a plain single-flow diagram.

If you're rendering the output of the `graph-topology-planner` skill as a client-facing or presentation deliverable (rather than the dev-facing Mermaid it produces by default), this is the renderer — it's the only one here that's a general DAG, matching that skill's Nodes table: map its Topology clusters to `lanes`, Gates to a `decision` shape or a dedicated "Human" lane, and any Evaluator-Optimizer revise loop to `edge.loop: true`.

### Critical path (`render_critical_path.py`)
```json
{
  "tasks": [
    {"id": "A", "name": "Task name", "duration": 3, "deps": []},
    {"id": "B", "name": "Task name", "duration": 10, "deps": ["A"]}
  ]
}
```
- `id` must be unique; `deps` lists predecessor `id`s (empty list = project start).
- `duration` is a plain number — days, weeks, whatever unit the user is planning in. Label the axis accordingly when you present it.
- The script **computes** ES/EF/LS/LF/float via a real forward+backward pass (see `compute_cpm()` in the script) — it will raise an error on a dependency cycle or an unknown task id rather than silently producing a wrong chart.
- Add `--network out.svg` for a second AON dependency-network image with the critical path highlighted, and `--json cpm.json` to dump the full computed table (useful if the user wants the numbers, not just the picture).

### Sketch / hand-drawn flowchart (`render_sketch.py`)
```json
{
  "nodes": [
    {"id": "start", "label": "Start", "shape": "oval"},
    {"id": "q1", "label": "Condition?", "shape": "diamond"},
    {"id": "step", "label": "Do the thing", "shape": "box"}
  ],
  "edges": [
    {"from": "start", "to": "q1"},
    {"from": "q1", "to": "step", "label": "yes"},
    {"from": "step", "to": "q1", "label": "retry", "loop": true}
  ]
}
```
`shape` ∈ `box` (process), `diamond` (decision), `oval` (start/end) — defaults to `box`. Edge `label` is optional.

`edge.loop: true` works the same way as in `render_flowchart.py`: it marks a retry/recheck back to an earlier step, keeps that edge out of the layering, and draws it as a dashed curve bowed away from the main flow. Any backwards edge must be marked, or it counts as a real cycle and the script errors out.
**Keep node fills light** for this renderer — matplotlib's xkcd hand-drawn text effect turns white/light text on a dark fill into an illegible smudge. Dark text on a light fill stays readable through the wobble; that's why the theme's oval nodes use `node_fill`/`accent`-outline rather than a solid accent fill.

## Troubleshooting

- **Labels overlapping / diagram too cramped**: shorten the label. `wrap_text` wraps at a fixed character width and *will* split a long unbroken token (a URL, a part number) mid-word, so nothing runs off the side — but the break lands at an arbitrary character. The mind map sizes each box to the wrapped result, so extra lines are absorbed; the org chart, flow tree and flowchart use fixed box heights, so a label wrapping to several lines overflows those boxes vertically. Shortening the label is the fix. For a one-off, `new_figure()` accepts `width=`/`height=`.
- **Mind map branch collides with its neighbor**: usually means one branch has far more leaves than its siblings — either flatten it a level or increase `--radius-step`.
- **Critical path script errors out**: it means either a cycle in `deps`, or a `deps` entry referencing an `id` that doesn't exist — both are real input errors, not a formatting issue, fix the task list.
- **Flowchart or sketch script raises "Cycle detected"**: an edge goes backward through the DAG without being marked `"loop": true` — either mark it as a loop-back or fix the logic; the script won't guess which you meant. Both `render_flowchart.py` and `render_sketch.py` honour `loop`.
- **Flowchart edge passes visually close to an unrelated node**: the layout auto-bypasses same-column skip-level edges to the left, but with three or more stacked skip-level edges in a lane-less diagram it can still get tight — adding `lanes` (even trivial ones, e.g. `["Process"]` isn't useful, but 2–3 real actors usually is) gives the layout more horizontal room and is usually the better fix.
- **Font warnings in stderr about "xkcd"/"Comic Neue" fonts**: harmless — matplotlib falls back to a default hand-drawn-adjacent font. Doesn't affect output quality.

## When NOT to use this skill

- CAD-grade electrical one-lines, panel schedules, arc-flash/short-circuit/protection-coordination studies → `short-circuit-study` skill, `electrical-sld` skill, or the QCAD CE/FreeCAD DXF pipeline.
- Software/system architecture diagrams meant to live in a git repo next to code → plain Mermaid is usually the better fit (renders natively on GitHub); this toolkit doesn't do diagram-as-code.
- Pixel-precise UI mockups or wireframes → `frontend-design` skill.
