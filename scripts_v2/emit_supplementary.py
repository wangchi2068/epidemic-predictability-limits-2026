# -*- coding: utf-8 -*-
"""emit_supplementary.py — build the supplementary table set S1--S9.

S1  notation glossary                     (hand-maintained, paper's notation)
S2  sample-size benchmarks & MC grid      reports/verify_t4.json
S3  data provenance / leakage audit       tables_v3/tab_leakage.tex
S4  horizon calibre definitions           tables_v3/tab_caliber_def.tex
S5  per-phase six-calibre horizon panel   reports_v3/caliber_table.json
S6  window / k-agg sensitivity matrix     tables_v3/tab_sensitivity.tex
S7  tolerance-tier warning map            tables_v3/table7_tiers.tex
S8  FluSight per-horizon score panel      reports_v3/flusight_v1.*_extended.json
S9  COVIDhub 12-origin skill decay        tables_v3/table6_hub.tex

Writes tables_v3/supp_s1.tex, supp_s2.tex, supp_s5.tex, supp_s8.tex.
Fragments backed by an existing generated file are input directly by the
supplementary document, so they stay under the consistency gate.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables_v3"
REPORTS = ROOT / "reports_v3"
REPORTS_OLD = ROOT / "reports"

S1_SYMBOLS = [
    (r"$\mathcal{F}_t$", "预测原点信息集", "原点 $t$ 处严格可得的全部历史与外生信息"),
    (r"$Y_{t+h}$", "预测目标", "前瞻 $h$ 步的真实状态（终报真值口径下 $Y_{t+h}=Z_{t+h}$）"),
    (r"$\delta_h$", "预测规则", r"$\mathcal{F}_t$ 可测且二阶可积的实随机变量"),
    (r"$m_h,\,V_h$", "条件均值与条件方差", r"$m_h=\mathbb{E}[Y_{t+h}\mid\mathcal{F}_t]$，$V_h=\operatorname{Var}(Y_{t+h}\mid\mathcal{F}_t)$"),
    (r"$\mathcal{R}_h(\delta_h)$", "条件平方预测风险", r"$\mathbb{E}[(Y_{t+h}-\delta_h)^2\mid\mathcal{F}_t]$；最小值为地板 $V_h$"),
    (r"$Z_t$", "周度宏观观测", "第 $t$ 周全辖区报告的新增住院计数"),
    (r"$R$", "代际增长乘子", "个体级（代际时钟）基本再生数"),
    (r"$R_{\text{周}}$", "周度增长乘子", r"$\exp(b_{\text{week}})$；宏观主口径使用"),
    (r"$s_{\text{周}}$", "斜率对数标准误", r"$\operatorname{SE}(b_{\text{week}})$，自由度 $3$（$W=5$）"),
    (r"$k_{\text{ind}}$", "个体级离散度", "个体子代分布负二项的 size 参数"),
    (r"$k_{\text{agg}}$", "宏观聚合离散度", "州级周度序列的有效离散度（对数差分二阶矩估计，上限 1,000）"),
    (r"$I_0$", "初始发病规模", "推断窗口内周度均值（平滑初始状态）"),
    (r"$\text{CV}^2_{\text{macro}}(h)$", "宏观过程相对方差", r"固定 $k_{\text{agg}}$ 的 NB2 更新模型有限步精确方差除以均值平方"),
    (r"$P_{\text{exact}}(h)$", "参数外推项（精确）", r"$\exp(2h^2s^2)-2\exp(h^2s^2/2)+1$（对数正态精确式）"),
    (r"$P_{\text{quad}}(h)$", "参数外推项（领先阶）", r"$(h_{\text{周}}s_{\text{周}})^2$，用于误差记账"),
    (r"$h^*$", "机制视界", r"$\text{RelMSE}(h)$ 首次达到容忍度 $\tau$ 的连续阈值根"),
    (r"$h^*_{\text{obs}}$", "实测绝对误差视界", "各州滚动误差首次穿越同一 $\tau$ 的插值点"),
    (r"$\tau$", "容忍度阈值", "本文主口径 $\\tau=0.5$"),
    (r"$\mathcal{E}_{\text{res}}(h)$", "模型—观测代数差额", r"$\text{RelMSE}_{\text{obs}}-(\text{CV}^2_{\text{macro}}+P_{\text{quad}})$，描述性记账"),
    (r"$\phi,\,s_e^2$", "AR(1) 持续性参数", "环境漂移自相关系数与其创新方差（$|\\phi|<1$）"),
    (r"$\text{WIS}$", "加权区间评分", "基于 23 个标准分位数的严格适当评分规则"),
    (r"$\text{PIT}$", "概率积分变换", "分位数插值近似随机化 PIT，完美校准时服从均匀分布"),
    (r"$C$", "理想样本量基准", "给定效应量与功效下由 CRB 反解的单代完全观测样本量"),
]


def emit_s1() -> None:
    rows = [f"{a} & {b} & {c} \\\\" for a, b, c in S1_SYMBOLS]
    body = ("\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{2.6cm}"
            ">{\\raggedright\\arraybackslash}p{3.2cm}"
            ">{\\raggedright\\arraybackslash}p{9.0cm}@{}}\n"
            "\\toprule\n符号 & 名称 & 定义与口径 \\\\\n\\midrule\n"
            + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (TABLES / "supp_s1.tex").write_text(body, encoding="utf-8")
    print("[OK] supp_s1.tex", len(S1_SYMBOLS), "rows")


def emit_s2() -> None:
    d = json.loads((REPORTS_OLD / "verify_t4.json").read_text(encoding="utf-8"))
    rows = []
    for key, r in d.items():
        rows.append("{:.2f} & {:.3f} & {} & {} & {:.3e} & {:.3e} & {:.4f} & {:+.2e} \\\\".format(
            r["R"], r["k"], r["C"], r["reps"], r["emp_var"], r["crb"], r["ratio"], r["bias"]))
    body = ("\\begin{tabular}{ccccrrrr}\n\\toprule\n"
            "$R$ & $k$ & $C$ & 重复次数 & 经验方差 & CRB & 经验/CRB & 偏差 \\\\\n\\midrule\n"
            + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (TABLES / "supp_s2.tex").write_text(body, encoding="utf-8")
    print("[OK] supp_s2.tex", len(rows), "rows")


def emit_s5() -> None:
    d = json.loads((REPORTS / "caliber_table.json").read_text(encoding="utf-8"))
    order = ["macro", "macro_lin", "heuristic", "k0.434", "k0.182", "k0.111", "observed", "persistence"]
    head = ["$h^*_{\\text{macro}}$", "$h^*_{\\text{macro,lin}}$", "$h^*_{\\text{heur}}$",
            "$h^*_{k=0.434}$", "$h^*_{k=0.182}$", "$h^*_{k=0.111}$",
            "$h^*_{\\text{obs}}$", "$h^*_{\\text{persist}}$"]
    rows = []
    for key, rec in d.items():
        cells = []
        for f in order:
            v = rec.get(f)
            cells.append("---" if v is None else "{:.2f}".format(v))
        rows.append("{} & {} & ".format(rec["display"], rec["n_states"]) + " & ".join(cells) + " \\\\")
    body = ("\\begin{tabular}{@{}lrrrrrrrrr@{}}\n\\toprule\n"
            "阶段 & $n$ & " + " & ".join(head) + " \\\\\n\\midrule\n"
            + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (TABLES / "supp_s5.tex").write_text(body, encoding="utf-8")
    print("[OK] supp_s5.tex", len(rows), "rows")


SEASONS = [("v1.0", "v1.0.0 (2023--24)"), ("v1.1", "v1.1.0 (2024--25)"), ("v1.2", "v1.2.0 (2025--26)")]
MODELS = [("ensemble", "Hub 集成"), ("baseline", "官方基线"), ("mechanistic", "机制预测器")]


def emit_s8() -> None:
    rows = []
    for rel, disp in SEASONS:
        src = json.loads((REPORTS / "flusight_{}_extended.json".format(rel)).read_text(encoding="utf-8"))
        for hk in ["1", "2", "3"]:
            blk = src["by_horizon"][hk]
            for j, (mk, mdisp) in enumerate(MODELS):
                m = blk["by_model"][mk]
                season_cell = "\\multirow{{3}}{{*}}{{{}}} & ".format(disp) if j == 0 else "& "
                h_cell = "\\multirow{{3}}{{*}}{{{}}} & ".format(hk) if j == 0 else "& "
                rows.append(
                    season_cell + h_cell +
                    "{:,} & {:.2f} & {:.3f} & {:.3f} & {:.3f} & "
                    "{:.1f} & {:.1f} & {:.3f} \\\\".format(
                        m["n"], m["wis"], m["cover50"], m["cover80"], m["cover95"],
                        m["width80"], m["width95"], m["pit_mean"]))
            rows.append("\\midrule")
    rows = rows[:-1]
    body = ("\\begin{tabular}{@{}llrrrrrrrr@{}}\n\\toprule\n"
            "赛季 & $h$（周） & $n$ & WIS & 覆盖率 50\\% & 覆盖率 80\\% & 覆盖率 95\\% & "
            "80\\% 区间宽 & 95\\% 区间宽 & PIT 均值 \\\\\n\\midrule\n"
            + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (TABLES / "supp_s8.tex").write_text(body, encoding="utf-8")
    print("[OK] supp_s8.tex", len(rows), "body lines")


def main() -> None:
    emit_s1()
    emit_s2()
    emit_s5()
    emit_s8()


if __name__ == "__main__":
    main()
