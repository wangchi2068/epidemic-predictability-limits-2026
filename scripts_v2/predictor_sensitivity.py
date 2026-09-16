# -*- coding: utf-8 -*-
"""predictor_sensitivity.py — how much does the mechanism horizon depend on the
forecast rule?

With log Rhat ~ N(log R, s^2):
  plug-in          Zhat = I0 Rhat^h
                   P_plug(h) = exp(2 x) - 2 exp(x/2) + 1,  x = (h s)^2
                   (carries a Jensen bias, E[Zhat] != I0 R^h)
  bias-corrected   Zhat = I0 exp(h log Rhat - x/2)
                   P_bc(h)   = exp(x) - 1                 (mean-unbiased)

Both closed forms are Monte-Carlo verified here, then used to solve
    cv2_macro(h, R_week, k_agg, I0) + P_rule(h, s_week) = tau^2
per state (weekly clock, tau = 0.5); cross-state medians are reported per phase.

Writes reports_v3/predictor_sensitivity.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts_v2"))
import macro_model  # noqa: E402

TAU = 0.5
SEED = 20260807


def p_plug(h, s):
    x = (np.asarray(h, dtype=float) * s) ** 2
    return np.exp(2.0 * x) - 2.0 * np.exp(0.5 * x) + 1.0


def p_bc(h, s):
    return np.exp((np.asarray(h, dtype=float) * s) ** 2) - 1.0


def verify(n=2_000_000):
    """Monte-Carlo check of both closed forms."""
    rng = np.random.default_rng(SEED)
    worst = {"plug": 0.0, "bc": 0.0}
    for s in (0.02, 0.05, 0.10):
        for R, I0 in ((1.2, 100.0), (1.4, 50.0)):
            logRh = np.log(R) + s * rng.standard_normal(n)
            for h in range(1, 11):
                Rh = np.exp(h * logRh)
                base = (I0 * R ** h) ** 2
                emp_plug = float(np.mean((I0 * Rh - I0 * R ** h) ** 2)) / base
                bcv = np.exp(h * logRh - 0.5 * (h * s) ** 2)
                emp_bc = float(np.mean((I0 * bcv - I0 * R ** h) ** 2)) / base
                worst["plug"] = max(worst["plug"],
                                    abs(emp_plug - float(p_plug(h, s))) / max(float(p_plug(h, s)), 1e-12))
                worst["bc"] = max(worst["bc"],
                                  abs(emp_bc - float(p_bc(h, s))) / max(float(p_bc(h, s)), 1e-12))
    return worst


def solve(R, k, I0, s, rule):
    f = lambda h: float(macro_model.cv2_macro(h, R, k, I0)) + rule(h, s) - TAU ** 2
    if not np.isfinite(f(1e-3)) or f(1e-3) > 0:
        return None
    hi = 2.0
    while f(hi) < 0 and hi < 1e6:
        hi *= 2.0
    return brentq(f, 1e-3, hi, xtol=1e-8)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    phases = json.loads((ROOT / "reports_v3" / "state_phases.json").read_text(encoding="utf-8"))
    worst = verify()
    out = {"mc_max_rel_deviation": worst, "phases": {}}
    for key, rec in phases.items():
        plug, bc, ratio = [], [], []
        for loc, s in rec["states"].items():
            a = solve(s["R_week"], s["k"], s["I0"], s["s_week"], p_plug)
            b = solve(s["R_week"], s["k"], s["I0"], s["s_week"], p_bc)
            if a is not None:
                plug.append(a)
            if b is not None:
                bc.append(b)
            if a and b:
                ratio.append(b / a)
        out["phases"][key] = {
            "display": rec["display"], "n": len(ratio),
            "median_plug": float(np.median(plug)) if plug else None,
            "median_bc": float(np.median(bc)) if bc else None,
            "median_bc_over_plug": float(np.median(ratio)) if ratio else None,
            "min_bc_over_plug": float(np.min(ratio)) if ratio else None,
            "max_bc_over_plug": float(np.max(ratio)) if ratio else None,
        }
        p = out["phases"][key]
        print(f"[{key:8}] plug={p['median_plug']:.2f} bc={p['median_bc']:.2f} "
              f"ratio={p['median_bc_over_plug']:.3f} "
              f"[{p['min_bc_over_plug']:.3f},{p['max_bc_over_plug']:.3f}] n={p['n']}")
    print("MC max rel dev:", worst)
    (ROOT / "reports_v3" / "predictor_sensitivity.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("wrote reports_v3/predictor_sensitivity.json")


if __name__ == "__main__":
    main()
