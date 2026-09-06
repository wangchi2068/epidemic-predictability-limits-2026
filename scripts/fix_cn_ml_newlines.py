"""Fix literal '\\n\\n' sequences in paper_cn/main.tex ML subsection headers."""

from pathlib import Path

P = Path("paper_cn/main.tex")
t = P.read_text(encoding="utf-8")
# replace the literal backslash-n pairs with real newlines
t = t.replace(
    r"\subsection{LightGBM：界紧致性}\label{sec:ml}\n\n\textbf{ML-2(紧致性)：}",
    "\\subsection{LightGBM：界紧致性}\\label{sec:ml}\n\n\\textbf{ML-2(紧致性)：}",
)
t = t.replace(
    r"\subsection{神经网络(MLP)：辨识地板检验}\n\n\textbf{ML-1(辨识地板检验)：}",
    "\\subsection{神经网络(MLP)：辨识地板检验}\n\n\\textbf{ML-1(辨识地板检验)：}",
)
P.write_text(t, encoding="utf-8")
print("repaired")
