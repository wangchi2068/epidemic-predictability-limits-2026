"""Remove duplicated \\subsection{模型与假定} in paper_cn/main.tex."""

from pathlib import Path

CN = Path("paper_cn/main.tex")
cn = CN.read_text(encoding="utf-8")
dup = "\\subsection{模型与假定}\n\n\\subsection{模型与假定}\n\n"
assert dup in cn, "duplicate not found"
cn = cn.replace(dup, "\\subsection{模型与假定}\n\n", 1)
CN.write_text(cn, encoding="utf-8")
print("deduped")
