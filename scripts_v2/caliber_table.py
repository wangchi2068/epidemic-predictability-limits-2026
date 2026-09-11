# -*- coding: utf-8 -*-
"""caliber_table.py — seven-phase multi-calibre horizon comparison.

Reviewer item: the claim "all three calibres lie above the observed horizon" is
contradicted by the individual-k sensitivities.  This script computes, per
phase (state medians), the horizon under five calibres:

  (1) heuristic   : Lemma-2 CV^2 evaluated at k_agg  [current main calibre]
  (2) macro law   : the fixed-k_agg macro model's own leading-order law
                    CV^2_macro(h) = h / k_agg  (Corollary 4), solved jointly
                    with the parameter term
  (3) micro k     : Lemma-2 CV^2 at the individual-level k = 0.434 / 0.182 / 0.111
  (4) observed    : the absolute-error horizon (RelRMSE crossing tau) from the budget
  (5) persistence : the rolling crossing point vs the persistence baseline

and reports, per phase, whether each calibre exceeds the observed horizon.

Writes reports_v3/caliber_table.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports_v3"
TAU = 0.5
INDIV_K = {"k0.434": 0.434, "k0.182": 0.182, "k0.111": 0.111}


def p_lognorm(h, s):
    x2 = (np.asarray(h, dtype=float) * s) ** 2
    return np.exp(2.0 * x2) - 2.0 * np.exp(0.5 * x2) + 1.0


def solve(f, lo=1e-3):
    if f(lo) > 0:
        return None
    hi = 2.0
    while f(hi) < 0 and hi < 1e6:
        hi *= 2.0
    return brentq(f, lo, hi, xtol=1e-8)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    phases = json.loads((REPORTS / "state_phases.json").read_text(encoding="utf-8"))
    budget = json.loads((REPORTS / "budget_national.json").read_text(encoding="utf-8"))
    roll = json.loads((REPORTS / "rolling_bootstrap.json").read_text(encoding="utf-8"))

    out = {}
    for key, rec in phases.items():
        mu_g = rec["mu_g"]
        dg = mu_g / 7.0
        rows = []
        for loc, v in rec["states"].items():
            R, s_gen, k, I0 = v.get("R"), v.get("s"), v.get("k"), v.get("I0")
            if None in (R, s_gen, k, I0) or R <= 0 or I0 <= 0:
                continue
            s_week = s_gen / dg  # weekly-calibre SE for the scale-invariant P term

            def cv2_lemma(hw, kk):
                hg = hw / dg
                if R > 1:
                    return (1 + R / kk) * (1 - R ** (-hg)) / (I0 * (R - 1))
                return (1 + R / kk) * (R ** (-hg) - 1) / (I0 * (1 - R)) if abs(R - 1) > 1e-9 \
                    else (1 + 1 / kk) * hg / I0

            row = {}
            row["heuristic"] = solve(lambda hw: cv2_lemma(hw, k) + p_lognorm(hw, s_week) - TAU ** 2)
            row["macro"] = solve(lambda hw: hw / k + p_lognorm(hw, s_week) - TAU ** 2)
            for nm, kk in INDIV_K.items():
                row[nm] = solve(lambda hw, kk=kk: cv2_lemma(hw, kk) + p_lognorm(hw, s_week) - TAU ** 2)
            rows.append(row)

        def med(field):
            vals = [r[field] for r in rows if r.get(field)]
            return float(np.median(vals)) if vals else None

        obs = budget[key].get("obs_horizon_weeks")
        pers = (roll.get(key, {}).get("persistence") or {}).get("median_crossing")
        out[key] = {
            "display": rec["display"], "n_states": len(rows),
            "heuristic": med("heuristic"), "macro": med("macro"),
            **{nm: med(nm) for nm in INDIV_K},
            "observed": obs, "persistence": pers,
        }
        r = out[key]
        print(f"[{r['display']}] heur={r['heuristic']:.1f} macro={r['macro']:.1f} "
              f"k.434={r['k0.434']:.1f} k.182={r['k0.182']:.1f} k.111={r['k0.111']:.1f} "
              f"| obs={obs:.2f} pers={pers:.2f}")
        for nm in ["heuristic", "macro", "k0.434", "k0.182", "k0.111"]:
            v = r[nm]
            if v is not None and obs is not None:
                print(f"      {nm}: {v:.2f} vs obs {obs:.2f} -> "
                      f"{'ABOVE' if v >= obs else 'BELOW'}  "
                      f"(vs persistence {pers:.2f}: {'above' if v >= pers else 'BELOW'})")

    (REPORTS / "caliber_table.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nwrote reports_v3/caliber_table.json")


if __name__ == "__main__":
    main()
