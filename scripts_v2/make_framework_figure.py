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
    ax.text(sb_x0 + 0.058, y0 + 0.728, "机制工作模型架构", fontsize=8.6, fontweight="bold", color="#1e3a8a", zorder=4)
    t1_1 = (
        "• 微观分支过程（个体传播链级）:\n"
        "  $Z_{t+1} \\mid Z_t \\sim \\mathrm{NB}(R Z_t, k_{\\mathrm{ind}} Z_t)$\n"
        "  超临界饱和常数地板: $\\mathrm{CV}^2_\\infty = \\frac{1 + R/k_{\\mathrm{ind}}}{I_0(R-1)}$\n"
        "• 宏观聚合更新模型（周度住院序列）:\n"
        "  $I_{t+1} \\mid I_t \\sim \\mathrm{NB}(R_{\\mathrm{agg}} I_t, k_{\\mathrm{agg}})$\n"
        "  宏观条件方差含二次项: $R I_t + \\frac{R^2 I_t^2}{k_{\\mathrm{agg}}}$"
    )
    ax.text(sb_x0 + 0.008, y0 + 0.628, t1_1, fontsize=7.4, color="#1e293b", va="center", zorder=4)

    # Subbox 1.2: 定理 5 精确有限步方差闭式递推
    draw_subbox(ax, sb_x0, y0 + 0.310, sb_w, 0.220, "white", "#cbd5e1",
                tag_text="闭式递推", tag_color=c_blue, zorder=2)
    ax.text(sb_x0 + 0.058, y0 + 0.518, "定理 5 有限步精确方差", fontsize=8.6, fontweight="bold", color="#1e3a8a", zorder=4)
    t1_2 = (
        "• 一阶非齐次全方差递推方程:\n"
        "  $V_{t+1} = q V_t + I_0 R^{t+1} + \\frac{I_0^2 R^{2t+2}}{k_{\\mathrm{agg}}}$\n"
        "  公比 $q = R^2 \\left(1 + \\frac{1}{k_{\\mathrm{agg}}}\\right) > R^2$\n"
        "• 有限步代数封闭解:\n"
        "  $V_h = q^h V_0 + \\sum_{j=1}^h q^{h-j} \\left(I_0 R^j + \\frac{I_0^2 R^{2j}}{k_{\\mathrm{agg}}}\\right)$\n"
        "  $\\Rightarrow \\mathrm{CV}^2_{\\mathrm{macro}}(h)$ 随步长严格单调几何发散"
    )
    ax.text(sb_x0 + 0.008, y0 + 0.405, t1_2, fontsize=7.4, color="#1e293b", va="center", zorder=4)

    # Subbox 1.3: 决策论下界与视界定义
    draw_subbox(ax, sb_x0, y0 + 0.012, sb_w, 0.288, "white", "#cbd5e1",
                tag_text="决策推导", tag_color=c_blue, zorder=2)
    ax.text(sb_x0 + 0.058, y0 + 0.288, "定理 1 决策界与视界求根", fontsize=8.6, fontweight="bold", color="#1e3a8a", zorder=4)
    t1_3 = (
        "• 条件均值预测器锐风险下界 (Thm 1):\n"
        "  $\\min_\\delta \\mathcal{R}(\\delta) = \\operatorname{Var}(I_h \\mid I_0)$\n"
        "• 对数正态后验混合参数外推项 (Prop 3):\n"
        "  $P(h) = \\exp(2h^2 s^2) - 2\\exp(\\frac{1}{2}h^2 s^2) + 1$\n"
        "• 条件精确机制视界方程:\n"
        "  $\\operatorname{RelMSE}(h) = \\mathrm{CV}^2_{\\mathrm{macro}}(h) + P(h) = \\tau^2$\n"
        "  在容忍误差 $\\tau=0.5$ 下二分数值求根 $h^*$\n"
        "【明确防御】作为模型条件基准而非物理绝对上限"
    )
    ax.text(sb_x0 + 0.008, y0 + 0.142, t1_3, fontsize=7.3, color="#1e293b", va="center", zorder=4)

    # -------------------------------------------------------------------------
    # Pillar 2: 多尺度实证证据链与误差记账 (Empirical Evidence)
    # -------------------------------------------------------------------------
    draw_card(ax, xs[1], y0, w, h, "#f0fdf4", c_teal, "第二支柱：多尺度实证与误差记账")
    sb_x1 = xs[1] + 0.008

    # Subbox 2.1: 微观传播链层
    draw_subbox(ax, sb_x1, y0 + 0.540, sb_w, 0.200, "white", "#cbd5e1",
                tag_text="微观拟合", tag_color=c_teal, zorder=2)
    ax.text(sb_x1 + 0.058, y0 + 0.728, "微观真实传播追踪层", fontsize=8.6, fontweight="bold", color="#115e59", zorder=4)
    t2_1 = (
        "• 真实传播网络金标准拟合:\n"
        "  香港 COVID-19 (N=355, 1038) 与几内亚埃博拉 (N=152)\n"
        "• 极大似然估计: 显著过度离散 $\\hat{k} \\in [0.11, 0.18]$\n"
        "  负二项拟合显著优于 Poisson ($\\Delta\\mathrm{AIC} \\geq 93.9$)\n"
        "• 信息论下界检验 (Theorem 4):\n"
        "  自助方差与 Cramér-Rao 界比值为 0.984--1.059"
    )
    ax.text(sb_x1 + 0.008, y0 + 0.628, t2_1, fontsize=7.4, color="#1e293b", va="center", zorder=4)

    # Subbox 2.2: 州级时空长面板
    draw_subbox(ax, sb_x1, y0 + 0.280, sb_w, 0.250, "white", "#cbd5e1",
                tag_text="州级面板", tag_color=c_teal, zorder=2)
    ax.text(sb_x1 + 0.058, y0 + 0.518, "51 州住院面板与机制视界", fontsize=8.6, fontweight="bold", color="#115e59", zorder=4)
    t2_2 = (
        "• 跨 3 种呼吸道病原体、7 个独立流行波次:\n"
        "  SARS-CoV-2 (Delta, Omicron, JN.1)\n"
        "  Influenza (2022-23, 2024-25), RSV (2024-25, 2025-26)\n"
        "• 宏观机制视界分布: 跨州中位数 $h^* \\in [2.2, 7.1]$ 周\n"
        "• 空间聚合平滑效应: 7 阶段中 6 个阶段州级短于国家级\n"
        "• 过程内在方差占主导: $\\mathrm{CV}^2/\\tau^2$ 达 73%--89%\n"
        "• 经验外包络性: 机制视界高于同口径实测时效"
    )
    ax.text(sb_x1 + 0.008, y0 + 0.392, t2_2, fontsize=7.3, color="#1e293b", va="center", zorder=4)

    # Subbox 2.3: 三项描述性误差记账
    draw_subbox(ax, sb_x1, y0 + 0.012, sb_w, 0.258, "white", "#cbd5e1",
                tag_text="误差记账", tag_color=c_teal, zorder=2)
    ax.text(sb_x1 + 0.058, y0 + 0.258, "无偏描述性误差恒等分解", fontsize=8.6, fontweight="bold", color="#115e59", zorder=4)
    t2_3 = (
        "• 样本均方预测误差无偏描述性恒等式:\n"
        "  $\\operatorname{RelMSE}_{\\mathrm{obs}}(h) = \\mathrm{CV}^2_{\\mathrm{macro}}(h) + P_{\\mathrm{plug}}(h) + \\mathcal{E}_{\\mathrm{res}}(h)$\n"
        "• 机制分量: 过程内在离散 + 参数外推项\n"
        "• 消除负交叉项争议，代数严格闭合\n"
        "• 全美各阶段中位未归因闭合余项: $\\mathcal{E}_{\\mathrm{res}} = 55.0\\%$\n"
        "  量化结构误配、非平稳行为与毒株漂移所占缺口"
    )
    ax.text(sb_x1 + 0.008, y0 + 0.128, t2_3, fontsize=7.3, color="#1e293b", va="center", zorder=4)

    # -------------------------------------------------------------------------
    # Pillar 3: CDC FluSight 连续三赛季外部审计 (External Operational Audit)
    # -------------------------------------------------------------------------
    draw_card(ax, xs[2], y0, w, h, "#eef2ff", c_indigo, "第三支柱：CDC FluSight 三季审计")
    sb_x2 = xs[2] + 0.008

    # Subbox 3.1: 数据固化与审计方案
    draw_subbox(ax, sb_x2, y0 + 0.540, sb_w, 0.200, "white", "#cbd5e1",
                tag_text="版本锁定", tag_color=c_indigo, zorder=2)
    ax.text(sb_x2 + 0.058, y0 + 0.728, "权威外部基准与版本锁定", fontsize=8.6, fontweight="bold", color="#3730a3", zorder=4)
    t3_1 = (
        "• 覆盖连续 3 个完整流感季 (2023--2026):\n"
        "  2023-24 (v1.0.0), 2024-25 (v1.1.0), 2025-26 (v1.2.0)\n"
        "• 204 个官方预测文件、12,384+ 组评估时空单元\n"
        "• 逐字节 SHA-256 哈希校验，零未来信息泄露\n"
        "• 全流程代码与历史预测流水线逐级可复现"
    )
    ax.text(sb_x2 + 0.008, y0 + 0.628, t3_1, fontsize=7.4, color="#1e293b", va="center", zorder=4)

    # Subbox 3.2: 严格四方交集
    draw_subbox(ax, sb_x2, y0 + 0.310, sb_w, 0.220, "white", "#cbd5e1",
                tag_text="四方交集", tag_color=c_indigo, zorder=2)
    ax.text(sb_x2 + 0.058, y0 + 0.518, "同条件配对对垒协议", fontsize=8.6, fontweight="bold", color="#3730a3", zorder=4)
    t3_2 = (
        "• 审计对垒模型池 (严格同条件配对):\n"
        "  ① FluSight-ensemble (全美顶尖多机构集成)\n"
        "  ② FluSight-baseline (官方朴素持续性基线)\n"
        "  ③ Plug-in mechanistic (插件式机制预测器)\n"
        "  ④ CDC 最终回填住院真实值 (Ground Truth)\n"
        "• 概率评估指标: 加权区间评分 (WIS)、MAE、\n"
        "  经验覆盖率 (Cover50/80/95) 与区间锐度"
    )
    ax.text(sb_x2 + 0.008, y0 + 0.405, t3_2, fontsize=7.3, color="#1e293b", va="center", zorder=4)

    # Subbox 3.3: 跨步长技能衰减
    draw_subbox(ax, sb_x2, y0 + 0.012, sb_w, 0.288, "white", "#cbd5e1",
                tag_text="时效衰减", tag_color=c_indigo, zorder=2)
    ax.text(sb_x2 + 0.058, y0 + 0.288, "多步预测技能与时效衰退", fontsize=8.6, fontweight="bold", color="#3730a3", zorder=4)
    t3_3 = (
        "• $h=1 \\to 4$ 周超前预测 WIS 呈快速单调恶化\n"
        "• 集成模型在点预测均方误差上优于插件式机制预测器\n"
        "• COVIDhub-ensemble 跨波次历史对照 (Delta/Omicron):\n"
        "  在 1--2 周内相对朴素基准丧失技能优势 (SERatio $\\geq 1$)\n"
        "• 证实预测技能在短步长内的迅速衰退是各类重大\n"
        "  呼吸道传染病暴发期的共性物理与动力学瓶颈"
    )
    ax.text(sb_x2 + 0.008, y0 + 0.142, t3_3, fontsize=7.3, color="#1e293b", va="center", zorder=4)

    # -------------------------------------------------------------------------
    # Pillar 4: 核心发现与公卫运筹闭环 (Key Discovery & Operations)
    # -------------------------------------------------------------------------
    draw_card(ax, xs[3], y0, w, h, "#fef2f2", c_crimson, "第四支柱：峰值相对位置分层与公卫运筹")
    sb_x3 = xs[3] + 0.008

    # Subbox 4.1: 峰后期 vs 峰前期对比
    draw_subbox(ax, sb_x3, y0 + 0.505, sb_w, 0.235, "white", "#cbd5e1",
                tag_text="核心特征", tag_color=c_crimson, zorder=2)
    ax.text(sb_x3 + 0.058, y0 + 0.728, "经验特征：峰前期经验覆盖率较低", fontsize=8.6, fontweight="bold", color="#991b1b", zorder=4)
    t4_1 = (
        "• 峰后期 (Post-peak) —— 近标称良好校准:\n"
        "  Hub 集成 95% 覆盖率稳定在 0.925--0.964\n"
        "  官方 Baseline 覆盖率为 0.881--0.922\n"
        "  退潮期自阻尼占优，系统表现出优良统计校准\n"
        "• 峰前期 (Pre-peak) —— 经验覆盖率显著偏低:\n"
        "  Hub 集成覆盖率降至 0.419--0.852\n"
        "  官方 Baseline 覆盖率降至 0.488--0.759\n"
        "  插件式机制预测器仅 0.140--0.385！"
    )
    ax.text(sb_x3 + 0.008, y0 + 0.610, t4_1, fontsize=7.3, color="#1e293b", va="center", zorder=4)

    # Subbox 4.2: 机制根源分析
    draw_subbox(ax, sb_x3, y0 + 0.260, sb_w, 0.235, "white", "#cbd5e1",
                tag_text="机制透视", tag_color=c_crimson, zorder=2)
    ax.text(sb_x3 + 0.058, y0 + 0.483, "虚假精确度与指数型前向放大", fontsize=8.6, fontweight="bold", color="#991b1b", zorder=4)
    t4_2 = (
        "• 参数外推误差随步长发生指数型前向放大:\n"
        "  $P(h) \\sim \\exp(2h^2 s^2)$ 高阶超指数膨胀\n"
        "• 预测系统表现出潜在【虚假精确度】(False Precision)\n"
        "• 真实住院人数系统性突破预测区间上限\n"
        "• 揭示黑盒统计集成在峰前期表现出严重欠覆盖"
    )
    ax.text(sb_x3 + 0.008, y0 + 0.366, t4_2, fontsize=7.3, color="#1e293b", va="center", zorder=4)

    # Subbox 4.3: 公共卫生决策启示
    draw_subbox(ax, sb_x3, y0 + 0.012, sb_w, 0.238, "white", "#cbd5e1",
                tag_text="运筹启示", tag_color=c_crimson, zorder=2)
    ax.text(sb_x3 + 0.058, y0 + 0.238, "非对称损失与动态不确定性", fontsize=8.6, fontweight="bold", color="#991b1b", zorder=4)
    t4_3 = (
        "• 公共卫生非对称损失结构 (Asymmetric Loss):\n"
        "  低估发病带来医疗挤兑与超额重症超额死亡\n"
        "  $\\mathcal{L}_{\\mathrm{under}}(e) \\gg \\mathcal{L}_{\\mathrm{over}}(e)$\n"
        "• 决策建议: 禁止在峰前期将标称区间视作刚性安全边界;\n"
        "  实施峰前期动态不确定性膨胀因子，为 ICU 扩容与\n"
        "  抗病毒药物调配保留 2--4 周的前置运筹缓冲"
    )
    ax.text(sb_x3 + 0.008, y0 + 0.120, t4_3, fontsize=7.3, color="#1e293b", va="center", zorder=4)

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
