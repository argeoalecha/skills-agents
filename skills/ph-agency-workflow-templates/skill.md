---
name: ph-agency-workflow-templates
description: Current DTI→SEC→LGU→BIR business registration sequencing and the BIR Form 2303 checklist, for Philippine agency registration roadmapping. Used by atty-sia-compliance. Not invoked directly by the user. Needs a quarterly refresh — fee schedules and form numbers move. Triggers on "business registration sequence", "DTI SEC LGU BIR", "Form 2303 checklist", "agency registration roadmap".
---

# PH Agency Registration Workflow Templates

Stateless skeleton for the DTI→SEC→LGU→BIR sequence. `atty-sia-compliance` fills this
skeleton with the query's specifics and corroborates every fee, form number, and
processing time against a live retrieval (web fetch to the issuing agency, or corpus)
before presenting it as current — this skill gives the *shape* of the roadmap, not
authoritative current figures.

**Last verified against agency sites: not yet performed — this skeleton is drafted from
general knowledge of the standard sequence, not a retrieval.** `atty-sia-compliance`
must treat every bracketed figure below as `[VERIFY LIVE]` until it has actually fetched
the current page. **Refresh cadence: quarterly** — re-derive this skeleton from a fresh
retrieval every quarter; do not let it silently go stale.

---

## Sequencing skeleton

### Sole proprietorship
1. **DTI** — Business Name (BN) registration via the DTI Business Name Registration
   System. `[VERIFY LIVE: current fee schedule, processing time]`
2. **LGU — Barangay** — Barangay Business Clearance from the barangay where the
   business is located.
3. **LGU — City/Municipality** — Mayor's/Business Permit application (Business Permits
   and Licensing Office), typically requires the DTI BN cert and barangay clearance as
   prerequisites. `[VERIFY LIVE: LGU-specific requirements — these vary by
   city/municipality, not just nationally]`
4. **BIR** — Certificate of Registration via BIR Form 1901 (self-employed/mixed income)
   or applicable form for the taxpayer type, at the Revenue District Office (RDO)
   covering the business address.

### Corporation / Partnership
1. **SEC** — Registration (Articles of Incorporation/Partnership, By-Laws, name
   verification via the SEC Company Registration System). Governed by R.A. 11232
   (Revised Corporation Code). `[VERIFY LIVE: current SEC MC governing the process, fee
   schedule]`
2. **LGU — Barangay** — Barangay Business Clearance.
3. **LGU — City/Municipality** — Mayor's/Business Permit.
4. **BIR** — Certificate of Registration via BIR Form 1903 (corporations/partnerships),
   at the RDO covering the registered office address.

### BIR — common to both paths, post-Certificate of Registration
- **Form 2303 (Certificate of Registration) checklist:**
  - [ ] Registered Books of Account (manual, loose-leaf, or computerized —
    `[VERIFY LIVE: current BIR rules on which method requires prior approval]`)
  - [ ] Authority to Print (ATP) receipts/invoices, or accreditation for a
    Computerized Accounting System / CRM-POS if applicable
  - [ ] Registration fee payment (BIR Form 0605) — `[VERIFY LIVE: current annual
    registration fee amount and whether it's still required post-Ease of Paying Taxes
    Act, R.A. 11976]`
  - [ ] Display of Form 2303 and "Ask for Receipt" notice at the place of business
  - [ ] Enrollment for applicable eFPS/eBIRForms filing channel

---

## Output requirements when `atty-sia-compliance` uses this skeleton

- Name the specific BIR RMC, SEC MC, or LGU ordinance for every step actually cited —
  never present a step as current without a source named per the citation-verification
  gate in `ph-legal-citation-format`.
- Flag LGU-specific variance explicitly — this skeleton is the *national* shape; actual
  requirements, fees, and processing times vary by city/municipality and change without
  a centralized index.
- If retrieval fails or returns nothing for a fee/form figure, mark it
  `[UNVERIFIED — could not retrieve current figure]` rather than filling it from this
  skeleton's placeholder framing or from training-data recall.
