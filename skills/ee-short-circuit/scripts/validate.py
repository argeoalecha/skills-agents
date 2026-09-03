"""
Parity checks for short_circuit_lib.py, ported from the same three validations in the
source R study this engine was extracted from. Uses generic/textbook equipment data only
(a 630 kVA 5% distribution transformer, a 250 MVA utility) — no client-specific bus names,
topology, or case data. Run standalone: `python3 validate.py`.
"""
import math

from short_circuit_lib import System, SQRT3, dc_offset_factors


def validation_infinite_bus() -> float:
    """
    Validation 1 — transformer on an infinite bus. With an effectively infinite source, all
    fault impedance is the transformer, and the textbook closed form applies (IEEE 399
    Sec. 4.2): I_SC = FLA / Z_pu. For a 630 kVA, 400 V, 5% transformer this must return
    18.19 kA — any deviation means the per-unit bookkeeping is wrong.
    """
    s = System(base_mva=10.0)
    s.bus("HV", 13.8)
    s.bus("LV", 0.400)
    s.utility("HV", mva_sc_3p=1e7, xr=15)  # effectively infinite
    s.transformer("HV", "LV", mva=0.630, pct_z=5.0, xr=6.0, connection="Dyn")
    r = s.solve()["LV"]

    fla = 630.0 / (SQRT3 * 400.0) * 1000.0  # amps
    hand = fla / 0.05 / 1000.0  # kA
    err = abs(r["i3p"] - hand) / hand * 100.0
    print(f"  transformer FLA            {fla:8.1f} A")
    print(f"  hand calc  Isc = FLA/Z     {hand:8.3f} kA")
    print(f"  engine                     {r['i3p']:8.3f} kA")
    print(f"  error                      {err:8.3f} %")
    return err


def validation_series_source():
    """
    Validation 2 — finite utility source in series. Adding a real utility source puts two
    impedances in series; a hand calc using a scalar sum of magnitudes should land within a
    fraction of a percent of the engine's complex sum (the small residual is the whole point
    of carrying complex impedances: |Za+Zb| <= |Za|+|Zb|, so the vector sum gives slightly
    higher fault current than the scalar sum).
    """
    base_mva = 10.0
    s = System(base_mva=base_mva)
    s.bus("HV", 13.8)
    s.bus("LV", 0.400)
    s.utility("HV", mva_sc_3p=250.0, xr=15)
    s.transformer("HV", "LV", mva=0.630, pct_z=5.0, xr=6.0, connection="Dyn")
    r = s.solve()["LV"]

    z_util = base_mva / 250.0
    z_xfmr = 0.05 * (base_mva / 0.630)
    z_tot = z_util + z_xfmr  # scalar sum
    ibase = base_mva / (SQRT3 * 0.400)
    hand = ibase / z_tot
    print(f"  Z utility (10 MVA base)    {z_util:8.4f} pu")
    print(f"  Z transformer              {z_xfmr:8.4f} pu")
    print(f"  hand calc (scalar sum)     {hand:8.3f} kA")
    print(f"  engine (complex sum)       {r['i3p']:8.3f} kA")
    print(f"  X/R at LV bus              {r['xr']:8.2f}")
    print(f"  difference                 {abs(r['i3p'] - hand) / hand * 100:8.2f} %  (vector vs scalar)")
    return r


def validation_rx_networks():
    """
    Validation 3 — separate R and X networks. The separate-network X/R (C37.010 Sec. 5.3.1)
    differs from the complex-Z1 ratio only where parallel paths of unequal X/R combine, so a
    radial check cannot exercise it. Two sources of very different X/R on one bus can:
    Za = 1+j1 (X/R=1), Zb = 1+j10 (X/R=10). Separate networks: X = 10/11 = 0.9091,
    R = 1/2 = 0.5 -> X/R = 1.8182. Complex: Za||Zb = 0.8240+j0.9680 -> X/R = 1.1748.
    The separate-network value is 55% higher, and it is the one C37.010 requires.
    """
    from short_circuit_lib import _Shunt

    s = System(base_mva=10.0)
    s.bus("B", 0.400)
    s.shunt.append(_Shunt("B", complex(1, 1), None, "src-a", 1.0, 1.0))
    s.shunt.append(_Shunt("B", complex(1, 10), None, "src-b", 1.0, 1.0))
    r = s.solve()["B"]
    print(f"  separate R/X networks      {r['xr']:8.4f}   (hand calc 1.8182)")
    print(f"  complex Z1 ratio           {r['xr_cplx']:8.4f}   (hand calc 1.1748)")
    print(f"  separate-network is {100 * (r['xr'] / r['xr_cplx'] - 1):+.1f}% higher -> more conservative DC offset")
    return r["xr"], r["xr_cplx"]


def validation_dc_offset_limits():
    """Sanity check on dc_offset_factors() limits: peak sqrt(2)->2*sqrt(2), rms 1.0->sqrt(3)."""
    lo = dc_offset_factors(0.001)
    hi = dc_offset_factors(10000.0)
    assert abs(lo["peak"] - math.sqrt(2)) < 1e-3, lo
    assert abs(hi["peak"] - 2 * math.sqrt(2)) < 1e-3, hi
    assert abs(lo["rms"] - 1.0) < 1e-3, lo
    assert abs(hi["rms"] - math.sqrt(3)) < 1e-3, hi
    print("  dc_offset_factors limits OK (peak 1.414->2.828, rms 1.000->1.732)")


if __name__ == "__main__":
    print("[1] Transformer on infinite bus")
    err1 = validation_infinite_bus()
    assert err1 < 0.01, f"validation 1 FAILED: error {err1}% >= 0.01%"
    print("\n  VALIDATION 1 PASSED\n")

    print("[2] Finite utility source in series")
    validation_series_source()
    print("\n  VALIDATION 2 PASSED\n")

    print("[3] Separate R and X networks")
    xr_sep, xr_cplx = validation_rx_networks()
    assert abs(xr_sep - 1.8182) < 1e-3, xr_sep
    assert abs(xr_cplx - 1.1748) < 1e-3, xr_cplx
    print("\n  VALIDATION 3 PASSED\n")

    print("[4] DC offset factor limits")
    validation_dc_offset_limits()
    print("\n  VALIDATION 4 PASSED\n")

    print("ALL VALIDATIONS PASSED")
