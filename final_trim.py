"""final_trim.py — last content trim pass; move QSD section to SI, compress simulation and empirical prose."""

from pathlib import Path

BASE = Path("D:/trae/epidemic_predictability_paper_final")
TEX = BASE / "main.tex"
SUPP = BASE / "supplementary.tex"
t = TEX.read_text(encoding="utf-8")
s = SUPP.read_text(encoding="utf-8")

# 1. move Section 2.5 (QSD + establishment) to SI
start = t.find("\\subsection{有限种群过程重标度与近临界动力学特征标度}")
end = t.find("\\subsection{状态辨识的信息论极限与 Cramér--Rao 界}")
if start > 0 and end > start:
    blk = t[start:end]
    t = t[:start] + (
        "\\subsection{有限种群过程重标度与近临界动力学特征标度}\\label{sec:qsd}\n\n"
        "在有限宿主种群中，传播阈值附近的近临界涨落可由带反射正则化的辅助扩散过程刻画："
        "平稳密度形如 $\\pi(x)\\propto x^{-1}\\exp(c_1x-c_2x^2)$，动力学重标度给出特征松弛时间候选标度 "
        "$t_{\\text{relax}}\\sim O(N^{1/2})$（命题~\\ref{prop:qsd}）；单输入病例的终极建群概率满足母函数不动点 "
        "$q=G(q)$，弱超临界下解析渐近为 $1-q\\approx 2\\varepsilon/[R^2(1+1/k_{\\text{ind}})]$"
        "（推论~\\ref{cor:establishment}）。该标度仅为近临界动力学的类比物理图像，"
        "不直接进入周度机制视界求解——后者的严格计算完全以定理~\\ref{thm:horizon} 与"
        "定理~\\ref{thm:macro_exact} 的方差方程为准。完整推导见补充材料。\n\n"
    ) + t[end:]
    i = s.rfind("\\bibliographystyle")
    s = s[:i] + "\n\n\\subsection*{命题 1 与推论 1 的证明要点}\n\n" + blk + "\n\n" + s[i:]
    print("Section 2.5 (QSD) moved to SI.")

# 2. compress Section 3 intro sentences
t = t.replace(
    "为检验第 2 节各定理类结论的数值自洽性（定理~\\ref{thm:sharp_floor}、\\ref{thm:horizon}、\\ref{thm:monotonicity}、\\ref{thm:fisher} 与定理 5R，命题~\\ref{prop:qsd} 与推论~\\ref{cor:establishment}），本文设计了高通量蒙特卡洛随机模拟实验。全部模拟按多组代表性参数执行，如表~\\ref{tab:sim_params} 所示。除特别说明外，20,000 条轨迹下方差型统计量的蒙特卡洛相对标准误约为 $\\sqrt{2/20{,}000} \\approx 1\\%$，故表中经验/理论比值偏离 1 的幅度需在该噪声尺度下解读。",
    "为检验第 2 节各定理类结论的数值自洽性，本文设计了高通量蒙特卡洛随机模拟实验（参数设置见补充材料表~\\ref{tab:sim_params}）。除特别说明外，20,000 条轨迹下方差型统计量的蒙特卡洛相对标准误约为 $1\\%$，故经验/理论比值偏离 1 的幅度需在该噪声尺度下解读。",
)
print("Section 3 intro compressed.")

# 3. compress Section 4.3 single paragraph
i43a = t.find("为检验\"州级短于国家级\"是否由抽样波动所致")
i43b = t.find("\\subsection{", i43a)
if i43a > 0 and i43b > i43a:
    t = t[:i43a] + (
        "逐州符号检验显示，七个阶段中有六个的大多数辖区视界短于国家级（Delta 42/50、JN.1 35/51、"
        "两季流感 32/38 与 39/45、两季 RSV 34/34 与 26/26），仅 Omicron 例外（25/51，与国家级 3.9 周不可区分）。"
        "须声明各州受共同季节与毒株驱动存在强空间相关、且国家级系各州之和，故该计数仅作方向性描述。"
        "机制上，州级斜率标准误显著高于国家级，宏观聚合的平滑效应抬高了视界；逐州复算显示宏观过程方差在"
        "工作点占主导（$\\text{CV}^2_{\\text{macro}}(h^*)/\\tau^2$ 跨州中位数 $0.73$--$0.89$），"
        "构成州级视界的核心约束。此外，RSV 2025--26 仅 26 州、流感 2022--23 仅 38 州满足数据门槛，"
        "直观印证了定理~\\ref{thm:fisher} 的数据充分性约束。\n\n"
    ) + t[i43b:]
    print("Section 4.3 long paragraph compressed.")

TEX.write_text(t, encoding="utf-8")
SUPP.write_text(s, encoding="utf-8")
print("final_trim done.")