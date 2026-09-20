# -*- coding: utf-8 -*-
"""alt_variance_calibers.py — how much of the horizon is the variance *structure*?

The manuscript's headline horizon rests on a fixed-dispersion NB2 aggregate
update model, whose relative variance carries the geometric term
(1 + 1/k)^h.  Reviewer item W/C6 asks whether the reported horizons survive a
change of that structural assumption.  This script answers it on the same state
panel, the same 5-week windows and the same parameters:

  (1) NB2, fixed k            Var(Z_{t+1}|Z_t) = R Z_t + R^2 Z_t^2 / k      [main]
  (2) NB1 / quasi-Poisson     Var = phi R Z_t        (linear in the mean)
  (3) Poisson                 Var = R Z_t
  (4) micro Galton-Watson     the individual-level flat-k caliber at k = k_agg

For (2) phi is calibrated so that the one-step conditional variance at the
working point mu = I0 equals the NB2 one, i.e. phi = 1 + R I0 / k; this makes
the comparison structural rather than a change of scale.  (3) is (2) with
phi = 1.  Horizons are solved with the same tolerance tau = 0.5 and the same
parameter-extrapolation term P_exact(h) as the main caliber, so only the
process-variance structure differs.

For (2) and (3) the relative process variance is available in closed form and
* saturates*:
    CV^2_NB1(h) = phi / (I0 (R-1)) * (1 - R^{-h})
so if the saturation level sits below tau^2 the crossing is driven by the
parameter term alone and the horizon lengthens sharply.

Writes reports_v3/alt_variance_calibers.json and tables_v3/tab_alt_variance.tex.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts_v2"))

import macro_model
import state_panel_v3 as SP

REPORTS = ROOT / "reports_v3"
TABLES = ROOT / "tables_v3"
TAU = 0.5
PHASE_ORDER = ["Delta", "Omicron", "JN1", "flu22", "flu24", "rsv24", "rsv25"]


def p_exact(h, s):
    x2 = (np.asarray(h, dtype=float) * s) ** 2
    return np.exp(2.0 * x2) - 2.0 * np.exp(0.5 * x2) + 1.0


def cv2_nb1(h, R, phi, I0):
    """Saturating relative variance of the linear-overdispersion (NB1) update."""
    h = np.asarray(h, dtype=float)
    if R > 1.0:
        return phi * (1.0 - R ** (-h)) / (I0 * (R - 1.0))
    if abs(R - 1.0) < 1e-9:
        return phi * h / I0
    return phi * (R ** (-h) - 1.0) / (I0 * (1.0 - R))


def solve(f, hi_cap=1e6):
    if not np.isfinite(f(1e-3)) or f(1e-3) > 0:
        return None
    hi = 2.0
    while f(hi) < 0 and hi < hi_cap:
        hi *= 2.0
    if f(hi) < 0:
        return None
    return float(brentq(f, 1e-3, hi, xtol=1e-6))


def horizons_for_state(R, s, k, I0):
    """Return h* under the four variance structures."""
    phi = 1.0 + R * I0 / k
    out = {}
    out["nb2"] = solve(lambda h: float(macro_model.cv2_macro(h, R, k, I0))
                       + float(p_exact(h, s)) - TAU ** 2)
    out["nb1"] = solve(lambda h: float(cv2_nb1(h, R, phi, I0))
                       + float(p_exact(h, s)) - TAU ** 2)
    out["poisson"] = solve(lambda h: float(cv2_nb1(h, R, 1.0, I0))
                           + float(p_exact(h, s)) - TAU ** 2)
    out["micro"] = solve(lambda h: float(macro_model.cv2_micro(h, R, k, I0))
                         + float(p_exact(h, s)) - TAU ** 2)
    out["_saturation"] = {"nb2": float("inf"),
                          "nb1": phi / (I0 * (R - 1.0)) if R > 1 else float("inf"),
                          "poisson": 1.0 / (I0 * (R - 1.0)) if R > 1 else float("inf")}
    return out


def main() -> None:
    phases = json.loads((REPORTS / "state_phases.json").read_text(encoding="utf-8"))
    CAL = ["nb2", "nb1", "poisson", "micro"]
    out, table_rows = {}, []

    print(f"{'阶段':<10s} " + "".join(f"{c:>10s}" for c in CAL) + f"{'NB1饱和':>10s}")
    for key in PHASE_ORDER:
        rec = phases[key]
        vals = {c: [] for c in CAL}
        sat = []
        for v in rec["states"].values():
            R, s, k, I0 = v.get("R_week"), v.get("s_week"), v.get("k"), v.get("I0")
            if None in (R, s, k, I0):
                continue
            h = horizons_for_state(R, s, k, I0)
            for c in CAL:
                if h[c] is not None:
                    vals[c].append(h[c])
            if np.isfinite(h["_saturation"]["nb1"]):
                sat.append(h["_saturation"]["nb1"])
        med = {c: (float(np.median(vals[c])) if vals[c] else None) for c in CAL}
        out[key] = {
            "display": rec["display"],
            "n": len(vals["nb2"]),
            "median": med,
            "n_unbounded": {c: len(rec["states"]) - len(vals[c]) for c in CAL},
            "median_nb1_saturation": float(np.median(sat)) if sat else None,
        }
        d = rec["display"]
        row = f"{key:<10s} " + "".join(
            (f"{med[c]:10.2f}" if med[c] is not None else f"{'—':>10s}") for c in CAL)
        print(row + (f"{out[key]['median_nb1_saturation']:10.3f}"
                     if out[key]["median_nb1_saturation"] else f"{'—':>10s}"))
        table_rows.append((d, med, out[key]["median_nb1_saturation"]))

    # Table fragment
    lines = ["\\begin{tabular}{lcccc}", "\\toprule",
             "阶段 & NB2 固定 $k$ & NB1／准 Poisson & Poisson & 微观 GW 口径 \\\\",
             "\\midrule"]
    for d, med, sat in table_rows:
        cells = " & ".join(
            (f"{med[c]:.2f}" if med[c] is not None else "---") for c in CAL)
        lines.append(f"{d} & {cells} \\\\")
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\begin{flushleft}\\scriptsize \\textbf{注：}四种宏观方差结构均在相同 5 周推断窗口、相同参数集与 $\\tau=0.5$ 容错门槛下由各州独立求根后取中位数。NB1／准 Poisson 的过度离散系数校准为 $\\phi = 1 + R I_0 / k_{\\text{agg}}$，保证单步方差与 NB2 在工作点严格对齐以隔离纯结构效应。\\end{flushleft}"
    ]
    (TABLES / "tab_alt_variance.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    (REPORTS / "alt_variance_calibers.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\n[OK] reports_v3/alt_variance_calibers.json")
    print("[OK] tables_v3/tab_alt_variance.tex")


if __name__ == "__main__":
    main()
