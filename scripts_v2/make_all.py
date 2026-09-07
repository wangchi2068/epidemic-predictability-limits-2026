# -*- coding: utf-8 -*-
"""make_all.py — One-command build: data -> params -> tables/figures -> consistency.

Run:  python scripts_v2/make_all.py [--fast]
(--fast skips the theorem Monte-Carlo suite; use for quick table refreshes.)
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

STEPS = [
    ("pipeline.py", "参数估计 + Bootstrap CI"),
    ("rolling_eval_v2.py", "滚动评估 (Table 5 / Fig 7)"),
    ("error_budget_v2.py", "四项误差记账 (Table 4 / Fig 6)"),
    ("verify_suite.py", "定理 5R + 推论 1 验证"),
    ("make_all_figures_v2.py", "全部图件"),
    ("make_tables_v2.py", "LaTeX 表体"),
    ("check_consistency.py", "一致性测试"),
]

def main():
    fast = "--fast" in sys.argv
    for script, desc in STEPS:
        if fast and script == "verify_suite.py":
            print(f"[skip] {script} (--fast)")
            continue
        print(f"\n=== {script} — {desc} ===", flush=True)
        r = subprocess.run([sys.executable, str(HERE / script)])
        if r.returncode != 0:
            print(f"FAILED: {script}", file=sys.stderr)
            sys.exit(r.returncode)
    print("\nAll build steps completed.", flush=True)

if __name__ == "__main__":
    main()
