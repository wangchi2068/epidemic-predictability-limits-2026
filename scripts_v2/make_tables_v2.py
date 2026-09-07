# -*- coding: utf-8 -*-
"""
make_tables_v2.py — Emits LaTeX table bodies for Tables 2, 3, 4, 5, 6 from the v2
JSON outputs (single source of truth). Written to reports/table_bodies.tex and
consumed by main.tex via \\input. Also prints a plain-text audit copy.

Inputs:
  reports/table2_params.json   (pipeline.py)
  reports/table4_budget.json   (error_budget_v2.py)
  reports/rolling_results.json (rolling_eval_v2.py)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import solve_hstar  # noqa: E402


def fmt_ci(ci):
    if ci is None:
        return "--"
    return f"{ci[0]:.1f}--{ci[1]:.1f}"


def table2_body():
    d = json.loads((REPORTS / "table2_params.json").read_text(encoding="utf-8"))["table2"]
    order = ["Delta", "Omicron", "JN1", "flu22", "flu24", "rsv24", "rsv25"]
    trunc = {"rsv24": "16--20 周截断", "rsv25": "16--20 周截断"}
    rows = []
    for k in order:
        r = d[k]
        hgen = r["h_star_gen"]
        hwk = r["h_star_weeks"]
        cv2_inf = (1 + r["R_gen"] / r["k_agg"]) / (r["I0"] * (r["R_gen"] - 1))
        share = cv2_inf / 0.25 * 100
        rows.append(
            f"{r['display']} & {r['R_gen']:.4f} & {r['s_gen']:.4f} & {r['k_agg']:.1f} & "
            f"{int(r['I0']):,} & {r['mu_g_days']:.1f} & {hgen:.1f} / {hwk:.1f} & "
            f"{hwk:.1f} ({fmt_ci(r['ci95_weeks'])}) & {share:.2f}\\% & "
            f"{trunc.get(k, '--')} \\\\")
    return "\n".join(rows)


def table3_body():
    d = json.loads((REPORTS / "table2_params.json").read_text(encoding="utf-8"))["table3"]
    rows = []
    meta = {
        "Delta_growth": ("COVID-19 Delta 阶段", "早期指数爬坡期", "2021-W26 至 W30", "强超临界增长，信噪比充沛，视界良定。"),
        "Delta_peak": ("COVID-19 Delta 阶段", "平台达峰期", "2021-W35 至 W39", "有效再生数跌破 1，进入消退体制。"),
        "Delta_decline": ("COVID-19 Delta 阶段", "拐点消退期", "2021-W41 至 W45", "亚临界消退，期望衰退向吸收态转移。"),
        "Omicron_growth": ("COVID-19 Omicron 阶段", "早期暴发爬坡期", "2021-W49 至 2022-W03", "高传播株，推断方差大，视界承压。"),
        "Omicron_decline": ("COVID-19 Omicron 阶段", "达峰消退期", "2022-W04 至 W08", "暴发顶点急速转折，$R<1$。"),
        "flu22_growth": ("流感 2022--23 流行季", "早期指数爬坡期", "2022-W40 至 W44", "快速早期爬坡，短代间隔下视界有限。"),
        "flu22_decline": ("流感 2022--23 流行季", "达峰消退期", "2022-W48 至 W52", "流行季过峰回落，进入零星输入期。"),
    }
    for key, (path, phase, window, mech) in meta.items():
        r = d[key]
        star = "$^*$" if r["R_gen"] < 1 else ""
        rows.append(
            f"{path} & {phase} & {window} & {r['R_gen']:.4f} & {r['s_gen']:.4f} & "
            f"{r['k_agg']:.1f} & {int(r['I0']):,} & {r['h_star_weeks']:.1f} 周 "
            f"({r['h_star_gen']:.1f} 代){star} & {mech} \\\\")
    return "\n".join(rows)


def table4_body():
    d = json.loads((REPORTS / "table4_budget.json").read_text(encoding="utf-8"))
    disp = {"Delta": "COVID-19 Delta 暴发期", "Omicron": "COVID-19 Omicron 达峰期",
            "flu22": "流感 2022--23 暴发早期", "rsv24": "RSV 2024--25 流行季",
            "rsv25": "RSV 2025--26 流行季"}
    SC = 1e4
    rows = []
    for key in ["Delta", "Omicron", "flu22", "rsv24", "rsv25"]:
        rec = d[key]
        for hwk, r in rec["horizons"].items():
            tot = r["obs_total"] * SC
            cv2 = r["cv2"] * SC
            dr = r["e_drift"] * SC
            p = r["p_param"] * SC
            mis = r["e_misspec"] * SC
            rows.append(
                f"{disp[key]} & {hwk} 周 & {r['h_gen']:.2f} 代 & {tot:.1f} (100.0\\%) & "
                f"{cv2:.2f} ({r['share_cv2']*100:.2f}\\%) & {dr:.2f} ({r['share_drift']*100:.2f}\\%) & "
                f"{p:.2f} ({r['share_p']*100:.2f}\\%) & {mis:.1f} ({r['share_misspec']*100:.2f}\\%) \\\\")
        rows.append("\\midrule")
    return "\n".join(rows[:-1])


def table5_body():
    t2 = json.loads((REPORTS / "table2_params.json").read_text(encoding="utf-8"))["table2"]
    rr = json.loads((REPORTS / "rolling_results.json").read_text(encoding="utf-8"))
    rows = []
    for wave, key in [("Delta", "Delta"), ("Omicron", "Omicron"), ("Flu_22_23", "flu22")]:
        th = t2[key]["h_star_weeks"]
        ci = t2[key]["ci95_weeks"]
        c = rr[wave]["crossing"]["pers"]
        if c["point"] is None:
            rows.append(f"COVID-19 {wave} 阶段 & {th:.1f} 周 ({fmt_ci(ci)} 周) & 未穿越 & -- \\\\")
            continue
        ratio = th / c["point"]
        name = {"Delta": "COVID-19 Delta 阶段", "Omicron": "COVID-19 Omicron 阶段",
                "Flu_22_23": "流感 2022--23 阶段"}[wave]
        rows.append(
            f"{name} & {th:.1f} 周 ({fmt_ci(ci)} 周) & "
            f"{c['point']:.2f} 周 (95\\% CI {fmt_ci(c['ci95'])} 周) & {ratio:.2f} 倍 \\\\")
    return "\n".join(rows)


def table6_body():
    d = json.loads((REPORTS / "table2_params.json").read_text(encoding="utf-8"))["table2"]
    order = ["Delta", "Omicron", "JN1", "flu22", "flu24", "rsv24", "rsv25"]
    disp = {"Delta": "COVID-19 Delta 暴发期", "Omicron": "COVID-19 Omicron 达峰期",
            "JN1": "COVID-19 JN.1 流行期", "flu22": "流感 2022--23 暴发早期",
            "flu24": "流感 2024--25 流行季", "rsv24": "RSV 2024--25 流行季",
            "rsv25": "RSV 2025--26 流行季"}
    strat = {
        "Delta": "低离散度波次，中长程外推相对平稳；采用集合预测中位数推进梯次床位筹备。",
        "Omicron": "高传播株，视界收缩；严控长程外推，实行见转折即报警的敏捷应急机制。",
        "JN1": "平缓爬坡期；聚焦 2--4 周内抗病毒药物分发与高危人群重点防护。",
        "flu22": "快速早期爬坡季；第 2--3 周完成儿科药物与门急诊运力跨区协同调配。",
        "flu24": "典型季节性流感波次；匹配 1--2 个月疫苗加强接种与聚集管控预警。",
        "rsv24": "数学外推根超单流行季自然跨度（16--20 周截断）；转向宏观峰值高度与总负荷评估。",
        "rsv25": "极低初始增长波次；放弃长程点位预报，采用流行季宏观总发病包络区间。",
    }
    rows = []
    nonrsv = {k: [] for k in range(4)}
    for k in order:
        r = d[k]
        vals = []
        for tau in [0.20, 0.35, 0.50, 0.70]:
            h = solve_hstar(r["R_gen"], r["s_gen"], r["k_agg"], r["I0"], tau=tau)
            vals.append(h * r["delta_g"])
        dag = "$^\\dagger$" if k.startswith("rsv") else ""
        cells = " & ".join(f"{v:.1f} 周 ({v/r['delta_g']:.1f} 代){dag}" for v in vals)
        rows.append(f"{disp[k]} & {cells} & {strat[k]} \\\\")
        if not k.startswith("rsv"):
            for i, v in enumerate(vals):
                nonrsv[i].append(v)
    lo = [min(v) for v in nonrsv.values()]
    hi = [max(v) for v in nonrsv.values()]
    rows.append("\\midrule")
    rows.append("\\textbf{非 RSV 视界总体区间} & " +
                " & ".join(f"\\textbf{{{a:.1f}--{b:.1f} 周}}" for a, b in zip(lo, hi)) +
                " & \\textbf{公卫应对全景}：由战术刚性应急向战略资源储备梯次推进。 \\\\")
    return "\n".join(rows)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    bodies = {
        "table2": table2_body(), "table3": table3_body(), "table4": table4_body(),
        "table5": table5_body(), "table6": table6_body(),
    }
    out = []
    for name, body in bodies.items():
        out.append(f"% ==== auto-generated {name} (make_tables_v2.py) ====\n{body}\n")
    (REPORTS / "table_bodies.tex").write_text("\n".join(out), encoding="utf-8")
    print("saved reports/table_bodies.tex", flush=True)
    for name, body in bodies.items():
        print(f"\n==== {name} ====")
        print(body)


if __name__ == "__main__":
    main()
