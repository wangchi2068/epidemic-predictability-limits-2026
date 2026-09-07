# -*- coding: utf-8 -*-
"""
make_tables_v2.py — Emits COMPLETE tabular environments for Tables 2, 3, 4, 5, 6
from the v2 JSON outputs (single source of truth). Written per-table to
paper_cn_journal_template/tables/*_body.tex (\\input inside \\resizebox by main.tex)
and also to a combined reports/table_bodies.tex audit copy. Also prints a
plain-text audit copy.

Note: the 2024+ LaTeX kernel does not allow \\input to open/close a tabular row
stream, so each fragment contains the FULL tabular environment (spec + header +
rules + rows) and main.tex only wraps it in \\resizebox{...}{!}{...}.
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

TABSPECS = {
    "table2": ("lccccccrrrl", r"\textbf{病原体 / 流行阶段} & $R$ & $s$ & $k_{\text{agg}}$ & $I_0$ & $\mu_g$ (天) & $h^*_{\text{approx}}$ (代/周) & $h^*_{\text{exact}}$ (代/周, 95\% CI) & $\text{CV}^2$ 贡献率 & $h^*/W$ & \textbf{单流行季截断}"),
    "table3": ("llccccccrr", r"\textbf{病原体 / 阶段} & \textbf{动力学相位} & \textbf{观测时间窗口} & $R$ & $s$ & $k_{\text{agg}}$ & $I_0$ & $\mu_g$ (天) & $h^*_{\text{exact}}$ (周, 95\% CI) & $\text{CV}^2$ 贡献率"),
    "table4": ("llccccc", r"\textbf{病原体 / 流行阶段} & \textbf{前瞻步长 $h$ (周)} & \textbf{微观内在方差 $\text{CV}^2$} & \textbf{时变漂移方差 $\mathcal{E}_{\text{drift}}$} & \textbf{参数估计误差 $P$} & \textbf{未建模结构残差 $\mathcal{E}_{\text{misspec}}$} & \textbf{实测总误差 $\text{relMSE}^2_{\text{obs}}$}"),
    "table5": ("lcccr", r"\textbf{流行阶段 / 病原体} & \textbf{第一层：理论机制视界 $h^*_{\text{exact}}$} & \textbf{第二层：实测业务交叉点 $h_{\text{cross}}$} & \textbf{比值（第一层 / 第二层）} & $n_{\text{boot}}/1000$"),
    "table6": ("lccccl", r"\textbf{流行波次 / 决策场景} & $\tau=0.20$ (刚性生命线) & $\tau=0.35$ (资源调配线) & $\tau=0.50$ (群体干预线) & $\tau=0.70$ (战略规划线) & \textbf{推荐业务预测与公共卫生风控策略}"),
}


def wrap(name, rows):
    spec, header = TABSPECS[name]
    return "\n".join(
        [rf"\begin{{tabular}}{{{spec}}}", r"\toprule", header + r" \\", r"\midrule"]
        + rows + [r"\bottomrule", r"\end{tabular}"]
    )


def fmt_ci(ci):
    if ci is None:
        return "--"
    return f"{ci[0]:.1f}--{ci[1]:.1f}"


def table2_rows():
    d = json.loads((REPORTS / "table2_params.json").read_text(encoding="utf-8"))["table2"]
    order = ["Delta", "Omicron", "JN1", "flu22", "flu24", "rsv24", "rsv25"]
    trunc = {"rsv24": "16--20 周截断", "rsv25": "16--20 周截断"}
    W_WINDOW = 5.0  # inference window length in weeks (Table 2 protocol)
    rows = []
    for k in order:
        r = d[k]
        hgen = r["h_star_gen"]
        hwk = r["h_star_weeks"]
        cv2_inf = (1 + r["R_gen"] / r["k_agg"]) / (r["I0"] * (r["R_gen"] - 1))
        share = cv2_inf / 0.25 * 100
        # first-order supercritical closed form (eq. horizon_cn):
        # h*_gen = (1/s) * sqrt(tau^2 - CV^2_inf); h*_week = h*_gen * mu_g/7
        hgen_approx = (1.0 / r["s_gen"]) * (0.25 - cv2_inf) ** 0.5
        hwk_approx = hgen_approx * r["delta_g"]
        k_disp = f"{r['k_agg']:.1f}$^\\ddagger$" if r["k_agg"] >= 1000.0 else f"{r['k_agg']:.1f}"
        ratio = hwk / W_WINDOW
        rows.append(
            f"{r['display']} & {r['R_gen']:.4f} & {r['s_gen']:.4f} & {k_disp} & "
            f"{int(r['I0']):,} & {r['mu_g_days']:.1f} & {hgen_approx:.1f} / {hwk_approx:.1f} & "
            f"{hgen:.1f} / {hwk:.1f} ({fmt_ci(r['ci95_weeks'])}) & {share:.2f}\\% & "
            f"{ratio:.1f}× & {trunc.get(k, '--')} \\\\")
    return rows


def table3_rows():
    d = json.loads((REPORTS / "table2_params.json").read_text(encoding="utf-8"))["table3"]
    meta = {
        "Delta_growth":   ("COVID-19 Delta", "早期指数爬坡期", "2021-07-03 至 07-31"),
        "Delta_peak":     ("", "平台达峰期", "2021-08-21 至 10-02"),
        "Delta_decline":  ("", "消退期", "2021-10-02 至 11-13"),
        "Omicron_growth": ("COVID-19 Omicron", "早期指数爬坡期", "2021-12-04 至 2022-01-01"),
        "Omicron_peak":   ("", "平台达峰期", "2022-01-01 至 01-29"),
        "Omicron_decline":("", "消退期", "2022-01-29 至 03-12"),
        "flu22_growth":   ("流感 2022--23", "早期指数爬坡期", "2022-10-08 至 11-05"),
        "flu22_peak":     ("", "平台达峰期", "2022-11-26 至 12-24"),
        "flu22_decline":  ("", "消退期", "2022-12-24 至 2023-02-04"),
    }
    rows = []
    for key, (path, phase, window) in meta.items():
        r = d[key]
        star = "$^*$" if r["R_gen"] < 1 else ""
        if r["R_gen"] > 1:
            cv2_inf = (1 + r["R_gen"] / r["k_agg"]) / (r["I0"] * (r["R_gen"] - 1))
            share = f"{cv2_inf / 0.25 * 100:.2f}\\%"
        else:
            share = "--"
        k_disp = f"{r['k_agg']:.1f}$^\\ddagger$" if r["k_agg"] >= 1000.0 else f"{r['k_agg']:.1f}"
        rows.append(
            f"{path} & {phase} & {window} & {r['R_gen']:.4f} & {r['s_gen']:.4f} & "
            f"{k_disp} & {int(r['I0']):,} & {r['mu_g_days']:.1f} & "
            f"{r['h_star_weeks']:.1f} ({fmt_ci(r['ci95_weeks'])}){star} & {share} \\\\")
        if key.endswith("decline") and key != "flu22_decline":
            rows.append("\\midrule")
    return rows


def table4_rows():
    d = json.loads((REPORTS / "table4_budget.json").read_text(encoding="utf-8"))
    disp = {"Delta": "COVID-19 Delta 阶段", "Omicron": "COVID-19 Omicron 阶段",
            "flu22": "流感 2022--23 阶段", "rsv24": "RSV 2024--25 阶段",
            "rsv25": "RSV 2025--26 阶段"}
    SC = 1e4
    rows = []
    for key in ["Delta", "Omicron", "flu22", "rsv24", "rsv25"]:
        rec = d[key]
        for hwk, r in sorted(rec["horizons"].items(), key=lambda kv: int(kv[0])):
            cv2 = r["cv2"] * SC
            dr = r["e_drift"] * SC
            p = r["p_param"] * SC
            mis = r["e_misspec"] * SC
            tot = r["obs_total"] * SC
            rows.append(
                f"{disp[key]} & $h={hwk}$ 周 ({r['h_gen']:.1f} 代) & "
                f"{cv2:.1f} ({r['share_cv2']*100:.1f}\\%) & {dr:.1f} ({r['share_drift']*100:.1f}\\%) & "
                f"{p:.1f} ({r['share_p']*100:.1f}\\%) & {mis:.1f} ({r['share_misspec']*100:.1f}\\%) & "
                f"{tot:.1f} (100.0\\%) \\\\")
        if key != "rsv25":
            rows.append("\\midrule")
    return rows


def table5_rows():
    t2 = json.loads((REPORTS / "table2_params.json").read_text(encoding="utf-8"))["table2"]
    rr = json.loads((REPORTS / "rolling_results.json").read_text(encoding="utf-8"))
    rows = []
    for wave, key in [("Delta", "Delta"), ("Omicron", "Omicron"), ("Flu_22_23", "flu22")]:
        th = t2[key]["h_star_weeks"]
        ci = t2[key]["ci95_weeks"]
        c = rr[wave]["crossing"]["pers"]
        n_ok = c.get("n_boot_ok", 0)
        name = {"Delta": "COVID-19 Delta 阶段", "Omicron": "COVID-19 Omicron 阶段",
                "Flu_22_23": "流感 2022--23 阶段"}[wave]
        if c["point"] is None:
            rows.append(f"{name} & {th:.1f} 周 ({fmt_ci(ci)} 周) & 未穿越 & -- & {n_ok} \\\\")
            continue
        ratio = th / c["point"]
        rows.append(
            f"{name} & {th:.1f} 周 ({fmt_ci(ci)} 周) & "
            f"{c['point']:.2f} 周 ({fmt_ci(c['ci95'])} 周) & {ratio:.2f} 倍 & {n_ok} \\\\")
    return rows


def table6_rows():
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
        for i, tau in enumerate([0.20, 0.35, 0.50, 0.70]):
            if abs(tau - 0.50) < 1e-9:
                # reuse the stored Table-2 exact horizon verbatim (Minor 11: the
                # tau=0.50 column must be row-for-row identical to Table 2)
                v = r["h_star_weeks"]
            else:
                h = solve_hstar(r["R_gen"], r["s_gen"], r["k_agg"], r["I0"], tau=tau)
                v = h * r["delta_g"]
            vals.append(v)
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
    return rows


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    bodies = {
        "table2": wrap("table2", table2_rows()),
        "table3": wrap("table3", table3_rows()),
        "table4": wrap("table4", table4_rows()),
        "table5": wrap("table5", table5_rows()),
        "table6": wrap("table6", table6_rows()),
    }
    out = []
    for name, body in bodies.items():
        out.append(f"% ==== auto-generated {name} (make_tables_v2.py) ====\n{body}\n")
    (REPORTS / "table_bodies.tex").write_text("\n".join(out), encoding="utf-8",
                                              newline="\n")
    print("saved reports/table_bodies.tex", flush=True)
    # per-table full-environment fragments consumed by main.tex via \input
    frag_dir = ROOT / "paper_cn_journal_template" / "tables"
    frag_dir.mkdir(exist_ok=True)
    for name, body in bodies.items():
        (frag_dir / f"{name}_body.tex").write_text(
            f"% auto-generated by make_tables_v2.py — DO NOT EDIT BY HAND\n{body}\n",
            encoding="utf-8", newline="\n")
    print(f"saved per-table fragments to {frag_dir}", flush=True)
    for name, body in bodies.items():
        print(f"\n==== {name} ====")
        print(body)


if __name__ == "__main__":
    main()
