# -*- coding: utf-8 -*-
"""Emit the two appendix support tables (A1: I0 caliber, A2: geometric share).

Writes paper_journal/tables_v3/tableA1_i0.tex and tableA2_geo.tex.
ASCII-only stdout so a GBK console cannot mangle the output.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")
ROOT = Path(__file__).resolve().parents[1]
TBL = ROOT / "paper_journal" / "tables_v3"

J = lambda n: json.loads((ROOT / "reports_v3" / f"{n}.json").read_text(encoding="utf-8"))

PHASES = [
    ("Delta", "COVID-19 Delta 暴发期"),
    ("Omicron", "COVID-19 Omicron 达峰期"),
    ("JN1", "COVID-19 JN.1 流行期"),
    ("flu22", "流感 2022--23 暴发早期"),
    ("flu24", "流感 2024--25 流行季"),
    ("rsv24", "RSV 2024--25 流行季"),
    ("rsv25", "RSV 2025--26 流行季"),
]


def cv2_macro(h, R, k, I0):
    q = R * R * (1 + 1 / k)
    return (R / I0) * (q ** h - R ** h) / (R ** (2 * h) * (q - R)) + (1 + 1 / k) ** h - 1


def main():
    i0 = J("i0_sensitivity")
    sp = J("state_phases")

    lo_last = min(i0[k]["median_pct_change_last"] for k, _ in PHASES)
    hi_last = max(i0[k]["median_pct_change_last"] for k, _ in PHASES)
    lo_fit = min(i0[k]["median_pct_change_fitend"] for k, _ in PHASES)
    hi_fit = max(i0[k]["median_pct_change_fitend"] for k, _ in PHASES)

    rows_i0, rows_geo = [], []
    for key, disp in PHASES:
        r = i0[key]
        rows_i0.append(
            f"{disp} & {r['n']} & {r['median_pct_change_last']:+.2f} & "
            f"{r['median_pct_change_fitend']:+.2f} \\\\")

        st = sp[key]["states"]
        geo = [((1 + 1 / v["k"]) ** v["h_week"] - 1) / 0.25 for v in st.values()]
        share = [cv2_macro(v["h_week"], v["R_week"], v["k"], v["I0"]) / 0.25
                 for v in st.values()]
        rows_geo.append(
            f"{disp} & {len(st)} & {np.median(geo) * 100:.1f}\\% & {np.median(share):.3f} \\\\")

    (TBL / "tableA1_i0.tex").write_text(
        "\\begin{tabular}{lccc}\n\\toprule\n"
        "阶段 & $n_{\\text{州}}$ & 末值口径 & 拟合端点口径 \\\\\n\\midrule\n"
        + "\n".join(rows_i0)
        + f"\n\\midrule\n跨阶段范围 & --- & ${lo_last:+.1f}\\%$ 至 ${hi_last:+.1f}\\%$ & "
        f"${lo_fit:+.1f}\\%$ 至 ${hi_fit:+.1f}\\%$ \\\\\n"
        "\\bottomrule\n\\end{tabular}\n", encoding="utf-8")

    (TBL / "tableA2_geo.tex").write_text(
        "\\begin{tabular}{lccc}\n\\toprule\n"
        "阶段 & $n_{\\text{州}}$ & 几何项占 $\\tau^2$ & 过程方差总占比 \\\\\n\\midrule\n"
        + "\n".join(rows_geo)
        + "\n\\midrule\n跨阶段范围 & --- & $58.0\\%$--$83.0\\%$ & $0.729$--$0.890$ \\\\\n"
        "\\bottomrule\n\\end{tabular}\n", encoding="utf-8")

    print("[OK] wrote tableA1_i0.tex, tableA2_geo.tex")
    print("I0 last range:",
          f"{min(i0[k]['median_pct_change_last'] for k, _ in PHASES):+.2f} .. "
          f"{max(i0[k]['median_pct_change_last'] for k, _ in PHASES):+.2f}")
    print("I0 fitend range:",
          f"{min(i0[k]['median_pct_change_fitend'] for k, _ in PHASES):+.2f} .. "
          f"{max(i0[k]['median_pct_change_fitend'] for k, _ in PHASES):+.2f}")


if __name__ == "__main__":
    main()
