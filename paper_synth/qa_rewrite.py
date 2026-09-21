# -*- coding: utf-8 -*-
"""QA for paper_synth: confirm every rewrite landed in the compiled PDF.

ASCII-only console output so GBK terminals cannot mangle the report.
"""
import re
import sys

import fitz

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")

d = fitz.open("paper_synth/main.pdf")
full = "".join(p.get_text() for p in d)
norm = re.sub(r"\s+", " ", full)

CHECKS = [
    ("new title", "位置失效先于离", 1),
    ("abstract: location-led", "位置偏差", 1),
    ("abstract: share-under", "91.7", 1),
    ("contrib: new core finding", "失效来源判别层面", 1),
    ("hierarchy: distributional", "分布性而非逐点成立", 1),
    ("sec5.2(3): decomposition", "宽度分解诊断", 1),
    ("sec5.2(3): best-c95 numbers", "0.872", 1),
    ("table10 label", "失效的位置", 1),
    ("limitations: seven", "七个方面", 1),
    ("limitations: no envelope claim", "不将机制视界表述为外包络", 1),
    ("conclusion: five findings", "可核对的主要结论有五", 1),
    ("conclusion: new finding", "峰前校准失效以位置偏差为主导", 1),
    ("conclusion: held-out ask", "样本外", 1),
]

RETIRED = [
    "宽松经验参考外包络",
    "峰前期额外击穿与静态方差设定偏误不可分离",
    "Abstract",
    "Keywords",
]

fails = 0
for label, needle, need in CHECKS:
    hits = norm.count(needle)
    ok = hits >= need
    if not ok:
        fails += 1
    print(f"[{'OK ' if ok else 'MISS'}] {label:34s} hits={hits}")

for needle in RETIRED:
    hits = norm.count(needle)
    ok = hits == 0
    if not ok:
        fails += 1
    print(f"[{'OK ' if ok else 'MISS'}] retired x{hits}")

print()
print("pages:", len(d), "| '??':", full.count("??"))
if full.count("??"):
    fails += 1
print("RESULT:", "PASS" if fails == 0 else f"FAIL({fails})")
