# -*- coding: utf-8 -*-
"""ingest_and_aggregate.py — provenance and integrity checks for the three-tier
empirical data set (micro transmission chains / state panels / hub benchmark).

The frozen analytical inputs live in `data/`:

  data/micro/    Hong Kong COVID-19 (Adam et al. 2020), Guinea Ebola (Faye et
                 al. 2015) and the Lloyd-Smith (2005) offspring-distribution
                 library, plus the fitted micro-branching results.
  data/panels/   51-jurisdiction weekly hospital-admission panels for COVID-19,
                 influenza and RSV, built from the terminal target data of the
                 three CDC forecast hubs (reichlab/covid19-forecast-hub,
                 FluSight, RSV hub), which are NHSN weekly hospital admissions.
                 `us_state_daily_hospitalizations.csv` is the COVID-19 daily
                 truth file; `covid_weekly_hospitalizations.csv.gz` is its
                 Saturday-ending weekly aggregation (complete weeks only).
  data/hub/      COVIDhub-ensemble archived forecast files (12 origins) and the
                 operational evaluation JSON.

This script (a) re-derives the weekly COVID panel from the daily file and checks
it against the frozen copy, (b) asserts structural invariants of all three
panels (jurisdiction set, weekday grid, non-negativity, coverage), and
(c) pins the deposited-series identity by the national window sums used in the
manuscript, so that a swap of the underlying series cannot pass silently.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PANELS = DATA / "panels"
STATE_FIPS = {f"{i:02d}" for i in range(1, 57)}

# National window sums that pin the identity of the deposited series
# (COVID-19 Delta, influenza 2022--23, RSV 2024--25 windows; see Table 2).
PINNED = {
    "covid": ("2021-07-03", "2021-07-31", 141735.0),
    "flu": ("2022-10-08", "2022-11-05", 15579.0),
    "rsv": ("2024-11-09", "2024-12-07", 22047.0),
}

# Deposited-input identity: SHA-256 of the frozen analytical inputs, mirrored in
# MANIFEST.md section 10. A swap of the underlying series cannot pass silently.
PINNED_HASHES = {
    "data/panels/covid_weekly_hospitalizations.csv.gz":
        "4ee61b27d547f8dbee3db139705316a951e2b431d45585a4bdd530c67e88476a",
    "data/panels/flu_weekly_hospitalizations.csv.gz":
        "05e7fc87a3362efcb0afb05b9a33d0579eda86f90e56319d18d63a782657048f",
    "data/panels/rsv_weekly_hospitalizations.csv.gz":
        "22c0f0fa1f38a551cf2ab880bb306b2cad7f5d1d8777d46ceaa9ae1627cdc5f8",
    "data/panels/us_state_daily_hospitalizations.csv":
        "90c9d057b9561c4ce26ac591a61c0e174df52acfbd3a695d35b09fac963ae338",
    "data/micro/micro_branching_fit_results.json":
        "2369cf1cce28be1c1e7f7cdc304098df06e682f081a94626fec4656fdce51977",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_weekly(name: str) -> pd.DataFrame:
    if name == "covid":
        d = pd.read_csv(PANELS / "covid_weekly_hospitalizations.csv.gz",
                        parse_dates=["week_end_date"])
        d = d.rename(columns={"week_end_date": "week_end",
                              "weekly_admissions": "value"})
    else:
        d = pd.read_csv(PANELS / f"{name}_weekly_hospitalizations.csv.gz",
                        parse_dates=["week_end"])
    d["location"] = d["location"].astype(str).str.zfill(2)
    return d[["location", "week_end", "value"]]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== data provenance & integrity ===", flush=True)

    # (a) rebuild the COVID weekly panel from the daily truth and compare
    daily = pd.read_csv(PANELS / "us_state_daily_hospitalizations.csv",
                        parse_dates=["date"])
    daily["location"] = daily["location"].astype(str).str.zfill(2)
    daily = daily[daily.location.isin(STATE_FIPS)]
    daily["week_end"] = daily["date"].dt.to_period("W-SAT").dt.end_time.dt.normalize()
    wk = (daily.groupby(["location", "week_end"])
          .agg(value=("value", "sum"), days=("value", "count")).reset_index())
    wk = wk[wk.days == 7].drop(columns="days")
    frozen = load_weekly("covid")
    frozen = frozen[frozen.location.isin(STATE_FIPS)]
    merged = frozen.merge(wk, on=["location", "week_end"], how="outer",
                          suffixes=("_frozen", "_rebuilt"), indicator=True)
    same = merged[merged._merge == "both"]
    assert (same.value_frozen == same.value_rebuilt).all(), "weekly rebuild mismatch"
    assert (merged._merge == "both").all(), "daily/weekly coverage mismatch"
    print(f"[OK] COVID weekly panel reproduces from daily truth "
          f"({len(frozen)} rows, {frozen.location.nunique()} jurisdictions)", flush=True)

    # (b) structural invariants
    states51 = set(load_weekly("flu").location)  # the 51 state-level FIPS codes
    for name in ("covid", "flu", "rsv"):
        d = load_weekly(name)
        assert states51.issubset(set(d.location)), \
            f"{name}: missing jurisdictions"
        if name != "covid":  # the COVID panel also carries territories + a US row
            assert set(d.location) == states51, f"{name}: unexpected jurisdiction set"
        assert (d.value >= 0).all(), f"{name}: negative counts"
        assert (d.week_end.dt.dayofweek == 5).all(), f"{name}: non-Saturday grid"
        print(f"[OK] {name} panel: {len(d)} rows, "
              f"{d.week_end.min().date()}..{d.week_end.max().date()}", flush=True)

    # (c) deposited-series identity (national window sums)
    for name, (w0, w1, pinned) in PINNED.items():
        d = load_weekly(name)
        nat = d[d.location.isin(STATE_FIPS)].groupby("week_end").value.sum()
        got = float(nat[w0:w1].sum())
        assert abs(got - pinned) < 1e-6, (
            f"{name}: national window sum {got} != pinned {pinned}")
        print(f"[OK] {name} identity pinned: {w0}..{w1} national sum = {got:.0f}",
              flush=True)

    print("\n=== input checksums (for MANIFEST.md) ===", flush=True)
    bad = 0
    for p in sorted(PANELS.glob("*")) + sorted((DATA / "micro").glob("*")):
        if p.is_file():
            got = sha256(p)
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            expect = PINNED_HASHES.get(rel)
            mark = ""
            if expect is not None:
                if got == expect:
                    mark = "  [OK pinned]"
                else:
                    mark = f"  [MISMATCH expected {expect}]"
                    bad += 1
            print(f"{got}  {rel}{mark}", flush=True)
    assert bad == 0, f"{bad} input checksum(s) diverged from MANIFEST.md"

    print("\nAll data-integrity checks passed.", flush=True)


if __name__ == "__main__":
    main()
