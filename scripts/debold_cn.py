"""Remove over-bolded fragments in paper_cn/main.tex (string-safe version)."""
from pathlib import Path

P = Path("paper_cn/main.tex")
t = P.read_text(encoding="utf-8")

# 1) "以\\textbf{周}为单位" -> "以周为单位"
t = t.replace(r"以\textbf{周}为单位", "以周为单位")

# 2) long bolded ML-1 horizon-ratio sentence -> plain text (split into pieces)
old = r"\textbf{中位视界比值(神经/理论地板)：6.69；(MLE/地板)：1.23，"
old += "其中"
old += "\u201c视界比值\u201d定义为估计器达到目标精度$\\tau$所需视界的估计值与理论地板$h^*$之比"
old += "（比值越大离地板越远）}"
new = "中位视界比值(神经/理论地板)：6.69；(MLE/地板)：1.23，"
new += "其中"
new += "\u201c视界比值\u201d定义为估计器达到目标精度$\\tau$所需视界的估计值与理论地板$h^*$之比"
new += "（比值越大离地板越远）"
t = t.replace(old, new)

# 3) contrast bold -> plain
t = t.replace(r"\textbf{有限样本下有偏MLE的经验方差}", "有限样本下有偏MLE的经验方差")
t = t.replace(r"\textbf{渐近Cramér-Rao理论下界}", "渐近Cramér-Rao理论下界")

P.write_text(t, encoding="utf-8")
print("de-bolded")
