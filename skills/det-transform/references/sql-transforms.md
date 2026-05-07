# SQL-like Transformation Reference

## DataTransformationEngine Methods

All methods return `self` for chaining (except `groupby_agg`, `quality_score`, `get_history`, `get_summary_statistics`, `get_dataframe`).

### load_data
```python
engine.load_data(df)  # Call first — copies df internally
```

### select
```python
engine.select(['customer_id', 'amount', 'date'])
```

### where
```python
# Single condition
engine.where(lambda df: df['amount'] > 1000)

# Compound condition
engine.where(lambda df: (df['category'] == 'Electronics') & (df['amount'] > 500))

# Date filter
engine.where(lambda df: df['date'] >= '2024-01-01')
```

### rename_columns
```python
engine.rename_columns({'customer_id': 'cust_id', 'old_name': 'new_name'})
```

### create_column
```python
# Simple formula
engine.create_column('profit', lambda df: df['amount'] - df['cost'])

# Using pd.cut for binning
engine.create_column('tier', lambda df: pd.cut(
    df['amount'],
    bins=[0, 100, 500, 1000, float('inf')],
    labels=['Low', 'Medium', 'High', 'Premium']
))
```

### groupby_agg → returns self (modifies internal df)
```python
engine.groupby_agg(
    by=['category', 'region'],
    aggs={'amount': 'sum', 'quantity': 'mean'}
)
# aggs values: any pandas agg string ('sum', 'mean', 'count', 'min', 'max', etc.)
```

### join
```python
# Inner join (default)
engine.join(customers_df, on='customer_id', how='inner')

# Left join
engine.join(customers_df, on='customer_id', how='left')

# Join types: "left" | "right" | "inner" | "outer"
# Note: only supports a single shared key column via `on`
# For different key names, use PowerQueryTransformations.merge() instead
```

### clean_data
```python
engine.clean_data()
# Drops exact duplicate rows and resets index
# Does NOT handle missing values or outliers — use pandas directly for those
```

### get_dataframe
```python
df_result = engine.get_dataframe()  # Returns a copy
```

### quality_score
```python
score = engine.quality_score()  # float 0-100
# Components:
#   Completeness (30 pts) — non-null cell ratio
#   Consistency  (25 pts) — columns with <90% unique or non-object dtype
#   Correctness  (25 pts) — penalizes inf values and all-null columns
#   Uniqueness   (20 pts) — penalizes duplicate rows
```

### get_history
```python
history = engine.get_history()
# Returns list of dicts: [{"operation": "load_data", "shape": [rows, cols]}, ...]
```

### get_summary_statistics
```python
stats = engine.get_summary_statistics()
# Returns: {
#   "shape": {"rows": int, "columns": int},
#   "null_counts": {col: int, ...},
#   "dtypes": {col: str, ...},
#   "numeric": {col: {"count", "mean", "std", "min", "25%", "50%", "75%", "max"}, ...}
# }
```

---

## Full Example

```python
from app.agents.data_extract_transform.transformation_engine import DataTransformationEngine
import pandas as pd

engine = DataTransformationEngine()
engine.load_data(raw_df)

(engine
 .select(['order_id', 'customer_id', 'amount', 'category', 'date'])
 .where(lambda df: df['date'] >= '2024-01-01')
 .where(lambda df: df['amount'] > 0)
 .rename_columns({'customer_id': 'cust_id'})
 .create_column('is_high_value', lambda df: df['amount'] > 5000)
 .groupby_agg(by=['category'], aggs={'amount': 'sum', 'order_id': 'count'})
 .clean_data()
)

df_result = engine.get_dataframe()
print(engine.quality_score())
print(engine.get_summary_statistics())
```

---

## Common Issues

| Problem | Cause | Fix |
|---|---|---|
| `KeyError` on select | Column name mismatch | Check `df.columns` first |
| `groupby_agg` returns wrong shape | Multiple agg functions per col not supported | Use one agg string per column |
| `join` fails on key mismatch | Different key names in both dfs | Use `PowerQueryTransformations.merge(left_on=..., right_on=...)` |
| Low quality score | Many nulls or duplicates | Run `clean_data()`, handle nulls with pandas before loading |
