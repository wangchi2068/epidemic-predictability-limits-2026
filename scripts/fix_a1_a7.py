"""Fix A1 (EN fig:real_horizons caption) and A7 (CN fig1_horizon caption)."""

from pathlib import Path

EN = Path("paper_en/main.tex")
CN = Path("paper_cn/main.tex")

# ---- A1: EN real_horizons caption must match Table 1 / JSON ----
en = EN.read_text(encoding="utf-8")
old_cap = (
    r"\caption{\textbf{Real-data predictability horizons.} Illustrative constant-$R$ "
    r"horizons $h^*$ (weeks) for national COVID-19, RSV, and influenza (2020--2023). "
    r"Horizontal bars show point estimates with 95\% bootstrap confidence intervals. "
    r"COVID horizon 23--68 weeks reflects sustained near-threshold conditions; "
    r"RSV 0--12 weeks and influenza 15--28 weeks reflect higher $R$ variability "
    r"and lower cumulative incidence.}"
)
new_cap = (
    r"\caption{\textbf{Real-data predictability horizons.} Illustrative constant-$R$ "
    r"horizons $h^*$ (weeks) for national COVID-19, RSV, and influenza phases from "
    r"Table~\ref{tab:horizons} (2021--2025 surveillance windows). Horizontal bars show "
    r"point estimates with 95\% bootstrap confidence intervals. The largest horizons "
    r"(RSV 2025--26: 68 weeks) arise from the most precise $R$ estimates; phases with "
    r"$R<1$ (COVID Omicron peak, Flu 2022--23 peak) yield $h^*=0$.}"
)
assert old_cap in en, "A1 caption pattern not found in EN"
en = en.replace(old_cap, new_cap)
EN.write_text(en, encoding="utf-8")
print("A1 EN fixed")

# ---- A7: CN Theorem-1 figure caption claims two panels but only fig1_horizon.png included ----
cn = CN.read_text(encoding="utf-8")
# add the second panel to match the caption, mirroring EN's two-panel figure
old_fig = (
    r"\begin{figure}[htbp]" + "\n"
    r"\centering" + "\n"
    r"\includegraphics[width=0.75\textwidth]{../reports/figures/fig1_horizon.png}"
    + "\n"
    r"\caption{\textbf{定理1验证。}左图：不同初始种子$I_0$下可预测视界$h^*$与$R$的关系，显示$(R/\delta R)$标度律。右图：变异系数(CV)理论值与实证验证跨参数域；比值0.99--1.03确认人口噪声分解。}"
    + "\n"
    r"\label{fig:t1_verify_cn}" + "\n"
    r"\end{figure}"
)
new_fig = (
    r"\begin{figure}[htbp]" + "\n"
    r"\centering" + "\n"
    r"\includegraphics[width=0.48\textwidth]{../reports/figures/fig1_horizon.png}"
    + "\n"
    r"\includegraphics[width=0.48\textwidth]{../reports/figures/fig2_cv_verify.png}"
    + "\n"
    r"\caption{\textbf{定理1验证。}左图：不同初始种子$I_0$下可预测视界$h^*$与$R$的关系，显示$(R/\delta R)$标度律。右图：变异系数(CV)理论值与实证验证跨参数域；比值0.99--1.03确认人口噪声分解。}"
    + "\n"
    r"\label{fig:t1_verify_cn}" + "\n"
    r"\end{figure}"
)
if old_fig in cn:
    cn = cn.replace(old_fig, new_fig)
    CN.write_text(cn, encoding="utf-8")
    print("A7 CN fixed (added second panel)")
else:
    print("A7: pattern not found, checking actual figure block")
    i = cn.find(
        r"\includegraphics[width=0.75\textwidth]{../reports/figures/fig1_horizon.png}"
    )
    print("fig1_horizon at", i)
