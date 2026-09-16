# -*- coding: utf-8 -*-
"""Reframed analysis: conditional horizons and paired rolling losses.

This script deliberately keeps two estimands separate:
* H_mech is a root of the fixed-k aggregate negative-binomial variance model.
* operational audit losses are computed at the same origin, target, scale, and
  state for the log-linear predictor and two simple baselines.

No frozen Forecast Hub evaluation file is read here.
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
REPORTS.mkdir(exist_ok=True)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from macro_model import cv2_macro  # noqa: E402

TAU = 0.5
SEED = 20260807
PHASES = [
    ("Delta", "covid", "2021-07-03", "2021-07-31", 4.7),
    ("Omicron", "covid", "2021-12-04", "2022-01-01", 3.0),
    ("JN1", "covid", "2023-12-16", "2024-01-13", 3.5),
    ("flu22", "flu", "2022-10-08", "2022-11-05", 3.2),
    ("flu24", "flu", "2024-11-23", "2024-12-21", 3.2),
    ("rsv24", "rsv", "2024-11-09", "2024-12-07", 8.4),
    ("rsv25", "rsv", "2025-11-08", "2025-12-06", 8.4),
]
STATE_FIPS = {f"{i:02d}" for i in range(1, 57)}


def fit_loglinear(values: np.ndarray) -> tuple[float, float]:
    x = np.arange(len(values), dtype=float)
    y = np.log(values.astype(float))
    design = np.column_stack([x, np.ones(len(values))])
    coef, *_ = np.linalg.lstsq(design, y, rcond=None)
    residual = y - design @ coef
    s2 = np.sum(residual ** 2) / (len(values) - 2)
    slope_se = np.sqrt(s2 / np.sum((x - x.mean()) ** 2))
    return float(coef[0]), float(slope_se)


def estimate_k(values: np.ndarray) -> float:
    dlog = np.diff(np.log(values.astype(float)))
    mean = float(np.mean(values))
    variance = float(np.var(dlog, ddof=1))
    return float(min(1000.0, 1.0 / max(variance - 1.0 / mean, 1e-3)))


def parameter_risk(h: float, slope_se: float) -> float:
    x2 = (h * slope_se) ** 2
    return float(np.exp(2.0 * x2) - 2.0 * np.exp(0.5 * x2) + 1.0)


def mechanistic_horizon(values: np.ndarray, tau: float = TAU) -> float | None:
    slope, slope_se = fit_loglinear(values)
    growth = float(np.exp(slope))
    k = estimate_k(values)
    initial = float(np.mean(values))

    def risk(h: float) -> float:
        return float(cv2_macro(h, growth, k, initial)) + parameter_risk(h, slope_se)

    if not np.isfinite(risk(1e-3)) or risk(1e-3) > tau * tau:
        return None
    upper = 2.0
    while risk(upper) < tau * tau and upper < 1e4:
        upper *= 2.0
    return float(brentq(lambda h: risk(h) - tau * tau, 1e-3, upper))


def load_panels() -> dict[str, pd.DataFrame]:
    covid = pd.read_csv(PANELS / "covid_weekly_hospitalizations.csv.gz", parse_dates=["week_end_date"])
    covid = covid.rename(columns={"week_end_date": "week_end", "weekly_admissions": "value"})
    flu = pd.read_csv(PANELS / "flu_weekly_hospitalizations.csv.gz", parse_dates=["week_end"])
    rsv = pd.read_csv(PANELS / "rsv_weekly_hospitalizations.csv.gz", parse_dates=["week_end"])
    for frame in (covid, flu, rsv):
        frame["location"] = frame["location"].astype(str).str.zfill(2)
    return {"covid": covid, "flu": flu, "rsv": rsv}


def phase_series(panel: pd.DataFrame, location: str, start: str, end: str) -> pd.Series:
    frame = panel[panel["location"] == location].set_index("week_end")["value"].sort_index()
    return frame[(frame.index >= start) & (frame.index <= end)]


def horizon_summary(panels: dict[str, pd.DataFrame]) -> dict:
    result = {}
    for name, source, start, end, _ in PHASES:
        panel = panels[source]
        horizons: list[float] = []
        fit_states = 0
        for location in sorted(STATE_FIPS):
            values = phase_series(panel, location, start, end).to_numpy(dtype=float)
            if len(values) != 5 or values.sum() < 50 or np.any(values <= 0):
                continue
            horizon = mechanistic_horizon(values)
            if horizon is not None:
                horizons.append(horizon)
            fit_states += 1
        national = panel[panel["location"].isin(STATE_FIPS)].groupby("week_end")["value"].sum()
        national = national[(national.index >= start) & (national.index <= end)].to_numpy(dtype=float)
        result[name] = {
            "n_states": fit_states,
            "horizon_weeks": {
                "n": len(horizons),
                "median": float(np.median(horizons)) if horizons else None,
                "q25": float(np.percentile(horizons, 25)) if horizons else None,
                "q75": float(np.percentile(horizons, 75)) if horizons else None,
            },
            "national_horizon_weeks": mechanistic_horizon(national) if len(national) == 5 else None,
        }
    return result


def paired_losses(panels: dict[str, pd.DataFrame]) -> dict:
    """Collect loss differences at identical state/origin/target cells."""
    result = {}
    for name, source, start, end, _ in PHASES:
        panel = panels[source]
        rows: list[dict] = []
        for location in sorted(STATE_FIPS):
            series = panel[panel["location"] == location].set_index("week_end")["value"].sort_index()
            origins = [d for d in series.index if d >= pd.Timestamp(start) and int((series.index < d).sum()) >= 4][:6]
            for origin in origins:
                history = series[series.index <= origin].iloc[-4:].to_numpy(dtype=float)
                if len(history) != 4 or np.any(history <= 0):
                    continue
                slope, _ = fit_loglinear(history)
                ratio = history[-1] / max(history[-2], 1.0)
                scale = history[-1]
                for horizon in range(1, 9):
                    target_date = origin + pd.Timedelta(weeks=horizon)
                    if target_date not in series.index:
                        continue
                    truth = float(series.loc[target_date])
                    if truth <= 0:
                        continue
                    predictions = {
                        "model": scale * np.exp(slope * horizon),
                        "persistence": scale,
                        "local_linear": scale * ratio ** horizon,
                    }
                    losses = {key: ((value - truth) / scale) ** 2 for key, value in predictions.items()}
                    rows.append({"location": location, "origin": str(origin.date()), "horizon": horizon, **losses})
        frame = pd.DataFrame(rows)
        horizon_rows = {}
        rng = np.random.default_rng(SEED)
        for horizon in range(1, 9):
            subset = frame[frame["horizon"] == horizon]
            if subset.empty:
                continue
            states = subset["location"].unique()
            observed = {
                "n_cells": int(len(subset)),
                "n_states": int(len(states)),
                "model_loss": float(subset["model"].mean()),
                "persistence_loss": float(subset["persistence"].mean()),
                "local_linear_loss": float(subset["local_linear"].mean()),
            }
            observed["delta_model_minus_persistence"] = observed["model_loss"] - observed["persistence_loss"]
            observed["delta_model_minus_local_linear"] = observed["model_loss"] - observed["local_linear_loss"]
            boot_p, boot_l = [], []
            state_groups = {state: group for state, group in subset.groupby("location")}
            for _ in range(2000):
                sampled = rng.choice(states, size=len(states), replace=True)
                bootstrap = pd.concat([state_groups[state] for state in sampled], ignore_index=True)
                boot_p.append(float((bootstrap["model"] - bootstrap["persistence"]).mean()))
                boot_l.append(float((bootstrap["model"] - bootstrap["local_linear"]).mean()))
            observed["bootstrap_95ci_delta_persistence"] = [float(np.percentile(boot_p, 2.5)), float(np.percentile(boot_p, 97.5))]
            observed["bootstrap_95ci_delta_local_linear"] = [float(np.percentile(boot_l, 2.5)), float(np.percentile(boot_l, 97.5))]
            horizon_rows[str(horizon)] = observed
        result[name] = {"rows": int(len(frame)), "by_horizon": horizon_rows}
    return result


def main() -> None:
    panels = load_panels()
    summary = {"analysis": "reframed_v1", "tau": TAU, "bootstrap": {"unit": "state", "B": 2000, "seed": SEED}}
    summary["mechanistic_horizons"] = horizon_summary(panels)
    summary["paired_losses"] = paired_losses(panels)
    output = REPORTS / "reframed_summary.json"
    output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    for name, record in summary["mechanistic_horizons"].items():
        horizon = record["horizon_weeks"]["median"]
        print(f"{name:8s} states={record['n_states']:2d} H_mech_median={horizon}")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
