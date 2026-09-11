# -*- coding: utf-8 -*-
"""sensitivity_v4.py — reviewer-requested sensitivities for the horizon model.

(A) k_agg estimation sensitivity: window length W in {5,6,8,10} and dispersion
    cap in {100,500,1000,inf}, and the resulting spread of the state-level
    median horizon.
(B) individual-k substitution: replace k_agg by the three measured individual
    dispersion values (0.434, 0.182, 0.111) and report the horizon change.
(D) weekly-vs-generation root finding: quantify the difference between
    (i) solving on the generation scale and converting via h_gen * mu_g/7,
    (ii) taking the largest integer number of weeks,
    (iii) the "naive" weekly-caliber solve that plugs the week count straight
         into the CV^2 formula without converting.

Writes reports_v3/sensitivity_v4.json and prints a compact summary.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts_v2"))
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


def h_week_from(R, s_week, k, I0, mu_g):
    """Solve on the generation scale, return continuous weeks."""
    dg = mu_g / 7.0
    s_gen = dg * s_week if False else None  # s already stored generation-scale below
    return None


def solve_gen(R, s_gen, k, I0):
    f = lambda h: sp.cv2(h, R, k, I0) + sp.p_lognorm(h, s_gen) - TAU ** 2
    if f(1e-3) > 0:
        return None
    hi = 2.0
    while f(hi) < 0 and hi < 1e6:
        hi *= 2.0
    return brentq(f, 1e-3, hi, xtol=1e-8)


def solve_naive_week(R, se_week, k, I0):
    """Wrong caliber: treat the week count as if it were the generation count."""
    f = lambda hw: sp.cv2(hw, R, k, I0) + sp.p_lognorm(hw, se_week) - TAU ** 2
    if f(1e-3) > 0:
        return None
    hi = 2.0
    while f(hi) < 0 and hi < 1e6:
        hi *= 2.0
    return brentq(f, 1e-3, hi, xtol=1e-8)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = {"A_kagg": {}, "B_individual_k": {}, "D_weekly_vs_gen": {}}

    for key, src, w0, w1, mu_g, disp in sp.PHASES:
        panel = load_panel(src)
        dg = mu_g / 7.0
        rows = []

        # --- A: window x cap sensitivity for k_agg, and horizon spread
        per_cap_h = {f"{c:g}": [] for c in K_CAPS}
        per_win_h = {w: [] for w in WINDOWS}
        for loc in sorted(STATE_FIPS):
            s = panel[panel.location == loc].set_index("week_end").value.sort_index()
            win5 = s[(s.index >= w0) & (s.index <= w1)]
            if len(win5) != 5 or win5.sum() < 50 or (win5.values <= 0).any():
                continue
            idx0 = list(s.index).index(win5.index[0])
            b, se_b, *_ = sp.fit_loglinear(np.log(win5.values.astype(float)))
            R = float(np.exp(dg * b))
            s_gen = float(dg * se_b)
            I0 = float(win5.mean())
            # cap sensitivity on the nominal W=5 window
            for c in K_CAPS:
                kk = k_from(win5.values.astype(float), cap=c)
                h = solve_gen(R, s_gen, kk, I0)
                if h is not None:
                    per_cap_h[f"{c:g}"].append(h * dg)
            # window sensitivity (extend the window forwards, keeping the fit)
            for w in WINDOWS:
                seg = s.iloc[idx0: idx0 + w]
                if len(seg) < w or (seg.values <= 0).any():
                    continue
                bb, seb, *_ = sp.fit_loglinear(np.log(seg.values.astype(float)))
                RR = float(np.exp(dg * bb))
                ss = float(dg * seb)
                II = float(seg.mean())
                kk = k_from(seg.values.astype(float), cap=1000.0)
                h = solve_gen(RR, ss, kk, II)
                if h is not None:
                    per_win_h[w].append(h * dg)
            rows.append((R, s_gen, k_from(win5.values.astype(float), 1000.0),
                         I0, se_b))

        out["A_kagg"][key] = {
            "median_h_by_cap": {c: (float(np.median(v)) if v else None)
                                for c, v in per_cap_h.items()},
            "median_h_by_window": {str(w): (float(np.median(v)) if v else None)
                                   for w, v in per_win_h.items()},
            "n": len(rows),
        }

        # --- B: substitute individual-level k
        b_h = {}
        for nm, kv in INDIV_K.items():
            hh = []
            for (R, s_gen, kk, I0, se_b) in rows:
                h = solve_gen(R, s_gen, kv, I0)
                if h is not None:
                    hh.append(h * dg)
            b_h[nm] = float(np.median(hh)) if hh else None
        hh0 = []
        for (R, s_gen, kk, I0, se_b) in rows:
            h = solve_gen(R, s_gen, kk, I0)
            if h is not None:
                hh0.append(h * dg)
        out["B_individual_k"][key] = {
            "median_h_with_kagg": float(np.median(hh0)) if hh0 else None,
            "median_h_with_individual_k": b_h,
        }

        # --- D: weekly vs generation caliber
        d_cont, d_int, d_naive = [], [], []
        for (R, s_gen, kk, I0, se_b) in rows:
            h = solve_gen(R, s_gen, kk, I0)
            if h is None:
                continue
            hw_cont = h * dg
            hw_int = float(np.floor(hw_cont))
            hn = solve_naive_week(R, se_b, kk, I0)
            d_cont.append(hw_cont)
            d_int.append(hw_int)
            if hn is not None:
                d_naive.append(hn)
        def _rel(a, b):
            if not a or not b:
                return None
            return float(np.median(np.abs(np.asarray(a) - np.asarray(b)) /
                                   np.asarray(a)) * 100)
        out["D_weekly_vs_gen"][key] = {
            "median_cont_weeks": float(np.median(d_cont)) if d_cont else None,
            "rel_diff_int_vs_cont_pct": _rel(d_cont, d_int),
            "median_naive_weeks": float(np.median(d_naive)) if d_naive else None,
            "rel_diff_naive_vs_cont_pct": _rel(d_cont, d_naive),
        }

        print(f"[{key:8s}] A caps:", {c: (None if v is None else round(v, 1))
                                     for c, v in out['A_kagg'][key]['median_h_by_cap'].items()})
        print(f"           A windows:", {w: (None if v is None else round(v, 1))
                                         for w, v in out['A_kagg'][key]['median_h_by_window'].items()})
        def fmt(v, nd=2):
            return 'NA' if v is None else f'{v:.{nd}f}'
        print(f"           B k_agg={fmt(out['B_individual_k'][key]['median_h_with_kagg'])} "
              f"-> " + " ".join(f"{n}={fmt(v)}" for n, v in b_h.items()))
        dd = out['D_weekly_vs_gen'][key]
        print(f"           D cont={fmt(dd['median_cont_weeks'])} "
              f"int_diff={fmt(dd['rel_diff_int_vs_cont_pct'],1)}% "
              f"naive={fmt(dd['median_naive_weeks'])} "
              f"naive_diff={fmt(dd['rel_diff_naive_vs_cont_pct'],1)}%")

    (REPORTS / "sensitivity_v4.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nwrote reports_v3/sensitivity_v4.json")


if __name__ == "__main__":
    main()
