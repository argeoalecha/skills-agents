#!/usr/bin/env python3
"""Convert Markdown (.md) files into R Markdown (.Rmd) files.

Wraps the body in a valid R Markdown YAML frontmatter (title, date, html_document
output with TOC) so the file opens and knits cleanly in RStudio. Plain fenced code
blocks (```lang) are left as-is -- they stay syntax-highlighted display blocks and
are never executed. Pass --live-r to turn ```r fences into live {r} knitr chunks.

Output defaults to the current working directory (the project/workspace folder
this script was invoked from), not alongside the source file. Batch conversions
mirror the source directory's subfolder structure under that output root.
"""

import argparse
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
R_FENCE_RE = re.compile(r"^```r\s*$", re.MULTILINE)


def humanize(stem):
    return re.sub(r"[-_]+", " ", stem).strip().title()


def extract_title(body, fallback):
    match = H1_RE.search(body)
    return match.group(1).strip() if match else fallback


def strip_existing_frontmatter(text):
    return FRONTMATTER_RE.sub("", text, count=1)


def make_frontmatter(title, theme, toc_depth):
    safe_title = title.replace('"', "'")
    return (
        "---\n"
        f'title: "{safe_title}"\n'
        f'date: "{date.today().isoformat()}"\n'
        "output:\n"
        "  html_document:\n"
        "    toc: true\n"
        "    toc_float: true\n"
        f"    toc_depth: {toc_depth}\n"
        f"    theme: {theme}\n"
        "    highlight: tango\n"
        "    df_print: paged\n"
        "---\n\n"
    )


def make_r_chunks_live(body):
    return R_FENCE_RE.sub("```{r}", body)


def convert_file(src, dest, theme, toc_depth, live_r):
    raw = src.read_text(encoding="utf-8")
    body = strip_existing_frontmatter(raw)
    title = extract_title(body, humanize(src.stem))
    if live_r:
        body = make_r_chunks_live(body)
    dest.write_text(make_frontmatter(title, theme, toc_depth) + body, encoding="utf-8")


def render_html(rmd):
    html = rmd.with_suffix(".preview.html")
    subprocess.run(
        [
            "pandoc",
            str(rmd),
            "--from",
            "markdown",
            "-o",
            str(html),
            "--standalone",
            "--toc",
            "--metadata",
            f"pagetitle={rmd.stem}",
        ],
        check=True,
    )
    return html


def collect_targets(source):
    if source.is_dir():
        return sorted(source.rglob("*.md"))
    return [source]


def main():
    parser = argparse.ArgumentParser(description="Convert .md docs to R Markdown (.Rmd)")
    parser.add_argument("source", type=Path, help=".md file or a directory to convert")
    parser.add_argument(
        "-o", "--out-dir", type=Path, default=None,
        help="Output directory (default: current working directory -- the "
             "project/workspace folder the skill was invoked from)",
    )
    parser.add_argument("--theme", default="flatly", help="RStudio bootswatch theme (default: flatly)")
    parser.add_argument("--toc-depth", type=int, default=3)
    parser.add_argument(
        "--live-r", action="store_true",
        help="Turn ```r fences into executable {r} knitr chunks (off by default)",
    )
    parser.add_argument(
        "--render", action="store_true",
        help="Also render an immediate HTML preview via pandoc (no R packages required)",
    )
    args = parser.parse_args()

    if not args.source.exists():
        sys.exit(f"error: {args.source} not found")

    targets = collect_targets(args.source)
    if not targets:
        sys.exit(f"error: no .md files found under {args.source}")

    if args.render and not shutil.which("pandoc"):
        sys.exit("error: --render requires pandoc on PATH")

    out_base = args.out_dir or Path.cwd()
    root = args.source if args.source.is_dir() else args.source.parent

    for src in targets:
        rel_dir = src.parent.relative_to(root)
        out_dir = out_base / rel_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        dest = out_dir / (src.stem + ".Rmd")
        convert_file(src, dest, args.theme, args.toc_depth, args.live_r)
        print(f"wrote {dest}")
        if args.render:
            html = render_html(dest)
            print(f"wrote {html}")


if __name__ == "__main__":
    main()
