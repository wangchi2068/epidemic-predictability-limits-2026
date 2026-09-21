# -*- coding: utf-8 -*-
"""Approach A, decomposed: is the pre-peak failure a WIDTH problem or a
LOCATION problem?

The first reverse scan showed that widening the interval cannot restore
nominal coverage in the rising phase, and that the 50% coverage is ~0
everywhere.  That points at the predictive MEDIAN being wrong rather than
the dispersion being too small.  This script separates the two by
reporting, per phase:

  cover95 / cover50           -- as published
  median signed error          -- (predicted median - truth) / truth, median
  |error| at the optimal shift -- after shifting the whole predictive law by
                                 its own per-cell median error, how much of
                                 the residual gap does widening k still close?

If a per-cell location correction alone brings cover95 close to nominal,
the pre-peak gap is dominated by median bias (a growth-model misspecification),
not by the static-k variance assumption the manuscript's attribution section
is built around.
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
K_GRID = [1.0, 0.25, 0.0625, 0.015625, 0.00390625]
PHASES = ("rising", "peak", "declining")


def cells_for(tag: str):
    rel = ROOT / "data" / "flusight" / tag
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
        truth=[truth.get((l, e), np.nan)
               for l, e in zip(cells.location, cells.target_end_date)]
    )
    cells = cells[cells.truth.notna()].drop(columns="target_end_date")
    mech = fx.build_mechanistic(rel, cells)
    keep = mech[["reference_date", "location", "horizon"]].drop_duplicates()
    cells = cells.merge(keep, on=["reference_date", "location", "horizon"], how="inner")
    lab = fx.phase_labels(truth, cells)
    cells["phase"] = [lab.get((r, l), "unknown")
                      for r, l in zip(cells.reference_date, cells.location)]
    mech = mech.merge(
        cells[["reference_date", "location", "horizon", "truth", "phase"]],
        on=["reference_date", "location", "horizon"], how="inner",
    )
    return mech[mech.horizon == 1].copy()


def cover(g, mult, shift, level_idx):
    """Coverage of a central interval after k-scaling and a median shift.

    shift: multiplicative factor applied to the whole predictive law
           (1.0 = no location correction).
    """
    lo_i, hi_i = level_idx
    hits = 0
    for row in g.itertuples():
        _, qs = fx.mechanistic_quantiles(row.R, row.slope_se, row.k * mult, row.I0, 1)
        q = qs * shift
        if q[lo_i] <= row.truth <= q[hi_i]:
            hits += 1
    return hits / len(g)


def optimal_shift(g):
    """Multiplicative shift of the predictive law that maximises 50% coverage.

    Uses the per-cell truth to build the empirical best shift -- this is an
    ORACLE diagnostic, i.e. an upper bound on what any location model could
    recover, not a deployable rule.
    """
    ratios = []
    for row in g.itertuples():
        _, qs = fx.mechanistic_quantiles(row.R, row.slope_se, row.k, row.I0, 1)
        med = float(qs[11])
        if med > 0 and row.truth > 0:
            ratios.append(row.truth / med)
    return float(np.median(ratios)) if ratios else 1.0


def main() -> None:
    out = {}
    for tag in RELEASES:
        rel = ROOT / "data" / "flusight" / tag
        if not rel.exists():
            continue
        print(f"=== {tag} ===", flush=True)
        mech1 = cells_for(tag)
        res = {}
        for ph in PHASES:
            g = mech1[mech1.phase == ph]
            if len(g) == 0:
                continue
            # oracle location correction
            s_star = optimal_shift(g)
            row = {"n": int(len(g)), "oracle_shift": round(s_star, 4)}
            for m in K_GRID:
                row[f"c95_k{m}"] = round(cover(g, m, 1.0, fx.LEVELS[95]), 4)
                row[f"c95_k{m}_shift"] = round(
                    cover(g, m, s_star, fx.LEVELS[95]), 4)
            row["c50_base"] = round(cover(g, 1.0, 1.0, fx.LEVELS[50]), 4)
            row["c50_base_shift"] = round(cover(g, 1.0, s_star, fx.LEVELS[50]), 4)
            res[ph] = row
            print(f"  {ph:9s} n={len(g):5d} oracle_shift={s_star:6.3f}  "
                  f"c50={row['c50_base']:.3f}->{row['c50_base_shift']:.3f}")
            print(f"      c95 by k: " + "  ".join(
                f"{m:g}:{row[f'c95_k{m}']:.3f}/{row[f'c95_k{m}_shift']:.3f}"
                for m in K_GRID) + "   (no-shift / oracle-shift)")
        out[tag] = res
        print()

    (ROOT / "reports_v3" / "timevarying_k_decomposed.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print("[OK] reports_v3/timevarying_k_decomposed.json")


if __name__ == "__main__":
    main()
