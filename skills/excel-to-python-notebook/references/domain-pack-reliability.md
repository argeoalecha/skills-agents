# Domain pack: reliability engineering

Reference implementation of a domain pack. Each entry gives the **formula signature** to
recognise in a worksheet, the **technique name** to cite, and the Python equivalent.
Built from an RE Level 3 training course; the patterns generalise to most reliability
and life-data material.

Cite by method name. These techniques are standard textbook material (Ebeling, Nelson,
O'Connor, MIL-HDBK-189) — do not attribute a specific page unless the workbook itself
names one.

## Recognition table

| Signature seen in cells | Technique | Section |
|---|---|---|
| `(i-0.3)/(n+0.4)` | median rank, Bernard's approximation | Rank regression |
| `LN(LN(1/(1-F)))` vs `LN(t)`, `SLOPE`/`INTERCEPT` | Weibull least-squares fit | Rank regression |
| `LN(1/(1-F))` vs `t` through origin | exponential least-squares fit | Rank regression |
| `r/T`, total-time-on-test sums | exponential MLE | MLE |
| `CHIINV(a/2, 2*r)` with `(2*T)/...` | exponential MTBF confidence limits | Confidence limits |
| `EXP(±0.78*z/SQRT(n))`, `EXP(±1.05*z/(b*SQRT(n)))` | Weibull MLE asymptotic confidence bounds | Confidence limits |
| `EXP(GAMMALN(1+1/beta))` | Weibull mean (MTTF) via gamma function | Weibull mean |
| `2r(LN(T/r)-...)/(1+(r+1)/(6r))` | Bartlett's test for exponentiality | Goodness of fit |
| ratio of log-spacings vs an F table | Mann's test for Weibull | Goodness of fit |
| `(SUM(t)/n - T/2)/(T*SQRT(1/(12n)))` | Laplace / centroid trend test | Trend test |
| `lambda*t^beta` or `(lambda/beta)*(t2^b - t1^b)` | NHPP power law (Crow-AMSAA) | Reliability growth |
| `LN(cum MTBF)` vs `LN(t)` linear fit | Duane plot | Reliability growth |
| `PRODUCT(R)` / `1-PRODUCT(1-R)` | series / parallel RBD | RBD |
| `IF(SUM(flags)>=k,1,0)` over n columns | k-out-of-n voting | RBD |
| `RAND()` + inverse CDF + `COUNTIF(...)/COUNT(...)` | Monte Carlo RBD | Monte Carlo |
| square transition matrix, rows summing to 1 | Markov chain | Markov |
| running `MAX(0, ...)` accumulation | CUSUM chart | Control charts |
| `mean ± 3*sd` limit columns | Shewhart control chart | Control charts |

## Rank regression (least squares on probability paper)

```python
import numpy as np
from scipy.stats import linregress

def median_rank(n):
    """Bernard's approximation — the F(t) estimate used on Weibull paper."""
    i = np.arange(1, n + 1)
    return (i - 0.3) / (n + 0.4)

def weibull_lsq(times):
    """Least-squares Weibull fit. Returns (beta, eta)."""
    t = np.sort(np.asarray(times, float))
    f = median_rank(t.size)
    x = np.log(t)
    y = np.log(np.log(1.0 / (1.0 - f)))
    fit = linregress(x, y)
    beta = fit.slope
    eta = np.exp(-fit.intercept / beta)
    return beta, eta, fit.rvalue ** 2

def exponential_lsq(times):
    """Least-squares exponential fit through the origin. Returns lambda."""
    t = np.sort(np.asarray(times, float))
    f = median_rank(t.size)
    y = np.log(1.0 / (1.0 - f))
    return float(np.dot(t, y) / np.dot(t, t))
```

`SLOPE(y, x)` takes y first, `linregress(x, y)` takes x first — a swap here yields a
plausible but wrong beta.

## MLE and confidence limits

```python
from scipy.special import gammaln
from scipy.stats import chi2, norm

def exponential_mle(n_failures, total_time_on_test):
    lam = n_failures / total_time_on_test
    return lam, 1.0 / lam                      # lambda, MTBF

def exponential_mtbf_ci(total_time, r, cl, failure_terminated=True):
    """Chi-square MTBF bounds. Excel's CHIINV is right-tailed -> chi2.isf."""
    a = 1 - cl
    lo = (2 * total_time) / chi2.isf(a / 2, 2 * r if failure_terminated else 2 * r + 2)
    hi = (2 * total_time) / chi2.isf(1 - a / 2, 2 * r)
    return lo, hi

def weibull_mean(beta, eta):
    """eta * Gamma(1 + 1/beta), computed in log space as Excel does."""
    return eta * np.exp(gammaln(1 + 1 / beta))

def weibull_mle_ci(beta, eta, n, cl):
    """Asymptotic bounds. The 0.78 / 1.05 constants are the standard
    large-sample variance approximations for Weibull MLE."""
    z = abs(norm.ppf((1 - cl) / 2))
    s = np.sqrt(n)
    beta_lo, beta_hi = beta * np.exp(-0.78 * z / s), beta * np.exp(0.78 * z / s)
    eta_lo, eta_hi = eta * np.exp(-1.05 * z / (beta * s)), eta * np.exp(1.05 * z / (beta * s))
    return (beta_lo, beta_hi), (eta_lo, eta_hi)
```

Verified: this reproduces a training workbook's confidence-limit table to `rtol=1e-9`
for `NORMSINV`-driven cells and `1e-6` for `CHIINV`-driven cells.

## Goodness of fit

```python
def bartlett_statistic(times):
    """Bartlett's test for exponentiality. Compare to chi2 with r-1 df;
    a value inside the two-sided critical range supports exponentiality."""
    t = np.asarray(times, float)
    r = t.size
    T = t.sum()
    num = 2 * r * (np.log(T / r) - np.log(t).sum() / r)
    den = 1 + (r + 1) / (6 * r)
    return num / den

def bartlett_pass(stat, r, cl=0.90):
    a = 1 - cl
    return chi2.ppf(a / 2, r - 1) < stat < chi2.isf(a / 2, r - 1)
```

**Mann's test for Weibull** compares a weighted ratio of successive log-spacings against
a critical value from an F distribution. Training workbooks usually ship a precomputed
"Mann Test Table" sheet. Extract that table verbatim to CSV rather than re-deriving it,
then cross-check a few entries against `scipy.stats.f.isf` and report any divergence —
do not assume the printed table and scipy agree.

## Trend test (is the system repairable / non-stationary?)

```python
def laplace_statistic(failure_times, T=None):
    """Centroid test. U ~ N(0,1). U>0 suggests deterioration (increasing
    failure rate), U<0 improvement, |U|<1.96 no trend at 95%."""
    t = np.asarray(failure_times, float)
    n = t.size
    T = float(t.max()) if T is None else float(T)   # time- vs failure-truncated
    return (t.mean() - T / 2) / (T * np.sqrt(1 / (12 * n)))
```

Run this **first**. A significant trend means the data are not i.i.d. and a Weibull/
exponential life-distribution fit is the wrong model — an NHPP is required instead.
Training templates encode this as the first step of the process flow.

## NHPP power law / Crow-AMSAA

Two parameterisations circulate. Check which one a workbook uses before porting:

- **Mean-value form:** `E[N(t)] = lambda * t**beta`, intensity `lambda*beta*t**(beta-1)`
- **Intensity form:** intensity `lambda * t**(beta-1)`, so `E[N(t)] = (lambda/beta) * t**beta`

A cell reading `=(lambda/beta)*(t2^beta - t1^beta)` is the intensity form. Getting this
wrong rescales every expected-count result by a factor of beta.

```python
def crow_amsaa_mle(failure_times, T=None):
    """Time-truncated MLE. Returns (lambda, beta) in mean-value form."""
    t = np.asarray(failure_times, float)
    n = t.size
    T = float(t.max()) if T is None else float(T)
    beta = n / np.log(T / t).sum()
    lam = n / T ** beta
    return lam, beta

def expected_failures(lam, beta, t1, t2):
    return lam * (t2 ** beta - t1 ** beta)      # mean-value form

def duane_fit(cum_time, cum_failures):
    """Duane plot: ln(cumulative MTBF) vs ln(t) is linear under the power law."""
    x = np.log(np.asarray(cum_time, float))
    y = np.log(np.asarray(cum_time, float) / np.asarray(cum_failures, float))
    fit = linregress(x, y)
    return fit.slope, fit.intercept, fit.rvalue ** 2
```

## RBD

```python
from math import comb

def r_series(rs):
    return float(np.prod(rs))

def r_parallel(rs):
    return float(1 - np.prod([1 - r for r in rs]))

def r_k_out_of_n(r, k, n):
    """Identical components, exactly k or more must survive."""
    return float(sum(comb(n, i) * r**i * (1 - r)**(n - i) for i in range(k, n + 1)))
```

High-level vs low-level redundancy: redundancy applied at the component level
(low-level) always yields reliability greater than or equal to the same redundancy
applied at the system level (high-level). Training workbooks demonstrate this by
computing both and comparing — reproduce both, don't just assert it.

## Monte Carlo RBD

```python
def mc_rbd(n_sims, k, betas, etas, mission_time, seed=0):
    """Weibull component lives, k-out-of-n success. Returns P(system survives)."""
    rng = np.random.default_rng(seed)
    lives = np.column_stack([
        eta * rng.weibull(beta, n_sims) for beta, eta in zip(betas, etas)
    ])
    survived = (lives >= mission_time).sum(axis=1)
    return float((survived >= k).mean())
```

Mind the unary-minus trap when porting the Excel inverse-CDF sampler literally — see
`excel-function-map.md`. `eta * rng.weibull(beta, n)` is equivalent and safer.

Excel's cached simulation results are one frozen draw. Validate with
`Validator.tolerance()` at an rtol justified by the Monte Carlo standard error
(`sqrt(p(1-p)/n)`), not with exact parity. For n=1000 and p around 0.75, one standard
error is about 1.4%, so an rtol of 5% is roughly 3 sigma — state this reasoning in the
notebook instead of picking a tolerance arbitrarily.

## Markov chains

```python
def steady_state(P):
    """Left eigenvector of the transition matrix for eigenvalue 1."""
    P = np.asarray(P, float)
    vals, vecs = np.linalg.eig(P.T)
    v = np.real(vecs[:, np.argmin(np.abs(vals - 1))])
    return v / v.sum()

def step(pi0, P, n):
    return np.asarray(pi0, float) @ np.linalg.matrix_power(np.asarray(P, float), n)
```

Check that each row of `P` sums to 1 before using it; training workbooks sometimes hold
a transposed matrix, which silently yields a wrong steady state.

## Control charts

```python
def shewhart_limits(x, k=3):
    x = np.asarray(x, float)
    mu, sd = x.mean(), x.std(ddof=1)
    return mu - k * sd, mu, mu + k * sd

def cusum(x, target=None, k=0.5, h=5):
    """Tabular CUSUM in sd units. k = allowance, h = decision interval."""
    x = np.asarray(x, float)
    mu = x.mean() if target is None else target
    sd = x.std(ddof=1)
    z = (x - mu) / sd
    cp = cm = 0.0
    hi, lo = [], []
    for zi in z:
        cp = max(0.0, cp + zi - k)
        cm = max(0.0, cm - zi - k)
        hi.append(cp)
        lo.append(cm)
    return np.array(hi), np.array(lo), h
```

Training material sometimes uses the simpler "cumulative sum of deviations from target"
(`np.cumsum(x - target)`) rather than the tabular CUSUM. Read the cells before choosing
— they are different charts with different signal rules.
