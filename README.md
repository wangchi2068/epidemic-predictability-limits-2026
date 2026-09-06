# Epidemic Predictability Limits & Horizons (2026 Final Replication Package)
# 《传染病传播动力学的可预测视界、理论极限与实证研究》开源复现代码与数据仓库

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Reproduction: 100% Verified](https://img.shields.io/badge/Replication-100%25%20Verified-brightgreen.svg)]()

This repository provides the complete replication package, numerical solvers, empirical datasets, and publication artifacts for the paper:
**"Predictability Horizons, Fundamental Limits, and Empirical Analysis of Epidemic Transmission Dynamics"**
**《传染病传播动力学的可预测视界、理论极限与实证研究》**

---

## 📌 Executive Summary (研究核心摘要)

Prospective forecasting of major infectious diseases frequently suffers from severe skill degradation near epidemic thresholds. Grounded in first-principles negative binomial branching processes $\text{NB}(R, k)$, this study derives a rigorous additive decomposition of prospective relative mean squared error:

$$\text{relMSE}^2(h) = \underbrace{\text{CV}^2(h)}_{\text{Demographic Stochastic Floor}} + \underbrace{P(h)}_{\text{Parameter Amplification}} \le \tau^2$$

Key analytical and empirical findings:
1. **Analytical Predictability Horizon ($h^*$)**: Closed-form leading-order ceiling and exact numerical roots via 40-node Gauss-Hermite integration over non-negative truncated normal parameter estimates.
2. **Phase Comparison**: Theoretical predictability horizons span **2.9–13.5 weeks** during early exponential growth phases, significantly contract to **7.8 weeks** (Delta) during peak plateau phases, and undergo a dynamical regime shift toward micro-extinction and absorption during subcritical decline phases ($R < 1$).
3. **Four-Term Error Accounting**: Short-term ($h = 1\text{--}2$ weeks) variance is dominated by unmodeled structural residuals ($72.6\%\text{--}94.2\%$, up to $95.4\%$ across horizons), whereas parameter extrapolation error rapidly dominates over longer horizons (explaining up to $88.7\%$ in seasonal influenza).
4. **Two-Tier Framework**: Reconciles the gap between theoretical mechanistic capacity limits ($h^*$) and operational forecast skill degradation (relative to persistence baselines, collapsing within $1\text{--}4$ weeks).

---

## 📁 Repository Structure (仓库目录结构)

```
epidemic-predictability-limits-2026/
├── README.md                      # Complete project guide and replication instructions
├── Response_to_Reviewers.md       # Full point-by-point response to peer review (Round 9)
├── environment.yml                # Conda environment definition
├── references.bib                 # Clean BibTeX database (all cited keys resolved)
├── scripts/                       # Reproduction scripts and numerical algorithms
│   ├── reproduce_all_tables_round9.py  # One-click reproduction of Tables 2, 3, 4, 5, 6
│   ├── consistency_audit.py            # End-to-end consistency verification (32/32 Pass)
│   ├── sim_verify_t1.py                # Theorem 1 orthogonal error decomposition
│   ├── sim_verify_t3.py                # Theorem 3 near-critical quasi-stationary scaling
│   ├── sim_verify_t4.py                # Theorem 4 Cramér-Rao Fisher information bound
│   ├── verify_t5R.py                   # Theorem 5/5R AR(1) and random-walk variance
│   ├── ml1_mdn.py                      # Shallow MLP neural network benchmark
│   ├── ml2_forecaster.py               # LightGBM tree forecaster benchmark
│   ├── real_data.py                    # CDC respiratory disease empirical analysis
│   └── make_figures.py                 # Manuscript figures generation script
├── paper_cn_journal_template/     # Chinese journal template manuscript (TeX, PDF, Word docx)
│   ├── main.tex                   # LaTeX source (39 pages)
│   ├── main.pdf                   # Compiled PDF (39 pages, 0 broken refs, publication-ready)
│   ├── references.bib             # References
│   └── 流行病传播动力学的可预测视界、极限机制与实证研究_期刊模版版.docx # Word version
├── paper_cn/                      # Standard Chinese manuscript package
├── paper_en/                      # English manuscript package
├── data_and_reports/              # Sanitized CDC surveillance series and JSON reports
├── figures/                       # High-resolution vector & raster figures (Figs 1-7)
└── derivations/                   # Formal mathematical derivation logs and notebooks
```

---

## 🚀 Quick Reproduction (快速一键复现)

### 1. Clone the Repository
```bash
git clone https://github.com/wangchi2068/epidemic-predictability-limits-2026.git
cd epidemic-predictability-limits-2026
```

### 2. Environment Setup
```bash
# Using Conda
conda env create -f environment.yml
conda activate epidemic_limits

# Or using pip
pip install numpy scipy pandas matplotlib lightgbm pypdf python-docx
```

### 3. One-Click Table Verification (< 5 seconds)
To reproduce **Table 2** (Empirical horizons), **Table 3** (Three-phase comparison with Delta 7.8w), and **Table 6** (Decision mapping matrix):
```bash
python scripts/reproduce_all_tables_round9.py
```

### 4. Run Full Consistency Audit (端到端全量自检)
```bash
python scripts/consistency_audit.py
```
*Expected Output: `=== AUDIT COMPLETE: ALL PASS ===`*

### 5. Compile LaTeX Manuscripts
```bash
# Compile Chinese Journal Template (39 pages)
cd paper_cn_journal_template
tectonic main.tex
```

---

## 📊 Summary of Core Numerical Results

| Pathogen & Phase | $R$ | $\delta R$ | Dispersion $k$ | $I_0$ | Generation Interval $\mu_g$ | $h^*_{\text{exact}}$ | Calendar Weeks |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **COVID-19 Delta Outbreak** | 1.3149 | 0.0285 | 223.2 | 28,347 | 4.7 d | 20.1 gen | **13.5 weeks** |
| **COVID-19 Delta Plateau Peak** | 1.0820 | 0.0410 | 223.2 | 28,347 | 4.7 d | 11.6 gen | **7.8 weeks** |
| **COVID-19 Delta Decline** | 0.8850 | 0.0350 | 223.2 | 28,347 | 4.7 d | 11.1 gen | **7.5 weeks\*** |
| **COVID-19 Omicron Peak** | 1.1632 | 0.0762 | 50.0 | 66,275 | 3.0 d | 6.8 gen | **2.9 weeks** |
| **COVID-19 JN.1 Surge** | 1.1023 | 0.0463 | 115.8 | 12,692 | 3.5 d | 8.4 gen | **4.2 weeks** |
| **Influenza 2022–23 Early** | 1.4138 | 0.0557 | 38.6 | 21,568 | 3.2 d | 11.2 gen | **5.1 weeks** |
| **Influenza 2024–25 Season** | 1.1925 | 0.0335 | 142.0 | 18,450 | 3.2 d | 15.8 gen | **7.2 weeks** |
| **RSV 2024–25 Season** | 1.0645 | 0.0125 | 185.4 | 8,920 | 8.4 d | 36.6 gen | **43.9 weeks\(^\dagger\)** |
| **RSV 2025–26 Season** | 1.0541 | 0.0078 | 210.0 | 11,200 | 8.4 d | 58.4 gen | **70.1 weeks\(^\dagger\)** |

*\(\*\) Subcritical decline phases ($R < 1$) undergo a dynamical regime shift toward micro-extinction and absorption; public health operations shift from continuous extrapolation to case contact tracing and elimination monitoring.*  
*\(^\dagger\) Subject to single-season physical boundary truncation (16–20 weeks).*

---

## 📜 Citation & License

If you find this codebase or theoretical framework helpful for your research, please cite:

```bibtex
@article{epidemic_predictability_limits_2026,
  title={传染病传播动力学的可预测视界、理论极限与实证研究},
  author={Anonymous Authors},
  journal={Working Paper / Submitted to Academic Journal},
  year={2026}
}
```

Distributed under the MIT License.
