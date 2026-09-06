# Predictability Boundary Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct Theorems 3 and 4, make the real-data pipeline unit-consistent and reproducible, regenerate manuscript tables/figures from one JSON source, and narrow unsupported claims.

**Architecture:** Keep the existing LaTeX manuscript and Python scripts, but introduce one shared calculation module for horizon units and error-budget components. Treat Theorem 3 as a truncated diffusion approximation unless an actual killed-process QSD solver is added; treat Theorem 4 as a fixed-parent-count information bound with the cumulative-case conversion stated separately.

**Tech Stack:** Python, NumPy, pandas, SciPy, Matplotlib/ existing figure scripts, LaTeX.

**Spec:** User request: “先修正定理 4 和定理 3，再统一真实数据计算流程；随后从同一 JSON 重新生成表格和图，最后收窄摘要与结论中的强断言。”

## Global Constraints

- Preserve existing user changes and submission-package layout.
- Use the same source JSON for manuscript tables and figures.
- Distinguish generation units from calendar weeks in names and labels.
- Do not describe approximate or misspecified comparisons as strict information-theoretic impossibility results.

---

### Task 1: Regression Tests for Theory and Pipeline

**Files:**
- Create: `final_submission_package/scripts/test_revision.py`

- [ ] Write tests for the corrected NB information conversion, generation-to-week conversion, and error-budget closure.
- [ ] Run tests and verify they fail against the current implementation/data.

### Task 2: Correct Theorems 3 and 4

**Files:**
- Modify: `final_submission_package/paper_cn/main.tex`
- Modify: `final_submission_package/paper_cn/main_final.tex`

- [ ] Replace the strict QSD claim with a clearly labeled truncated zero-current diffusion approximation and state its boundary/truncation limitations.
- [ ] State Theorem 4 for fixed parent count (n), then separately derive the cumulative-case approximation (C\approx nR), yielding (1+R/k) in the denominator.
- [ ] Remove unsupported claims about nuisance-(k) orthogonality unless a full information-matrix derivation is included.

### Task 3: Unify Real-Data Calculations

**Files:**
- Create: `final_submission_package/scripts/real_data_common.py`
- Modify: `final_submission_package/scripts/real_data.py`
- Modify: `final_submission_package/scripts/error_budget.py`
- Modify: `final_submission_package/scripts/make_figures.py`

- [ ] Use a single explicit `generation_to_week` conversion per pathogen.
- [ ] Store both `h_gen` and `h_week` in JSON; use one canonical horizon JSON for tables and figures.
- [ ] Compute budget components with consistent definitions and preserve signed residual/cross terms without clipping.

### Task 4: Regenerate Artifacts

**Files:**
- Modify: `final_submission_package/data_and_reports/real_data_horizons_with_ci.json`
- Modify: `final_submission_package/data_and_reports/real_data_illustration.json`
- Modify: `final_submission_package/data_and_reports/error_budget.json`
- Regenerate: `final_submission_package/reports/figures/*.png`

- [ ] Run the canonical scripts from the package root and verify all output JSON values use the same units.
- [ ] Regenerate figures and verify referenced files exist.
- [ ] Regenerate the LaTeX table rows from the canonical JSON or update them from the generated artifact.

### Task 5: Narrow Claims and Verify

**Files:**
- Modify: `final_submission_package/paper_cn/main.tex`
- Modify: `final_submission_package/paper_cn/main_final.tex`

- [ ] Narrow abstract and conclusion language to the corrected theorem scope and empirical support level.
- [ ] Run regression tests, reference checks, consistency audit, and a final diff/JSON consistency check.
