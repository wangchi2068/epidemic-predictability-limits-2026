# -*- coding: utf-8 -*-
"""make_framework_figure.py — Publication-grade conceptual & methodological flowchart (Figure 1).

Generates a top-tier journal style workflow diagram illustrating:
1. First-Principles Theoretical Foundations & Scale Isolation
2. Multi-Scale Empirical Evidence & Descriptive Error Budget
3. CDC FluSight 3-Season Strict External Audit
4. Dynamic Phase Stratification & Public Health Operational Implications
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

plt.rcParams.update(
    {
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "Segoe UI", "DejaVu Sans", "Arial"],
        "axes.unicode_minus": False,
    }
)


def draw_card(ax, x, y, w, h, bg_color, border_color, title, radius=0.012):
    """Draw a rounded card container with a stylish header banner."""
    card = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.005,rounding_size={radius}",
                          facecolor=bg_color, edgecolor=border_color, linewidth=1.8,
                          zorder=1)
    ax.add_patch(card)
    
    # Header background strip
    hh = 0.052
    hdr = FancyBboxPatch((x, y + h - hh), w, hh, boxstyle=f"round,pad=0.005,rounding_size={radius}",
                         facecolor=border_color, edgecolor=border_color, linewidth=1,
                         zorder=2)
    ax.add_patch(hdr)
    ax.text(x + w / 2, y + h - hh / 2, title, ha="center", va="center",
            fontsize=11.0, fontweight="bold", color="white", zorder=3)


def draw_subbox(ax, x, y, w, h, bg_color, border_color, tag_text=None, tag_color="#1e40af", zorder=2):
    """Draw an inner content box with an optional stylish category pill."""
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.007",
                         facecolor=bg_color, edgecolor=border_color, linewidth=0.9,
                         zorder=zorder)
    ax.add_patch(box)
    
    if tag_text:
        pw, ph = 0.046, 0.020
        px, py = x + 0.008, y + h - 0.018
        pill = FancyBboxPatch((px, py), pw, ph, boxstyle="round,pad=0.002,rounding_size=0.004",
                              facecolor=tag_color, edgecolor=tag_color, linewidth=0.5, zorder=zorder+1)
        ax.add_patch(pill)
        ax.text(px + pw / 2, py + ph / 2, tag_text, ha="center", va="center",
                fontsize=6.8, fontweight="bold", color="white", zorder=zorder+2)


def draw_arrow(ax, x1, y1, x2, y2, color="#34495e", lw=2.2, zorder=10):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                            arrowstyle="-|>,head_length=5,head_width=3.5",
                            color=color, linewidth=lw, zorder=zorder)
    ax.add_patch(arrow)


def generate_flowchart():
    fig = plt.figure(figsize=(15.2, 9.4), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Canvas overall background
    ax.fill_between([0, 1], 0, 1, color="#f8fafc", zorder=0)

    # Main Title and Subtitle Banner
    ax.text(0.5, 0.967, "传染病传播动力学可预测视界、理论界限与多尺度实证审计全景架构",
            ha="center", va="center", fontsize=15.5, fontweight="bold", color="#0f172a", zorder=10)
    ax.text(0.5, 0.941, "Methodological & Theoretical Framework: From First-Principles Renewal to CDC Operational External Audit",
            ha="center", va="center", fontsize=9.4, style="italic", color="#475569", zorder=10)

    # 4 Main Columns / Pillars Layout Coordinates
    w = 0.222
    h = 0.81
    y0 = 0.085
    xs = [0.020, 0.268, 0.516, 0.764]

    # Colors
    c_blue = "#1e40af"       # Pillar 1: Theory
    c_teal = "#0f766e"       # Pillar 2: Empirical
    c_indigo = "#4338ca"     # Pillar 3: CDC Audit
    c_crimson = "#b91c1c"    # Pillar 4: Operational Finding

    sb_w = w - 0.016

    # -------------------------------------------------------------------------
    # Pillar 1: 理论基础与尺度隔离 (Theory & Scale Isolation)
    # -------------------------------------------------------------------------
    draw_card(ax, xs[0], y0, w, h, "#f0fdfa", c_blue, "第一支柱：机制推导与尺度隔离")
    sb_x0 = xs[0] + 0.008
    
    # Subbox 1.1: 尺度隔离双层模型
    draw_subbox(ax, sb_x0, y0 + 0.540, sb_w, 0.200, "white", "#cbd5e1",
                tag_text="尺度隔离", tag_color=c_blue, zorder=2)
    ax.text(sb_x0 + 0.058, y0 + 0.728, "机制工作模型架构", fontsize=9.0, fontweight="bold", color="#1e3a8a", zorder=4)
    t1_1 = (
        "• 微观分支过程（个体传播链级）:\n"
        "  $Z_{t+1} \\mid Z_t \\sim \\mathrm{NB}(R Z_t, k_{\\mathrm{ind}} Z_t)$\n"
        "  超临界有界饱和: $\\mathrm{CV}^2_\\infty = \\frac{1 + R/k_{\\mathrm{ind}}}{I_0(R-1)}$\n"
        "• 宏观聚合更新模型（周度住院序列）:\n"
        "  $I_{t+1} \\mid I_t \\sim \\mathrm{NB}(R_{\\mathrm{agg}} I_t, k_{\\mathrm{agg}})$\n"
        "  宏观条件方差含二次项: $R I_t + \\frac{R^2 I_t^2}{k_{\\mathrm{agg}}}$"
    )
    ax.text(sb_x0 + 0.008, y0 + 0.628, t1_1, fontsize=8.2, color="#1e293b", va="center", zorder=4)

    # Subbox 1.2: 定理 5 精确有限步方差闭式递推
    draw_subbox(ax, sb_x0, y0 + 0.310, sb_w, 0.220, "white", "#cbd5e1",
                tag_text="闭式递推", tag_color=c_blue, zorder=2)
    ax.text(sb_x0 + 0.058, y0 + 0.518, "定理 5 有限步精确方差", fontsize=9.0, fontweight="bold", color="#1e3a8a", zorder=4)
    t1_2 = (
        "• 一阶非齐次全方差递推方程:\n"
        "  $V_{t+1} = q V_t + I_0 R^{t+1} + \\frac{I_0^2 R^{2t+2}}{k_{\\mathrm{agg}}}$\n"
        "  递推比率 $q = R^2 (1 + 1/k_{\\mathrm{agg}}) > R^2$\n"
        "• 有限步代数封闭解:\n"
        "  $\\mathrm{CV}^2_{\\mathrm{macro}}(h)$ 随步长呈几何增长发散"
    )
    ax.text(sb_x0 + 0.008, y0 + 0.405, t1_2, fontsize=8.2, color="#1e293b", va="center", zorder=4)

    # Subbox 1.3: 决策论下界与视界定义
    draw_subbox(ax, sb_x0, y0 + 0.012, sb_w, 0.288, "white", "#cbd5e1",
                tag_text="决策推导", tag_color=c_blue, zorder=2)
    ax.text(sb_x0 + 0.058, y0 + 0.288, "定理 1 决策界与视界求根", fontsize=9.0, fontweight="bold", color="#1e3a8a", zorder=4)
    t1_3 = (
        "• 条件均值预测器锐风险下界 (定理 1):\n"
        "  $\\min_\\delta \\mathcal{R}(\\delta) = \\operatorname{Var}(I_h \\mid I_0) = V_h^{(M)}$\n"
        "• 参数外推精确放大项 (引理 2):\n"
        "  $P_{\\mathrm{exact}}(h) = e^{2h^2 s^2} - 2e^{\\frac{1}{2}h^2 s^2} + 1$\n"
        "• 机制视界临界求根方程:\n"
        "  $\\mathrm{CV}^2_{\\mathrm{macro}}(h) + P_{\\mathrm{exact}}(h) = \\tau^2$\n"
        "  作为模型条件基准而非物理绝对上限"
    )
    ax.text(sb_x0 + 0.008, y0 + 0.142, t1_3, fontsize=8.2, color="#1e293b", va="center", zorder=4)

    # -------------------------------------------------------------------------
    # Pillar 2: 多尺度实证证据链与误差记账 (Empirical Evidence)
    # -------------------------------------------------------------------------
    draw_card(ax, xs[1], y0, w, h, "#f0fdf4", c_teal, "第二支柱：多尺度实证与误差记账")
    sb_x1 = xs[1] + 0.008

    # Subbox 2.1: 微观传播链层
    draw_subbox(ax, sb_x1, y0 + 0.540, sb_w, 0.200, "white", "#cbd5e1",
                tag_text="微观拟合", tag_color=c_teal, zorder=2)
    ax.text(sb_x1 + 0.058, y0 + 0.728, "微观真实传播追踪层", fontsize=9.0, fontweight="bold", color="#115e59", zorder=4)
    t2_1 = (
        "• 真实传播网络金标准拟合:\n"
        "  香港 COVID-19 与几内亚埃博拉三组数据\n"
        "• 负二项拟合明显优于 Poisson ($\\Delta\\mathrm{AIC} \\geq 93.9$)\n"
        "• 极大似然估计验证 Fisher 信息量理论下界:\n"
        "  Bootstrap 方差与 CRB 比值为 0.984--1.059"
    )
    ax.text(sb_x1 + 0.008, y0 + 0.628, t2_1, fontsize=8.2, color="#1e293b", va="center", zorder=4)

    # Subbox 2.2: 州级时空长面板
    draw_subbox(ax, sb_x1, y0 + 0.280, sb_w, 0.250, "white", "#cbd5e1",
                tag_text="州级面板", tag_color=c_teal, zorder=2)
    ax.text(sb_x1 + 0.058, y0 + 0.518, "51 州住院面板与机制视界", fontsize=9.0, fontweight="bold", color="#115e59", zorder=4)
    t2_2 = (
        "• 51 个州级辖区、3 种病原体、7 个流行阶段\n"
        "• 插件式 NB2 机制视界中位数: 2.2--7.1 周\n"
        "• 空间聚合效应: 6/7 阶段州级短于国家级\n"
        "• 过程方差占主导: $\\mathrm{CV}^2/\\tau^2$ 达 73%--89%\n"
        "• 构成实测绝对误差视界的宽松经验参考外包络"
    )
    ax.text(sb_x1 + 0.008, y0 + 0.392, t2_2, fontsize=8.2, color="#1e293b", va="center", zorder=4)

    # Subbox 2.3: 三项描述性误差记账
    draw_subbox(ax, sb_x1, y0 + 0.012, sb_w, 0.258, "white", "#cbd5e1",
                tag_text="误差记账", tag_color=c_teal, zorder=2)
    ax.text(sb_x1 + 0.058, y0 + 0.258, "无偏描述性误差恒等分解", fontsize=9.0, fontweight="bold", color="#115e59", zorder=4)
    t2_3 = (
        "• 描述性代数记账恒等式:\n"
        "  $\\operatorname{RelMSE}_{\\mathrm{obs}}(h) = \\mathrm{CV}^2_{\\mathrm{macro}}(h) + P_{\\mathrm{quad}}(h) + \\mathcal{E}_{\\mathrm{res}}(h)$\n"
        "• 两项显式模型分量: 过程方差 + 参数二次项\n"
        "• 跨州中位模型—观测代数差额占比达 55.0%\n"
        "  综合吸收未建模非平稳行为、变点与报告回填"
    )
    ax.text(sb_x1 + 0.008, y0 + 0.128, t2_3, fontsize=8.2, color="#1e293b", va="center", zorder=4)

    # -------------------------------------------------------------------------
    # Pillar 3: CDC FluSight 连续三赛季外部审计 (External Operational Audit)
    # -------------------------------------------------------------------------
    draw_card(ax, xs[2], y0, w, h, "#eef2ff", c_indigo, "第三支柱：CDC FluSight 三季审计")
    sb_x2 = xs[2] + 0.008

    # Subbox 3.1: 数据固化与审计方案
    draw_subbox(ax, sb_x2, y0 + 0.540, sb_w, 0.200, "white", "#cbd5e1",
                tag_text="版本锁定", tag_color=c_indigo, zorder=2)
    ax.text(sb_x2 + 0.058, y0 + 0.728, "权威外部基准与版本锁定", fontsize=9.0, fontweight="bold", color="#3730a3", zorder=4)
    t3_1 = (
        "• 覆盖连续三个锁定流感季 (2023--2026)\n"
        "• 204 个官方归档文件、逐字节 SHA-256 锁定\n"
        "• 回溯性审计保证高数据质量压力测试\n"
        "• 全流程代码与历史预测流水线严格可复现"
    )
    ax.text(sb_x2 + 0.008, y0 + 0.628, t3_1, fontsize=8.2, color="#1e293b", va="center", zorder=4)

    # Subbox 3.2: 严格四方交集
    draw_subbox(ax, sb_x2, y0 + 0.310, sb_w, 0.220, "white", "#cbd5e1",
                tag_text="四方交集", tag_color=c_indigo, zorder=2)
    ax.text(sb_x2 + 0.058, y0 + 0.518, "同条件配对对垒协议", fontsize=9.0, fontweight="bold", color="#3730a3", zorder=4)
    t3_2 = (
        "• 严格四方共同单元配对评估:\n"
        "  ① Hub 集成 (多机构预测集成)\n"
        "  ② 官方基线 (持续性预测模型)\n"
        "  ③ 插件式机制预测器 (NB2 矩匹配构造)\n"
        "  ④ 最终住院真值序列\n"
        "• 概率多维评估: WIS、经验覆盖率与 PIT"
    )
    ax.text(sb_x2 + 0.008, y0 + 0.405, t3_2, fontsize=8.2, color="#1e293b", va="center", zorder=4)

    # Subbox 3.3: 跨步长技能衰减
    draw_subbox(ax, sb_x2, y0 + 0.012, sb_w, 0.288, "white", "#cbd5e1",
                tag_text="时效衰减", tag_color=c_indigo, zorder=2)
    ax.text(sb_x2 + 0.058, y0 + 0.288, "多步预测技能与时效衰退", fontsize=9.0, fontweight="bold", color="#3730a3", zorder=4)
    t3_3 = (
        "• Hub 集成在各提前期保持稳定的配对评分优势\n"
        "• 插件式机制预测器存在严重经验欠覆盖\n"
        "  标称 95% 区间实测覆盖率仅 0.405--0.554\n"
        "• COVIDhub 历史对照: 1--2 周内穿透基线\n"
        "  证实短步长技能衰退具有跨病原共性"
    )
    ax.text(sb_x2 + 0.008, y0 + 0.142, t3_3, fontsize=8.2, color="#1e293b", va="center", zorder=4)

    # -------------------------------------------------------------------------
    # Pillar 4: 核心发现与公卫运筹闭环 (Key Discovery & Operations)
    # -------------------------------------------------------------------------
    draw_card(ax, xs[3], y0, w, h, "#fef2f2", c_crimson, "第四支柱：峰值相对位置分层与公卫运筹")
    sb_x3 = xs[3] + 0.008

    # Subbox 4.1: 峰后期 vs 峰前期对比
    draw_subbox(ax, sb_x3, y0 + 0.505, sb_w, 0.235, "white", "#cbd5e1",
                tag_text="核心特征", tag_color=c_crimson, zorder=2)
    ax.text(sb_x3 + 0.058, y0 + 0.728, "经验特征：峰前期经验覆盖率较低", fontsize=9.0, fontweight="bold", color="#991b1b", zorder=4)
    t4_1 = (
        "• 峰后期 —— 经验覆盖率近标称水平:\n"
        "  Hub 集成 95% 覆盖率稳定在 0.925--0.964\n"
        "  官方基线覆盖率为 0.881--0.922\n"
        "• 峰前期 —— 经验覆盖率显著偏低:\n"
        "  Hub 集成覆盖率降至 0.419--0.852\n"
        "  插件式机制预测器仅为 0.140--0.385"
    )
    ax.text(sb_x3 + 0.008, y0 + 0.610, t4_1, fontsize=8.2, color="#1e293b", va="center", zorder=4)

    # Subbox 4.2: 机制根源分析
    draw_subbox(ax, sb_x3, y0 + 0.260, sb_w, 0.235, "white", "#cbd5e1",
                tag_text="机制透视", tag_color=c_crimson, zorder=2)
    ax.text(sb_x3 + 0.058, y0 + 0.483, "过度精确信号与指数型前向放大", fontsize=9.0, fontweight="bold", color="#991b1b", zorder=4)
    t4_2 = (
        "• 参数外推误差随步长发生指数型前向放大\n"
        "• 预测系统在峰前期表现出过度精确信号\n"
        "• 实测发病更易突破预测区间，导致欠覆盖\n"
        "• 该结果属描述性差异，未识别单一因果机制"
    )
    ax.text(sb_x3 + 0.008, y0 + 0.366, t4_2, fontsize=8.2, color="#1e293b", va="center", zorder=4)

    # Subbox 4.3: 公共卫生决策启示
    draw_subbox(ax, sb_x3, y0 + 0.012, sb_w, 0.238, "white", "#cbd5e1",
                tag_text="运筹启示", tag_color=c_crimson, zorder=2)
    ax.text(sb_x3 + 0.058, y0 + 0.238, "非对称损失与动态不确定性", fontsize=9.0, fontweight="bold", color="#991b1b", zorder=4)
    t4_3 = (
        "• 公共卫生非对称损失: 低估发病带来医疗挤兑\n"
        "  $\\mathcal{L}_{\\mathrm{under}}(e) \\gg \\mathcal{L}_{\\mathrm{over}}(e)$\n"
        "• 决策启示: 峰前期勿将标称区间视作刚性边界\n"
        "• 实施阶段特异的不确定性动态膨胀因子\n"
        "  为床位扩容与抗病毒药物调配保留安全缓冲"
    )
    ax.text(sb_x3 + 0.008, y0 + 0.120, t4_3, fontsize=8.2, color="#1e293b", va="center", zorder=4)

    # -------------------------------------------------------------------------
    # Connecting Arrows Across Pillars
    # -------------------------------------------------------------------------
    # Arrow 1 -> 2
    draw_arrow(ax, xs[0]+w+0.002, y0+0.64, xs[1]-0.002, y0+0.64, color=c_blue, lw=2.2)
    ax.text(xs[0]+w+0.012, y0+0.655, "微观拟合", fontsize=7.2, fontweight="bold", color=c_blue, zorder=10)

    draw_arrow(ax, xs[0]+w+0.002, y0+0.14, xs[1]-0.002, y0+0.14, color=c_blue, lw=2.2)
    ax.text(xs[0]+w+0.012, y0+0.155, "记账闭合", fontsize=7.2, fontweight="bold", color=c_blue, zorder=10)

    # Arrow 2 -> 3
    draw_arrow(ax, xs[1]+w+0.002, y0+0.42, xs[2]-0.002, y0+0.42, color=c_teal, lw=2.2)
    ax.text(xs[1]+w+0.012, y0+0.435, "外部基准", fontsize=7.2, fontweight="bold", color=c_teal, zorder=10)

    # Arrow 3 -> 4
    draw_arrow(ax, xs[2]+w+0.002, y0+0.62, xs[3]-0.002, y0+0.62, color=c_crimson, lw=2.4)
    ax.text(xs[2]+w+0.012, y0+0.635, "分层审计", fontsize=7.2, fontweight="bold", color=c_crimson, zorder=10)

    # Bottom Legend / Footer
    ax.text(0.5, 0.038, "图 1: 传染病传播动力学可预测视界理论推导、多尺度实证校准、CDC 业务审计与公共卫生运筹决策架构图",
            ha="center", va="center", fontsize=10.2, fontweight="bold", color="#1e293b", zorder=10)
    ax.text(0.5, 0.016, "Figure 1: Conceptual and Methodological Framework of Theoretical Horizons, Multi-Scale Empirical Calibration, and CDC FluSight Operational Audit",
            ha="center", va="center", fontsize=8.4, style="italic", color="#64748b", zorder=10)

    out = FIGS / "fig1_framework.png"
    fig.savefig(out, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    fig.savefig(FIGS / "fig1_framework.pdf", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print("Generated flowchart successfully:", out)


if __name__ == "__main__":
    generate_flowchart()
