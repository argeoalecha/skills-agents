# Excel to Python function map

Mappings and the traps that silently produce wrong numbers. Everything below was
verified against real workbooks, not recalled from memory.

## Operator traps

### Unary minus binds tighter than `^` in Excel — the opposite of Python

Excel precedence puts negation *above* exponentiation. Python puts it below.

```
Excel:   =-2^2          ->  4        because it means (-2)^2
Python:   -2**2         -> -4        because it means -(2**2)
```

This is not academic. Inverse-CDF Weibull sampling appears in training workbooks as:

```
=$B$8*(-LN(1-RAND())^(1/$B$9))
```

Excel reads that as `eta * ((-ln(1-u)) ** (1/beta))` — correct. The literal Python
transcription `eta * (-np.log(1-u)**(1/beta))` reads as `eta * -(np.log(1-u)**(1/beta))`,
and since `ln(1-u)` is negative, a fractional power of a negative number yields `nan`.
Always parenthesize: `eta * (-np.log(1 - u)) ** (1 / beta)`.

### Other operator differences

| Excel | Python |
|---|---|
| `^` | `**` |
| `&` (concat) | `+` on str, or f-string |
| `=` (compare) | `==` |
| `<>` | `!=` |
| `%` (postfix percent) | `/ 100` — Excel's `%` is not modulo |

Integer division and modulo: Excel `QUOTIENT(a,b)` -> `a // b`, `MOD(a,b)` -> `a % b`
(both match Python's sign behaviour for positive operands only; for mixed signs Excel's
`MOD` follows the divisor's sign, same as Python, but `INT` truncates toward negative
infinity like `math.floor`, not like `int()`).

## Statistical inverse functions — check the tail convention

The single most common silent error. Excel's legacy `CHIINV`/`CHIDIST` are
**right-tailed**; scipy's `.ppf`/`.cdf` are left-tailed.

| Excel | Python | Note |
|---|---|---|
| `CHIINV(p, df)` | `chi2.isf(p, df)` | `isf`, not `ppf` — Excel p is the right-tail area |
| `CHIDIST(x, df)` | `chi2.sf(x, df)` | `sf`, not `cdf` |
| `CHISQ.INV(p, df)` | `chi2.ppf(p, df)` | the modern name *is* left-tailed |
| `CHISQ.INV.RT(p, df)` | `chi2.isf(p, df)` | |
| `NORMSINV(p)` | `norm.ppf(p)` | left-tailed both sides |
| `NORMSDIST(z)` | `norm.cdf(z)` | |
| `NORMINV(p, mu, sd)` | `norm.ppf(p, mu, sd)` | |
| `NORMDIST(x, mu, sd, TRUE)` | `norm.cdf(x, mu, sd)` | `FALSE` -> `norm.pdf` |
| `TINV(p, df)` | `t.isf(p/2, df)` | legacy `TINV` is **two-tailed** |
| `T.INV(p, df)` | `t.ppf(p, df)` | one-tailed |
| `FINV(p, d1, d2)` | `f.isf(p, d1, d2)` | right-tailed |
| `LOGINV(p, mu, sd)` | `lognorm.ppf(p, s=sd, scale=np.exp(mu))` | see below |
| `GAMMALN(x)` | `scipy.special.gammaln(x)` | |
| `GAMMAINV(p, a, b)` | `gamma.ppf(p, a, scale=b)` | |
| `WEIBULL(x, a, b, TRUE)` | `weibull_min.cdf(x, a, scale=b)` | Excel `a`=shape, `b`=scale |

### Lognormal parameterisation

Excel's `LOGINV(p, mean, sd)` takes the mean and sd **of ln(X)**. scipy's `lognorm`
takes `s` = sd of ln(X) as the shape and `scale` = exp(mean of ln(X)). Passing the
Excel arguments positionally to `lognorm.ppf` is wrong every time.

### Precision: Excel's legacy solvers are not machine-accurate

Measured on a real workbook (`Session 2.4.2 - MLE`, 10 cells):

| Function | Worst relative disagreement with scipy |
|---|---|
| `NORMSINV` | 8e-16 — machine precision |
| `CHIINV` | 2.9e-8 |

`CHIINV`, `TINV`, `FINV`, `GAMMAINV`, `BETAINV` use iterative solvers accurate to
roughly 1e-7 relative. When a conversion check fails *only* at the 1e-8 level on one of
these, **scipy is the more accurate side** — validate with `rtol=1e-6` via
`Validator.legacy_stat()` and note it in the notebook. Never bend the Python to
reproduce Excel's solver error.

## Random and simulation

| Excel | Python |
|---|---|
| `RAND()` | `rng.random()` with `rng = np.random.default_rng(seed)` |
| `RANDBETWEEN(a,b)` | `rng.integers(a, b + 1)` — Excel's bound is inclusive |
| `NORMINV(RAND(), mu, sd)` | `rng.normal(mu, sd)` |
| `-LN(1-RAND())/lambda` | `rng.exponential(1 / lam)` |
| `eta*(-LN(1-RAND()))^(1/beta)` | `eta * rng.weibull(beta)` |

Excel's RNG state cannot be reproduced in Python. A cached value in a `RAND()`-driven
cell is one frozen draw, so it is not an exact target — validate with
`Validator.tolerance()` and a stated rtol, and always seed the Python side so the
notebook itself is reproducible.

## Lookup, aggregation, arrays

| Excel | Python |
|---|---|
| `VLOOKUP(v, tbl, i, FALSE)` | dict lookup, or `df.merge(...)` / `df.set_index(k).loc[v, col]` |
| `INDEX(rng, MATCH(v, key, 0))` | same as above — prefer a dict or a merge over index arithmetic |
| `COUNTIF(rng, "=1")` | `int((arr == 1).sum())` |
| `COUNTIFS` | boolean mask conjunction: `((a > 1) & (b < 2)).sum()` |
| `SUMPRODUCT(a, b)` | `np.dot(a, b)` |
| `FREQUENCY(data, bins)` | `np.histogram(data, bins)[0]` — mind bin-edge convention |
| `PERCENTILE(rng, p)` | `np.percentile(arr, p * 100)` — both linear-interpolate |
| `QUARTILE(rng, k)` | `np.percentile(arr, 25 * k)` |
| `SLOPE(y, x)` / `INTERCEPT(y, x)` | `scipy.stats.linregress(x, y).slope` / `.intercept` |
| `RSQ(y, x)` | `linregress(x, y).rvalue ** 2` |
| `LINEST(y, x)` | `np.polyfit(x, y, 1)` — note LINEST returns slope first, polyfit too |
| `TREND` / `FORECAST` | fit with `linregress`, then evaluate |
| `FACT(n)` | `math.factorial(n)` — for arrays, `scipy.special.factorial` |

Note `SLOPE(y, x)` takes y first; `linregress(x, y)` takes x first. Swapping them
produces a plausible-looking wrong number.

## Dates

Excel stores dates as serial numbers with a deliberate 1900 leap-year bug. Convert with
origin `1899-12-30`:

```python
pd.to_datetime(serial, unit="D", origin="1899-12-30")
```

`openpyxl` usually converts date-formatted cells to `datetime` already; check the cell
type before converting twice.

## Text and logic

| Excel | Python |
|---|---|
| `IF(c, a, b)` | `a if c else b`, or `np.where(c, a, b)` on arrays |
| `IFERROR(x, alt)` | `try/except`, or `np.nan_to_num` |
| `AND(...)` / `OR(...)` | `all([...])` / `any([...])`, or `&` / `\|` on arrays |
| `ROUND(x, n)` | **not** `round()` — see below |

Excel's `ROUND` is half-away-from-zero. Python's built-in `round()` is banker's rounding
(half-to-even), so `round(2.5)` is `2` in Python and `3` in Excel. When a workbook's
displayed results depend on rounding:

```python
from decimal import Decimal, ROUND_HALF_UP
def excel_round(x, n=0):
    q = Decimal(10) ** -n
    return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))
```

Also: cell *display* formatting is not rounding. A cell showing `2.35` may hold
`2.34999...`; the cached value is the truth, the format string is cosmetic.

## Operator precedence traps beyond `^` vs unary minus

`/` binds tighter than `-` in Excel, same as Python — but a formula missing intended
parentheses reads as plausible either way. Found in a real training workbook:

```
=SQRT(O38/$A$35-1)
```

This reads, at a glance, as `sqrt(SS / (n-1))` — the standard sample-standard-deviation
formula. It is not. Excel evaluates it as `sqrt((SS/n) - 1)`, because `-1` is not inside
the division. The two differ by more than the last few significant digits (11.297 vs.
the statistically correct 11.535 on real course data) — this is a **source authoring
defect**, not a floating-point nuance.

The tell: if a validation check on a recursive/cumulative formula (a running CUSUM, a
running total) fails with an error that *compounds* — off by `x` at step 1, `2x` at
step 2, `3x` at step 3 — the Python side is using a slightly wrong constant somewhere
upstream, not a slightly wrong recursion. Trace every constant in the recursion back to
the literal cell the Excel formula references (not the cell that *looks* like the
settings cell — a workbook can carry a second, unused block of "settings" cells that
nothing actually points at). Confirm by re-deriving the referenced cell's own formula
character by character, watching operator precedence, before assuming the discrepancy
is precision.

## Error values

`#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`, `#NULL!`, `#NUM!` appearing in a
formula or cached value mean the **source workbook is broken at that cell**. Real
example found in training material: `=#REF!*100` across a whole column. Never reproduce
these silently — surface them, exclude the cell from validation with an explicit
`unvalidatable()` note, and tell the user the source is defective.
