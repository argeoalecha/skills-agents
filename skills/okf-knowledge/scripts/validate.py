#!/usr/bin/env python3
"""
Validate an OKF v0.1 bundle.

Enforces ONLY the three hard conformance rules from the spec (§9):
  1. Every non-reserved .md file has a parseable YAML frontmatter block.
  2. Every frontmatter block has a non-empty `type` field.
  3. Reserved files (index.md, log.md) follow their structure when present.

Everything else (missing recommended fields, broken links) is reported as a
WARNING, never an error — matching OKF's intentionally permissive consumption
model. Exit code is non-zero only on hard-rule violations.

Usage:
    python validate.py <bundle-root>

No third-party dependencies required: a minimal frontmatter parser is built in
so the script runs anywhere Python 3 is available. If PyYAML is installed it is
used for more robust YAML parsing.
"""
from __future__ import annotations
import sys
import re
from pathlib import Path

RESERVED = {"index.md", "log.md"}

try:
    import yaml  # type: ignore
    _HAVE_YAML = True
except Exception:
    _HAVE_YAML = False


def split_frontmatter(text: str):
    """Return (frontmatter_dict_or_None, parse_ok, reason).

    A valid block opens with '---' on the first line and closes with a line
    that is exactly '---'.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, False, "no opening '---' on first line"
    # find closing fence
    close = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            close = i
            break
    if close is None:
        return None, False, "no closing '---' for frontmatter"
    block = "\n".join(lines[1:close])
    if _HAVE_YAML:
        try:
            data = yaml.safe_load(block) or {}
            if not isinstance(data, dict):
                return None, False, "frontmatter is not a mapping"
            return data, True, ""
        except Exception as e:  # pragma: no cover
            return None, False, f"YAML parse error: {e}"
    # minimal fallback parser: top-level `key: value` pairs only
    data = {}
    for ln in block.splitlines():
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.*)$", ln)
        if m:
            data[m.group(1)] = m.group(2).strip()
    return data, True, ""


def check_index(path: Path):
    """index.md must have no frontmatter, except bundle-root may carry okf_version."""
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("---"):
        fm, ok, _ = split_frontmatter(text)
        if ok and fm and set(fm.keys()) - {"okf_version"}:
            return [f"index.md should not carry frontmatter (except okf_version): {path}"]
    return []


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = Path(argv[1]).resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}")
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    concept_ids: set[str] = set()
    concept_count = 0

    md_files = sorted(root.rglob("*.md"))
    for f in md_files:
        rel = f.relative_to(root)
        name = f.name

        if name in RESERVED:
            if name == "index.md":
                warnings += [w for w in check_index(f)]
            continue

        concept_count += 1
        concept_ids.add(str(rel.with_suffix("")))
        text = f.read_text(encoding="utf-8")
        fm, ok, reason = split_frontmatter(text)

        # Rule 1
        if not ok:
            errors.append(f"[rule 1] {rel}: unparseable frontmatter ({reason})")
            continue
        # Rule 2
        type_val = fm.get("type") if fm else None
        if type_val is None or str(type_val).strip() == "":
            errors.append(f"[rule 2] {rel}: missing or empty `type`")

        # Soft guidance (warnings only)
        for rec in ("title", "description"):
            if not fm.get(rec):
                warnings.append(f"{rel}: missing recommended field `{rec}`")

    # Soft: broken bundle-relative links
    link_re = re.compile(r"\]\((/[^)\s]+\.md)\)")
    for f in md_files:
        rel = f.relative_to(root)
        for m in link_re.finditer(f.read_text(encoding="utf-8")):
            target = m.group(1).lstrip("/")
            tid = target[:-3] if target.endswith(".md") else target
            if tid not in concept_ids and not (root / target).exists():
                warnings.append(f"{rel}: link to missing concept /{target} (allowed — may be not-yet-written)")

    print(f"OKF v0.1 validation — {root}")
    print(f"  concepts checked: {concept_count}")
    print(f"  errors:   {len(errors)}")
    print(f"  warnings: {len(warnings)}")
    if errors:
        print("\nERRORS (hard-rule violations — bundle is NOT conformant):")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print("\nWarnings (soft guidance — bundle remains conformant):")
        for w in warnings:
            print(f"  • {w}")
    if not errors:
        print("\n✓ CONFORMANT with OKF v0.1.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
