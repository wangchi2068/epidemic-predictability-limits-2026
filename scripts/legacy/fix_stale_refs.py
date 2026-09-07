"""Fix stale hardcoded cross-references found by OpenJudge review (A2-A6)."""

from pathlib import Path

EN = Path("paper_en/main.tex")
CN = Path("paper_cn/main.tex")

# ---- A3: EN "Equation (1) thus" -> "\ref{eq:cv2}" ----
en = EN.read_text(encoding="utf-8")
en = en.replace(
    r"Equation (1) thus extends continuously to $R = 1$",
    r"Equation~\\ref{eq:cv2} thus extends continuously to $R = 1$",
)
EN.write_text(en, encoding="utf-8")
print("A3 EN fixed")

# ---- A4/A5: CN "第~6节" -> \ref{sec:data} (two occurrences) ----
cn = CN.read_text(encoding="utf-8")
# A4: 本文第~6节 -> 本文第~\\ref{sec:data}节 (real-data verification)
cn = cn.replace("（本文第~6节）", "（本文第~\\ref{sec:data}节）")
cn = cn.replace("(本文第~6节)", "(本文第~\\ref{sec:data}节)")
# A5: 第~6节的真实数据误差预算 -> 第~\\ref{sec:data}节
cn = cn.replace("第~6节的真实数据误差预算", "第~\\ref{sec:data}节的真实数据误差预算")
CN.write_text(cn, encoding="utf-8")
print("A4/A5 CN fixed")

# ---- A6: CN "第4.3节" (population floor) -> \ref{eq:pop_floor} ----
cn = CN.read_text(encoding="utf-8")
cn = cn.replace("（第4.3节）", "（\\ref{eq:pop_floor}）")
cn = cn.replace("(第4.3节)", "(\\ref{eq:pop_floor})")
cn = cn.replace("第4.3节", "\\ref{eq:pop_floor}")
CN.write_text(cn, encoding="utf-8")
print("A6 CN fixed")

# ---- A2: EN "verification summary in Section 5" (if present) ----
en = EN.read_text(encoding="utf-8")
en = en.replace(
    "the verification summary in Section 5",
    "the verification summary in Section~\\ref{sec:simulation}",
)
en = en.replace(
    "verification summary in Section 5",
    "verification summary in Section~\\ref{sec:simulation}",
)
EN.write_text(en, encoding="utf-8")
print("A2 EN fixed")
