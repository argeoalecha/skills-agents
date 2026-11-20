"""procbuild — house-style builder for electrical engineering procedures, execution
plans and their field forms (.docx), on top of python-office-builds/officekit.

    import sys; sys.path.insert(0, "<skill_dir>/scripts")
    from procbuild import ProcDoc, opts

House style (matches the reference deliverables): US Letter, Arial 10 pt, black
headings 15 / 12 / 10.5 pt, grey D9D9D9 table headers, F2F2F2 group rows and field
labels, 808080 cell borders, italic grey captions "Table n.m - Title", forms F-nn each in
their own portrait or landscape section, header "<title> <tab> <ref> Rev X" with a
bottom rule, centred footer "Page X of Y".

Inline markup in any text: **bold**. Everything returns python-docx objects.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Sequence

_OFFICEKIT = Path(__file__).resolve().parents[2] / "python-office-builds" / "scripts"
sys.path.insert(0, str(_OFFICEKIT))
import officekit as ok  # noqa: E402

from docx.enum.section import WD_ORIENT, WD_SECTION  # noqa: E402
from docx.enum.table import WD_TABLE_ALIGNMENT  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Twips  # noqa: E402

FONT = "Arial"
GREY_HDR, GREY_GRP, BORDER = "D9D9D9", "F2F2F2", "808080"
MUTED, COVER_GREY = "595959", "404040"
TEXT_W = 9360          # twips, Letter portrait with 1 in side margins
TEXT_W_LAND = 12960    # Letter landscape
BOX = "☐"         # ☐
STATUS = {"IFR": "Issued for Review", "IFA": "Issued for Acceptance", "IFU": "Issued for Use",
          "IFC": "Issued for Comment"}
FORM_KEYS = ("code", "title", "purpose", "feeds", "orientation", "completed")


def opts(choices: Sequence[str]) -> str:
    """Tick-box options for a form cell: opts(['Yes','No','UNK']) -> '☐ Yes ☐ No ☐ UNK'."""
    return " ".join(f"{BOX} {c}" for c in choices)


def _runs(p, text: str, size: float, bold: bool = False, italic: bool = False,
          color: str | None = None):
    """Add text to paragraph p, honouring **bold** markup."""
    parts = re.split(r"(\*\*[^*]+\*\*)", text or "")
    for part in parts:
        if not part:
            continue
        b = bold or (part.startswith("**") and part.endswith("**"))
        r = p.add_run(part[2:-2] if part.startswith("**") and part.endswith("**") else part)
        ok._set_font(r, FONT, size, color, bold=b)
        r.italic = italic or None
    return p


def _spacing(p, before: int = 0, after: int = 0):
    pf = p.paragraph_format
    pf.space_before, pf.space_after = Twips(before), Twips(after)


class ProcDoc:
    """One procedure / plan document. Build top to bottom, then save()."""

    def __init__(self, meta: dict):
        need = ("project", "title", "ref", "rev", "status", "date", "header_title")
        missing = [k for k in need if not meta.get(k)]
        if missing:
            raise ValueError(f"meta missing: {', '.join(missing)}")
        self.meta = meta
        self.doc = ok.new_document(ok.get_theme("neutral"), paper="Letter", margins_in=1.0,
                                   body_size=10)
        self._style()
        sec = self.doc.sections[0]
        sec.top_margin, sec.bottom_margin = Twips(1300), Twips(1100)
        sec.header_distance = sec.footer_distance = Twips(708)
        self._header_footer(sec)
        self.h1_no, self.h2_no, self.appendix_no = 0, 0, 0
        self.table_no = 0
        self.in_appendix = False
        self.form_specs: dict[str, dict] = {}
        self.built_forms: list[str] = []
        self.hp_codes: list[str] = []
        self.landscape = False

    # ── styles / page furniture ──────────────────────────────────────────
    def _style(self):
        st = self.doc.styles
        ok._set_font(st["Normal"], FONT, 10, "000000")
        st["Normal"].paragraph_format.line_spacing = 1.0
        st["Normal"].paragraph_format.space_after = Twips(100)
        for name, sz, before, after in (("Heading 1", 15, 360, 140), ("Heading 2", 12, 240, 100),
                                        ("Heading 3", 10.5, 180, 80)):
            s = st[name]
            ok._set_font(s, FONT, sz, "000000", bold=True)
            s.font.italic = False
            s.paragraph_format.space_before, s.paragraph_format.space_after = Twips(before), Twips(after)
            s.paragraph_format.keep_with_next = True
        for name in ("List Bullet", "List Number"):
            ok._set_font(st[name], FONT, 10, "000000")
            st[name].paragraph_format.space_after = Twips(60)

    def _header_footer(self, sec, width: int = TEXT_W):
        m = self.meta
        hp = sec.header.paragraphs[0]
        hp.paragraph_format.tab_stops.add_tab_stop(Twips(width), WD_TAB_ALIGNMENT.RIGHT)
        _runs(hp, f"{m['header_title']}\t{m['ref']} Rev {m['rev']}", 8, color=MUTED)
        ppr = hp._p.get_or_add_pPr()
        bdr = OxmlElement("w:pBdr")
        b = OxmlElement("w:bottom")
        for k, v in (("w:val", "single"), ("w:sz", "4"), ("w:space", "1"), ("w:color", BORDER)):
            b.set(qn(k), v)
        bdr.append(b)
        ppr.append(bdr)
        fp = sec.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for chunk in ("Page ", "PAGE", " of ", "NUMPAGES"):
            r = fp.add_run("" if chunk.isupper() else chunk)
            ok._set_font(r, FONT, 8, MUTED)
            if chunk.isupper():
                ok._field(r, chunk)

    def _new_section(self, landscape: bool):
        sec = self.doc.add_section(WD_SECTION.NEW_PAGE)
        w, h = Twips(12240), Twips(15840)
        sec.orientation = WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
        sec.page_width, sec.page_height = (h, w) if landscape else (w, h)
        sec.left_margin = sec.right_margin = Twips(1440)
        sec.top_margin, sec.bottom_margin = Twips(1000), Twips(800)
        sec.header_distance, sec.footer_distance = Twips(450), Twips(400)
        self.landscape = landscape
        # header right tab follows the text width of this orientation
        sec.header.is_linked_to_previous = False
        sec.footer.is_linked_to_previous = False
        for part in (sec.header, sec.footer):
            for p in part.paragraphs:
                p._p.getparent().remove(p._p)
            part._element.append(OxmlElement("w:p"))
        self._header_footer(sec, TEXT_W_LAND if landscape else TEXT_W)
        return sec

    @property
    def width(self) -> int:
        return TEXT_W_LAND if self.landscape else TEXT_W

    # ── cover ────────────────────────────────────────────────────────────
    def cover(self, control: Sequence[tuple[str, str]], approval: dict, revisions: Sequence[Sequence[str]]):
        """control: [(label, value)]; approval: {"parties": [...3], "names": [...3]};
        revisions: [(rev, date, status, description)]."""
        m = self.meta
        if m.get("client"):
            _spacing(_runs(self.doc.add_paragraph(), m["client"], 11, color=COVER_GREY), 600, 60)
        _spacing(_runs(self.doc.add_paragraph(), m["project"], 12, color=COVER_GREY), 0, 600)
        _spacing(_runs(self.doc.add_paragraph(), f"**{m['title']}**", 22), 0, 80)
        if m.get("subtitle"):
            _spacing(_runs(self.doc.add_paragraph(), m["subtitle"], 13, color=COVER_GREY), 0, 120)
        status = STATUS.get(m["status"], m["status"])
        _spacing(_runs(self.doc.add_paragraph(),
                       f"Deliverable {m['ref']}  |  Rev {m['rev']}  |  {status}", 12), 0, 600)
        self._grid([[f"**{k}**", v] for k, v in control], [2800, TEXT_W - 2800], size=10)
        self.label("Approval")
        parties, names = approval["parties"], approval.get("names", [""] * 3)
        rows = [["Party", *parties], ["Name", *names], ["Signature", "", "", ""], ["Date", "", "", ""]]
        self.grid_table(["", "Prepared by", "Checked by", "Accepted by"], rows,
                        [1560, 2600, 2600, 2600], first_col_bold=False, row_height=None)
        self.label("Revision history")
        self.grid_table(["Rev", "Date", "Status", "Description"], [list(r) for r in revisions],
                        [800, 2000, 1200, TEXT_W - 4000])

    def contents(self, levels: str = "1-2"):
        """Contents as a TOC field (Word refreshes on open; verify.py renders it)."""
        p = _runs(self.doc.add_paragraph(), "Contents", 15, bold=True)
        _spacing(p, 360, 140)
        ok._field(self.doc.add_paragraph().add_run(), f'TOC \\o "{levels}" \\h \\z \\u')
        s = self.doc.settings.element
        if s.find(qn("w:updateFields")) is None:
            uf = OxmlElement("w:updateFields"); uf.set(qn("w:val"), "true"); s.append(uf)
        ok.add_page_break(self.doc)

    # ── headings and text ────────────────────────────────────────────────
    def h1(self, title: str):
        self.h1_no += 1
        self.h2_no = self.table_no = 0
        return self.doc.add_heading(f"{self.h1_no}. {title}", 1)

    def h2(self, title: str):
        self.h2_no += 1
        n = self.appendix_letter if self.in_appendix else self.h1_no
        return self.doc.add_heading(f"{n}.{self.h2_no} {title}", 2)

    def h3(self, title: str):
        return self.doc.add_heading(title, 3)

    def para(self, text: str, size: float = 10, italic: bool = False):
        return _runs(self.doc.add_paragraph(), text, size, italic=italic)

    def label(self, text: str):
        p = _runs(self.doc.add_paragraph(), f"**{text}**", 10)
        _spacing(p, 200, 80)
        p.paragraph_format.keep_with_next = True
        return p

    def bullets(self, items: Sequence[str]):
        for it in items:
            _runs(self.doc.add_paragraph(style="List Bullet"), it, 10)

    def steps(self, items: Sequence[str]):
        """Numbered steps restarting at 1."""
        ps = ok.add_numbered_list(self.doc, ["" for _ in items])
        for p, it in zip(ps, items):
            _runs(p, it, 10)
        return ps

    def hold_points(self, points: Sequence[tuple[str, str]], label: str = "Hold points in this procedure"):
        """Labelled Ref | Hold point table. Each text says what may not start until what."""
        for code, _ in points:
            if not re.fullmatch(r"HP-\d+", code) or code in self.hp_codes:
                raise ValueError(f"hold point {code!r}: use HP-n, once")
            self.hp_codes.append(code)
        self.label(label)
        t = self.grid_table(["Ref", "Hold point"], [[f"**{c}**", txt] for c, txt in points],
                            [900, self.width - 900])
        _spacing(self.doc.add_paragraph(), 0, 60)
        return t

    # ── tables ───────────────────────────────────────────────────────────
    def _caption(self, title: str) -> str:
        self.table_no += 1
        n = self.appendix_letter if self.in_appendix else self.h1_no
        text = f"Table {n}.{self.table_no} - {title}"
        p = _runs(self.doc.add_paragraph(), text, 9, italic=True, color=MUTED)
        _spacing(p, 60, 200)
        return text

    def table(self, header: Sequence[str], rows: Sequence, caption: str | None,
              widths: Sequence[int] | None = None, size: float = 9, note: str | None = None):
        """Body table: grey bold header (repeats), plain rows. A row given as
        ("group", "Part A - ...") becomes a full-width F2F2F2 bold group row.
        caption is required for body tables (None only inside forms/appendix lists)."""
        widths = list(widths or [self.width // len(header)] * len(header))
        t = self.grid_table(header, rows, widths, size=size)
        if caption:
            self._caption(caption + (f". {note}" if note else ""))
        else:
            _spacing(self.doc.add_paragraph(), 0, 60)
        return t

    def grid_table(self, header, rows, widths, size: float = 9, first_col_bold: bool = False,
                   label_col_shade: bool = False, row_height: int | None = None):
        t = self._new_table(len(widths), widths)
        if header:
            self._row(t, [f"**{h}**" if h else "" for h in header], widths, size, fill=GREY_HDR,
                      header=True)
        for r in rows:
            if isinstance(r, tuple) and len(r) == 2 and r[0] == "group":
                self._group_row(t, r[1], widths, size)
                continue
            cells = [f"**{c}**" if (first_col_bold and i == 0 and c) else c for i, c in enumerate(r)]
            fills = [GREY_GRP if (label_col_shade and i == 0) else None for i in range(len(widths))]
            self._row(t, cells, widths, size, fills=fills, height=row_height)
        return t

    def _grid(self, rows, widths, size: float = 9):
        t = self._new_table(len(widths), widths)
        for r in rows:
            self._row(t, r, widths, size)
        _spacing(self.doc.add_paragraph(), 0, 60)
        return t

    def _new_table(self, ncols: int, widths):
        t = self.doc.add_table(rows=0, cols=ncols)
        t.alignment = WD_TABLE_ALIGNMENT.LEFT
        t.autofit = False
        tblpr = t._tbl.tblPr
        tw = OxmlElement("w:tblW"); tw.set(qn("w:type"), "dxa"); tw.set(qn("w:w"), str(sum(widths)))
        tblpr.append(tw)
        lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblpr.append(lay)
        grid = t._tbl.tblGrid
        for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
            gc.set(qn("w:w"), str(w))
        return t

    def _cell(self, cell, text: str, width: int, size: float, fill: str | None):
        cell.width = Twips(width)
        tcpr = cell._tc.get_or_add_tcPr()
        bd = OxmlElement("w:tcBorders")
        for edge in ("top", "left", "bottom", "right"):
            e = OxmlElement(f"w:{edge}")
            for k, v in (("w:val", "single"), ("w:sz", "4"), ("w:color", BORDER)):
                e.set(qn(k), v)
            bd.append(e)
        tcpr.append(bd)
        if fill:
            ok.shade_cell(cell, fill)
        mar = OxmlElement("w:tcMar")
        for side, v in (("top", 35), ("left", 80), ("bottom", 35), ("right", 80)):
            e = OxmlElement(f"w:{side}"); e.set(qn("w:w"), str(v)); e.set(qn("w:type"), "dxa"); mar.append(e)
        tcpr.append(mar)
        p = cell.paragraphs[0]
        _spacing(p, 0, 20)
        _runs(p, "" if text is None else str(text), size)

    def _row(self, t, cells, widths, size, fill=None, fills=None, header=False, height=None):
        row = t.add_row()
        trpr = row._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit"); trpr.append(cs)
        if header:
            th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trpr.append(th)
        if height:
            h = OxmlElement("w:trHeight"); h.set(qn("w:val"), str(height)); trpr.append(h)
        for i, (c, w) in enumerate(zip(row.cells, widths)):
            text = cells[i] if i < len(cells) else ""
            self._cell(c, text, w, size, fill or (fills[i] if fills else None))
        return row

    def _group_row(self, t, text, widths, size):
        row = self._row(t, [f"**{text}**"], widths, size, fills=[GREY_GRP] * len(widths))
        merged = row.cells[0].merge(row.cells[-1])
        for p in merged.paragraphs[1:]:
            p._p.getparent().remove(p._p)
        return row

    # ── appendices and forms ─────────────────────────────────────────────
    def appendix(self, title: str, landscape: bool = False, new_section: bool = True):
        self.in_appendix = True
        self.appendix_no += 1
        self.appendix_letter = chr(64 + self.appendix_no)
        self.h2_no = self.table_no = 0
        if new_section:
            self._new_section(landscape)
        return self.doc.add_heading(f"Appendix {self.appendix_letter} - {title}", 1)

    def form_index(self, forms: Sequence[dict]):
        """Register the field forms and draw their index. Each spec: code (F-nn), title,
        purpose, feeds, orientation (Portrait|Landscape), completed, optional group and rev.
        This list is the single source for the index and for every form() section."""
        rows, last = [], None
        for f in forms:
            missing = [k for k in FORM_KEYS if not f.get(k)]
            if missing:
                raise ValueError(f"form spec {f.get('code', '?')}: missing {', '.join(missing)}")
            if not re.fullmatch(r"F-\d{2}", f["code"]):
                raise ValueError(f"form code {f['code']!r}: use F-nn")
            if f["code"] in self.form_specs:
                raise ValueError(f"duplicate form {f['code']}")
            if f["orientation"] not in ("Portrait", "Landscape"):
                raise ValueError(f"form {f['code']}: orientation must be Portrait or Landscape")
            self.form_specs[f["code"]] = dict(f)
            if f.get("group") and f["group"] != last:
                rows.append(("group", f["group"])); last = f["group"]
            rows.append([f["code"], f["title"], f["orientation"], f["completed"]])
        w = self.width
        return self.table(["Form", "Title", "Orientation", "Completed"], rows, None,
                          [900, w - 4700, 1400, 2400])

    def form(self, code: str) -> "Form":
        """Start form `code` from its form_index spec, in its own section."""
        spec = self.form_specs.get(code)
        if spec is None:
            raise ValueError(f"form {code} is not in the form index")
        if code in self.built_forms:
            raise ValueError(f"form {code} built twice")
        self.built_forms.append(code)
        self._new_section(spec["orientation"] == "Landscape")
        self.doc.add_heading(f"{code} - {spec['title']}", 2)
        p = _runs(self.doc.add_paragraph(),
                  f"{spec['purpose']} **Feeds:** {spec['feeds']}. **Form rev:** {spec.get('rev', 'A')}", 9)
        _spacing(p, 0, 120)
        return Form(self, code)

    def appendix_form(self, title: str) -> "Form":
        """A lightweight form inside the current appendix, numbered like a sub-section
        (G.1 Transmittal), with no section break or Feeds line - the execution-plan style."""
        if not self.in_appendix:
            raise ValueError("appendix_form() belongs inside an appendix")
        h = self.h2(title)
        return Form(self, h.text.split()[0])

    def save(self, path: str, author: str = ""):
        unbuilt = [c for c in self.form_specs if c not in self.built_forms]
        if unbuilt:
            raise ValueError(f"forms in the index but never built: {', '.join(unbuilt)}")
        ok.set_core_props(self.doc, f"{self.meta['ref']} {self.meta['title']}", author=author or "")
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(path)
        return path


class Form:
    """Body of one form. Call grid(), then fields()/entries()/log()/checks(), then signoff()."""

    def __init__(self, pd: ProcDoc, code: str):
        self.pd, self.code = pd, code

    @property
    def w(self) -> int:
        return self.pd.width

    def _table(self, *a, **kw):
        t = self.pd.grid_table(*a, **kw)
        _spacing(self.pd.doc.add_paragraph(), 0, 60)
        return t

    def grid(self, labels: Sequence[str]):
        """Header block: labels in pairs, two pairs per row, values blank."""
        lw = 1700
        vw = (self.w - 2 * lw) // 2
        rows = []
        for i in range(0, len(labels), 2):
            pair = list(labels[i:i + 2]) + [""] * (2 - len(labels[i:i + 2]))
            rows.append([f"**{pair[0]}**", "", f"**{pair[1]}**" if pair[1] else "", ""])
        return self.pd._grid(rows, [lw, vw, lw, self.w - 2 * lw - vw], size=8)

    def fields(self, rows: Sequence, src: bool = True, value_head: str = "Value"):
        """Field / Value [/ Src] table. rows: "label", ("label", "preset value"),
        or ("group", "Part A - ...")."""
        head = ["Field", value_head] + (["Src"] if src else [])
        widths = [int(self.w * 0.395), 0] + ([800] if src else [])
        widths[1] = self.w - widths[0] - (800 if src else 0)
        out = []
        for r in rows:
            if isinstance(r, tuple) and r[0] == "group":
                out.append(r)
            elif isinstance(r, tuple):
                out.append([r[0], r[1]] + ([""] if src else []))
            else:
                out.append([r, ""] + ([""] if src else []))
        return self._table(head, out, widths, size=8, label_col_shade=True)

    def entries(self, rows: Sequence[tuple[str, str]], label_w: int = 3200):
        """Two-column label / value table with no header and bold labels; values may be
        preset guidance ("TR-<sender>-<nnn>", "Rev __ | IFR / ...")."""
        return self._table(None, [[f"**{k}**", v] for k, v in rows], [label_w, self.w - label_w], size=9)

    def log(self, header: Sequence[str], n_rows: int, widths: Sequence[int] | None = None,
            preset: Sequence[Sequence[str]] | None = None):
        """Multi-row register/log: header row, preset rows (e.g. a checklist), then blank rows."""
        widths = list(widths or [self.w // len(header)] * len(header))
        if sum(widths) != self.w:
            widths[-1] += self.w - sum(widths)
        rows = [list(r) if not (isinstance(r, tuple) and r[0] == "group") else r for r in (preset or [])]
        rows += [[""] * len(header) for _ in range(n_rows)]
        return self._table(header, rows, widths, size=8, row_height=None if preset else 340)

    def checks(self, rows: Sequence, choices: Sequence[str] = ("Done", "NA"), third: str = "Count / ref"):
        """Checklist: Check | Status (tick boxes) | third column."""
        body = []
        for r in rows:
            body.append(r if isinstance(r, tuple) else [r, opts(choices), ""])
        w0 = int(self.w * 0.55)
        return self._table(["Check", "Status", third], body,
                                  [w0, int(self.w * 0.25), self.w - w0 - int(self.w * 0.25)], size=8)

    def note(self, text: str):
        return self.pd.label(text)

    def continued(self, labels: Sequence[str]):
        """Continuation sheet header for a long form."""
        _spacing(_runs(self.pd.doc.add_paragraph(), f"**{self.code} (continued)**", 10), 200, 80)
        return self.grid(labels)

    def signoff(self, roles: Sequence[str]):
        w = self.w
        return self._table(["Role", "Name", "Signature", "Date"], [[r, "", "", ""] for r in roles],
                                  [int(w * 0.29), int(w * 0.29), int(w * 0.25), w - int(w * 0.29) * 2 - int(w * 0.25)],
                                  size=8, row_height=460)
