# -*- coding: utf-8 -*-
"""
check_consistency.py — Consistency tests between the JSON outputs and the table
bodies that ACTUALLY COMPILE into main.tex. Fails loudly on divergence.

Design (Major 5 fix): previously the table assertions validated
reports/table_bodies.tex, a file that main.tex never \\input'd, so net coverage of
the printed tables was zero. Now main.tex \\input's per-table fragments under
paper_cn_journal_template/tables/*_body.tex (emitted by make_tables_v2.py); this
script (a) confirms no hand-typed table bodies remain in main.tex, (b) recomputes
each fragment from the JSONs and compares it byte-for-byte against the on-disk
fragment that compiles, (c) checks headline abstract ranges, figure non-emptiness,
and a stale-literal blacklist.

Checks:
  1. main.tex \\input's all five generated fragments and contains no hand-typed
     data rows for Tables 2/3/4/5/6.
  2. Each on-disk fragment equals make_tables_v2's output from the current JSONs
     (JSON -> fragment -> PDF single source of truth).
  3. Figure files referenced by main.tex exist and are non-blank (content check).
  4. Abstract headline ranges match the JSON extremes.
  5. No superseded numeric literals remain anywhere in main.tex.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PAPER = ROOT / "paper_cn_journal_template"
FRAG = PAPER / "tables"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_tables_v2 import (TABSPECS, wrap, table2_rows, table3_rows,
                            table4_rows, table5_rows, table6_rows)  # noqa: E402

GENERATORS = {
    "table2": lambda: wrap("table2", table2_rows()),
    "table3": lambda: wrap("table3", table3_rows()),
    "table4": lambda: wrap("table4", table4_rows()),
    "table5": lambda: wrap("table5", table5_rows()),
    "table6": lambda: wrap("table6", table6_rows()),
}

FAILURES = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append((name, detail))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    tex = (PAPER / "main.tex").read_text(encoding="utf-8")

    # ---- 1. main.tex must \\input each generated fragment, not hand-type it
    for name in ["table2", "table3", "table4", "table5", "table6"]:
        check(f"main.tex \\\\inputs {name}_body",
              re.search(r'\\input\{tables/' + name + r'_body\}', tex) is not None)
    # no hand-typed horizon data row should survive (heuristic: a literal "暴发期 & 1." style row)
    hand_typed = re.findall(r'(Delta 暴发期|Omicron 达峰期) & 1\.\d{3}', tex)
    check("no hand-typed Table2 rows remain", not hand_typed,
          f"found {hand_typed}")

    # ---- 2. on-disk fragments == JSON-derived bodies (recompute both sides)
    for name, gen in GENERATORS.items():
        fpath = FRAG / f"{name}_body.tex"
        check(f"{name} fragment exists", fpath.exists())
        if not fpath.exists():
            continue
        on_disk = fpath.read_text(encoding="utf-8")
        # strip the header comment line we emit
        on_disk_body = "\n".join(l for l in on_disk.splitlines() if not l.startswith("%"))
        regenerated = gen()
        check(f"{name} fragment matches JSON (single source of truth)",
              on_disk_body.strip() == regenerated.strip(),
              "fragment drifted from JSON — rerun make_tables_v2.py")

    # ---- 3. figure existence AND non-emptiness (content, not just size)
    figs = re.findall(r'\\includegraphics\[[^\]]*\]\{([^}]+)\}', tex)
    try:
        from PIL import Image
        import collections
        have_pil = True
    except Exception:
        have_pil = False
    for f in figs:
        p = (PAPER / f).resolve()
        check(f"figure exists: {f}", p.exists())
        if have_pil and p.exists():
            try:
                im = Image.open(p).convert("RGB")
                cnt = collections.Counter(im.getdata())
                nonbg = 1 - cnt.most_common(1)[0][1] / (im.size[0] * im.size[1])
                check(f"figure non-blank: {f}", nonbg > 0.05,
                      f"non-background fraction {nonbg:.3f}")
            except Exception as exc:
                check(f"figure decodable: {f}", False, str(exc))

    # ---- 4. headline ranges in the Chinese abstract vs JSON
    t2 = json.loads((REPORTS / "table2_params.json").read_text(encoding="utf-8"))["table2"]
    t2v = {k: v["h_star_weeks"] for k, v in t2.items()}
    nonrsv = [t2v[k] for k in ["Delta", "Omicron", "JN1", "flu22", "flu24"]]
    lo, hi = min(nonrsv), max(nonrsv)
    m = re.search(r'(\d+\.\d)--(\d+\.\d)\s*周', tex)
    if m:
        tex_lo, tex_hi = float(m.group(1)), float(m.group(2))
        check("abstract non-RSV horizon range matches JSON",
              abs(tex_lo - lo) < 0.15 and abs(tex_hi - hi) < 0.15,
              f"tex {tex_lo}--{tex_hi} vs json {lo:.1f}--{hi:.1f}")

    # ---- 5. stale literals from prior rounds must be gone everywhere
    stale = ["13.5 周", "43.9 周", "70.1 周", "8.9--20.0", "1.8--6.0",
             "27.9--65.0", "46.2--95.0", "88.7", "0.0574", "物理硬上限",
             "客观物理标尺", "第一性原理", "违背倍数达 2.46", "51.2\\%--99.6",
             "22,986", "8,694", "完全实测", "100\\% 严密自洽",
             "6.2\\%--99.2", "9 of 12", "8/9 个正残差", "-54.2\\%", "-297.4\\%",
             "均无穿越", "三波次均不穿越", "0.9570", "0.9621", "11.6--34.5",
             "16.5\\%--17.6", "16.7\\%--18.0", "视界收缩至零"]
    for s in stale:
        check(f"stale literal removed: '{s}'", s not in tex)

    # ---- 6. corrected CRB ratio must be the recomputed one (1.48, not 2.46)
    crb = json.loads((REPORTS / "crb_analysis.json").read_text(encoding="utf-8"))
    check("rsv25 CRB ratio recomputed ~1.48 (R^2 bug fixed)",
          abs(crb["rsv25"]["ratio"] - 1.476) < 0.02, f"got {crb['rsv25']['ratio']}")
    check("rsv24 CRB ratio < 1 (no violation)", crb["rsv24"]["ratio"] < 1.0)

    # ---- 7. E_drift time scale: e_drift must equal h_week * v_drift (per-week variance),
    # not h_gen * v_drift. Round-14 §3.1 dimensional fix, guarded against regression.
    b4 = json.loads((REPORTS / "table4_budget.json").read_text(encoding="utf-8"))
    scale_fail = []
    for key, rec in b4.items():
        v = rec["v_drift"]
        for hw, r in rec["horizons"].items():
            expected = int(hw) * v
            if abs(r["e_drift"] - expected) > 1e-9 * max(expected, 1.0):
                scale_fail.append(f"{key} h={hw}: e_drift={r['e_drift']:.3e} != h_week*v={expected:.3e}")
    check("E_drift uses h_week * v_drift (week/generation scale)",
          not scale_fail, "; ".join(scale_fail[:3]))

    # ---- 8. two-way crossing detector: local-linear crossings must exist for Delta/Omicron
    rr = json.loads((REPORTS / "rolling_results.json").read_text(encoding="utf-8"))
    for w in ["Delta", "Omicron"]:
        lin = rr[w]["crossing"]["lin"]
        check(f"{w} local-linear crossing detected (two-way detector)",
              lin["point"] is not None and lin["direction"] == "down",
              f"got {lin}")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURES:")
        for n, d in FAILURES:
            print(" -", n, d)
        sys.exit(1)
    print("All consistency checks passed.")


if __name__ == "__main__":
    main()
