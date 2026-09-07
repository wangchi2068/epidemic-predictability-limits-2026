# -*- coding: utf-8 -*-
"""
pipeline.py — Single source of truth for parameter estimation, horizon roots,
and uncertainty (parametric bootstrap).

Estimation protocol (fixed, documented in manuscript Section 2.1):
  1. For each phase window (W weeks, W=5 for Table 2), fit OLS on log weekly counts:
         log I_t = a + b_week * t + eps_t,  t = 0..W-1.
     SE(b_week) is the standard OLS slope standard error (df = W - 2).
  2. Time-scale conversion to the generation scale (Delta_g = mu_g / 7 weeks):
         b_gen   = Delta_g * b_week            (log-scale growth per generation)
         s_gen   = Delta_g * SE(b_week)        (its standard error, Delta method)
         R_gen   = exp(b_gen)
     The horizon equation is solved on the generation scale with the intrinsic
     variance CV^2(h_gen) and the lognormal parameter-extrapolation term
         P(h) = E[(Y^h - 1)^2], Y = Rhat/R ~ Lognormal(0, s_gen^2)
              = exp(2 (h s)^2) - 2 exp((h s)^2 / 2) + 1   (exact closed form).
  3. Overdispersion k_agg: moment estimator on first differences of log counts,
         Var(dlog) = 1/m + 1/k  =>  k = 1 / (Var(dlog) - 1/m),  capped at 1000.
  4. I0 = arithmetic mean of weekly counts in the inference window (documented unit).
  5. Horizon root h*_exact solves CV^2(h) + P(h) = tau^2 (tau = 0.5 baseline).
  6. 95% CIs: parametric bootstrap, B = 2000 replicates, seed 20260807.
     Each replicate resamples log-scale residuals around the fitted line,
     refits (b*, SE*), re-estimates k* and I0* on the resampled counts,
     and re-solves the horizon equation. Percentile intervals.

Outputs: reports/table2_params.json (single source for Tables 2, 3, 5, 6 and
Figures 5; consumed by make_tables_v2.py / make_all_figures_v2.py /
check_consistency.py).
"""
from __future__ import annotations
import json
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

SEED = 20260807
B_BOOT = 2000
TAU = 0.5
K_CAP = 1000.0

# ---------------------------------------------------------------- data loading

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_series(name: str) -> pd.Series:
    d = pd.read_csv(PROC / f"{name}_final_weekly.csv.gz", parse_dates=["week_end"])
    if name == "covid":
        d = d[d.week_end >= "2020-08-01"]
    return d.groupby("week_end")["value"].sum().sort_index()


# ---------------------------------------------------------------- estimators

def fit_loglinear(y: np.ndarray):
    """OLS on log counts. Returns slope, slope SE (df = n-2), intercept, resid variance."""
    n = len(y)
    x = np.arange(n, dtype=float)
    A = np.vstack([x, np.ones(n)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ coef
    df = n - 2
    Sxx = ((x - x.mean()) ** 2).sum()
    s2 = (resid ** 2).sum() / df
    se = np.sqrt(s2 / Sxx)
    return float(coef[0]), float(se), float(coef[1]), float(s2), x


def estimate_k(counts: np.ndarray) -> float:
    """Moment estimator: Var(d log I) = 1/m + 1/k, capped at K_CAP."""
    dlog = np.diff(np.log(counts))
    m = float(np.mean(counts))
    var = float(np.var(dlog, ddof=1))
    return float(min(1.0 / max(var - 1.0 / m, 1e-3), K_CAP))


def p_lognorm(h: np.ndarray, s: float) -> np.ndarray:
    """Exact E[(Y^h - 1)^2] for Y ~ Lognormal with log-scale s (centered)."""
    x2 = (np.asarray(h, dtype=float) * s) ** 2
    return np.exp(2.0 * x2) - 2.0 * np.exp(0.5 * x2) + 1.0


def cv2(h: float, R: float, k: float, I0: float) -> float:
    """Intrinsic relative variance of generation-h incidence."""
    if R > 1.0:
        return (1.0 + R / k) * (1.0 - R ** (-h)) / (I0 * (R - 1.0))
    if abs(R - 1.0) < 1e-9:
        return (1.0 + 1.0 / k) * h / I0
    return (1.0 + R / k) * (R ** (-h) - 1.0) / (I0 * (1.0 - R))


def relmse2(h: float, R: float, s: float, k: float, I0: float) -> float:
    return cv2(h, R, k, I0) + p_lognorm(h, s)


def solve_hstar(R: float, s: float, k: float, I0: float, tau: float = TAU) -> float | None:
    """Root of CV^2(h) + P(h) = tau^2 on h > 0, or None when relMSE^2(1) > tau^2."""
    if relmse2(1.0, R, s, k, I0) > tau ** 2:
        return None
    f = lambda h: relmse2(h, R, s, k, I0) - tau ** 2
    hi = 2.0
    while f(hi) < 0 and hi < 1e6:
        hi *= 2.0
    return brentq(f, 1e-3, hi, xtol=1e-6)


# ---------------------------------------------------------------- bootstrap

def bootstrap_replicate(rng, y, x, b_hat, a_hat, sigma2, delta_g):
    """One parametric bootstrap replicate -> (R*, s*, k*, I0*)."""
    e = rng.normal(0.0, np.sqrt(sigma2), size=len(y))
    y_star = a_hat + b_hat * x + e
    b_star, se_star, *_ = fit_loglinear(y_star)
    counts_star = np.exp(y_star)
    # finite-sample guards: keep counts positive and finite
    if not np.isfinite(b_star) or not np.isfinite(se_star) or se_star <= 0:
        return None
    k_star = estimate_k(counts_star)
    I0_star = float(np.mean(counts_star))
    R_star = np.exp(delta_g * b_star)
    s_star = delta_g * se_star
    return R_star, s_star, k_star, I0_star


def horizon_ci(R, s, k, I0, delta_g, b_hat, a_hat, sigma2, y, x,
               tau=TAU, B=B_BOOT, seed=SEED):
    """Percentile CI for the horizon (in weeks) under the parametric bootstrap."""
    rng = np.random.default_rng(seed)
    mu_g = delta_g * 7.0
    reps = []
    for _ in range(B):
        rep = bootstrap_replicate(rng, y, x, b_hat, a_hat, sigma2, delta_g)
        if rep is None:
            continue
        h = solve_hstar(*rep, tau=tau)
        if h is not None and np.isfinite(h):
            reps.append(h * delta_g)
    if not reps:
        return None, None, None, 0
    lo, hi = np.percentile(reps, [2.5, 97.5])
    return float(lo), float(hi), float(np.std(reps, ddof=1)), len(reps)


# ---------------------------------------------------------------- phases

PHASES = [
    # key, series, window start, window end, mu_g (days), display name (zh)
    ("Delta",    "covid", "2021-07-03", "2021-07-31", 4.7, "COVID-19 Delta 暴发期"),
    ("Omicron",  "covid", "2021-12-04", "2022-01-01", 3.0, "COVID-19 Omicron 达峰期"),
    ("JN1",      "covid", "2023-12-16", "2024-01-13", 3.5, "COVID-19 JN.1 流行期"),
    ("flu22",    "flu",   "2022-10-08", "2022-11-05", 3.2, "流感 2022-23 暴发早期"),
    ("flu24",    "flu",   "2024-11-23", "2024-12-21", 3.2, "流感 2024-25 流行季"),
    ("rsv24",    "rsv",   "2024-11-09", "2024-12-07", 8.4, "RSV 2024-25 流行季"),
    ("rsv25",    "rsv",   "2025-11-08", "2025-12-06", 8.4, "RSV 2025-26 流行季"),
]

# Table 3 (phase-comparison) windows. I0/k are re-estimated on each window.
PHASES_T3 = [
    ("Delta_growth",   "covid", "2021-07-03", "2021-07-31", 4.7),
    ("Delta_peak",     "covid", "2021-08-28", "2021-10-02", 4.7),
    ("Delta_decline",  "covid", "2021-10-09", "2021-11-13", 4.7),
    ("Omicron_growth", "covid", "2021-12-04", "2022-01-01", 3.0),
    ("Omicron_decline","covid", "2022-01-08", "2022-02-05", 3.0),
    ("flu22_growth",   "flu",   "2022-10-08", "2022-11-05", 3.2),
    ("flu22_decline",  "flu",   "2022-12-03", "2022-12-31", 3.2),
]


def analyze_phase(series, w0, w1, mu_g):
    seg = series[(series.index >= w0) & (series.index <= w1)]
    y = np.log(seg.values.astype(float))
    b, se_b, a, sigma2, x = fit_loglinear(y)
    counts = seg.values.astype(float)
    k = estimate_k(counts)
    I0 = float(np.mean(counts))
    delta_g = mu_g / 7.0
    R = float(np.exp(delta_g * b))
    s = float(delta_g * se_b)
    h_gen = solve_hstar(R, s, k, I0)
    out = {
        "window": [w0, w1],
        "n_weeks": int(len(y)),
        "b_week": round(b, 4),
        "se_slope": round(se_b, 4),
        "mu_g_days": mu_g,
        "delta_g": round(delta_g, 4),
        "R_gen": round(R, 4),
        "s_gen": round(s, 4),
        "k_agg": round(k, 1),
        "I0": round(I0),
        "I0_total": int(round(counts.sum())),
    }
    if h_gen is not None:
        h_wk = h_gen * delta_g
        lo, hi, se_boot, nb = horizon_ci(R, s, k, I0, delta_g, b, a, sigma2, y, x)
        out.update({
            "h_star_gen": round(h_gen, 2),
            "h_star_weeks": round(h_wk, 2),
            "ci95_weeks": [round(lo, 2), round(hi, 2)],
            "boot_se_weeks": round(se_boot, 2),
            "n_boot_ok": nb,
            "hs_ratio": round(h_gen * s, 3),
        })
    else:
        out.update({"h_star_gen": None, "h_star_weeks": None,
                    "ci95_weeks": None, "boot_se_weeks": None, "n_boot_ok": 0})
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    manifest = {"seed": SEED, "B": B_BOOT, "tau": TAU, "k_cap": K_CAP,
                "inputs": {f: sha256(PROC / f) for f in
                           ["covid_final_weekly.csv.gz", "flu_final_weekly.csv.gz",
                            "rsv_final_weekly.csv.gz"]}}
    table2 = {}
    for key, src, w0, w1, mu_g, disp in PHASES:
        s = load_series(src)
        rec = analyze_phase(s, w0, w1, mu_g)
        rec["display"] = disp
        table2[key] = rec
        h = rec.get("h_star_weeks")
        print(f"[{key:8}] R={rec['R_gen']:.4f} s={rec['s_gen']:.4f} k={rec['k_agg']:7.1f} "
              f"I0={rec['I0']:6d} -> h*={h if h is None else round(h,2)} wk "
              f"(CI {[None if v is None else round(v,1) for v in rec['ci95_weeks']] if rec['ci95_weeks'] else None})",
              flush=True)

    table3 = {}
    for key, src, w0, w1, mu_g in PHASES_T3:
        s = load_series(src)
        table3[key] = analyze_phase(s, w0, w1, mu_g)
        h = table3[key].get("h_star_weeks")
        print(f"[t3:{key:16}] R={table3[key]['R_gen']:.4f} -> h*={h if h is None else round(h,2)} wk", flush=True)

    out = {"manifest": manifest, "table2": table2, "table3": table3}
    path = REPORTS / "table2_params.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"saved {path}", flush=True)


if __name__ == "__main__":
    main()


def crb_analysis(rec: dict) -> dict:
    """Theorem-4 required independent-cluster count for the observed relative SE."""
    s_rel = rec["s_gen"] / rec["R_gen"]
    c_req = (1.0 / rec["R_gen"] + 1.0 / rec["k_agg"]) / s_rel ** 2
    return {"C_req": round(c_req), "window_total": rec["I0_total"],
            "ratio": round(c_req / rec["I0_total"], 3),
            "violates": bool(c_req > rec["I0_total"])}
