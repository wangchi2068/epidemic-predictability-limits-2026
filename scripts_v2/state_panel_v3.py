# -*- coding: utf-8 -*-
"""state_panel_v3.py — Rebuild the manuscript's empirical layer on the
three-module data architecture (micro transmission chains / state-level
hospitalization panels / forecast-hub benchmark).

Outputs
-------
reports_v3/state_phases.json      per-phase, per-state parameter and horizon fits
reports_v3/state_rolling.json     per-phase, per-state rolling-origin skill crossings
reports_v3/state_budget.json      per-phase four-term error accounting (state-level)
reports_v3/scenarios.json         tolerance-tier horizons (state-level medians)
tables_v3/table2_state.tex        Table 2  (state-level phase parameters & horizons)
tables_v3/table3_phases.tex       Table 3  (growth/peak/decline state-level comparison)
tables_v3/table4_budget.tex       Table 4  (four-term error accounting)
tables_v3/table5_tiers.tex        Table 5  (tolerance-tier horizons)
tables_v3/table6_hub.tex          Table 6  (forecast-hub operational benchmark)

All fits use the manuscript's conventions:
  R = exp(Delta_g * b_week), s = Delta_g * SE(b_week), Delta_g = mu_g/7
  k_agg: Var(dlog I) = 1/m + 1/k, capped at 1000
  h*_exact: root of CV^2(h) + P(h) = tau^2, tau = 0.5, lognormal exact P(h)
State-level panels: 51 FIPS state-level jurisdictions only (territories and the
national US row are excluded from state statistics; the national series is the
state sum and is reported alongside).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
PANELS = ROOT / "data" / "panels"
REPORTS = ROOT / "reports_v3"
TABLES = ROOT / "tables_v3"
REPORTS.mkdir(exist_ok=True)
TABLES.mkdir(exist_ok=True)

TAU = 0.5
K_CAP = 1000.0
SEED = 20260807
STATE_FIPS = {f"{i:02d}" for i in range(1, 57)}

PHASES = [
    # key, panel, window start, window end, mu_g (days), display
    ("Delta",   "covid", "2021-07-03", "2021-07-31", 4.7, "COVID-19 Delta 暴发期"),
    ("Omicron", "covid", "2021-12-04", "2022-01-01", 3.0, "COVID-19 Omicron 达峰期"),
    ("JN1",     "covid", "2023-12-16", "2024-01-13", 3.5, "COVID-19 JN.1 流行期"),
    ("flu22",   "flu",   "2022-10-08", "2022-11-05", 3.2, "流感 2022--23 暴发早期"),
    ("flu24",   "flu",   "2024-11-23", "2024-12-21", 3.2, "流感 2024--25 流行季"),
    ("rsv24",   "rsv",   "2024-11-09", "2024-12-07", 8.4, "RSV 2024--25 流行季"),
    ("rsv25",   "rsv",   "2025-11-08", "2025-12-06", 8.4, "RSV 2025--26 流行季"),
]

PHASES_T3 = [
    ("Delta_growth",    "covid", "2021-07-03", "2021-07-31", 4.7, "Delta 爬坡期"),
    ("Delta_peak",      "covid", "2021-08-21", "2021-10-02", 4.7, "Delta 平台期"),
    ("Delta_decline",   "covid", "2021-10-02", "2021-11-13", 4.7, "Delta 消退期"),
    ("Omicron_growth",  "covid", "2021-12-04", "2022-01-01", 3.0, "Omicron 爬坡期"),
    ("Omicron_peak",    "covid", "2022-01-01", "2022-01-29", 3.0, "Omicron 平台期"),
    ("Omicron_decline", "covid", "2022-01-29", "2022-03-12", 3.0, "Omicron 消退期"),
    ("flu22_growth",    "flu",   "2022-10-08", "2022-11-05", 3.2, "流感 2022--23 爬坡期"),
    ("flu22_peak",      "flu",   "2022-11-26", "2022-12-24", 3.2, "流感 2022--23 平台期"),
    ("flu22_decline",   "flu",   "2022-12-24", "2023-02-04", 3.2, "流感 2022--23 消退期"),
]

WAVES = {"Delta": ["2021-08-02", "2021-08-09", "2021-08-16", "2021-08-23",
                   "2021-08-30", "2021-09-06"],
         "Omicron": ["2021-12-06", "2021-12-13", "2021-12-20", "2021-12-27",
                     "2022-01-03", "2022-01-10"]}

# minimum data requirements for a state to enter the state-level statistics
MIN_WINDOW_TOTAL = 50.0     # phase window total reported counts
MIN_WEEK_COUNT = 1.0        # every week of the window must be positive (log)
MIN_ROLL_TOTAL = 30.0       # rolling-backtest window total


# ------------------------------------------------------------------ numerics
def fit_loglinear(y):
    n = len(y)
    x = np.arange(n, dtype=float)
    A = np.vstack([x, np.ones(n)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ coef
    df = n - 2
    sxx = ((x - x.mean()) ** 2).sum()
    s2 = (resid ** 2).sum() / df
    se = np.sqrt(s2 / sxx)
    return float(coef[0]), float(se), float(coef[1]), float(s2), x


def estimate_k(counts):
    dlog = np.diff(np.log(counts))
    m = float(np.mean(counts))
    var = float(np.var(dlog, ddof=1))
    return float(min(1.0 / max(var - 1.0 / m, 1e-3), K_CAP))


def p_lognorm(h, s):
    x2 = (np.asarray(h, dtype=float) * s) ** 2
    return np.exp(2.0 * x2) - 2.0 * np.exp(0.5 * x2) + 1.0


def cv2(h, R, k, I0):
    if R > 1.0:
        return (1.0 + R / k) * (1.0 - R ** (-h)) / (I0 * (R - 1.0))
    if abs(R - 1.0) < 1e-9:
        return (1.0 + 1.0 / k) * h / I0
    return (1.0 + R / k) * (R ** (-h) - 1.0) / (I0 * (1.0 - R))


def solve_hstar(R, s, k, I0, tau=TAU):
    f = lambda h: cv2(h, R, k, I0) + p_lognorm(h, s) - tau ** 2
    if f(1e-3) > 0:
        return None
    hi = 2.0
    while f(hi) < 0 and hi < 1e6:
        hi *= 2.0
    return brentq(f, 1e-3, hi, xtol=1e-6)


def analyze_segment(counts, mu_g):
    """Fit one phase window. Returns None when data requirements are not met."""
    counts = np.asarray(counts, dtype=float)
    if counts.size < 5 or counts.sum() < MIN_WINDOW_TOTAL or (counts < MIN_WEEK_COUNT).any():
        return None
    y = np.log(counts)
    b, se_b, a, sigma2, x = fit_loglinear(y)
    k = estimate_k(counts)
    I0 = float(counts.mean())
    delta_g = mu_g / 7.0
    R = float(np.exp(delta_g * b))
    s = float(delta_g * se_b)
    h = solve_hstar(R, s, k, I0)
    out = {"R": R, "s": s, "k": k, "I0": I0, "window_total": float(counts.sum()),
           "b_week": b, "se_slope": se_b}
    if h is not None:
        out.update({"h_gen": h, "h_week": h * delta_g, "hs": h * s})
    else:
        out.update({"h_gen": None, "h_week": None, "hs": None})
    return out


# ------------------------------------------------------------------ loading
def load_panels():
    covid = pd.read_csv(PANELS / "covid_weekly_hospitalizations.csv.gz",
                        parse_dates=["week_end_date"])
    covid = covid.rename(columns={"week_end_date": "week_end",
                                  "weekly_admissions": "value"})
    flu = pd.read_csv(PANELS / "flu_weekly_hospitalizations.csv.gz",
                      parse_dates=["week_end"])
    rsv = pd.read_csv(PANELS / "rsv_weekly_hospitalizations.csv.gz",
                      parse_dates=["week_end"])
    for d in (covid, flu, rsv):
        d["location"] = d["location"].astype(str).str.zfill(2)
    return {"covid": covid, "flu": flu, "rsv": rsv}


def series_for(panel, loc):
    s = panel[panel.location == loc].set_index("week_end").value.sort_index()
    return s


def window_values(panel, loc, w0, w1):
    s = series_for(panel, loc)
    seg = s[(s.index >= w0) & (s.index <= w1)]
    return seg


# ------------------------------------------------------------------ analyses
def state_phase_analysis(panels):
    out = {}
    for key, src, w0, w1, mu_g, disp in PHASES:
        panel = panels[src]
        states = {}
        for loc in sorted(STATE_FIPS):
            seg = window_values(panel, loc, w0, w1)
            if len(seg) != 5:
                continue
            rec = analyze_segment(seg.values, mu_g)
            if rec is not None:
                states[loc] = rec
        nat = window_values(panel, "01", w0, w1)  # placeholder
        nat_series = (panel[panel.location.isin(STATE_FIPS)]
                      .groupby("week_end").value.sum().sort_index())
        nat_seg = nat_series[(nat_series.index >= w0) & (nat_series.index <= w1)]
        nat_rec = analyze_segment(nat_seg.values, mu_g) if len(nat_seg) == 5 else None
        out[key] = {"display": disp, "window": [w0, w1], "mu_g": mu_g,
                    "n_states": len(states), "states": states,
                    "national": nat_rec}
    return out


def summarize(recs, field):
    vals = [r[field] for r in recs.values() if r.get(field) is not None]
    if not vals:
        return None
    a = np.array(vals, dtype=float)
    return {"n": len(a), "median": float(np.median(a)),
            "q25": float(np.percentile(a, 25)), "q75": float(np.percentile(a, 75))}


def rolling_backtest(panels, phases):
    """Per-state rolling-origin skill crossings vs persistence and local-linear.

    Convention (identical to the manuscript's rolling evaluation): errors are
    normalized by the origin value z_t, and the skill ratio is the ratio of
    mean normalized MSEs, Skill(h) = MSE_model(h) / MSE_baseline(h).
    """
    out = {}
    for key, src, w0, w1, mu_g, disp in phases:
        panel = panels[src]
        per_state = {}
        for loc in sorted(STATE_FIPS):
            s = series_for(panel, loc)
            if len(s) < 6:
                continue
            win = s[(s.index >= w0) & (s.index <= w1)]
            if len(win) != 5 or win.sum() < MIN_ROLL_TOTAL:
                continue
            origins = [d for d in s.index
                       if d >= pd.Timestamp(w0) and int((s.index < d).sum()) >= 4][:6]
            if len(origins) < 3:
                continue
            errs = {m: {h: [] for h in range(1, 9)} for m in ("model", "pers", "lin")}
            for t0 in origins:
                hist = s[s.index <= t0].iloc[-4:]
                if (hist.values <= 0).any():
                    continue
                y = np.log(hist.values.astype(float))
                b = float(np.polyfit(np.arange(4), y, 1)[0])
                z = float(hist.values[-1])
                if z <= 0:
                    continue
                ratio = z / max(float(hist.values[-2]), 1.0)
                for h in range(1, 9):
                    tgt = t0 + pd.Timedelta(weeks=h)
                    i = int(s.index.get_indexer([tgt], method="nearest")[0])
                    if abs((s.index[i] - tgt).days) > 3:
                        continue
                    actual = float(s.values[i])
                    if actual <= 0:
                        continue
                    preds = {"model": z * np.exp(b * h), "pers": z,
                             "lin": z * ratio ** h}
                    for m, v in preds.items():
                        errs[m][h].append(((v - actual) / z) ** 2)
            if not errs["model"][1]:
                continue
            mse = {m: {h: float(np.mean(errs[m][h])) for h in range(1, 9)
                       if errs[m][h]} for m in errs}
            sp = {h: mse["model"][h] / mse["pers"][h] for h in range(1, 9)
                  if mse["pers"].get(h, 0) > 0}
            sl = {h: mse["model"][h] / mse["lin"][h] for h in range(1, 9)
                  if mse["lin"].get(h, 0) > 0}
            per_state[loc] = {"skill_persistence": sp, "skill_linear": sl}
        out[key] = {"display": disp, "n_states": len(per_state), "states": per_state}
    return out


def crossing(series_dict, direction):
    """First h where the skill series crosses 1.0 (interpolated)."""
    hs = sorted(series_dict)
    if not hs:
        return None
    vals = [series_dict[h] for h in hs]
    if direction == "up":
        for i, v in enumerate(vals):
            if v >= 1.0:
                if i == 0:
                    return float(hs[0])
                x0, x1, y0, y1 = hs[i - 1], hs[i], vals[i - 1], vals[i]
                return x0 + (1 - y0) / (y1 - y0) * (x1 - x0)
        return None
    for i, v in enumerate(vals):
        if v <= 1.0:
            if i == 0:
                return float(hs[0])
            x0, x1, y0, y1 = hs[i - 1], hs[i], vals[i - 1], vals[i]
            return x0 + (1 - y0) / (y1 - y0) * (x1 - x0)
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    panels = load_panels()

    print("=== state-level phase fits ===", flush=True)
    phases = state_phase_analysis(panels)
    for key, rec in phases.items():
        for f in ("R", "s", "k", "I0", "h_week", "hs"):
            sm = summarize(rec["states"], f)
            rec[f + "_summary"] = sm
        nat = rec["national"]
        print(f"[{key:8}] n_states={rec['n_states']:2d}  "
              f"median R={rec['R_summary']['median']:.3f}  "
              f"s={rec['s_summary']['median']:.4f}  "
              f"k={rec['k_summary']['median']:.1f}  "
              f"h*={rec['h_week_summary']['median'] if rec['h_week_summary'] else None} wk  "
              f"national h*={None if nat is None or nat['h_week'] is None else round(nat['h_week'],2)} wk",
              flush=True)
    (REPORTS / "state_phases.json").write_text(
        json.dumps(phases, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== state-level rolling backtest ===", flush=True)
    roll = rolling_backtest(panels, PHASES)
    for key, rec in roll.items():
        cross_p, cross_l = [], []
        for loc, st in rec["states"].items():
            cp = crossing(st["skill_persistence"], "up")
            cl = crossing(st["skill_linear"], "down")
            if cp is not None:
                cross_p.append(cp)
            if cl is not None:
                cross_l.append(cl)
        rec["crossing_persistence"] = {
            "n": len(cross_p),
            "median": float(np.median(cross_p)) if cross_p else None,
            "q25": float(np.percentile(cross_p, 25)) if cross_p else None,
            "q75": float(np.percentile(cross_p, 75)) if cross_p else None}
        rec["crossing_linear"] = {
            "n": len(cross_l),
            "median": float(np.median(cross_l)) if cross_l else None,
            "q25": float(np.percentile(cross_l, 25)) if cross_l else None,
            "q75": float(np.percentile(cross_l, 75)) if cross_l else None}
        print(f"[{key:8}] n_states={rec['n_states']:2d}  "
              f"persistence crossing: n={len(cross_p)} median="
              f"{rec['crossing_persistence']['median']}  "
              f"local-linear crossing: n={len(cross_l)} median="
              f"{rec['crossing_linear']['median']}", flush=True)
    (REPORTS / "state_rolling.json").write_text(
        json.dumps(roll, indent=2, ensure_ascii=False), encoding="utf-8")

    # tolerance tiers at state level
    print("\n=== tolerance tiers (state medians) ===", flush=True)
    tiers = {}
    for key, src, w0, w1, mu_g, disp in PHASES:
        panel = panels[src]
        row = {}
        for tau in (0.20, 0.35, 0.50, 0.70):
            hs = []
            for loc in sorted(STATE_FIPS):
                seg = window_values(panel, loc, w0, w1)
                if len(seg) != 5:
                    continue
                counts = seg.values.astype(float)
                if counts.sum() < MIN_WINDOW_TOTAL or (counts < MIN_WEEK_COUNT).any():
                    continue
                y = np.log(counts)
                b, se_b, *_ = fit_loglinear(y)
                delta_g = mu_g / 7.0
                R = float(np.exp(delta_g * b))
                s = float(delta_g * se_b)
                k = estimate_k(counts)
                h = solve_hstar(R, s, k, float(counts.mean()), tau=tau)
                if h is not None:
                    hs.append(h * delta_g)
            row[f"tau_{tau:.2f}"] = {
                "n": len(hs),
                "median": float(np.median(hs)) if hs else None,
                "q25": float(np.percentile(hs, 25)) if hs else None,
                "q75": float(np.percentile(hs, 75)) if hs else None}
        tiers[key] = {"display": disp, "tiers": row}
        print(f"[{key:8}] " + "  ".join(
            f"tau={t:.2f}: {row['tau_%.2f' % t]['median']} "
            f"(n={row['tau_%.2f' % t]['n']})" for t in (0.20, 0.35, 0.50, 0.70)),
            flush=True)
    (REPORTS / "scenarios.json").write_text(
        json.dumps(tiers, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\ndone.")


if __name__ == "__main__":
    main()
