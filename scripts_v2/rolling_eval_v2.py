# -*- coding: utf-8 -*-
"""
rolling_eval_v2.py — Pseudo-prospective rolling walk-forward evaluation (Table 5 / Figure 7).

Protocol (matches the manuscript description exactly):
  * Origins: 6 consecutive weekly origins per wave (documented per origin).
  * Inference window: the W = 4 weeks ending at the origin (inclusive).
  * Model: renewal-type exponential extrapolation
        Zhat_{t+h} = Z_t * exp(b_t * h)        (b_t = 4-week OLS log-slope),
    i.e. the weekly-scale counterpart of the Table-2 model (whose generation-scale
    root is converted back to weeks).
  * Baselines:
      1. Persistence: Zhat = Z_t.
      2. Local linear: Zhat = Z_t * (Z_t / Z_{t-1})^h.
      3. Seasonal naive: Zhat = value from the same week of the previous analogous
         period (for flu/RSV: same week of the previous season; for the COVID waves:
         the value 52 weeks earlier, which is outside the evaluated windows' rapid
         growth and therefore documented as an explicitly weak reference).
  * Horizons: h = 1..8 weeks.
  * Dependence-aware uncertainty: MOVING-BLOCK bootstrap over the origin sequence
    (block length 3, 6 origins, circular wrap), 1000 resamples, seed 20260807.
    Adjacent origins share overlapping future targets, so iid resampling would
    understate uncertainty; the moving-block scheme preserves local dependence.
  * Crossing point h_cross: linear interpolation of Skill(h) through 1.0 between
    adjacent integer horizons; percentile CI from the bootstrap.

Outputs: reports/rolling_results.json, reports/figures_v2/fig7_skill_decay.png
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
FIGS = REPORTS / "figures_v2"
FIGS.mkdir(parents=True, exist_ok=True)

SEED = 20260807
B_BOOT = 1000
BLOCK_LEN = 3
HORIZONS = list(range(1, 9))

WAVES = {
    "Delta": {
        "series": "covid", "mu_g": 4.7,
        "origins": ["2021-07-03", "2021-07-10", "2021-07-17",
                    "2021-07-24", "2021-07-31", "2021-08-07"],
        "t2_key": "Delta",
    },
    "Omicron": {
        "series": "covid", "mu_g": 3.0,
        "origins": ["2021-12-04", "2021-12-11", "2021-12-18",
                    "2021-12-25", "2022-01-01", "2022-01-08"],
        "t2_key": "Omicron",
    },
    "Flu_22_23": {
        "series": "flu", "mu_g": 3.2,
        "origins": ["2022-10-08", "2022-10-15", "2022-10-22",
                    "2022-10-29", "2022-11-05", "2022-11-12"],
        "t2_key": "flu22",
    },
}


def load_series(name):
    d = pd.read_csv(PROC / f"{name}_final_weekly.csv.gz", parse_dates=["week_end"])
    if name == "covid":
        d = d[d.week_end >= "2020-08-01"]
    return d.groupby("week_end")["value"].sum().sort_index()


def fit4(y):
    x = np.arange(len(y), dtype=float)
    A = np.vstack([x, np.ones(len(y))]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(coef[0])


def cross_point(skill):
    """Linear-interpolated crossing of 1.0; None if never crosses."""
    for i in range(len(skill) - 1):
        h0, h1 = HORIZONS[i], HORIZONS[i + 1]
        s0, s1 = skill[i], skill[i + 1]
        if s0 <= 1.0 < s1:
            return h0 + (1.0 - s0) / (s1 - s0)
    return None


def run_wave(w, s, cfg):
    origins = [pd.to_datetime(o) for o in cfg["origins"]]
    errs = {m: {h: [] for h in HORIZONS} for m in ["model", "pers", "lin", "seas"]}
    per_origin = []
    for t0 in origins:
        hist = s[s.index <= t0]
        if len(hist) < 5:
            continue
        win = hist.iloc[-4:]
        b_t = fit4(np.log(win.values.astype(float)))
        z_t = float(win.values[-1])
        z_prev = float(win.values[-2])
        ratio = z_t / max(z_prev, 1.0)
        rec = {"origin": str(t0.date()), "Z_t": z_t, "b_t": round(b_t, 4), "fc": {}}
        for h in HORIZONS:
            tgt = t0 + pd.Timedelta(weeks=h)
            idx = s.index.get_indexer([tgt], method="nearest")
            if abs((s.index[idx[0]] - tgt).days) > 3:
                continue
            actual = float(s.values[idx[0]])
            seas_tgt = tgt - pd.Timedelta(weeks=52)
            j = s.index.get_indexer([seas_tgt], method="nearest")
            seas_val = float(s.values[j[0]]) if abs((s.index[j[0]] - seas_tgt).days) <= 3 else np.nan
            pred = {
                "model": z_t * np.exp(b_t * h),
                "pers": z_t,
                "lin": z_t * ratio ** h,
                "seas": seas_val,
            }
            for m, v in pred.items():
                errs[m][h].append(((v - actual) / z_t) ** 2 if np.isfinite(v) else np.nan)
            rec["fc"][h] = {"actual": actual, **{m: round(v, 1) for m, v in pred.items()}}
        per_origin.append(rec)

    n = len(per_origin)
    mse = {m: {h: float(np.nanmean(errs[m][h])) if np.any(np.isfinite(errs[m][h])) else np.nan
               for h in HORIZONS} for m in errs}
    skill = {m: [mse["model"][h] / mse[m][h] if mse[m][h] > 0 else np.nan
                 for h in HORIZONS] for m in ["pers", "lin", "seas"]}

    # ---- moving-block bootstrap over origins ----
    # error matrix: method x horizon x origin; seasonal may hold NaN (missing lag for
    # series shorter than 52 weeks), so the bootstrap gate only requires the methods
    # being resampled (model/pers/lin) to be finite.
    err_arr = {m: {h: np.array(errs[m][h], dtype=float) for h in HORIZONS} for m in errs}
    n = len(per_origin)
    rng = np.random.default_rng(SEED)
    boot_cross = {"pers": [], "lin": []}
    for _ in range(B_BOOT):
        starts = rng.integers(0, n, size=n)
        idx = [(start + d) % n for start in starts for d in range(BLOCK_LEN)][:n]
        bm = {}
        ok = True
        for m in ["model", "pers", "lin"]:
            bm[m] = {}
            for i in range(len(HORIZONS)):
                v = err_arr[m][HORIZONS[i]][idx]
                mv = float(np.mean(v))
                if not np.isfinite(mv):
                    ok = False
                bm[m][i] = mv
        if not ok:
            continue
        for m in boot_cross:
            sk = [bm["model"][i] / bm[m][i] if bm[m][i] > 0 else np.nan
                  for i in range(len(HORIZONS))]
            c = cross_point(sk)
            if c is not None:
                boot_cross[m].append(c)
    res = {
        "n_origins": n,
        "origin_dates": [str(d.date()) for d in origins],
        "horizons": HORIZONS,
        "mse": {m: {h: round(mse[m][h], 4) for h in HORIZONS} for m in mse},
        "skill_persistence": dict(zip(HORIZONS, np.round(skill["pers"], 3))),
        "skill_linear": dict(zip(HORIZONS, np.round(skill["lin"], 3))),
        "skill_seasonal": dict(zip(HORIZONS, np.round(skill["seas"], 3))),
        "crossing": {},
        "per_origin": per_origin,
    }
    for m in ["pers", "lin"]:
        c = cross_point(skill[m])
        if c is not None and boot_cross[m]:
            lo, hi = np.percentile(boot_cross[m], [2.5, 97.5])
            res["crossing"][m] = {
                "point": round(c, 2),
                "ci95": [round(float(lo), 2), round(float(hi), 2)],
                "n_boot_ok": len(boot_cross[m]),
            }
        else:
            res["crossing"][m] = {"point": None, "ci95": None, "n_boot_ok": 0}
    return res


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = {}
    for key, cfg in WAVES.items():
        s = load_series(cfg["series"])
        out[key] = run_wave(key, s, cfg)
        cr = out[key]["crossing"]["pers"]
        print(f"[{key}] h_cross(persistence) = {cr['point']} wk "
              f"(95% CI {cr['ci95']}, n_boot {cr['n_boot_ok']})", flush=True)
        print(f"         skill_pers h=1..8: "
              f"{[out[key]['skill_persistence'][h] for h in HORIZONS]}", flush=True)
    (REPORTS / "rolling_results.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("saved reports/rolling_results.json", flush=True)
    make_fig7(out)


def make_fig7(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    colors = {"Delta": "#1f77b4", "Omicron": "#2ca02c", "Flu_22_23": "#ff7f0e"}
    marks = {"Delta": "o", "Omicron": "^", "Flu_22_23": "s"}
    disp = {"Delta": "COVID-19 Delta", "Omicron": "COVID-19 Omicron",
            "Flu_22_23": "流感 2022-23"}
    for key, rec in out.items():
        h = rec["horizons"]
        sk = [rec["skill_persistence"][i] for i in h]
        c = rec["crossing"]["pers"]
        lab = (f"{disp[key]} (穿越点 {c['point']:.2f} 周)"
               if c["point"] is not None else f"{disp[key]}（未穿越）")
        ax.plot(h, sk, marks[key] + "-", color=colors[key], lw=2, ms=6, label=lab)
        ax.plot(h, [rec["skill_linear"][i] for i in h], ":", color=colors[key],
                lw=1.1, alpha=0.7,
                label=f"{disp[key]} 相对局部线性基线" if key in ("Delta", "Flu_22_23") else None)
    ax.axhline(1.0, color="#d9534f", ls="--", lw=1.5, label="Skill = 1.0")
    ax.set_yscale("log")
    ax.set_xlabel("前瞻预测步长 $h$（周）")
    ax.set_ylabel("相对均方误差技能比 MSE_model / MSE_baseline")
    ax.set_title("图 7：伪实时滚动样本外技能衰减（移动块 Bootstrap 置信区间）")
    ax.legend(loc="upper left", fontsize=8.5, ncol=2)
    ax.grid(alpha=0.3, which="both")
    plt.tight_layout()
    plt.savefig(FIGS / "fig7_skill_decay.png", dpi=200)
    plt.close()
    print("saved figures_v2/fig7_skill_decay.png", flush=True)


if __name__ == "__main__":
    main()
