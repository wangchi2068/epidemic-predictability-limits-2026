"""Estimate k from real national weekly series (moment estimator)."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"


def estimate_k(w0, w1, name):
    if name == "covid":
        d = pd.read_csv(PROC / "covid_final_weekly.csv.gz", parse_dates=["week_end"])
        d = d[d.week_end >= "2020-08-01"]
    elif name == "rsv":
        d = pd.read_csv(PROC / "rsv_final_weekly.csv.gz", parse_dates=["week_end"])
    elif name == "flu":
        d = pd.read_csv(PROC / "flu_final_weekly.csv.gz", parse_dates=["week_end"])
    g = d.groupby("week_end")["value"].sum().sort_index()
    seg = g[(g.index >= w0) & (g.index <= w1)]
    if len(seg) < 4:
        return None
    dlog = np.diff(np.log(seg.values + 0.5))
    m = float(np.mean(seg.values))
    var = float(np.var(dlog))
    k_hat = 1.0 / max(var - 1.0 / m, 1e-3)
    return {"k_hat": k_hat, "var_dlog": var, "mean": m, "n": len(seg)}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    res = {}
    wins = {"covid": [("2021-07-03", "2021-07-31"), ("2021-12-04", "2022-01-01"), ("2023-12-16", "2024-01-13")],
            "rsv": [("2024-11-09", "2024-12-07"), ("2025-11-08", "2025-12-06")],
            "flu": [("2022-10-08", "2022-11-05"), ("2024-11-23", "2024-12-21")]}
    for name, ws in wins.items():
        res[name] = {}
        for a, b in ws:
            r = estimate_k(a, b, name)
            if r:
                res[name][f"{a}..{b}"] = r
                print(name, a, json.dumps(r), flush=True)
    (REPORTS / "k_real.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("saved", flush=True)