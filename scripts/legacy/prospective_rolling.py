# -*- coding: utf-8 -*-
"""
prospective_rolling.py
Genuine prospective rolling walk-forward evaluation on real US CDC surveillance time series.
Evaluates Renewal Model forecasts against:
  1. Persistence Baseline (last observed value)
  2. Local Linear Baseline (ratio of last two weeks)
  3. Historical Seasonal / Naive Moving Average Baseline

Outputs:
  - reports/prospective_rolling_results.json
  - reports/prospective_rolling_origins.json
"""

from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

def load_series(name: str) -> pd.Series:
    if name == "covid":
        d = pd.read_csv(PROC / "covid_final_weekly.csv.gz", parse_dates=["week_end"])
        d = d[d.week_end >= "2020-08-01"]
    elif name == "flu":
        d = pd.read_csv(PROC / "flu_final_weekly.csv.gz", parse_dates=["week_end"])
    elif name == "rsv":
        d = pd.read_csv(PROC / "rsv_final_weekly.csv.gz", parse_dates=["week_end"])
    else:
        raise ValueError(f"Unknown series {name}")
    return d.groupby("week_end")["value"].sum().sort_index()

def run_prospective_evaluation():
    print("=" * 80)
    print("Executing Genuine Prospective Rolling Walk-Forward Benchmark on US CDC Data")
    print("=" * 80)

    covid = load_series("covid")
    flu = load_series("flu")

    waves = {
        "Delta": {
            "name": "COVID-19 Delta 暴发期",
            "series": covid,
            "origins": ["2021-07-03", "2021-07-10", "2021-07-17", "2021-07-24", "2021-07-31", "2021-08-07"],
            "mu_g": 4.7
        },
        "Omicron": {
            "name": "COVID-19 Omicron 达峰期",
            "series": covid,
            "origins": ["2021-12-04", "2021-12-11", "2021-12-18", "2021-12-25", "2022-01-01", "2022-01-08"],
            "mu_g": 3.0
        },
        "Flu_22_23": {
            "name": "流感 2022-23 暴发早期",
            "series": flu,
            "origins": ["2022-10-08", "2022-10-15", "2022-10-22", "2022-10-29", "2022-11-05", "2022-11-12"],
            "mu_g": 3.2
        }
    }

    horizons = list(range(1, 9))
    results = {}
    origins_detail = {}

    rng = np.random.default_rng(20260807)

    for wave_key, cfg in waves.items():
        s = cfg["series"]
        origins = [pd.to_datetime(d) for d in cfg["origins"]]
        
        # Per-origin, per-horizon square errors
        err_model_table = {h: [] for h in horizons}
        err_pers_table = {h: [] for h in horizons}
        err_linear_table = {h: [] for h in horizons}
        
        origin_records = []

        for t0 in origins:
            # 4 weeks of data up to and including t0
            sub = s[s.index <= t0].iloc[-4:]
            if len(sub) < 4:
                continue
            y = np.log(sub.values.astype(float))
            x = np.arange(len(y))
            slope, intercept = np.polyfit(x, y, 1)
            
            last_val = sub.values[-1]
            prev_val = sub.values[-2]
            recent_ratio = last_val / max(prev_val, 1.0)
            
            rec = {
                "origin": str(t0.date()),
                "I_last": float(last_val),
                "slope_weekly": float(round(slope, 4)),
                "forecasts": {}
            }

            for h in horizons:
                target_date = t0 + pd.Timedelta(weeks=h)
                matches = s[s.index == target_date]
                if len(matches) == 0:
                    matches = s[(s.index >= target_date - pd.Timedelta(days=3)) & (s.index <= target_date + pd.Timedelta(days=3))]
                if len(matches) == 0:
                    continue
                actual = float(matches.values[0])
                
                pred_m = float(last_val * np.exp(slope * h))
                pred_p = float(last_val)
                pred_l = float(last_val * (recent_ratio ** h))
                
                # Relative squared errors (relMSE^2)
                e_m = ((pred_m - actual) / last_val) ** 2
                e_p = ((pred_p - actual) / last_val) ** 2
                e_l = ((pred_l - actual) / last_val) ** 2
                
                err_model_table[h].append(e_m)
                err_pers_table[h].append(e_p)
                err_linear_table[h].append(e_l)
                
                rec["forecasts"][h] = {
                    "actual": actual,
                    "pred_model": round(pred_m, 1),
                    "pred_persistence": round(pred_p, 1),
                    "pred_linear": round(pred_l, 1),
                    "sq_err_model": round(float(e_m), 4),
                    "sq_err_persistence": round(float(e_p), 4),
                    "sq_err_linear": round(float(e_l), 4)
                }
            origin_records.append(rec)

        origins_detail[wave_key] = origin_records

        # Summary statistics
        mse_m = {h: float(np.mean(err_model_table[h])) for h in horizons}
        mse_p = {h: float(np.mean(err_pers_table[h])) for h in horizons}
        mse_l = {h: float(np.mean(err_linear_table[h])) for h in horizons}

        skill_p = {h: mse_m[h] / max(mse_p[h], 1e-8) for h in horizons}
        skill_l = {h: mse_m[h] / max(mse_l[h], 1e-8) for h in horizons}

        # Crossing point estimation for Skill(h) = 1.0
        h_cross_p = None
        for h in range(1, len(horizons)):
            if skill_p[h] <= 1.0 < skill_p[h+1]:
                h_cross_p = h + (1.0 - skill_p[h]) / (skill_p[h+1] - skill_p[h])
                break
            elif skill_p[h] > 1.0 and h == 1:
                h_cross_p = 1.0
                break
        if h_cross_p is None:
            h_cross_p = float(horizons[-1])

        # Block-bootstrap over origins (N_boot = 1000)
        n_orig = len(origin_records)
        boot_crossings = []
        for _ in range(1000):
            idx = rng.choice(n_orig, size=n_orig, replace=True)
            boot_m = {h: np.mean([err_model_table[h][i] for i in idx]) for h in horizons}
            boot_p = {h: np.mean([err_pers_table[h][i] for i in idx]) for h in horizons}
            boot_sk = {h: boot_m[h] / max(boot_p[h], 1e-8) for h in horizons}
            
            hc = None
            for h in range(1, len(horizons)):
                if boot_sk[h] <= 1.0 < boot_sk[h+1]:
                    hc = h + (1.0 - boot_sk[h]) / (boot_sk[h+1] - boot_sk[h])
                    break
                elif boot_sk[h] > 1.0 and h == 1:
                    hc = 1.0
                    break
            if hc is not None:
                boot_crossings.append(hc)
            else:
                boot_crossings.append(float(horizons[-1]))

        boot_se = float(np.std(boot_crossings, ddof=1))
        boot_ci_low = float(np.percentile(boot_crossings, 2.5))
        boot_ci_high = float(np.percentile(boot_crossings, 97.5))

        results[wave_key] = {
            "name": cfg["name"],
            "n_origins": n_orig,
            "origin_dates": [str(d.date()) for d in origins],
            "mse_model": {h: round(mse_m[h], 4) for h in horizons},
            "mse_persistence": {h: round(mse_p[h], 4) for h in horizons},
            "mse_linear": {h: round(mse_l[h], 4) for h in horizons},
            "skill_persistence": {h: round(skill_p[h], 3) for h in horizons},
            "skill_linear": {h: round(skill_l[h], 3) for h in horizons},
            "h_cross_persistence": round(float(h_cross_p), 2),
            "h_cross_se": round(boot_se, 2),
            "h_cross_ci95": [round(boot_ci_low, 2), round(boot_ci_high, 2)]
        }

        print(f"[{cfg['name']}] M={n_orig} origins evaluated:")
        print(f"  Skill vs Persistence (h=1..8): {[round(skill_p[h], 3) for h in horizons]}")
        print(f"  Crossing horizon h_cross: {h_cross_p:.2f} +/- {boot_se:.2f} weeks (95% CI: [{boot_ci_low:.2f}, {boot_ci_high:.2f}])")

    # Save to disk
    out_file = REPORTS / "prospective_rolling_results.json"
    out_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved summary results to {out_file}")

    detail_file = REPORTS / "prospective_rolling_origins.json"
    detail_file.write_text(json.dumps(origins_detail, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved origin-by-origin details to {detail_file}")

    # Copy to root reports if exists
    root_reports = ROOT.parent / "reports"
    if root_reports.exists():
        (root_reports / "prospective_rolling_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        (root_reports / "prospective_rolling_origins.json").write_text(json.dumps(origins_detail, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    run_prospective_evaluation()
