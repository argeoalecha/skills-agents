"""
Arc-flash workplace-safety workflow layer — PPE category banding, governing-case
selection, and safety-critical-flag logic per NFPA 70E (2024) Article 130.5 and the
IEEE 1584-2018 assessment process.

This module deliberately does NOT implement the IEEE 1584-2018 arcing-current or
incident-energy equations themselves. That calculation requires either a licensed
commercial tool (ETAP, SKM PowerTools, EasyPower, DIgSILENT PowerFactory) or a
documented independent implementation built directly against your own copy of IEEE
1584-2018 Section 4's equations and coefficient tables — the model's coefficients are
numerous, revised substantially between the 2002 and 2018 editions (results can nearly
double for the same equipment across that revision), and are not something to trust from
an LLM's training-data recall for a safety deliverable that determines what protective
equipment a worker relies on. Supply incident energy (cal/cm^2) per bus, per case,
computed externally; this module handles everything downstream of that number:
governing-case selection, PPE banding, boundary/control flagging, and report structuring.

PPE category bands, the arc-flash-boundary threshold, valid conductor-gap ranges, and
working-distance conventions below are cited directly from NFPA 70E (2024) Article 130.5
/ IEEE 1584-2018 as retrieved from a governing procedure document for a prior campus
engagement — not recalled from training data.
"""
from dataclasses import dataclass, field
from typing import Optional

# NFPA 70E (2024) Article 130.5 — onset of a second-degree burn; defines the arc flash
# boundary distance.
ARC_FLASH_BOUNDARY_THRESHOLD_CAL_CM2 = 1.2

# NFPA 70E (2024) Article 130.5 PPE category bands, incident energy in cal/cm^2 (upper
# bound of each band).
PPE_CATEGORY_BANDS = [
    (4.0, 1),
    (8.0, 2),
    (25.0, 3),
    (40.0, 4),
]

# Above this: arc blast becomes a pressure/shrapnel hazard independent of the thermal
# one. The only correct control is de-energizing or engineering the energy down — not a
# heavier suit. Never silently band a result above this threshold into "Category 4".
NO_PRACTICAL_PPE_THRESHOLD_CAL_CM2 = 40.0

# IEEE 1584-2018 valid conductor-gap ranges, voltage-dependent. Do not apply the wrong
# band for the voltage class.
VALID_GAP_RANGE_MM = {
    "lv": (6.35, 76.2),     # 0.25-3 in, 208-600 V
    "mv": (19.05, 254.0),   # 0.75-10 in, 601 V - 15 kV
}

# IEEE 1584-2018 default working distance. Confirm against the actual task distance
# where a worker's hands are closer than the standard convention assumes.
WORKING_DISTANCE_DEFAULT_MM = {
    "lv": 455,       # 18 in
    "mv_min": 610,   # 24 in
    "mv_max": 914,   # 36 in
}

ELECTRODE_CONFIGS = {
    "VCB":  "Vertical conductors/electrodes in a metal box/enclosure",
    "VCBB": "Vertical conductors/electrodes in a metal box/enclosure with a barrier",
    "HCB":  "Horizontal conductors/electrodes in a metal box/enclosure",
    "VOA":  "Vertical conductors/electrodes in open air",
    "HOA":  "Horizontal conductors/electrodes in open air",
}


def ppe_category(incident_energy_cal_cm2: float) -> int:
    """
    PPE category from incident energy, per NFPA 70E (2024) Article 130.5 bands.
    Returns 0 below the 1.2 cal/cm^2 arc-flash-boundary threshold (no category
    triggered), 1-4 per the standard bands. Raises above 40 cal/cm^2 — that case has
    no practical PPE answer and must be reported as a control-required finding, never
    silently banded into "Category 4".
    """
    if incident_energy_cal_cm2 > NO_PRACTICAL_PPE_THRESHOLD_CAL_CM2:
        raise ValueError(
            f"{incident_energy_cal_cm2:.2f} cal/cm^2 exceeds "
            f"{NO_PRACTICAL_PPE_THRESHOLD_CAL_CM2} cal/cm^2 — no practical PPE category "
            "applies. Report as a control-required finding (de-energize or engineer the "
            "energy down), not a PPE band.")
    if incident_energy_cal_cm2 < ARC_FLASH_BOUNDARY_THRESHOLD_CAL_CM2:
        return 0
    for threshold, category in PPE_CATEGORY_BANDS:
        if incident_energy_cal_cm2 <= threshold:
            return category
    raise AssertionError("unreachable — band table and NO_PRACTICAL_PPE_THRESHOLD disagree")


def electrode_config_risk_note(config: str) -> str:
    """
    Per IEEE 1584-2018 guidance: for identical fault current, voltage, and gap, an
    enclosed vertical configuration (VCB) can produce incident energy two to three
    times higher than an open-air configuration (VOA). Misidentifying the configuration
    is the single largest source of error in an arc-flash study — larger than any
    fault-current or clearing-time input error.
    """
    if config not in ELECTRODE_CONFIGS:
        raise ValueError(f"unknown electrode config {config!r}; use one of: "
                          f"{', '.join(ELECTRODE_CONFIGS)}")
    if config in ("VCB", "VCBB", "HCB"):
        return (f"{config} is an enclosed configuration — incident energy can run 2-3x "
                "an equivalent open-air (VOA/HOA) result for the same fault current, "
                "voltage, and gap. Confirm this classification before trusting the "
                "result; this is the single largest source of error in an arc-flash "
                "study.")
    return f"{config} is an open-air configuration."


def check_gap_range(gap_mm: float, voltage_class: str) -> bool:
    """True if gap_mm falls within IEEE 1584-2018's validated range for voltage_class
    ('lv' or 'mv'). A gap outside range means the model is being extrapolated beyond
    its validated basis — flag rather than apply silently."""
    lo, hi = VALID_GAP_RANGE_MM[voltage_class]
    return lo <= gap_mm <= hi


@dataclass
class ArcFlashCase:
    """
    One arcing-current case (average or minimum-current) at one bus, per IEEE
    1584-2018 Sec. 6.4 — both must be computed and compared, never only the average
    case, because a lower arcing current can produce a longer clearing time (device
    times out on its long-time element rather than the instantaneous pickup) and
    therefore a HIGHER incident energy than the average case.

    incident_energy_cal_cm2 and arcing_current_ka are supplied externally — see the
    module docstring. clearing_time_s must be read at THIS case's arcing current, not
    at the bolted fault current.
    """
    case_name: str  # "average" | "minimum"
    arcing_current_ka: float
    clearing_time_s: float
    incident_energy_cal_cm2: float
    working_distance_mm: float


@dataclass
class BusAssessment:
    bus: str
    electrode_config: str          # one of ELECTRODE_CONFIGS
    config_source: str             # "drawing" | "field-confirmed" | "conservative-default"
    bolted_i3p_ka: Optional[float] = None   # from ee-short-circuit — required
    bolted_islg_ka: Optional[float] = None
    cases: list = field(default_factory=list)  # list[ArcFlashCase]


def governing_case(bus: BusAssessment) -> ArcFlashCase:
    """
    Select the governing case per IEEE 1584-2018 Sec. 6.4 — the HIGHER incident energy
    of the average-arcing-current and minimum-arcing-current cases, never automatically
    the average case. Raises if both cases weren't actually supplied; silently
    defaulting to only the average case is the classic mistake this function exists to
    prevent.
    """
    case_names = {c.case_name for c in bus.cases}
    if not {"average", "minimum"}.issubset(case_names):
        raise ValueError(
            f"bus {bus.bus}: both 'average' and 'minimum' arcing-current cases are "
            f"required (IEEE 1584-2018 Sec. 6.4) — only found {sorted(case_names)}. A "
            "lower arcing current can produce a HIGHER incident energy if it falls "
            "below a breaker's instantaneous pickup; running only the average case can "
            "silently miss the worse outcome.")
    return max(bus.cases, key=lambda c: c.incident_energy_cal_cm2)


def assess_bus(bus: BusAssessment) -> dict:
    """
    Full per-bus assessment: governing case, PPE category (or control-required flag),
    electrode-config risk note, and traceability of the fault-current basis back to
    ee-short-circuit (never an assumed value).
    """
    if bus.bolted_i3p_ka is None:
        raise ValueError(
            f"bus {bus.bus}: no bolted fault current supplied. Run ee-short-circuit "
            "first — never assume or estimate a fault current for an arc-flash study.")
    gov = governing_case(bus)
    control_required = gov.incident_energy_cal_cm2 > NO_PRACTICAL_PPE_THRESHOLD_CAL_CM2
    result = {
        "bus": bus.bus,
        "electrode_config": bus.electrode_config,
        "config_source": bus.config_source,
        "config_risk_note": electrode_config_risk_note(bus.electrode_config),
        "governing_case": gov.case_name,
        "incident_energy_cal_cm2": gov.incident_energy_cal_cm2,
        "arcing_current_ka": gov.arcing_current_ka,
        "clearing_time_s": gov.clearing_time_s,
        "working_distance_mm": gov.working_distance_mm,
        "control_required": control_required,
        "ppe_category": None if control_required else ppe_category(gov.incident_energy_cal_cm2),
    }
    if control_required:
        result["control_note"] = (
            f"{gov.incident_energy_cal_cm2:.1f} cal/cm^2 exceeds "
            f"{NO_PRACTICAL_PPE_THRESHOLD_CAL_CM2} cal/cm^2 — no PPE category applies. "
            "Arc blast is a pressure/shrapnel hazard independent of the thermal one; the "
            "only correct control is de-energizing or engineering the energy down.")
    return result


def assessment_report(results: list) -> str:
    """
    Plain-text summary table: incident energy, governing case, PPE category (or
    control-required flag) per bus, and a rollup of buses needing a control other than
    PPE.
    """
    lines = []
    w = 100
    lines.append("=" * w)
    lines.append("ARC FLASH / INCIDENT ENERGY ASSESSMENT — PRELIMINARY, FOR PEE REVIEW")
    lines.append("=" * w)
    lines.append(f"{'BUS':14s}{'CONFIG':8s}{'GOVERNS':10s}{'IE cal/cm2':12s}{'PPE CAT':14s}NOTE")
    lines.append("-" * w)
    flagged = []
    for r in results:
        cat = "CONTROL REQ'D" if r["ppe_category"] is None else str(r["ppe_category"])
        note = "" if r["ppe_category"] is not None else "exceeds 40 cal/cm^2"
        lines.append(f"{r['bus']:14s}{r['electrode_config']:8s}{r['governing_case']:10s}"
                      f"{r['incident_energy_cal_cm2']:<12.2f}{cat:14s}{note}")
        if r["ppe_category"] is None:
            flagged.append(r["bus"])
    lines.append("-" * w)
    if flagged:
        lines.append(f"BUSES REQUIRING A CONTROL OTHER THAN PPE: {', '.join(flagged)}")
    lines.append("")
    lines.append("Incident energy for each bus is the HIGHER of the average- and minimum-")
    lines.append("arcing-current cases (IEEE 1584-2018 Sec. 6.4) — never the average case alone.")
    lines.append("Electrode configuration is the single largest source of error in this table;")
    lines.append("confirm every 'conservative-default' source against a drawing or field survey")
    lines.append("before this is issued.")
    lines.append("=" * w)
    return "\n".join(lines)
