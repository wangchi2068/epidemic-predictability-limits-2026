"""Clean up redundant subsection titles in paper_en/main.tex.

1) 2.1 Data: remove the nested \\subsubsection{Data}; move \\label{sec:data} up.
2) Remove all \\subsubsection{Theorem ...} / \\subsubsection{Lemma ...} headers
   (theorem environments carry their own numbering; the extra level is redundant).
"""

import re
from pathlib import Path

P = Path("paper_en/main.tex")
t = P.read_text(encoding="utf-8")

# 1) Data / Data duplication
t = t.replace(
    r"\subsection{Data}" + "\n",
    r"\subsection{Data}\label{sec:data}" + "\n",
)
t = re.sub(r"\\subsubsection\{Data\}\\label\{sec:data\}" + r"\n\n", "", t)

# 2) drop theorem/lemma subsubsection headers (keep the blank line)
patterns = [
    r"\\subsubsection\{Lemma 1: Branching-process moments\}\n\n",
    r"\\subsubsection\{Lemma 2: Parameter amplification\}\n\n",
    r"\\subsubsection\{Theorem 1: Error decomposition and horizon\}\n\n",
    r"\\subsubsection\{Theorem 2: Finite-horizon accuracy boundary\}\n\n",
    r"\\subsubsection\{Theorem 3: Near-critical finite-population window\}\n\n",
    r"\\subsubsection\{Theorem 4: Fisher information bound \(likelihood-specific\)\}\n\n",
    r"\\subsubsection\{Theorem 5: Time-varying \$R\$ with independent innovations\}\n\n",
    r"\\subsubsection\{Theorem 5R: Persistent growth-rate drift \(AR\(1\) extension\)\}\n\n",
    r"\\subsubsection\{Population-level noise floor\}\n\n",
]
for pat in patterns:
    t = re.sub(pat, "", t)

# also drop the standalone subsubsection Simulation design? keep it (has label)
P.write_text(t, encoding="utf-8")
print("EN titles cleaned")
