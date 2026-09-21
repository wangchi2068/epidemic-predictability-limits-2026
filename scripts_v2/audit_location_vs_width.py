# -*- coding: utf-8 -*-
"""Is the pre-peak failure LOCATION or WIDTH?  Independent re-derivation.

Three checks, each designed to be able to REFUTE the location story:

  C1  Sign structure of the per-cell relative median error, by phase.
      If the pre-peak phase is dominated by UNDER-prediction (model median
      below truth) while post-peak is dominated by OVER-prediction, the
      location bias has a coherent dynamical sign rather than being noise.

  C2  Can ANY dispersion setting reach nominal coverage?  Scan k over a
      very wide grid and report the best achievable c95 per phase.  If a
      phase cannot reach 0.95 even at k -> 0, width alone cannot explain
      the gap.  (k -> 0 means NB size -> 0, a wildly over-dispersed law.)

  C3  Is the oracle shift STABLE across seasons?  A per-cell oracle shift
      can always be fitted.  What matters is whether the PHASE-LEVEL
      median shift repeats across three independent seasons.  If the
      pre-peak shift is systematically > 1 in all three, it is a real
      property of the predictor, not a coincidence of one season.

ASCII output only.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts_v2"))

import flusight_audit_extended as fx  # noqa: E402

RELEASES = ("v1.0.0", "v1.1.0", "v1.2.0")
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


def median_rel_error(g) -> dict:
    """Median and IQR of (predicted median - truth)/truth, per cell.

    Cells with truth == 0 have no defined relative error and are dropped
    (they are counted and reported so the exclusion is visible).
    """
    v = []
    dropped = 0
    for row in g.itertuples():
        if not (row.truth > 0):
            dropped += 1
            continue
        _, qs = fx.mechanistic_quantiles(row.R, row.slope_se, row.k, row.I0, 1)
        v.append((float(qs[11]) - row.truth) / row.truth)
    v = np.array(v)
    return {"median": float(np.median(v)),
            "q25": float(np.percentile(v, 25)),
            "q75": float(np.percentile(v, 75)),
            "share_under": float(np.mean(v < 0)),
            "n_used": int(len(v)),
            "n_dropped_zero_truth": int(dropped)}


def best_cover95(g, grid) -> tuple[float, float]:
    """(best c95 over the k grid, the k multiplier achieving it)."""
    best, best_m = -1.0, None
    for m in grid:
        hits = 0
        for row in g.itertuples():
            _, qs = fx.mechanistic_quantiles(row.R, row.slope_se, row.k * m, row.I0, 1)
            if float(qs[1]) <= row.truth <= float(qs[21]):
                hits += 1
        c = hits / len(g)
        if c > best:
            best, best_m = c, m
    return best, best_m


def main() -> None:
    k_wide = [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625,
              0.0078125, 0.00390625, 0.001953125]
    print("=" * 96)
    print("C1  per-cell signed relative median error  (predicted median - truth)/truth")
    print("=" * 96)
    print(f"{'season':8s} {'phase':9s} {'n':>5s} {'median':>8s} {'IQR':>18s} "
          f"{'share under':>11s}")
    c1 = {}
    for tag in RELEASES:
        m1 = cells_for(tag)
        c1[tag] = {}
        for ph in PHASES:
            g = m1[m1.phase == ph]
            if not len(g):
                continue
            s = median_rel_error(g)
            c1[tag][ph] = s
            print(f"{tag:8s} {ph:9s} {len(g):5d} {s['median']:+8.3f} "
                  f"[{s['q25']:+6.3f},{s['q75']:+6.3f}] {s['share_under']:11.3f}")
        print()

    print("=" * 96)
    print("C2  best achievable c95 over k in [1/512, 1]  -- can width alone fix it?")
    print("=" * 96)
    print(f"{'season':8s} {'phase':9s} {'n':>5s} {'best c95':>9s} {'at k*':>9s}")
    c2 = {}
    for tag in RELEASES:
        m1 = cells_for(tag)
        c2[tag] = {}
        for ph in PHASES:
            g = m1[m1.phase == ph]
            if not len(g):
                continue
            b, bm = best_cover95(g, k_wide)
            c2[tag][ph] = {"best_c95": round(b, 4), "k_mult": bm}
            print(f"{tag:8s} {ph:9s} {len(g):5d} {b:9.3f} {bm:9.5g}")
        print()

    print("=" * 96)
    print("C3  oracle phase-level shift, cross-season stability")
    print("=" * 96)
    print(f"{'season':8s} {'rising':>9s} {'peak':>9s} {'declining':>10s}")
    c3 = {}
    for tag in RELEASES:
        m1 = cells_for(tag)
        vals = {}
        for ph in PHASES:
            g = m1[m1.phase == ph]
            if not len(g):
                vals[ph] = float("nan")
                continue
            ratios = []
            for row in g.itertuples():
                _, qs = fx.mechanistic_quantiles(row.R, row.slope_se, row.k, row.I0, 1)
                med = float(qs[11])
                if med > 0 and row.truth > 0:
                    ratios.append(row.truth / med)
            vals[ph] = float(np.median(ratios)) if ratios else float("nan")
        c3[tag] = vals
        print(f"{tag:8s} {vals['rising']:9.3f} {vals['peak']:9.3f} "
              f"{vals['declining']:10.3f}")

    print()
    rising = [c3[t]["rising"] for t in RELEASES]
    declining = [c3[t]["declining"] for t in RELEASES]
    print(f"rising   shift across seasons: {[round(v,3) for v in rising]}"
          f"  -> all > 1? {all(v > 1 for v in rising)}")
    print(f"declining shift across seasons: {[round(v,3) for v in declining]}"
          f"  -> all < 1? {all(v < 1 for v in declining)}")
    print()
    unreachable = {t: [p for p, r in c2[t].items() if r["best_c95"] < 0.90]
                   for t in RELEASES}
    print("phases whose c95 stays below 0.90 even at the widest k:")
    for t, ps in unreachable.items():
        print(f"  {t}: {ps}")

    (ROOT / "reports_v3" / "location_vs_width_audit.json").write_text(
        __import__("json").dumps(
            {"c1_signed_error": c1, "c2_best_cover95": c2, "c3_oracle_shift": c3},
            indent=2), encoding="utf-8")
    print("\n[OK] reports_v3/location_vs_width_audit.json")


if __name__ == "__main__":
    main()
