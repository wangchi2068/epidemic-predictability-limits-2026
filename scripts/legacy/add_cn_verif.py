"""Add CN Results '验证总结' subsection for EN/CN parity (OpenJudge C.1)."""

from pathlib import Path

CN = Path("paper_cn/main.tex")
cn = CN.read_text(encoding="utf-8")

summary_lines = [
    "\\section{结果}",
    "\\subsection{验证总结}",
    "",
    "所有定理与模拟达到紧致或数量级一致：",
    "\\begin{itemize}",
    "\\item \\textbf{T1:} 人口项CV比值(经验/理论)0.995--1.001；全分解比值0.99--1.03，跨越全部$(R, k, I_0, \\delta R)$格与视界。",
    "\\item \\textbf{T2:} 单调性在全部64个参数配置中得到确认。",
    "\\item \\textbf{T3(a):} 平稳CV比值在$(\\varepsilon,R,N)\\in\\{(0.2,1.2,2000),(0.4,1.4,2000)\\}$处为0.998与0.999；$x_{\\min}\\in\\{0.05,0.1,0.2,0.5\\}$变化时理论CV变化小于$1.1\\times10^{-9}\\%$。",
    "\\item \\textbf{T3(b):} $2\\varepsilon/R$近似在八个有限阈值格中的七个落入95\\% Beta后验区间；唯一例外为$(N,\\varepsilon)=(500,0.02)$，经验概率0.0775(0.0552--0.1079)对比近似值0.0392。",
    "\\item \\textbf{T4:} MLE方差/CRB比值范围0.57--1.81；中位1.02(数量级一致，如定理所述)。",
    "\\item \\textbf{T5:} 独立log-$R$创新给出全比值0.86--1.44；限制$h \\geq 2$、$v \\leq 0.05$后收窄至0.93--1.05。",
    "\\item \\textbf{T5R:} AR(1)持久性$\\phi \\in \\{0, 0.5, 0.8, 0.95\\}$与$h \\in \\{1, 2, 4, 8\\}$给出比值0.58--1.10。",
    "\\item \\textbf{种群级$1/k$地板:} 比值0.98--1.03。",
    "\\end{itemize}",
    "",
    "所有数值结果以JSON格式存档，含随机种子、numpy/scipy版本与运行时长元数据，便于复现审计。",
    "",
]

# locate "\section{结果}\n\n\n\subsection{LightGBM"
anchor = "\\section{结果}\n\n\n\\subsection{LightGBM：界紧致性}"
assert anchor in cn, "anchor not found"
summary = "\n".join(summary_lines)
cn = cn.replace(anchor, summary + "\n\n\\subsection{LightGBM：界紧致性}")
CN.write_text(cn, encoding="utf-8")
print("CN verification summary added")
