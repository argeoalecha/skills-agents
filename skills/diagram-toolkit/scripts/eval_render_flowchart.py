#!/usr/bin/env python3
"""Functional eval for diagram-toolkit.

Covers every renderer against its shipped example, the LR/fill/accent/eyebrow
paths, and the guard rails that are supposed to raise rather than mis-draw.

Run: python3 eval_render_flowchart.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL / "scripts"
EXAMPLES = SKILL / "examples"
OUT = Path(tempfile.mkdtemp(prefix="dtk_eval_"))

results = []


def run(name, script, payload, expect="ok", extra_args=()):
    """expect: "ok" for a successful render, else a substring required in stderr."""
    if isinstance(payload, Path):
        inp = payload
    else:
        inp = OUT / f"{name.replace('::', '_')}.json"
        inp.write_text(json.dumps(payload))
    outfile = OUT / f"{name.replace('::', '_')}.svg"
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), str(inp), "-o", str(outfile), *extra_args],
        capture_output=True, text=True)
    if expect == "ok":
        ok = proc.returncode == 0 and outfile.exists() and outfile.stat().st_size > 0
        detail = "" if ok else (proc.stderr.strip().splitlines() or ["no output"])[-1]
    else:
        ok = proc.returncode != 0 and expect in proc.stderr
        detail = "" if ok else f"expected guard {expect!r}, got rc={proc.returncode}"
    results.append((name, ok, detail))


# 1. Every renderer against its shipped example.
for script, example in [
    ("render_mindmap.py", "mindmap_example.json"),
    ("render_orgchart.py", "orgchart_example.json"),
    ("render_flowtree.py", "flowtree_example.json"),
    ("render_flowchart.py", "flowchart_example.json"),
    ("render_critical_path.py", "critical_path_example.json"),
    ("render_sketch.py", "sketch_example.json"),
]:
    run(f"example::{script}", script, EXAMPLES / example)

# 2. The hayah theme still renders (the accent override must not break theming).
run("theme::hayah", "render_flowchart.py", EXAMPLES / "flowchart_example.json",
    extra_args=("--theme", "hayah"))

# 3. TD regression: lanes + decision branch + convergence + loop-back together.
TD = {
    "title": "Alarm Response Procedure",
    "lanes": ["SCADA System", "Field Technician", "Campus Engineer"],
    "nodes": [
        {"id": "start", "label": "Alarm triggered", "shape": "terminator", "lane": "SCADA System"},
        {"id": "notify", "label": "Send alert", "shape": "process", "lane": "SCADA System"},
        {"id": "ack", "label": "Acknowledged in 15 min?", "shape": "decision", "lane": "Field Technician"},
        {"id": "dispatch", "label": "Dispatch to site", "shape": "process", "lane": "Field Technician"},
        {"id": "escalate", "label": "Escalate to engineer", "shape": "process", "lane": "Campus Engineer"},
        {"id": "log", "label": "Log resolution", "shape": "document", "lane": "Field Technician"},
        {"id": "end", "label": "Alarm cleared", "shape": "terminator", "lane": "SCADA System"},
    ],
    "edges": [
        {"from": "start", "to": "notify"},
        {"from": "notify", "to": "ack"},
        {"from": "ack", "to": "dispatch", "label": "Yes"},
        {"from": "ack", "to": "escalate", "label": "No"},
        {"from": "escalate", "to": "dispatch"},
        {"from": "dispatch", "to": "log"},
        {"from": "log", "to": "end"},
        {"from": "log", "to": "ack", "label": "Recurs in 24h", "loop": True},
    ],
}
run("td::lanes+branch+converge+loop", "render_flowchart.py", TD)

# 4. LR plus the per-node and top-level color overrides.
LR = {
    "title": "Ingestion Pipeline",
    "eyebrow": "Data Platform",
    "accent": "#7c3aed",
    "direction": "LR",
    "nodes": [
        {"id": "source", "label": "Source system", "shape": "terminator",
         "fill": "#0a3d3a", "text_color": "#ffffff"},
        {"id": "extract", "label": "Extract", "shape": "process"},
        {"id": "transform", "label": "Transform", "shape": "process", "fill": "#ff6b47"},
        {"id": "load", "label": "Load to warehouse", "shape": "io"},
        {"id": "dest", "label": "Warehouse", "shape": "terminator"},
    ],
    "edges": [
        {"from": "source", "to": "extract"},
        {"from": "extract", "to": "transform"},
        {"from": "transform", "to": "load", "label": "validated"},
        {"from": "load", "to": "dest"},
    ],
}
run("lr::fill+accent+eyebrow", "render_flowchart.py", LR)

# LR with a real fan-out/fan-in, which exercises barycenter ordering on the y axis.
run("lr::fanout+fanin", "render_flowchart.py", {
    "direction": "LR",
    "nodes": [
        {"id": "a", "label": "Intake", "shape": "terminator"},
        {"id": "b1", "label": "Branch one", "shape": "process"},
        {"id": "b2", "label": "Branch two", "shape": "process"},
        {"id": "b3", "label": "Branch three", "shape": "process"},
        {"id": "j", "label": "Join", "shape": "process"},
    ],
    "edges": [
        {"from": "a", "to": "b1"}, {"from": "a", "to": "b2"}, {"from": "a", "to": "b3"},
        {"from": "b1", "to": "j"}, {"from": "b2", "to": "j"}, {"from": "b3", "to": "j"},
    ],
})

# 5. Guard rails: these must raise rather than draw something misleading.
run("guard::lr+lanes", "render_flowchart.py",
    {**LR, "lanes": ["A"], "nodes": [{**n, "lane": "A"} for n in LR["nodes"]]},
    expect="does not support swimlanes")

run("guard::lr+loop", "render_flowchart.py",
    {**LR, "edges": LR["edges"] + [{"from": "dest", "to": "source", "loop": True}]},
    expect="does not support loop-back")

run("guard::bad-direction", "render_flowchart.py", {**LR, "direction": "DIAGONAL"},
    expect='direction must be "TD" or "LR"')

run("guard::unmarked-cycle", "render_flowchart.py",
    {"nodes": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
     "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}]},
    expect="Cycle detected")

run("guard::unknown-node-id", "render_flowchart.py",
    {"nodes": [{"id": "a", "label": "A"}], "edges": [{"from": "a", "to": "ghost"}]},
    expect="isn't in 'nodes'")

run("guard::lane-not-declared", "render_flowchart.py",
    {"lanes": ["Real"], "nodes": [{"id": "a", "label": "A", "lane": "Fake"}], "edges": []},
    expect="not present in top-level 'lanes'")

# 6. A pre-session input using none of the new keys must be unaffected.
run("compat::no-new-keys", "render_flowchart.py", {
    "title": "Plain flow",
    "nodes": [{"id": "s", "label": "Start", "shape": "terminator"},
              {"id": "p", "label": "Do work", "shape": "process"},
              {"id": "e", "label": "End", "shape": "terminator"}],
    "edges": [{"from": "s", "to": "p"}, {"from": "p", "to": "e"}],
})

passed = sum(1 for _, ok, _ in results if ok)
for name, ok, detail in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  <- {detail}" if detail else ""))
print(f"\n{passed}/{len(results)} passed   (artifacts: {OUT})")
sys.exit(0 if passed == len(results) else 1)
