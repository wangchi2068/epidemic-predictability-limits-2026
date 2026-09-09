# -*- coding: utf-8 -*-
"""check_consistency.py — build-halting consistency suite (eight assertion classes).

1. Table fragments: regenerate every tables_v3/*.tex body from the deposited
   JSONs and byte-compare against the committed fragments.
2. Figures: every figure referenced in main.tex exists and is non-blank
   (>5% of pixels differ from the background).
3. Stale-literal blacklist: retired phrases from earlier versions must be
   absent from every reader-facing file (main.tex and README.md).
4. Abstract assertions: headline ranges printed in the abstracts match the
   JSON-derived values.
5. Cramér--Rao ratios: the micro-layer bootstrap/CRB ratios in the table match
   the fit JSON.
6. Dimensional assertion: every budget row's drift term equals h_week x the
   per-week drift variance (weekly clock; the generation-step form is retired).
7. Two-sided crossing assertion: the rolling evaluation contains both an
   upward persistence crossing and a downward local-linear crossing for the
   Delta and Omicron waves.
8. Deposited-series identity: the national window sums that pin the analysis
   series equal the values the manuscript's tables were built from.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper_cn_journal_template"
REPORTS = ROOT / "reports_v3"
TABLES = ROOT / "tables_v3"
DATA = ROOT / "data"
STATE_FIPS = {f"{i:02d}" for i in range(1, 57)}

# phrases retired from earlier versions; must not appear in reader-facing text
STALE = [
    "26.1\\%--99.3\\%",          # old four-term budget residual range
    "51.2\\%--99.6\\%",          # README's retired residual range
    "1.8--5.3",                  # old operational-lead-time headline
    "41.5--67.8",                # old RSV extrapolation range
    "2.46",                      # old RSV 2025-26 cluster-count ratio
    "h_{\\text{gen}} \\cdot \\widehat{v}^2",  # retired generation-step drift form
    "10 个中为正",                # old budget tally
    "0.74\\%",                   # old national CV^2 contribution
    "三波次、每波次六原点",        # old sample description
    "1.4 倍",                    # retired aggregation-inflation threshold
]


def fail(msg):
    print(f"[FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def check_tables():
    import emit_v3
    phases = json.loads((REPORTS / "state_phases.json").read_text(encoding="utf-8"))
    roll_state = json.loads((REPORTS / "state_rolling.json").read_text(encoding="utf-8"))
    roll_nat = json.loads((REPORTS / "national_rolling.json").read_text(encoding="utf-8"))
    scen = json.loads((REPORTS / "scenarios.json").read_text(encoding="utf-8"))
    bud = json.loads((REPORTS / "budget_national.json").read_text(encoding="utf-8"))
    micro = json.loads((DATA / "micro" / "micro_branching_fit_results.json")
                       .read_text(encoding="utf-8"))
    hub = json.loads((DATA / "hub" / "forecast_hub_operational_evaluation.json")
                     .read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        emit_v3.TABLES = tmp
        emit_v3.emit_table2(phases)
        emit_v3.emit_table3(roll_state, roll_nat, phases)
        emit_v3.emit_table4(bud)
        emit_v3.emit_table5_hub(hub)
        emit_v3.emit_table6_tiers(scen)
        emit_v3.emit_table7(micro)
        for f in sorted(tmp.glob("*.tex")):
            committed = TABLES / f.name
            if not committed.exists():
                fail(f"missing committed table fragment {f.name}")
            if committed.read_bytes() != f.read_bytes():
                fail(f"table fragment {f.name} diverges from the JSONs")
    print("[OK] table fragments match the deposited JSONs (6 fragments)")


def check_figures():
    import matplotlib.image as mpimg
    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    refs = re.findall(r"\\includegraphics\[[^\]]*\]\{([^}]+)\}", tex)
    if not refs:
        fail("no figure references found")
    for r in refs:
        p = (PAPER / r).resolve()
        if not p.exists():
            fail(f"figure missing: {r}")
        img = mpimg.imread(p)
        frac = float((img[..., :3].min(axis=-1) < 245).mean())
        if frac < 0.05:
            fail(f"figure nearly blank ({frac:.3%} ink): {r}")
    print(f"[OK] {len(refs)} referenced figures exist and are non-blank")


def _norm(t: str) -> str:
    """Normalize dashes/escapes so blacklist hits survive formatting variants."""
    for ch in ("–", "—", "−"):  # en dash, em dash, minus
        t = t.replace(ch, "-")
    return t.replace("\\", "").replace("--", "-").replace(" ", "")


def check_blacklist():
    files = [PAPER / "main.tex", ROOT / "README.md"]
    for f in files:
        if not f.exists():
            fail(f"reader-facing file missing: {f.name}")
        t = _norm(f.read_text(encoding="utf-8"))
        for phrase in STALE:
            if _norm(phrase) in t:
                fail(f"stale literal {phrase!r} found in {f.name}")
    print(f"[OK] stale-literal scan clean across {len(files)} reader-facing files")


def check_abstract():
    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    phases = json.loads((REPORTS / "state_phases.json").read_text(encoding="utf-8"))
    med = [p["h_week_summary"]["median"] for p in phases.values()
           if p.get("h_week_summary")]
    lo, hi = min(med), max(med)
    if f"{lo:.1f}--{hi:.1f}" not in tex:
        fail(f"abstract does not state the state-median horizon range "
             f"{lo:.1f}--{hi:.1f}")
    micro = json.loads((DATA / "micro" / "micro_branching_fit_results.json")
                       .read_text(encoding="utf-8"))
    ratios = [r["bootstrap"]["ratio_var_to_crb"] for k, r in micro.items()
              if k != "LloydSmith_reference"]
    if f"{min(ratios):.2f}--{max(ratios):.2f}" not in tex:
        fail("abstract CRB-ratio range does not match the micro JSON")
    aics = [r["delta_aic_poisson_vs_nb"] for k, r in micro.items()
            if k != "LloydSmith_reference"]
    if f"{min(aics):.1f}--{max(aics):.1f}" not in tex:
        fail("abstract dAIC range does not match the micro JSON")
    print(f"[OK] abstract ranges consistent (h* {lo:.1f}--{hi:.1f} wk, "
          f"CRB {min(ratios):.2f}--{max(ratios):.2f}, "
          f"dAIC {min(aics):.1f}--{max(aics):.1f})")


def check_crb_ratios():
    micro = json.loads((DATA / "micro" / "micro_branching_fit_results.json")
                       .read_text(encoding="utf-8"))
    frag = (TABLES / "table7_micro.tex").read_text(encoding="utf-8")
    for k, r in micro.items():
        if k == "LloydSmith_reference":
            continue
        v = f"{r['bootstrap']['ratio_var_to_crb']:.3f}"
        if v not in frag:
            fail(f"CRB ratio {v} for {k} missing from table7 fragment")
    print("[OK] CRB bootstrap ratios in the table match the fit JSON")


def check_drift_dimension():
    bud = json.loads((REPORTS / "budget_national.json").read_text(encoding="utf-8"))
    for key, rec in bud.items():
        for h, row in rec["horizons"].items():
            expect = float(h) * row["median_v_week"]
            if abs(row["median_drift"] - expect) > 1e-12:
                fail(f"{key} h={h}: e_drift {row['median_drift']} != "
                     f"h_week*v {expect} (generation-step form?)")
    print("[OK] drift term equals h_week x weekly variance in every budget row")


def check_crossings():
    roll = json.loads((REPORTS / "state_rolling.json").read_text(encoding="utf-8"))
    for wave in ("Delta", "Omicron"):
        cp = roll[wave]["crossing_persistence"]["median"]
        cl = roll[wave]["crossing_linear"]["median"]
        if cp is None or cl is None:
            fail(f"{wave}: missing a persistence (up) or local-linear (down) crossing")
    print("[OK] two-sided crossings present for Delta and Omicron")


def check_series_identity():
    pinned = {"covid": ("2021-07-03", "2021-07-31", 141735.0),
              "flu": ("2022-10-08", "2022-11-05", 15579.0),
              "rsv": ("2024-11-09", "2024-12-07", 22047.0)}
    for name, (w0, w1, val) in pinned.items():
        if name == "covid":
            d = pd.read_csv(DATA / "panels" / "covid_weekly_hospitalizations.csv.gz",
                            parse_dates=["week_end_date"])
            d = d.rename(columns={"week_end_date": "week_end",
                                  "weekly_admissions": "value"})
        else:
            d = pd.read_csv(DATA / "panels" / f"{name}_weekly_hospitalizations.csv.gz",
                            parse_dates=["week_end"])
        d["location"] = d["location"].astype(str).str.zfill(2)
        nat = (d[d.location.isin(STATE_FIPS)]
               .groupby("week_end").value.sum().sort_index())
        got = float(nat[w0:w1].sum())
        if abs(got - val) > 1e-6:
            fail(f"{name}: national window sum {got} != pinned {val}")
    print("[OK] deposited-series identity pinned for all three panels")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== consistency suite ===", flush=True)
    check_tables()
    check_figures()
    check_blacklist()
    check_abstract()
    check_crb_ratios()
    check_drift_dimension()
    check_crossings()
    check_series_identity()
    print("\nAll consistency assertions passed.", flush=True)


if __name__ == "__main__":
    main()
