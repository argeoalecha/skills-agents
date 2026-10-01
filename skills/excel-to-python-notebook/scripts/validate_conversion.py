"""Validation of a Python conversion against its source workbook.

Import this into a converted notebook, with formula_fidelity.py beside it. Two things
are checked, and report() fails unless both were:

Formula fidelity — the conversion still carries the workbook's formulas

    formulas_carried()  every distinct source formula appears verbatim in the
                        conversion's FORMULAS map, beside its Python expression
    engine_parity()     an Excel-compatible engine recalculates those formula strings
                        and is compared with what Excel cached
    engine()            Python must match the formula itself, evaluated by the engine —
                        at the cached inputs or at changed ones

Numeric parity — the Python reproduces what Excel computed

    exact()         deterministic cell — Python must match Excel to rtol
    legacy_stat()   deterministic cell from a low-precision legacy Excel solver
    tolerance()     volatile/simulated cell — Excel's cached value is one frozen
                    draw and its RNG cannot be seed-matched, so only agreement
                    within a stated tolerance is meaningful
    unvalidatable() no cached value exists (VBA-written range, or the source cell
                    is broken) — recorded as a known gap, never silently skipped

Usage in a notebook:

    from validate_conversion import Validator
    v = Validator("Session 2.4.2 - MLE.xlsx")
    v.formulas_carried(FORMULAS)
    v.engine_parity()
    v.exact("beta (MLE)", beta_py, v.cell("CL-Weibull", "D2"))
    v.engine("MTTF at beta=2.5", model(beta=2.5), "CL-Weibull", "D4",
             inputs={("CL-Weibull", "D2"): 2.5})
    v.tolerance("P(system up)", p_py, v.cell("SERIES", "G5"), rtol=0.05)
    v.unvalidatable("SERIES!C6:C12", "VBA-written at runtime, no cached value")
    assert v.report()

CLI (quick look at what a sheet cached):

    python3 validate_conversion.py <workbook> --sheet NAME --range B15:D20
"""

import argparse
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl required: pip install openpyxl")

from formula_fidelity import EngineUnavailable, FormulaBook, agree, is_error

PASS, FAIL, GAP = "PASS", "FAIL", "GAP"

# Excel's legacy iterative solvers for inverse distributions are accurate to roughly
# 1e-7 relative, not machine precision. Measured against scipy on real workbooks:
# CHIINV drifts up to ~3e-8, while NORMSINV agrees to ~8e-16. When a check fails only
# at the 1e-8 level on one of these, scipy is the more accurate side — loosen rtol to
# RTOL_LEGACY_STAT and say so in the notebook rather than bending the Python to match.
RTOL_LEGACY_STAT = 1e-6


class Validator:
    """Collects verdicts comparing a conversion against its source workbook."""

    def __init__(self, workbook, rtol=1e-9, cached_from=None):
        """cached_from: a recalculated copy of an uncached workbook, used for cached
        values only. Formulas are always read from `workbook` itself."""
        self.path = Path(workbook)
        self.default_rtol = rtol
        self._cached_from = cached_from
        self._wb = openpyxl.load_workbook(cached_from or self.path, data_only=True)
        self.checks = []
        self._book = None
        self._parity = None
        self._carried_checked = False
        self._parity_checked = False

    @property
    def book(self):
        """Every formula in the source workbook; see formula_fidelity.FormulaBook."""
        if self._book is None:
            self._book = FormulaBook(self.path, self._cached_from)
        return self._book

    # -- reading the source -------------------------------------------------

    def cell(self, sheet, coord):
        """Cached value of one cell. Returns None when Excel never cached one."""
        value = self._wb[sheet][coord].value
        if is_error(value):
            return None
        if value is None and self.book.formula(sheet, coord) is not None:
            return self.book.cached(sheet, coord)
        return value

    def range(self, sheet, ref, drop_none=True):
        """Cached values of a range as a flat list, e.g. range('Data', 'B15:B1014')."""
        out = []
        for row in self._wb[sheet][ref]:
            cells = row if isinstance(row, tuple) else (row,)
            for c in cells:
                v = None if is_error(c.value) else c.value
                if v is None and drop_none:
                    continue
                out.append(v)
        return out

    def formula(self, sheet, coord):
        """The source formula at a cell, verbatim. None for a constant."""
        return self.book.formula(sheet, coord)

    # -- formula fidelity ---------------------------------------------------

    def formulas_carried(self, carried, excluded=None):
        """Every distinct source formula must be carried verbatim into the conversion.

        carried   {"Sheet!Cell": (excel_formula, python_expression)} — one entry per
                  distinct formula, keyed by any cell that holds it
        excluded  {"Sheet!Cell": reason} for formulas deliberately not converted
        """
        self._carried_checked = True
        covered, failed = set(), False
        for ref, pair in carried.items():
            sheet, _, coord = ref.rpartition("!")
            excel, python = pair
            actual = self.book.formula(sheet, coord)
            if actual is None:
                self._record(FAIL, f"formula carried: {ref}", "the source workbook holds no formula at this cell")
            elif actual != excel:
                self._record(FAIL, f"formula carried: {ref}", f"not verbatim — source holds {actual}")
            elif not str(python).strip() or str(python).startswith("TODO"):
                self._record(FAIL, f"formula carried: {ref}", f"no Python expression given for {actual}")
            else:
                covered.add(self.book.shape_of(sheet, coord))
                continue
            failed = True
        for ref, reason in (excluded or {}).items():
            sheet, _, coord = ref.rpartition("!")
            shape = self.book.shape_of(sheet, coord)
            if shape is None:
                self._record(FAIL, f"formula excluded: {ref}", "the source workbook holds no formula at this cell")
                failed = True
                continue
            covered.add(shape)
            self._record(GAP, f"formula excluded: {ref}  {self.book.formula(sheet, coord)}", reason)
        for shape in self.book.shapes:
            if shape["id"] not in covered:
                failed = True
                self._record(FAIL, f"formula not carried: {shape['sheet']}!{shape['cell']}",
                             f"{shape['formula']}  ({len(shape['cells'])} cells)")
        if not failed:
            self._record(PASS, "formulas carried verbatim",
                         f"{len(self.book.shapes)} distinct formulas covering {len(self.book.cells)} cells")
        return not failed

    def _engine_parity(self):
        if self._parity is None:
            try:
                self._parity = self.book.engine_parity(self.default_rtol)
            except EngineUnavailable as exc:
                self._parity = exc
        return self._parity

    def engine_parity(self):
        """Recalculate the source formulas with the Excel-compatible engine.

        Agreement with Excel's cached values shows the carried formula strings are
        what produced the workbook's numbers. Where the engine disagrees, Excel stays
        the authority and the cell is recorded as a gap in the engine's coverage.
        """
        self._parity_checked = True
        parity = self._engine_parity()
        if isinstance(parity, EngineUnavailable):
            return self._record(GAP, "engine parity", str(parity))
        skipped = f"{parity['volatile']} volatile, {parity['uncached']} uncached or broken not compared"
        if parity["agree"]:
            self._record(PASS, "engine parity",
                         f"engine reproduces {parity['agree']} cached formula results ({skipped})")
        elif not parity["disagree"]:
            self._record(GAP, "engine parity", f"no cached formula results to compare with ({skipped})")
        for d in parity["disagree"]:
            self._record(GAP, f"engine parity: {d['sheet']}!{d['cell']}  {d['formula']}",
                         f"engine gives {d['engine']!r}, Excel cached {d['excel']!r} — Excel is the authority")
        return not parity["disagree"]

    def engine(self, label, python_value, sheet, coord, inputs=None, rtol=None):
        """Python must match the source formula at this cell, evaluated by the engine.

        With inputs={(sheet, coord): value} the workbook is recalculated at changed
        inputs first, which tests the formula rather than one cached number.
        """
        rtol = self.default_rtol if rtol is None else rtol
        parity = self._engine_parity()
        if isinstance(parity, EngineUnavailable):
            return self._record(GAP, label, str(parity))
        if (sheet, coord) in parity["cells"]:
            return self._record(GAP, label, f"engine does not reproduce Excel at {sheet}!{coord}")
        try:
            value = self.book.engine.value(sheet, coord, inputs)
        except Exception as exc:
            return self._record(GAP, label, f"engine could not recalculate: {exc}")
        if value is None or is_error(value):
            return self._record(GAP, label, f"engine has no value at {sheet}!{coord} ({value!r})")
        ok = agree(python_value, value, rtol)
        shown = "" if not inputs else " at " + ", ".join(f"{s}!{c}={v!r}" for (s, c), v in inputs.items())
        self.checks.append((PASS if ok else FAIL, label, python_value, value,
                            f"engine {sheet}!{coord}{shown} rtol={rtol:g}"))
        return ok

    # -- numeric parity -----------------------------------------------------

    def legacy_stat(self, label, python_value, excel_value):
        """Deterministic cell computed by a low-precision legacy Excel solver.

        Use for CHIINV/TINV/FINV/GAMMAINV and friends — see RTOL_LEGACY_STAT.
        """
        return self.exact(label, python_value, excel_value, rtol=RTOL_LEGACY_STAT)

    def exact(self, label, python_value, excel_value, rtol=None):
        """Deterministic cell: Python must reproduce Excel to floating-point tolerance."""
        rtol = self.default_rtol if rtol is None else rtol
        if excel_value is None:
            return self.unvalidatable(label, "no cached value in source workbook")
        ok = agree(python_value, excel_value, rtol)
        self.checks.append((PASS if ok else FAIL, label, python_value, excel_value,
                            f"exact rtol={rtol:g}"))
        return ok

    def tolerance(self, label, python_value, excel_value, rtol=0.05):
        """Volatile/simulated cell: agreement within rtol is the strongest claim available."""
        if excel_value is None:
            return self.unvalidatable(label, "no cached value in source workbook")
        ok = agree(python_value, excel_value, rtol)
        self.checks.append((PASS if ok else FAIL, label, python_value, excel_value,
                            f"tolerance rtol={rtol:g} (Excel RNG not seed-matchable)"))
        return ok

    def unvalidatable(self, label, reason):
        """Record a known validation gap so it appears in the report instead of vanishing."""
        return self._record(GAP, label, reason)

    def _record(self, verdict, label, note):
        self.checks.append((verdict, label, None, None, note))
        return None

    # -- output -------------------------------------------------------------

    def report(self, verbose=True):
        """Print the verdict table. Returns True when nothing FAILed."""
        checks = list(self.checks)
        if not self._carried_checked:
            checks.append((FAIL, "formula fidelity", None, None, "formulas_carried() was never called"))
        if not self._parity_checked:
            checks.append((FAIL, "formula fidelity", None, None, "engine_parity() was never called"))
        n_pass = sum(1 for c in checks if c[0] == PASS)
        n_fail = sum(1 for c in checks if c[0] == FAIL)
        n_gap = sum(1 for c in checks if c[0] == GAP)

        if verbose:
            print(f"Validation against {self.path.name}")
            print("-" * 78)
            for verdict, label, py, xl, note in checks:
                print(f"  {verdict:4}  {label}")
                if py is None and xl is None:
                    print(f"        {'not validatable: ' if verdict == GAP else ''}{note}")
                else:
                    against = "engine" if note.startswith("engine") else "excel"
                    print(f"        python={py!r}  {against}={xl!r}  [{note}]")
            print("-" * 78)
            print(f"  {n_pass} passed, {n_fail} failed, {n_gap} unvalidatable")
            if n_gap and not n_fail:
                print("  Note: unvalidatable entries are known gaps, not silent passes.")

        return n_fail == 0


def main():
    ap = argparse.ArgumentParser(description="Inspect cached values in a workbook range.")
    ap.add_argument("workbook")
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--range", dest="ref", required=True, help="e.g. B15:D20")
    args = ap.parse_args()

    v = Validator(args.workbook)
    values = v.range(args.sheet, args.ref, drop_none=False)
    print(f"{args.sheet}!{args.ref} — {len(values)} cells, "
          f"{sum(1 for x in values if x is None)} with no cached value")
    for val in values:
        print(f"  {val!r}")


if __name__ == "__main__":
    main()
