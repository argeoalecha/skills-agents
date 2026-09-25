#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml"]
# ///
"""
Validate an OKF v0.2 bundle.

ERRORS (exit 1) — only the three hard conformance rules from the spec (§11):
  1. Every non-reserved .md file has a parseable YAML frontmatter block.
  2. Every frontmatter block has a non-empty `type` field.
  3. Reserved files follow their structure when present: index.md carries no
     frontmatter (bundle-root index.md may carry only okf_version); log.md
     date headings are ISO YYYY-MM-DD.

WARNINGS — soft guidance; the bundle stays conformant:
  - missing recommended fields (title, description)
  - v0.1 legacy: `timestamp` field, body `# Citations` section
  - timestamps that are not ISO 8601 datetimes with an explicit offset
  - `status` outside draft | stable | deprecated; concepts past `stale_after`
  - malformed `generated`, `verified`, `sources`; actors outside the convention
  - footnote labels with no matching sources[].id
  - Attested Computation missing `runtime` or a computation
  - broken cross-links (allowed — may be not-yet-written knowledge)

Usage:
    uv run validate.py <bundle-root>       # installs PyYAML automatically
    python3 validate.py <bundle-root>      # works without PyYAML, fewer checks

Without PyYAML a minimal top-level `key: value` parser is used, so checks on
nested fields (generated, verified, sources, parameters) are skipped.
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

RESERVED = {"index.md", "log.md"}
STATUSES = {"draft", "stable", "deprecated"}

try:
    import yaml  # type: ignore

    _HAVE_YAML = True
except Exception:
    _HAVE_YAML = False

DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})$"
)
ACTOR_RE = re.compile(r"^(human:\S+|process:\S+|[^\s/:]+/\S+)$")
FOOTNOTE_REF_RE = re.compile(r"\[\^([^\]\s]+)\](?!:)")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^(```|~~~)")


def split_frontmatter(text: str):
    """Return (frontmatter_dict_or_None, body, parse_ok, reason)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text, False, "no opening '---' on first line"
    close = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            close = i
            break
    if close is None:
        return None, text, False, "no closing '---' for frontmatter"
    block = "\n".join(lines[1:close])
    body = "\n".join(lines[close + 1:])
    if _HAVE_YAML:
        try:
            data = yaml.safe_load(block) or {}
        except Exception as e:
            return None, body, False, f"YAML parse error: {e}"
        if not isinstance(data, dict):
            return None, body, False, "frontmatter is not a mapping"
        return data, body, True, ""
    data = {}
    for ln in block.splitlines():
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.*)$", ln)
        if m:
            data[m.group(1)] = m.group(2).strip().strip("'\"")
    return data, body, True, ""


def unfenced_lines(body: str):
    in_fence = False
    for ln in body.splitlines():
        if FENCE_RE.match(ln.strip()):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield ln


def timestamp_problem(value) -> str | None:
    """None if value is an ISO 8601 datetime with explicit offset."""
    if isinstance(value, dt.datetime):
        return None if value.tzinfo is not None else "datetime has no UTC offset"
    if isinstance(value, dt.date):
        return "bare date, needs a datetime with offset"
    if isinstance(value, str) and DATETIME_RE.match(value.strip()):
        return None
    return "not an ISO 8601 datetime with explicit offset"


def as_aware(value):
    if isinstance(value, dt.datetime) and value.tzinfo is not None:
        return value
    if isinstance(value, str) and DATETIME_RE.match(value.strip()):
        s = value.strip().replace(" ", "T")
        s = re.sub(r"Z$", "+00:00", s)
        s = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", s)
        try:
            return dt.datetime.fromisoformat(s)
        except ValueError:
            return None
    return None


def check_actor_events(rel, key, value, warnings):
    """Validate generated (single mapping) or verified (mapping or list)."""
    events = value if isinstance(value, list) else [value]
    for ev in events:
        if not isinstance(ev, dict):
            warnings.append(f"{rel}: `{key}` entries must be {{ by, at }} mappings")
            continue
        by = ev.get("by")
        if not by:
            warnings.append(f"{rel}: `{key}.by` is required")
        elif not ACTOR_RE.match(str(by)):
            warnings.append(
                f"{rel}: `{key}.by: {by}` is not an actor "
                "(<producer>/<version>, human:<id>, process:<id>)"
            )
        if "at" in ev:
            p = timestamp_problem(ev["at"])
            if p:
                warnings.append(f"{rel}: `{key}.at` {p}")
        elif key == "verified":
            warnings.append(f"{rel}: `verified.at` is missing")


def check_concept(rel, fm, body, warnings, now):
    for rec in ("title", "description"):
        if not fm.get(rec):
            warnings.append(f"{rel}: missing recommended field `{rec}`")

    if "timestamp" in fm:
        warnings.append(f"{rel}: v0.1 `timestamp` is superseded — use `generated: {{ by, at }}`")
    if any(ln.strip().lower() == "# citations" for ln in unfenced_lines(body)):
        warnings.append(f"{rel}: v0.1 `# Citations` section is superseded — use `sources` + footnotes")

    status = fm.get("status")
    if status is not None and str(status) not in STATUSES:
        warnings.append(
            f"{rel}: `status: {status}` is not draft | stable | deprecated "
            "(move domain states to another key)"
        )

    if "stale_after" in fm:
        p = timestamp_problem(fm["stale_after"])
        if p:
            warnings.append(f"{rel}: `stale_after` {p}")
        else:
            when = as_aware(fm["stale_after"])
            if when and now >= when:
                warnings.append(f"{rel}: stale since {fm['stale_after']} (past `stale_after`)")

    if _HAVE_YAML:
        tags = fm.get("tags")
        if tags is not None and not isinstance(tags, list):
            warnings.append(f"{rel}: `tags` should be a YAML list")
        if "generated" in fm:
            if isinstance(fm["generated"], list):
                warnings.append(f"{rel}: `generated` is a single {{ by, at }} mapping, not a list")
            else:
                check_actor_events(rel, "generated", fm["generated"], warnings)
        if "verified" in fm:
            check_actor_events(rel, "verified", fm["verified"], warnings)

    source_ids: set[str] = set()
    if _HAVE_YAML and "sources" in fm:
        sources = fm["sources"]
        if not isinstance(sources, list):
            warnings.append(f"{rel}: `sources` should be a list")
            sources = []
        for i, s in enumerate(sources):
            if not isinstance(s, dict):
                warnings.append(f"{rel}: sources[{i}] should be a mapping")
                continue
            if not s.get("resource"):
                warnings.append(f"{rel}: sources[{i}] is missing required `resource`")
            sid = s.get("id")
            if sid is not None:
                if str(sid) in source_ids:
                    warnings.append(f"{rel}: duplicate sources id `{sid}`")
                source_ids.add(str(sid))
            if "last_modified" in s:
                p = timestamp_problem(s["last_modified"])
                if p:
                    warnings.append(f"{rel}: sources[{i}].last_modified {p}")
            if "usage_count" in s and "usage_window" not in s and "usage_window" not in fm:
                warnings.append(f"{rel}: sources[{i}].usage_count has no `usage_window`")
        uw = fm.get("usage_window")
        if uw is not None:
            if not isinstance(uw, dict):
                warnings.append(f"{rel}: `usage_window` should be a {{ from, to }} mapping")
            else:
                for k in ("from", "to"):
                    p = timestamp_problem(uw.get(k))
                    if p:
                        warnings.append(f"{rel}: `usage_window.{k}` {p}")
        refs = {m.group(1) for ln in unfenced_lines(body) for m in FOOTNOTE_REF_RE.finditer(ln)}
        for label in sorted(refs - source_ids):
            warnings.append(f"{rel}: footnote [^{label}] has no matching sources[].id")

    if str(fm.get("type", "")).strip() == "Attested Computation":
        if not fm.get("runtime"):
            warnings.append(f"{rel}: Attested Computation is missing required `runtime`")
        has_heading = any(ln.strip().lower() == "# computation" for ln in unfenced_lines(body))
        if not fm.get("computation") and not has_heading:
            warnings.append(
                f"{rel}: Attested Computation has neither `computation` nor a `# Computation` section"
            )


def check_index(path: Path, is_root: bool, rel, errors, warnings):
    text = path.read_text(encoding="utf-8")
    if not text.lstrip().startswith("---"):
        if is_root:
            warnings.append(f"{rel}: bundle root does not declare `okf_version`")
        return
    fm, _, ok, reason = split_frontmatter(text)
    if not ok:
        errors.append(f"[rule 3] {rel}: unparseable index frontmatter ({reason})")
        return
    extra = set(fm) - {"okf_version"}
    if extra:
        errors.append(f"[rule 3] {rel}: index.md must not carry frontmatter (found {sorted(extra)})")
    if "okf_version" in fm:
        if not is_root:
            errors.append(f"[rule 3] {rel}: okf_version is only allowed in the bundle-root index.md")
        elif str(fm["okf_version"]) != "0.2":
            warnings.append(f"{rel}: declares okf_version {fm['okf_version']!r}; this validator targets 0.2")


def check_log(path: Path, rel, errors, warnings):
    dates = []
    for ln in unfenced_lines(path.read_text(encoding="utf-8")):
        if ln.startswith("## "):
            head = ln[3:].strip()
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", head):
                errors.append(f"[rule 3] {rel}: log heading `{head}` is not ISO YYYY-MM-DD")
            else:
                dates.append(head)
    if dates != sorted(dates, reverse=True):
        warnings.append(f"{rel}: log entries should be newest first")


def link_target(src: Path, root: Path, href: str):
    href = href.split("#", 1)[0]
    if not href.endswith(".md") or re.match(r"^[a-z][a-z0-9+.-]*:", href, re.I):
        return None
    if href.startswith("/"):
        return (root / href.lstrip("/")).resolve()
    return (src.parent / href).resolve()


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = Path(argv[1]).resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}")
        return 2

    now = dt.datetime.now(dt.timezone.utc)
    errors: list[str] = []
    warnings: list[str] = []
    concept_count = 0

    md_files = sorted(root.rglob("*.md"))
    for f in md_files:
        rel = f.relative_to(root)
        if f.name == "index.md":
            check_index(f, f.parent == root, rel, errors, warnings)
            continue
        if f.name == "log.md":
            check_log(f, rel, errors, warnings)
            continue

        concept_count += 1
        fm, body, ok, reason = split_frontmatter(f.read_text(encoding="utf-8"))
        if not ok:
            errors.append(f"[rule 1] {rel}: unparseable frontmatter ({reason})")
            continue
        type_val = fm.get("type")
        if type_val is None or str(type_val).strip() == "":
            errors.append(f"[rule 2] {rel}: missing or empty `type`")
        check_concept(rel, fm, body, warnings, now)

    for f in md_files:
        rel = f.relative_to(root)
        for ln in unfenced_lines(f.read_text(encoding="utf-8")):
            for m in LINK_RE.finditer(ln):
                target = link_target(f, root, m.group(1))
                if target is not None and not target.exists():
                    warnings.append(
                        f"{rel}: link to missing concept {m.group(1)} (allowed — may be not-yet-written)"
                    )

    print(f"OKF v0.2 validation — {root}")
    print(f"  concepts checked: {concept_count}")
    print(f"  errors:   {len(errors)}")
    print(f"  warnings: {len(warnings)}")
    if not _HAVE_YAML:
        print("  note: PyYAML not installed — nested-field checks skipped (use `uv run validate.py`)")
    if errors:
        print("\nERRORS (hard-rule violations — bundle is NOT conformant):")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print("\nWarnings (soft guidance — bundle remains conformant):")
        for w in warnings:
            print(f"  • {w}")
    if not errors:
        print("\n✓ CONFORMANT with OKF v0.2.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
