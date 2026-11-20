# Forms and Recording Conventions

## Form anatomy (every F-nn)

1. **Own section**, portrait or landscape (registers and logs with 8+ columns go landscape).
2. **Heading** `F-nn - Title` (level 2, so it appears in the contents).
3. **Intro line**: one or two sentences on when and how it is used (who opens the doors,
   what is not done), then `**Feeds:** <deliverables>. **Form rev:** A`.
4. **Header grid**: label / blank value pairs, two per row, labels bold:
   site or campus, unit (building / board), T-ID, location, date, `Sheet ___ of ___`,
   recorded by, escort or witness.
5. **Body**, one of:
   - field table `Field | Value | Src`, grouped by `Part A - ...` rows, label cells shaded;
   - register / log: column header plus 10-14 blank rows;
   - checklist `Check | Status | Count / ref` with tick boxes `☐ Done ☐ NA`.
6. **Continuation** for long forms: `F-nn (continued)` with a short grid that repeats the
   unit, T-ID and date, so a separated sheet still identifies itself.
7. **References row** at the end of record forms: observation refs (F-nn of the observation
   log), remarks.
8. **Sign-off** `Role | Name | Signature | Date` on record, completion and verification forms.
   State what a signature means when it is not technical acceptance ("the escort's
   signature confirms the survey took place as recorded").

Form design rules:

- Field names are the database column names. Write them so they can be: one value each,
  units in the label (`Dimensions L x W x H (m)`), `(as marked)` where a value is transcribed.
- Closed lists as tick boxes with `opts([...])`, always with an escape (`UNK`, `NV`, `Other`).
- Every field takes a value or a reserved entry; nothing is left blank.
- A form never asks the Consultant for a judgement reserved to the PEE (adequate, compliant,
  correctly sized). It asks for what is seen, read or measured.
- The last form is the PEE's: Part A checks the procedure itself (`<ref>-V`), Part B is the
  sample walk-down (T-ID / field checked / recorded value / found value / agree), then a
  summary and the result `☐ Agreed ☐ Agreed with comments ☐ Not agreed - re-survey`.

Typical survey form set (rename to the engagement): document intake register; information
request checklist (Part A owner facilities, Part B owner IT, Part C utility through the
owner); unit survey record; main switchboard and incomer; distribution / panelboard; circuit
schedule; standby, UPS and on-site generation; monitoring interface point; network closet,
links, core and edge; power-source trace; photograph log; GPS log; daily field log and safety
record; observation and discrepancy log; unit completion and sign-off; PEE verification checklist.

## Reserved entries

| Entry | Meaning |
|---|---|
| NV | Not visible without opening an enclosure, removing a cover or navigating a menu |
| ILL | Present but illegible |
| UNK | Cannot be determined from any available source |
| NA | Does not apply to this asset |
| NONE | Checked and confirmed absent |

## Source codes (Src column)

| Code | Source |
|---|---|
| N | Nameplate or rating plate |
| L | Label or panel directory |
| O | Observed directly (count, type, arrangement, colour) |
| M | Measured by the Consultant - dimensions and distances only |
| D | Document - quote the intake document number |
| S | Stated by owner staff - record the name |
| R | Read from a device display or interface |

Recording rules that go with them: transcribe nameplates verbatim with units as marked;
never convert, calculate or infer a rating; a value from a drawing needs `D` and the document
number; when two sources disagree record both and log a discrepancy, do not choose; cable
sizes as printed on the insulation; distances to 0.1 m; dates `dd-mmm-yyyy`, 24-hour times;
ink on paper, corrections struck once and initialled, scanned the same day.

## Observation categories (adapt the set, keep the shape)

| Cat. | Title | Notify |
|---|---|---|
| S | Safety (exposed live parts, overheating, water ingress) | Owner representative at once; PEE the same day; stop-work |
| C | Condition | Daily log; weekly |
| D | Documentation discrepancy (drawing / label / directory differs; fed-from not confirmed) | Weekly; joint walk-down |
| L | Labelling and identification | Weekly; labelling phase input |
| A | Access and working space | Weekly to owner |
| M / I | Discipline-specific (monitoring interface, IT backbone) | Weekly to design |

Observations describe what was seen. "Non-compliant", "undersized" and "must be replaced" are
the PEE's determinations and never appear in an observation. Number them `OBS-<site>-nnn`.

## Identification

- Temporary IDs (`T-ID`) reuse the owner's site and asset-type codes with a numeric unit
  segment so they cannot be mistaken for permanent IDs: `CCC-Bnn-TTnn`, circuits
  `<T-ID>/nn`, devices in a board `<board T-ID>-CBnn`.
- T-IDs are never reused; a duplicate is closed with a note.
- The as-found label is recorded verbatim beside every T-ID, even when wrong.
- The crosswalk (T-ID, as-found label, permanent ID later) lives in the asset database from
  day one.
- Photos: `<T-ID>_<view code>_<nn>.jpg`; originals unedited; annotated copies `_ann`.
- GPS: WGS84 decimal degrees, six places, with the device's stated accuracy; indoor assets
  get the fix at the room door plus floor / room / offset.

## Review, revision and document control (from the management plan)

| Code | Meaning | Next step |
|---|---|---|
| A | Agreed - no comments | Owner issues for acceptance |
| B | Agreed with comments | Incorporate in the next revision |
| C | Not agreed | Revise and resubmit within the agreed working days |

Revisions: A, B, C ... for review; 0 on acceptance; 1, 2 ... later accepted revisions.
Status codes: IFR issued for review, IFC issued for comment, IFA issued for acceptance, IFU
issued for use. File names: `<Ref>_<Short-title>_Rev<X>.<ext>`.

## Hold points

A hold point names the activity that may not start and the condition that releases it:
"No site survey starts until the PEE has checked this procedure (`<ref>-V`) and the owner
has accepted it." Typical set: procedure checked and accepted; written authorisation for any
IT read-out; no dead-front removed except in a PEE-attended session; no test energised
without the PEE's permit and isolation in place.
