# -*- coding: utf-8 -*-
"""emit_v3.py — national-level rolling evaluation, four-term error accounting,
and LaTeX table bodies for the rebuilt empirical section.

Reads the JSONs produced by state_panel_v3.py plus the micro-layer fit results
and the forecast-hub evaluation, and writes tables_v3/*.tex.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANELS = ROOT / "data" / "panels"
REPORTS = ROOT / "reports_v3"
TABLES = ROOT / "tables_v3"
STATE_FIPS = {f"{i:02d}" for i in range(1, 57)}
TAU = 0.5

PHASES = [
    ("Delta",   "covid", "2021-07-03", "2021-07-31", 4.7, "COVID-19 Delta 暴发期"),
    ("Omicron", "covid", "2021-12-04", "2022-01-01", 3.0, "COVID-19 Omicron 达峰期"),
    ("JN1",     "covid", "2023-12-16", "2024-01-13", 3.5, "COVID-19 JN.1 流行期"),
    ("flu22",   "flu",   "2022-10-08", "2022-11-05", 3.2, "流感 2022--23 暴发早期"),
    ("flu24",   "flu",   "2024-11-23", "2024-12-21", 3.2, "流感 2024--25 流行季"),
    ("rsv24",   "rsv",   "2024-11-09", "2024-12-07", 8.4, "RSV 2024--25 流行季"),
    ("rsv25",   "rsv",   "2025-11-08", "2025-12-06", 8.4, "RSV 2025--26 流行季"),
]
BUDGET_PHASES = ["Delta", "Omicron", "JN1", "flu22", "flu24", "rsv24", "rsv25"]
BUDGET_HORIZONS = {"Delta": [1, 2, 4], "Omicron": [1, 2, 4], "JN1": [1, 2, 4],
                   "flu22": [1, 2, 4], "flu24": [1, 2, 4], "rsv24": [1, 2, 4],
                   "rsv25": [1, 2, 4]}


def load_panel(name):
    if name == "covid":
        d = pd.read_csv(PANELS / "covid_weekly_hospitalizations.csv.gz",
                        parse_dates=["week_end_date"])
        d = d.rename(columns={"week_end_date": "week_end",
                              "weekly_admissions": "value"})
    else:
        d = pd.read_csv(PANELS / f"{name}_weekly_hospitalizations.csv.gz",
                        parse_dates=["week_end"])
    d["location"] = d["location"].astype(str).str.zfill(2)
    return d


def national(panel):
    return (panel[panel.location.isin(STATE_FIPS)]
            .groupby("week_end").value.sum().sort_index())


def fit4(y):
    x = np.arange(len(y), dtype=float)
    A = np.vstack([x, np.ones(len(y))]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(coef[0])


def national_rolling():
    """National rolling-origin skill ratios (paper convention)."""
    out = {}
    for key, src, w0, w1, mu_g, disp in PHASES:
        s = national(load_panel(src))
        origins = [d for d in s.index
                   if d >= pd.Timestamp(w0) and int((s.index < d).sum()) >= 4][:6]
        errs = {m: {h: [] for h in range(1, 9)} for m in ("model", "pers", "lin")}
        for t0 in origins:
            hist = s[s.index <= t0].iloc[-4:]
            if (hist.values <= 0).any():
                continue
            b = fit4(np.log(hist.values.astype(float)))
            z = float(hist.values[-1])
            ratio = z / max(float(hist.values[-2]), 1.0)
            for h in range(1, 9):
                tgt = t0 + pd.Timedelta(weeks=h)
                i = int(s.index.get_indexer([tgt], method="nearest")[0])
                if abs((s.index[i] - tgt).days) > 3:
                    continue
                actual = float(s.values[i])
                if actual <= 0:
                    continue
                for m, v in {"model": z * np.exp(b * h), "pers": z,
                             "lin": z * ratio ** h}.items():
                    errs[m][h].append(((v - actual) / z) ** 2)
        mse = {m: {h: float(np.mean(errs[m][h])) for h in range(1, 9)
                   if errs[m][h]} for m in errs}
        sp = {h: mse["model"][h] / mse["pers"][h] for h in range(1, 9)
              if mse["pers"].get(h, 0) > 0}
        sl = {h: mse["model"][h] / mse["lin"][h] for h in range(1, 9)
              if mse["lin"].get(h, 0) > 0}
        out[key] = {"display": disp, "origins": [str(d.date()) for d in origins],
                    "skill_persistence": sp, "skill_linear": sl}
    return out


def crossing(series, direction):
    hs = sorted(series)
    if not hs:
        return None
    vals = [series[h] for h in hs]
    for i, v in enumerate(vals):
        hit = v >= 1.0 if direction == "up" else v <= 1.0
        if hit:
            if i == 0:
                return float(hs[0])
            x0, x1, y0, y1 = hs[i - 1], hs[i], vals[i - 1], vals[i]
            return x0 + (1 - y0) / (y1 - y0) * (x1 - x0)
    return None


def drift_volatility(s, calib_start, n_weeks=16):
    band = s[s.index >= calib_start][: n_weeks + 4]
    if len(band) < 6:
        return np.nan
    dlog = np.diff(np.log(band.values.astype(float)))
    ma = pd.Series(dlog).rolling(4, center=True).mean()
    resid = (dlog - ma).dropna()
    return float(np.var(resid, ddof=1)) if len(resid) >= 3 else np.nan


def budget(phases_json):
    """State-level four-term accounting: per state, per phase, per horizon.

    For each state the observed relMSE^2 uses that state's own rolling origins
    (W = 4 in-window slope, errors normalized by the model prediction, matching
    the manuscript's printed definition), and the three modeled terms use that
    state's phase-level parameters. The table reports the median and IQR of the
    closure-residual share across states.
    """
    out = {}
    for key, src, w0, w1, mu_g, disp in PHASES:
        if key not in BUDGET_PHASES:
            continue
        panel = load_panel(src)
        delta_g = mu_g / 7.0
        per_h = {h: [] for h in BUDGET_HORIZONS[key]}
        for loc in sorted(STATE_FIPS):
            s = panel[panel.location == loc].set_index("week_end").value.sort_index()
            win = s[(s.index >= w0) & (s.index <= w1)]
            if len(win) != 5 or win.sum() < 50 or (win.values <= 0).any():
                continue
            p = phases_json[key]["states"].get(loc)
            if p is None:
                continue
            R, sgen, k, I0 = p["R"], p["s"], p["k"], p["I0"]
            v = drift_volatility(s, w0)
            if not np.isfinite(v):
                continue
            origins = [d for d in s.index
                       if d >= pd.Timestamp(w0) and int((s.index < d).sum()) >= 4][:6]
            for h_wk in BUDGET_HORIZONS[key]:
                h_gen = h_wk / delta_g
                errs = []
                for t0 in origins:
                    hist = s[s.index <= t0].iloc[-4:]
                    if (hist.values <= 0).any():
                        continue
                    b = fit4(np.log(hist.values.astype(float)))
                    z = float(hist.values[-1])
                    tgt = t0 + pd.Timedelta(weeks=h_wk)
                    i = int(s.index.get_indexer([tgt], method="nearest")[0])
                    if abs((s.index[i] - tgt).days) > 3:
                        continue
                    pred = z * np.exp(b * h_wk)
                    errs.append(((pred - float(s.values[i])) / pred) ** 2)
                if len(errs) < 3:
                    continue
                obs = float(np.mean(errs))
                cv = (1.0 + R / k) * (1.0 - R ** (-h_gen)) / (I0 * (R - 1.0)) if R > 1 else 0.0
                e_drift = h_wk * v
                p_err = (h_gen * sgen) ** 2
                resid = obs - (cv + e_drift + p_err)
                per_h[h_wk].append({"obs": obs, "cv2": cv, "e_drift": e_drift,
                                    "p_param": p_err, "e_misspec": resid,
                                    "v": float(v),
                                    "share_misspec": resid / obs if obs > 0 else None})
        summary = {}
        for h_wk, rows in per_h.items():
            if not rows:
                continue
            shares = np.array([r["share_misspec"] for r in rows
                               if r["share_misspec"] is not None])
            summary[h_wk] = {
                "n_states": len(rows),
                "median_obs": float(np.median([r["obs"] for r in rows])),
                "median_cv2": float(np.median([r["cv2"] for r in rows])),
                "median_drift": float(np.median([r["e_drift"] for r in rows])),
                "median_p": float(np.median([r["p_param"] for r in rows])),
                "median_resid": float(np.median([r["e_misspec"] for r in rows])),
                "median_share": float(np.median(shares)),
                "q25_share": float(np.percentile(shares, 25)),
                "q75_share": float(np.percentile(shares, 75)),
                "frac_positive": float((shares > 0).mean()),
                "median_v_week": float(np.median([r["v"] for r in rows])),
            }
        out[key] = {"display": disp, "horizons": summary}
        # observed horizon: first h where the state-median observed RelRMSE
        # (sqrt of median RelMSE_obs) reaches tau = 0.5, linearly interpolated
        # between the evaluated weekly grid points.
        hs_sorted = sorted((int(h), r) for h, r in summary.items())
        if not hs_sorted:
            out[key]["obs_horizon_weeks"] = None
            continue
        rmses = [(h, float(np.sqrt(r["median_obs"]))) for h, r in hs_sorted]
        obs_h = None
        for i, (h, rm) in enumerate(rmses):
            if rm >= TAU:
                if i == 0:
                    obs_h = float(h)
                else:
                    h0, r0 = rmses[i - 1]
                    obs_h = float(h0 + (TAU - r0) / (rm - r0) * (h - h0))
                break
        out[key]["obs_horizon_weeks"] = obs_h
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    phases = json.loads((REPORTS / "state_phases.json").read_text(encoding="utf-8"))
    roll_state = json.loads((REPORTS / "state_rolling.json").read_text(encoding="utf-8"))
    scen = json.loads((REPORTS / "scenarios.json").read_text(encoding="utf-8"))
    micro = json.loads((ROOT / "data" / "micro" /
                        "micro_branching_fit_results.json").read_text(encoding="utf-8"))
    hub = json.loads((ROOT / "data" / "hub" /
                      "forecast_hub_operational_evaluation.json").read_text(encoding="utf-8"))

    print("=== national rolling ===", flush=True)
    roll_nat = national_rolling()
    for k, rec in roll_nat.items():
        cp = crossing(rec["skill_persistence"], "up")
        cl = crossing(rec["skill_linear"], "down")
        rec["crossing_persistence"] = cp
        rec["crossing_linear"] = cl
        print(f"[{k:8}] national crossing: persistence={None if cp is None else round(cp,2)} "
              f"local-linear={None if cl is None else round(cl,2)}", flush=True)
    (REPORTS / "national_rolling.json").write_text(
        json.dumps(roll_nat, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== four-term budget (state-level medians) ===", flush=True)
    bud = budget(phases)
    for k, rec in bud.items():
        for h, r in sorted(rec["horizons"].items()):
            print(f"[{k:8} h={h}] n={r['n_states']:2d} "
                  f"obs={r['median_obs']:.4f} cv2={r['median_cv2']:.4f} "
                  f"drift={r['median_drift']:.4f} P={r['median_p']:.4f} "
                  f"resid_share={100*r['median_share']:.1f}% "
                  f"[{100*r['q25_share']:.1f},{100*r['q75_share']:.1f}] "
                  f"pos={100*r['frac_positive']:.0f}%", flush=True)
    (REPORTS / "budget_national.json").write_text(
        json.dumps(bud, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------------------------------------------------------------- tables
    print("\n=== emitting LaTeX tables ===", flush=True)
    emit_table2(phases)
    emit_table3(roll_state, roll_nat, phases, bud)
    emit_table4(bud)
    emit_table5_hub(hub)
    emit_table6_tiers(scen)
    emit_table7(micro)
    print("tables written to tables_v3/")


def _fmt(v, nd=2):
    return "--" if v is None else f"{v:.{nd}f}"


def emit_table2(phases):
    rows = []
    for key, src, w0, w1, mu_g, disp in PHASES:
        rec = phases[key]
        R = rec["R_summary"]
        s = rec["s_summary"]
        k = rec["k_summary"]
        I0 = rec["I0_summary"]
        h = rec["h_week_summary"]
        nat = rec["national"]
        rows.append(
            f"{disp} & {rec['n_states']} & "
            f"{_fmt(R['median'],3)} [{_fmt(R['q25'],3)}, {_fmt(R['q75'],3)}] & "
            f"{_fmt(s['median'],4)} & {_fmt(k['median'],1)} & "
            f"{int(I0['median'])} & "
            f"{_fmt(h['median'],1)} [{_fmt(h['q25'],1)}, {_fmt(h['q75'],1)}] & "
            f"{_fmt(nat['h_week'],1)} \\\\")
    body = ("\\begin{tabular}{lccccccc}\n"
            "\\toprule\n"
            "阶段 & $n_{\\text{州}}$ & $R$ 中位数 [IQR] & $s$ 中位数 & "
            "$k_{\\text{agg}}$ 中位数 & $I_0$ 中位数 & "
            "$h^*_{\\text{周}}$ 中位数 [IQR] & 国家级 $h^*_{\\text{周}}$ \\\\\n"
            "\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (TABLES / "table3_state.tex").write_text(body, encoding="utf-8")


def emit_table3(roll_state, roll_nat, phases, bud=None):
    rows = []
    for key, src, w0, w1, mu_g, disp in PHASES:
        rs = roll_state[key]
        rn = roll_nat[key]
        cp = rs["crossing_persistence"]
        cl = rs["crossing_linear"]
        hp = phases[key]["h_week_summary"]
        oh = bud[key]["obs_horizon_weeks"] if bud else None
        rows.append(
            f"{disp} & {rs['n_states']} & "
            f"{_fmt(cp['median'],1)} [{_fmt(cp['q25'],1)}, {_fmt(cp['q75'],1)}] & "
            f"{_fmt(cl['median'],1)} & "
            f"{_fmt(oh,2)} & "
            f"{_fmt(rn['crossing_persistence'],2)} & "
            f"{_fmt(rn['crossing_linear'],2)} & "
            f"{_fmt(hp['median'],1)} \\\\")
    body = ("\\begin{tabular}{lccccccc}\n"
            "\\toprule\n"
            "阶段 & $n_{\\text{州}}$ & 州级持续性穿越 [IQR] & "
            "州级局部线性穿越 & 州级实测视界 & 国家级持续性 & 国家级局部线性 & "
            "州级 $h^*$ 中位数 \\\\\n"
            "\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (TABLES / "table5_rolling.tex").write_text(body, encoding="utf-8")


def emit_table4(bud):
    rows = []
    for key, rec in bud.items():
        for h, r in sorted(rec["horizons"].items()):
            rows.append(
                f"{rec['display']} & {h} & {r['n_states']} & "
                f"{r['median_obs']*1e4:.2f} & {r['median_cv2']*1e4:.2f} & "
                f"{r['median_drift']*1e4:.2f} & {r['median_p']*1e4:.2f} & "
                f"{100*r['median_share']:.1f}\\% "
                f"[{100*r['q25_share']:.1f}, {100*r['q75_share']:.1f}] & "
                f"{100*r['frac_positive']:.0f}\\% \\\\")
    body = ("\\begin{tabular}{lcccccccc}\n"
            "\\toprule\n"
            "阶段 & $h_{\\text{周}}$ & $n_{\\text{州}}$ & "
            "$\\text{RelMSE}_{\\text{obs}}$ & $\\text{CV}^2$ & "
            "$\\mathcal{E}_{\\text{drift}}$ & $P$ & "
            "闭合残差占比 (IQR) & 为正占比 \\\\\n"
            "\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (TABLES / "table4_budget.tex").write_text(body, encoding="utf-8")


def emit_table5_hub(hub):
    rows = []
    for rec in hub:
        for h in rec["horizons"]:
            rows.append(
                f"{rec['wave']} & {rec['forecast_date']} & {h['h_weeks']} & "
                f"{h['n_states']} & {h['median_relMSE']:.3f} & "
                f"{100*h['frac_relMSE_ge_1']:.0f}\\% & {h['median_WIS']:.0f} & "
                f"{h['median_abs_pct_err']:.1f}\\% \\\\")
    body = ("\\begin{tabular}{llcccccc}\n"
            "\\toprule\n"
            "波次 & 预测原点 & $h$ (周) & $n_{\\text{州}}$ & "
            "中位 MSE 比率 & $\\ge 1$ 占比 & 中位 WIS & 中位绝对误差 \\\\\n"
            "\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (TABLES / "table6_hub.tex").write_text(body, encoding="utf-8")


def emit_table6_tiers(scen):
    rows = []
    for key, rec in scen.items():
        t = rec["tiers"]
        rows.append(
            f"{rec['display']} & "
            + " & ".join(
                f"{_fmt(t[f'tau_{x:.2f}']['median'],1)} ({t[f'tau_{x:.2f}']['n']})"
                for x in (0.20, 0.35, 0.50, 0.70))
            + " \\\\")
    body = ("\\begin{tabular}{lcccc}\n"
            "\\toprule\n"
            "阶段 & $\\tau=0.20$ & $\\tau=0.35$ & $\\tau=0.50$ & $\\tau=0.70$ \\\\\n"
            "\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (TABLES / "table7_tiers.tex").write_text(body, encoding="utf-8")


def emit_table7(micro):
    rean = json.loads((REPORTS / "micro_reanalysis.json").read_text(encoding="utf-8"))
    rows = []
    for name, rec in micro.items():
        if name == "LloydSmith_reference":
            continue
        ra = rean.get(name, {})
        r_ci = ra.get("parametric_ci_R")
        k_ci = ra.get("parametric_ci_k")
        r_lo, r_hi = (f"{r_ci[0]:.2f}", f"{r_ci[1]:.2f}") if r_ci else ("--", "--")
        k_lo, k_hi = (f"{k_ci[0]:.2f}", f"{k_ci[1]:.2f}") if k_ci else ("--", "--")
        rows.append(
            f"{name.replace('_', ' ')} & {rec['N']} & {rec['R_mle']:.3f} & "
            f"{r_lo}--{r_hi} & {rec['k_mle']:.3f} & {k_lo}--{k_hi} & "
            f"{rec['empirical_CV2']:.2f} & {rec['theory_CV2']:.2f} & "
            f"{rec['delta_aic_poisson_vs_nb']:.1f} & "
            f"{rec['bootstrap']['ratio_var_to_crb']:.3f} \\\\")
    body = ("\\begin{tabular}{lcc c c c cc c c}\n"
            "\\toprule\n"
            "数据集 & $N$ & $\\hat R$ & 95\\% CI & $\\hat k$ & 95\\% CI & "
            "经验 $\\text{CV}^2$ & 理论 $\\text{CV}^2$ & $\\Delta\\text{AIC}$ & 自助/CRB \\\\\n"
            "\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (TABLES / "table2_micro.tex").write_text(body, encoding="utf-8")


if __name__ == "__main__":
    main()
