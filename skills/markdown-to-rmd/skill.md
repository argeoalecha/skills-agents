---
name: markdown-to-rmd
description: Converts .md documents into R Markdown (.Rmd) files with a valid YAML frontmatter (title, TOC, theme) so they open and knit cleanly in RStudio for a more readable, styled rendering. Use whenever the user asks to convert a markdown doc to R Markdown/Rmd, wants "a better readable version" of a generated .md doc, mentions RStudio/knit/knitr, or wants to batch-convert a folder of .md docs to .Rmd. Not for creating brand-new R analysis notebooks from scratch with live executable R code -- this skill wraps existing prose docs, code fences stay display-only (non-executed) unless --live-r is explicitly requested.
---

# Markdown to R Markdown

Wraps existing `.md` files in valid R Markdown so they knit into a styled,
navigable document (TOC, theme, syntax highlighting) in RStudio, instead of
staying as flat GitHub-style markdown.

## When to use this vs. leaving the doc as .md

This is for making an *existing* generated doc more readable, not for writing
new R analysis. Default behavior treats every fenced code block as
display-only -- nothing executes on knit. Only opt into live `{r}` chunks if
the user actually wants R code in the doc to run.

## Workflow

1. **Identify the source** -- a single `.md` file, or a directory to
   batch-convert (all `*.md` files under it, recursively).
2. **Run the converter from the project/workspace folder** the skill was
   triggered from -- that's where output lands by default:
   ```bash
   python3 scripts/md_to_rmd.py path/to/doc.md
   ```
   This strips any existing YAML frontmatter, pulls the title from the first
   `# H1` (falling back to a humanized filename), and writes `doc.Rmd` into
   the **current working directory** (not next to the source `.md`) with a
   `html_document` frontmatter (TOC, `flatly` theme, `tango` highlighting).
   Use `-o/--out-dir` to send it somewhere else instead.
3. **Batch mode** -- pass a directory instead of a file to convert everything
   under it in one pass; each `.Rmd` lands in the current working directory,
   mirroring the source's subfolder structure:
   ```bash
   python3 scripts/md_to_rmd.py docs/
   ```
4. **Immediate preview (optional)** -- this machine has `pandoc` but not the R
   `rmarkdown`/`knitr` packages, so `rmarkdown::render()` / RStudio's Knit
   button aren't available here. Pass `--render` to get a plain-pandoc HTML
   preview alongside the `.Rmd` without needing those packages:
   ```bash
   python3 scripts/md_to_rmd.py path/to/doc.md --render
   ```
   Note this preview won't pick up the `theme:`/`toc_float:` styling (those
   are `rmarkdown::html_document` features) -- it's a readability check, not
   the final styled output. Tell the user the fully-styled version requires
   opening the `.Rmd` in RStudio and hitting Knit (RStudio ships `rmarkdown`
   by default), or installing the packages locally:
   `Rscript -e 'install.packages(c("rmarkdown","knitr"))'`.
5. **Live R chunks (rare)** -- only if the user explicitly wants embedded R
   code to execute on knit, add `--live-r`, which turns bare ` ```r ` fences
   into executable ` ```{r} ` chunks. Leave this off by default.

## Options

| Flag | Default | Purpose |
|---|---|---|
| `-o/--out-dir DIR` | current working directory | write all `.Rmd` output here instead |
| `--theme NAME` | `flatly` | any RStudio bootswatch theme (`cosmo`, `united`, `journal`, ...) |
| `--toc-depth N` | `3` | heading depth included in the table of contents |
| `--live-r` | off | convert ` ```r ` fences into executable `{r}` chunks |
| `--render` | off | also produce a `.preview.html` via plain pandoc |

## Edge cases and format compatibility

See `references/conversion-notes.md` for what carries over cleanly (tables,
task lists, footnotes, math) versus what needs manual attention (mermaid
diagrams don't render in base R Markdown; math needs `--mathjax` added to a
plain-pandoc render; existing frontmatter in the source is replaced, not
merged).

## After conversion

Report the output path(s) to the user and remind them: open the `.Rmd` in
RStudio and Knit for the full styled/TOC'd version, or use `--render` for a
quick plain-HTML readability check without RStudio.
