"""
Arc-flash workplace-safety workflow layer — governing-case selection, minimum arc-rated
PPE from incident energy, arc-flash-boundary and control-required flagging, per the
NFPA 70E (2024) incident energy analysis method and the IEEE 1584-2018 assessment process.

This module deliberately does NOT implement the IEEE 1584-2018 arcing-current or
incident-energy equations themselves. That calculation requires either a licensed
commercial tool (ETAP, SKM PowerTools, EasyPower, DIgSILENT PowerFactory) or a
documented independent implementation built directly against your own copy of IEEE
1584-2018 Section 4's equations and coefficient tables — the model's coefficients are
numerous, revised substantially between the 2002 and 2018 editions (results can nearly
double for the same equipment across that revision), and are not something to trust from
an LLM's training-data recall for a safety deliverable that determines what protective
equipment a worker relies on. Supply incident energy (cal/cm^2) per bus, per case,
computed externally; this module handles everything downstream of that number.

Incident energy analysis vs. PPE category method: NFPA 70E (2024) gives two separate PPE
selection methods — the incident energy analysis method (130.5(G)) and the PPE category
method (Table 130.7(C)(15)(c), driven by task/equipment tables, not by a calculated
energy). The standard does not permit using incident-energy results to pick a PPE
category, and both methods may not be applied to the same equipment. This module
implements the incident energy method only: the result is a minimum arc rating
(cal/cm^2) that the selected PPE must meet or exceed at the stated working distance.
Confirm clause numbers against the physical 2024 edition before citing them in a report.

The 1.2 cal/cm^2 arc-flash-boundary threshold, valid conductor-gap ranges, and typical
working distances below were taken from NFPA 70E (2024) / IEEE 1584-2018 as reproduced
in a governing procedure document for a prior campus engagement and cross-checked
against secondary reproductions of IEEE 1584-2018's typical working distance table.
"""
from dataclasses import dataclass, field
from typing import Optional

# NFPA 70E (2024) — onset of a second-degree burn; defines the arc flash boundary distance.
ARC_FLASH_BOUNDARY_THRESHOLD_CAL_CM2 = 1.2

# Engineering-practice threshold, not an NFPA 70E requirement: above this, arc blast
# becomes a pressure/shrapnel hazard independent of the thermal one, and the correct
# control is de-energizing or engineering the energy down — not a heavier suit.
CONTROL_REQUIRED_THRESHOLD_CAL_CM2 = 40.0

# IEEE 1584-2018 valid conductor-gap ranges, voltage-dependent. Do not apply the wrong
# band for the voltage class.
VALID_GAP_RANGE_MM = {
    "lv": (6.35, 76.2),     # 0.25-3 in, 208-600 V
    "mv": (19.05, 254.0),   # 0.75-10 in, 601 V - 15 kV
}

# IEEE 1584-2018 typical working distances by equipment class. These are defaults for
# when the actual task distance is unknown; use the real task distance where a worker's
# hands are closer than the convention assumes.
TYPICAL_WORKING_DISTANCE_MM = {
    "15kv_switchgear": 914,
    "15kv_mcc": 914,
    "5kv_switchgear": 914,
    "5kv_mcc": 914,
    "lv_switchgear": 610,
    "lv_mcc_panelboard": 455,
    "cable_junction_box": 455,
}

ELECTRODE_CONFIGS = {
    "VCB":  "Vertical conductors/electrodes in a metal box/enclosure",
    "VCBB": "Vertical conductors/electrodes in a metal box/enclosure with a barrier",
    "HCB":  "Horizontal conductors/electrodes in a metal box/enclosure",
    "VOA":  "Vertical conductors/electrodes in open air",
    "HOA":  "Horizontal conductors/electrodes in open air",
}


def typical_working_distance_mm(equipment_class: str) -> int:
    """IEEE 1584-2018 typical working distance for an equipment class key in
    TYPICAL_WORKING_DISTANCE_MM. Raises on an unknown class rather than guessing — a
    panelboard default applied to LV switchgear understates the distance's effect."""
    if equipment_class not in TYPICAL_WORKING_DISTANCE_MM:
        raise ValueError(f"unknown equipment class {equipment_class!r}; use one of: "
                         f"{', '.join(TYPICAL_WORKING_DISTANCE_MM)}")
    return TYPICAL_WORKING_DISTANCE_MM[equipment_class]


def minimum_arc_rating(incident_energy_cal_cm2: float) -> Optional[float]:
    """
    Incident energy analysis method: the arc rating of the selected PPE must be at least
    the incident energy at the working distance. Returns None below the 1.2 cal/cm^2
    arc-flash-boundary threshold (arc-rated PPE not triggered by the thermal hazard).
    Raises above the control-required threshold — that case is reported as a
    control-required finding, never as a PPE rating to buy.
    """
    if incident_energy_cal_cm2 > CONTROL_REQUIRED_THRESHOLD_CAL_CM2:
        raise ValueError(
            f"{incident_energy_cal_cm2:.2f} cal/cm^2 exceeds "
            f"{CONTROL_REQUIRED_THRESHOLD_CAL_CM2} cal/cm^2 — report as a control-required "
            "finding (de-energize or engineer the energy down), not a PPE arc rating.")
    if incident_energy_cal_cm2 < ARC_FLASH_BOUNDARY_THRESHOLD_CAL_CM2:
        return None
    return incident_energy_cal_cm2


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
    Full per-bus assessment: governing case, minimum arc rating (or control-required
    flag), electrode-config risk note, and traceability of the fault-current basis back
    to ee-short-circuit (never an assumed value).
    """
    if bus.bolted_i3p_ka is None:
        raise ValueError(
            f"bus {bus.bus}: no bolted fault current supplied. Run ee-short-circuit "
            "first — never assume or estimate a fault current for an arc-flash study.")
    gov = governing_case(bus)
    control_required = gov.incident_energy_cal_cm2 > CONTROL_REQUIRED_THRESHOLD_CAL_CM2
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
        "within_arc_flash_boundary": gov.incident_energy_cal_cm2 >= ARC_FLASH_BOUNDARY_THRESHOLD_CAL_CM2,
        "control_required": control_required,
        "min_arc_rating_cal_cm2": None if control_required else minimum_arc_rating(gov.incident_energy_cal_cm2),
    }
    if control_required:
        result["control_note"] = (
            f"{gov.incident_energy_cal_cm2:.1f} cal/cm^2 exceeds "
            f"{CONTROL_REQUIRED_THRESHOLD_CAL_CM2} cal/cm^2 — do not specify PPE for "
            "energized work. Arc blast is a pressure/shrapnel hazard independent of the "
            "thermal one; the only correct control is de-energizing or engineering the "
            "energy down.")
    return result


def assessment_report(results: list) -> str:
    """
    Plain-text summary table: incident energy, governing case, minimum arc rating (or
    control-required flag) per bus, and a rollup of buses needing a control other than
    PPE.
    """
    lines = []
    w = 100
    lines.append("=" * w)
    lines.append("ARC FLASH / INCIDENT ENERGY ASSESSMENT — PRELIMINARY, FOR PEE REVIEW")
    lines.append("=" * w)
    lines.append(f"{'BUS':14s}{'CONFIG':8s}{'GOVERNS':10s}{'IE cal/cm2':12s}{'MIN ARC RATING':16s}NOTE")
    lines.append("-" * w)
    flagged = []
    for r in results:
        if r["control_required"]:
            rating, note = "CONTROL REQ'D", f"exceeds {CONTROL_REQUIRED_THRESHOLD_CAL_CM2:.0f} cal/cm^2"
            flagged.append(r["bus"])
        elif r["min_arc_rating_cal_cm2"] is None:
            rating, note = "not triggered", "below 1.2 cal/cm^2"
        else:
            rating, note = f">= {r['min_arc_rating_cal_cm2']:.1f}", ""
        lines.append(f"{r['bus']:14s}{r['electrode_config']:8s}{r['governing_case']:10s}"
                      f"{r['incident_energy_cal_cm2']:<12.2f}{rating:16s}{note}")
    lines.append("-" * w)
    if flagged:
        lines.append(f"BUSES REQUIRING A CONTROL OTHER THAN PPE: {', '.join(flagged)}")
    lines.append("")
    lines.append("Incident energy for each bus is the HIGHER of the average- and minimum-")
    lines.append("arcing-current cases (IEEE 1584-2018 Sec. 6.4) — never the average case alone.")
    lines.append("PPE arc rating must meet or exceed the incident energy at the working distance")
    lines.append("(NFPA 70E incident energy analysis method). Do not convert these results into a")
    lines.append("PPE category — that is a separate method NFPA 70E does not permit mixing in.")
    lines.append("Electrode configuration is the single largest source of error in this table;")
    lines.append("confirm every 'conservative-default' source against a drawing or field survey")
    lines.append("before this is issued.")
    lines.append("=" * w)
    return "\n".join(lines)
