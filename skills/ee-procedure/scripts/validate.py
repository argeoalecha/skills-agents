"""Validate a procedure / plan .docx built with procbuild, or self-test the skill.

    python validate.py out/EX-1.03_...RevA.docx    # check one built document
    python validate.py                              # build the example, check it, run rejection tests

Exit 0 = every check passed, 1 = a check failed. Checks are structural and cross-reference
checks; they do not judge the engineering content (that is the PEE's review).
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from docx import Document  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402

FAILS: list[str] = []
COVER_LABELS = ("Project", "Deliverable", "Owner / Checked by", "Revision / Status", "Date")
PLACEHOLDER = re.compile(r"\bTBD\b|\{\{|\blorem\b|\bXXX\b", re.I)


def check(cond: bool, msg: str):
    print(f"  {'ok ' if cond else 'FAIL'} {msg}")
    if not cond:
        FAILS.append(msg)


def body_items(doc):
    """Paragraphs and tables in document order, with the heading context."""
    for el in doc.element.body.iterchildren():
        if el.tag == qn("w:p"):
            yield "p", el
        elif el.tag == qn("w:tbl"):
            yield "t", el


def ptext(el) -> str:
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def pstyle(el) -> str:
    s = el.find(f"{qn('w:pPr')}/{qn('w:pStyle')}")
    return s.get(qn("w:val")) if s is not None else ""


EXTERNAL_BEFORE = re.compile(r"(?:\b(?:PEC|NEC|NFPA|IEEE|IEC|ANSI|TIA|OSHS|RA|DOLE)(?:\s+[\w./-]+)?|§)\s*$")
EXTERNAL_AFTER = re.compile(r"^\s*(?:of|in)\s+(?:the\s+)?[A-Z]")


def local_refs(word: str, text: str) -> set[str]:
    """Numbers after 'Table' / 'Section' that refer to this document. A reference is
    external, and skipped, when a code name (PEC 2017, NFPA 70E, NEC, RA 7920 ...) or a
    section sign stands right before it, or 'of the <document>' follows it."""
    out = set()
    for m in re.finditer(rf"\b{word} ([0-9A-Z]+(?:\.\d+)*)", text):
        if word == "Section" and not m.group(1)[0].isdigit():
            continue
        before = text[max(0, m.start() - 24):m.start()]
        if EXTERNAL_BEFORE.search(before) or EXTERNAL_AFTER.match(text[m.end():m.end() + 30]):
            continue
        out.add(m.group(1))
    return out


def is_label(el) -> bool:
    """A short all-bold paragraph that introduces a table (Approval, Hold points ...)."""
    runs = [r for r in el.iter(qn("w:r")) if "".join(t.text or "" for t in r.iter(qn("w:t"))).strip()]
    return bool(runs) and len(ptext(el)) <= 60 and all(r.find(f"{qn('w:rPr')}/{qn('w:b')}") is not None for r in runs)


def table_rows(tbl):
    return [[ptext(tc) for tc in tr.iter(qn("w:tc"))] for tr in tbl.iter(qn("w:tr"))]


def validate_doc(path: str) -> None:
    doc = Document(path)
    items = list(body_items(doc))
    paras = [(pstyle(e), ptext(e)) for k, e in items if k == "p"]
    alltext = "\n".join(t for _, t in paras) + "\n" + "\n".join(
        " ".join(c for r in table_rows(e) for c in r) for k, e in items if k == "t")
    print(f"[1] House style and page furniture: {Path(path).name}")
    sec0 = doc.sections[0]
    check(round(sec0.page_width.inches, 2) == 8.5 and round(sec0.page_height.inches, 2) == 11.0,
          "first section is US Letter portrait")
    dflt = doc.styles.element.find(f"{qn('w:docDefaults')}/{qn('w:rPrDefault')}/{qn('w:rPr')}/{qn('w:rFonts')}")
    body_font = doc.styles["Normal"].font.name or (dflt.get(qn("w:ascii")) if dflt is not None else None)
    check(body_font == "Arial", f"body font is Arial ({body_font})")
    for i, sec in enumerate(doc.sections):
        hdr = " ".join(p.text for p in sec.header.paragraphs)
        ftr = sec.footer._element.xml
        land = sec.page_width > sec.page_height
        if land:
            check(round(sec.page_width.inches, 2) == 11.0, f"section {i + 1} landscape swaps width/height")
        check(bool(re.search(r"\S+ Rev [A-Z0-9]+$", hdr.strip())), f"section {i + 1} header ends '<ref> Rev X'")
        check("PAGE" in ftr and "NUMPAGES" in ftr, f"section {i + 1} footer has Page X of Y")

    print("[2] Cover: control block, approval, revision history, contents")
    tables = [table_rows(e) for k, e in items if k == "t"]
    labels = {r[0] for r in tables[0]} if tables else set()
    for lab in COVER_LABELS:
        check(lab in labels, f"control block has '{lab}'")
    texts = [t for _, t in paras]
    check(any(re.match(r"Deliverable \S+ +\| +Rev \S+ +\| ", t) for t in texts[:8]),
          "cover line 'Deliverable <ref> | Rev X | <status>'")
    appr = next((t for t in tables if t and t[0][1:4] == ["Prepared by", "Checked by", "Accepted by"]), None)
    check(appr is not None and [r[0] for r in appr[1:]] == ["Party", "Name", "Signature", "Date"],
          "approval table: Prepared / Checked / Accepted by, Party/Name/Signature/Date")
    revs = next((t for t in tables if t and t[0][:2] == ["Rev", "Date"]), None)
    check(revs is not None and len(revs) > 1, "revision history has at least one row")
    has_toc = "TOC \\o" in doc.element.body.xml
    check(has_toc or any(t.strip() == "Contents" for t in texts), "contents present (TOC field or static list)")

    print("[3] Numbering: sections, sub-sections, captions")
    h1 = [t for s, t in paras if s == "Heading1"]
    numbered = [t for t in h1 if re.match(r"\d+\. ", t)]
    nums = [int(t.split(".")[0]) for t in numbered]
    check(nums == list(range(1, len(nums) + 1)) and len(nums) > 0, f"sections numbered 1..{len(nums)} with no gaps")
    if has_toc:
        check("Contents" not in h1, "contents title is not a heading (TOC does not list itself)")
    apps = [t for t in h1 if t.startswith("Appendix ")]
    letters = [t.split()[1] for t in apps]
    check(letters == [chr(65 + i) for i in range(len(letters))], f"appendices lettered A..{letters[-1] if letters else '-'}")
    cur, last2 = None, 0
    ok2 = True
    for s, t in paras:
        if s == "Heading1":
            m = re.match(r"(\d+)\. |Appendix ([A-Z]) ", t)
            cur, last2 = (m.group(1) or m.group(2)) if m else None, 0
        elif s == "Heading2" and re.match(r"[0-9A-Z]+\.\d+ ", t):
            sec, sub = t.split()[0].split(".")
            if sec != cur or int(sub) != last2 + 1:
                ok2 = False
                print(f"       out of sequence: {t}")
            last2 = int(sub)
    check(ok2, "sub-sections n.1, n.2 ... follow their section")
    caps = [t for _, t in paras if re.match(r"Table [0-9A-Z]+\.\d+ - ", t)]
    seen, seq_ok = {}, True
    for c in caps:
        sec, n = c.split()[1].split(".")
        if int(n) != seen.get(sec, 0) + 1:
            seq_ok = False
            print(f"       caption out of sequence: {c}")
        seen[sec] = int(n)
    check(seq_ok, f"{len(caps)} table captions numbered per section")
    pre_app, uncaptioned = True, 0
    for i, (k, e) in enumerate(items):
        if k == "p" and pstyle(e) == "Heading1" and ptext(e).startswith("Appendix "):
            pre_app = False
        if k == "t" and pre_app and i > 0 and tables.index(table_rows(e)) > 2:
            nxt = items[i + 1] if i + 1 < len(items) else None
            prv = items[i - 1]
            captioned = nxt and nxt[0] == "p" and re.match(r"Table \d+\.\d+ - ", ptext(nxt[1]))
            labelled = prv[0] == "p" and is_label(prv[1])
            if not (captioned or labelled):
                uncaptioned += 1
    check(uncaptioned == 0, f"every body table before the appendices is captioned or labelled ({uncaptioned} not)")

    print("[4] Forms: heading, Feeds, Form rev, own section, index")
    form_heads = [(i, ptext(e)) for i, (k, e) in enumerate(items)
                  if k == "p" and pstyle(e) == "Heading2" and re.match(r"F-\d{2} - ", ptext(e))]
    codes = [t.split()[0] for _, t in form_heads]
    check(len(codes) == len(set(codes)), f"{len(codes)} forms, no duplicate codes")
    check(codes == sorted(codes), "forms in code order")
    for i, t in form_heads:
        intro = ptext(items[i + 1][1]) if items[i + 1][0] == "p" else ""
        check("Feeds:" in intro and "Form rev:" in intro, f"{t.split(' - ')[0]} states Feeds and Form rev")
        prev = items[i - 1][1] if i else None
        has_break = prev is not None and prev.find(f"{qn('w:pPr')}/{qn('w:sectPr')}") is not None
        check(has_break, f"{t.split(' - ')[0]} starts its own section")
    idx = next((t for t in tables if t and t[0][:3] == ["Form", "Title", "Orientation"]), None)
    if codes:
        listed = [r[0] for r in (idx or [])[1:] if re.fullmatch(r"F-\d{2}", r[0])]
        check(listed == codes, "form index lists exactly the forms in the document")
    signoff_forms = [t.split()[0] for _, t in form_heads
                     if re.search(r"sign-off|completion|verification", t, re.I)]
    for code in signoff_forms:
        i = next(i for i, t in form_heads if t.startswith(code))
        j = next((n for n, t in form_heads if n > i), len(items))
        has = any(k == "t" and table_rows(e)[0][:2] == ["Role", "Name"] for k, e in items[i:j])
        check(has, f"{code} (sign-off / completion / verification form) has a signature block")

    print("[5] Cross-references resolve")
    hp_def = set(re.findall(r"\b(HP-\d+) - ", alltext)) | {
        r[0] for t in tables for r in t[1:] if r and re.fullmatch(r"HP-\d+", r[0])}
    hp_used = set(re.findall(r"\bHP-\d+\b", alltext))
    check(hp_used <= hp_def, f"every hold point used is defined ({sorted(hp_used - hp_def) or 'all defined'})")
    f_used = set(re.findall(r"\bF-\d{2}\b", alltext))
    f_ranges = set()
    for a, b in re.findall(r"\bF-(\d{2}) to F-(\d{2})\b", alltext):
        f_ranges |= {f"F-{n:02d}" for n in range(int(a), int(b) + 1)}
    missing_f = sorted((f_used | f_ranges) - set(codes))
    check(not missing_f, f"every form referenced exists ({missing_f or 'all exist'})")
    internal = {str(n) for n in nums} | set(letters)
    subs = {t.split()[0] for s, t in paras if s == "Heading2" and re.match(r"[0-9A-Z]+\.\d+ ", t)}
    t_used = {r for r in local_refs("Table", alltext) if len(r.split(".")) == 2 and r.split(".")[0] in internal}
    t_def = {c.split()[1] for c in caps}
    check(t_used <= t_def, f"every 'Table n.m' referenced exists ({sorted(t_used - t_def) or 'all exist'})")
    s_refs = local_refs("Section", alltext)
    bad_s = sorted(r for r in s_refs if (len(r.split(".")) == 1 and not 1 <= int(r) <= len(nums))
                   or (len(r.split(".")) == 2 and r not in subs) or len(r.split(".")) > 2)
    check(not bad_s, f"every 'Section n' / 'Section n.m' referenced exists ({bad_s or 'all exist'})")

    print("[6] Content guards")
    check(not PLACEHOLDER.search(alltext), "no placeholder text (TBD, {{, lorem, XXX)")
    check("RA 7920" in alltext, "RA 7920 licensure boundary stated")
    check("PEE" in alltext, "PEE named as checker / Engineer of Record")


def self_test() -> None:
    import procbuild as pb
    with tempfile.TemporaryDirectory() as t:
        out = Path(t) / "EX-1.03_example.docx"
        ex = HERE.parent / "examples" / "build_example_procedure.py"
        import runpy
        sys.argv = [str(ex), str(out)]
        runpy.run_path(str(ex), run_name="__main__")
        validate_doc(str(out))
    print("[7] Builder rejects bad input")
    meta = dict(project="P", title="T", ref="X-1", rev="A", status="IFR", date="1 Jan 2026", header_title="H")
    spec = dict(code="F-01", title="T", purpose="P.", feeds="X", orientation="Portrait", completed="Daily")
    for name, fn in {
        "missing meta": lambda: pb.ProcDoc({k: v for k, v in meta.items() if k != "ref"}),
        "bad form code": lambda: pb.ProcDoc(meta).form_index([dict(spec, code="F-1")]),
        "incomplete form spec": lambda: pb.ProcDoc(meta).form_index([dict(spec, feeds="")]),
        "duplicate form": lambda: pb.ProcDoc(meta).form_index([spec, spec]),
        "form not in the index": lambda: pb.ProcDoc(meta).form("F-09"),
        "form built twice": lambda: [d := pb.ProcDoc(meta), d.form_index([spec]), d.form("F-01"), d.form("F-01")],
        "indexed form never built": lambda: [d := pb.ProcDoc(meta), d.form_index([spec]),
                                             d.save(tempfile.mktemp(suffix=".docx"))],
        "appendix form outside an appendix": lambda: pb.ProcDoc(meta).appendix_form("Transmittal"),
        "duplicate hold point": lambda: pb.ProcDoc(meta).hold_points([("HP-1", "a"), ("HP-1", "b")]),
        "bad hold point code": lambda: pb.ProcDoc(meta).hold_points([("H1", "a")]),
    }.items():
        try:
            fn()
            check(False, f"rejects {name}")
        except ValueError:
            check(True, f"rejects {name}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        validate_doc(sys.argv[1])
    else:
        self_test()
    print(f"\n{'ALL CHECKS PASSED' if not FAILS else f'{len(FAILS)} CHECK(S) FAILED'}")
    sys.exit(1 if FAILS else 0)
