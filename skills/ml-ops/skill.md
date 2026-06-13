---
name: ml-ops
description: End-to-end ML model lifecycle skill for projects that BUILD or MAINTAIN machine learning models. Covers systematic algorithm selection with multi-criteria evaluation, baseline implementation, validation design, hyperparameter tuning, accuracy assurance gates, and scheduled retraining/drift monitoring. Adapts to task type (classification, regression, anomaly detection, clustering, time series, ranking, NLP). Triggers on "select a model", "choose an algorithm", "ML model selection", "validate the model", "tune the model", "retrain schedule", "drift detection", "model accuracy", "which algorithm should I use", "benchmark the model", "ml pipeline", "train and test", or any request to design, evaluate, or maintain an ML model. NOT for documenting an already-built pipeline — use /ml-inside for that.
---

# ML Model Lifecycle — Selection, Enhancement, Validation, and Maintenance

A structured, phase-gated workflow for selecting, building, validating, and maintaining ML models to industry accuracy and reliability standards. Adapts to the specific task type and domain constraints of the project.

**Companion skill — `/ml-inside`:** writes the spec document for a pipeline that already exists. Run `/ml-ops` first to build it; run `/ml-inside` after to document it. If the user asks for "documentation of how the model works" without intending to change it, hand off to `/ml-inside` and stop.

## Entry Point

Before reading Phase 0 into the user's context, gather the Phase 0 inputs interactively with `AskUserQuestion`. Ask in this order, one or two questions per turn:

1. **Task type** — classification / regression / anomaly detection / clustering / time series / ranking / NLP
2. **Primary metric + minimum threshold** — single locked metric (see Phase 4b for selection)
3. **Latency budget** — p95 inference target in ms
4. **Interpretability requirement** — yes / no, and why (regulator / stakeholder / debug)
5. **Target column name** — to substitute throughout (referred to below as `<target_col>`)

Record answers and proceed.

---

## Phase Summary

```
Phase 0 — Problem & Constraint Inventory     (define scope before touching code)     HARD STOP if unclear
Phase 1 — Data Assessment                    (quality, size, distribution, labels)   HARD STOP if data unusable
Phase 2 — Algorithm Candidate Matrix         (multi-criteria evaluation)
Phase 3 — Baseline Implementation            (minimal working model + sanity checks)
Phase 4 — Validation Design                  (split strategy + metric contract)
Phase 5 — Enhancement Cycle                  (tuning + feature engineering)
Phase 6 — Accuracy Assurance Gates           (benchmarks + statistical tests)
Phase 7 — Production Readiness               (latency, serialization, footprint)
Phase 8 — Scheduled Maintenance Protocol     (retraining cadence + drift detection)
```

---

## Phase 0 — Problem & Constraint Inventory (Hard Stop)

Before any code or algorithm discussion, establish the full constraint set. Missing information here invalidates all downstream decisions.

### 0pre. Does this actually need ML?

Before anything else, ask:

- Could a deterministic rule, threshold, or SQL query produce the same outcome at acceptable accuracy?
- Is the target a stable function of a few known features (e.g. tax calculation)? → not ML
- Do you have < 100 labelled examples and no path to more? → not ML yet; collect data first
- Is there an existing service or pre-trained API (OCR, translation, sentiment) that solves this off-the-shelf? → use that, skip training

If a non-ML solution works, stop here and recommend it. ML is the right answer when the relationship is complex, the data exists, and the deployment cost is justified.

### 0a. Task Type

Identify the ML task. Each type unlocks a different candidate pool:

| Task Type | Signal |
|---|---|
| Binary / Multi-class Classification | Discrete labels, predict category |
| Regression | Continuous target, predict value |
| Anomaly / Outlier Detection | No clean labels, flag deviations |
| Clustering | No labels, discover structure |
| Time Series Forecasting | Ordered temporal target |
| Ranking / Recommendation | Relative ordering matters |
| Multi-label Classification | Multiple simultaneous labels per sample |
| NLP / Sequence | Text, tokens, embeddings |

### 0b. Constraint Inventory

Document all constraints **before** shortlisting algorithms:

```
Data
├── Volume: N samples available for training
├── Dimensionality: P features
├── Label availability: fully labelled / partially labelled / unlabelled
├── Class balance: balanced / imbalanced (record ratio)
├── Stationarity: stationary / non-stationary / concept drift expected
└── Privacy: PII present? (affects cloud API usage)

Compute
├── Training environment: local CPU / GPU / cloud / edge
├── Max training time: __ minutes/hours per run
├── Max inference latency: __ ms (p95)
├── Max model size: __ MB
└── Retraining cadence: real-time / hourly / daily / weekly / on-demand

Accuracy
├── Primary metric: (define ONE; see Phase 4 for selection guide)
├── Minimum acceptable threshold: (numeric)
├── Secondary metric: (optional guardrail)
└── Baseline to beat: (random, heuristic, or prior model)

Interpretability
├── Regulatory requirement: explainability required? (GDPR Art. 22, FDA, etc.)
├── Stakeholder requirement: "why" must be explainable to non-ML audience?
└── Debugging requirement: feature attribution for post-hoc analysis?

Operational
├── Serving mode: batch / online / streaming
├── Deployment target: REST API / embedded / edge / browser (WASM)
└── Update mechanism: replace model file / shadow deploy / canary
```

**Hard Stop**: If task type, primary metric, or minimum accuracy threshold cannot be determined, stop and resolve with the user before proceeding.

---

## Phase 1 — Data Assessment (Hard Stop)

Run these checks before any modelling. Bad data invalidates all results.

### 1a. Size Assessment

| Task Type | Minimum Viable N | Notes |
|---|---|---|
| Tabular classification | 1,000 per class | For deep learning: 10k+ per class |
| Regression | 500–2,000 | Depends on feature count (10:1 rule) |
| Anomaly detection | 1,000 normal samples | Anomaly rate ≥ 0.5% for any validation signal |
| Time series | ≥ 3× longest seasonality | e.g. daily pattern → 3+ days; annual → 3+ years |
| NLP (fine-tuning) | 500–5,000 | Pre-trained base absorbs data scarcity |

### 1b. Quality Checks

Substitute `<target_col>` and the data source for the project. The skill assumes pandas + a tabular source — for parquet, multi-file, or DB-extracted data, replace the loader (e.g. `pd.read_parquet`, `mcp__supabase__execute_sql`, `duckdb.sql(...)`).

```python
import pandas as pd
import numpy as np

df = pd.read_csv("data.csv")  # swap for project's actual loader
TARGET = "<target_col>"

# Missing values
missing = df.isnull().mean().sort_values(ascending=False)
print(missing[missing > 0])

# Duplicates
n_dupes = df.duplicated().sum()
print(f"Duplicates: {n_dupes} ({n_dupes/len(df)*100:.1f}%)")

# Target distribution (classification)
print(df[TARGET].value_counts(normalize=True))

# Numeric feature statistics
print(df.describe())

# Cardinality of categoricals
for col in df.select_dtypes("object").columns:
    print(f"{col}: {df[col].nunique()} unique values")

# Temporal ordering (time series)
if "ts" in df.columns:
    df["ts"] = pd.to_datetime(df["ts"])
    gaps = df["ts"].diff().dropna()
    print(f"Median gap: {gaps.median()}, Max gap: {gaps.max()}")
```

**Hard Stop conditions:**
- Missing rate > 40% on target or primary features — investigate root cause
- Class imbalance > 20:1 — requires explicit strategy (record it in Phase 5)
- Temporal leakage detectable (future data in training window)
- Duplicate rate > 5% without explanation

### 1c. Leakage Audit

Flag columns that may encode the target post-hoc:
- Timestamps created at event time (predict before the event)
- IDs or keys that are assigned only after the outcome is known
- Columns that are downstream consequences of the target
- Features with suspiciously high correlation with target (> 0.95)

```python
corr_with_target = df.corr(numeric_only=True)[TARGET].abs().sort_values(ascending=False)
print(corr_with_target[corr_with_target > 0.8])
```

---

## Phase 2 — Algorithm Candidate Matrix

Use the constraint inventory from Phase 0 to build the candidate shortlist. Never shortlist without first completing Phase 0 and Phase 1.

### 2a. Candidate Pool by Task Type

#### Supervised — Classification & Regression

| Algorithm | Interpretable | GPU Required | Min N | Handles Missing | Non-Linear | Notes |
|---|---|---|---|---|---|---|
| Logistic / Linear Regression | Yes | No | 100 | No | No | Baseline; coefficient interpretability |
| Ridge / Lasso / ElasticNet | Yes | No | 100 | No | No | Regularised linear; Lasso = feature selection |
| Decision Tree | Yes | No | 100 | No | Yes | Prone to overfit; good explainability |
| Random Forest | Partial | No | 1,000 | Yes | Yes | Strong general baseline; permutation importance |
| Gradient Boosted Trees (XGBoost / LightGBM / CatBoost) | Partial | Optional | 500 | Yes (native) | Yes | Best tabular default; SHAP compatible |
| SVM (RBF kernel) | No | No | 500 | No | Yes | Good for high-dim low-N; slow on large N |
| k-Nearest Neighbors | No | No | 200 | No | Yes | No training cost; slow inference; curse of dimensionality |
| MLP / Feedforward Neural Net | No | Preferred | 5,000 | No | Yes | Use when GBT underperforms and N is large |
| Transformer (tabular) | No | Yes | 10,000 | Partial | Yes | TabPFN, TabTransformer — large N only |

#### Unsupervised — Anomaly Detection

| Algorithm | Label-free | Streaming | Non-stationary | Memory | Notes |
|---|---|---|---|---|---|
| Isolation Forest | Yes | No (retrain) | Partial (retrain) | Low | Best default for tabular sensor data |
| Extended IF (EIF) | Yes | No | Partial | Low | Fixes axis-parallel bias; drop-in for IF |
| Local Outlier Factor (LOF) | Yes | No | No | Medium | Density-based; poor at global anomalies |
| One-Class SVM | Yes | No | No | Medium | Sensitive to scale; slow on large N |
| DBSCAN | Yes | No | No | Low | Cluster-then-outlier; poor with high-dim |
| Gaussian Mixture Model | Yes | No | No | Low | Assumes Gaussian; fails with multi-modal |
| Autoencoder (AE) | Yes | Partial | Partial | High | Strong; needs GPU for large input |
| LSTM-Autoencoder | Yes | Yes | Yes | High | Best for temporal sequences; requires GPU |
| Rolling Z-Score | Yes | Yes | No | Minimal | Per-univariate baseline; retain as complement |

#### Unsupervised — Clustering

| Algorithm | Handles Noise | Scalable | Non-convex Shapes | k Required |
|---|---|---|---|---|
| K-Means | No | Yes | No | Yes |
| K-Medoids (PAM) | Partial | No | No | Yes |
| DBSCAN | Yes | Medium | Yes | No |
| HDBSCAN | Yes | Medium | Yes | No (min_samples) |
| Gaussian Mixture Model | No | Medium | Partial | Yes |
| Hierarchical (Ward/Complete) | No | No (O(n²)) | Partial | No |
| UMAP + HDBSCAN | Yes | Yes | Yes | No |

#### Time Series

| Algorithm | Multivariate | Long-range | Uncertainty | Notes |
|---|---|---|---|---|
| ARIMA / SARIMA | No | Poor | Yes (CI) | Univariate baseline; interpretable |
| Prophet | No | Medium | Yes | Business seasonality; additive |
| N-BEATS / N-HiTS | Yes | Yes | No | Pure DL forecaster |
| LSTM / GRU | Yes | Good | No | Classic sequence model |
| Temporal Fusion Transformer | Yes | Excellent | Yes | Best general purpose; heavy |
| LightGBM (tabular lag features) | Yes | Medium | No | Fastest tabular time series; strong baseline |

#### Ranking / Recommendation

| Algorithm | Cold Start | Implicit Feedback | Listwise Aware | Notes |
|---|---|---|---|---|
| BM25 / TF-IDF | Yes | No | No | Text retrieval baseline; always include |
| Popularity / heuristic | Yes | No | No | Baseline — most rec systems should beat this |
| Matrix Factorisation (ALS, SVD) | No | Yes (iALS) | No | Classic CF; strong on dense interaction data |
| LightFM | Partial (hybrid) | Yes | No | Hybrid CF + content features |
| LambdaMART (XGBoost / LightGBM) | Yes (via features) | Yes | Yes (NDCG loss) | Best gradient-boosted ranker; SHAP compatible |
| Two-Tower Neural Network | Yes (content) | Yes | No | Production embeddings for large catalogs |
| Sequential / Session-based (SASRec, BERT4Rec) | Partial | Yes | Yes | Strong for session/sequence rec |

#### NLP / Sequence

| Algorithm | Min N (fine-tune) | GPU Required | Multilingual | Notes |
|---|---|---|---|---|
| TF-IDF + Logistic Regression | 500 | No | Yes | Always include as baseline |
| FastText | 1,000 | No | Yes (with vectors) | Cheap classification; good for short text |
| Pre-trained encoder (DistilBERT, MiniLM) + classifier head | 500 | Preferred | Variant-dependent | Strong default for classification / retrieval |
| Sentence-Transformers embeddings + downstream model | 200 | Optional | Yes | Embed-once, classify-many; reusable for clustering / search |
| Fine-tuned encoder (BERT, RoBERTa, XLM-R) | 2,000 | Yes | XLM-R yes | When pre-trained head is insufficient |
| Encoder-decoder (T5, BART) | 5,000 | Yes | mT5 yes | Generative tasks — summarisation, QA |
| LLM via API (Claude, GPT) + prompt | 0 (zero-shot) | n/a | Yes | Use when N is tiny; cost-per-call applies; **PII check required** |
| LLM via API + few-shot / RAG | 0–100 | n/a | Yes | Use over fine-tuning when N < 500 or task is open-ended |

### 2b. Evaluation Criteria Matrix

Score each shortlisted candidate (1–5) against the project constraints from Phase 0. A candidate must score ≥ 3 on every hard constraint.

| Criterion | Weight | Hard Constraint? |
|---|---|---|
| Meets minimum accuracy threshold | Critical | Yes |
| Training time within budget | High | Conditional |
| Inference latency within budget | High | Conditional |
| Interpretability requirement | Medium | Conditional |
| Handles data characteristics (imbalance, missing, non-stationary) | High | Yes |
| Implementation complexity | Low | No |
| Maintenance cost (retraining, drift sensitivity) | Medium | No |
| Dependency risk (library maturity, licence) | Medium | No |

### 2c. Shortlist Rule

- Shortlist **2–4 candidates** maximum
- Always include **one simple baseline** (logistic regression, linear regression, rolling Z-score, or ARIMA)
- Reject any candidate that fails a hard constraint before implementation
- Document the rejection reason explicitly — this becomes the decision record

---

## Phase 3 — Baseline Implementation & Sanity Checks

### 3a. Implementation Order

1. Simplest baseline first (linear model, rolling stat, or dummy classifier)
2. Primary candidate second
3. Additional candidates in parallel only if baseline passes

### 3b. Pre-training Sanity Checks

Run these before claiming any result:

```python
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.model_selection import cross_val_score

# 1. Dummy baseline — your model must beat this or the problem is not ML-solvable
dummy = DummyClassifier(strategy="most_frequent")  # or DummyRegressor(strategy="mean")
dummy_scores = cross_val_score(dummy, X_train, y_train, cv=5, scoring="f1_weighted")
print(f"Dummy baseline: {dummy_scores.mean():.3f} ± {dummy_scores.std():.3f}")

# 2. Check that train score >> val score (overfit check)
model.fit(X_train, y_train)
train_score = model.score(X_train, y_train)
val_score   = model.score(X_val, y_val)
print(f"Train: {train_score:.3f}, Val: {val_score:.3f}, Gap: {train_score - val_score:.3f}")

# 3. Prediction sanity — check output distribution
preds = model.predict(X_val)
print(pd.Series(preds).value_counts(normalize=True))  # classification
print(pd.Series(preds).describe())                     # regression

# 4. Feature importance sanity — top features should be domain-meaningful
import shap
explainer = shap.TreeExplainer(model)
shap_vals  = explainer.shap_values(X_val[:200])
shap.summary_plot(shap_vals, X_val[:200])
```

**Sanity check gates:**
- Model beats dummy baseline (otherwise: re-examine features or labels)
- Train-val gap < 15 pp (otherwise: regularise, add data, or reduce features)
- Top features make domain sense (otherwise: suspect leakage)
- Prediction distribution looks plausible (no constant predictions, no extreme outliers)

---

## Phase 4 — Validation Design

### 4a. Split Strategy

| Scenario | Strategy |
|---|---|
| IID tabular data | Stratified 80/10/10 split (train/val/test); never touch test until Phase 6 |
| Imbalanced classes | Stratified k-Fold (k=5 or 10) |
| Time series / ordered data | Walk-forward CV or expanding window; never random shuffle |
| Spatial or grouped data | Group k-Fold (no leakage across groups) |
| Very small N (< 500) | Nested CV: outer 5-Fold evaluation, inner 3-Fold selection |
| Multiple datasets | Domain-split: train on A, val on B, test on C |

```python
# Stratified k-Fold (classification)
from sklearn.model_selection import StratifiedKFold, cross_validate
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
results = cross_validate(model, X, y, cv=cv,
                         scoring=["f1_weighted", "roc_auc", "precision_weighted", "recall_weighted"],
                         return_train_score=True)

# Time-series walk-forward
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5, gap=0)
for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
    X_tr, X_v = X[train_idx], X[val_idx]
    y_tr, y_v = y[train_idx], y[val_idx]
    model.fit(X_tr, y_tr)
    print(f"Fold {fold}: val={model.score(X_v, y_v):.3f}, n_train={len(train_idx)}")
```

### 4b. Metric Selection

Define ONE primary metric and lock it at Phase 0. Do not change it post-hoc.

#### Classification

| Scenario | Primary Metric | Rationale |
|---|---|---|
| Balanced classes | Accuracy or F1 (macro) | Equal weight per class |
| Imbalanced; miss is costly | Recall | Minimise false negatives |
| Imbalanced; false alarm is costly | Precision | Minimise false positives |
| Imbalanced; need balance | F1 (weighted) or PR-AUC | Imbalance-aware |
| Probabilistic output matters | ROC-AUC or Brier Score | Calibration matters |
| Multi-class, strict | Matthews Correlation Coefficient | Robust to imbalance |

#### Regression

| Scenario | Primary Metric |
|---|---|
| Outliers acceptable | MAE |
| Outliers penalised heavily | RMSE |
| Scale-invariant comparison | MAPE (only if target > 0) |
| Relative error tolerance | MASE (time series) |
| Explained variance | R² (supplement, not primary) |

#### Anomaly Detection (no labels)

| Scenario | Primary Metric |
|---|---|
| Labelled hold-out available | F1 at threshold, PR-AUC |
| No labels | Qualitative review + contamination rate audit |
| Streaming/online | Precision@k and Recall@k over flagged window |

#### Clustering (no labels)

| Metric | Use When |
|---|---|
| Silhouette Score (−1 to 1, higher = better) | Comparing k or algorithm |
| Davies-Bouldin Index (lower = better) | Compact, well-separated clusters |
| Calinski-Harabász (higher = better) | Convex, dense clusters |
| External (ARI, NMI) | Ground-truth cluster labels available |

#### Ranking / Recommendation

| Metric | Use When |
|---|---|
| NDCG@k | Graded relevance, position matters |
| MAP@k | Binary relevance, position matters |
| Recall@k / Precision@k | Retrieval quality; pair with NDCG |
| MRR | First-relevant-position emphasis (e.g. search) |
| Hit Rate @ k | Sparse implicit feedback |

### 4c. Threshold Strategy (Classification / Anomaly Detection)

Default threshold (0.5) is rarely optimal. Find the threshold on the **validation set**, never the test set:

```python
from sklearn.metrics import precision_recall_curve, f1_score
import numpy as np

y_prob = model.predict_proba(X_val)[:, 1]
precision, recall, thresholds = precision_recall_curve(y_val, y_prob)

# F1-optimal threshold
f1_scores = 2 * precision * recall / (precision + recall + 1e-9)
opt_idx   = np.argmax(f1_scores)
opt_threshold = thresholds[opt_idx]
print(f"Optimal threshold: {opt_threshold:.3f} → F1: {f1_scores[opt_idx]:.3f}")
```

---

## Phase 5 — Enhancement Cycle

Run enhancement only after the baseline passes sanity checks. Enhancement without a valid baseline is premature optimisation.

### 5a. Feature Engineering

Priority order (highest ROI first):

1. **Domain-driven features** — features that a domain expert would derive manually
2. **Interaction terms** — products or ratios of correlated features (e.g. `vibration / temperature`)
3. **Lag features** (time series) — `feature_t-1`, `feature_t-k`, rolling mean/std
4. **Binning / discretisation** — for non-linear relationships with linear models
5. **Target encoding** (high-cardinality categoricals) — with k-Fold to prevent leakage
6. **Embeddings** — for categoricals with >50 unique values in DL pipelines

Feature selection after engineering:

```python
from sklearn.inspection import permutation_importance

result = permutation_importance(model, X_val, y_val, n_repeats=10, random_state=42)
importance_df = pd.DataFrame({
    "feature": X_val.columns,
    "importance_mean": result.importances_mean,
    "importance_std":  result.importances_std
}).sort_values("importance_mean", ascending=False)

# Drop features with mean importance < 0 (hurts model)
drop_cols = importance_df[importance_df["importance_mean"] < 0]["feature"].tolist()
```

### 5b. Class Imbalance Handling

Apply in order of preference (least to most invasive):

1. `class_weight="balanced"` in model constructor — free, no data change
2. Threshold tuning (Phase 4c) — free if probabilities are calibrated
3. Over-sampling: SMOTE (tabular) or `RandomOverSampler` — training data only
4. Under-sampling: `RandomUnderSampler` — only when majority class is massive
5. Cost-sensitive learning: `sample_weight` with inverse class frequency

```python
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

pipe = ImbPipeline([
    ("smote", SMOTE(random_state=42, k_neighbors=5)),
    ("model", XGBClassifier(random_state=42))
])
```

### 5c. Hyperparameter Tuning

| Method | Space Size | Budget | Tool |
|---|---|---|---|
| Grid Search | ≤ 50 combinations | Unlimited | `GridSearchCV` |
| Random Search | Any | Moderate | `RandomizedSearchCV` |
| Bayesian Optimisation | Any | Limited | Optuna, Hyperopt |
| Successive Halving | Any | Limited | `HalvingGridSearchCV` |

**Rule**: tune on validation set, evaluate final result on held-out test set. Never tune on the test set.

**Run long tuning sweeps in the background.** A 100-trial Optuna study with a 1h timeout will block the conversation. Launch with `Bash(run_in_background=true)` and continue with other work; you'll be notified when it finishes.

**Experiment tracking is mandatory for any sweep > 10 trials.** Log to MLflow, Weights & Biases, or — for lightweight projects — a `experiments/runs.csv` (trial_id, params, cv_score, train_time, timestamp). Untracked sweeps are unreproducible.

```python
import optuna
from sklearn.model_selection import cross_val_score

def objective(trial):
    params = {
        "n_estimators":      trial.suggest_int("n_estimators", 100, 1000, step=100),
        "max_depth":         trial.suggest_int("max_depth", 3, 10),
        "learning_rate":     trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
        "subsample":         trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree":  trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "min_child_weight":  trial.suggest_int("min_child_weight", 1, 10),
        "reg_alpha":         trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        "reg_lambda":        trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
    }
    model = XGBClassifier(**params, random_state=42, eval_metric="logloss")
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring="f1_weighted")
    return scores.mean()

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100, timeout=3600)  # 1h budget
print(study.best_params)
```

### 5d. Ensemble Strategies

| Strategy | When | Tool |
|---|---|---|
| Voting / Averaging | Diverse models with similar performance | `VotingClassifier`, manual average |
| Stacking | Top 2–3 models with uncorrelated errors | `StackingClassifier` with CV predictions |
| Blending | Large dataset, fast iteration needed | Weighted average on hold-out |
| Boosting (already an ensemble) | Single best tabular performer | XGBoost, LightGBM, CatBoost |

**Ensemble diminishing returns**: if stacking improves primary metric < 1 pp over best single model, it is not worth the maintenance cost.

---

## Phase 6 — Accuracy Assurance Gates

### 6a. Acceptance Criteria Checklist

Acceptance thresholds are **defaults** — override per project from the Phase 0 inventory. Document overrides explicitly so they're traceable. The thresholds below are sensible starting points, not universal truths:

```
Accuracy Gate
  Primary metric on test set ≥ Phase 0 threshold                                PASS / FAIL
  Primary metric on test set > dummy baseline by ≥ <delta from Phase 0; default 10 pp>   PASS / FAIL
  Primary metric on test set > prior model by ≥ <delta from Phase 0; default 2 pp>       PASS / FAIL

Robustness Gate
  Metric variance across CV folds < <override or 5 pp>                          PASS / FAIL
  Degradation under 10% feature dropout < <override or 10 pp>                   PASS / FAIL
  Performance on every critical slice ≥ <override or 80%> of overall metric     PASS / FAIL

Calibration Gate (probability models only — adjust by stakes)
  Brier Score < <override or 0.20>                                              PASS / FAIL
  Expected Calibration Error (ECE) < <override or 0.10>                         PASS / FAIL

Latency Gate (production models)
  p50 inference latency ≤ Phase 0 budget                                        PASS / FAIL
  p99 inference latency ≤ 3× Phase 0 budget                                     PASS / FAIL

Fairness Gate (regulated decisions only — see 6e)
  Disparate-impact ratio across protected slices ≥ 0.80 (4/5 rule)              PASS / FAIL
  Equalised-odds gap ≤ <override or 0.10>                                       PASS / FAIL
```

**Stake-sensitivity**: medical, lending, hiring, and other high-stakes models should tighten Brier/ECE to 0.10/0.05 and require fairness sign-off. Low-stakes lead scoring or content ranking can loosen.

### 6b. Statistical Significance Test

When comparing two models, confirm the difference is not noise:

```python
from scipy import stats

# McNemar's test (classification, matched samples)
from statsmodels.stats.contingency_tables import mcnemar
preds_a = model_a.predict(X_test)
preds_b = model_b.predict(X_test)
correct_a = (preds_a == y_test)
correct_b = (preds_b == y_test)
table = pd.crosstab(correct_a, correct_b)
result = mcnemar(table, exact=True)
print(f"p-value: {result.pvalue:.4f}")  # < 0.05 → difference is significant

# Permutation test (any metric)
from sklearn.model_selection import permutation_test_score
score, perm_scores, p_value = permutation_test_score(
    model, X_test, y_test, n_permutations=1000, scoring="f1_weighted", random_state=42
)
print(f"Model F1: {score:.3f}, p-value: {p_value:.4f}")
```

### 6c. Slice Analysis

Disaggregate metrics by meaningful subgroups. A model with high overall accuracy but poor performance on a critical slice is not production-ready:

```python
for slice_val in df_test["asset_type"].unique():
    mask   = df_test["asset_type"] == slice_val
    subset = df_test[mask]
    score  = f1_score(subset["y_true"], subset["y_pred"], average="weighted")
    print(f"{slice_val}: F1={score:.3f}, n={mask.sum()}")
```

### 6d. Ablation Study

Remove each major component and measure impact. Documents that complexity is justified:

| Component Removed | Primary Metric | Delta | Keep? |
|---|---|---|---|
| Lag features | — | — | — |
| SMOTE | — | — | — |
| Feature X cluster | — | — | — |
| Tuned hyperparams (vs. defaults) | — | — | — |

If removing a component has no measurable impact (< 0.5 pp), remove it from the production pipeline.

### 6e. Fairness Audit (regulated / PH-market context)

Required for any model that influences lending, credit scoring, hiring, insurance pricing, healthcare triage, or other regulated decisions. For PH-targeted projects this also intersects RA 10173 (DPA) automated-decision rights — see `/ph-dpa-compliance`.

For each protected attribute (gender, age band, region, civil status, etc.):

```python
from sklearn.metrics import confusion_matrix

def disparate_impact(y_pred, group):
    """Selection rate of unprivileged / selection rate of privileged.
    4/5 rule: ratio ≥ 0.80 is the regulatory threshold."""
    groups = group.unique()
    rates = {g: (y_pred[group == g] == 1).mean() for g in groups}
    privileged   = max(rates, key=rates.get)
    unprivileged = min(rates, key=rates.get)
    return rates[unprivileged] / rates[privileged], rates

def equalised_odds_gap(y_true, y_pred, group):
    """Max |TPR_a − TPR_b| and max |FPR_a − FPR_b| across groups."""
    tprs, fprs = {}, {}
    for g in group.unique():
        mask = group == g
        tn, fp, fn, tp = confusion_matrix(y_true[mask], y_pred[mask]).ravel()
        tprs[g] = tp / (tp + fn + 1e-9)
        fprs[g] = fp / (fp + tn + 1e-9)
    return max(tprs.values()) - min(tprs.values()), max(fprs.values()) - min(fprs.values())
```

If a protected attribute is **not** in the feature set, audit anyway against held-back demographic data — proxies (zip, education, name) routinely leak protected information.

---

## Phase 7 — Production Readiness

### 7a. Serialisation

```python
import joblib
import json
from datetime import datetime

# Save model with metadata
model_artifact = {
    "model":         model,
    "feature_names": list(X_train.columns),
    "threshold":     opt_threshold,
    "trained_at":    datetime.utcnow().isoformat(),
    "n_train":       len(X_train),
    "primary_metric": {"name": "f1_weighted", "value": float(val_score)},
}
joblib.dump(model_artifact, "models/model_v1.pkl")

# Version manifest (checked into repo)
manifest = {
    "version":       "v1",
    "trained_at":    model_artifact["trained_at"],
    "n_train":       model_artifact["n_train"],
    "val_f1":        model_artifact["primary_metric"]["value"],
    "file":          "models/model_v1.pkl",
}
with open("models/manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
```

**Never commit model files to git.** Store in object storage (S3, GCS, Supabase Storage) and load at runtime. Commit only the manifest.

### 7b. Inference Latency Benchmarking

```python
import time
import numpy as np

n_samples = [1, 10, 100, 1000]
for n in n_samples:
    batch = X_test.sample(n)
    times = []
    for _ in range(50):
        t0 = time.perf_counter()
        _ = model.predict(batch)
        times.append(time.perf_counter() - t0)
    p50, p95, p99 = np.percentile(times, [50, 95, 99])
    print(f"n={n:5d}: p50={p50*1000:.1f}ms, p95={p95*1000:.1f}ms, p99={p99*1000:.1f}ms")
```

Gate: fails if any latency percentile exceeds Phase 0 budget. Fix options: lighter model, ONNX export, feature pruning, batching.

### 7c. Memory Footprint

```python
import sys
model_size_mb = sys.getsizeof(joblib.dumps(model)) / (1024 ** 2)
print(f"Model size: {model_size_mb:.1f} MB")
```

---

## Phase 8 — Scheduled Maintenance Protocol

### 8a. Retraining Cadence by Pattern Type

| Data Pattern | Recommended Cadence | Trigger |
|---|---|---|
| Stable stationary tabular | Monthly | Performance drop > 3 pp |
| Sensor / IoT with seasonal shift | Weekly | Data drift alert |
| Financial / market data | Daily or real-time | Concept drift alert |
| NLP on evolving topics | Monthly | Vocabulary drift alert |
| User behaviour data | Weekly | Distribution shift > PSI 0.2 |

### 8b. Data Drift Detection

Run before every retrain decision:

```python
import numpy as np
from scipy import stats

def population_stability_index(reference: np.ndarray, production: np.ndarray, n_bins=10) -> float:
    """PSI < 0.1: stable. 0.1–0.2: monitor. > 0.2: retrain."""
    ref_counts, bins = np.histogram(reference, bins=n_bins)
    prod_counts, _   = np.histogram(production, bins=bins)
    ref_pct  = ref_counts / ref_counts.sum() + 1e-8
    prod_pct = prod_counts / prod_counts.sum() + 1e-8
    return float(np.sum((prod_pct - ref_pct) * np.log(prod_pct / ref_pct)))

def ks_drift(reference: np.ndarray, production: np.ndarray, alpha=0.05) -> dict:
    """KS test for distributional shift. p < alpha → drift detected."""
    stat, p = stats.ks_2samp(reference, production)
    return {"statistic": float(stat), "p_value": float(p), "drift": p < alpha}

# Run for each feature
for col in feature_cols:
    psi = population_stability_index(X_train[col].values, X_prod[col].values)
    ks  = ks_drift(X_train[col].values, X_prod[col].values)
    if psi > 0.1 or ks["drift"]:
        print(f"DRIFT: {col}  PSI={psi:.3f}  KS p={ks['p_value']:.4f}")
```

### 8c. Concept Drift (Performance Degradation)

When ground-truth labels arrive with delay, track performance on labelled windows:

```python
# Rolling performance window — alert if primary metric drops below threshold
window_size = 500  # samples
alerts = []
for i in range(0, len(df_prod) - window_size, window_size // 2):
    window = df_prod.iloc[i:i+window_size]
    score  = f1_score(window["y_true"], window["y_pred"], average="weighted")
    if score < acceptance_threshold:
        alerts.append({"window_start": i, "score": score})
        print(f"CONCEPT DRIFT ALERT at offset {i}: F1={score:.3f}")
```

### 8d. Retraining Checklist

Before each scheduled retrain:

```
Pre-retrain
  Data drift check on all features (PSI + KS)                        PASS / FAIL
  Data quality check (missing rate, outlier rate, N_new)             PASS / FAIL
  Label quality audit (for supervised models)                        PASS / FAIL

Retraining
  Use same preprocessing pipeline (fitted on new training data)
  Use same CV strategy and metric as Phase 4
  Tune hyperparams only if drift is severe — minor retrains inherit tuned params
  Produce test-set accuracy report for the new model version

Post-retrain comparison
  New model primary metric ≥ old model metric − 1 pp                 PASS / FAIL
  New model beats dummy baseline by ≥ 10 pp                          PASS / FAIL
  Latency budget still met                                           PASS / FAIL
  Shadow deploy (route 10% traffic to new model) before full switch
```

### 8e. Model Registry Entry

Every trained model version must be logged:

```json
{
  "version":           "v3",
  "trained_at":        "2026-06-01T04:00:00Z",
  "n_train":           52480,
  "feature_count":     12,
  "hyperparams":       { "n_estimators": 200, "max_depth": 7 },
  "val_f1":            0.83,
  "test_f1":           0.81,
  "psi_max":           0.08,
  "latency_p95_ms":    14,
  "drift_trigger":     false,
  "retrain_reason":    "scheduled weekly",
  "deployed":          true,
  "replaced_version":  "v2"
}
```

---

## Output Format & Follow-through

### Write the report to `MODEL_REPORT.md` in the project root

Overwrite previous runs. Use this structure:

```markdown
# ML Model Report — <Project Name> / <Task Type>
Generated: <timestamp>
Model version: <vN>
Data snapshot: <hash or path>
RNG seed: <int>

## Constraint Summary
- Task: <type>
- Primary metric: <name> ≥ <threshold>
- Training budget: <time/compute>
- Inference budget: <latency>
- Interpretability required: yes/no
- Fairness audit required: yes/no

## Algorithm Decision Record
- Selected: <algorithm>
- Retained: <algorithm (if any)>
- Rejected: <algorithm> — <one-line reason>
- Rejected: <algorithm> — <one-line reason>

## Validation Design
- Split strategy: <method>
- CV folds: <k>
- Metric: <primary> (secondary: <metric>)
- Threshold: <value> (optimised on val set)

## Accuracy Results
- Dummy baseline:  <score>
- Primary model:   <score> (val) / <score> (test)
- Prior model:     <score> (if applicable)
- Folds variance:  <std>
- Statistical sig: p=<value> (<significant/not significant>)
- Acceptance gate: PASS / FAIL
- Fairness gate:   PASS / FAIL / N/A

## Enhancement Summary
- Features added/dropped: <list>
- Tuning method: <method>, <n_trials> trials
- Best hyperparams: <key params>
- Experiment log: <path / MLflow run URI>
- Ensemble: <yes/no, method>

## Production Readiness
- Model size: <MB>
- p50 latency: <ms>
- p95 latency: <ms>
- Storage: <path/bucket> (manifest committed to repo, model file not)

## Maintenance Schedule
- Retraining cadence: <cadence>
- Drift check: <PSI threshold> / <KS alpha>
- Alert threshold: primary metric < <value>
- Next scheduled retrain: <date>

## Open Items
- <anything that failed a gate and needs resolution>
```

### Append failed gates to `TODO.md`

Every FAIL in the report becomes a remediation task under a `## ML Model Remediation` section in `TODO.md` (create the section if missing). Format:

```markdown
- [ ] [GATE: Accuracy] Primary metric 0.71 < 0.80 threshold — see MODEL_REPORT.md
- [ ] [GATE: Fairness] DI ratio 0.62 < 0.80 (4/5 rule) on region slice — see MODEL_REPORT.md §6e
```

### Hand off to `/ml-inside`

After a model passes all gates and is ready to ship, the human-readable spec document (formulas, feature definitions, calculation walkthrough, known limitations) is `/ml-inside`'s job. End the run with:

> "Model passes all gates. Run `/ml-inside` to generate the spec document."

### State the GO / NO-GO verdict in chat

End the session with an explicit one-line verdict. GO requires all hard gates PASS and any open items resolved or explicitly accepted by the user.

---

## Rules

### Process
- Never select an algorithm without completing Phase 0 and Phase 1
- Never report test-set results until Phase 6 — keep the test set sealed
- Never tune hyperparameters on the test set
- The primary metric is locked at Phase 0 — never change it post-hoc to make the model look better
- Time-series data must never be randomly shuffled for splitting

### Quality
- Complexity must be justified by ablation — if removing a component costs < 0.5 pp, remove it
- All models must beat the dummy baseline by the Phase 0 delta (default 10 pp) or the task framing is wrong
- Acceptance thresholds in Phase 6 are defaults — high-stakes models tighten, low-stakes can loosen, both must be explicit

### Reproducibility (non-negotiable)
- Every RNG source seeded (`random_state`, `numpy.random.seed`, framework seeds) and the seed recorded in the manifest
- Data snapshot identified by hash, version tag, or DB query timestamp — recorded in the manifest
- Python environment pinned (`pyproject.toml` + lock file, or `requirements.txt` with hashes)
- Any tuning sweep > 10 trials must be logged (MLflow / W&B / experiments/runs.csv)

### Production
- Every trained model version must have a manifest entry and a rejection/selection reason
- Model files never committed to git — manifest yes, artifact in object storage
- Retraining must use the same held-out test set construction logic — never overfit to a fixed test set over time
- For regulated/PH-market decisions, fairness audit (6e) is mandatory and DPA implications are handed off to `/ph-dpa-compliance`
