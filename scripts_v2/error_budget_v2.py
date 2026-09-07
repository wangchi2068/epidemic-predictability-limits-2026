# -*- coding: utf-8 -*-
"""
error_budget_v2.py — Generates Table 4 (four-term empirical error accounting)
and Figure 6 from origin-level rolling forecasts on the deposited series.

Definition (matches the manuscript note verbatim):
  relMSE^2_obs(h) = (1/M) * sum_t (Z_{t+h} - Zhat_{t+h})^2 / (I0_t * R_t^{h_gen})^2
where the per-origin model forecast is Zhat_{t+h} = I0_t * R_t^{h_gen},
I0_t = Z_t (last observed count at the origin), R_t = exp(Delta_g * b_t) with b_t the
4-week in-window OLS log-slope, h_gen = h_week / Delta_g, and M = number of origins.

Components:
  CV^2(h_gen)          — Lemma 2, from the phase-level Table-2 parameters. I0 is the
                         window-mean count from Table 2 (the phase's characteristic initial
                         size); the observed relMSE^2 above uses per-origin I0_t = Z_t for
                         its own normalization, which is an intentional, documented
                         distinction (backtest at each origin vs. phase-level theoretical
                         floor), NOT a shared quantity.
  E_drift(h)           = h_gen * v_drift, v_drift = variance of the 4-week-smoothed weekly
                         log-growth increments in a calibration band around the window
                         (Theorem 5 linear accumulation, empirical proxy). v_drift is
                         already a variance (drift_volatility returns np.var), so it enters
                         linearly — h_gen * v_drift — matching the printed formula
                         E_drift = h_gen * v^2 at main.tex.
  P(h)                 = (h_gen * s_gen)^2 — Lemma 3 first-order (s_gen from Table 2).
  E_misspec(h)         = relMSE^2_obs(h) - [CV^2 + E_drift + P]  (closure; may be negative
                         and is NOT clipped — a negative residual is itself diagnostic).

Outputs: reports/table4_budget.json, reports/figures_v2/fig6_error_budget.png
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

SEED_ORIGIN_COUNT = 6

PHASES = [
    # key, series, origin list (weekly), mu_g, window start (for drift calibration)
    ("Delta",   "covid", ["2021-07-03", "2021-07-10", "2021-07-17", "2021-07-24", "2021-07-31", "2021-08-07"], 4.7),
    ("Omicron", "covid", ["2021-12-04", "2021-12-11", "2021-12-18", "2021-12-25", "2022-01-01", "2022-01-08"], 3.0),
    ("flu22",   "flu",   ["2022-10-08", "2022-10-15", "2022-10-22", "2022-10-29", "2022-11-05", "2022-11-12"], 3.2),
    ("rsv24",   "rsv",   ["2024-11-09", "2024-11-16", "2024-11-23", "2024-11-30", "2024-12-07", "2024-12-14"], 8.4),
    ("rsv25",   "rsv",   ["2025-11-08", "2025-11-15", "2025-11-22", "2025-11-29", "2025-12-06", "2025-12-13"], 8.4),
]

HORIZONS = {"Delta": [1, 2, 4], "Omicron": [1, 2, 4], "flu22": [1, 2, 4],
            "rsv24": [2, 4], "rsv25": [2]}

DRIFT_CALIB_START = {"Delta": "2021-07-03", "Omicron": "2021-12-04", "flu22": "2022-10-08",
                     "rsv24": "2024-11-09", "rsv25": "2025-11-08"}
DRIFT_CALIB_WEEKS = 16  # calibration band for growth-rate volatility (4-week smoothed)


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


def drift_volatility(s, calib_start, n_weeks):
    """Growth-rate fluctuation proxy: variance of weekly log-growth increments around
    their 4-week centered moving average, over the calibration band. This is the
    empirical counterpart of the environment-noise variance v^2 in Theorem 5
    (log-scale variance maps one-to-one to relative variance for lognormal flips)."""
    band = s[(s.index >= calib_start)][: n_weeks + 4]
    if len(band) < 6:
        return np.nan
    dlog = np.diff(np.log(band.values.astype(float)))
    ma = pd.Series(dlog).rolling(4, center=True).mean()
    resid = dlog - ma
    resid = resid[~np.isnan(resid)]
    if len(resid) < 3:
        return np.nan
    return float(np.var(resid, ddof=1))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    params = json.loads((REPORTS / "table2_params.json").read_text(encoding="utf-8"))["table2"]

    out = {}
    for key, src, origins, mu_g in PHASES:
        s = load_series(src)
        delta_g = mu_g / 7.0
        v_drift = drift_volatility(s, DRIFT_CALIB_START[key], DRIFT_CALIB_WEEKS)
        p = params[key]
        R_phase, s_gen, k, I0_phase = p["R_gen"], p["s_gen"], p["k_agg"], p["I0"]

        per_h = {}
        for h_wk in HORIZONS[key]:
            h_gen = h_wk / delta_g
            errs, norms, preds = [], [], []
            for o in origins:
                t0 = pd.to_datetime(o)
                hist = s[s.index <= t0]
                if len(hist) < 4:
                    continue
                win = hist.iloc[-4:]
                b_t = fit4(np.log(win.values.astype(float)))
                I0_t = float(win.values[-1])
                R_t = float(np.exp(delta_g * b_t))
                tgt = t0 + pd.Timedelta(weeks=h_wk)
                m = s.index.get_indexer([tgt], method="nearest")
                if abs((s.index[m[0]] - tgt).days) > 3:
                    continue
                actual = float(s.values[m[0]])
                pred = I0_t * R_t ** h_gen
                errs.append((actual - pred) ** 2)
                norms.append((I0_t * R_t ** h_gen) ** 2)
                preds.append({"origin": o, "I0_t": I0_t, "R_t": round(R_t, 4),
                              "actual": actual, "pred": round(pred, 1)})
            if not errs:
                continue
            obs = float(np.mean(np.array(errs) / np.array(norms)))
            cv2_h = p_lognorm_slow(h_gen, R_phase, k, I0_phase)
            e_drift = h_gen * v_drift  # v_drift is already the variance v^2 (see docstring)
            p_h = (h_gen * s_gen) ** 2
            e_mis = obs - (cv2_h + e_drift + p_h)
            per_h[str(h_wk)] = {
                "h_week": h_wk, "h_gen": round(h_gen, 3), "n_origins": len(errs),
                "obs_total": obs,
                "cv2": cv2_h, "e_drift": e_drift, "p_param": p_h,
                "e_misspec": e_mis,
                "share_cv2": cv2_h / obs, "share_drift": e_drift / obs,
                "share_p": p_h / obs, "share_misspec": e_mis / obs,
                "origins": preds,
            }
        out[key] = {"mu_g_days": mu_g, "delta_g": delta_g, "v_drift": v_drift,
                    "R_gen": R_phase, "s_gen": s_gen, "k_agg": k, "I0": I0_phase,
                    "horizons": per_h}
        print(f"[{key}] v_drift={v_drift:.5f}", flush=True)
        for hw, rec in per_h.items():
            print(f"   h={hw}wk obs={rec['obs_total']:.5f} cv2={rec['share_cv2']*100:.2f}% "
                  f"drift={rec['share_drift']*100:.2f}% P={rec['share_p']*100:.2f}% "
                  f"misspec={rec['share_misspec']*100:.2f}%", flush=True)

    (REPORTS / "table4_budget.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("saved reports/table4_budget.json", flush=True)

    make_fig6(out)


def p_lognorm_slow(h, R, k, I0):
    """CV^2(h) on the generation scale (Lemma 2)."""
    if R > 1:
        return (1.0 + R / k) * (1.0 - R ** (-h)) / (I0 * (R - 1.0))
    if abs(R - 1.0) < 1e-9:
        return (1.0 + 1.0 / k) * h / I0
    return (1.0 + R / k) * (R ** (-h) - 1.0) / (I0 * (1.0 - R))


def make_fig6(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    labels, cv2s, drifts, ps, tot_below = [], [], [], [], []
    for key, rec in out.items():
        for hw, r in sorted(rec["horizons"].items(), key=lambda kv: int(kv[0])):
            labels.append(f"{key}\nh={hw}wk")
            cv2s.append(r["share_cv2"] * 100)
            drifts.append(r["share_drift"] * 100)
            ps.append(r["share_p"] * 100)
            tot_below.append(r["share_misspec"] * 100 < 0)
    x = np.arange(len(labels))
    ax.bar(x, cv2s, label="群体随机性 CV²", color="#4c72b0")
    ax.bar(x, drifts, bottom=cv2s, label="时变漂移", color="#dd8452")
    ax.bar(x, ps, bottom=np.array(cv2s) + np.array(drifts), label="参数外推 P", color="#55a868")
    ax.axhline(100.0, color="#c44e52", ls="--", lw=1.2,
               label="实测总误差（100%）；堆叠柱低于虚线 ⇒ 已建模项过解释（负闭合残差）")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("占实测总相对均方误差的百分比 (%)")
    ax.set_title("图 6：四项预测误差记账实测分解（生成自 table4_budget.json）")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(FIGS / "fig6_error_budget.png", dpi=200)
    plt.close()
    print("saved figures_v2/fig6_error_budget.png", flush=True)


if __name__ == "__main__":
    main()
