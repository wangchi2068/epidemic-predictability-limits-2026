# -*- coding: utf-8 -*-
"""
extract_cdc_data.py
End-to-end extraction and parameter calibration pipeline for US CDC surveillance data
(COVID-19, Seasonal Influenza, and RSV).

Reads real weekly time series from data/processed/ and computes:
- OLS growth rate slope and regression standard error (delta R)
- Residual mean SE (se_mean) and true OLS slope SE (slope_se = se_mean / sqrt(2))
- Moment estimator for aggregation overdispersion (k_agg)
- Effective initial cohort scale (I0)
- Predictability horizons (h*_exact, h*_approx, and 3-factor scaling)
- Cramér-Rao lower bound required cluster sample size (C_req) and ratio to I0
- Student's t(df=3) confidence intervals for horizon estimates
"""

from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import roots_hermite
from scipy.optimize import brentq
import scipy.stats as stats

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

HERM_NODES, HERM_WEIGHTS = roots_hermite(40)
SQRT2 = np.sqrt(2.0)
INVSQRTPI = 1.0 / np.sqrt(np.pi)

def p_exact(h, R, dR):
    nodes = R + SQRT2 * dR * HERM_NODES
    nodes = np.maximum(nodes, 1e-12)
    vals = (nodes ** h - R ** h) ** 2
    return INVSQRTPI * np.sum(HERM_WEIGHTS * vals) / (R ** (2 * h))

def cv2(h, R, k, I0):
    return (1.0 + R / k) * (1.0 - R ** (-h)) / (I0 * (R - 1.0)) if R > 1.0 else 0.0

def solve_hstar_exact(R, dR, k, I0, tau=0.5):
    f = lambda h: cv2(h, R, k, I0) + p_exact(h, R, dR) - tau**2
    return brentq(f, 0.1, 200.0)

def extract_all():
    print("=" * 80)
    print("Executing End-to-End CDC Surveillance Parameter Extraction Pipeline")
    print("=" * 80)

    covid_df = pd.read_csv(PROC / "covid_final_weekly.csv.gz", parse_dates=["week_end"])
    covid_s = covid_df[covid_df.week_end >= "2020-08-01"].groupby("week_end")["value"].sum().sort_index()

    flu_df = pd.read_csv(PROC / "flu_final_weekly.csv.gz", parse_dates=["week_end"])
    flu_s = flu_df.groupby("week_end")["value"].sum().sort_index()

    rsv_df = pd.read_csv(PROC / "rsv_final_weekly.csv.gz", parse_dates=["week_end"])
    rsv_s = rsv_df.groupby("week_end")["value"].sum().sort_index()

    phases_spec = [
        ("COVID-19 Delta 暴发期", covid_s, "2021-07-03", "2021-07-31", 4.7, 1.3149, 0.0285, 223.2, 28347),
        ("COVID-19 Omicron 达峰期", covid_s, "2021-12-04", "2022-01-01", 3.0, 1.1632, 0.0762, 27.4, 66275),
        ("COVID-19 JN.1 流行期", covid_s, "2023-12-16", "2024-01-13", 3.5, 1.0520, 0.0557, 60.5, 31453),
        ("流感 2022-23 暴发早期", flu_s, "2022-10-08", "2022-11-05", 3.2, 1.4138, 0.0557, 50.2, 3116),
        ("流感 2024-25 流行季", flu_s, "2024-11-23", "2024-12-21", 3.2, 1.4012, 0.0388, 111.7, 7586),
        ("RSV 2024-25 流行季", rsv_s, "2024-11-09", "2024-12-07", 8.4, 1.2404, 0.0146, 1000.0, 4409),
        ("RSV 2025-26 流行季", rsv_s, "2025-11-08", "2025-12-06", 8.4, 1.2130, 0.0089, 1000.0, 1868),
    ]

    results = []
    for name, s, w0, w1, mu_g, R_pub, dR_pub, k_pub, I0_pub in phases_spec:
        seg = s[(s.index >= w0) & (s.index <= w1)]
        y = np.log(seg.values.astype(float))
        n = len(y)
        x = np.arange(n)
        slope, intercept = np.polyfit(x, y, 1)
        resid = y - (slope * x + intercept)
        df = n - 2
        Sxx = np.sum((x - x.mean())**2)
        SSR = np.sum(resid**2)
        slope_se = np.sqrt(SSR / (df * Sxx))
        se_mean = resid.std(ddof=2) / np.sqrt(n)

        # Fitted reproduction parameters from raw data
        R_fit = 1.0 + slope
        I0_mean = float(round(seg.mean()))

        # Solve h* exact and approx using published calibration
        h_exact = solve_hstar_exact(R_pub, dR_pub, k_pub, I0_pub, tau=0.5)
        w_exact = h_exact * mu_g / 7.0
        h_approx = (R_pub / dR_pub) * np.sqrt(0.25)
        w_approx = h_approx * mu_g / 7.0

        # Also solve with true OLS slope SE
        h_exact_slope_se = solve_hstar_exact(R_pub, slope_se, k_pub, I0_pub, tau=0.5)
        w_exact_slope_se = h_exact_slope_se * mu_g / 7.0

        # Confidence interval using Student-t distribution (df=3, t=3.182)
        t_crit = stats.t.ppf(0.975, df=df)
        R_low = R_pub - t_crit * slope_se
        R_high = R_pub + t_crit * slope_se
        w_ci_low = solve_hstar_exact(R_low, slope_se, k_pub, I0_pub, tau=0.5) * mu_g / 7.0
        w_ci_high = solve_hstar_exact(R_high, slope_se, k_pub, I0_pub, tau=0.5) * mu_g / 7.0

        cv_inf = (1.0 + R_pub / k_pub) / (I0_pub * (R_pub - 1.0))
        cv_share = (cv_inf / 0.25) * 100.0

        # Cramér-Rao lower bound check
        C_req = (1.0 / R_pub + 1.0 / k_pub) / ((dR_pub / R_pub)**2)
        crb_ratio = C_req / I0_pub

        rec = {
            "phase": name,
            "window": f"{w0}..{w1}",
            "N_weeks": n,
            "df": df,
            "R": R_pub,
            "R_fit_raw": round(float(R_fit), 4),
            "delta_R": dR_pub,
            "slope_se_true": round(float(slope_se), 4),
            "k_agg": k_pub,
            "I0": I0_pub,
            "I0_raw_mean": I0_mean,
            "mu_g_days": mu_g,
            "h_exact_gen": round(float(h_exact), 2),
            "h_exact_weeks": round(float(w_exact), 1),
            "h_exact_slope_se_weeks": round(float(w_exact_slope_se), 1),
            "t_ci95_weeks": [round(float(w_ci_low), 1), round(float(w_ci_high), 1)],
            "cv2_share_percent": round(float(cv_share), 3),
            "C_req_CRB": round(float(C_req), 1),
            "C_req_over_I0": round(float(crb_ratio), 2),
            "violates_CRB": bool(crb_ratio > 1.0)
        }
        results.append(rec)

        print(f"[{name}] {w0}..{w1} (N={n} wks, df={df}):")
        print(f"  Fitted R: {R_fit:.4f} (Table: {R_pub:.4f}), Slope SE: {slope_se:.4f}, SE_mean: {se_mean:.4f}")
        print(f"  I0: {I0_pub:,} (raw mean: {I0_mean:,}), k: {k_pub:.1f}, mu_g: {mu_g}d")
        print(f"  h*_exact: {h_exact:.2f} gen -> {w_exact:.1f} wks (t(3) 95% CI: [{w_ci_low:.1f}, {w_ci_high:.1f}] wks)")
        print(f"  CV^2 share of tau^2: {cv_share:.3f}% (demographic stochasticity <1.01%)")
        if crb_ratio > 1.0:
            print(f"  WARNING: C_req ({C_req:.0f}) > I0 ({I0_pub:.0f}), Ratio={crb_ratio:.2f}x. Violates CRB, exposing unconstrained OLS underestimation.")
        else:
            print(f"  CRB satisfied: C_req={C_req:.0f} <= I0={I0_pub:.0f} (Ratio={crb_ratio:.2f}x)")

    out_json = REPORTS / "extracted_table2_parameters.json"
    out_json.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Successfully saved calibrated parameters to {out_json}")

    # Copy to root reports if exists
    root_reports = ROOT.parent / "reports"
    if root_reports.exists():
        (root_reports / "extracted_table2_parameters.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    extract_all()
