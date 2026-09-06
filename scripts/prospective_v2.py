"""Strengthened prospective validation: seasonal-corrected walk-forward forecaster;
full error model (demographic + parameter + R-fluctuation) predicts realised
log-variance; bootstrap CIs; sensitivity to k and window length."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
TAU = 0.5


def load_national(name):
    if name == "covid":
        d = pd.read_csv(PROC / "covid_final_weekly.csv.gz", parse_dates=["week_end"])
        d = d[d.week_end >= "2020-08-01"]
    elif name == "rsv":
        d = pd.read_csv(PROC / "rsv_final_weekly.csv.gz", parse_dates=["week_end"])
    elif name == "flu":
        d = pd.read_csv(PROC / "flu_final_weekly.csv.gz", parse_dates=["week_end"])
    return d.groupby("week_end")["value"].sum().sort_index()


def seasonal_means(logc, dates, up_to):
    """Calendar-week mean log count from data up to `up_to` (dates aligned to logc)."""
    df = pd.DataFrame({"logc": logc, "w": dates.isocalendar().week.astype(int).values,
                       "t": np.arange(len(logc))})
    past = df[df.t < up_to]
    m = past.groupby("w")["logc"].mean()
    full = np.array([m.get(w, np.nanmean(past.logc)) for w in range(1, 53)])
    ext = np.concatenate([full[-2:], full, full[:2]])
    return np.convolve(ext, np.ones(5) / 5, mode="valid")


def run_system(name, lookback=12, k_fixed=None):
    counts = load_national(name)
    logc = np.log(counts.values + 0.5)
    dates = counts.index
    T = len(logc)
    rows = []
    for t0 in range(lookback + 4, T - 12 - 2, 2):
        seg = counts.iloc[t0 - lookback:t0]
        if len(seg) < 8:
            continue
        y = logc[t0 - lookback:t0]
        inc = np.diff(y)
        r_hat = inc.mean()
        dR = inc.std(ddof=1) / np.sqrt(len(inc))
        m_bar = seg.mean()
        k_hat = k_fixed if k_fixed else 1.0 / max(np.var(inc) - 1.0 / m_bar, 1e-3)
        v_hat = pd.Series(inc).rolling(4).mean().dropna().std()
        s = seasonal_means(logc, dates, t0)
        sw = s[(dates.isocalendar().week.astype(int).values) % 52]  # placeholder
        for h in [1, 2, 4, 8]:
            if t0 + h >= T:
                continue
            w0 = (dates[t0].isocalendar().week - 1) % 52
            w1 = (dates[t0 + h].isocalendar().week - 1) % 52
            pred = y[-1] + r_hat * h + (s[w1] - s[w0])
            err = pred - logc[t0 + h]
            dem = h * (1.0 / k_hat + 1.0 / m_bar)
            R_est = 1 + r_hat
            param = (h * dR / R_est) ** 2 if abs(R_est) > 1e-6 else 0.0
            rfl = h * (v_hat ** 2)
            pred_var = dem + param + rfl
            rows.append({"h": h, "err2": err ** 2, "pred_var": pred_var,
                         "dem": dem, "param": param, "rfl": rfl,
                         "k_hat": k_hat, "m_bar": m_bar, "v_hat": v_hat})
    df = pd.DataFrame(rows)
    out = {}
    for h in [1, 2, 4, 8]:
        sub = df[df.h == h]
        if len(sub) < 15:
            continue
        real = sub.err2.mean()
        pred = sub.pred_var.mean()
        ratio = real / pred
        rng = np.random.default_rng(9)
        bs = [sub.err2.sample(n=len(sub), replace=True).mean() / sub.pred_var.mean() for _ in range(2000)]
        out[str(h)] = {"n": int(len(sub)), "realised_var": float(real),
                       "predicted_var": float(pred), "ratio": float(ratio),
                       "ci": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))],
                       "share_dem": float(sub.dem.mean() / sub.pred_var.mean()),
                       "share_param": float(sub.param.mean() / sub.pred_var.mean()),
                       "share_rfl": float(sub.rfl.mean() / sub.pred_var.mean())}
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    res = {}
    for name in ["covid", "rsv", "flu"]:
        res[name] = {"default": run_system(name),
                     "k_fixed_0_5": run_system(name, k_fixed=0.5),
                     "k_fixed_5": run_system(name, k_fixed=5.0),
                     "window_8": run_system(name, lookback=8),
                     "window_16": run_system(name, lookback=16)}
        print(name, json.dumps(res[name]["default"]), flush=True)
        print(name, "sensitivity h=4:", {k2: res[name][k2].get("4", {}).get("ratio") for k2 in res[name]}, flush=True)
    (REPORTS / "prospective_v2.json").write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    print("saved", flush=True)