---
name: jupyter-notebook
description: Creates production-ready Jupyter notebooks (.ipynb) as downloadable files. Use this skill whenever the user asks to "put X in a notebook", "create a Jupyter notebook for Y", "document this as a notebook", "make this into a .ipynb", or wants to turn any analysis, scraping pipeline, data workflow, API integration, or code tutorial into a structured notebook. Also trigger when the user mentions Jupyter, IPython, Google Colab, or .ipynb explicitly. Do NOT skip this skill for notebook requests — always read it first before writing any notebook generation code.
---

# Jupyter Notebook Creator

Produces well-structured, immediately executable `.ipynb` files using the safe `json.dump()` build pattern. Always read this skill before generating any notebook.

---

## Critical Build Pattern

**Never** use `nbformat.new_code_cell()` with Python triple-quoted strings as the builder script source. Python's parser will fail on:
- Em dashes (`—`) inside triple-quoted strings
- Peso signs (`₱`) and other multi-byte Unicode inside string literals
- Unmatched triple quotes inside f-strings inside triple-quoted strings
- Raw regex patterns without r-strings

**Always** use `json.dump()` to write the `.ipynb` directly:

```python
import json

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source}

def code(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source
    }

cells = []
cells.append(md("## Section Title"))
cells.append(code('print("hello world")'))

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {"name": "python", "version": "3.12.3"}
    },
    "cells": cells
}

with open("output.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
```

Use `ensure_ascii=False` so Unicode renders correctly in the notebook without breaking the builder script.

---

## Cell Content Rules

### Markdown cells
- Plain markdown string — no restrictions on Unicode, emojis, or special characters
- Tables, headers, bold, lists, code fences all supported
- Use for: section headers, documentation, data dictionaries, instructions

### Code cells
- The `source` string is the literal Python code users will run
- Unicode in code cells is fine — it's just stored as a JSON string
- Regex patterns with backslashes: use raw strings in the cell source (`r"\d+"`)
- Triple-quoted docstrings inside cell source: escape as `\"\"\"` or use single-quoted `'''`
- f-strings with braces: standard Python — no escaping needed in the JSON value

### Common trap — escaped content in the builder vs. in the notebook
The cell `source` field is a JSON string. What you write in Python becomes what users see. Example:

```python
# Builder script (Python):
cells.append(code(r'pattern = re.findall(r"\d+", text)'))

# Notebook shows users:
# pattern = re.findall(r"\d+", text)
```

---

## Standard Notebook Structure

Every notebook should follow this anatomy:

```
Cell 0:  Title (markdown) — name, objective, data sources table
Cell 1:  Setup & install  (code) — pip installs, one-time setup
Cell 2:  Imports & config (code) — all imports + API keys + constants
Cell 3+: Logical sections (markdown header + code pairs)
Last:    Next steps / export / summary (markdown)
```

### Title cell template
```python
cells.append(md("""# Notebook Title
### Subtitle or context line
---
**Objective:** One sentence.

**Sources / Inputs:**

| # | Source | Method | Notes |
|---|--------|--------|-------|
| 1 | ...    | ...    | ...   |
"""))
```

### Setup cell template
```python
cells.append(code("""import subprocess, sys

packages = ["httpx", "pandas", "openpyxl"]
for pkg in packages:
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

print("All packages ready")
"""))
```

### Config cell template (API keys)
```python
cells.append(code("""import os

CONFIG = {
    "API_KEY": os.getenv("API_KEY", "YOUR_API_KEY_HERE"),
    "DELAY":   2,
}

for key, val in CONFIG.items():
    if "KEY" in key:
        status = "NOT SET" if str(val).startswith("YOUR_") else "CONFIGURED"
        print(f"  {key}: {status}")
"""))
```

---

## Output & Validation

### File path
Always write to `/home/claude/` first, validate, then copy to `/mnt/user-data/outputs/`:

```python
import nbformat

NB_PATH = "/home/claude/my_notebook.ipynb"

# Write
with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

# Validate (non-fatal MissingIDFieldWarning is OK to ignore)
nb_check = nbformat.read(NB_PATH, as_version=4)
print(f"Validation passed — {len(nb_check.cells)} cells")

# Copy to outputs
import shutil
shutil.copy(NB_PATH, "/mnt/user-data/outputs/my_notebook.ipynb")
```

### Validation checklist before copying to outputs
- [ ] `json.dump()` completed without exception
- [ ] `nbformat.read()` loaded without `SyntaxError` or `JSONDecodeError`
- [ ] Cell count matches expected section count
- [ ] At least one markdown cell and one code cell present

---

## Notebook Design Principles

**One concept per cell pair.** Each logical section = one markdown header cell + one code cell. Never cram multiple unrelated operations into one code cell.

**Every code cell must be independently runnable** after running Setup and Imports. No hidden state dependencies between non-sequential cells.

**Config in one place.** All API keys, file paths, and tunable parameters go in the Config cell (Cell 2). Never scatter magic strings across cells.

**Fail gracefully.** Wrap external API calls in try/except. Print clear messages when keys are missing rather than crashing. Users will run this without a developer present.

**Progressive output.** Each cell should `print()` something — a count, a status, a sample row. Silent cells frustrate notebook users.

**Last cell = actionable.** Always end with a summary cell showing total outputs, file path of the export, and next steps.

---

## Common Notebook Types & Section Patterns

### Data Scraping Notebook
```
Title → Setup → Imports/Config → [Source 1 scraper] → [Source 2 scraper]
→ Merge & Deduplicate → Enrich → Score/Filter → Export → Next Steps
```

### Data Analysis Notebook
```
Title → Setup → Imports/Config → Load Data → EDA (shape, dtypes, nulls)
→ Cleaning → Feature Engineering → Analysis/Visualization → Summary → Export
```

### API Integration Notebook
```
Title → Setup → Imports/Config → Auth/Connection Test → [Endpoint 1]
→ [Endpoint 2] → Data Processing → Export → Next Steps
```

### Tutorial/Documentation Notebook
```
Title → Overview → Concept 1 (markdown + code example) → Concept 2
→ ... → Full Example → Exercises → References
```

---

## Excel Export Pattern (common companion to notebooks)

```python
cells.append(code("""from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter
import pandas as pd

def export_excel(df, path, sheet_name="Results"):
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        wb = writer.book
        ws = wb[sheet_name]

        # Style header row
        header_fill = PatternFill("solid", fgColor="0D9488")
        header_font = Font(color="FFFFFF", bold=True)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        # Auto-width columns
        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 4, 45)

        ws.freeze_panes = "A2"

    print(f"Exported {len(df)} rows -> {path}")

export_excel(df_results, "output/results.xlsx")
"""))
```

---

## Delivery

```bash
# Copy builder script output to outputs dir
cp /home/claude/notebook_name.ipynb /mnt/user-data/outputs/notebook_name.ipynb
```

Then call `present_files` with the output path. The notebook downloads as `.ipynb` and opens directly in Jupyter Lab, VS Code, or Google Colab.

Include a brief note after presenting:
- How to open (Jupyter Lab / VS Code / Colab)
- Which cells to configure before running (API keys)
- Expected runtime for long-running cells
