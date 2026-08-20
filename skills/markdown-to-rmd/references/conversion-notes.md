# Markdown -> R Markdown compatibility notes

R Markdown is pandoc's markdown dialect plus an optional knitr execution layer.
Most GitHub-flavored markdown (GFM) that Claude generates passes through unchanged.
The items below are the actual friction points.

## Passes through unchanged
- ATX headers (`#`, `##`, ...), bold/italic, blockquotes
- GFM tables
- Ordered/unordered lists, nested lists
- Task list checkboxes `- [ ]` / `- [x]`
- Inline code and plain fenced code blocks (```lang with no braces) -- rendered
  as syntax-highlighted, non-executed blocks
- Relative links and image paths
- HTML comments `<!-- -->`
- Footnotes (`[^1]`) -- pandoc supports these natively

## Needs attention
- **Fenced code blocks with curly braces** (` ```{r} `, ` ```{python} `) are knitr
  *chunk headers*, not plain fences. If source markdown ever contains one literally
  (e.g. a doc that teaches R Markdown itself), it will be treated as a live,
  executable chunk on knit. `md_to_rmd.py` does not create these unless `--live-r`
  is passed, and only for bare ` ```r ` fences.
- **Math** (`$inline$`, `$$block$$`) requires MathJax, which `html_document` loads
  by default when rendered with `rmarkdown::render()`. A plain `pandoc` render
  (no R packages) still handles it via `--mathjax`, not added by default here --
  add `--mathjax` to the render command if a doc has math and looks broken.
- **Mermaid diagrams** in fenced ` ```mermaid ` blocks do NOT render in base R
  Markdown -- pandoc/knitr has no built-in mermaid engine. They fall back to a
  plain code block showing the diagram source as text. If a doc leans on mermaid,
  either flag it to the user or swap in a static image before conversion.
- **YAML frontmatter already present** in the source `.md` (rare, but happens with
  some generated docs) is stripped and replaced by the script's own frontmatter
  rather than merged, to avoid producing two YAML blocks.

## Rendering without the `rmarkdown` R package
Full knitting (`rmarkdown::render()`) needs the R `rmarkdown` + `knitr` packages,
which may not be installed everywhere (check with `Rscript -e 'rmarkdown::pandoc_available()'`
or just try `--render`). `md_to_rmd.py --render` sidesteps this by calling `pandoc`
directly on the `.Rmd` file for an immediate `.preview.html`. This works because a
`.Rmd` with no live `{r}` chunks is, to pandoc, just markdown with YAML frontmatter --
nothing needs to execute. `theme:`/`highlight:` YAML keys are ignored by plain pandoc
(they're `rmarkdown::html_document` features), so the preview is plain pandoc HTML,
not themed. For the themed, fully-knitted version, open the `.Rmd` in RStudio (which
ships `rmarkdown` by default) and hit Knit.
