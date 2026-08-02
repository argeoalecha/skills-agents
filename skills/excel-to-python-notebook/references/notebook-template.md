# Converted notebook anatomy

Every converted workbook produces a `.py` and a `.ipynb` with the same content. The
`.py` is the reviewable, diffable, importable artifact; the `.ipynb` is the teaching
artifact. Generate the `.py` first, then build the notebook from the same cell list.

## Required sections, in order

1. **Header (markdown)** — source path, sheet, technique name, citation with confidence
   tier, one-paragraph plain-language description of what the sheet computes.
2. **Provenance table (markdown)** — one row per distinct formula: Excel cell, the
   formula verbatim, the Python expression, a note. This is the audit trail; it is the
   reason the conversion is more explainable than the spreadsheet.
3. **Imports and source data (code)** — inputs read from constants transcribed out of
   the workbook, or loaded from the workbook itself with `openpyxl`. State which.
4. **Implementation (code)** — the calculation, using shared library functions where
   the technique already exists. One concept per cell.
5. **Validation (code)** — `Validator` checks against the workbook's cached values,
   ending in `v.report()`.
6. **Notes and limitations (markdown)** — anything unvalidatable, any source defect
   found, any convention assumed (e.g. which NHPP parameterisation), open questions.

## Header template

```markdown
# Weibull confidence limits by MLE

**Source:** `RE - L3 Training/1.1 RE L3 part1/Session 2.4.2 - MLE (Step 2).xlsx`,
sheet `CL-Weibull`

**Technique:** Weibull MLE asymptotic confidence bounds

**Citation:** method name only — no source cited in the workbook. See `ATTRIBUTION.md`.

Given point estimates of the Weibull shape and scale from a prior MLE step, this
computes two-sided confidence intervals on both parameters and on the resulting mean
life, across a range of confidence levels.
```

## Provenance table template

```markdown
| Excel cell | Formula | Python | Note |
|---|---|---|---|
| `D4` | `=D3*EXP(GAMMALN(1+1/D2))` | `eta * np.exp(gammaln(1 + 1/beta))` | Weibull mean |
| `D9` | `=ABS(NORMSINV(C9))` | `abs(norm.ppf(alpha/2))` | two-sided z |
| `E9` | `=$D$2*EXP((-0.78*D9)/(SQRT($D$5)))` | `beta*np.exp(-0.78*z/np.sqrt(n))` | lower bound on shape |
| `Y16` | `=#REF!*100` | — | **source defect**, excluded |
```

Collapse row-repeated formulas to one row. `inspect_workbook.py` already reports the
distinct formula shapes; a sheet with 5,061 formula cells typically has 6 distinct ones.

## Validation cell template

```python
import sys; sys.path.insert(0, "../shared")
from validate_conversion import Validator

v = Validator(SOURCE_WORKBOOK)
for i, row in enumerate(range(9, 14)):
    v.exact(f"beta_L @ CL={cls[i]}", beta_lo[i], v.cell("CL-Weibull", f"E{row}"))
v.legacy_stat("chi-square bound", x_py, v.cell("CL-Exponential", "E7"))
v.tolerance("MC failure probability", p_py, v.cell("SERIES", "G5"), rtol=0.05)
v.unvalidatable("SERIES!C6:C12", "written by VBA at runtime, no cached value")
assert v.report(), "conversion does not reproduce the source workbook"
```

Ending on an `assert` makes a broken conversion fail loudly when the notebook is run
top to bottom, rather than printing a red line someone scrolls past.

## Building the .ipynb

Write cells as data and `json.dump` them. Do not build notebook sources by nesting
triple-quoted Python inside triple-quoted Python — em dashes, currency symbols and
nested quotes break the builder before the notebook is ever written.

```python
import json
from pathlib import Path

def md(src):   return {"cell_type": "markdown", "metadata": {}, "source": src}
def code(src): return {"cell_type": "code", "execution_count": None,
                       "metadata": {}, "outputs": [], "source": src}

cells = [md(HEADER), md(PROVENANCE), code(IMPORTS), code(IMPL), code(VALIDATION), md(NOTES)]

nb = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "cells": cells,
}
Path(out).write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
```

Validate before delivering:

```bash
python3 -c "import nbformat; nb=nbformat.read('out.ipynb', as_version=4); print(len(nb.cells), 'cells ok')"
python3 out.py    # the .py must run clean and its assert must pass
```

Run the `.py`, not just the notebook — a notebook that was never executed proves
nothing about whether the conversion reproduces the source.

## Style

- Cite the source cell in a comment wherever a magic constant appears:
  `beta = 1.8067   # CL-Weibull!D2, MLE from the prior exercise`
- Prefer a shared library call over re-deriving a technique inline.
- Seed every RNG so the notebook is reproducible: `rng = np.random.default_rng(0)`.
- Print something in every code cell — a count, a parameter, a comparison.
- Do not silently repair a defective source. Reproduce the intent, flag the defect.
