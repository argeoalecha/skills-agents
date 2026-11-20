"""Synthetic example: a short electrical survey procedure with forms, built in the
ee-procedure house style. Not a real project — names, references and campuses are
invented. Run:  python build_example_procedure.py out/EX-1.03_Example_Procedure_RevA.docx
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from procbuild import ProcDoc, opts  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "out/EX-1.03_Panelboard_Survey_Procedure_RevA.docx"

META = dict(
    client="Example Medical Centre (SYNTHETIC)",
    project="Example Electrical Records Upgrade Project",
    title="Panelboard Survey Procedure and Forms",
    subtitle="Low-voltage as-built verification of distribution and panelboards",
    ref="EX-1.03", rev="A", status="IFR", date="21 November 2026",
    header_title="EMC Electrical Records Upgrade - Panelboard Survey Procedure and Forms",
)

d = ProcDoc(META)
d.cover(
    control=[
        ("Project", META["project"]),
        ("Client", META["client"]),
        ("Deliverable", f"{META['ref']} - {META['title']} (Phase 1 - Electrical Assessment)"),
        ("Basis", "EX-AGR-100 Appendix A; EX-1.02 Execution Plan Rev A"),
        ("Owner / Checked by", "Consultant / PEE (Engineer of Record) - verification EX-1.03-V"),
        ("Revision / Status", "Rev A - Issued for Review (IFR) to the PEE"),
        ("Date", META["date"]),
        ("Contents", "Procedure (Sections 1-12); Appendix A board index; Appendix B field forms F-01 to F-04"),
    ],
    approval={"parties": ["Consultant", "PEE (Engineer of Record)", "Owner representative"],
              "names": ["(Consultant name)", "(PEE name)", "(nominated at kick-off)"]},
    revisions=[("A", META["date"], "IFR", "First issue for PEE review"),
               ("0", "", "Accepted", "Issue for use after PEE agreement and Owner acceptance")],
)
d.contents()

d.h1("Purpose")
d.para("This procedure sets out how the Consultant records, checks and reports the as-built "
       "condition of the low-voltage distribution boards and panelboards of the Example Medical "
       "Centre. It contains the field forms used for that work (Appendix B).")
d.para("**Governing principle: record what is found, not what the drawings say.** Existing "
       "drawings are unverified until checked in the field. Every recorded value carries its "
       "source (Section 7).")

d.h1("Scope")
d.h2("Included")
d.bullets(["main and sub-distribution boards and their incoming feeders;",
           "lighting and power panelboards and their directories, recorded verbatim;",
           "visible grounding and bonding at each board."])
d.h2("Exclusions")
d.bullets(["Energised work of any kind, and removal of any cover or dead-front by the Consultant.",
           "Operation of any switching device or change to any setting.",
           "Tests and measurements of any kind.",
           "Engineering evaluation of adequacy or compliance. These are reserved to the PEE under "
           "RA 7920."])

d.h1("References")
d.table(["Reference", "Title and use in this procedure"], [
    ["EX-AGR-100", "Services Agreement, Appendix A - deliverables"],
    ["EX-1.02 Rev A", "Execution Plan - roles, regulatory boundary, document control"],
    ["PEC 2017 Part 1", "Philippine Electrical Code - terminology. Compliance is determined by the PEE"],
    ["RA 7920", "Electrical Engineering Law - reserved acts and the Consultant's boundary"],
    ["RA 11058 and DOLE OSHS", "Occupational safety and health - general site duties"],
    ["NFPA 70E", "Electrical safe work practice - approach boundaries (Section 5)"],
    ["RA 10173", "Data Privacy Act of 2012 - photographs on an occupied site"],
], "References", [2600, 6760])

d.h1("Roles and responsibilities")
d.table(["Party", "Responsibilities under this procedure"], [
    ["Consultant", "Prepares this procedure and forms. Carries out the survey and photographs. "
                   "Records observations. Does no energised work and makes no engineering evaluation."],
    ["PEE (Engineer of Record)", "Checks this procedure (EX-1.03-V) before the survey starts. Sets "
                                 "approach boundaries and PPE for any PEE-attended session. Verifies "
                                 "the records by sample walk-down."],
    ["Owner representative", "Confirms the board list. Provides keys, access and an escort. Opens "
                             "enclosure doors. Receives all observations."],
], "Responsibilities", [2600, 6760])
d.hold_points([("HP-1", "No survey starts until the PEE has checked this procedure and the Owner "
                        "has accepted it."),
               ("HP-2", "No dead-front is removed except in a PEE-attended session.")])

d.h1("Safety and site rules")
d.steps(["**No energised work.** The Consultant never touches conductors or internal components.",
         "**Doors.** Enclosure doors are opened by the Owner's electrician. The Consultant views "
         "and photographs only.",
         "**Approach.** Stay outside the limited approach boundary set by the PEE for any exposed "
         "energised part.",
         "**Stop-work.** On exposed live parts, signs of overheating or water ingress: stop, keep "
         "others away, notify the Owner representative at once and record a category S "
         "observation (Form F-03)."])

d.h1("Survey workflow")
d.table(["Stage", "Activity", "Forms", "Feeds"], [
    ["1 Preparation", "Board list, document intake, PEE check of this procedure (HP-1)", "App. A, F-01", "EX-1.04"],
    ["2 Survey", "Per board, upstream to downstream", "F-02", "EX-1.06"],
    ["3 Close-out", "Observations, completion and sign-off", "F-03, F-04", "Progress"],
], "Workflow summary", [1800, 4360, 1600, 1600])

d.h1("Data recording rules")
d.h2("Reserved entries")
d.table(["Entry", "Meaning"], [
    ["NV", "Not visible without opening an enclosure or removing a cover"],
    ["ILL", "Present but illegible"],
    ["UNK", "Cannot be determined from any available source"],
    ["NA", "Does not apply to this asset"],
    ["NONE", "Checked and confirmed absent"],
], "Reserved entries", [1400, 7960], note="No field is left blank")
d.h2("Source codes")
d.table(["Code", "Source of the value"], [
    ["N", "Nameplate or rating plate"], ["L", "Label or panel directory"],
    ["O", "Observed directly"], ["M", "Measured by the Consultant (dimensions only)"],
    ["D", "Document - quote the F-01 document number"], ["S", "Stated by Owner staff - record the name"],
], "Source codes", [1400, 7960])

d.h1("Observations")
d.para("An observation is a recorded fact that needs attention or referral. It describes what "
       "was seen; it does not state that something is non-compliant. That determination is the PEE's.")
d.table(["Cat.", "Title", "Examples", "Notify"], [
    ["S", "Safety", "Exposed live parts, signs of overheating, water ingress", "Owner at once; PEE same day"],
    ["D", "Documentation discrepancy", "Drawing or directory differs from what is found", "Weekly; joint walk-down"],
    ["L", "Labelling", "Missing, illegible or duplicated labels", "Weekly"],
], "Observation categories", [800, 2200, 4060, 2300], note="Numbering: OBS-nnn")

d.h1("Quality control and acceptance")
d.table(["#", "Criterion", "Evidence"], [
    ["1", "Every board on the confirmed list surveyed and signed off", "Board index; F-04 set"],
    ["2", "Every board has a fed-from reference, or UNK with a D observation", "F-02; F-03"],
    ["3", "Every category S observation notified on the day it was found", "F-03 times"],
    ["4", "PEE sample verification with no unresolved disagreement", "PEE checklist"],
], "Acceptance criteria", [600, 5560, 3200])

d.h1("Open items affecting this procedure")
d.table(["#", "Item", "Owner", "Needed by"], [
    ["1", "Authoritative board list", "Owner", "Kick-off"],
    ["2", "Schedule of PEE-attended sessions for dead-front removal", "PEE / Owner", "Before Stage 2 ends"],
], "Open items", [600, 5160, 1800, 1800])

d.appendix("Board index and survey schedule", landscape=True)
d.para("One row per board. Survey numbers are assigned at kick-off and never reused.")
d.table(["Board no.", "Building", "Board name (as found)", "Fed from", "Location",
         "Planned date", "Actual date", "F-04 signed", "Remarks"],
        [[""] * 9 for _ in range(10)], None, [1200, 1300, 1900, 1300, 1700, 1300, 1300, 1100, 1860])

d.appendix("Field forms", new_section=False)
d.para("Every field takes a value or a reserved entry (NV, ILL, UNK, NA, NONE) and, where a Src "
       "column is shown, a source code (N, L, O, M, D, S).")
INDEX = [
    dict(group="Section A - Preparation", code="F-01", title="Document intake register", orientation="Landscape", completed="Stage 1 onward"),
    dict(group="Section B - Survey", code="F-02", title="Board record", orientation="Portrait", completed="Per board"),
    dict(group="Section C - Close-out", code="F-03", title="Observation log", orientation="Landscape", completed="As found"),
    dict(group="Section C - Close-out", code="F-04", title="Board survey completion and sign-off", orientation="Portrait", completed="Per board"),
]
d.form_index(INDEX)

f = d.form("F-01", "Document intake register", "Every existing drawing or record received, "
           "whatever its condition.", "EX-1.04", landscape=True)
f.grid(["Building", "Received from", "Recorded by", "Sheet ___ of ___"])
f.log(["Doc no. (DOC-nnn)", "Title / description", "Type", "Provided by", "Doc date / rev",
       "Format", "Condition", "Date received", "Remarks"], 10,
      [1500, 2600, 1200, 1300, 1300, 1100, 1300, 1300, 1360])

f = d.form("F-02", "Board record", "One per board. Doors opened by the Owner's electrician; "
           "dead-front in place.", "EX-1.06")
f.grid(["Building", "Board no.", "Location", "Date", "Recorded by", "Sheet ___ of ___"])
f.fields([("group", "Part A - Identification"), "Board name as found", "Fed from (board / way)",
          ("group", "Part B - Nameplate"), "Manufacturer", "Rated voltage (as marked)",
          "Main device type and rating (as marked)",
          ("Enclosure condition", opts(["Good", "Damaged", "NV"])),
          ("group", "Part C - Directory"),
          ("Panel directory", opts(["Typed", "Handwritten", "None"])), "Ways used / spare",
          "Observation refs (F-03)"])
f.signoff(["Recorded by (Consultant)", "Owner escort"])

f = d.form("F-03", "Observation log", "Each observation as found, categorised under Section 8.",
           "EX-1.06, Owner and PEE", landscape=True)
f.grid(["Building", "Recorded by"])
f.log(["Obs. no. (OBS-nnn)", "Date / time", "Board no.", "Cat.", "Description (what was seen)",
       "Photo refs", "Notified to / when", "Status"], 10,
      [1500, 1300, 1200, 700, 4000, 1300, 1660, 1300])

f = d.form("F-04", "Board survey completion and sign-off", "Signed when every item is done or "
           "not applicable. The escort's signature confirms the survey took place as recorded, "
           "not technical acceptance.", "Physical progress")
f.grid(["Building", "Board no.", "Survey date", "Board name"])
f.checks([("group", "Records"), "F-02 board record complete", "Directory recorded verbatim",
          ("group", "Quality"), "No blank fields; reserved entries used",
          "Fed-from recorded, or UNK with a D observation", "All category S observations notified"])
f.signoff(["Consultant", "Owner escort (witness)"])

print(d.save(OUT))
