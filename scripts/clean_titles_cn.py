"""Clean up redundant subsection titles in paper_cn/main.tex (mirror of EN)."""

import re
from pathlib import Path

P = Path("paper_cn/main.tex")
t = P.read_text(encoding="utf-8")

# 1) 数据: remove nested subsubsection if present; ensure label on subsection
# CN currently: \subsection{数据} ... (no nested subsubsection{数据} seen)
# 2) drop 引理/定理 subsubsection headers
patterns = [
    r"\\subsubsection\{引理1 \(Galton-Watson二阶矩\)\}\n\n",
    r"\\subsubsection\{引理2 \(人口地板，有限视界\)\}\n\n",
    r"\\subsubsection\{引理3 \(参数放大，精确\)\}\n\n",
    r"\\subsubsection\{定理1 \(误差分解与视界\)\}\n\n",
    r"\\subsubsection\{定理2 \(有限视界精度边界\)\}\n\n",
    r"\\subsubsection\{定理3 \(近临界有限种群窗口\)\}\n\n",
    r"\\subsubsection\{定理4 \(辨识极限；似然特定\)\}\n\n",
    r"\\subsubsection\{定理5 \(时变\$R\$，独立同分布\)\}\n\n",
    r"\\subsubsection\{定理5R \(增长率持久性：状态污染\)\}\n\n",
    r"\\subsubsection\{种群级噪声地板\}\n\n",
]
for pat in patterns:
    t = re.sub(pat, "", t)

P.write_text(t, encoding="utf-8")
print("CN titles cleaned")
