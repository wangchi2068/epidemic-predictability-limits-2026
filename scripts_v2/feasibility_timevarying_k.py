# -*- coding: utf-8 -*-
"""Feasibility probe for the time-varying k_agg controlled experiment.

The paper's width-compensation diagnostic already reports the median width
multiplier the mechanistic predictor would need to reach nominal coverage:
  2.1--2.2x post-peak, 2.5--6.1x pre-peak.
For a location-scale-ish family, interval width scales like sd, so the
implied VARIANCE multiplier is the square.  This script asks: what k_agg
would be needed to produce that variance inflation at h=1, and is that
value physically plausible (compare with the micro k = 0.111--0.434)?
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")
ROOT = Path(__file__).resolve().parents[1]
J = lambda n: json.loads((ROOT / "reports_v3" / f"{n}.json").read_text(encoding="utf-8"))

SP = J("state_phases")
PHASES = [
    ("Delta", "COVID-19 Delta"), ("Omicron", "COVID-19 Omicron"),
    ("JN1", "COVID-19 JN.1"), ("flu22", "flu 2022-23"),
    ("flu24", "flu 2024-25"), ("rsv24", "RSV 2024-25"), ("rsv25", "RSV 2025-26"),
]


def cv2_macro_h1(R, k, I0):
    """Exact CV^2_macro at h=1 from the Theorem-2 closed form."""
    q = R * R * (1 + 1 / k)
    return (R / I0) * (q - R) / (R * R * (q - R)) + (1 + 1 / k) - 1


def p_exact(h, s):
    x = h * h * s * s
    return float(np.exp(2 * x) - 2 * np.exp(0.5 * x) + 1)


def solve_k_for_var_target(R, I0, s, target_var, h=1):
    """Find k_agg whose total h-step variance equals target_var."""
    from scipy.optimize import brentq
    f = lambda k: cv2_macro_h1(R, k, I0) + p_exact(h, s) - target_var
    # geometric term is decreasing in k; bracket widely
    try:
        return float(brentq(f, 1e-4, 1e6, xtol=1e-8))
    except ValueError:
        return float("nan")


print("=" * 92)
print("What k_agg would the pre-peak width compensation require?  (h = 1)")
print("=" * 92)
print(f"{'phase':16s} {'k_agg':>7s} {'var(h=1)':>10s} {'k@2.5x':>8s} {'k@6.1x':>8s} "
      f"{'k@2.15x':>8s}   verdict")

rows = []
for key, disp in PHASES:
    st = SP[key]["states"]
    med = {}
    for fld in ("k", "R_week", "I0", "s_week"):
        med[fld] = float(np.median([v[fld] for v in st.values()]))
    k0, R, I0, s = med["k"], med["R_week"], med["I0"], med["s_week"]
    v0 = cv2_macro_h1(R, k0, I0) + p_exact(1, s)
    # width multipliers -> variance multipliers
    k_pre_lo = solve_k_for_var_target(R, I0, s, v0 * 2.5 ** 2)
    k_pre_hi = solve_k_for_var_target(R, I0, s, v0 * 6.1 ** 2)
    k_post = solve_k_for_var_target(R, I0, s, v0 * 2.15 ** 2)
    rows.append((disp, k0, v0, k_pre_lo, k_pre_hi, k_post))
    print(f"{disp:16s} {k0:7.1f} {v0:10.5f} {k_pre_lo:8.2f} {k_pre_hi:8.2f} {k_post:8.2f}"
          f"   {'IN micro range' if k_pre_hi < 0.434 else 'above micro range'}")

print()
print("micro k (individual-level, Table 2): 0.111 -- 0.434")
print("macro k_agg (Table 3, medians):       11.2 -- 56.6")
print()
ks_pre_lo = [r[3] for r in rows]
ks_pre_hi = [r[4] for r in rows]
print(f"implied pre-peak k_agg range across phases: "
      f"{min(ks_pre_lo):.2f} -- {max(ks_pre_lo):.2f} (mild, 2.5x width)")
print(f"                                        {min(ks_pre_hi):.2f} -- {max(ks_pre_hi):.2f} "
      f"(severe, 6.1x width)")
print(f"implied post-peak k_agg (2.15x width):   "
      f"{min(r[5] for r in rows):.2f} -- {max(r[5] for r in rows):.2f}")

print()
print("=" * 92)
print("Interpretation")
print("=" * 92)
n_micro = sum(1 for r in rows if r[4] < 0.434)
print(f"phases whose severe pre-peak requirement lands inside the MICRO k range: "
      f"{n_micro}/7")
print("=> the experiment's predicted outcome is not absurd: a pre-peak k_agg of")
print("   order 1 (or lower) is a physically meaningful claim, and it is")
print("   FALSIFIABLE -- the state panel gives ~26-51 estimates per phase.")
