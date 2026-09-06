"""Remove author + declarations, rename 2.2.1 in EN/CN tex files."""
import re
from pathlib import Path

CN = Path("paper_cn/main.tex")
EN = Path("paper_en/main.tex")

# ---- CN ----
cn = CN.read_text(encoding="utf-8")
# remove \author{匿名}
cn = re.sub(r"\\author\{[^}]*\}\n", "", cn, count=1)
# remove 声明 section: from \section*{声明} to \bibliographystyle
cn = re.sub(r"\\section\*\{声明\}.*?(?=\\bibliographystyle)", "", cn, flags=re.S)
# rename 2.2.1
cn = cn.replace(r"\subsubsection{与仓室模型的关系}",
                r"\subsubsection{与确定性仓室模型的关系}")
CN.write_text(cn, encoding="utf-8")
print("CN: author removed, declarations removed, 2.2.1 renamed")

# ---- EN ----
en = EN.read_text(encoding="utf-8")
en = re.sub(r"\\author\{[^}]*\}\n", "", en, count=1)
# remove Declarations + Acknowledgments: from \section*{Declarations} to \bibliographystyle
en = re.sub(r"\\section\*\{Declarations\}.*?(?=\\bibliographystyle)", "", en, flags=re.S)
en = en.replace(r"\subsubsection{Relation to compartmental models}",
                r"\subsubsection{Relation to deterministic compartmental models}")
EN.write_text(en, encoding="utf-8")
print("EN: author removed, declarations removed, 2.2.1 renamed")

# verify
for name, p in [("CN", CN), ("EN", EN)]:
    t = p.read_text(encoding="utf-8")
    print(f"{name}: author={'author' in t} declarations={'声明' in t or 'Declarations' in t} "
          f"comp={'与确定性仓室模型' in t or 'deterministic compartmental' in t}")
