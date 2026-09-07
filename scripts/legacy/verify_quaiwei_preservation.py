"""Verify the qu-ai-wei rewrite of paper_cn/main.tex preserved all facts.
Compares numbers, \\citep citations, and key formulas against the backup."""

import re
import sys
from pathlib import Path

ROOT = Path("D:/trae/epidemic_predictability_paper_2026_final")
old = (ROOT / "paper_cn/main.tex.bak_quaiwei").read_text(encoding="utf-8")
new = (ROOT / "paper_cn/main.tex").read_text(encoding="utf-8")

failures = 0


def check(label, ok, detail=""):
    global failures
    if not ok:
        failures += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {label} {detail}")


# 1) citations
citep_old = set(re.findall(r"\\citep\{[^}]*\}", old))
citep_new = set(re.findall(r"\\citep\{[^}]*\}", new))
check(
    "citep preserved",
    citep_old == citep_new,
    f"lost={sorted(citep_old - citep_new)[:5]} added={sorted(citep_new - citep_old)[:5]}",
)

# 2) numeric tokens (with surrounding context to avoid false matches)
num_pat = re.compile(
    r"(?<![A-Za-z0-9_\\\\])(?:"
    r"\d+\.\d+(?:--\d+\.\d+)?%?"
    r"|\d+(?:--\d+)?%?"
    r"|1\.1\\times10\^\{?-9\}?%?"
    r"|N\^\{1/2\}"
    r"|N\^\{0\.51\}"
    r")(?![A-Za-z0-9_\\\\])"
)
n_old = sorted(set(num_pat.findall(old)))
n_new = sorted(set(num_pat.findall(new)))
lost = set(n_old) - set(n_new)
added = set(n_new) - set(n_old)
check(
    "numbers preserved",
    not lost and not added,
    f"lost={sorted(lost)[:8]} added={sorted(added)[:8]}",
)

# 3) key formulas / symbols that must survive
formulas = [
    r"2\varepsilon/R",
    r"c_1 = \frac{2\varepsilon}{R+1}",
    r"c_2 = \frac{R}{N(R+1)}",
    r"\sqrt{(R+1)X}",
    r"\frac{(1 + R/k)(1 - R^{-h})}{I_0(R - 1)}",
    r"\frac{1+R/k}{I_0(R-1)}",
    r"P(h; R, \delta R)",
    r"h^* \approx \mu_g",
    r"\frac{1/R + 1/k}{C}",
    r"\gamma_0 \left[ h + 2 \sum",
    r"s_e^2 h^3/3",
    r"\text{Var}(\log \hat{I}_h)",
    r"\frac{h}{k}",
    r"\pi(x) \propto x^{-1}",
    r"q = e^{-R(1-q)}",
    r"2\text{Cov}(Z_h, I_0\hat{R}^h)",
    r"\text{CV}^2(h) = \frac{\text{Var}(Z_h)}{\mathbb{E}[Z_h]^2}",
]
for f in formulas:
    check(f"formula: {f[:40]}...", f in new)

# 4) theorem/lemma headers and section structure preserved
for sec in [
    r"\\section\{引言\}",
    r"\\section\{模型与记号\}",
    r"\\section\{结果\}",
    r"\\section\{模拟验证\}",
    r"\\section\{机器学习角色\}",
    r"\\section\{真实数据示例\}",
    r"\\section\{讨论\}",
    r"\\section\{结论\}",
    r"\\subsection\{引理1",
    r"\\subsection\{引理2",
    r"\\subsection\{引理3",
    r"\\subsection\{定理1",
    r"\\subsection\{定理2",
    r"\\subsection\{定理3",
    r"\\subsection\{定理4",
    r"\\subsection\{定理5",
    r"\\subsection\{定理5R",
    r"\\subsection\{种群级噪声地板\}",
]:
    check(f"structure: {sec}", re.search(sec, new) is not None)

# 5) table data rows preserved
for row in [
    "1.31 & 0.028 & 23 [15, 53]",
    "1.16 & 0.076 & 7.6 [0, 19]",
    "1.05 & 0.056 & 9.4 [0, 22]",
    "1.24 & 0.015 & 43 [27, 99]",
    "1.21 & 0.009 & 68 [43, 169]",
    "1.41 & 0.056 & 13 [8, 31]",
    "1.40 & 0.039 & 18 [11, 43]",
]:
    check(f"table row: {row}", row in new)

# 6) all ratio ranges that must survive verbatim
for rng in [
    "0.995--1.001",
    "0.99--1.03",
    "0.57--1.81",
    "0.86--1.44",
    "0.93--1.05",
    "0.58--1.10",
    "0.66--1.10",
    "0.98--1.03",
    "2.1--9.1",
    "3.1--6.8",
    "4.1--9.1",
    "2.1--4.9",
    "42--69",
    "15--33",
    "6--39",
    "9.7\\%",
    "7.6\\%",
    "82.8\\%",
    "9.0\\%",
    "7.0\\%",
    "84.0\\%",
    "86\\%",
    "6--44\\%",
    "0.0775",
    "0.0552--0.1079",
    "0.0392",
    "0.176",
    "0.182",
    "0.165",
    "1.032",
    "0.938",
    "6.69",
    "1.23",
    "5.4",
    "6.2",
    "0.901",
    "0.3\\%",
    "1.13",
    "1.00",
    "0.48",
    "0.5",
    "0.8",
    "0.132",
    "0.998",
    "0.999",
]:
    check(f"ratio/number: {rng}", rng in new)

print(
    f"\n=== VERIFY COMPLETE: {'ALL PASS' if failures == 0 else str(failures) + ' FAILURE(S)'} ==="
)
sys.exit(1 if failures else 0)
