#!/usr/bin/env python3
"""
Generate an OKF index.md for a directory (progressive disclosure).

Scans a single directory's concept files, reads each one's frontmatter
`title` and `description`, and writes an index.md listing them. Subdirectories
are listed too. index.md and log.md are skipped.

The bundle-root index may carry an okf_version declaration; pass --root to add
`okf_version: "0.1"` frontmatter (the only place frontmatter is allowed in an
index file).

Usage:
    python gen_index.py <directory> [--root] [--version 0.1]
"""
from __future__ import annotations
import sys
from pathlib import Path

RESERVED = {"index.md", "log.md"}


def read_meta(path: Path):
    text = path.read_text(encoding="utf-8")
    title, desc = None, None
    if text.lstrip().startswith("---"):
        lines = text.splitlines()
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                break
            ln = lines[i]
            if ln.startswith("title:"):
                title = ln.split(":", 1)[1].strip()
            elif ln.startswith("description:"):
                desc = ln.split(":", 1)[1].strip()
    if not title:
        title = path.stem.replace("-", " ").replace("_", " ").title()
    return title, desc


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = [a for a in argv[1:] if a.startswith("--")]
    if len(args) < 1:
        print(__doc__)
        return 2
    d = Path(args[0]).resolve()
    if not d.is_dir():
        print(f"ERROR: not a directory: {d}")
        return 2

    is_root = "--root" in flags
    version = "0.1"
    for fl in flags:
        if fl.startswith("--version"):
            parts = fl.split("=", 1)
            if len(parts) == 2:
                version = parts[1]

    concepts = []
    subdirs = []
    for child in sorted(d.iterdir()):
        if child.is_dir():
            subdirs.append(child)
        elif child.suffix == ".md" and child.name not in RESERVED:
            concepts.append(child)

    out = []
    if is_root:
        out.append("---")
        out.append(f'okf_version: "{version}"')
        out.append("---")
        out.append("")

    dir_title = d.name.replace("-", " ").replace("_", " ").title() or "Bundle"
    out.append(f"# {dir_title}")
    out.append("")

    if concepts:
        out.append("# Concepts")
        out.append("")
        for c in concepts:
            title, desc = read_meta(c)
            line = f"* [{title}]({c.name})"
            if desc:
                line += f" - {desc}"
            out.append(line)
        out.append("")

    if subdirs:
        out.append("# Sections")
        out.append("")
        for s in subdirs:
            out.append(f"* [{s.name.replace('-', ' ').title()}]({s.name}/index.md)")
        out.append("")

    index_path = d / "index.md"
    index_path.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {index_path} ({len(concepts)} concepts, {len(subdirs)} subdirs)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
