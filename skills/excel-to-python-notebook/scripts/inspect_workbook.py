"""Extract everything needed to plan an Excel to Python conversion.

Two passes over the workbook: formulas (data_only=False) and cached values
(data_only=True). Reports the facts that decide conversion strategy — which cells
carry logic, which functions appear, what is volatile, what has no cached value to
validate against, whether VBA or iterative calculation is involved.

Usage:
    python3 inspect_workbook.py <workbook> [--sheet NAME] [--json OUT] [--formulas N]

For the complete formula record (every cell, not a sample) use
formula_fidelity.py manifest.

Exit codes: 0 ok, 2 workbook unreadable.
"""

import argparse
import json
import re
import sys
import warnings
import zipfile
from collections import Counter
from pathlib import Path

warnings.filterwarnings("ignore")

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl required: pip install openpyxl")

from formula_fidelity import (ERROR_VALUES, VOLATILE, analyse, formula_text, grid_sheets,
                              uncached_formula_cells)

# Excel functions with no direct numpy/scipy equivalent worth flagging early.
NEEDS_CARE = {
    "GAMMALN", "NORMSINV", "NORMSDIST", "NORMINV", "NORMDIST", "CHIINV", "CHIDIST",
    "CHISQ.INV", "CHISQ.INV.RT", "CHISQ.DIST", "TINV", "FINV", "WEIBULL", "EXPON.DIST",
    "LINEST", "TREND", "SLOPE", "INTERCEPT", "RSQ", "FORECAST", "VLOOKUP", "HLOOKUP",
    "INDEX", "MATCH", "SUMPRODUCT", "FREQUENCY", "PERCENTILE", "QUARTILE",
}


def inspect(path, only_sheet=None, formula_samples=12):
    path = Path(path)
    try:
        wb_f = openpyxl.load_workbook(path, data_only=False)
        wb_v = openpyxl.load_workbook(path, data_only=True)
    except Exception as exc:
        sys.exit(f"cannot read {path}: {exc}")

    calc = getattr(wb_f, "calculation", None)
    report = {
        "workbook": str(path),
        "sheets_all": wb_f.sheetnames,
        "chartsheets": [n for n in wb_f.sheetnames if not hasattr(wb_f[n], "iter_rows")],
        "has_vba": False,
        "calculated_by": None,
        "calc_mode": getattr(calc, "calcMode", None),
        "iterative_calc": bool(getattr(calc, "iterate", False)),
        "iterate_count": getattr(calc, "iterateCount", None),
        "defined_names": [],
        "external_links": 0,
        "sheets": [],
    }

    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            report["has_vba"] = "xl/vbaProject.bin" in names
            if "docProps/app.xml" in names:
                app = re.search(r"<Application>(.*?)</Application>", z.read("docProps/app.xml").decode("utf-8", "replace"))
                report["calculated_by"] = app.group(1) if app else None
    except Exception:
        pass

    try:
        report["defined_names"] = sorted(wb_f.defined_names.keys())
    except Exception:
        pass
    try:
        report["external_links"] = len(wb_f._external_links or [])
    except Exception:
        pass

    try:
        uncached = uncached_formula_cells(path)
    except Exception:
        uncached = None

    for name, ws in grid_sheets(wb_f):
        if only_sheet and name != only_sheet:
            continue
        ws_v = wb_v[name] if hasattr(wb_v[name], "iter_rows") else None
        no_result = uncached.get(name, set()) if uncached is not None else None

        funcs = Counter()
        n_formula = n_const = n_uncached = 0
        volatile_cells = []
        uncached_cells = []
        error_cells = []
        samples = []
        unique_shapes = {}

        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                cached_val = ws_v[cell.coordinate].value if ws_v is not None else None
                if isinstance(cached_val, str) and cached_val.startswith(ERROR_VALUES):
                    if len(error_cells) < 25:
                        error_cells.append(f"{cell.coordinate}={cached_val}")

                ftext = formula_text(cell.value)
                if ftext is None:
                    n_const += 1
                    continue
                n_formula += 1
                shape, names = analyse(ftext, cell.coordinate)
                found = set(names)
                funcs.update(found)

                if any(e in ftext for e in ERROR_VALUES) and len(error_cells) < 25:
                    error_cells.append(f"{cell.coordinate} formula:{ftext[:40]}")

                if found & VOLATILE:
                    volatile_cells.append(cell.coordinate)

                # A formula returning "" reads as None too, but it is a real cached value.
                if no_result is not None:
                    is_uncached = cell.coordinate in no_result
                else:
                    is_uncached = ws_v is not None and cached_val is None
                if is_uncached:
                    n_uncached += 1
                    if len(uncached_cells) < 25:
                        uncached_cells.append(cell.coordinate)
                elif cached_val is None:
                    cached_val = ""

                if shape not in unique_shapes:
                    unique_shapes[shape] = cell.coordinate
                    if len(samples) < formula_samples:
                        samples.append({
                            "cell": cell.coordinate,
                            "formula": ftext,
                            "cached": cached_val,
                        })

        report["sheets"].append({
            "name": name,
            "dimensions": ws.dimensions,
            "max_row": ws.max_row,
            "max_col": ws.max_column,
            "n_formula_cells": n_formula,
            "n_constant_cells": n_const,
            "n_unique_formula_shapes": len(unique_shapes),
            "n_uncached_formula_cells": n_uncached,
            "uncached_sample": uncached_cells,
            "n_volatile_cells": len(volatile_cells),
            "volatile_sample": volatile_cells[:10],
            "error_cells": error_cells,
            "functions": dict(funcs.most_common()),
            "functions_needing_care": sorted(set(funcs) & NEEDS_CARE),
            "distinct_formulas": samples,
        })

    return report


def render(report):
    out = []
    add = out.append
    add(f"WORKBOOK  {report['workbook']}")
    add(f"  sheets: {len(report['sheets_all'])}  (chartsheets skipped: {report['chartsheets'] or 'none'})")
    add(f"  VBA project: {'YES — macro logic lives outside cells' if report['has_vba'] else 'no'}")
    saved_by = report["calculated_by"] or "unknown"
    is_excel = saved_by.startswith("Microsoft Excel") and "Compatible" not in saved_by
    not_excel = "" if is_excel else "  — cached values are not Excel's own"
    add(f"  last saved by: {saved_by}{not_excel}")
    add(f"  calc mode: {report['calc_mode']}   iterative: {report['iterative_calc']} ({report['iterate_count']})")
    if report["external_links"]:
        add(f"  external links: {report['external_links']}  — resolve before converting")
    if report["defined_names"]:
        add(f"  defined names: {', '.join(report['defined_names'][:12])}")
    add("")

    for s in report["sheets"]:
        add(f"SHEET  {s['name']}   [{s['dimensions']}]")
        add(f"  formula cells {s['n_formula_cells']}  (unique shapes {s['n_unique_formula_shapes']})  constants {s['n_constant_cells']}")
        if s["n_uncached_formula_cells"]:
            add(f"  UNCACHED formula cells: {s['n_uncached_formula_cells']} — no cached value; check against the formula engine")
            add(f"    e.g. {', '.join(s['uncached_sample'][:8])}")
        if s["n_volatile_cells"]:
            add(f"  VOLATILE cells: {s['n_volatile_cells']} — cached values are one frozen draw, use tolerance checks")
            add(f"    e.g. {', '.join(s['volatile_sample'][:8])}")
        if s["error_cells"]:
            add(f"  ERROR VALUES in source: {len(s['error_cells'])} — the workbook itself is broken here, do not reproduce silently")
            add(f"    e.g. {', '.join(s['error_cells'][:5])}")
        if s["functions_needing_care"]:
            add(f"  functions needing a deliberate Python mapping: {', '.join(s['functions_needing_care'])}")
        if s["functions"]:
            top = ", ".join(f"{k}x{v}" for k, v in list(s["functions"].items())[:12])
            add(f"  function use: {top}")
        if s["distinct_formulas"]:
            add("  distinct formulas:")
            for d in s["distinct_formulas"]:
                cached = d["cached"]
                shown = f"  -> {cached!r}" if cached is not None else "  -> (no cached value)"
                add(f"    {d['cell']:>6}  {d['formula']}{shown}")
        add("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("workbook")
    ap.add_argument("--sheet", help="inspect only this sheet")
    ap.add_argument("--json", help="write full report as JSON to this path")
    ap.add_argument("--formulas", type=int, default=12, help="distinct formulas to show per sheet")
    args = ap.parse_args()

    report = inspect(args.workbook, args.sheet, args.formulas)
    print(render(report))
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        print(f"[json written to {args.json}]")


if __name__ == "__main__":
    main()
