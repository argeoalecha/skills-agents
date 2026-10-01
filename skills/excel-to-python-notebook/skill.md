---
name: excel-to-python-notebook
description: Convert formula-driven Excel workbooks into explainable, cited, numerically-validated Python scripts and Jupyter notebooks that still carry every source formula verbatim, checked with Excel-compatible libraries (openpyxl, the formulas engine, LibreOffice). Use when the user wants a spreadsheet's calculations turned into code that documents where each number comes from — training material, engineering calcs, financial or statistical models. Triggers on "convert this Excel to Python", "turn this workbook into a notebook", "make this spreadsheet explainable", "port these formulas to Python", "document what this xlsx actually computes", "keep the Excel formulas in the Python version". Not for simply reading or editing a spreadsheet — use document-skills:xlsx for that.
---

# Excel to Python notebook conversion

Turn a workbook's formulas into code that shows its work: every source formula carried
across verbatim, every result traceable to a source cell, every technique named, every
number validated against what Excel actually computed.

Domain-agnostic pipeline with a pluggable domain pack for technique recognition.
`references/domain-pack-reliability.md` is the reference pack (reliability and life-data
analysis); without a matching pack the pipeline still works by transcribing formulas
literally and naming techniques only where certain.

## The rules

**Numbers.** A converted notebook that has not been run against the source workbook's
cached values is not a conversion, it is a guess. Every notebook ends in a validation
cell that asserts. If a number cannot be validated, say so in the notebook — never let
an unvalidatable cell look like a passing one.

**Formulas.** The conversion must hold the same formula information as the workbook.
Every distinct source formula appears in the notebook exactly as Excel stores it, next
to the Python that replaces it, and the complete per-cell record ships beside it as
`<name>.formulas.json`. A formula that was paraphrased, retyped from memory, or left
out fails validation. A cached value proves the Python right at one set of inputs;
only the formula says what the cell computes, so the formula is checked as well.

## Excel-compatible libraries

Each does the part it is reliable at. Install with `pip install openpyxl formulas`.

| Library | Role |
|---|---|
| `openpyxl` | Reads each formula string exactly as stored, tokenizes it, reads cached values, writes a workbook back out with formulas live |
| `formulas` | Evaluates the workbook's own formula strings with Excel semantics — precedence, tail conventions, rounding, defined names — at the cached inputs or at changed ones |
| LibreOffice (`soffice --headless`) | Recalculates a workbook that has no cached values, giving a second independent set of results |

Excel's cached value is the authority. The engine is a second witness, not a
replacement: it does not implement every function, and where it disagrees with the
cache the disagreement is recorded as a gap in the engine's coverage. Measured limits
are listed in `references/excel-function-map.md`.

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
external-link flags and which application last saved the file.

Read the distinct shapes, not the cells. A 5,000-cell sheet is usually 6 formulas filled
down; understanding those 6 is the whole job. Two formulas share a shape only when one
is a fill-down or fill-right copy of the other — a changed constant is a new shape.

Then write the formula record that ships with the conversion, and get the map to fill in:

```bash
python3 scripts/formula_fidelity.py manifest "workbook.xlsx" --out "name.formulas.json" --skeleton
python3 scripts/formula_fidelity.py engine "workbook.xlsx"
```

`manifest` writes every formula cell (verbatim text, shape, cached value, defined
names, workbook hash) and `--skeleton` prints a `FORMULAS` dict with one entry per
distinct formula. Paste that dict into the conversion — never retype a formula.
`engine` recalculates the workbook with the `formulas` engine and lists every formula
where it disagrees with Excel's cache, which tells you before converting which cells
the engine can vouch for. Loading takes about a minute per 5,000 formula cells.

Act on these flags:

- **VBA present** — logic lives outside the cells. Default: if the macro implements a
  nameable standard technique and its written cells hold no cached values, rebuild from
  the underlying theory rather than transcribing the macro. Only reverse-engineer
  `vbaProject.bin` (via `oletools`) when the specific implementation is the point.
- **Uncached formula cells** — Excel never calculated them (the file was written by a
  script, or a macro fills them at runtime). Validate against the formula instead with
  `v.engine()`, and where LibreOffice is available recalculate a copy for cached values:
  `soffice --headless --convert-to xlsx --outdir recalculated "workbook.xlsx"`, then
  `Validator("workbook.xlsx", cached_from="recalculated/workbook.xlsx")`. Take formulas
  from the original only — LibreOffice rewrites formula text on save (`FALSE` becomes
  `FALSE()`). Use `unvalidatable()` only when neither route gives a value. A formula
  whose result is the empty string is cached, not uncached.
- **Last saved by something other than Excel** — the cached values are that
  application's, not Excel's. LibreOffice and Excel differ where a blank passes through
  a formula. Say so in the notebook, and treat an engine disagreement on such a cell as
  a finding about the source.
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

Follow `references/notebook-template.md`. Produce a `.py`, a matching `.ipynb` and the
`.formulas.json` manifest. The `.py` and `.ipynb` both carry: header with citation, the
`FORMULAS` map holding every distinct Excel formula verbatim beside its Python
expression, the provenance table generated from that map, the implementation, the
validation cell, and a limitations note.

Write the implementation as a function of the workbook's input cells
(`def model(beta=..., eta=...)`), not as module-level arithmetic on constants. The
formula checks in step 6 call it at inputs Excel never cached.

When the user needs to keep working in Excel, hand back a workbook with every formula
still live rather than pasted values:

```python
from formula_fidelity import export_with_formulas
export_with_formulas("source.xlsx", "scenario.xlsx", inputs={("CL-Weibull", "D2"): 2.5})
```

It refuses to overwrite a formula cell and raises if any formula changed on the way
out. The export holds no cached values until Excel or LibreOffice opens it.

### 6. Validate

Copy `scripts/validate_conversion.py` and `scripts/formula_fidelity.py` into the project
once — a `shared/` directory next to the converted notebooks — and point `sys.path` at
it, as the notebook template does. Do not import them from this skill directory; the
conversion must run standalone.

```python
import sys; sys.path.insert(0, "../shared")
from validate_conversion import Validator
v = Validator("source.xlsx")

# formula fidelity — report() fails if either call is missing
v.formulas_carried(FORMULAS, excluded={"SERIES!Y16": "source defect, =#REF!*100"})
v.engine_parity()
v.engine("MTBF at beta=2.5", model(beta=2.5)["mtbf"], "CL-Weibull", "D4",
         inputs={("CL-Weibull", "D2"): 2.5})

# numeric parity
v.exact("MTBF", mtbf_py, v.cell("CL-Weibull", "D4"))          # deterministic
v.legacy_stat("chi-square bound", x_py, v.cell("CL-Exp", "E7"))  # low-precision Excel solver
v.tolerance("P(up)", p_py, v.cell("SERIES", "G5"), rtol=0.05)    # volatile / simulated
v.unvalidatable("SERIES!C6:C12", "VBA-written, no cached value")
assert v.report()
```

Formula fidelity, three checks:

| Check | What it proves | Fails when |
|---|---|---|
| `formulas_carried(FORMULAS)` | every distinct source formula is in the conversion, character for character, with a Python expression | a formula is missing, differs from the workbook, or has no Python beside it |
| `engine_parity()` | the carried formula strings, run by the engine, produce what Excel cached | never fails the conversion — a disagreement is the engine's gap, listed per formula |
| `engine(..., inputs=)` | the Python matches the formula itself at inputs Excel never cached | the Python and the formula diverge away from the cached point |

Give every output of the model at least one `engine()` check at changed inputs. Change
several inputs at once and pick values that are not round multiples of the originals. A
transcription with a misplaced parenthesis can match one cached number by coincidence;
it does not survive a second point. `engine()` records a gap, not a pass, for a cell
where the engine failed parity — there the cached value is the only witness.

Numeric parity, three tiers, chosen by cell type, never by whichever one passes:

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

State the formula count both ways — distinct formulas carried and cells they cover —
name every excluded formula with its reason, and list the formulas the engine could not
vouch for. Those rest on the cached value alone.

## Files

- `scripts/inspect_workbook.py` — two-pass extraction and risk flags
- `scripts/formula_fidelity.py` — formula manifest, shape grouping, the `formulas`
  engine wrapper, formula-preserving export; copy beside the validator
- `scripts/validate_conversion.py` — formula-fidelity and numeric checks; import into
  every notebook
- `references/excel-function-map.md` — function mappings, operator and precision traps
- `references/domain-pack-reliability.md` — reference domain pack, reliability engineering
- `references/notebook-template.md` — required notebook anatomy and build pattern

## Writing a new domain pack

A pack is a markdown reference with a recognition table mapping formula signatures to
technique names, plus tested Python for each technique. Follow the reliability pack's
shape. Keep packs additive — new domains get their own file; the extraction and
validation scripts stay domain-free.
