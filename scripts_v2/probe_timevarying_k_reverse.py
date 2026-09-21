# -*- coding: utf-8 -*-
"""Approach A, reverse direction: how much SMALLER must k_agg be to reach nominal?

The first probe scanned k upward (wider dispersion -> narrower intervals ->
lower coverage) and confirmed the monotone direction.  The question that
actually bears on the paper's attribution claim is the reverse one: at the
h=1 strict four-way cells, what k multiplier achieves 95% coverage in each
phase, and is the pre-peak requirement systematically larger than the
post-peak one?

Read the direction carefully:
  k_multipler < 1  =>  k_agg is DIVIDED  =>  larger dispersion  =>  wider
                       intervals  =>  higher coverage.

Output: reports_v3/timevarying_k_reverse.json, ASCII console.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts_v2"))

import flusight_audit_extended as fx  # noqa: E402

RELEASES = ("v1.0.0", "v1.1.0", "v1.2.0")

# Multipliers applied to each cell's own k_agg.  <1 widens the interval.
K_GRID = [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0078125, 0.00390625]

PHASE_ORDER = ("rising", "peak", "declining")


def release_dir(tag: str) -> Path:
    return ROOT / "data" / "flusight" / tag


def cells_for(tag: str):
    """Strict four-way h=1 cells with fitted params, truth and phase label."""
    rel = release_dir(tag)
    truth = fx.load_truth(rel)
    frames = []
    for model in ("ensemble", "baseline"):
        fc = fx.load_model(rel, model)
        if not fc.empty:
            frames.append(fc.assign(model=model))
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
    mech = fx.build_mechanistic(rel, cells)
    keep = mech[["reference_date", "location", "horizon"]].drop_duplicates()
    cells = cells.merge(keep, on=["reference_date", "location", "horizon"], how="inner")
    labels = fx.phase_labels(truth, cells)
    cells["phase"] = [labels.get((r, l), "unknown") for r, l in
                      zip(cells.reference_date, cells.location)]
    mech = mech.merge(
        cells[["reference_date", "location", "horizon", "truth", "phase"]],
        on=["reference_date", "location", "horizon"], how="inner",
    )
    return mech[mech.horizon == 1].copy()


def cover95(mech1, mult: float) -> float:
    """Share of cells whose 95% interval covers the truth at k*mult."""
    hits = 0
    for row in mech1.itertuples():
        _, qs = fx.mechanistic_quantiles(row.R, row.slope_se, row.k * mult, row.I0, 1)
        if float(qs[0]) <= row.truth <= float(qs[-1]):
            hits += 1
    return hits / len(mech1)


def mult_for_target(mech1, target: float):
    """Interpolate (log k) the multiplier reaching `target` coverage.

    Coverage is DECREASING in the multiplier (larger k => narrower interval
    => fewer hits), so ys is decreasing in xs.  np.interp needs an increasing
    abscissa, hence the reversal.
    """
    xs = np.log(np.array(K_GRID))
    ys = np.array([cover95(mech1, m) for m in K_GRID])
    if ys[-1] >= target:
        # widest interval in the grid still short of the target
        return float("inf"), ys[0]
    if ys[0] <= target:
        # baseline already covers at least `target`
        return None, ys[0]
    return float(np.exp(np.interp(target, ys[::-1], xs[::-1]))), ys[0]


def main() -> None:
    out = {}
    for tag in RELEASES:
        rel = release_dir(tag)
        if not rel.exists():
            continue
        print(f"=== {tag} ===", flush=True)
        mech1 = cells_for(tag)
        res = {
            "n_cells": int(len(mech1)),
            "phase_counts": mech1.phase.value_counts().to_dict(),
            "k_median": float(np.median(mech1.k.to_numpy(float))),
            "by_phase": {},
        }
        print(f"  cells={len(mech1)}  k_median={res['k_median']:.1f}  "
              f"phases={res['phase_counts']}")
        for ph in PHASE_ORDER:
            g = mech1[mech1.phase == ph]
            if len(g) == 0:
                continue
            m95, base = mult_for_target(g, 0.95)
            m90, _ = mult_for_target(g, 0.90)
            res["by_phase"][ph] = {
                "n": int(len(g)),
                "cover95_at_baseline": round(base, 4),
                "k_mult_for_0.95": (None if m95 is None else
                                    ("inf" if m95 == float("inf") else round(m95, 5))),
                "k_mult_for_0.90": (None if m90 is None else
                                    ("inf" if m90 == float("inf") else round(m90, 5))),
            }
            f95 = "baseline" if m95 is None else (
                "unreachable" if m95 == float("inf") else f"{m95:.4f}")
            f90 = "baseline" if m90 is None else (
                "unreachable" if m90 == float("inf") else f"{m90:.4f}")
            print(f"   {ph:9s} n={len(g):5d}  cov95(k)={base:.3f}   "
                  f"k_mult->0.95: {f95:>11s}   k_mult->0.90: {f90:>11s}")
        # ratio: how much MORE widening the pre-peak phase needs
        rp = res["by_phase"].get("rising", {}).get("k_mult_for_0.95")
        dp = res["by_phase"].get("declining", {}).get("k_mult_for_0.95")
        if isinstance(rp, float) and isinstance(dp, float) and dp > 0:
            res["pre_over_post_ratio"] = round(rp / dp, 4)
            print(f"   -> pre-peak needs {rp / dp:.2f}x the widening of post-peak")
        out[tag] = res
        print()

    (ROOT / "reports_v3" / "timevarying_k_reverse.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print("[OK] reports_v3/timevarying_k_reverse.json")


if __name__ == "__main__":
    main()
