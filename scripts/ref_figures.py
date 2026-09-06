"""Add in-text references for previously unreferenced figures (OpenJudge B-caveat)."""

from pathlib import Path

EN = Path("paper_en/main.tex")
CN = Path("paper_cn/main.tex")

# ---- EN fig:framework: reference in Modeling framework subsubsection ----
en = EN.read_text(encoding="utf-8")
anchor = r"\subsubsection{Modeling framework}" + "\n\n"
insert = (
    anchor
    + r"Figure~\ref{fig:framework} summarizes the two sources of forecast error and their assembly into the horizon."
)
if "Figure~\\ref{fig:framework}" not in en:
    assert anchor in en, "Modeling framework anchor not found"
    en = en.replace(anchor, anchor + insert + "\n\n", 1)
EN.write_text(en, encoding="utf-8")
print("EN fig:framework referenced")

# ---- EN fig:real_horizons: reference in Illustrative horizons ----
en = EN.read_text(encoding="utf-8")
anchor2 = r"\subsubsection{Illustrative constant-$R$ horizons}" + "\n\n"
insert2 = (
    anchor2
    + r"Figure~\ref{fig:real_horizons} visualizes the horizons of Table~\ref{tab:horizons}."
)
if "Figure~\\ref{fig:real_horizons}" not in en:
    assert anchor2 in en, "Illustrative anchor not found"
    en = en.replace(anchor2, anchor2 + insert2 + "\n\n", 1)
EN.write_text(en, encoding="utf-8")
print("EN fig:real_horizons referenced")

# ---- CN fig:framework_cn: reference in 模型与假定 ----
cn = CN.read_text(encoding="utf-8")
anchor_cn = r"\subsection{模型与假定}" + "\n\n"
insert_cn = (
    anchor_cn + r"图~\ref{fig:framework_cn}概括两类预报误差来源及其组装为视界的过程。"
)
if "图~\\ref{fig:framework_cn}" not in cn:
    assert anchor_cn in cn, "CN model anchor not found"
    cn = cn.replace(anchor_cn, anchor_cn + insert_cn + "\n\n", 1)
CN.write_text(cn, encoding="utf-8")
print("CN fig:framework_cn referenced")
