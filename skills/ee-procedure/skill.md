---
name: ee-procedure
description: >-
  Writes electrical engineering procedures and execution plans as issued .docx
  deliverables in the house style: field-survey and assessment procedures with field
  forms (F-01..F-nn), method statements for PEE-attended sessions, test, inspection and
  labelling procedures, and project execution and management plans (PEMP). Cover with
  control block, approval and revision history; numbered sections; hold points; captioned
  tables; reserved entries and source codes; observation categories; acceptance criteria;
  forms in their own portrait or landscape sections with Feeds / Form rev / sign-off.
  Built by a reproducible Python script and checked by a validator. Every document is
  Rev A Issued for Review to the PEE under RA 7920. Use when an electrical engagement
  needs a procedure, work method, field forms, survey forms, checklist set, or execution
  plan. Triggers on /ee-procedure, "write a procedure", "assessment procedure", "survey
  procedure and forms", "field forms", "method statement", "test procedure",
  "commissioning procedure", "inspection procedure", "execution plan", "PEMP",
  "project management plan".
---

# Electrical Procedures and Execution Plans

A procedure says **how** work is done, by whom, with what limits, and how its data is
recorded and accepted. Write it so a field engineer can follow it without asking, and so the
PEE can check it against RA 7920 in one reading. The .docx is produced by a build script; the
script is the editable source.

## Jurisdiction

| Skill / agent | Owns |
|---|---|
| **`/ee-procedure` (this skill)** | How work is done and recorded: procedures, field forms, method statements, execution and management plans |
| `/ee-spec-writer` | What is supplied and installed: 3-part specification sections. A test procedure cites the spec's acceptance values; it never sets them |
| `/ee-load-calc`, `/ee-short-circuit`, `elektra-arc-flash` | Every number a procedure relies on (limits, boundaries, settings). Cite their output; never compute or assume one here |
| `as-built-agent` | Carries out the survey and turns completed forms into topology data. The forms here are its input contract |
| `/ee-drafting` | Drawings produced from the recorded data |
| `/python-office-builds` | The docx mechanics (`officekit`, `verify.py`) this skill builds on; the PEMP's tracker workbook (.xlsx) |
| `/ee-audit` | Cross-checking issued deliverables against each other before release |
| `/proposal-tech` | Scope and phases a PEMP turns into a baseline |

## Inputs - stop if missing

Ask for, or read from the project folder, before drafting:

1. **The basis**: the agreement / scope appendix and the proposal the document implements,
   with deliverable refs. Never invent a deliverable reference.
2. **Parties and roles**: Consultant, PEE (Engineer of Record), owner representative,
   other owner units; who checks and who accepts.
3. **The governing plan** (for a procedure: the PEMP's roles, safety and document-control
   sections) so the two do not contradict each other.
4. **Owner standards and codes** to reuse (site codes, asset type codes, labelling standard).
5. **Ref, revision, date, status**: normally Rev A, IFR.

If an input does not exist yet, write the dependent item into Section 15 "Open items" with an
owner and a "needed by". Do not fill it with a plausible guess.

## Procedure

1. **Pick the document type** and read its section model in
   `reference/procedure-anatomy.md` (Type P procedure with forms, Type M execution plan, or
   a mapped type: method statement, test, inspection, labelling).
2. **Draft the content first**, section by section, following the writing rules below.
   Design the forms from the data the downstream deliverables need: list each deliverable a
   form feeds, then the fields it needs (`reference/forms-and-recording.md`).
3. **Write the build script** `build_<ref>.py` in the project's `build/` folder, modelled on
   `examples/build_example_procedure.py`:
   ```python
   import sys; sys.path.insert(0, "/Users/<user>/.claude/skills/ee-procedure/scripts")
   from procbuild import ProcDoc, opts
   d = ProcDoc(META)                       # project, title, ref, rev, status, date, header_title
   d.cover(control, approval, revisions); d.contents()
   d.h1("Purpose"); d.para("... **Governing principle: ...**")
   d.table(header, rows, "References", widths)          # caption numbered Table n.m
   d.hold_points([("HP-1", "No ... until ...")])
   d.appendix("Field forms", new_section=False); d.form_index(INDEX)
   f = d.form("F-01", "Title", "When and how used.", "Feeds", landscape=True)
   f.grid([...]); f.fields([("group", "Part A - ..."), "Field", ("Field", opts([...]))]); f.signoff([...])
   d.save("out/<Ref>_<Short-title>_RevA.docx")
   ```
   Widths are in twips (portrait text width 9360, landscape 12960). `**bold**` works in any text.
4. **Build and validate** in an environment with python-docx (on macOS create a venv:
   `python3 -m venv .venv && .venv/bin/pip install python-docx`):
   ```bash
   .venv/bin/python build/build_<ref>.py
   .venv/bin/python ~/.claude/skills/ee-procedure/scripts/validate.py out/<file>.docx
   .venv/bin/python ~/.claude/skills/python-office-builds/scripts/verify.py out/<file>.docx --pages=1-40
   ```
   `validate.py` checks house style, cover blocks, section / sub-section / caption numbering,
   that every body table is captioned or labelled, every form's Feeds / Form rev / own
   section / index entry / signature block, and that every HP-n, F-nn, Table n.m and Section n
   referenced exists. `verify.py` renders the PDF and page images. Exit 0 from both, then
   **look at the pages**: forms that split badly, landscape logs that overflow, orphan headings.
5. **Report** what the PEE must check: the hold points, the safety boundaries, every open
   item, and anything you could not source.
6. **Issue**: PDF plus the .docx under transmittal, as Rev A IFR to the PEE. Rev 0 only after
   the PEE agrees and the owner accepts.

## Writing rules

- **Plain, imperative, present tense.** "The owner's electrician opens the door. The
  Consultant photographs only." One instruction per sentence. Steps are numbered; lists of things are
  bulleted and end with `;` except the last.
- **Bold leads** on rules and steps: `**No energised work.** The Consultant never ...`.
- **Every party named the same way throughout** (Consultant, PEE, owner representative), never
  "we" or "the team".
- **Boundaries are explicit and repeated where they bite**: exclusions in Section 2, the rule in
  Section 6, the hold point in Section 5, the "not used" tools in Section 7.
- **Facts, not judgements.** The Consultant records what is found. Adequacy, compliance and
  sizing are reserved to the PEE under RA 7920; say so wherever a form or observation could
  drift into a judgement.
- **Numbers come from a source.** Approach distances cite NFPA 70E's table; limits cite the spec
  or calc; turnaround times cite the PEMP. Never state a value without one.
- **Every table gets a caption** `Table n.m - Title` (with an optional note: numbering scheme,
  file-name rule), except labelled blocks (Approval, Revision history, Hold points).
- **Cross-reference by number** (Section 10, Table 10.2, Form F-17, PEMP §7.3) and make sure the
  target exists - the validator checks it.
- **Units**: A, V, kA, kVA, kW, mm², m. Dates `16 November 2026` in prose, `dd-mmm-yyyy` on forms.
- **Philippine context**: PEC 2017 for terminology, RA 7920 for the licensure boundary,
  RA 11058 / DOLE OSHS for site safety, RA 10173 for photographs and personal data; utility
  data (Meralco or the local distribution utility) is requested through the owner.

## House style (applied by `procbuild`)

US Letter; Arial 10 pt; headings 15 / 12 / 10.5 pt bold black; tables with grey `D9D9D9`
header rows that repeat on each page, `F2F2F2` group rows and form label cells, `808080`
borders, 9 pt (8 pt in forms); italic grey 9 pt captions; header
`<short client> <project> - <title>` with `<ref> Rev X` right-aligned over a rule; centred
`Page X of Y` footer; each form in its own section. Change the style in `procbuild.py`, not
per document.

## Licensure boundary

Every document is a draft issued for the PEE's review. Under RA 7920 the PEE checks the
procedure before any field work (a hold point), owns every engineering determination, and
directs any work near energised equipment. This skill never writes a procedure that has the
Consultant touch, open, operate or test energised equipment, and never states a code
compliance finding.

## Files

- `scripts/procbuild.py` - `ProcDoc` (cover, contents, h1/h2/h3, para, bullets, steps,
  hold_points, table, appendix, form_index, form, save) and `Form` (grid, fields, log, checks,
  continued, note, signoff); `opts()` for tick boxes. Builds on
  `python-office-builds/scripts/officekit.py`.
- `scripts/validate.py` - document checks (`validate.py <file.docx>`) or self-test (no argument:
  builds the example, checks it, tests that bad input is rejected).
- `examples/build_example_procedure.py` - synthetic panelboard survey procedure with four forms.
- `reference/procedure-anatomy.md` - section models for procedures and execution plans.
- `reference/forms-and-recording.md` - form anatomy, reserved entries, source codes,
  observation categories, IDs, review codes, hold points.
