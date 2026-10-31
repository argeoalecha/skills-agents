"""officekit — thin, opinionated helpers for building .docx (python-docx) and
.xlsx (openpyxl) deliverables. Import it from the build script:

    import sys; sys.path.insert(0, "<skill_dir>/scripts")
    from officekit import *

Everything returns plain python-docx / openpyxl objects, so drop to the raw
API whenever a helper doesn't cover a case.
"""
from __future__ import annotations

import datetime as _dt
from copy import deepcopy
from typing import Iterable, Sequence

# ─────────────────────────────── Themes ────────────────────────────────
# Hex without '#'. Fonts default to ones every Office install has; set
# brand_fonts=True only when the recipient has Playfair Display / Inter.
THEMES = {
    "hayah": dict(
        primary="0A3D3A",   # deep teal — headings, header fills
        secondary="1E6E66", # ocean teal — H2/H3, chart series 1
        accent="FF6B47",    # vibrant coral — highlights, negatives, CTAs
        success="25A497",   # aqua green — positive deltas, series 2
        tint="E8F4F1",      # pearl — zebra rows, callout fill
        tint2="F3FFF9",     # fresh mint — page/section fill
        muted="7A9B96",     # sage — captions, footers, borders
        text="2C3E3A",      # charcoal — body text
        heading_font="Georgia", body_font="Calibri", mono_font="Consolas",
        brand_heading_font="Playfair Display", brand_body_font="Inter",
        brand_mono_font="JetBrains Mono",
        series=["1E6E66", "FF6B47", "25A497", "0A3D3A", "A1E4DB", "FFB5A0"],
    ),
    "neutral": dict(
        primary="1F2937", secondary="374151", accent="B91C1C", success="047857",
        tint="F3F4F6", tint2="F9FAFB", muted="6B7280", text="111827",
        heading_font="Calibri", body_font="Calibri", mono_font="Consolas",
        brand_heading_font="Calibri", brand_body_font="Calibri", brand_mono_font="Consolas",
        series=["1F4E79", "C55A11", "548235", "7F6000", "7030A0", "2F5597"],
    ),
}


def get_theme(name: str = "hayah", brand_fonts: bool = False) -> dict:
    t = deepcopy(THEMES[name])
    if brand_fonts:
        t["heading_font"] = t["brand_heading_font"]
        t["body_font"] = t["brand_body_font"]
        t["mono_font"] = t["brand_mono_font"]
    return t


# Paper sizes in inches (w, h). PH government/legal uses "long" 8.5x13.
PAPER = {"A4": (8.27, 11.69), "Letter": (8.5, 11.0), "Legal": (8.5, 14.0),
         "Long": (8.5, 13.0)}

# PH number formats (₱, negatives in parentheses, zero as dash)
FMT = {
    "php": '"₱"#,##0.00;("₱"#,##0.00);"-"',
    "php0": '"₱"#,##0;("₱"#,##0);"-"',
    "usd": '"$"#,##0.00;("$"#,##0.00);"-"',
    "int": '#,##0;(#,##0);"-"',
    "dec2": '#,##0.00;(#,##0.00);"-"',
    "pct": '0.0%;(0.0%);"-"',
    "date": "yyyy-mm-dd",
    "date_ph": "dd-mmm-yyyy",
    "datetime": "yyyy-mm-dd hh:mm",
    "kwh": '#,##0.0" kWh"',
    "kw": '#,##0.00" kW"',
}


# ═════════════════════════════════ DOCX ═════════════════════════════════
def _docx():
    import docx  # noqa: F401  (lazy so xlsx-only builds don't need it)
    from docx import Document
    from docx.enum.section import WD_ORIENT
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt, RGBColor
    return dict(Document=Document, WD_ORIENT=WD_ORIENT, WD_TABLE_ALIGNMENT=WD_TABLE_ALIGNMENT,
                WD_ALIGN_PARAGRAPH=WD_ALIGN_PARAGRAPH, WD_BREAK=WD_BREAK,
                OxmlElement=OxmlElement, qn=qn, Inches=Inches, Pt=Pt, RGBColor=RGBColor)


def _set_font(style_or_run, name: str, size: float | None = None, color: str | None = None,
              bold: bool | None = None):
    d = _docx()
    f = style_or_run.font
    f.name = name
    # python-docx only writes w:ascii/w:hAnsi; set eastAsia + cs too or Word
    # silently substitutes on some locales.
    el = style_or_run.element if hasattr(style_or_run, "element") else style_or_run._element
    rpr = el.get_or_add_rPr()
    rfonts = rpr.find(d["qn"]("w:rFonts"))
    if rfonts is None:
        rfonts = d["OxmlElement"]("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(d["qn"](attr), name)
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        rfonts.attrib.pop(d["qn"](attr), None)
    if size is not None:
        f.size = d["Pt"](size)
    if color is not None:
        f.color.rgb = d["RGBColor"].from_string(color)
    if bold is not None:
        f.bold = bold


def new_document(theme: dict | None = None, paper: str = "A4", landscape: bool = False,
                 margins_in: float = 1.0, body_size: float = 10.5):
    """Blank document with themed Normal/Heading/List/Caption styles."""
    d = _docx()
    t = theme or get_theme()
    doc = d["Document"]()
    sec = doc.sections[0]
    w, h = PAPER[paper]
    if landscape:  # python-docx does NOT swap for you
        sec.orientation = d["WD_ORIENT"].LANDSCAPE
        w, h = h, w
    sec.page_width, sec.page_height = d["Inches"](w), d["Inches"](h)
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, side, d["Inches"](margins_in))

    st = doc.styles
    _set_font(st["Normal"], t["body_font"], body_size, t["text"])
    st["Normal"].paragraph_format.space_after = d["Pt"](6)
    st["Normal"].paragraph_format.line_spacing = 1.15
    sizes = {"Title": 26, "Heading 1": 18, "Heading 2": 14, "Heading 3": 12}
    for name, sz in sizes.items():
        s = st[name]
        color = t["primary"] if name in ("Title", "Heading 1") else t["secondary"]
        _set_font(s, t["heading_font"], sz, color, bold=name != "Title")
        s.font.italic = False
        s.paragraph_format.space_before = d["Pt"](14 if name == "Heading 1" else 10)
        s.paragraph_format.space_after = d["Pt"](4)
        s.paragraph_format.keep_with_next = True
    tppr = st["Title"].element.get_or_add_pPr()
    for b in tppr.findall(d["qn"]("w:pBdr")):
        tppr.remove(b)
    for name in ("List Bullet", "List Number", "Caption"):
        _set_font(st[name], t["body_font"], body_size if name != "Caption" else 9,
                  t["muted"] if name == "Caption" else t["text"])
    doc._officekit_theme = t  # type: ignore[attr-defined]
    return doc


def _theme(doc) -> dict:
    return getattr(doc, "_officekit_theme", get_theme())


def add_title(doc, title: str, subtitle: str | None = None, meta: str | None = None):
    d = _docx()
    t = _theme(doc)
    doc.add_paragraph(title, style="Title")
    if subtitle:
        p = doc.add_paragraph()
        r = p.add_run(subtitle)
        _set_font(r, t["body_font"], 13, t["secondary"])
    if meta:
        p = doc.add_paragraph()
        r = p.add_run(meta)
        _set_font(r, t["body_font"], 9, t["muted"])
    add_rule(doc, color=t["accent"], size_eighths=12)
    return doc


def add_rule(doc, color: str | None = None, size_eighths: int = 6):
    """Horizontal rule as a paragraph bottom border (never a 1-row table)."""
    d = _docx()
    p = doc.add_paragraph()
    ppr = p._p.get_or_add_pPr()
    bdr = d["OxmlElement"]("w:pBdr")
    bottom = d["OxmlElement"]("w:bottom")
    for k, v in {"w:val": "single", "w:sz": str(size_eighths), "w:space": "1",
                 "w:color": color or _theme(doc)["muted"]}.items():
        bottom.set(d["qn"](k), v)
    bdr.append(bottom)
    ppr.append(bdr)
    p.paragraph_format.space_after = d["Pt"](8)
    return p


def add_rich(doc, parts: Sequence[str | tuple[str, dict]], style: str | None = None):
    """Paragraph from runs: ["plain ", ("bold", {"bold": True}), ("x", {"color": "FF6B47"})].
    Run opts: bold, italic, underline, color, size, font, mono, highlight."""
    d = _docx()
    t = _theme(doc)
    p = doc.add_paragraph(style=style)
    for part in parts:
        text, o = (part, {}) if isinstance(part, str) else part
        r = p.add_run(text)
        r.bold, r.italic, r.underline = o.get("bold"), o.get("italic"), o.get("underline")
        if o.get("mono"):
            _set_font(r, t["mono_font"], o.get("size", 9.5))
        elif o.get("font"):
            _set_font(r, o["font"])
        if o.get("size") and not o.get("mono"):
            r.font.size = d["Pt"](o["size"])
        if o.get("color"):
            r.font.color.rgb = d["RGBColor"].from_string(o["color"])
    return p


def add_bullets(doc, items: Iterable[str | Sequence], numbered: bool = False):
    """Bullets (or numbers). Items may be str or a parts list for add_rich.
    NOTE: 'List Number' continues numbering across lists; call restart=True
    via add_numbered_list when you need 1. again."""
    style = "List Number" if numbered else "List Bullet"
    out = []
    for it in items:
        out.append(doc.add_paragraph(it, style=style) if isinstance(it, str)
                   else add_rich(doc, it, style=style))
    return out


def add_numbered_list(doc, items: Iterable[str]):
    """Numbered list that restarts at 1 (creates a fresh w:num instance)."""
    d = _docx()
    qn, OxE = d["qn"], d["OxmlElement"]
    paras = add_bullets(doc, items, numbered=True)
    if not paras:
        return paras
    numbering = doc.part.numbering_part.element
    style_numid = doc.styles["List Number"].element.pPr.numPr.numId.val
    abstract_id = numbering.num_having_numId(style_numid).abstractNumId.val
    new_id = max(int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num"))) + 1
    num = OxE("w:num"); num.set(qn("w:numId"), str(new_id))
    an = OxE("w:abstractNumId"); an.set(qn("w:val"), str(abstract_id)); num.append(an)
    lo = OxE("w:lvlOverride"); lo.set(qn("w:ilvl"), "0")
    so = OxE("w:startOverride"); so.set(qn("w:val"), "1"); lo.append(so); num.append(lo)
    numbering.append(num)
    for p in paras:
        numpr = p._p.get_or_add_pPr().get_or_add_numPr()
        numpr.get_or_add_ilvl().val = 0
        numpr.get_or_add_numId().val = new_id
    return paras


def shade_cell(cell, fill_hex: str):
    d = _docx()
    tcpr = cell._tc.get_or_add_tcPr()
    for old in tcpr.findall(d["qn"]("w:shd")):
        tcpr.remove(old)
    shd = d["OxmlElement"]("w:shd")
    shd.set(d["qn"]("w:val"), "clear")  # 'clear' + fill; 'solid' renders black
    shd.set(d["qn"]("w:color"), "auto")
    shd.set(d["qn"]("w:fill"), fill_hex)
    tcpr.append(shd)


def _cell_margins(table, top=50, bottom=50, left=90, right=90):
    d = _docx()
    tblpr = table._tbl.tblPr
    mar = d["OxmlElement"]("w:tblCellMar")
    for side, v in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        e = d["OxmlElement"](f"w:{side}")
        e.set(d["qn"]("w:w"), str(v)); e.set(d["qn"]("w:type"), "dxa")
        mar.append(e)
    tblpr.append(mar)


def add_table(doc, header: Sequence[str], rows: Sequence[Sequence], col_widths_in: Sequence[float] | None = None,
              align: Sequence[str] | None = None, zebra: bool = True, font_size: float = 9.5,
              total_row: bool = False, caption: str | None = None):
    """Themed table. align: per column 'l'|'c'|'r'. Widths default to equal split
    of the text width. Header row repeats across pages."""
    d = _docx()
    t = _theme(doc)
    sec = doc.sections[-1]
    text_w = (sec.page_width - sec.left_margin - sec.right_margin) / 914400
    n = len(header)
    widths = list(col_widths_in or [text_w / n] * n)
    align = list(align or ["l"] * n)
    amap = {"l": d["WD_ALIGN_PARAGRAPH"].LEFT, "c": d["WD_ALIGN_PARAGRAPH"].CENTER,
            "r": d["WD_ALIGN_PARAGRAPH"].RIGHT}

    tbl = doc.add_table(rows=1 + len(rows), cols=n)
    tbl.style = doc.styles["Table Grid"]
    tbl.alignment = d["WD_TABLE_ALIGNMENT"].CENTER
    tbl.autofit = False
    _cell_margins(tbl)
    # fixed layout so Word/LibreOffice/Google Docs honour the widths
    lay = d["OxmlElement"]("w:tblLayout"); lay.set(d["qn"]("w:type"), "fixed")
    tbl._tbl.tblPr.append(lay)

    def _fill(cell, value, bold=False, color=None, ci=0):
        cell.width = d["Inches"](widths[ci])  # width on EVERY cell, not column
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = d["Pt"](0)
        p.alignment = amap[align[ci]]
        r = p.add_run("" if value is None else str(value))
        r.font.size = d["Pt"](font_size)
        r.bold = bold
        if color:
            r.font.color.rgb = d["RGBColor"].from_string(color)

    hdr = tbl.rows[0]
    trpr = hdr._tr.get_or_add_trPr()
    th = d["OxmlElement"]("w:tblHeader"); th.set(d["qn"]("w:val"), "true"); trpr.append(th)
    for ci, h in enumerate(header):
        _fill(hdr.cells[ci], h, bold=True, color="FFFFFF", ci=ci)
        shade_cell(hdr.cells[ci], t["primary"])
    for ri, row in enumerate(rows, start=1):
        last = total_row and ri == len(rows)
        for ci, v in enumerate(row):
            _fill(tbl.rows[ri].cells[ci], v, bold=last, ci=ci)
            if last:
                shade_cell(tbl.rows[ri].cells[ci], t["tint"])
            elif zebra and ri % 2 == 0:
                shade_cell(tbl.rows[ri].cells[ci], t["tint2"])
    # thin themed borders
    borders = d["OxmlElement"]("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = d["OxmlElement"](f"w:{edge}")
        e.set(d["qn"]("w:val"), "single"); e.set(d["qn"]("w:sz"), "4")
        e.set(d["qn"]("w:color"), t["muted"] if edge in ("top", "bottom") else "D5DFDC")
        borders.append(e)
    tbl._tbl.tblPr.append(borders)
    if caption:
        doc.add_paragraph(caption, style="Caption")
    else:
        doc.add_paragraph().paragraph_format.space_after = d["Pt"](2)
    return tbl


def add_callout(doc, text: str, label: str | None = "Note", color: str | None = None):
    """Shaded single-cell box with a coloured left bar — for key findings."""
    d = _docx()
    t = _theme(doc)
    sec = doc.sections[-1]
    text_w = (sec.page_width - sec.left_margin - sec.right_margin) / 914400
    tbl = doc.add_table(rows=1, cols=1)
    tbl.autofit = False
    c = tbl.cell(0, 0)
    c.width = d["Inches"](text_w)
    shade_cell(c, t["tint"])
    tcpr = c._tc.get_or_add_tcPr()
    b = d["OxmlElement"]("w:tcBorders")
    for edge in ("top", "bottom", "right"):
        e = d["OxmlElement"](f"w:{edge}"); e.set(d["qn"]("w:val"), "nil"); b.append(e)
    left = d["OxmlElement"]("w:left")
    for k, v in {"w:val": "single", "w:sz": "24", "w:color": color or t["accent"]}.items():
        left.set(d["qn"](k), v)
    b.append(left); tcpr.append(b)
    p = c.paragraphs[0]
    if label:
        r = p.add_run(label + "  "); r.bold = True
        r.font.color.rgb = d["RGBColor"].from_string(color or t["accent"])
    p.add_run(text)
    doc.add_paragraph().paragraph_format.space_after = d["Pt"](2)
    return tbl


def add_image(doc, path: str, width_in: float | None = None, caption: str | None = None):
    d = _docx()
    sec = doc.sections[-1]
    text_w = (sec.page_width - sec.left_margin - sec.right_margin) / 914400
    doc.add_picture(path, width=d["Inches"](min(width_in or text_w, text_w)))
    doc.paragraphs[-1].alignment = d["WD_ALIGN_PARAGRAPH"].CENTER
    if caption:
        doc.add_paragraph(caption, style="Caption").alignment = d["WD_ALIGN_PARAGRAPH"].CENTER


def _field(run, instr: str):
    d = _docx()
    OxE, qn = d["OxmlElement"], d["qn"]
    for kind, text in (("begin", None), (None, instr), ("separate", None), (None, "1"), ("end", None)):
        if kind:
            fc = OxE("w:fldChar"); fc.set(qn("w:fldCharType"), kind); run._r.append(fc)
        elif text == instr:
            it = OxE("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = f" {instr} "
            run._r.append(it)
        else:
            tt = OxE("w:t"); tt.text = text; run._r.append(tt)


def add_header_footer(doc, header_left: str = "", header_right: str = "",
                      footer_left: str = "", page_numbers: bool = True):
    """Tab-aligned header/footer with 'Page X of Y' on the right."""
    d = _docx()
    t = _theme(doc)
    from docx.enum.text import WD_TAB_ALIGNMENT
    sec0 = doc.sections[0]
    right0 = sec0.page_width - sec0.left_margin - sec0.right_margin
    for sname in ("Header", "Footer"):
        sty = doc.styles[sname]
        _set_font(sty, t["body_font"], 8, t["muted"])
        ppr = sty.element.get_or_add_pPr()
        for tabs in ppr.findall(d["qn"]("w:tabs")):  # default 3.25"/6.5" (Letter) tabs
            ppr.remove(tabs)
        sty.paragraph_format.tab_stops.add_tab_stop(int(right0 / 2), WD_TAB_ALIGNMENT.CENTER)
        sty.paragraph_format.tab_stops.add_tab_stop(right0, WD_TAB_ALIGNMENT.RIGHT)
    for sec in doc.sections:
        right = sec.page_width - sec.left_margin - sec.right_margin
        for part, left_txt, right_txt in ((sec.header, header_left, header_right),
                                           (sec.footer, footer_left, None)):
            p = part.paragraphs[0]
            p.style = doc.styles["Header" if part is sec.header else "Footer"]
            p.add_run(left_txt)
            p.add_run("\t\t")  # skip centre stop → right-aligned
            if right_txt is not None:
                p.add_run(right_txt)
            elif page_numbers:
                for chunk in ("Page ", "PAGE", " of ", "NUMPAGES"):
                    r = p.add_run("" if chunk.isupper() else chunk)
                    if chunk.isupper():
                        _field(r, chunk)


def add_toc(doc, levels: str = "1-3", title: str = "Contents"):
    """TOC field. Word fills it on open (we set updateFields); LibreOffice
    fills it during PDF export via verify.py. Headings must use 'Heading N'."""
    d = _docx()
    t = _theme(doc)
    hp = doc.add_paragraph()  # not a Heading style, so it doesn't list itself
    hp.paragraph_format.space_before, hp.paragraph_format.space_after = d["Pt"](14), d["Pt"](6)
    _set_font(hp.add_run(title), t["heading_font"], 18, t["primary"], bold=True)
    _field(doc.add_paragraph().add_run(), f'TOC \\o "{levels}" \\h \\z \\u')
    settings = doc.settings.element
    uf = d["OxmlElement"]("w:updateFields"); uf.set(d["qn"]("w:val"), "true")
    settings.append(uf)
    add_page_break(doc)


def add_page_break(doc):
    d = _docx()
    doc.add_paragraph().add_run().add_break(d["WD_BREAK"].PAGE)


def add_hyperlink(paragraph, text: str, url: str, color: str = "1E6E66"):
    d = _docx()
    OxE, qn = d["OxmlElement"], d["qn"]
    rid = paragraph.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                                   is_external=True)
    h = OxE("w:hyperlink"); h.set(qn("r:id"), rid)
    r = OxE("w:r"); rpr = OxE("w:rPr")
    c = OxE("w:color"); c.set(qn("w:val"), color); rpr.append(c)
    u = OxE("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
    r.append(rpr); tt = OxE("w:t"); tt.text = text; r.append(tt); h.append(r)
    paragraph._p.append(h)
    return h


def set_core_props(doc_or_wb, title: str, author: str = "Hayah-AI", subject: str = "",
                   keywords: str = ""):
    """Works for python-docx Document and openpyxl Workbook."""
    props = doc_or_wb.core_properties if hasattr(doc_or_wb, "core_properties") else doc_or_wb.properties
    props.title = title
    if hasattr(props, "author"):
        props.author = author
    else:
        props.creator = author
    props.subject = subject
    props.keywords = keywords
    if hasattr(props, "last_modified_by"):
        props.last_modified_by = author
    else:
        props.lastModifiedBy = author


# ═════════════════════════════════ XLSX ═════════════════════════════════
def _xl():
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.table import Table, TableStyleInfo
    return dict(Workbook=Workbook, Alignment=Alignment, Border=Border, Font=Font,
                PatternFill=PatternFill, Side=Side, gcl=get_column_letter, Table=Table,
                TableStyleInfo=TableStyleInfo)


def xl_styles(theme: dict | None = None) -> dict:
    """Named style kit. Inputs blue, formulas black, cross-sheet links green."""
    x = _xl()
    t = theme or get_theme()
    thin = x["Side"](style="thin", color="D5DFDC")
    font = t["body_font"]
    return dict(
        title=x["Font"](name=t["heading_font"], size=16, bold=True, color=t["primary"]),
        subtitle=x["Font"](name=font, size=10, italic=True, color=t["muted"]),
        hdr_font=x["Font"](name=font, size=10, bold=True, color="FFFFFF"),
        hdr_fill=x["PatternFill"]("solid", fgColor=t["primary"]),
        body=x["Font"](name=font, size=10, color=t["text"]),
        input=x["Font"](name=font, size=10, color="0000FF"),
        link=x["Font"](name=font, size=10, color="008000"),
        input_fill=x["PatternFill"]("solid", fgColor="FFF2CC"),
        total_font=x["Font"](name=font, size=10, bold=True, color=t["primary"]),
        total_fill=x["PatternFill"]("solid", fgColor=t["tint"]),
        zebra=x["PatternFill"]("solid", fgColor=t["tint2"]),
        border=x["Border"](top=thin, bottom=thin, left=thin, right=thin),
        total_border=x["Border"](top=x["Side"](style="thin", color=t["primary"]),
                                 bottom=x["Side"](style="double", color=t["primary"])),
        wrap=x["Alignment"](wrap_text=True, vertical="top"),
        center=x["Alignment"](horizontal="center", vertical="center", wrap_text=True),
    )


def new_workbook(theme: dict | None = None, first_sheet: str = "Summary"):
    x = _xl()
    wb = x["Workbook"]()
    wb.active.title = first_sheet
    wb._officekit_theme = theme or get_theme()  # type: ignore[attr-defined]
    return wb


def _wb_theme(ws) -> dict:
    return getattr(ws.parent, "_officekit_theme", get_theme())


def _clean(v):
    """Coerce values openpyxl rejects: tz-aware datetimes, numpy/pandas scalars, NaN."""
    try:
        import numpy as np
        if isinstance(v, np.generic):
            v = v.item()
    except ImportError:
        pass
    try:
        import pandas as pd
        if v is pd.NaT:
            return None
        if isinstance(v, pd.Timestamp):
            v = v.to_pydatetime()
    except ImportError:
        pass
    if isinstance(v, float) and v != v:  # NaN
        return None
    if isinstance(v, _dt.datetime) and v.tzinfo is not None:
        return v.replace(tzinfo=None)  # caller must convert to local (PHT) first
    return v


def write_title(ws, title: str, subtitle: str | None = None, row: int = 1):
    s = xl_styles(_wb_theme(ws))
    ws.cell(row=row, column=1, value=title).font = s["title"]
    if subtitle:
        ws.cell(row=row + 1, column=1, value=subtitle).font = s["subtitle"]
    return row + (3 if subtitle else 2)


def write_table(ws, header: Sequence[str], rows: Iterable[Sequence], start_row: int = 1,
                start_col: int = 1, formats: dict | None = None, widths: dict | None = None,
                table_name: str | None = None, totals: dict | None = None,
                freeze: bool = True, zebra: bool = True) -> dict:
    """Styled block. formats/widths keyed by header text (FMT key or raw format).
    table_name → real Excel Table (filter buttons, structured refs).
    totals: {header: "SUM"|"AVERAGE"|"COUNT"|"=custom formula"} adds a formula total row.
    Returns dict with first/last data row and column letters by header."""
    x = _xl()
    s = xl_styles(_wb_theme(ws))
    formats, widths = formats or {}, widths or {}
    cols = {h: x["gcl"](start_col + i) for i, h in enumerate(header)}
    for i, h in enumerate(header):
        c = ws.cell(row=start_row, column=start_col + i, value=h)
        c.font, c.fill, c.alignment, c.border = s["hdr_font"], s["hdr_fill"], s["center"], s["border"]
    r = start_row
    for r_i, row in enumerate(rows, start=1):
        r = start_row + r_i
        for i, v in enumerate(row):
            c = ws.cell(row=r, column=start_col + i, value=_clean(v))
            c.font, c.border = s["body"], s["border"]
            f = formats.get(header[i])
            if f:
                c.number_format = FMT.get(f, f)
            if zebra and not table_name and r_i % 2 == 0:
                c.fill = s["zebra"]
    first, last = start_row + 1, r
    if table_name and last >= first:
        ref = f"{cols[header[0]]}{start_row}:{cols[header[-1]]}{last}"
        tb = x["Table"](displayName=table_name, ref=ref)
        tb.tableStyleInfo = x["TableStyleInfo"](name="TableStyleLight1", showRowStripes=zebra)
        ws.add_table(tb)
    elif last >= first:
        ws.auto_filter.ref = f"{cols[header[0]]}{start_row}:{cols[header[-1]]}{last}"
    if totals:
        tr = last + 1
        ws.cell(row=tr, column=start_col, value="Total").font = s["total_font"]
        for i, h in enumerate(header):
            c = ws.cell(row=tr, column=start_col + i)
            if h in totals:
                fn = totals[h]
                c.value = fn if fn.startswith("=") else f"={fn}({cols[h]}{first}:{cols[h]}{last})"
                c.number_format = FMT.get(formats.get(h, ""), formats.get(h, "General"))
            c.font = s["total_font"]; c.fill = s["total_fill"]; c.border = s["total_border"]
    if freeze:
        ws.freeze_panes = ws.cell(row=start_row + 1, column=start_col)
    autofit(ws, overrides=widths, header_cols=cols)
    return dict(first=first, last=last, cols=cols, header_row=start_row)


def df_to_sheet(ws, df, start_row: int = 1, formats: dict | None = None, **kw) -> dict:
    """pandas DataFrame → styled block (index dropped; reset_index() first if needed)."""
    return write_table(ws, [str(c) for c in df.columns], df.itertuples(index=False, name=None),
                       start_row=start_row, formats=formats, **kw)


def autofit(ws, min_w: int = 8, max_w: int = 60, overrides: dict | None = None,
            header_cols: dict | None = None):
    """Approximate autofit (openpyxl can't measure text). Formulas count as 12 chars."""
    x = _xl()
    widths: dict[str, int] = {}
    for row in ws.iter_rows():
        for c in row:
            if c.value is None or type(c).__name__ == "MergedCell":
                continue
            v = c.value
            n = 12 if isinstance(v, str) and v.startswith("=") else len(
                v.strftime("%Y-%m-%d") if isinstance(v, (_dt.date, _dt.datetime)) else
                f"{v:,.2f}" if isinstance(v, float) else str(v))
            widths[c.column_letter] = max(widths.get(c.column_letter, 0), n)
    for col, n in widths.items():
        ws.column_dimensions[col].width = max(min_w, min(max_w, n + 3))
    for h, w in (overrides or {}).items():
        col = (header_cols or {}).get(h, h)
        ws.column_dimensions[col].width = w


def add_chart(ws, kind: str, data_ref: tuple, cats_ref: tuple, anchor: str, title: str = "",
              y_title: str = "", x_title: str = "", width_cm: float = 18, height_cm: float = 9,
              theme: dict | None = None, stacked: bool = False):
    """Native Excel chart. data_ref/cats_ref: (min_col, min_row, max_col, max_row) on ws.
    data_ref INCLUDES the header row (titles_from_data). kind: bar|col|line|pie|scatter."""
    from openpyxl.chart import BarChart, LineChart, PieChart, Reference, ScatterChart, Series
    t = theme or _wb_theme(ws)
    mc, mr, xc, xr = data_ref
    data = Reference(ws, min_col=mc, min_row=mr, max_col=xc, max_row=xr)
    cats = Reference(ws, min_col=cats_ref[0], min_row=cats_ref[1], max_col=cats_ref[2], max_row=cats_ref[3])
    if kind in ("bar", "col"):
        ch = BarChart(); ch.type = "bar" if kind == "bar" else "col"
        if stacked:
            ch.grouping = "stacked"; ch.overlap = 100
    elif kind == "line":
        ch = LineChart()
    elif kind == "pie":
        ch = PieChart()
    elif kind == "scatter":
        ch = ScatterChart()
        for col in range(mc, xc + 1):
            s = Series(Reference(ws, min_col=col, min_row=mr, max_row=xr), cats, title_from_data=True)
            ch.series.append(s)
    else:
        raise ValueError(kind)
    if kind != "scatter":
        ch.add_data(data, titles_from_data=True)
        ch.set_categories(cats)
    ch.title = title or None
    if kind != "pie":
        ch.y_axis.title = y_title or None
        ch.x_axis.title = x_title or None
        ch.x_axis.delete = False; ch.y_axis.delete = False  # openpyxl ≥3.1 hides axes otherwise
        ch.legend.position = "b"
        ch.y_axis.number_format = "#,##0"
        ch.y_axis.majorGridlines.spPr = None
        if kind in ("bar", "col"):
            ch.y_axis.scaling.min = 0  # truncated bar axes exaggerate differences
            ch.gapWidth = 60
    for i, s in enumerate(ch.series):
        color = t["series"][i % len(t["series"])]
        s.graphicalProperties.solidFill = color
        s.graphicalProperties.line.solidFill = color
        if kind == "line":
            s.smooth = False; s.graphicalProperties.line.width = 22000
    ch.width, ch.height = width_cm, height_cm
    ws.add_chart(ch, anchor)
    return ch


def add_list_validation(ws, cell_range: str, options: Sequence[str], allow_blank: bool = True):
    from openpyxl.worksheet.datavalidation import DataValidation
    dv = DataValidation(type="list", formula1='"' + ",".join(options) + '"', allow_blank=allow_blank)
    ws.add_data_validation(dv); dv.add(cell_range)
    return dv


def highlight_negative(ws, cell_range: str, theme: dict | None = None):
    from openpyxl.formatting.rule import CellIsRule
    from openpyxl.styles import Font
    t = theme or _wb_theme(ws)
    ws.conditional_formatting.add(cell_range, CellIsRule(operator="lessThan", formula=["0"],
                                                         font=Font(color=t["accent"])))


def add_notes_sheet(wb, notes: Sequence[tuple[str, str]], title: str = "Notes",
                    generated: str | None = None):
    """Assumptions / sources / legend sheet — every hardcoded number gets a line here.
    generated: stamp from CONFIG (e.g. "2026-10-31") so re-runs are deterministic."""
    ws = wb.create_sheet(title)
    r = write_title(ws, title, f"Generated {generated}" if generated else None)
    write_table(ws, ["Item", "Detail"], notes, start_row=r, widths={"Item": 28, "Detail": 90},
                freeze=False, zebra=False)
    wrap = xl_styles(_wb_theme(ws))["wrap"]
    for row in ws.iter_rows(min_row=r + 1):
        for c in row:
            c.alignment = wrap
    return ws


def set_print(ws, landscape: bool = True, fit_width: bool = True, paper: str = "A4",
              repeat_header_row: int | None = None):
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.page_setup.paperSize = {"A4": ws.PAPERSIZE_A4, "Letter": ws.PAPERSIZE_LETTER,
                               "Legal": ws.PAPERSIZE_LEGAL}.get(paper, ws.PAPERSIZE_A4)
    if fit_width:
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    if repeat_header_row:
        ws.print_title_rows = f"{repeat_header_row}:{repeat_header_row}"
    ws.oddFooter.center.text = "Page &P of &N"


__all__ = [n for n in dir() if not n.startswith("_")]
