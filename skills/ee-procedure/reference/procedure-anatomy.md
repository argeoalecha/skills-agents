# Document Anatomy

Section models for the two document types this skill writes. They were taken from two
issued reference deliverables (a Phase 1 execution and management plan and a Phase 1
electrical assessment procedure with forms) and generalised. Keep the section order and
titles unless the engagement has a reason to differ; reviewers learn where to look.

## Front matter (both types)

| Block | Content |
|---|---|
| Cover lines | Client (11 pt grey), project (12 pt grey), **title** (22 pt bold), subtitle (13 pt grey, optional), `Deliverable <ref> \| Rev X \| <status>` |
| Control block | Project; Client; Deliverable (ref - title (phase)); Basis (the agreement appendix, proposal, and governing plan this document rests on); Owner / Checked by (with the verification ref, e.g. `<ref>-V`); Revision / Status; Date; Contents (what the document contains, or a separate-file appendix) |
| Approval | Prepared by / Checked by / Accepted by x Party / Name / Signature / Date. Normally Consultant / PEE (Engineer of Record) / Owner representative |
| Revision history | Rev / Date / Status / Description. Rev A = first IFR; Rev 0 = issue after checker agreement and owner acceptance |
| Contents | TOC field, levels 1-2 (forms are level 2, so they list) |

## Type P - Procedure with field forms

| # | Section | Must contain |
|---|---|---|
| 1 | Purpose | What the procedure governs, who does it, what it contains; which deliverables its data feeds; the **governing principle** in bold (e.g. "record what is found, not what the drawings say") |
| 2 | Scope | 2.1..2.n what is covered, by system, as bullets ending in `;`; a sub-section **Exclusions** that names every reserved act: energised work, switching, settings, tests, engineering evaluation (reserved to the PEE under RA 7920), utility-owned equipment, permanent labelling; the survey/work unit (one building, one board) and its numbering |
| 3 | References | Table: Reference / Title and use in this procedure. Agreement, proposal, governing plan, owner standards, PEC 2017 (terminology only - compliance is the PEE's), RA 7920, RA 11058 + DOLE OSHS, NFPA 70E, RA 10173, discipline standards |
| 4 | Definitions and abbreviations | Table: Term / Meaning. Every coined term (as-found, survey unit, T-ID, source code, observation, PEE-attended session) and every abbreviation used |
| 5 | Roles and responsibilities | Table: Party / Responsibilities under this procedure, one row per party. Then the **hold points** table (HP-1..n): what may not start until what |
| 6 | Safety and site rules | 6.1 General (escort, sign-in, toolbox talk, minimum PPE, work at height); 6.2 Electrical as **numbered rules with bold leads**: no energised work, doors, dead-fronts, approach boundary (cite NFPA 70E table and distance), no operation, stop-work; 6.3 other disciplines (IT rooms); 6.4 operations and privacy |
| 7 | Tools and equipment | Table: Item / Use and notes. Then what is **not** used (testers, meters) so the boundary is visible |
| 8 | Identification | Temporary ID format table (level / format / example), survey-only codes, as-found label recorded verbatim, crosswalk to permanent IDs, survey tags |
| 9 | Workflow | Summary table Stage / Activity / Forms / Feeds, then one sub-section per stage as numbered steps. Photo set table (code / view / content) with the file-name rule in the caption note |
| 10 | Data recording rules | Reserved entries table, source codes table, recording rules (verbatim nameplates, units, two sources disagree = record both, corrections struck once and initialled) |
| 11 | Observations | Definition (facts, not compliance judgements), category table Cat. / Title / Examples / Notify, numbering scheme in the caption |
| 12 | Quality control and acceptance | Consultant checks (daily, per unit); PEE verification (sample rule, e.g. all main boards + at least 10% of others); acceptance criteria table # / Criterion / Evidence |
| 13 | Reporting and outputs | Form-to-deliverable map; database structure (table / content / from forms); progress and summary report contents |
| 14 | Records and confidentiality | Folder structure, originals kept unedited, restricted data, ownership and handover |
| 15 | Open items affecting this procedure | Table # / Item / Owner / Needed by |
| App. A | Index / schedule of units | Landscape register, one row per unit, blank rows |
| App. B | Field forms | Intro (reserved entries + source codes apply), form index grouped by section (Form / Title / Orientation / Completed), then F-01..F-nn |

Drop a section only when it truly does not apply (a desk-only procedure has no Section 7);
renumber, never leave a gap.

## Type M - Execution and management plan

| # | Section | Must contain |
|---|---|---|
| 1 | Purpose and governing documents | 1.1 purpose (turns the proposal into a baseline; Rev 0 becomes BL-0); 1.2 precedence list (each party's contract, then the signed proposal, then this plan) and the statement that the plan creates no contractual link and changes no scope or fee; 1.3 users |
| 2 | Project summary | Objectives, scope by phase, exclusions, planning assumptions (response times, calendars) |
| 3 | Organisation and responsibilities | Parties and reporting; owner / checker / acceptor of each deliverable; **regulatory boundary (RA 7920)** |
| 4 | Work breakdown structure | Structure and coding of deliverable refs; deliverable types; pointer to the register |
| 5 | Schedule management | Baseline programme, key milestones, critical path, gates, hand-offs and review turnaround, forecasting and baseline control |
| 6 | Deliverable review and acceptance | Submission under transmittal (PDF + editable source); review codes table (A agreed / B agreed with comments / C not agreed - resubmit within n WD); acceptance turnaround; revision convention (letters for review, numbers after acceptance) |
| 7 | Progress measurement and reporting | Method, rules of credit, field and milestone items, weighting, planned progress, KPIs, tracker, reporting cycle |
| 8 | Communication | Meetings, channels, distribution |
| 9 | Document control | Numbering, file name `<Ref>_<Short-title>_Rev<X>.<ext>`, superseded revisions, register, storage, field-record naming |
| 10 | Quality, safety and site work | Owner-checker principle and counter-checks; safety rules (no energised work by the Consultant, escorts, permits, outages outside operating hours); data privacy (RA 10173) |
| 11 | Risk and issue management | Scoring (likelihood x impact 1-5, bands), owner, response, trigger, review cadence; actions log |
| 12 | Change control | What a change is; numbered procedure (request, assess, approve in writing, update register, raise baseline BL-n); forecast slips do not re-baseline |
| 13 | Interfaces | Table Interface / Managed through |
| 14 | Close-out | Conditions for closure and handover |
| 15 | Items to close at kick-off | Numbered list |
| Apps | Tracker (separate .xlsx via `/python-office-builds`), baseline register, programme and milestones, hand-off schedule, responsibility matrix, initial risk register, forms (transmittal, comment response sheet, change request, progress report outline) |

## Other procedure types

Map them onto Type P and keep its front matter, hold points, recording rules and acceptance
table:

| Type | Adjust |
|---|---|
| Method statement for a PEE-attended session (dead-front removal, setting extraction) | The Consultant drafts; the work is under the PEE's responsible charge and the owner's permit-to-work. Section 6 becomes the PEE's boundaries and PPE, stated as "set by the PEE", never chosen by this skill |
| Test / commissioning procedure | Draft for the PEE. Test values, acceptance limits and instrument classes come from the spec (`/ee-spec-writer`) or the calc (`/ee-load-calc`, `/ee-short-circuit`), cited; never invented. Results forms carry measured value, limit, pass/fail and instrument ID with calibration date |
| Inspection procedure (installation vs design) | Observations stay factual; nonconformity is logged, the corrective decision is the PEE's |
| Labelling / identification procedure | Section 8 becomes the main body: ID grammar, crosswalk, label materials from the owner's standard |
