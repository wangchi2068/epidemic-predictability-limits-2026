# -*- coding: utf-8 -*-
"""Independent audit of specific claims in the journal manuscript.

Each check recomputes a number the paper states, from data in reports_v3/.
ASCII-only output so console encoding cannot mangle the results.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")
ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "reports_v3"

J = lambda n: json.loads((REP / n).read_text(encoding="utf-8"))


def cv2_macro(h, R, k, I0):
    q = R * R * (1 + 1 / k)
    return (R / I0) * (q ** h - R ** h) / (R ** (2 * h) * (q - R)) + (1 + 1 / k) ** h - 1


def p_exact(h, s):
    x = h * h * s * s
    return float(np.exp(2 * x) - 2 * np.exp(0.5 * x) + 1)


print("=" * 78)
print("CHECK 1  process-variance share at the horizon root (paper says 0.73--0.89)")
print("=" * 78)
sens = J("sensitivity_v4.json")
scen = J("scenarios.json")
SP = J("state_phases.json")
phases = ["Delta", "Omicron", "JN1", "flu22", "flu24", "rsv24", "rsv25"]
medians = {}
for ph in phases:
    h_star = scen[ph]["tiers"]["tau_0.50"]["median"]
    sr = SP[ph]["states"]
    shares = []
    for loc, v in sr.items():
        shares.append(cv2_macro(v["h_week"], v["R_week"], v["k"], v["I0"]) / 0.25)
    medians[ph] = float(np.median(shares))
    print(f"  {ph:8s} n={len(shares):3d}  median share = {medians[ph]:.4f}")
print(f"  -> range {min(medians.values()):.3f}--{max(medians.values()):.3f}")

print()
print("=" * 78)
print("CHECK 2  geometric share of tau^2 at the root (note 4 says 57.6%--82.2%)")
print("=" * 78)
for ph in phases:
    sr = SP[ph]["states"]
    geo = [((1 + 1 / v["k"]) ** v["h_week"] - 1) / 0.25 for v in sr.values()]
    print(f"  {ph:8s} geometric share median = {np.median(geo):.4f}")

print()
print("=" * 78)
print("CHECK 3  tau-tier table vs scenarios.json")
print("=" * 78)
tiers = {"tau_0.20": 0.20, "tau_0.35": 0.35, "tau_0.50": 0.50, "tau_0.70": 0.70}
lo, hi = {}, {}
for key, t in tiers.items():
    vals = [scen[ph]["tiers"][key]["median"] for ph in phases]
    lo[t] = min(vals); hi[t] = max(vals)
    print(f"  tau={t}: {min(vals):.2f}--{max(vals):.2f}  (paper table row)")
print("  tau=0.50 cross-phase range matches tab:horizons 5-week medians?")

print()
print("=" * 78)
print("CHECK 4  window envelope (paper says 1.52--8.07, -48.8%..+44.6%)")
print("=" * 78)
A = sens["A_kagg"]
allh, base = [], {}
for ph in phases:
    byw = A[ph]["median_h_by_window"]
    b = byw["5"]
    base[ph] = b
    vals = [byw["5"], byw["6"], byw["8"], byw["10"]]
    allh += vals
    ch = [(v / b - 1) * 100 for v in vals]
    print(f"  {ph:8s} base={b:5.2f}  changes% = " + " ".join(f"{c:+6.1f}" for c in ch))
print(f"  envelope = {min(allh):.2f}--{max(allh):.2f}")
print(f"  change range = {min((v/base[p]-1)*100 for p in phases for v in [A[p]['median_h_by_window'][w] for w in ['5','6','8','10']]):+.1f}%"
      f" .. {max((v/base[p]-1)*100 for p in phases for v in [A[p]['median_h_by_window'][w] for w in ['5','6','8','10']]):+.1f}%")

print()
print("=" * 78)
print("CHECK 5  alt variance calibers (paper: NB1 1.06--1.53x, Poisson 1.56--2.56x)")
print("=" * 78)
alt = J("alt_variance_calibers.json")
nb1, poi = [], []
for ph in phases:
    m = alt[ph]["median"]
    nb1.append(m["nb1"] / m["nb2"]); poi.append(m["poisson"] / m["nb2"])
    print(f"  {ph:8s} NB1/NB2 = {m['nb1']/m['nb2']:.3f}   Poisson/NB2 = {m['poisson']/m['nb2']:.3f}")
print(f"  -> NB1 {min(nb1):.2f}--{max(nb1):.2f}x ; Poisson {min(poi):.2f}--{max(poi):.2f}x")

print()
print("=" * 78)
print("CHECK 6  I0 sensitivity magnitude (paper §6.1 claims s and I0 both move)")
print("=" * 78)
i0 = J("i0_sensitivity.json")
for ph in phases:
    r = i0[ph]
    print(f"  {ph:8s} n={r['n']:3d} median%chg last={r['median_pct_change_last']:+6.2f}  "
          f"fitend={r['median_pct_change_fitend']:+6.2f}")

print()
print("=" * 78)
print("CHECK 7  skill_persistence crossing week (paper §6.1: 1.0--4.3 wk, 0.20--1.27x)")
print("=" * 78)
sr = J("state_rolling.json")
cross = {}
for ph in phases:
    per_state = []
    for loc, v in sr[ph]["states"].items():
        sp_ = v.get("skill_persistence") or {}
        for wk in sorted(sp_, key=lambda z: int(z)):
            if sp_[wk] >= 1.0:
                per_state.append(int(wk))
                break
    cross[ph] = float(np.median(per_state)) if per_state else float("nan")
    print(f"  {ph:8s} n={len(per_state):3d} median crossing week = {cross[ph]:.1f}")
print("  -> range", f"{min(cross.values()):.1f}--{max(cross.values()):.1f}")
