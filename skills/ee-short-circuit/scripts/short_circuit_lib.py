"""
Short-circuit fault-current engine — per-unit, symmetrical components, Zbus method.

Ported (engine only, no case data) from a validated R implementation built for a prior
campus power-system short-circuit study. Formulas are standard public-domain IEEE/ANSI
methodology:

  IEEE Std 3002.3-2018   overall method, source modelling, first-cycle network
  IEEE Std 399-1997      per-unit system, network reduction, Zbus formulation (Brown Book)
  ANSI/IEEE C37.010-1999 MV breaker duty basis, X/R multiplying factors
  ANSI/IEEE C37.13-2024  LV power circuit breaker duty basis, test power factor
  IEEE Std 242-2001      device protection/coordination, ground-fault duty (Buff Book)
  IEEE Std C57.12.00-2021 transformer impedance manufacturing tolerance (+-7.5%)
  J. L. Blackburn, Symmetrical Components for Power Systems Engineering (sequence networks)
  Grainger & Stevenson, Power System Analysis, Ch. 8, 10-12 (shunt-fault equations)

Table data (NEC Ch.9 conductor R/X, PEC ampacity tables) is NOT embedded here, same
convention as ee-load-calc/scripts/pec_calc_lib.py — copyrighted table values are supplied
as arguments from your own copy of the code/standard or a manufacturer datasheet, never
guessed or reproduced.

This engine solves bolted three-phase, single-line-to-ground (SLG), line-to-line (L-L),
and double-line-to-ground (LLG) fault duty at every bus simultaneously (one Zbus inversion
per network), plus ANSI C37.010 asymmetrical (peak/rms) duty and the C37.13 low-voltage X/R
adjustment for device duty checks.

It does NOT perform arc-flash incident-energy (IEEE 1584) calculations — see the
ee-arc-flash-calc skill, which consumes this engine's bolted-fault output as its required
input and must not be given an assumed or estimated fault current instead.

Verify all outputs against the current code edition and a certified equipment test report
before issuing a stamped deliverable.
"""
import cmath
import math
from dataclasses import dataclass
from typing import Optional

import numpy as np

SQRT3 = 3.0 ** 0.5
A120 = cmath.rect(1.0, 2 * cmath.pi / 3)  # a = 1<120 deg, symmetrical-component rotation operator


def zbase_ohm(kv: float, base_mva: float) -> float:
    """Base impedance in ohms. Z_base = kV^2 / MVA_base (IEEE 399 Sec. 3.3)."""
    return kv * kv / base_mva


def ibase_ka(kv: float, base_mva: float) -> float:
    """Base current in kA. I_base = MVA_base / (sqrt(3) * kV_base)."""
    return base_mva / (SQRT3 * kv)


def split_rx(z_mag: float, xr: float) -> complex:
    """
    Split |Z| into R + jX for a given X/R ratio.
    R = |Z| / sqrt(1 + (X/R)^2) ; X = (X/R) * R
    """
    r = z_mag / (1.0 + xr * xr) ** 0.5
    return complex(r, xr * r)


def cable_z(length_m: float, r_ohm_per_km: float, x_ohm_per_km: float, sets: int = 1,
            temp_c: float = 75.0, table_temp_c: float = 75.0,
            cu_temp_const: float = 234.5) -> complex:
    """
    Series impedance of a cable run, in ohms.

    r_ohm_per_km / x_ohm_per_km must come from a manufacturer datasheet or your own copy of
    NEC Ch.9 Table 9 / PEC conductor tables — not reproduced here (copyrighted table data,
    same convention as pec_calc_lib.py's "Inputs the library does not supply"). Applies the
    copper resistance temperature correction from the table's base temperature (NEC Ch.9
    Table 8 note; inferred-zero-resistance constant 234.5 degC for copper).
    """
    r = r_ohm_per_km * (cu_temp_const + temp_c) / (cu_temp_const + table_temp_c)
    return complex(r, x_ohm_per_km) * (length_m / 1000.0) / sets


def dc_offset_factors(xr: float) -> dict:
    """
    Peak and rms asymmetrical-duty multipliers for a given X/R (ANSI/IEEE C37.010-1999
    Sec. 5.4.2). Limits: peak sqrt(2) -> 2*sqrt(2) ; rms 1.0 -> sqrt(3).
    """
    mf_peak = 2.0 ** 0.5 * (1.0 + math.exp(-math.pi / xr))
    mf_rms = (1.0 + 2.0 * math.exp(-2.0 * math.pi / xr)) ** 0.5
    return {"peak": mf_peak, "rms": mf_rms}


# C37.010 rotating-machine multipliers on X"d, per duty network (Sec. 10.3 of the source
# study). None = machine omitted from that network entirely.
#                        first-cycle, interrupting
MOTOR_CLASS = {
    "lv_group":         (1.00, None),
    "small_lt50hp":     (1.67, None),
    "medium_50_1000hp": (1.20, 3.00),
    "large_ge1000hp":   (1.00, 1.50),
    "synchronous":      (1.00, 1.50),
}

# Standard test X/R implied by each standard's test power factor, X/R = sqrt(1-PF^2)/PF.
# ANSI/IEEE C37.13 for power circuit breakers, UL 489 / NEMA AB-1 for molded case.
LV_TEST_XR = {
    "lvpcb": 6.60,        # LV power circuit breaker (ACB), unfused  - 15% test PF
    "lvpcb_fused": 4.90,  # fused LVPCB                              - 20% test PF
    "iccb": 4.90,         # insulated-case circuit breaker           - 20% test PF
    "mccb_le10ka": 1.73,  # molded case, rating <= 10 kA             - 50% test PF
    "mccb_10_20ka": 3.18, # molded case, 10-20 kA                    - 30% test PF
    "mccb_gt20ka": 4.90,  # molded case, > 20 kA                     - 20% test PF
}


def lv_test_xr(dev_type: Optional[str], ka_rating: float) -> Optional[float]:
    """
    Standard test X/R for an LV device. "mccb" auto-selects the UL 489 band from the
    interrupting rating. Returns None for devices outside C37.13 scope (dev_type="mv").
    """
    if dev_type is None or dev_type == "mv":
        return None
    if dev_type == "mccb":
        if ka_rating <= 10.0:
            return LV_TEST_XR["mccb_le10ka"]
        if ka_rating <= 20.0:
            return LV_TEST_XR["mccb_10_20ka"]
        return LV_TEST_XR["mccb_gt20ka"]
    if dev_type not in LV_TEST_XR:
        raise ValueError(f"unknown device type {dev_type!r}; use 'mccb', 'mv', or one of: "
                          f"{', '.join(LV_TEST_XR)}")
    return LV_TEST_XR[dev_type]


def lv_adjust_mf(xr_sys: float, xr_test: Optional[float]) -> float:
    """
    C37.13 low-voltage X/R adjustment factor, peak basis:
      MF = (1 + e^(-pi/(X/R)_sys)) / (1 + e^(-pi/(X/R)_test))
    Clamped at 1.0 — no credit is taken when the system is softer than the test.
    """
    if xr_test is None:
        return 1.0
    return max(1.0, (1.0 + math.exp(-math.pi / xr_sys)) / (1.0 + math.exp(-math.pi / xr_test)))


@dataclass
class _Series:
    i: str
    j: str
    z1: Optional[complex]
    z0: Optional[complex]


@dataclass
class _Shunt:
    bus: str
    z1: Optional[complex]
    z0: Optional[complex]
    tag: str
    m_first: float
    m_int: Optional[float]


@dataclass
class _Device:
    label: str
    rating: float
    dev_type: str


class System:
    """
    Per-unit symmetrical-components short-circuit engine, Zbus method.

    Build with .bus() / .utility() / .generator() / .motor_group() / .transformer() /
    .cable() / .impedance() / .device(), then call .solve() for bolted-fault duty at every
    bus in one pass (one Zbus inversion per sequence network yields every bus's
    driving-point impedance simultaneously).
    """

    def __init__(self, base_mva: float = 10.0, prefault_pu: float = 1.0):
        self.base_mva = base_mva
        self.vpf = prefault_pu
        self.bus_kv: dict[str, float] = {}
        self.series: list[_Series] = []
        self.shunt: list[_Shunt] = []
        self.devices: dict[str, _Device] = {}

    # ---------- buses ----------
    def bus(self, name: str, kv: float) -> str:
        self.bus_kv[name] = kv
        return name

    def zbase(self, bus: str) -> float:
        return zbase_ohm(self.bus_kv[bus], self.base_mva)

    def ibase(self, bus: str) -> float:
        return ibase_ka(self.bus_kv[bus], self.base_mva)

    # ---------- sources ----------
    def utility(self, bus: str, mva_sc_3p: float, xr: float = 15.0,
                mva_sc_1p: Optional[float] = None):
        """Z1 = MVA_base / MVA_sc_3ph. Optional SLG MVA gives Z0 = 3*Z_1ph - 2*Z1."""
        z1 = split_rx(self.base_mva / mva_sc_3p, xr)
        if mva_sc_1p is not None and mva_sc_1p > 0:
            zt = self.base_mva / mva_sc_1p
            z0 = split_rx(max(3.0 * zt - 2.0 * abs(z1), 1e-6), xr)
        else:
            z0 = z1
        self.shunt.append(_Shunt(bus, z1, z0, "utility", 1.0, 1.0))

    def generator(self, bus: str, mva: float, xd2_pu: float, xr: float = 25.0,
                  x0_pu: Optional[float] = None, grounded: bool = True):
        """Z1 = Xd'' * MVA_base / MVA_gen (subtransient, first-cycle)."""
        z1 = split_rx(xd2_pu * self.base_mva / mva, xr)
        z0 = None
        if grounded:
            x0 = x0_pu if x0_pu is not None else 0.5 * xd2_pu
            z0 = split_rx(x0 * self.base_mva / mva, xr)
        self.shunt.append(_Shunt(bus, z1, z0, "generator", 1.0, 1.0))

    def motor_group(self, bus: str, kva_total: float, xd2_pu: float = 0.25, xr: float = 6.0,
                     mtr_class: str = "lv_group"):
        """
        Lumped first-cycle motor contribution. xd2_pu=0.25 (default, "lv_group" class) is
        the customary LV lumped-motor effective value, ~4x FLA — already an effective
        value, not a nameplate Xd''.
        """
        if kva_total <= 0:
            return
        if mtr_class not in MOTOR_CLASS:
            raise ValueError(f"unknown motor class {mtr_class!r}; use one of: "
                              f"{', '.join(MOTOR_CLASS)}")
        mva = kva_total / 1000.0
        if mva > 0.5 * self.base_mva:
            raise ValueError(
                f"motor group at {bus} is {mva:.1f} MVA, more than half the "
                f"{self.base_mva:.0f} MVA study base. kva_total is in kVA - did you mean "
                f"{kva_total / 1000:.0f}?")
        m_first, m_int = MOTOR_CLASS[mtr_class]
        z1 = split_rx(xd2_pu * self.base_mva / mva, xr)
        self.shunt.append(_Shunt(bus, z1, None, "motors", m_first, m_int))

    # ---------- series elements ----------
    def transformer(self, hv_bus: str, lv_bus: str, mva: float, pct_z: float, xr: float = 10.0,
                     connection: str = "Dyn", z0_ratio: float = 1.0, tol: float = 0.0,
                     zg_ohm: float = 0.0):
        """
        Impedance on the study base (IEEE 399 Sec. 3.4). tol=-0.075 for the maximum-fault
        case (IEEE C57.12.00 manufacturing tolerance, +-7.5%); +0.075 for a minimum-fault
        (protection pickup) study. zg_ohm = neutral grounding impedance on the LV side;
        enters the zero-sequence network as 3*Zg (3*I0 flows through it).

        Zero-sequence network by winding connection (Blackburn, Ch. 4):
          Dyn  (delta HV / wye-grounded LV) -> delta blocks Z0; LV winding is itself a Z0 source
          YNyn (both wye-grounded)          -> Z0 passes through as a series element
          Dd/Dy (ungrounded)                -> no LV zero-sequence path at all
        """
        zpu = (pct_z / 100.0) * (1.0 + tol) * (self.base_mva / mva)
        z1 = split_rx(zpu, xr)
        zt0 = z1 * z0_ratio
        if zg_ohm != 0:
            zt0 = zt0 + complex(3.0 * zg_ohm / self.zbase(lv_bus), 0)

        conn = connection.upper()
        if conn == "DYN":
            self.series.append(_Series(hv_bus, lv_bus, z1, None))
            self.shunt.append(_Shunt(lv_bus, None, zt0, "xfmr-z0", 1.0, 1.0))
        elif conn == "YNYN":
            self.series.append(_Series(hv_bus, lv_bus, z1, zt0))
        else:
            self.series.append(_Series(hv_bus, lv_bus, z1, None))

    def cable(self, bus_i: str, bus_j: str, z_ohm: complex, z0_mult: float = 3.0):
        """
        Series cable branch from a pre-computed run impedance (build z_ohm with cable_z()).
        Z0 of a cable run is taken as z0_mult x Z1 (typical 3x for conduit returns).
        """
        z1 = z_ohm / self.zbase(bus_j)
        self.series.append(_Series(bus_i, bus_j, z1, z1 * z0_mult))

    def impedance(self, bus_i: str, bus_j: str, z1_pu: complex, z0_pu: Optional[complex] = None):
        self.series.append(_Series(bus_i, bus_j, z1_pu, z0_pu))

    def device(self, bus: str, label: str, ka_rating: float, dev_type: str = "mccb"):
        """
        dev_type drives the C37.13 X/R adjustment (Sec. 12.1 of the source study).
        "mccb" auto-bands by rating; use "lvpcb" for an ACB, "mv" to disable the LV
        adjustment (MV breakers rated on C37.010 alone).
        """
        self.devices[bus] = _Device(label, ka_rating, dev_type)

    # ---------- internal: network solve ----------
    @staticmethod
    def _part(z: complex, part: str) -> complex:
        """part = 'complex' | 'X' | 'R'. 'X' zeroes every resistance and 'R' zeroes every
        reactance, giving the two auxiliary networks C37.010 Sec. 5.3.1 requires for X/R."""
        if part == "X":
            v = complex(0, z.imag)
        elif part == "R":
            v = complex(z.real, 0)
        else:
            return z
        if abs(v) < 1e-15:
            v = complex(1e-15, 0) if part == "R" else complex(0, 1e-15)
        return v

    def _zbus(self, sequence: int, network: str = "first", part: str = "complex"):
        names = list(self.bus_kv.keys())
        idx = {name: k for k, name in enumerate(names)}
        n = len(names)
        y = np.zeros((n, n), dtype=complex)

        for br in self.series:
            z = br.z1 if sequence == 1 else br.z0
            if z is None:
                continue
            z = self._part(z, part)
            a, b = idx[br.i], idx[br.j]
            adm = 1 / z
            y[a, a] += adm
            y[b, b] += adm
            y[a, b] -= adm
            y[b, a] -= adm

        for sh in self.shunt:
            m = sh.m_first if network == "first" else sh.m_int
            if m is None:  # machine omitted from this network (C37.010)
                continue
            z = sh.z1 if sequence == 1 else sh.z0
            if z is None:
                continue
            z = self._part(z * m, part)
            k = idx[sh.bus]
            y[k, k] += 1 / z

        # buses isolated in this sequence: park at a huge impedance so Y is invertible
        for k in range(n):
            if abs(y[k, k]) < 1e-12:
                y[k, k] = complex(1e-9, 0)

        return np.linalg.inv(y), idx

    # ---------- fault equations ----------
    def solve(self) -> dict:
        """
        Returns {bus_name: {...}} with bolted three-phase/SLG/L-L/LLG duty, ANSI C37.010
        asymmetrical (peak/rms) duty, the interrupting-network duty, and (where a device is
        attached) the C37.13 LV X/R-adjusted duty. One Zbus inversion per network yields
        every bus's driving-point impedance simultaneously (IEEE 399 Sec. 4.3).
        """
        z1b, idx = self._zbus(1, "first", "complex")
        z0b, _ = self._zbus(0, "first", "complex")
        zxb, _ = self._zbus(1, "first", "X")   # C37.010 Sec. 5.3.1 separate X network
        zrb, _ = self._zbus(1, "first", "R")   # C37.010 Sec. 5.3.1 separate R network
        z1i, _ = self._zbus(1, "int", "complex")
        z0i, _ = self._zbus(0, "int", "complex")
        zxi, _ = self._zbus(1, "int", "X")
        zri, _ = self._zbus(1, "int", "R")
        v = self.vpf
        out: dict = {}

        for name, k in idx.items():
            z1 = z1b[k, k]
            z2 = z1  # Z2 = Z1 assumption for static plant (IEEE 399 practice)
            z0 = z0b[k, k]
            ib = self.ibase(name)

            # three-phase (balanced) — positive sequence only
            i3p = v / z1 * ib

            # single line-to-ground — three sequence networks in series
            denom_slg = z1 + z2 + z0
            islg = 3.0 * v / denom_slg * ib if abs(denom_slg) > 1e-9 else complex(0, 0)

            # line-to-line — positive and negative in parallel opposition
            ill = SQRT3 * v / (z1 + z2) * ib

            # double line-to-ground — negative and zero in parallel, in series with positive
            denom_p = z2 + z0
            zp = z2 * z0 / denom_p if abs(denom_p) > 1e-12 else complex(0, 0)
            denom1 = z1 + zp
            ia1 = v / denom1 if abs(denom1) > 1e-12 else complex(0, 0)
            ia2 = -ia1 * z0 / denom_p if abs(denom_p) > 1e-12 else complex(0, 0)
            ia0 = -ia1 * z2 / denom_p if abs(denom_p) > 1e-12 else complex(0, 0)
            ib_ph = (ia0 + A120 ** 2 * ia1 + A120 * ia2) * ib
            ig_llg = 3.0 * ia0 * ib

            # C37.010 Sec. 5.3.1 — X/R from separate R-only and X-only networks, not the
            # complex Z1 ratio. Diverges from the complex ratio wherever parallel paths of
            # differing X/R combine, and is always the more conservative (larger) value there.
            xn, rn = zxb[k, k].imag, zrb[k, k].real
            xr = abs(xn / rn) if abs(rn) > 1e-12 else 999.0
            xr_cplx = abs(z1.imag / z1.real) if abs(z1.real) > 1e-12 else 999.0  # audit only
            mf = dc_offset_factors(xr)

            # C37.010 Sec. 10.3 interrupting-network duty (1.5-4 cycle; motors partly/wholly
            # decayed). Governs MV breakers rated on a symmetrical current basis; LV breakers
            # are rated on the first-cycle network per C37.13.
            z1n, z0n = z1i[k, k], z0i[k, k]
            i3p_int = v / z1n * ib
            den_i = z1n + z1n + z0n
            islg_int = 3.0 * v / den_i * ib if abs(den_i) > 1e-9 else complex(0, 0)
            xni, rni = zxi[k, k].imag, zri[k, k].real
            xr_int = abs(xni / rni) if abs(rni) > 1e-12 else 999.0

            # C37.13 low-voltage X/R adjustment — a breaker is only proven at its test X/R
            dev = self.devices.get(name)
            xr_test = lv_test_xr(dev.dev_type, dev.rating) if dev else None
            mf_lv = lv_adjust_mf(xr, xr_test)

            if abs(i3p) > 200.0 and self.bus_kv[name] < 1.0:
                raise ValueError(
                    f"implausible LV fault duty at {name}: {abs(i3p):.0f} kA. Check source "
                    f"and motor ratings - a units error in kVA vs MVA is the usual cause.")

            out[name] = {
                "kv": self.bus_kv[name], "z1": z1, "z0": z0,
                "i3p": abs(i3p), "islg": abs(islg), "ill": abs(ill),
                "illg": abs(ib_ph), "ig_llg": abs(ig_llg),
                "xr": xr, "xr_cplx": xr_cplx,
                "ipeak": abs(i3p) * mf["peak"], "irms_asym": abs(i3p) * mf["rms"],
                "i3p_int": abs(i3p_int), "islg_int": abs(islg_int), "xr_int": xr_int,
                "xr_test": xr_test, "mf_lv": mf_lv,
                "device": dev,
            }
        return out


def device_duty_check(res: dict) -> list[dict]:
    """
    Device duty check: rates against I_duty = max(I_3ph, I_SLG) x MF_lv (IEEE C37.010 for
    MV breakers, C37.13 for LV power breakers; MF_lv=1.0 where no device is attached at that
    bus, or where the system is softer than the device's test X/R). >100% = FAIL, >80% =
    MARGINAL (an engineering-practice margin, not a code limit). Checking three-phase duty
    alone is unsafe wherever Z0 < Z1 — flag SLG-governed buses for ground-fault/single-pole
    rating confirmation separately (IEEE 242 Sec. 9).
    """
    rows = []
    for name, r in res.items():
        dev = r["device"]
        if dev is None:
            continue
        i3p, islg = r["i3p"], r["islg"]
        governs = "SLG" if islg > i3p * 1.001 else "3PH"
        duty = max(i3p, islg) * r["mf_lv"]
        pct = duty / dev.rating * 100.0
        if pct > 100:
            verdict = "FAIL - exceeds rating"
        elif pct > 80:
            verdict = "MARGINAL - review"
        else:
            verdict = "pass"
        if governs == "SLG":
            verdict += " (check GF rating)"
        rows.append({
            "bus": name, "device": dev.label, "dev_type": dev.dev_type,
            "i3p_ka": i3p, "islg_ka": islg, "governs": governs,
            "mf_lv": r["mf_lv"], "duty_ka": duty, "rating_ka": dev.rating,
            "pct_used": pct, "verdict": verdict,
        })
    return rows


def to_rows(res: dict) -> list[dict]:
    """Flat rows for CSV export / tabular review."""
    rows = []
    for name, r in res.items():
        rows.append({
            "bus": name, "kv": r["kv"],
            "i3p_ka": round(r["i3p"], 3), "islg_ka": round(r["islg"], 3),
            "ill_ka": round(r["ill"], 3), "illg_ka": round(r["illg"], 3),
            "xr": round(r["xr"], 2), "xr_cplx": round(r["xr_cplx"], 2),
            "ipeak_ka": round(r["ipeak"], 3), "irms_asym_ka": round(r["irms_asym"], 3),
            "i3p_int_ka": round(r["i3p_int"], 3), "islg_int_ka": round(r["islg_int"], 3),
            "xr_int": round(r["xr_int"], 2),
            "xr_test": "" if r["xr_test"] is None else round(r["xr_test"], 2),
            "mf_lv": round(r["mf_lv"], 4),
            "adj_duty_ka": round(max(r["i3p"], r["islg"]) * r["mf_lv"], 3),
            "r1_pu": round(r["z1"].real, 5), "x1_pu": round(r["z1"].imag, 5),
        })
    return rows
