"""Extended versioned external audit for the reframed manuscript.

Two things this adds over `score_flusight.py`:

1. A full score palette on the identical locked cells -- the 23-quantile WIS and
   its exact additive decomposition (sharpness, under-prediction,
   over-prediction), MAE, 50/80/95% interval coverage, mean interval width, and
   a randomized-PIT histogram -- plus stratification by horizon, epidemic phase,
   and state.

2. The manuscript's own fixed-k aggregate negative-binomial predictor scored as
   a fourth forecast on the *same* origin--state--horizon cells.  This measures
   the calibration gap of the model-conditional benchmark against operational
   forecasters without making any cross-scale mechanism claim: it is a paired
   loss audit, nothing more.

Honesty boundaries that the code enforces:

* Forecasts are final-vintage.  The mechanistic predictor is fit on the
  final-vintage target file truncated to `reference_date - 7 days`, i.e. the
  observations a submitter would have had, but with their *revised* values.
  This is a hindsight-fit benchmark, not a real-time reanalysis.  Every output
  records `vintage = "final"`.
* Cells dropped for a guard (non-positive count window, missing truth,
  non-23-quantile grid) are counted and reported, never silently discarded.

Usage:
    python scripts_v2/flusight_audit_extended.py \
        --release data/flusight/v1.0.0 --start-date 2023-10-14 --end-date 2024-05-04 \
        --output reports_v3/flusight_v1.0_extended.json \
        --csv   reports_v3/flusight_v1.0_extended.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

FIPS = {f"{i:02d}" for i in range(1, 57)}
Q23 = np.array(
    [
        0.01,
        0.025,
        0.05,
        0.1,
        0.15,
        0.2,
        0.25,
        0.3,
        0.35,
        0.4,
        0.45,
        0.5,
        0.55,
        0.6,
        0.65,
        0.7,
        0.75,
        0.8,
        0.85,
        0.9,
        0.95,
        0.975,
        0.99,
    ]
)
# Central interval pair indices into Q23 for the 50/80/95% intervals.
LEVELS = {50: (6, 16), 80: (3, 19), 95: (1, 21)}
LOWER = Q23[:11]  # 0.01 ... 0.45, the 11 interval tails
MEDIAN_INDEX = 11
SEED = 20260914


# ---------------------------------------------------------------- scoring ---


def wis_decomposed(values: np.ndarray, truth: float) -> dict:
    """23-quantile WIS and its exact additive decomposition.

    Values are a (..., 23) array in ascending quantile order.  The 11 symmetric
    interval pairs run (0.01, 0.99) ... (0.45, 0.55); the score is
        wis = (0.5*|y-m| + spread + under + over) / 11.5
    with spread/under/over the sharpness, under-prediction, and over-prediction
    terms.  The identity is checked against `reframed_statistics.quantile_wis`.
    """
    v = np.asarray(values, dtype=float)
    lower = v[..., :MEDIAN_INDEX]
    upper = v[..., :MEDIAN_INDEX:-1]
    median = v[..., MEDIAN_INDEX]
    alpha = 2.0 * LOWER
    spread = float(np.sum(alpha / 2.0 * (upper - lower)))
    over = float(np.sum(np.maximum(lower - truth, 0.0)))
    under = float(np.sum(np.maximum(truth - upper, 0.0)))
    point = float(0.5 * abs(median - truth))
    return {
        "wis": (point + spread + under + over) / 11.5,
        "point": point / 11.5,
        "spread": spread / 11.5,
        "under": under / 11.5,
        "over": over / 11.5,
    }


def coverage_and_width(values: np.ndarray, truth: float) -> dict:
    v = np.asarray(values, dtype=float)
    out = {}
    for level, (lo, hi) in LEVELS.items():
        low, high = v[..., lo], v[..., hi]
        out[f"cover{level}"] = float(np.mean((truth >= low) & (truth <= high)))
        out[f"width{level}"] = float(np.mean(high - low))
    return out


def randomized_pit(values: np.ndarray, truth: float, rng: np.random.Generator) -> float:
    """Randomized probability integral transform for a quantile grid.

    Inside the grid the PIT interpolates linearly in the quantile level; the two
    tails are filled uniformly so the transform is approximately uniform under
    correct calibration of the reconstructed piecewise-quantile distribution.
    """
    v = np.asarray(values, dtype=float)
    if truth <= v[0]:
        return float(rng.uniform(0.0, Q23[0]))
    if truth >= v[-1]:
        return float(rng.uniform(Q23[-1], 1.0))
    k = int(np.searchsorted(v, truth, side="right")) - 1
    k = min(max(k, 0), len(Q23) - 2)
    span = v[k + 1] - v[k]
    frac = 0.0 if span <= 0 else (truth - v[k]) / span
    return float(Q23[k] + frac * (Q23[k + 1] - Q23[k]))


# ----------------------------------------------------- mechanistic model ---


def fit_window(values: np.ndarray) -> tuple[float, float, float] | None:
    """Log-linear window fit returning (R, slope_se, I0); None if inadmissible."""
    y = np.asarray(values, dtype=float)
    if len(y) < 4 or np.any(y <= 0):
        return None
    x = np.arange(len(y), dtype=float)
    logy = np.log(y)
    design = np.column_stack([x, np.ones(len(y))])
    coef, *_ = np.linalg.lstsq(design, logy, rcond=None)
    residual = logy - design @ coef
    s2 = float(np.sum(residual**2) / (len(y) - 2))
    slope_se = float(np.sqrt(s2 / np.sum((x - x.mean()) ** 2)))
    return float(np.exp(coef[0])), slope_se, float(np.mean(y))


def estimate_k(values: np.ndarray) -> float:
    dlog = np.diff(np.log(np.asarray(values, dtype=float)))
    mean = float(np.mean(values))
    variance = float(np.var(dlog, ddof=1))
    return float(min(1000.0, 1.0 / max(variance - 1.0 / mean, 1e-3)))


def macro_cv2(h, R, k, I0):
    """Relative variance of the fixed-k aggregate NB update (macro_model.py)."""
    h = np.asarray(h, dtype=float)
    if R <= 0 or k <= 0 or I0 <= 0:
        return np.full_like(h, np.nan)
    q = R * R * (1.0 + 1.0 / k)
    if abs(R - 1.0) < 1e-9:
        return (k / I0 + 1.0) * ((1.0 + 1.0 / k) ** h - 1.0)
    if abs(q - R) < 1e-12:
        first = I0 * R * h * R ** (h - 1.0)
    else:
        first = I0 * R * (q**h - R**h) / (q - R)
    second = I0 * I0 * (q**h - R ** (2.0 * h))
    return (first + second) / (I0 * R**h) ** 2


def mechanistic_quantiles(
    R: float, se: float, k: float, I0: float, h: int
) -> tuple[np.ndarray, np.ndarray]:
    """Mean and 23 quantiles of the plug-in predictive law at horizon h.

    Process variance is the exact macro closed form; the parameter-propagation
    term P(h) = exp(2 h^2 s^2) - 2 exp(h^2 s^2 / 2) + 1 is added in relative
    variance units, exactly as in the manuscript's horizon definition.
    """
    hh = np.asarray([h], dtype=float)
    cv2 = float(macro_cv2(hh, R, k, I0)[0])
    P = float(np.exp(2.0 * h * h * se * se) - 2.0 * np.exp(h * h * se * se / 2.0) + 1.0)
    mean = I0 * R**h
    var = (cv2 + P) * mean**2
    var = max(var, mean)  # floor at Poisson so NB size > 0
    size = mean**2 / (var - mean)
    qs = stats.nbinom.ppf(Q23, size, size / (size + mean))
    qs = np.maximum.accumulate(np.maximum(qs, 0.0))
    return np.asarray([mean]), qs


# ------------------------------------------------------------- data load ---


def load_truth(release: Path) -> pd.Series:
    t = pd.read_csv(release / "target-hospital-admissions.csv")
    t.date = pd.to_datetime(t.date)
    t.location = t.location.astype(str).str.zfill(2)
    t = t[t.location.isin(FIPS)]
    return t.set_index(["location", "date"]).value.sort_index()


def load_model(release: Path, model: str) -> pd.DataFrame:
    files = sorted((release / model).glob("*.csv"))
    if not files:
        return pd.DataFrame()
    fc = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    fc.location = fc.location.astype(str).str.zfill(2)
    fc.reference_date = pd.to_datetime(fc.reference_date)
    fc.target_end_date = pd.to_datetime(fc.target_end_date)
    fc = fc[
        (fc.location.isin(FIPS))
        & (fc.target == "wk inc flu hosp")
        & (fc.output_type == "quantile")
        & (fc.horizon.isin([1, 2, 3]))
    ]
    fc["horizon"] = fc.horizon.astype(int)
    rows = []
    for key, g in fc.groupby(
        ["reference_date", "location", "horizon", "target_end_date"]
    ):
        g = g.sort_values("output_type_id")
        v = g.value.to_numpy(float)
        if len(v) != 23 or not np.allclose(g.output_type_id.to_numpy(float), Q23):
            continue
        rows.append((key[0], key[1], key[2], key[3], v))
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(
        rows,
        columns=["reference_date", "location", "horizon", "target_end_date", "value"],
    )


def build_mechanistic(release: Path, cells: pd.DataFrame) -> pd.DataFrame:
    """Score the fixed-k NB predictor on the supplied origin--state--horizon cells."""
    t = pd.read_csv(release / "target-hospital-admissions.csv")
    t.date = pd.to_datetime(t.date)
    t.location = t.location.astype(str).str.zfill(2)
    history = {
        loc: g.sort_values("date").set_index("date").value
        for loc, g in t.groupby("location")
    }
    out = []
    for (ref, loc), g in cells.groupby(["reference_date", "location"]):
        series = history.get(loc)
        if series is None:
            continue
        cutoff = pd.Timestamp(ref) - pd.Timedelta(days=7)
        window = series[series.index <= cutoff]
        if len(window) < 5:
            continue
        fit = fit_window(window.iloc[-5:].to_numpy(float))
        if fit is None:
            continue
        R, se, I0 = fit
        k = estimate_k(window.iloc[-5:].to_numpy(float))
        for h in sorted(g.horizon.unique()):
            _, qs = mechanistic_quantiles(R, se, k, I0, int(h))
            out.append((pd.Timestamp(ref), loc, int(h), R, se, k, I0, qs))
    return pd.DataFrame(
        out,
        columns=[
            "reference_date",
            "location",
            "horizon",
            "R",
            "slope_se",
            "k",
            "I0",
            "value",
        ],
    )


# --------------------------------------------------------------- auditing ---


def phase_labels(truth: pd.Series, cells: pd.DataFrame) -> dict:
    """Classify each origin as rising / peak / declining from the season curve."""
    peak = {}
    for loc, g in truth.groupby(level=0):
        peak[loc] = g.idxmax()[1]
    labels = {}
    for ref, loc in (
        cells[["reference_date", "location"]].drop_duplicates().itertuples(index=False)
    ):
        p = peak.get(loc)
        if p is None:
            labels[(pd.Timestamp(ref), loc)] = "unknown"
        elif abs((pd.Timestamp(ref) - p).days) <= 7:
            labels[(pd.Timestamp(ref), loc)] = "peak"
        elif pd.Timestamp(ref) < p:
            labels[(pd.Timestamp(ref), loc)] = "rising"
        else:
            labels[(pd.Timestamp(ref), loc)] = "declining"
    return labels


def summarize(
    df: pd.DataFrame, group_cols: list[str], rng: np.random.Generator
) -> list[dict]:
    rows = []
    for key, g in df.groupby(group_cols):
        key = key if isinstance(key, tuple) else (key,)
        rec = dict(zip(group_cols, key, strict=False))
        rec["n"] = int(len(g))
        rec["wis"] = float(g.wis.mean())
        rec["mae"] = float(g.mae.mean())
        rec["point"] = float(g.point.mean())
        rec["spread"] = float(g.spread.mean())
        rec["under"] = float(g.under.mean())
        rec["over"] = float(g.over.mean())
        for level in LEVELS:
            rec[f"cover{level}"] = float(g[f"cover{level}"].mean())
            rec[f"width{level}"] = float(g[f"width{level}"].mean())
        rec["pit_mean"] = float(g.pit.mean())
        rows.append(rec)
    return rows


def moving_block_ci(
    frame: pd.DataFrame, block: int, replicates: int, rng: np.random.Generator
) -> np.ndarray:
    """Moving-block bootstrap over origin weeks for the mean of `frame.value`."""
    origins = np.array(sorted(frame.reference_date.unique()), dtype="datetime64[ns]")
    if len(origins) == 0:
        return np.array([np.nan, np.nan])
    by_origin = {
        pd.Timestamp(o): frame[frame.reference_date == o].value.mean() for o in origins
    }
    values = np.array([by_origin[pd.Timestamp(o)] for o in origins], dtype=float)
    n = len(values)
    n_blocks = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=(replicates, n_blocks))
    idx = ((starts[..., None] + np.arange(block)) % n).reshape(replicates, -1)[:, :n]
    means = values[idx].mean(axis=1)
    return np.percentile(means, [2.5, 97.5])


def run(
    release: Path, start: str | None, end: str | None, block: int, replicates: int
) -> tuple[dict, pd.DataFrame]:
    rng = np.random.default_rng(SEED)
    truth = load_truth(release)
    frames, dropped = [], {}

    for model in ("ensemble", "baseline"):
        fc = load_model(release, model)
        if fc.empty:
            continue
        if start:
            fc = fc[fc.reference_date >= pd.Timestamp(start)]
        if end:
            fc = fc[fc.reference_date <= pd.Timestamp(end)]
        frames.append(fc.assign(model=model))
        dropped[model] = {"after_date_filter": int(len(fc))}

    # Restrict every model to the cells all models share, then attach truth.
    common = frames[0][["reference_date", "location", "horizon", "target_end_date"]]
    for fr in frames[1:]:
        common = common.merge(
            fr[["reference_date", "location", "horizon"]],
            on=["reference_date", "location", "horizon"],
        )
    cells = common.drop_duplicates(subset=["reference_date", "location", "horizon"])
    cells = cells.assign(
        truth=[
            truth.get((loc, end), np.nan)
            for loc, end in zip(cells.location, cells.target_end_date, strict=False)
        ]
    )
    cells = cells[cells.truth.notna()].drop(columns="target_end_date")

    mech = build_mechanistic(release, cells)
    if not mech.empty:
        mech = mech[["reference_date", "location", "horizon", "value"]].assign(
            model="mechanistic"
        )
        # Strict four-way intersection: retain only cells where EVERY model
        # (ensemble, baseline, mechanistic) also has a value under the same
        # final-vintage truth.  Without this step the mechanistic benchmark is
        # scored on a strict subset and its WIS is not paired-comparable.
        keep = mech[["reference_date", "location", "horizon"]].drop_duplicates()
        cells = cells.merge(
            keep, on=["reference_date", "location", "horizon"], how="inner"
        )

    scored = []
    for fr in frames + ([mech] if not mech.empty else []):
        merged = fr.merge(
            cells[["reference_date", "location", "horizon", "truth"]],
            on=["reference_date", "location", "horizon"],
            how="inner",
        )
        merged = merged[merged.truth.notna()]
        for row in merged.itertuples(index=False):
            d = wis_decomposed(row.value, float(row.truth))
            d.update(coverage_and_width(row.value, float(row.truth)))
            d["pit"] = randomized_pit(row.value, float(row.truth), rng)
            d["mae"] = abs(float(row.value[MEDIAN_INDEX]) - float(row.truth))
            scored.append(
                dict(
                    model=row.model,
                    reference_date=row.reference_date,
                    location=row.location,
                    horizon=row.horizon,
                    **d,
                )
            )
    cell_df = pd.DataFrame(scored)
    if cell_df.empty:
        raise SystemExit("no scorable cells; check the release directory")

    labels = phase_labels(truth, cells)
    cell_df["phase"] = [
        labels.get((r.reference_date, r.location), "unknown")
        for r in cell_df.itertuples(index=False)
    ]

    models = sorted(cell_df.model.unique())
    result = {
        "release": release.name,
        "vintage": "final",
        "provenance": {
            "protocol": "scripts_v2/flusight_audit_extended.py",
            "base_scorer": "scripts_v2/score_flusight.py",
        },
        "bootstrap": {
            "B": replicates,
            "block_weeks": block,
            "unit": "origin_week",
            "seed": SEED,
        },
        "models": models,
        "n_cells": int(len(cell_df)),
        "by_horizon": {},
        "by_phase": {},
        "by_state": {},
        "paired_vs_ensemble": {},
        "dropped": dropped,
    }

    for h, g in cell_df.groupby("horizon"):
        rec = {
            "n": int(len(g)),
            "n_origins": int(g.reference_date.nunique()),
            "n_states": int(g.location.nunique()),
            "by_model": {
                d["model"]: {k: v for k, v in d.items() if k != "model"}
                for d in summarize(g, ["model"], rng)
            },
        }
        for m in models:
            sub = g[g.model == m].assign(value=lambda x: x.wis)
            rec["by_model"][m]["wis_ci95"] = [
                float(x) for x in moving_block_ci(sub, block, replicates, rng)
            ]
        if "ensemble" in models:
            rec["paired_vs_ensemble"] = {}
            for m in models:
                if m == "ensemble":
                    continue
                a = g[g.model == "ensemble"].set_index(["reference_date", "location"])[
                    ["wis", "mae"]
                ]
                b = g[g.model == m].set_index(["reference_date", "location"])[
                    ["wis", "mae"]
                ]
                both = a.join(
                    b, lsuffix="_ens", rsuffix="_alt", how="inner"
                ).reset_index()
                both["d_wis"] = both.wis_alt - both.wis_ens
                both["d_mae"] = both.mae_alt - both.mae_ens
                rec["paired_vs_ensemble"][m] = {
                    "n_pairs": int(len(both)),
                    "delta_wis": float(both.d_wis.mean()),
                    "delta_mae": float(both.d_mae.mean()),
                    "delta_wis_ci95": [
                        float(x)
                        for x in moving_block_ci(
                            both.assign(value=both.d_wis), block, replicates, rng
                        )
                    ],
                }
        result["by_horizon"][str(int(h))] = rec

    # Phase summaries are reported per horizon so that a table labelled h=1 is
    # genuinely h=1; the pooled variant is kept under a separate key.
    result["by_phase"] = {
        p: summarize(g, ["model"], rng)
        for p, g in cell_df[cell_df.horizon == 1].groupby("phase")
    }
    result["by_phase_by_horizon"] = {
        str(int(h)): {
            p: summarize(g, ["model"], rng)
            for p, g in cell_df[cell_df.horizon == h].groupby("phase")
        }
        for h in sorted(cell_df.horizon.unique())
    }
    result["by_state"] = summarize(cell_df, ["model", "location"], rng)
    return result, cell_df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", type=Path, required=True)
    ap.add_argument("--start-date")
    ap.add_argument("--end-date")
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--csv", type=Path)
    ap.add_argument("--block", type=int, default=4)
    ap.add_argument("--B", type=int, default=2000)
    a = ap.parse_args()
    result, cells = run(a.release, a.start_date, a.end_date, a.block, a.B)
    a.output.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    if a.csv:
        cells.to_csv(a.csv, index=False)
    print(
        json.dumps({k: result[k] for k in ("release", "n_cells", "models")}, indent=2)
    )
    for h, rec in result["by_horizon"].items():
        print(
            f"h{h}: "
            + " | ".join(
                f"{m} WIS={rec['by_model'][m]['wis']:.2f} cov95={rec['by_model'][m]['cover95']:.3f}"
                for m in result["models"]
            )
        )


if __name__ == "__main__":
    main()
