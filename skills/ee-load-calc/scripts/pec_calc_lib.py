"""
PEC 2017-oriented electrical calc library.
Formulas are standard public-domain electrical engineering methods
(Ohm's law, point-to-point fault current, NEC/PEC-style continuous
load derating). Ampacity and demand factor TABLE VALUES are not
included here — pull those from your physical PEC 2017 copy and
enter them in reference/demand_factors.md, then feed as arguments.
Verify all outputs against the current code edition before issuing
a stamped deliverable.
"""
from dataclasses import dataclass
from typing import Literal

STANDARD_BREAKER_RATINGS_A = [15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80,
                               90, 100, 110, 125, 150, 175, 200, 225, 250,
                               300, 350, 400, 450, 500, 600, 700, 800, 1000,
                               1200, 1600, 2000]

@dataclass
class Load:
    id: str
    va: float
    continuous: bool = False
    demand_factor: float = 1.0

def demand_load_va(load: Load) -> float:
    return load.va * load.demand_factor

def min_conductor_ampacity(demand_va: float, voltage: float, phases: int,
                            continuous: bool) -> float:
    """125% derating on continuous loads per PEC Art. 2.15 / NEC 210.19(A)(1)."""
    if phases == 3:
        amps = demand_va / (voltage * 1.732)
    else:
        amps = demand_va / voltage
    return amps * 1.25 if continuous else amps

def select_breaker(min_amps: float) -> int:
    """Next standard breaker rating at or above the minimum required ampacity."""
    for rating in STANDARD_BREAKER_RATINGS_A:
        if rating >= min_amps:
            return rating
    raise ValueError(f"No standard breaker rating covers {min_amps:.1f}A — check load list.")

def voltage_drop_pct(amps: float, length_m: float, voltage: float,
                      resistance_ohm_per_km: float, phases: int,
                      reactance_ohm_per_km: float = 0.0,
                      power_factor: float = 1.0) -> float:
    """
    Approximate voltage drop % using conductor resistance (and optional
    reactance) per km. Get resistance/reactance from cable manufacturer
    datasheet or PEC conductor tables for the specific conductor size
    being checked — this function doesn't select the conductor for you.
    """
    length_km = length_m / 1000
    r = resistance_ohm_per_km * length_km
    x = reactance_ohm_per_km * length_km
    z_effective = r * power_factor + x * (1 - power_factor**2) ** 0.5
    multiplier = 1.732 if phases == 3 else 2
    vd = multiplier * amps * z_effective
    return (vd / voltage) * 100

def fault_current_point_to_point(source_kva: float, source_voltage: float,
                                  transformer_impedance_pct: float,
                                  cable_impedance_ohm: float = 0.0) -> float:
    """
    Simplified point-to-point available fault current at transformer
    secondary, ignoring downstream cable impedance if not provided.
    For coordination studies, chain this calc point-to-point through
    each cable segment per IEEE 242 methodology.
    """
    full_load_amps = source_kva * 1000 / (source_voltage * 1.732)
    if_transformer = full_load_amps / (transformer_impedance_pct / 100)
    if cable_impedance_ohm > 0:
        if_at_point = source_voltage / (1.732 * cable_impedance_ohm)
        return min(if_transformer, if_at_point)
    return if_transformer

def continuous_derating_check(operating_amps: float, breaker_rating: int) -> dict:
    pct = (operating_amps / breaker_rating) * 100
    return {"pct_of_rating": round(pct, 1), "flag": pct > 80}

if __name__ == "__main__":
    # Example usage — replace with real load list data per engagement
    load = Load(id="PANEL-A-L1", va=15000, continuous=True, demand_factor=1.0)
    demand = demand_load_va(load)
    min_amps = min_conductor_ampacity(demand, voltage=230, phases=1, continuous=True)
    breaker = select_breaker(min_amps)
    print(f"Demand load: {demand} VA")
    print(f"Min conductor ampacity (125% continuous): {min_amps:.1f} A")
    print(f"Selected breaker: {breaker} A")
    print(continuous_derating_check(min_amps, breaker))
