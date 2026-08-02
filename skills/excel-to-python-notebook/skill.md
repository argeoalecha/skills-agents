---
name: excel-to-python-notebook
description: Convert formula-driven Excel workbooks into explainable, cited, numerically-validated Python scripts and Jupyter notebooks. Use when the user wants a spreadsheet's calculations turned into code that documents where each number comes from — training material, engineering calcs, financial or statistical models. Triggers on "convert this Excel to Python", "turn this workbook into a notebook", "make this spreadsheet explainable", "port these formulas to Python", "document what this xlsx actually computes". Not for simply reading or editing a spreadsheet — use document-skills:xlsx for that.
---

# Excel to Python notebook conversion

Turn a workbook's formulas into code that shows its work: every result traceable to a
source cell, every technique named, every number validated against what Excel actually
computed.

Domain-agnostic pipeline with a pluggable domain pack for technique recognition.
`references/domain-pack-reliability.md` is the reference pack (reliability and life-data
analysis); without a matching pack the pipeline still works by transcribing formulas
literally and naming techniques only where certain.

## The rule

A converted notebook that has not been run against the source workbook's cached values
is not a conversion, it is a guess. Every notebook ends in a validation cell that
asserts. If a number cannot be validated, say so in the notebook — never let an
unvalidatable cell look like a passing one.

## Procedure

### 1. Inventory

For a batch, deduplicate first — training folders routinely ship the same workbook in
two places:

```bash
find . -type f \( -iname "*.xls*" \) -exec md5 -q {} \; -exec echo {} \; | paste - - | sort
```

Byte-identical copies convert once. Near-duplicates (same sheet names, different
content — `rev 3.0` vs `rev 3.1`) are the dangerous case: diff them cell by cell before
choosing, because the later revision often silently fixes a formula bug. Report the diff
rather than assuming the higher number supersedes.

### 2. Extract

```bash
python3 scripts/inspect_workbook.py "workbook.xlsx" [--sheet NAME] [--json report.json]
```

Reports per sheet: formula count and **distinct formula shapes**, function histogram,
volatile cells, uncached cells, error values, plus workbook-level VBA/iterative-calc/
external-link flags.

Read the distinct shapes, not the cells. A 5,000-cell sheet is usually 6 formulas filled
down; understanding those 6 is the whole job.

Act on these flags:

- **VBA present** — logic lives outside the cells. Default: if the macro implements a
  nameable standard technique and its written cells hold no cached values, rebuild from
  the underlying theory rather than transcribing the macro. Only reverse-engineer
  `vbaProject.bin` (via `oletools`) when the specific implementation is the point.
- **Uncached formula cells** — nothing to validate against. Record each with
  `unvalidatable()` and a reason.
- **Volatile cells** (`RAND`, `NOW`, `OFFSET`, `INDIRECT`) — the cached value is one
  frozen draw. Validate by tolerance, never exact.
- **Error values** (`#REF!`, `#DIV/0!`) — the source is broken there. Surface it to the
  user; do not reproduce it and do not quietly patch it.
- **Iterative calculation on** — a circular reference is intentional; port it as an
  explicit fixed-point loop, not a single expression.
- **External links** — resolve or flag; those cached values came from a file you may
  not have.

### 3. Classify

Match the formula signatures to named techniques using the active domain pack. Reuse an
existing shared-library function when the technique already appears elsewhere in the
project; only write new code for a genuinely new technique. Where no pack entry matches,
transcribe literally and do not invent a technique name.

Consult `references/excel-function-map.md` for every function mapping. It is not
optional reading — it documents the traps that produce plausible wrong numbers:

- Excel's unary minus binds tighter than `^`; Python's does not. The literal
  transcription of an inverse-CDF sampler yields `nan`.
- `CHIINV`/`CHIDIST`/`TINV`/`FINV` are right- or two-tailed; scipy's `ppf`/`cdf` are
  left-tailed. Use `isf`/`sf`.
- `LOGINV(p, mu, sd)` does not map positionally onto `lognorm.ppf`.
- `SLOPE(y, x)` and `linregress(x, y)` take their arguments in opposite order.
- Excel `ROUND` is half-away-from-zero; Python `round` is half-to-even.

### 4. Determine citation confidence

Check sheet names, cell comments and defined names for explicit sources. Tag each claim:

- `confirmed` — an explicit citation exists in the workbook (e.g. a sheet literally
  named `Ebeling p373`)
- `inferred` — formula structure matches a known named method, no citation present
- `unverified` — generic technique, or no domain-pack match

Default policy: for `inferred` and `unverified`, **cite the method name only**. Do not
manufacture page numbers. When the material's date is known but the edition is not,
infer the edition from publication timing, tag it as inferred, and move on rather than
blocking. Never upgrade a confidence tier without textual basis.

### 5. Convert

Follow `references/notebook-template.md`. Produce a `.py` and a matching `.ipynb`, both
carrying: header with citation, a provenance table mapping every distinct Excel cell to
its Python expression, the implementation, the validation cell, and a limitations note.

### 6. Validate

Copy `scripts/validate_conversion.py` into the project once — a `shared/` directory
next to the converted notebooks — and point `sys.path` at it, as the notebook template
does. Do not import it from this skill directory; the conversion must run standalone.

```python
import sys; sys.path.insert(0, "../shared")
from validate_conversion import Validator
v = Validator("source.xlsx")
v.exact("MTBF", mtbf_py, v.cell("CL-Weibull", "D4"))          # deterministic
v.legacy_stat("chi-square bound", x_py, v.cell("CL-Exp", "E7"))  # low-precision Excel solver
v.tolerance("P(up)", p_py, v.cell("SERIES", "G5"), rtol=0.05)    # volatile / simulated
v.unvalidatable("SERIES!C6:C12", "VBA-written, no cached value")
assert v.report()
```

Three tiers, chosen by cell type, never by whichever one passes:

| Tier | When | Tolerance |
|---|---|---|
| `exact` | ordinary arithmetic, `EXP`, `LN`, `NORMSINV` | `rtol=1e-9` |
| `legacy_stat` | `CHIINV`, `TINV`, `FINV`, `GAMMAINV`, `BETAINV` | `rtol=1e-6` |
| `tolerance` | anything downstream of `RAND()` | justified by Monte Carlo standard error |

If an `exact` check fails only at the 1e-8 level on a legacy statistical function, scipy
is the more accurate side — move it to `legacy_stat` and note it. Do not bend Python to
reproduce Excel's solver error. Any other failure is a real conversion bug: fix the
Python, do not loosen the tolerance.

Then actually run it:

```bash
python3 converted.py    # must exit clean with the assert passing
```

### 7. Report

Tell the user what was converted, what validated, what could not be validated and why,
and any defects found in the source workbook. A source defect discovered during
conversion is a finding worth stating plainly, not a detail to bury.

## Files

- `scripts/inspect_workbook.py` — two-pass extraction and risk flags
- `scripts/validate_conversion.py` — three-tier validation; import into every notebook
- `references/excel-function-map.md` — function mappings, operator and precision traps
- `references/domain-pack-reliability.md` — reference domain pack, reliability engineering
- `references/notebook-template.md` — required notebook anatomy and build pattern

## Writing a new domain pack

A pack is a markdown reference with a recognition table mapping formula signatures to
technique names, plus tested Python for each technique. Follow the reliability pack's
shape. Keep packs additive — new domains get their own file; the extraction and
validation scripts stay domain-free.
