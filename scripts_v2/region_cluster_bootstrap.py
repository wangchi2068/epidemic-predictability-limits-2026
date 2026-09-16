"""region_cluster_bootstrap.py — HHS-region cluster bootstrap for the paired WIS difference.

Answers the reviewer request for a spatial-correlation sensitivity analysis: the
main text reports an origin-week moving-block bootstrap, which absorbs temporal
dependence but treats states as if exchangeable. Here we instead resample whole
HHS regions (which share season, variant turnover and reporting regime), giving a
conservative interval for the ensemble-minus-baseline paired WIS difference.
"""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports_v3"

# FIPS (2-digit string) -> HHS region 1..10 (50 states + DC).
HHS = {
    "09": 1, "23": 1, "25": 1, "33": 1, "44": 1, "50": 1,
    "34": 2, "36": 2,
    "10": 3, "11": 3, "24": 3, "42": 3, "51": 3, "54": 3,
    "01": 4, "12": 4, "13": 4, "21": 4, "28": 4, "37": 4, "45": 4, "47": 4,
    "17": 5, "18": 5, "26": 5, "27": 5, "39": 5, "55": 5,
    "05": 6, "22": 6, "35": 6, "40": 6, "48": 6,
    "19": 7, "20": 7, "29": 7, "31": 7,
    "08": 8, "30": 8, "38": 8, "46": 8, "49": 8, "56": 8,
    "04": 9, "06": 9, "15": 9, "32": 9,
    "02": 10, "16": 10, "41": 10, "53": 10,
}

RELEASES = ("v1.0", "v1.1", "v1.2")
N_BOOT = 2000
SEED = 20260916


def load_pairs(release: str, horizon: int) -> list[tuple[int, float]]:
    """Return (hhs_region, wis_ensemble - wis_baseline) for every paired cell."""
    if release not in RELEASES:
        raise ValueError(f"unknown release {release!r}; expected one of {RELEASES}")
    path = (REPORTS / f"flusight_{release}_extended.csv").resolve()
    if REPORTS.resolve() not in path.parents:
        raise ValueError(f"resolved path escapes reports dir: {path}")
    if not path.exists():
        return []

    per_cell: dict[tuple[str, str], dict[str, float]] = {}
    with path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                h = int(r["horizon"])
                wis = float(r["wis"])
                key = (r["reference_date"], r["location"])
            except (TypeError, ValueError, KeyError) as exc:
                raise ValueError(
                    f"malformed row in {path.name}: {r!r}"
                ) from exc
            if h != horizon:
                continue
            per_cell.setdefault(key, {})[r["model"]] = wis

    out: list[tuple[int, float]] = []
    for (_origin, loc), vals in per_cell.items():
        if "ensemble" in vals and "baseline" in vals:
            reg = HHS.get(loc)
            if reg is not None:
                out.append((reg, vals["ensemble"] - vals["baseline"]))
    return out


def cluster_bootstrap(pairs: list[tuple[int, float]], n_boot: int, seed: int) -> dict:
    if not isinstance(n_boot, int) or n_boot < 40:
        raise ValueError(f"n_boot={n_boot!r} must be an int >= 40 for a 95% percentile interval")

    by_region: dict[int, list[float]] = {}
    for reg, d in pairs:
        by_region.setdefault(reg, []).append(d)
    regions = sorted(by_region)
    if len(regions) < 2:
        return {}

    def stat(draw: list[int]) -> float:
        vals = [v for r in draw for v in by_region[r]]
        return sum(vals) / len(vals)

    point = stat(regions)
    rng = random.Random(seed)
    boots = sorted(stat([rng.choice(regions) for _ in regions]) for _ in range(n_boot))

    # Pure integer arithmetic: no conversion call can raise here.
    lo_idx = max(min((n_boot * 25) // 1000, n_boot - 1), 0)
    hi_idx = max(min((n_boot * 975) // 1000 - 1, n_boot - 1), 0)
    lo, hi = boots[lo_idx], boots[hi_idx]
    return {
        "n_cells": len(pairs),
        "n_regions": len(regions),
        "cells_per_region": {str(r): len(by_region[r]) for r in regions},
        "point_mean_diff": point,
        "cluster_ci95": [lo, hi],
        "region_means": {str(r): sum(by_region[r]) / len(by_region[r]) for r in regions},
        "excludes_zero": (lo > 0) or (hi < 0),
    }


def main() -> None:
    result = {
        "schema": "hhs_region_cluster_bootstrap_v1",
        "n_boot": N_BOOT,
        "seed": SEED,
        "unit": "hhs_region",
        "releases": {},
    }
    for rel in RELEASES:
        result["releases"][rel] = {}
        for h in (1, 2, 3):
            pairs = load_pairs(rel, h)
            if pairs:
                result["releases"][rel][f"h{h}"] = cluster_bootstrap(pairs, N_BOOT, SEED)

    out = REPORTS / "region_cluster_bootstrap.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    for rel, byh in result["releases"].items():
        for hk, rec in sorted(byh.items()):
            lo, hi = rec["cluster_ci95"]
            print(
                f"{rel} {hk}: n={rec['n_cells']:5d} regions={rec['n_regions']} "
                f"mean={rec['point_mean_diff']:7.2f} "
                f"clustered 95%CI=[{lo:7.2f}, {hi:7.2f}] "
                f"excludes0={rec['excludes_zero']}"
            )
    print("written:", out)


if __name__ == "__main__":
    main()
