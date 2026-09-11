# -*- coding: utf-8 -*-
"""make_all.py — one-command build: data integrity -> empirical pipeline ->
figures -> theorem simulations -> consistency suite.

Run:  python scripts_v2/make_all.py [--fast]
(--fast skips the theorem Monte-Carlo suites; use for quick table refreshes.)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

STEPS = [
    ("ingest_and_aggregate.py", "数据溯源与完整性校验"),
    ("state_panel_v3.py", "州级面板：参数估计 + 视界 + 滚动回测"),
    ("emit_v3.py", "四项误差记账 + LaTeX 表体"),
    ("make_figures_v3.py", "实证图件"),
    ("sim_verify_t1.py", "定理 1/2 数值验证"),
    ("sim_verify_t4.py", "定理 4 Cram\'er--Rao 下界验证"),
    ("verify_suite.py", "定理 5R + 推论 1 验证"),
    ("sim_verify_t3.py", "定理 3 拟平稳 + 定殖概率验证"),
    ("make_all_figures_v2.py", "第 3 节图件"),
    ("sensitivity_v4.py", "视界方程敏感性（k_agg 窗口/截断、个体 k、周代求根）"),
    ("rolling_bootstrap.py", "滚动穿越点原点级自助"),
    ("coarsegrain_check.py", "个体 k → 宏观 k_agg 粗粒化核验"),
    ("macro_cv_check.py", "宏观固定 k_agg 模型方差律核验"),
    ("check_consistency.py", "一致性测试（九类断言）"),
]


def main():
    fast = "--fast" in sys.argv
    for script, desc in STEPS:
        if fast and script in ("verify_suite.py", "sim_verify_t3.py", "sim_verify_t4.py"):
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
