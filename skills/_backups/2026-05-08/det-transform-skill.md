---
name: det-transform
description: >
  Data cleaning and transformation skill for the data-analyst project. Use when the user
  asks to clean, transform, reshape, filter, aggregate, or prepare a dataset — including:
  removing duplicates, handling missing values, detecting outliers, type inference,
  SQL-like operations (SELECT/WHERE/GROUP BY/JOIN), Power Query-style operations
  (PIVOT/UNPIVOT/text ops/method chaining), and end-to-end analytics pipelines.
  Source code lives at: ~/projects-mvp/data-analyst/backend/app/agents/data_extract_transform/
---

# DET Transform Skill

Two engines are available. Choose based on the task:

---

## Engine Selection Guide

| Task | Engine | Why |
|---|---|---|
| Filter rows, select columns, join, group/aggregate | `DataTransformationEngine` | SQL-like chaining |
| Pivot wide→long, unpivot long→wide, split/merge columns | `PowerQueryTransformations` | Power Query-style |
| Sort, deduplicate, column ops with method chaining | Either — prefer `PowerQueryBuilder` | Fluent interface |
| Multi-step pipeline combining both | Use both — chain engines | Each handles what it does best |

---

## Engine 1: DataTransformationEngine (SQL-like)

Source: `app/agents/data_extract_transform/transformation_engine.py`

```python
from app.agents.data_extract_transform.transformation_engine import DataTransformationEngine

engine = DataTransformationEngine()
engine.load_data(df)   # call first — copies df internally

result = (engine
  .select(['col1', 'col2', 'amount'])
  .where(lambda df: df['amount'] > 0)
  .where(lambda df: df['date'] >= '2024-01-01')
  .rename_columns({'old_name': 'new_name'})
  .create_column('profit', lambda df: df['revenue'] - df['cost'])
  .groupby_agg(by=['category'], aggs={'amount': 'sum', 'order_id': 'count'})
  .clean_data()
)

df_result = engine.get_dataframe()
print(engine.quality_score())     # float 0-100
print(engine.get_history())       # list of operations applied
print(engine.get_summary_statistics())
```

**All methods return `self` for chaining** (except `get_dataframe`, `quality_score`, `get_history`, `get_summary_statistics`).

See `references/sql-transforms.md` for full method signatures, parameter options, and common issues.

### Key methods

| Method | What it does |
|---|---|
| `select(cols)` | Keep only listed columns |
| `where(lambda df: ...)` | Filter rows — compound conditions with `&` / `\|` |
| `rename_columns({'old': 'new'})` | Rename one or more columns |
| `create_column('name', lambda df: ...)` | Compute a new column |
| `groupby_agg(by=[], aggs={})` | GROUP BY with aggregation |
| `join(other_df, on='key', how='left')` | Join on a shared key column |
| `clean_data()` | Drop exact duplicates + reset index |

---

## Engine 2: PowerQueryTransformations (Power Query-style)

Source: `app/agents/data_extract_transform/power_query.py`

### Option A — PowerQueryBuilder (fluent chaining, limited ops)

```python
from app.agents.data_extract_transform.power_query import PowerQueryBuilder

df_result = (
    PowerQueryBuilder(df)
    .merge_columns(['first_name', 'last_name'], ' ')
    .split_column('address', ',')
    .remove_duplicates()
    .sort(by=['date'])
    .execute()   # always end with .execute()
)
```

### Option B — PowerQueryTransformations (full feature set)

```python
from app.agents.data_extract_transform.power_query import (
    PowerQueryTransformations, PivotConfig, UnpivotConfig
)

pq = PowerQueryTransformations(df)
```

**Pivot (long → wide):**
```python
df_wide = pq.pivot(PivotConfig(
    index=['date'],
    columns=['product'],
    values=['sales'],
    aggfunc='sum',
    fill_value=0
))
```

**Unpivot (wide → long):**
```python
df_long = pq.unpivot(UnpivotConfig(
    id_vars=['Product'],
    value_vars=['Jan', 'Feb', 'Mar'],
    var_name='Month',
    value_name='Sales'
))
```

**Other operations:** `merge()`, `append()`, `split_column()`, `merge_columns()`, `remove_duplicates()`, `sort()`, `fill_down()`, `fill_up()`, `add_conditional_column()`, `group_and_aggregate()`, `replace_values()`, `expand_list_column()`

See `references/power-query-transforms.md` for full signatures and real-world examples.

---

## Standard Pipeline Pattern

```python
import pandas as pd
from app.agents.data_extract_transform.transformation_engine import DataTransformationEngine
from app.agents.data_extract_transform.power_query import PowerQueryTransformations, PivotConfig

# 1. Load
df_raw = pd.read_csv('data/input.csv')

# 2. Clean + filter with SQL engine
engine = DataTransformationEngine()
engine.load_data(df_raw)
(engine
 .select(['id', 'category', 'region', 'amount', 'date'])
 .where(lambda df: df['amount'] > 0)
 .where(lambda df: df['date'] >= '2024-01-01')
 .clean_data()
)
df_clean = engine.get_dataframe()

# 3. Reshape with Power Query engine
pq = PowerQueryTransformations(df_clean)
df_pivot = pq.pivot(PivotConfig(
    index=['region'],
    columns=['category'],
    values=['amount'],
    aggfunc='sum',
    fill_value=0
))

# 4. Inspect quality
print(f"Quality score: {engine.quality_score():.1f}/100")
print(f"Shape: {df_pivot.shape}")

# 5. Export
df_pivot.to_excel('data/output.xlsx', index=False)
```

---

## Working Directory

All scripts relative to: `~/projects-mvp/data-analyst/backend/`

```bash
cd ~/projects-mvp/data-analyst/backend
source .venv/bin/activate  # activate virtualenv
python3 -c "from app.agents.data_extract_transform.transformation_engine import DataTransformationEngine; print('OK')"
```

---

## Common Issues

| Problem | Cause | Fix |
|---|---|---|
| `KeyError` on `select` | Column name mismatch | Print `df.columns` first |
| `groupby_agg` wrong shape | Multiple agg functions per col not supported | One agg string per column |
| `join` fails on key mismatch | Different key names in both dfs | Use `PowerQueryTransformations.merge(left_on=..., right_on=...)` |
| Low quality score | Many nulls or duplicates | Run `clean_data()`, handle nulls with pandas before loading |
| Import error | venv not activated or package missing | `source .venv/bin/activate && pip install -r requirements.txt` |
