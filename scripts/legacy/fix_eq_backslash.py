"""Fix equation blocks that have backslash-letter directly after \\begin{equation}.

The bug: '\\begin{equation}\\h_{...' should be '\\begin{equation} h_{...'
(i.e., a space between the environment opener and the formula content).
"""

import re
from pathlib import Path

P = Path("paper_cn/main.tex")
t = P.read_text(encoding="utf-8")

# pattern: \begin{equation}\X  (backslash + letter right after opener) -> \begin{equation} \X
fixed = re.sub(r"\\begin\{equation\}(\\[a-zA-Z])", r"\\begin{equation} \\\1", t)
P.write_text(fixed, encoding="utf-8")
print("fixed backslash-letter after begin{equation}")

# verify no more
t2 = P.read_text(encoding="utf-8")
bad = re.findall(r"\\begin\{equation\}(\\[a-zA-Z])", t2)
print("remaining:", bad[:5] if bad else "none")
