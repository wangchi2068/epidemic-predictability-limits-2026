"""Action 1 v2: prospective validation of the volatility-adjusted horizon.
At T0 (lookback only): sigma_inc = SD of weekly log-increments; predict
log-error SD at horizon h = sqrt(h)*sigma_inc (random-walk drift model with
decomposed variance). Also report constant-R h* and its (failing) test."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
TAU = 0.5
LOOKBACK = 12


def load_national(name):
    if name == "covid":
        d = pd.read_csv(PROC / "covid_final_weekly.csv.gz", parse_dates=["week_end"])
        d = d[d.week_end >= "2020-08-01"]
    elif name == "rsv":
        d = pd.read_csv(PROC / "rsv_final_weekly.csv.gz", parse_dates=["week_end"])
    elif name == "flu":
        d = pd.read_csv(PROC / "flu_final_weekly.csv.gz", parse_dates=["week_end"])
    return d.groupby("week_end")["value"].sum().sort_index()


def run_prospective(name):
    counts = load_national(name)
    logc = np.log(counts.values + 0.5)
    T = len(logc)
    rows = []
    for t0 in range(LOOKBACK + 2, T - 12, 2):
        seg = logc[max(0, t0 - LOOKBACK):t0]
        if len(seg) < 8:
            continue
        inc = np.diff(seg)
        sigma_inc = inc.std(ddof=1)
        r_week = inc.mean()
        # volatility-adjusted horizon (weeks) at relative-error tau
        h_vol = (TAU / sigma_inc) ** 2
        # constant-R horizon (for reference)
        dlog = np.diff(logc[max(0, t0 - LOOKBACK):t0])
        m_eff = np.mean(np.exp(logc[max(0, t0 - LOOKBACK):t0]) - 0.5)
        k_hat = 1.0 / max(np.var(dlog) - 1.0 / m_eff, 1e-3)
        R = 1 + r_week
        se = inc.std(ddof=1) / np.sqrt(len(inc))
        noise2 = (1 + R / k_hat) / (m_eff * max(R - 1, 1e-6)) if R > 1 else np.inf
        disc = TAU ** 2 - noise2
        h_c = (R / max(se, 1e-6)) * np.sqrt(max(disc, 0)) if R > 1 and disc > 0 else 0.0
        for h in [1, 2, 4, 8]:
            if t0 + h >= T:
                continue
            pred = logc[t0] + r_week * h
            err = pred - logc[t0 + h]
            rows.append({"t0": t0, "h": h, "err": err, "sigma_inc": sigma_inc,
                         "h_vol": h_vol, "h_c": h_c})
    df = pd.DataFrame(rows)
    out = {"system": name}
    for h in [1, 2, 4, 8]:
        sub = df[df.h == h]
        if len(sub) < 10:
            continue
        emp_sd = sub.err.std()
        pred_sd = np.sqrt(h) * sub.sigma_inc.mean()
        ratio = emp_sd / pred_sd
        # bootstrap CI for ratio
        rng = np.random.default_rng(3)
        bs = []
        for _ in range(2000):
            idx = rng.integers(0, len(sub), len(sub))
            bs.append(sub.err.values[idx].std() / (np.sqrt(h) * sub.sigma_inc.values[idx].mean()))
        out[f"h{h}"] = {"emp_sd": float(emp_sd), "pred_sd_sqrt_h_sigma": float(pred_sd),
                        "ratio": float(ratio),
                        "ci": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))],
                        "n": int(len(sub))}
    out["h_vol_dist"] = {"median": float(np.median(df.h_vol)), "q25": float(np.quantile(df.h_vol, 0.25)),
                         "q75": float(np.quantile(df.h_vol, 0.75))}
    out["h_const_R_dist"] = {"median": float(np.median(df.h_c)), "q25": float(np.quantile(df.h_c, 0.25)),
                             "q75": float(np.quantile(df.h_c, 0.75))}
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    res = {}
    for name in ["covid", "rsv", "flu"]:
        r = run_prospective(name)
        res[name] = r
        print(name, json.dumps(r), flush=True)
    (REPORTS / "prospective_validation.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("saved", flush=True)