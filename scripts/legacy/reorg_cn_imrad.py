"""IMRaD reorganization for paper_cn/main.tex (3-lemma structure).

Mapping:
  Intro (35-60) keep
  Methods: Data (from 真实数据示例 head), Model (模型与记号 61-104),
           Error decomposition (引理1-3 + 定理1-2), Near-critical (定理3),
           Identification (定理4), Time-varying (定理5/5R+1k), Simulation design (模拟验证)
  Results: Verification summary (模拟配置), LightGBM + MLP (机器学习角色 renamed),
           Real-data application (真实数据示例)
  Discussion (332-355, split Limitations out), Limitations, Conclusion (356-375)
"""

from pathlib import Path

P = Path("paper_cn/main.tex")
lines = P.read_text(encoding="utf-8").split("\n")


def block(a, b):
    return "\n".join(lines[a - 1 : b])


def dedup(t):
    out, prev = [], None
    for ln in t.split("\n"):
        if ln == prev and ln.startswith(
            ("\\section", "\\subsection", "\\subsubsection")
        ):
            continue
        out.append(ln)
        prev = ln
    return "\n".join(out)


preamble = block(1, 34)  # up to \begin{document} + \maketitle + abstract
intro = block(35, 60)  # 引言 + 相关工作

# 模型与记号 61-104
model = block(61, 104)
model = model.replace("\\section{模型与记号}", "\\subsection{模型与假定}")
model = model.replace(
    "\\subsection{与仓室模型的关系}", "\\subsubsection{与仓室模型的关系}"
)

# 结果 105-271: 引理1-3 + 定理1-2 (105-185) / 定理3 (186-210) / 定理4 (211-238) / 定理5-1k (239-271)
res = block(105, 271)
res = res.replace("\\section{结果}", "\\subsection{误差分解与视界}")
res = res.replace(
    "\\subsection{引理1 (Galton-Watson二阶矩)}",
    "\\subsubsection{引理1 (Galton-Watson二阶矩)}",
)
res = res.replace(
    "\\subsection{引理2 (人口地板，有限视界)}",
    "\\subsubsection{引理2 (人口地板，有限视界)}",
)
res = res.replace(
    "\\subsection{引理3 (参数放大，精确)}", "\\subsubsection{引理3 (参数放大，精确)}"
)
res = res.replace(
    "\\subsection{定理1 (误差分解与视界)}", "\\subsubsection{定理1 (误差分解与视界)}"
)
res = res.replace(
    "\\subsection{定理2 (有限视界精度边界)}",
    "\\subsubsection{定理2 (有限视界精度边界)}",
)
i3 = res.find("\\subsection{定理3 (近临界有限种群窗口)}")
part1 = res[:i3]
rest = res[i3:]
i4 = rest.find("\\subsection{定理4 (辨识极限；似然特定)}")
nearcrit = rest[:i4].replace(
    "\\subsection{定理3 (近临界有限种群窗口)}",
    "\\subsubsection{定理3 (近临界有限种群窗口)}",
)
rest2 = rest[i4:]
i5 = rest2.find("\\subsection{定理5 (时变$R$，独立同分布)}")
ident = rest2[:i5].replace(
    "\\subsection{定理4 (辨识极限；似然特定)}",
    "\\subsubsection{定理4 (辨识极限；似然特定)}",
)
timevar = rest2[i5:]
timevar = timevar.replace(
    "\\subsection{定理5 (时变$R$，独立同分布)}",
    "\\subsubsection{定理5 (时变$R$，独立同分布)}",
)
timevar = timevar.replace(
    "\\subsection{定理5R (增长率持久性：状态污染)}",
    "\\subsubsection{定理5R (增长率持久性：状态污染)}",
)
timevar = timevar.replace(
    "\\subsection{种群级噪声地板}", "\\subsubsection{种群级噪声地板}"
)

# 模拟验证 272-277 -> Methods 2.7 (Simulation design)
sim = block(272, 277)
sim = sim.replace(
    "\\section{模拟验证}\\label{sec:simulation}",
    "\\subsubsection{模拟设计}\\label{sec:simulation}",
)

# 机器学习角色 278-283 -> Results (algorithm names)
ml = block(278, 283)
ml = ml.replace("\\section{机器学习角色}\\label{sec:ml}", "")
ml = ml.replace(
    "\\textbf{ML-2(紧致性)：}",
    "\\subsection{LightGBM：界紧致性}\\label{sec:ml}\\textbf{ML-2(紧致性)：}",
)
ml = ml.replace(
    "\\textbf{ML-1(辨识地板检验)：}",
    "\\subsection{神经网络(MLP)：辨识地板检验}\\textbf{ML-1(辨识地板检验)：}",
)

# 真实数据 284-331 -> Methods 2.1 (data head) + Results (application)
rd = block(284, 331)
i_table = rd.find("\\begin{table}[ht]")
data_head = rd[:i_table]
data_head = data_head.replace("\\section{真实数据示例}", "")
app_body = rd[i_table:]
app_body = app_body.replace(
    "\\begin{table}[ht]", "\\subsubsection{示意性恒定$R$视界}\\begin{table}[ht]"
)

# 讨论 332-355: split Limitations (352-355)
disc = block(332, 355)
i_lim = disc.find("\\subsection{局限性}")
disc_main = disc[:i_lim]
lim_body = disc[i_lim:].replace("\\subsection{局限性}", "")
# within disc_main, keep subsections as-is (they are Discussion subsections)
disc_main = disc_main.replace(
    "\\subsection{预报中心的实践含义}", "\\subsection{预报中心的实践含义}"
)
disc_main = disc_main.replace(
    "\\subsection{与临界相变和信息论极限的联系}",
    "\\subsection{与临界相变和信息论极限的联系}",
)

# 结论 + tail 356-375
conc = block(356, 375)

out = [
    preamble,
    "",
    "\\section{引言}",
    intro,
    "",
    "\\section{方法}",
    "\\subsection{数据}",
    data_head,
    "",
    "\\subsection{模型与假定}",
    model,
    "",
    "\\subsection{误差分解与视界}",
    part1,
    "",
    "\\subsection{近临界窗口}",
    nearcrit,
    "",
    "\\subsection{辨识极限}",
    ident,
    "",
    "\\subsection{时变情形与种群级地板}",
    timevar,
    "",
    "\\subsubsection{模拟设计}\\label{sec:simulation}",
    sim,
    "",
    "\\section{结果}",
    ml,
    "",
    "\\subsection{真实数据应用}",
    app_body,
    "",
    "\\section{讨论}",
    disc_main,
    "",
    "\\section{局限性}",
    lim_body,
    "",
    "\\section{结论}",
    conc,
]
final = dedup("\n".join(out))
P.write_text(final, encoding="utf-8")
print("CN reorganized, lines:", len(final.split("\n")))
