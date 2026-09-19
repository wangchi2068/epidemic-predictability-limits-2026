# -*- coding: utf-8 -*-
r"""make_framework_figure.py — Figure 1: methodological framework flowchart.

Layout note (2026-09 revision): the figure is printed at full text width
(17 cm). A four-column arrangement left each card only ~3.5 cm wide, which is
below the legibility floor once the canvas is scaled to print size. The layout
is therefore a 2x2 snake (1 top-left -> 2 top-right -> 3 bottom-right ->
4 bottom-left) on a square canvas, which doubles the horizontal room per card
and lets every label print at >= 7 pt. The in-figure title and footer caption
are omitted because the LaTeX \caption already provides them.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
FIGS = ROOT / "reports_v3" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "Segoe UI", "DejaVu Sans", "Arial"],
    "axes.unicode_minus": False,
})

CANVAS = (8.6, 10.0)         # printed at 17.3 x 20.1 cm -> scale 0.792
BODY_FS = 9.5
SUB_FS = 10.0
CARD_FS = 12.0


def draw_card(ax, x, y, w, h, bg, border, title, radius=0.010, hh=0.032):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad=0.004,rounding_size={radius}",
                                facecolor=bg, edgecolor=border, linewidth=1.8, zorder=1))
    ax.add_patch(FancyBboxPatch((x, y + h - hh), w, hh,
                                boxstyle=f"round,pad=0.004,rounding_size={radius}",
                                facecolor=border, edgecolor=border, linewidth=1, zorder=2))
    ax.text(x + w / 2, y + h - hh / 2, title, ha="center", va="center",
            fontsize=CARD_FS, fontweight="bold", color="white", zorder=3)


def draw_subbox(ax, x, y, w, h, border, tag, tag_color, title, color, zorder=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.003,rounding_size=0.006",
                                facecolor="white", edgecolor=border, linewidth=0.9,
                                zorder=zorder))
    pw, ph = 0.068, 0.0140
    px, py = x + 0.011, y + h - 0.0210
    ax.add_patch(FancyBboxPatch((px, py), pw, ph,
                                boxstyle="round,pad=0.002,rounding_size=0.004",
                                facecolor=tag_color, edgecolor=tag_color,
                                linewidth=0.5, zorder=zorder + 1))
    ax.text(px + pw / 2, py + ph / 2, tag, ha="center", va="center",
            fontsize=BODY_FS, fontweight="bold", color="white", zorder=zorder + 2)
    ax.text(px + pw + 0.012, py + ph / 2, title, ha="left", va="center",
            fontsize=SUB_FS, fontweight="bold", color=color, zorder=zorder + 2)


def body(ax, x, y, text, zorder=4):
    ax.text(x, y, text, fontsize=BODY_FS, color="#1e293b", va="top",
            ha="left", linespacing=1.5, zorder=zorder)


def arrow(ax, x1, y1, x2, y2, color, label=None, lx=0.0, ly=0.012):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                 arrowstyle="-|>,head_length=5,head_width=3.5",
                                 color=color, linewidth=2.2, zorder=10))
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, ha="center",
                va="center", fontsize=BODY_FS, fontweight="bold",
                color=color, zorder=11,
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor="none", alpha=0.85))


def generate_flowchart():
    fig = plt.figure(figsize=CANVAS, dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.fill_between([0, 1], 0, 1, color="#f8fafc", zorder=0)

    c_blue, c_teal, c_indigo, c_crimson = "#1e40af", "#0f766e", "#4338ca", "#b91c1c"
    w, h = 0.465, 0.455
    hh, gap = 0.032, 0.008
    sh = (h - hh - 0.014 - 2 * gap) / 3.0
    sw = w - 0.028

    def pillar(x0, y0, bg, border, title, subs, color):
        draw_card(ax, x0, y0, w, h, bg, border, title, hh=hh)
        x = x0 + 0.014
        ytop = y0 + h - hh - 0.014
        for i, (tag, subt, text) in enumerate(subs):
            sy = ytop - (i + 1) * sh - i * gap
            draw_subbox(ax, x, sy, sw, sh, "#cbd5e1", tag, color, subt, color)
            body(ax, x + 0.014, sy + sh - 0.034, text)

    # ---- Pillar 1: theory & scale isolation (top-left) ----
    pillar(0.020, 0.515, "#f0fdfa", c_blue, "第一支柱 · 机制推导与尺度隔离", [
        ("尺度隔离", "双层机制工作模型",
         "• 微观分支（个体传播链级）\n"
         "  $Z_{t+1}\\mid Z_t\\sim\\mathrm{NB}(RZ_t,k_{\\mathrm{ind}}Z_t)$\n"
         "  相对方差超临界有界饱和于 $\\mathrm{CV}^2_\\infty$\n"
         "• 宏观聚合更新（周度住院序列）\n"
         "  $I_{t+1}\\mid I_t\\sim\\mathrm{NB}(R_{\\mathrm{agg}}I_t,k_{\\mathrm{agg}})$，方差含 $R^2I_t^2/k_{\\mathrm{agg}}$"),
        ("闭式递推", "定理 5 有限步精确方差",
         "• 一阶非齐次全方差递推方程\n"
         "  $V_{t+1}=qV_t+I_0R^{t+1}+I_0^2R^{2t+2}/k_{\\mathrm{agg}}$\n"
         "  递推比率 $q=R^2(1+1/k_{\\mathrm{agg}})>R^2$\n"
         "• 有限步代数封闭解\n"
         "  $\\mathrm{CV}^2_{\\mathrm{macro}}(h)$ 随步长几何增长发散"),
        ("决策推导", "定理 1 决策界与视界求根",
         "• 条件均值达到锐条件风险地板（定理 1）\n"
         "  $\\min_{\\delta}\\mathcal{R}_h(\\delta)=V_h^{(M)}$\n"
         "• 参数外推精确放大项（引理 3）\n"
         "  $P_{\\mathrm{exact}}(h)=e^{2h^2s^2}-2e^{\\frac{1}{2}h^2s^2}+1$\n"
         "• 机制视界临界求根 $\\mathrm{CV}^2_{\\mathrm{macro}}+P_{\\mathrm{exact}}=\\tau^2$"),
    ], c_blue)

    # ---- Pillar 2: multi-scale evidence (top-right) ----
    pillar(0.515, 0.515, "#f0fdf4", c_teal, "第二支柱 · 多尺度实证与误差记账", [
        ("微观拟合", "微观真实传播追踪层",
         "• 真实传播网络金标准拟合：香港 COVID-19\n"
         "  与几内亚埃博拉三组队列（$N=355/1038/152$）\n"
         "• 负二项显著优于 Poisson，$\\Delta\\mathrm{AIC}=93.9\\text{--}244.0$\n"
         "• 极大似然方差贴合 Fisher 信息下界\n"
         "  自助方差与 CRB 比值 0.984--1.059（模型内检验）"),
        ("州级面板", "美国州级住院面板与机制视界",
         "• 最多 51 个州级辖区、3 种病原体、7 个流行阶段\n"
         "• 逐阶段满足准入门槛的辖区数为 26--51（表 3）\n"
         "• 插件式 NB2 机制视界中位数 2.2--7.1 周\n"
         "• 门槛放宽至 $\\geq 10$ 例后为 1.73--6.81 周\n"
         "• 空间聚合：6/7 阶段州级短于国家级"),
        ("误差记账", "描述性误差记账恒等式",
         "• $\\mathrm{RelMSE}_{\\mathrm{obs}}=\\mathrm{CV}^2_{\\mathrm{macro}}+P_{\\mathrm{quad}}+\\mathcal{E}_{\\mathrm{res}}$\n"
         "• 两项显式模型分量：过程方差 + 参数二次项\n"
         "• 跨州中位代数差额占比 55.0%（$h=1$ 为 45.4%）\n"
         "• 吸收未建模非平稳行为、变点与报告回填"),
    ], c_teal)

    # ---- Pillar 3: external audit (bottom-right) ----
    pillar(0.515, 0.030, "#eef2ff", c_indigo, "第三支柱 · CDC FluSight 外部审计", [
        ("版本锁定", "权威外部基准与版本锁定",
         "• 连续三个锁定流感季（2023--2026）\n"
         "• 204 个官方归档文件、逐字节 SHA-256 锁定\n"
         "• v1.2.0 以文件级校验和锁定（无 Git tag）\n"
         "• 回溯性终报审计：受控诊断性基准"),
        ("四方交集", "同条件配对对垒协议",
         "• 严格四方共同单元配对：\n"
         "  ① Hub 集成　② 官方基线　③ 机制预测器　④ 终报真值\n"
         "• 同一赛季三模型共享完全相同的 $n$\n"
         "• 多维评估：WIS、50/80/95% 覆盖率、区间宽与 PIT"),
        ("时效衰减", "多步预测技能与时效衰退",
         "• Hub 集成在各提前期保持配对评分优势\n"
         "• 机制预测器严重欠覆盖：标称 95% 区间\n"
         "  实测覆盖率仅 0.405--0.554\n"
         "• COVIDhub 历史对照：12 个原点中 11 个\n"
         "  在 1--2 周内穿透持续性基线"),
    ], c_indigo)

    # ---- Pillar 4: peak stratification & operations (bottom-left) ----
    pillar(0.020, 0.030, "#fef2f2", c_crimson, "第四支柱 · 峰值分层与公卫运筹", [
        ("核心特征", "峰前期经验覆盖率偏低",
         "• 峰后期：Hub 集成 95% 覆盖率 0.925--0.964\n"
         "  官方基线 0.881--0.922\n"
         "• 峰前期：Hub 集成降至 0.419--0.852\n"
         "  机制预测器仅 0.140--0.385\n"
         "• 属事后分层描述，不作显著性主张"),
        ("机制透视", "过度精确与指数型前向放大",
         "• 参数外推误差随步长发生指数型放大\n"
         "• 峰前期预测系统表现出过度精确信号\n"
         "• 实测发病更易突破预测区间，导致欠覆盖\n"
         "• 属描述性差异，未识别单一因果机制"),
        ("运筹启示", "非对称损失与动态不确定性",
         "• 非对称损失：低估发病带来医疗挤兑\n"
         "  $\\mathcal{L}_{\\mathrm{under}}(e)\\gg\\mathcal{L}_{\\mathrm{over}}(e)$\n"
         "• 峰前期勿将标称区间视作刚性边界\n"
         "• 实施阶段特异的不确定性膨胀因子"),
    ], c_crimson)

    # ---- snake arrows: 1 -> 2 -> 3 -> 4 ----
    arrow(ax, 0.487, 0.742, 0.513, 0.742, c_blue, "微观拟合", ly=0.020)
    arrow(ax, 0.742, 0.507, 0.742, 0.483, c_teal, "外部基准")
    arrow(ax, 0.513, 0.257, 0.487, 0.257, c_crimson, "分层审计", ly=0.020)

    out = FIGS / "fig1_framework.png"
    fig.savefig(out, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    fig.savefig(FIGS / "fig1_framework.pdf", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print("Generated flowchart successfully:", out)


if __name__ == "__main__":
    generate_flowchart()
