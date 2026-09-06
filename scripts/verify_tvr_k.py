"""Verify time-varying-R term (log-variance ~ h v^2 + demographic floor) and
estimate k from real weekly series by a moment estimator."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
rng = np.random.default_rng(20260807)


def renewal_tvR(T, R0, v, k, I0=100.0, g=(0.7, 0.3)):
    """Renewal with log R random walk (innovation sd v per week)."""
    logR = np.zeros(T + 2)
    logR[0] = np.log(R0)
    for t in range(1, T + 2):
        logR[t] = logR[t - 1] + rng.normal(0, v)
    I = np.zeros(T + 2)
    I[0] = I[1] = I0
    for t in range(2, T + 2):
        R = np.exp(logR[t])
        mean = R * (g[0] * I[t - 1] + g[1] * I[t - 2])
        I[t] = rng.negative_binomial(k, k / (k + mean)) if mean > 0 else 0.0
    return np.maximum(I[2:], 0), logR[2:]


def verify_tvR(R0, v, k, T, reps, h_max=8):
    """Optimal forecaster uses the unconditional mean R0; error = h v^2 + dem."""
    err2 = np.zeros(h_max + 1)
    cnt = np.zeros(h_max + 1)
    for r in range(reps):
        I, logR = renewal_tvR(T, R0, v, k)
        logc = np.log(I + 0.5)
        for t in range(8, T - h_max):
            mu = R0 ** np.arange(1, h_max + 1)
            pred = logc[t] + np.log(mu)
            e = (logc[t + 1:t + 1 + h_max] - pred) ** 2
            err2[1:h_max + 1] += e
            cnt[1:h_max + 1] += 1
    emp = err2 / np.maximum(cnt, 1)
    out = {}
    for h in range(1, h_max + 1):
        theory = h * v ** 2 + (1 / R0 + 1 / k) * R0 / ((R0 - 1) * 100.0)
        out[h] = {"emp_logvar": float(emp[h]), "theory_h_v2_plus_dem": float(theory),
                  "ratio": float(emp[h] / theory)}
    return out


def estimate_k_national(name, windows):
    if name == "covid":
        d = pd.read_csv(PROC / "covid_final_weekly.csv.gz", parse_dates=["week_end"])
        d = d[d.week_end >= "2020-08-01"]
    elif name == "rsv":
        d = pd.read_csv(PROC / "rsv_final_weekly.csv.gz", parse_dates=["week_end"])
    elif name == "flu":
        d = pd.read_csv(PROC / "flu_final_weekly.csv.gz", parse_dates=["week_end"])
    g = d.groupby("week_end")["value"].sum().sort_index()
    out = {}
    for w0, w1 in windows:
        seg = g[(g.index >= w0) & (g.index <= w1)]
        if len(seg) < 6:
            continue
        dlog = np.diff(np.log(seg.values + 0.5))
        m = np.mean(seg.values)
        var = np.var(dlog)
        k_hat = 1.0 / max(var - 1.0 / m, 1e-3)
        out[f"{w0}..{w1}"] = {"k_hat": float(k_hat), "var_dlog": float(var), "mean": float(m)}
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    tv = {}
    for v in [0.02, 0.05, 0.10]:
        tv[f"v{v}"] = verify_tvR(1.3, v, 1.0, 80, reps=600)
        print("tvR v=", v, json.dumps(tv[f"v{v}"]), flush=True)
    ke = {}
    wins = {"covid": [("2021-07-03", "2021-07-31"), ("2021-12-04", "2022-01-01"), ("2023-12-16", "2024-01-13")],
            "rsv": [("2024-11-09", "2024-12-07"), ("2025-11-08", "2025-12-06")],
            "flu": [("2022-10-08", "2022-11-05"), ("2024-11-23", "2024-12-21")]}
    for name, ws in wins.items():
        ke[name] = estimate_k_national(name, ws)
        print("k", name, json.dumps(ke[name]), flush=True)
    (REPORTS / "verify_tvr_and_k.json").write_text(json.dumps({"tvR": tv, "k_real": ke}, indent=2), encoding="utf-8")
    print("saved", flush=True)