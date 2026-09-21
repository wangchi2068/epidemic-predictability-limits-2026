# -*- coding: utf-8 -*-
"""Round-3 review checks: closure of labels/refs/citations, theorem envs, overclaims."""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
BS = chr(92)
S = io.open("paper_journal/main.tex", encoding="utf-8").read()

print("=== A. labels never referenced ===")
labels = set(re.findall(re.escape(BS) + r"label\{([^}]+)\}", S))
refs = set(re.findall(re.escape(BS) + r"ref\{([^}]+)\}", S))
print("labels:", len(labels), "| never referenced:", sorted(labels - refs))

print("\n=== B. eq labels never eqref'd ===")
eqs = set(re.findall(re.escape(BS) + r"label\{(eq:[^}]+)\}", S))
eqr = set(re.findall(re.escape(BS) + r"eqref\{([^}]+)\}", S))
print(sorted(eqs - eqr))

print("\n=== C. theorem environments ===")
for env in ("theorem", "lemma", "assumption", "remark"):
    print("  ", env, len(re.findall(re.escape(BS) + r"begin\{" + env + r"\}", S)))

print("\n=== D. citation closure ===")
allk = set()
for k in re.findall(re.escape(BS) + r"cite[a-z]*\{([^}]+)\}", S):
    for x in k.split(","):
        allk.add(x.strip())
bib = io.open("paper_journal/references.bib", encoding="utf-8").read()
bibkeys = set(re.findall(r"@\w+\{([^,]+),", bib))
print("cited:", len(allk), " bib:", len(bibkeys))
print("cited but not in bib:", sorted(allk - bibkeys))
print("in bib but uncited:", sorted(bibkeys - allk))

print("\n=== E. claims that need a locatable test ===")
for m in re.finditer("统计显著", S):
    seg = S[max(0, m.start() - 90):m.start() + 90].replace("\n", " ")
    print("   *", seg)

print("\n=== F. 外包络 / 参考外包络 phrasing consistency ===")
for w in ("宽松经验参考外包络", "外包络", "绝对理论上限"):
    print(f"  {w}: {S.count(w)}")

print("\n=== G. page/table/figure inventory from PDF ===")
import fitz

d = fitz.open("paper_journal/main.pdf")
txt = "".join(p.get_text() for p in d)
print("  pages:", len(d))
for i, p in enumerate(d, 1):
    t = p.get_text()
    tabs = re.findall(r"表\s?(\d+)", t)
    figs = re.findall(r"图\s?(\d+)", t)
    if tabs or figs:
        print(f"  p{i}: tables={sorted(set(tabs))} figures={sorted(set(figs))}")
