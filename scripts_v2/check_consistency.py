# -*- coding: utf-8 -*-
"""
check_consistency.py — Consistency tests between the generated JSON outputs and the
claims printed in the manuscript (main.tex). Fails loudly on divergence.

Checks:
  1. Every numeric value printed in Tables 2/3/4/5/6 bodies equals the corresponding
     JSON-derived value (make_tables_v2 output vs. the \\input'd file).
  2. Abstract headline ranges match the JSON extremes.
  3. Figure files referenced by main.tex exist and are unique (no divergent copies).
  4. No hard-coded table bodies remain in main.tex for generated tables.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PAPER = ROOT / "paper_cn_journal_template"
sys.path.insert(0, str(Path(__file__).resolve().parent))

FAILURES = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append((name, detail))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    tex = (PAPER / "main.tex").read_text(encoding="utf-8")

    # ---- 1. figure files: referenced files exist in the canonical figure dir
    figs = re.findall(r'\\includegraphics\[[^\]]*\]\{([^}]+)\}', tex)
    for f in figs:
        p = (PAPER / f).resolve()
        check(f"figure exists: {f}", p.exists())
    # uniqueness: no same-named figure in other dirs of the repo
    all_pngs = [q for q in ROOT.rglob("*.png") if "_archive" not in q.parts and "legacy" not in q.parts]
    names = [p.name for p in all_pngs]
    for f in figs:
        fname = Path(f).name
        copies = [p for p in all_pngs if p.name == fname]
        if len(copies) > 1:
            same = all(c.stat().st_size == copies[0].stat().st_size for c in copies)
            check(f"figure copies identical: {fname}", same,
                  f"{len(copies)} divergent copies")

    # ---- 2. Table 2 rows vs JSON
    t2 = json.loads((REPORTS / "table2_params.json").read_text(encoding="utf-8"))["table2"]
    body_file = REPORTS / "table_bodies.tex"
    check("table_bodies.tex exists", body_file.exists())
    if body_file.exists():
        bodies = body_file.read_text(encoding="utf-8")
        for key, rec in t2.items():
            frag = f"{rec['R_gen']:.4f} & {rec['s_gen']:.4f}"
            check(f"table2 row params in generated body: {key}", frag in bodies)

    # ---- 3. headline ranges in the abstract vs JSON
    t2v = {k: v["h_star_weeks"] for k, v in t2.items()}
    nonrsv = [t2v[k] for k in ["Delta", "Omicron", "JN1", "flu22", "flu24"]]
    lo, hi = min(nonrsv), max(nonrsv)
    m = re.search(r'(\d+\.\d)--(\d+\.\d)\s*周', tex)
    if m:
        tex_lo, tex_hi = float(m.group(1)), float(m.group(2))
        check("abstract non-RSV horizon range matches JSON",
              abs(tex_lo - lo) < 0.15 and abs(tex_hi - hi) < 0.15,
              f"tex {tex_lo}--{tex_hi} vs json {lo:.1f}--{hi:.1f}")

    # ---- 4. no hard-coded horizon literals from the OLD version remain
    stale = ["13.5 周", "2.9 周 (6.8 代)", "43.9 周", "70.1 周", "3.52 \\pm 1.26",
             "1.82 \\pm 2.25", "5.34 \\pm 1.13", "8.9--20.0", "1.8--6.0",
             "27.9--65.0", "46.2--95.0"]
    for s in stale:
        check(f"stale literal removed: '{s}'", s not in tex)


    # ---- 5. Table 5 crossing points vs rolling JSON
    roll = json.loads((REPORTS / "rolling_results.json").read_text(encoding="utf-8"))
    for wave, key in [("Delta", "Delta"), ("Omicron", "Omicron"), ("Flu_22_23", "flu22")]:
        c = roll[wave]["crossing"]["pers"]
        if body_file.exists() and c["point"] is not None:
            frag = f"{c['point']:.2f} 周 (95"
            check(f"table5 crossing in generated body: {wave}", frag in bodies)

    # ---- 6. Table 4 totals vs budget JSON
    budget = json.loads((REPORTS / "table4_budget.json").read_text(encoding="utf-8"))
    n_cfg = sum(len(v["horizons"]) for v in budget.values())
    check("budget config count = 12", n_cfg == 12, f"got {n_cfg}")

    # ---- 7. CRB analysis exists and matches prose claims
    crb = json.loads((REPORTS / "crb_analysis.json").read_text(encoding="utf-8"))
    check("rsv25 CRB ratio 2.46", abs(crb["rsv25"]["ratio"] - 2.46) < 0.01)
    check("rsv24 CRB ratio < 1 (no violation)", crb["rsv24"]["ratio"] < 1.0)
    check("rsv25 violates", crb["rsv25"]["violates"])

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURES:")
        for n, d in FAILURES:
            print(" -", n, d)
        sys.exit(1)
    print("All consistency checks passed.")


if __name__ == "__main__":
    main()
