"""Real-data illustration: per-window horizon h* for COVID/RSV/Flu national
series + LightGBM forecaster error vs the theoretical log-SD bound."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
import lightgbm as lgb

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
rng = np.random.default_rng(20260807)

TAU = 0.5
K_ASSUME = {"covid": 0.3, "rsv": 1.0, "flu": 0.5}
K_REAL = json.loads((REPORTS / "k_real.json").read_text(encoding="utf-8")) if (REPORTS / "k_real.json").exists() else {}


def national_series(name):
    if name == "covid":
        d = pd.read_csv(PROC / "covid_final_weekly.csv.gz", parse_dates=["week_end"])
        d = d[d.week_end >= "2020-08-01"]
    elif name == "rsv":
        d = pd.read_csv(PROC / "rsv_final_weekly.csv.gz", parse_dates=["week_end"])
    elif name == "flu":
        d = pd.read_csv(PROC / "flu_final_weekly.csv.gz", parse_dates=["week_end"])
    g = d.groupby("week_end")["value"].sum().sort_index()
    return g


def horizon_at_window(counts, w0, w1, k):
    seg = counts[(counts.index >= w0) & (counts.index <= w1)]
    if len(seg) < 4:
        return None
    y = np.log(seg.values + 0.5)
    x = np.arange(len(y))
    beta = np.polyfit(x, y, 1)
    r_week = beta[0]
    resid = y - np.polyval(beta, x)
    se = resid.std(ddof=2) / np.sqrt(len(y))
    R = 1 + r_week            # R ~ 1 + weekly growth (serial interval ~ 1 wk)
    dR = se
    I_eff = np.mean(seg.values)
    noise2 = (1 + R / k) / (I_eff * max(R - 1, 1e-6))
    disc = TAU ** 2 - noise2
    h = (R / max(dR, 1e-6)) * np.sqrt(max(disc, 0)) if disc > 0 else 0.0
    return {"window": f"{w0.date()}..{w1.date()}", "R": float(R), "dR": float(dR),
            "I_eff": float(I_eff), "noise_floor_cv": float(np.sqrt(noise2)),
            "horizon_weeks_50pct": float(h), "predictable": bool(disc > 0)}


def ml_forecast_vs_bound(name):
    counts = national_series(name)
    logc = np.log(counts.values + 0.5)
    T = len(logc)
    n_lags = 8
    X, y, hcol = [], [], []
    for t in range(n_lags, T - 8):
        feat = list(logc[t - n_lags + 1:t + 1])
        for h in range(1, 9):
            X.append(feat + [h / 8]); y.append(logc[t + h]); hcol.append(h)
    X = np.array(X); y = np.array(y); hcol = np.array(hcol)
    split = int(0.7 * len(X))
    model = lgb.LGBMRegressor(n_estimators=200, learning_rate=0.05, num_leaves=15,
                              min_child_samples=10, verbosity=-1, n_jobs=4)
    model.fit(X[:split], y[:split])
    pred = model.predict(X[split:])
    out = {}
    for h in range(1, 9):
        mm = hcol[split:] == h
        rmse = float(np.sqrt(np.mean((pred[mm] - y[split:][mm]) ** 2)))
        out[h] = {"ml_log_rmse": rmse}
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    res = {}
    # 4-week onset windows (stylized illustration; see paper for caveats)
    windows = {
        "covid": [("2021-07-03", "2021-07-31"), ("2021-12-04", "2022-01-01"),
                  ("2022-01-08", "2022-02-05"), ("2023-12-16", "2024-01-13")],
        "rsv": [("2024-11-09", "2024-12-07"), ("2025-11-08", "2025-12-06")],
        "flu": [("2022-10-08", "2022-11-05"), ("2022-12-03", "2022-12-31"),
                ("2024-11-23", "2024-12-21")],
    }
    for name, ws in windows.items():
        counts = national_series(name)
        k = K_ASSUME[name]
        hw = []
        for a, b in ws:
            r = K_REAL.get(name, {}).get(f"{a}..{b}")
            kk = r["k_hat"] if r else k
            h = horizon_at_window(counts, pd.Timestamp(a), pd.Timestamp(b), kk)
            if h: h["k_used"] = kk
            hw.append(h)
        ml = ml_forecast_vs_bound(name)
        res[name] = {"windows": hw, "ml_vs_h": ml}
        print(name, json.dumps(hw, default=str), flush=True)
        print(name, "ML:", json.dumps(ml), flush=True)
    (REPORTS / "real_data_illustration.json").write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    print("saved", flush=True)