# Power Query Transformation Reference

## Two Entry Points

### PowerQueryBuilder — fluent method chaining (limited ops)
```python
from app.agents.data_extract_transform.power_query import PowerQueryBuilder

df_result = (
    PowerQueryBuilder(df)
    .method_1(...)
    .method_2(...)
    .execute()   # Always call at the end to get the DataFrame
)
```

### PowerQueryTransformations — direct operations (full feature set)
```python
from app.agents.data_extract_transform.power_query import PowerQueryTransformations, PivotConfig, UnpivotConfig

pq = PowerQueryTransformations(df)
result = pq.some_operation(...)   # Returns a new DataFrame
```

---

## PowerQueryBuilder Methods

`PowerQueryBuilder` wraps `PowerQueryTransformations` with a chainable interface. Only the following methods are available:

```python
# Pivot / Unpivot
.pivot(config: PivotConfig) -> PowerQueryBuilder
.unpivot(config: UnpivotConfig) -> PowerQueryBuilder

# Column operations
.merge_columns(columns: list[str], delimiter: str = ' ') -> PowerQueryBuilder
.split_column(column: str, delimiter: str = ' ') -> PowerQueryBuilder

# Row operations
.remove_duplicates() -> PowerQueryBuilder
.sort(by: list[str]) -> PowerQueryBuilder

# Finalize
.execute() -> pd.DataFrame
```

Example:
```python
df_result = (
    PowerQueryBuilder(df)
    .merge_columns(['first_name', 'last_name'], ' ')
    .split_column('address', ',')
    .remove_duplicates()
    .sort(by=['date', 'amount'])
    .execute()
)
```

For operations not on `PowerQueryBuilder`, use `PowerQueryTransformations` directly.

---

## PowerQueryTransformations Methods

All methods return a `pd.DataFrame`.

### Pivot — Long → Wide
```python
pq = PowerQueryTransformations(df)
df_wide = pq.pivot(PivotConfig(
    index=['date'],           # Row identifiers
    columns=['product'],      # Column headers come from these values
    values=['sales'],         # Values to aggregate
    aggfunc='sum',            # "sum" | "mean" | "count" | "min" | "max"
    fill_value=0,             # Optional: fill NaN in pivoted table
    margins=False             # Optional: add totals row/column
))
```

**Example transformation:**
```
Input (long):                      Output (wide):
date       product  sales          date        ProductA  ProductB
2024-01    A        100            2024-01     100       200
2024-01    B        200            2024-02     150       300
```

### Unpivot — Wide → Long
```python
df_long = pq.unpivot(UnpivotConfig(
    id_vars=['Product'],              # Columns to keep as-is
    value_vars=['Jan', 'Feb', 'Mar'], # Columns to melt (required)
    var_name='Month',                 # Name for the new variable column
    value_name='Sales'                # Name for the new value column
))
```

**Example transformation:**
```
Input (wide):                      Output (long):
Product  Jan  Feb  Mar             Product  Month  Sales
A        100  110  120             A        Jan    100
B        200  210  220             A        Feb    110
                                   A        Mar    120
```

### Transpose
```python
df_transposed = pq.transpose()   # Swaps rows and columns
```

### Merge (Join two DataFrames)
```python
# Same key name in both
df_merged = pq.merge(other_df, on='customer_id', how='left')

# Different key names
df_merged = pq.merge(other_df, left_on='cust_id', right_on='id', how='inner')

# Join types: "left" | "right" | "inner" | "outer"
```

### Append (Stack rows)
```python
df_appended = pq.append(other_df, ignore_index=True)
```

### Split Column
```python
# Splits in-place, inserts new columns after the source column
df_split = pq.split_column('full_name', ' ', num_splits=1, column_names=['first', 'last'])
```

### Merge Columns
```python
df_merged = pq.merge_columns(['first', 'last'], delimiter=' ', new_column_name='full_name')
```

### Duplicate Column
```python
df_dup = pq.duplicate_column('amount', 'amount_backup')
```

### Remove Duplicates
```python
df_deduped = pq.remove_duplicates(subset=['customer_id'], keep='first')
# subset: optional list of columns to check; omit to check all columns
```

### Sort
```python
df_sorted = pq.sort(by=['date', 'amount'], ascending=[True, False])
```

### Reverse Rows
```python
df_reversed = pq.reverse_rows()
```

### Fill Down / Fill Up
```python
df_filled = pq.fill_down('column_name')   # Forward fill (ffill)
df_filled = pq.fill_up('column_name')     # Backward fill (bfill)
```

### Unpivot Other Columns
```python
# Unpivots all columns NOT in columns_to_keep; creates "attribute" and "value" cols
df_long = pq.unpivot_other_columns(columns_to_keep=['Product', 'Region'])
```

### Expand List Column
```python
# Explodes a column containing lists into one row per element
df_exploded = pq.expand_list_column('tags')
```

### Replace Values
```python
df_replaced = pq.replace_values('status', {'active': 1, 'inactive': 0})
```

### Add Conditional Column
```python
# conditions: list of (predicate_function, value) tuples
# predicate receives the full DataFrame and must return a boolean Series
df_cond = pq.add_conditional_column(
    'tier',
    [
        (lambda df: df['amount'] > 10000, 'Premium'),
        (lambda df: df['amount'] > 5000, 'Gold'),
        (lambda df: df['amount'] > 1000, 'Silver'),
    ],
    else_value='Standard'
)
```

### Group and Aggregate
```python
# aggregations dict: {column: agg_function_string}
df_grouped = pq.group_and_aggregate(
    group_by=['category', 'region'],
    aggregations={'amount': 'sum', 'quantity': 'mean'}
)
```

---

## Transformation History
```python
pq.get_transformation_history()   # Returns list of operation dicts
```

---

## Complete Real-World Examples

### Customer segmentation
```python
pq = PowerQueryTransformations(customers_df)
df = pq.merge_columns(['FirstName', 'LastName'], ' ', 'FullName')
df = PowerQueryTransformations(df).add_conditional_column(
    'Segment',
    [
        (lambda df: df['LifetimeValue'] > 100000, 'VIP'),
        (lambda df: df['LifetimeValue'] > 50000, 'Gold'),
        (lambda df: df['LifetimeValue'] > 10000, 'Silver'),
    ],
    else_value='Standard'
)
```

### Time series wide-to-long then sort
```python
monthly = pd.DataFrame({
    'Product': ['A', 'B'],
    'Jan': [100, 150], 'Feb': [110, 160], 'Mar': [120, 170]
})

pq = PowerQueryTransformations(monthly)
long_df = pq.unpivot(UnpivotConfig(
    id_vars=['Product'],
    value_vars=['Jan', 'Feb', 'Mar'],
    var_name='Month',
    value_name='Sales'
))

result = (
    PowerQueryBuilder(long_df)
    .sort(by=['Product', 'Month'])
    .execute()
)
```

### Sales pivot for cross-tab
```python
pq = PowerQueryTransformations(sales_df)
pivot = pq.pivot(PivotConfig(
    index=['Region'],
    columns=['Product'],
    values=['Revenue'],
    aggfunc='sum',
    fill_value=0
))
```
