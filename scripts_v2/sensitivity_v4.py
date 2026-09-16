# -*- coding: utf-8 -*-
"""sensitivity_v4.py — sensitivities for the macro-exact horizon model.

The manuscript's primary state-level caliber is now the exact finite-step
relative variance of the fixed-k_agg macro negative-binomial update model on
the WEEKLY clock (macro_model.cv2_macro).  This script reports:

  (A) k_agg estimation sensitivity: window length W in {5,6,8,10} and
      dispersion cap in {100,500,1000,inf}, and the resulting spread of the
      state-level median horizon under the macro-exact caliber.
  (B) individual-k substitution: replace k_agg by the three measured
      individual dispersion values (0.434, 0.182, 0.111) inside the macro
      model, and report the horizon change.
  (C) caliber comparison: macro-exact vs its h/k_agg leading order vs the
      previous micro closed form evaluated at k_agg (generation clock).

Writes reports_v3/sensitivity_v4.json and prints a compact summary.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts_v2"))
import macro_model  # noqa: E402
import state_panel_v3 as sp  # noqa: E402

PANELS = ROOT / "data" / "panels"
REPORTS = ROOT / "reports_v3"
TAU = 0.5
STATE_FIPS = {f"{i:02d}" for i in range(1, 57)}
K_CAPS = [100.0, 500.0, 1000.0, float("inf")]
WINDOWS = [5, 6, 8, 10]
INDIV_K = {"HK_local": 0.434, "Ebola": 0.182, "HK_all": 0.111}


def load_panel(name):
    if name == "covid":
        d = pd.read_csv(PANELS / "covid_weekly_hospitalizations.csv.gz",
                        parse_dates=["week_end_date"])
        d = d.rename(columns={"week_end_date": "week_end",
                              "weekly_admissions": "value"})
    else:
        d = pd.read_csv(PANELS / f"{name}_weekly_hospitalizations.csv.gz",
                        parse_dates=["week_end"])
    d["location"] = d["location"].astype(str).str.zfill(2)
    return d


def k_from(counts, cap=1000.0):
    dlog = np.diff(np.log(counts))
    m = float(np.mean(counts))
    var = float(np.var(dlog, ddof=1))
    return float(min(1.0 / max(var - 1.0 / m, 1e-3), cap))


def _solve(f):
    if not np.isfinite(f(1e-3)) or f(1e-3) > 0:
        return None
    hi = 2.0
    while f(hi) < 0 and hi < 1e6:
        hi *= 2.0
    return brentq(f, 1e-3, hi, xtol=1e-8)


def solve_macro(R_w, s_w, k, I0):
    """Exact macro model, weekly clock (primary)."""
    return _solve(lambda h: float(macro_model.cv2_macro(h, R_w, k, I0))
                  + sp.p_lognorm(h, s_w) - TAU ** 2)


def solve_macro_lin(R_w, s_w, k, I0):
    """h/k_agg leading order of the macro model."""
    return _solve(lambda h: float(macro_model.cv2_macro_leading(h, R_w, k, I0))
                  + sp.p_lognorm(h, s_w) - TAU ** 2)


def solve_heur(R_g, s_g, k, I0):
    """Previous main caliber: micro closed form at k_agg, generation clock."""
    return _solve(lambda h: sp.cv2(h, R_g, k, I0) + sp.p_lognorm(h, s_g) - TAU ** 2)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = {"A_kagg": {}, "B_individual_k": {}, "C_caliber": {}}

    for key, src, w0, w1, mu_g, disp in sp.PHASES:
        panel = load_panel(src)
        dg = mu_g / 7.0
        rows = []

        per_cap_h = {f"{c:g}": [] for c in K_CAPS}
        per_win_h = {w: [] for w in WINDOWS}
        for loc in sorted(STATE_FIPS):
            s = panel[panel.location == loc].set_index("week_end").value.sort_index()
            win5 = s[(s.index >= w0) & (s.index <= w1)]
            if len(win5) != 5 or win5.sum() < 50 or (win5.values <= 0).any():
                continue
            idx0 = list(s.index).index(win5.index[0])
            b, se_b, *_ = sp.fit_loglinear(np.log(win5.values.astype(float)))
            R_w, s_w = float(np.exp(b)), float(se_b)
            I0 = float(win5.mean())
            for c in K_CAPS:
                kk = k_from(win5.values.astype(float), cap=c)
                h = solve_macro(R_w, s_w, kk, I0)
                if h is not None:
                    per_cap_h[f"{c:g}"].append(h)
            for w in WINDOWS:
                seg = s.iloc[idx0: idx0 + w]
                if len(seg) < w or (seg.values <= 0).any():
                    continue
                bb, seb, *_ = sp.fit_loglinear(np.log(seg.values.astype(float)))
                II = float(seg.mean())
                kk = k_from(seg.values.astype(float), cap=1000.0)
                h = solve_macro(float(np.exp(bb)), float(seb), kk, II)
                if h is not None:
                    per_win_h[w].append(h)
            rows.append((R_w, s_w, k_from(win5.values.astype(float), 1000.0),
                         I0, float(np.exp(dg * b)), float(dg * se_b)))

        out["A_kagg"][key] = {
            "median_h_by_cap": {c: (float(np.median(v)) if v else None)
                                for c, v in per_cap_h.items()},
            "median_h_by_window": {str(w): (float(np.median(v)) if v else None)
                                   for w, v in per_win_h.items()},
            "n": len(rows),
        }

        # --- B: substitute individual-level k into the micro closed form
        #        (scale-mapping sensitivity, matches the caliber-table columns)
        b_h = {}
        for nm, kv in INDIV_K.items():
            hh = [solve_heur(R_g, s_g, kv, I0) for (R_w, s_w, kk, I0, R_g, s_g) in rows]
            hh = [h * dg for h in hh if h is not None]
            b_h[nm] = float(np.median(hh)) if hh else None
        hh0 = [solve_heur(R_g, s_g, kk, I0) for (R_w, s_w, kk, I0, R_g, s_g) in rows]
        hh0 = [h * dg for h in hh0 if h is not None]
        out["B_individual_k"][key] = {
            "median_h_with_kagg": float(np.median(hh0)) if hh0 else None,
            "median_h_with_individual_k": b_h,
        }

        # --- C: caliber comparison (macro-exact / macro-leading / micro-heuristic)
        c_ex, c_lin, c_heur = [], [], []
        for (R_w, s_w, kk, I0, R_g, s_g) in rows:
            for acc, val in (
                (c_ex, solve_macro(R_w, s_w, kk, I0)),
                (c_lin, solve_macro_lin(R_w, s_w, kk, I0)),
            ):
                if val is not None:
                    acc.append(val)
            hh = solve_heur(R_g, s_g, kk, I0)
            if hh is not None:
                c_heur.append(hh * dg)

        def med(a):
            return float(np.median(a)) if a else None
        out["C_caliber"][key] = {
            "median_macro_exact": med(c_ex),
            "median_macro_leading": med(c_lin),
            "median_micro_heuristic": med(c_heur),
        }

        print(f"[{key:8s}] A caps:", {c: (None if v is None else round(v, 1))
                                     for c, v in out['A_kagg'][key]['median_h_by_cap'].items()})
        print(f"           A windows:", {w: (None if v is None else round(v, 1))
                                         for w, v in out['A_kagg'][key]['median_h_by_window'].items()})

        def fmt(v, nd=2):
            return 'NA' if v is None else f'{v:.{nd}f}'
        print(f"           B k_agg={fmt(out['B_individual_k'][key]['median_h_with_kagg'])} "
              f"-> " + " ".join(f"{n}={fmt(v)}" for n, v in b_h.items()))
        cc = out['C_caliber'][key]
        print(f"           C macro={fmt(cc['median_macro_exact'])} "
              f"lead={fmt(cc['median_macro_leading'])} heur={fmt(cc['median_micro_heuristic'])}")

    (REPORTS / "sensitivity_v4.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nwrote reports_v3/sensitivity_v4.json")


if __name__ == "__main__":
    main()
