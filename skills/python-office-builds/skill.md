---
name: python-office-builds
description: Build Word (.docx) and Excel (.xlsx) deliverables with Python — python-docx, openpyxl, pandas, xlsxwriter — as reproducible build scripts, themed (Hayah-AI by default) and verified by render + formula recalc. Use when the user asks for a .docx or .xlsx produced with Python, a python-docx/openpyxl/xlsxwriter script, a report or workbook generated from data (pandas, SQL, CSV, API), a recurring report generator, or a fix to such a script. Not for tracked changes/redlines/comments on an existing Word file (use the docx skill) or Google Docs/Sheets.
---

# Python Office Builds (.docx / .xlsx)

Every deliverable is produced by a **build script** (`build_<name>.py`) that can be re-run on next month's data. The file is the output; the script is the asset.

Helpers live beside this file: `scripts/officekit.py` (theme + docx/xlsx builders) and `scripts/verify.py` (lint, render, recalc). `SKILL_DIR=~/.claude/skills/python-office-builds`; `sys.path.insert(0, f"{SKILL_DIR}/scripts")`. A complete worked example (docx report + xlsx workbook from one DataFrame) is in `examples/build_sample.py`. If `scripts/` is missing, write raw python-docx/openpyxl and still apply every gotcha below.

## 1. Route the request

| Request | Tool | Why |
|---|---|---|
| New .docx from data/content | **python-docx + officekit** | data is already in Python; no Node hop |
| Client supplied a branded .docx template with placeholders | **docxtpl** (`pip install docxtpl`, Jinja tags in the .docx) | keeps their styles exactly |
| Edit text/tables in an existing .docx (amend a contract, revise a client template) | python-docx in place — **§5a** | never rebuild a client file from scratch |
| Tracked changes, comments, redlines | **built-in `docx` skill** (raw XML) | python-docx can't write `w:ins`/`w:del` |
| New .xlsx with formulas, styling, native charts | **openpyxl + officekit** | default |
| Bulk export > ~100k rows, write-once | **xlsxwriter** `Workbook(path, {"constant_memory": True})` or `df.to_excel(engine="xlsxwriter")` | much faster, low RAM; cannot read/edit — never mix with openpyxl on one file |
| Edit existing .xlsx/.xlsm | openpyxl `load_workbook(p, keep_vba=True for .xlsm)` | match the file's conventions; touch input cells only |
| Read/inspect | `pandoc -t markdown f.docx`, `markitdown f.xlsx`, `pd.read_excel(sheet_name=None)` | |
| Deliverable is a PDF | build .docx, convert via LibreOffice (`verify.py` already produces it) | one source, two formats |

Check imports before installing: `python -c "import docx, openpyxl, xlsxwriter, pandas"`. Install only what fails (`pip install python-docx openpyxl xlsxwriter` — add `--break-system-packages` in sandboxes). On macOS the system `python3` lacks these and Homebrew Python refuses global installs (PEP 668): use the project's venv, or create one (`python3 -m venv .venv && .venv/bin/pip install python-docx openpyxl xlsxwriter pandas matplotlib`). Never install into `~/projects-mvp` globally. `verify.py` needs LibreOffice (`soffice`) and `pdftoppm` (poppler) on PATH — both present on this machine.

## 2. Workflow

1. **Content first.** Load and transform the data, compute the numbers, draft the text. Layout comes last — a polished shell around thin content is the failure mode.
2. **Write the build script** with this shape:
   ```python
   # build_energy_report.py
   CONFIG = dict(period="2026-10", src="data/meter.csv", out="out/Energy_Report_2026-10.docx", theme="hayah")
   def load(cfg) -> pd.DataFrame: ...
   def transform(df) -> dict: ...          # all numbers computed here
   def render_docx(ctx, cfg): ...          # layout only, no maths
   def render_xlsx(ctx, cfg): ...
   if __name__ == "__main__": ctx = transform(load(CONFIG)); render_docx(ctx, CONFIG)
   ```
   Deterministic: no network or `random` in render; seed any synthetic data; date stamps come from CONFIG, not `now()`, unless the user wants "generated at".
   **When a .docx and an .xlsx share data** (a contract appendix and its budget workbook), put the data in one register module (`register.py`: constants, a list of row dicts, `totals()`, and a `check()` of the invariants: unique refs, allowed values, cross-field rules). Every builder imports it and calls `reg.check()` at import, so a bad edit fails both builds instead of shipping two documents that disagree.
3. **Run it**, then **verify**:
   ```bash
   python "$SKILL_DIR/scripts/verify.py" out/report.docx           # lint + PDF + page PNGs (TOC refreshed in preview)
   python "$SKILL_DIR/scripts/verify.py" out/model.xlsx --render   # lint + recalc in place + error scan (+ PNGs)
   python "$SKILL_DIR/scripts/verify.py" out/amended.docx --baseline=client_source.docx  # source's own issues → "inherited", not failures
   python "$SKILL_DIR/scripts/verify.py" out/long.docx --pages=17-22  # PNGs default to pages 1-12; "rendered" says when more exist
   ```
   Exit 0 = clean, 1 = issues (fix them all), 2 = tool failure (report it, don't hide it). **Open the PNGs and look** — verify passes on files that are ugly or wrong. xlsx recalc rewrites the file in place: verify a copy when the workbook is a shipped deliverable.
   **Prove a refactor changed nothing:** rebuild to a scratch path and diff against the shipped file — xlsx cell by cell (`ws[c].value`), docx paragraph and table-cell text plus per-run bold/italic/size/color. Zero diffs, then overwrite.
4. **Deliver** the file. Hand over the build script too when the report recurs or the user is a developer.
5. File naming: `Client_Deliverable_YYYY-MM[_vN].ext` — no spaces, sortable.

## 3. officekit reference

```python
import sys; sys.path.insert(0, f"{SKILL_DIR}/scripts")
from officekit import *
T = get_theme("hayah")                 # or "neutral"; get_theme("hayah", brand_fonts=True)

# DOCX
doc = new_document(T, paper="A4")      # "Letter" | "Legal" | "Long" (8.5x13); landscape=True
set_core_props(doc, "Title", author="Hayah-AI")
add_header_footer(doc, "Hayah-AI · Report", "October 2026", footer_left="Confidential")  # Page X of Y
add_title(doc, "Title", "Subtitle", "Prepared 31 October 2026")
add_toc(doc)                           # Word fills on open; preview fills via verify.py
doc.add_heading("1. Summary", 1)       # always built-in Heading N (TOC depends on it)
add_rich(doc, ["Total ", ("99,891 kWh", {"bold": True}), " — ", ("+6%", {"color": T["accent"]})])
add_callout(doc, "Key finding text", label="Finding")
add_bullets(doc, ["a", ["b ", ("bold", {"bold": True})]])
add_numbered_list(doc, ["step 1", "step 2"])   # restarts at 1 (plain add_bullets(numbered=True) continues)
add_table(doc, header, rows, col_widths_in=[3.2, 1.6, 1.4], align=["l","r","r"], total_row=True, caption="Table 1 — …")
add_image(doc, "chart.png", caption="Figure 1 — …")
add_hyperlink(doc.add_paragraph("See: "), "dashboard", "https://…")
add_page_break(doc); add_rule(doc)
doc.save(out)
merge_runs(Document("client.docx"))    # before editing an existing file in place (§5a)

# XLSX
wb = new_workbook(T, "Summary"); ws = wb["Summary"]
r = write_title(ws, "Title", "Source: …")
info = write_table(ws, header, rows, start_row=r, formats={"kWh": "dec2", "Cost": "php", "Share": "pct"},
                   totals={"kWh": "SUM", "Cost": "SUM"}, table_name=None, widths={"Building": 18})
df_to_sheet(wb.create_sheet("Data"), df, formats={"Date": "date"}, table_name="RawData")
h, last = info["header_row"], info["last"]
add_chart(ws, "col", data_ref=(2, h, 2, last), cats_ref=(1, h+1, 1, last), anchor="F3", title="…", y_title="kWh")
add_list_validation(ws, "E2:E200", ["Open", "Closed"]); highlight_negative(ws, "D2:D200")
add_notes_sheet(wb, [("Tariff", "₱11.25/kWh — client-supplied input")], generated=CONFIG["period"])
set_print(ws, landscape=True, repeat_header_row=h)
wb.save(out)
```
`FMT` keys: `php php0 usd int dec2 pct date date_ph datetime kwh kw`. `xl_styles(T)` gives fonts/fills for inputs (blue on yellow), links (green), totals. Everything returns raw python-docx/openpyxl objects — drop to the native API freely.

## 4. Theme

- Default **hayah** (matches `/theme-hayahai` core palette): primary deep teal `#0A3D3A`, secondary `#1E6E66`, accent coral `#FF6B47`, success `#25A497`, tints `#E8F4F1`/`#F3FFF9`, muted `#7A9B96`, text `#2C3E3A`.
- Fonts default to **Georgia / Calibri / Consolas** — installed on every Office machine. Playfair Display / Inter (`brand_fonts=True`) only for files that stay in-house or will be exported to PDF on a machine that has them; otherwise Word substitutes and layouts shift.
- Client deliverables under the client's identity: `get_theme("neutral")` or pass their own dict with the same keys — if `/theme-client` has run, build the dict from `<project-root>/brand/theme.json`. Never mix two brands in one file.
- Coral is for emphasis/negatives only — one or two hits per page.

## 5. DOCX gotchas (python-docx)

- **Default template is US Letter.** PH clients: A4; government/legal submissions often "Long" bond (8.5×13). `new_document(paper=…)` sets it.
- **Landscape does not swap dimensions** — set orientation *and* swap width/height (helper does both).
- **Fonts:** `style.font.name` writes only ascii/hAnsi; also set `w:eastAsia`/`w:cs` and drop theme-font attributes or Word substitutes. `_set_font` handles it.
- **Tables:** set `table.autofit=False`, fixed layout, and a width on **every cell** (column widths alone are ignored by Word/Google Docs). Shading uses `w:shd val="clear"` + fill — `solid` renders black. Mark the header row `w:tblHeader` so it repeats across pages.
- **Lists:** use `List Bullet`/`List Number` styles, never literal `•`. `List Number` continues across the document — use `add_numbered_list` for a fresh 1.
- **No `\n` in text** — one paragraph per line; line break inside a paragraph is `run.add_break()`.
- **TOC/page numbers are fields**: empty until rendered. Helper sets `updateFields` so Word refreshes on open (user may see a prompt — expected). PDFs from `verify.py` are pre-refreshed.
- **Horizontal rules:** paragraph bottom border, never a 1-row table.
- **Images:** `add_picture(width=Inches(…))`, cap at text width; PNG at 200 dpi. Generate charts with matplotlib: theme `series` colors, `ConciseDateFormatter` for date axes (default labels collide), spines off, bars start at zero.
- **Editing an existing doc:** see §5a. Don't use `paragraph.text = …` (wipes run formatting).
- **Placeholders** (`TBD`, `{{…}}`, `lorem`) never ship — verify.py flags them.

## 5a. Editing a client .docx in place

The source (a signed-off FINAL, a client template) is the layout; the script only changes words, rows and annexes. The build reads the source and writes a new file, never overwriting the source.

1. **`merge_runs(doc)` first.** Word splits one visible phrase across many runs (spell-check, revision ids). Writing into `runs[0]` and blanking the rest of an unmerged paragraph runs without error but leaves fragments: "2026September 2026", "Title..", a stray trailing letter. `merge_runs` joins adjacent runs with identical formatting and is idempotent, so it is safe on an already-clean file. Keep a copy inside the project's build script if the project must build without this skill on the path.
2. **Find by prefix, exactly once.** `hits = [p for p in paras if p.text.strip().startswith(prefix)]`; raise unless `len(hits) == 1`. Iterate `body.iterchildren(w:p)` rather than `doc.paragraphs` once you start inserting. A moved or renamed clause then fails loudly instead of editing the wrong paragraph.
3. **Keep label runs, replace the body run.** Contract clauses are `"Section 2.4."` (bold) + `"  Title."` (underlined) + body (plain). Pick the first non-bold, non-underlined run with text, write the new body into it, and blank only the runs after it.
4. **Clone, don't create.** New clauses, definitions, table rows and appendix headers: `copy.deepcopy(template._p)` / `template._tr`, then `anchor._p.addnext(new)`, then set text. Formatting, numbering and spacing come along. Set `cell.width` on every cloned cell.
5. **Deletion guards.** Never remove a paragraph whose `pPr` holds a `w:sectPr` (it ends a section and deletes its page setup). After removing images, drop image relationships no longer referenced in `document.xml`, or the file keeps the dead bytes.
6. **Embedding another document** (a proposal as an appendix): convert it to PDF with LibreOffice, `pdftoppm -png -r 150`, then insert one picture per page, capped at text width, with a "page N of M" caption cloned from the source.
7. **Verify with `--baseline=<source>`.** Inherited layout (cover-page blank paragraphs, missing Heading styles in a legal document) is reported as `inherited` instead of failing the check. Report it to the user, don't fix it silently.
8. **Typography last:** normalise straight apostrophes to `’` across `w:t` nodes only if the source already uses curly quotes.

## 6. XLSX gotchas (openpyxl)

- **Formulas, not Python results.** Totals, shares, costs are `=SUM(...)`, `=B5*$B$3`. Only raw data and stated inputs are literals.
- **openpyxl writes no cached values** → pandas / `data_only=True` / previewers see `None` until recalculated. `verify.py` recalcs in place via LibreOffice. Never ship while it reports errors. Set `wb.calculation.fullCalcOnLoad = True` (`new_workbook` does) so Excel recomputes on open regardless.
- **Function compatibility:** no `XLOOKUP XMATCH FILTER SORT UNIQUE SEQUENCE LET LAMBDA` (not evaluable outside Excel 365, spill metadata absent) — use `INDEX/MATCH`, `SUMIFS`, and sort/filter in pandas. `TEXTJOIN CONCAT IFS SWITCH MAXIFS MINIFS` need the `_xlfn.` prefix.
- **Sheet refs:** names with spaces must be quoted `='Sales Data'!B2`. Sheet names ≤31 chars, none of `[]:*?/\`.
- **Datetimes:** Excel rejects tz-aware values. Convert to PHT first (`s.dt.tz_convert("Asia/Manila").dt.tz_localize(None)`), *then* strip — stripping UTC silently shifts times by 8 h. Always set a date `number_format`.
- **NaN/NaT/numpy scalars** → `_clean()` handles them in `write_table`; raw `ws.append` will write `nan` strings or crash.
- **Numbers as text:** never write `f"{x:,.2f}"` into a cell; write the float and set `number_format`. (In .docx tables, formatted strings are correct.)
- **Percentages stored as fractions** (0.153 with `0.0%`).
- **`data_only=True` + save destroys every formula.** Read-only use only.
- **Merged cells:** write the top-left anchor only. Prefer "center across selection" or no merges in data regions — they break sort/filter/pandas.
- **Excel Tables:** `displayName` unique, no spaces; header cells must be strings; don't also set `auto_filter` on the same range.
- **Charts:** openpyxl ≥3.1 hides axes unless `axis.delete = False`; bar/column axes must start at 0 (`add_chart` sets both). Reference ranges, never hardcode values.
- **Limits:** 1,048,576 rows × 16,384 cols per sheet; split by period/category beyond ~500k rows or ship CSV/Parquet alongside.
- **Column widths** are estimates (openpyxl can't measure text) — `autofit()` then override key columns.
- **.xlsm:** `keep_vba=True` or macros are dropped. **External links** (`'[1]Sheet'!A1`): don't re-save/recalc — values are lost; verify.py refuses.

## 7. Workbook conventions

- Tab order: **Summary → working sheets → Data → Notes**. Summary readable without scrolling right.
- Inputs: blue font on light-yellow fill, each in its own labelled cell, referenced absolutely (`$B$3`). Formulas black; cross-sheet links green.
- Every hardcoded number gets a line on the **Notes** sheet (source, date, who supplied it). Peso amounts: `FMT["php"]` (`₱#,##0.00`, negatives in parentheses, zero as `-`).
- VAT (12%), tariffs, FX rates, escalation % are inputs, never literals inside formulas.
- Freeze header panes, filters on data tables, print setup (fit to width, repeat header, "Page X of Y") on any sheet that may be printed. Without it a 7-column Summary prints its last columns on a separate page. In a hand-rolled build, apply it in one loop over `wb.worksheets` with a `{sheet: header_row}` map.
- Build 2–3 formulas, recalc, check against pandas, *then* fill the grid. A clean recalc proves formulas evaluate, not that they're right.

## 8. Final checklist

- [ ] verify.py exit 0 (`--baseline` for edited client files); PNGs inspected (no overflow, overlaps, clipped tables, orphan headings, empty pages), including pages past 12 via `--pages`
- [ ] Shared data: every builder calls the register's `check()`; doc and workbook totals agree
- [ ] xlsx: recalc `total_errors: 0`; spot-check 2–3 totals against pandas
- [ ] Numbers in the doc match the workbook/source exactly (same rounding)
- [ ] Core properties set (title, author); no placeholder text; filename follows convention
- [ ] Build script re-runs cleanly from a fresh shell

## 9. Related skills (jurisdiction)

| Skill | Boundary |
|---|---|
| `document-skills:docx` / `document-skills:xlsx` | Plugin skills, not Python build scripts. Use them for tracked changes, comments, redlines, and raw-XML surgery on existing files. This skill owns reproducible Python-generated deliverables. |
| `/excel-to-python-notebook` | Reverse direction: an existing formula workbook → validated Python. This skill goes Python/data → workbook. A converted notebook that must hand results back as a styled .xlsx calls `officekit` for the export. |
| `/jupyter-notebook` | Notebooks are the analysis; when a notebook's output is a client .docx/.xlsx, its export cell imports `officekit` instead of hand-styling openpyxl. |
| `/sheets-app-dev` | Google Sheets as a live database. This skill produces offline .xlsx files; Google Sheets/Docs are out of scope. |
| `/ee-spec-writer`, `/ee-load-calc` | Markdown spec / calc output is the source; instrument schedules, BOQs, and load schedules with live formulas are built here. |
| `/theme-hayahai`, `/theme-client` | Source of brand colors; this skill's `THEMES["hayah"]` mirrors the core palette. |
| `document-skills:pdf` | PDF manipulation (merge, split, forms). For a PDF *deliverable* built from content, build the .docx here and let `verify.py` export it. |
