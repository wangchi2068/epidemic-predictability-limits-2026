# -*- coding: utf-8 -*-
"""Approach A: does a time-varying k_agg remove the pre-peak coverage gap?

Design note -- what is and is not rolling in the current predictor
------------------------------------------------------------------
`flusight_audit_extended.build_mechanistic` already re-estimates k_agg at
EVER origin from that origin's own trailing 5-week window (line: k =
estimate_k(window.iloc[-5:])).  So the baseline predictor is *not* a
single fixed-k model in the FluSight application -- it is a locally
re-fitted one.  What is fixed is the *structural form*: a single k per
origin, 5 weeks of data, no allowance for the dispersion being different
before vs after the peak.

This script therefore tests the structural question directly.  For each
strict four-way cell we recompute the 23 mechanistic quantiles under a
grid of k multipliers applied to that cell's own estimated k, and report
how the 95% coverage responds by epidemic phase.  Two diagnostics follow:

  (1) phase contrast -- the k that achieves nominal coverage in the
      pre-peak phase vs the post-peak phase.  If the two are close, the
      static-variance-misspecification explanation is weakened; if the
      pre-peak phase needs a systematically SMALLER k (wider intervals),
      the time-varying-dispersion story gains support.

  (2) identifiability -- the sampling distribution of the 5-week
      log-difference k estimate.  With ~4 differenced observations the
      estimator is extremely noisy; this is what decides whether any
      rolling-k scheme can actually be estimated from 5 weeks of data.

Output: reports_v3/timevarying_k_probe.json (ASCII console print).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts_v2"))

import flusight_audit_extended as fx  # noqa: E402

RELEASES = {
    "v1.0.0": "2023-10-14/2024-05-04",
    "v1.1.0": "2024-11-23/2025-05-31",
    "v1.2.0": "2025-11-22/2026-05-30",
}

# k multipliers: 1.0 = as published.  >1 means wider (smaller dispersion).
K_GRID = [1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 20.0]


def release_dir(tag: str) -> Path:
    return ROOT / "data" / "flusight" / tag


def cells_for(tag: str) -> pd.DataFrame:
    """Rebuild the strict four-way cell table (same as the audit run)."""
    rel = release_dir(tag)
    rng = np.random.default_rng(fx.SEED)
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


def coverage_at(mech1: pd.DataFrame, mult: float) -> dict:
    """95% coverage per phase at a given k multiplier."""
    out = {}
    for ph, g in mech1.groupby("phase"):
        if len(g) == 0:
            continue
        hits = 0
        for row in g.itertuples():
            _, qs = fx.mechanistic_quantiles(
                row.R, row.slope_se, row.k * mult, row.I0, 1)
            lo, hi = float(qs[0]), float(qs[-1])
            if lo <= row.truth <= hi:
                hits += 1
        out[ph] = {"n": int(len(g)), "cover95": hits / len(g)}
    return out


def main() -> None:
    all_out = {}
    for tag in RELEASES:
        rel = release_dir(tag)
        if not rel.exists():
            print(f"[skip] {tag}: {rel} not found")
            continue
        print(f"=== {tag} ===", flush=True)
        mech1 = cells_for(tag)
        print(f"  strict h=1 cells: {len(mech1)}  "
              f"phases: {mech1.phase.value_counts().to_dict()}")
        base_k = mech1.k.to_numpy(float)
        print(f"  k_agg: median {np.median(base_k):.1f}  "
              f"IQR [{np.percentile(base_k, 25):.1f}, "
              f"{np.percentile(base_k, 75):.1f}]")
        res = {"n_cells": int(len(mech1)),
               "phase_counts": mech1.phase.value_counts().to_dict(),
               "k_median": float(np.median(base_k)),
               "by_mult": {}}
        for m in K_GRID:
            cov = coverage_at(mech1, m)
            res["by_mult"][str(m)] = cov
            print(f"   k x{m:<5g} " + "  ".join(
                f"{ph}={cov[ph]['cover95']:.3f}(n={cov[ph]['n']})"
                for ph in sorted(cov)))
        all_out[tag] = res
        print()

    (ROOT / "reports_v3" / "timevarying_k_probe.json").write_text(
        json.dumps(all_out, indent=2), encoding="utf-8")
    print("[OK] reports_v3/timevarying_k_probe.json")


if __name__ == "__main__":
    main()
