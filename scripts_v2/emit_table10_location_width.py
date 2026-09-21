# -*- coding: utf-8 -*-
"""Emit table10_location_width.tex for the synthesised paper.

Rows: season x phase.  Columns:
  n | share-under | median rel error | best k-scale | cov@that k
  | oracle shift | cov@oracle
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
PHASE_LABEL = {"rising": "峰前", "peak": "峰值", "declining": "峰后"}
K_GRID = [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625,
          0.0078125, 0.00390625, 0.001953125]


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


def q(row):
    _, qs = fx.mechanistic_quantiles(row.R, row.slope_se, row.k, row.I0, 1)
    return qs


def main() -> None:
    rows = []
    for tag in RELEASES:
        m1 = cells_for(tag)
        block = []
        for ph in ("rising", "peak", "declining"):
            g = m1[m1.phase == ph]
            if not len(g):
                continue
            rel_err, under = [], 0
            for row in g.itertuples():
                if not (row.truth > 0):
                    continue
                qs = q(row)
                e = (float(qs[11]) - row.truth) / row.truth
                rel_err.append(e)
                under += e < 0
            med_err = float(np.median(rel_err))

            best_c, best_m = -1.0, None
            for m in K_GRID:
                hits = 0
                for row in g.itertuples():
                    _, qs = fx.mechanistic_quantiles(
                        row.R, row.slope_se, row.k * m, row.I0, 1)
                    if float(qs[1]) <= row.truth <= float(qs[21]):
                        hits += 1
                c = hits / len(g)
                if c > best_c:
                    best_c, best_m = c, m

            ratios = []
            for row in g.itertuples():
                if not (row.truth > 0):
                    continue
                qs = q(row)
                med = float(qs[11])
                if med > 0:
                    ratios.append(row.truth / med)
            s_star = float(np.median(ratios)) if ratios else float("nan")

            # coverage after oracle shift, at the k that maximises it
            best_shift_c, best_shift_m = -1.0, None
            for m in K_GRID:
                hits = 0
                for row in g.itertuples():
                    _, qs = fx.mechanistic_quantiles(
                        row.R, row.slope_se, row.k * m, row.I0, 1)
                    lo, hi = float(qs[1]) * s_star, float(qs[21]) * s_star
                    if lo <= row.truth <= hi:
                        hits += 1
                c = hits / len(g)
                if c > best_shift_c:
                    best_shift_c, best_shift_m = c, m

            block.append((
                len(g), under / len(rel_err), med_err,
                best_m, best_c, s_star, best_shift_c))

        for i, (n, sh, me, km, kc, ss, sc) in enumerate(block):
            season = f"\\multirow{{{len(block)}}}{{*}}{{{tag}}}" if i == 0 else ""
            km_s = "1" if km == 1.0 else f"$1/{round(1/km):g}$"
            rows.append(
                f"{season} & {PHASE_LABEL[('rising','peak','declining')[i]]} & {n} & "
                f"{sh*100:.1f}\\% & {me:+.3f} & {km_s} & {kc:.3f} & "
                f"{ss:.2f} & {sc:.3f} \\\\")
        rows.append("\\midrule")

    if rows and rows[-1] == "\\midrule":
        rows.pop()

    body = (
        "\\begin{tabular}{@{}llrrrrrrr@{}}\n\\toprule\n"
        "赛季 & 相位 & $n$ & 低估比例 & 中位相对误差 & 最优 $k$ 缩放 & "
        "该档覆盖率 & oracle 位置缩放 & 缩放后覆盖率 \\\\\n\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n\\end{tabular}\n")

    out = ROOT / "paper_synth" / "tables_v3" / "table10_location_width.tex"
    out.write_text(body, encoding="utf-8")
    print("[OK]", out)
    print(body)


if __name__ == "__main__":
    main()
