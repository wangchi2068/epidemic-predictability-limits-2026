"""Find unresolved \\ref in CN/EN and fix CN sec:data label."""

import re
from pathlib import Path

CN = Path("paper_cn/main.tex")
EN = Path("paper_en/main.tex")

for name, P in [("CN", CN), ("EN", EN)]:
    t = P.read_text(encoding="utf-8")
    refs = set(re.findall(r"\\ref\{([^}]*)\}", t))
    labels = set(re.findall(r"\\label\{([^}]*)\}", t))
    unresolved = sorted(refs - labels)
    print(f"{name}: refs={len(refs)} labels={len(labels)} unresolved={unresolved}")

# fix CN: add label to 数据 subsection
cn = CN.read_text(encoding="utf-8")
if r"\subsection{数据}" in cn and r"\label{sec:data}" not in cn:
    cn = cn.replace(r"\subsection{数据}", r"\subsection{数据}\label{sec:data}", 1)
    CN.write_text(cn, encoding="utf-8")
    print("CN: added \\label{sec:data} to 数据 subsection")
else:
    print("CN: no change needed")
