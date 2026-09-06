# Epidemic Predictability Limits & Horizons (Replication Package)
# 《传染病传播动力学的可预测视界、理论极限与实证研究》开源复现代码与数据仓库

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Replication: 100% Verified](https://img.shields.io/badge/Replication-100%25%20Verified-brightgreen.svg)]()

This repository provides the complete, self-contained replication package, end-to-end data processing pipelines, numerical quadrature solvers, empirical surveillance datasets, and publication manuscripts for the research:
**"Predictability Horizons, Fundamental Limits, and Empirical Analysis of Epidemic Transmission Dynamics"**
**《传染病传播动力学的可预测视界、理论极限与实证研究》**

---

## 📌 Executive Summary (研究核心结论)

Adapting the ecological forecast horizon paradigm (Petchey et al., 2015) to branching process epidemic dynamics, this study derives an additive decomposition of prospective relative mean squared error:

$$\text{relMSE}^2(h) = \underbrace{\text{CV}^2(h)}_{\text{Demographic Stochastic Floor}} + \underbrace{P(h)}_{\text{Parameter Amplification}} \le \tau^2$$

Key analytical, methodological, and empirical findings:
1. **Macro Scaling Law vs. Micro Floor**:
   - In national aggregate surveillance ($I_0 \ge 10^4$), the Law of Large Numbers smooths microscopic demographic branching stochasticity (contributing $< 0.51\%$ to $\tau^2 = 0.25$). Predictability horizons are predominantly governed by the parameter signal-to-noise ratio (SNR) scaling law:
     $$h^* \approx \tau \cdot \frac{R}{\delta R}, \quad h^*_{\text{weeks}} \approx \tau \cdot \frac{R}{\delta R} \cdot \frac{\mu_g}{7}$$
   - In micro outbreaks ($I_0 \le 200, k \le 0.1$), demographic variance $CV^2$ creates an irreducible physical capacity boundary.
2. **Phase Horizons & Boundary Conditions**:
   - Across five non-RSV growth phases, theoretical exact horizons span **2.9–13.5 weeks**, contracting to **7.8 weeks** at peak plateaus, before undergoing a dynamical regime shift toward micro-absorption in decline phases.
   - For RSV, unconstrained mathematical extrapolation yields 43.9 and 70.1 weeks, which violates single-season physical bounds (16–20 weeks) and requires sample sizes exceeding total cases, illustrating the formal boundary of unconstrained growth models.
3. **Four-Term Error Accounting**:
   - In short horizons ($h = 1\text{--}2$ weeks), known mechanistic terms explain $4.6\%\text{--}27.4\%$ of empirical MSE, while unmodeled structural residuals account for $72.6\%\text{--}94.2\%$.
   - Over longer horizons, parameter extrapolation error dominates (explaining up to $88.7\%$ in influenza).
4. **Two-Tier Analytical Framework**:
   - Bridges the gap between theoretical mechanistic ceilings ($h^*$) and operational forecast skill windows (relative to naive persistence baselines, which cross $1.0$ within $1\text{--}4$ weeks).

---

## 📁 Repository Structure (仓库目录架构)

```
epidemic-predictability-limits-2026/
├── README.md                      # Project guide, theoretical summary, and replication instructions
├── LICENSE                        # Official MIT License
├── Response_to_Reviewers.md       # Point-by-point response to peer reviews
├── environment.yml                # Conda environment definition (Python 3.11)
├── references.bib                 # Clean BibTeX database (48 verified entries)
├── data/
│   └── processed/                 # Official US CDC weekly surveillance time series
│       ├── covid_final_weekly.csv.gz  # COVID-19 national weekly cases
│       ├── flu_final_weekly.csv.gz    # Influenza weekly positive clinical specimens
│       └── rsv_final_weekly.csv.gz    # RSV weekly PCR detections
├── scripts/                       # End-to-end numerical and empirical pipelines
│   ├── extract_cdc_data.py            # End-to-end parameter extraction from raw time series
│   ├── reproduce_all_tables.py        # One-click reproduction of Tables 2, 3, 4, 5, and 6
│   ├── make_all_figures.py            # Generates all 11 manuscript figures (Figs 1-6 + theory)
│   ├── consistency_audit.py           # Cross-checks numerical consistency across all outputs
│   ├── sim_verify_t1.py               # Theorem 1 & Lemma 2 branching simulation verification
│   ├── sim_verify_t3.py               # Theorem 3 near-critical quasi-stationary scaling
│   ├── sim_verify_t4.py               # Theorem 4 Cramér-Rao Fisher information bound
│   ├── verify_t5R.py                  # Theorem 5/5R AR(1) and random-walk variance
│   ├── ml1_mdn.py                     # MLP neural estimator benchmark
│   └── ml2_forecaster.py              # LightGBM forecaster benchmark
├── paper_cn_journal_template/     # Chinese journal template manuscript (LaTeX, PDF, Word docx)
│   ├── main.tex                   # LaTeX source (clean compilation)
│   ├── main.pdf                   # Publication-ready PDF (0 errors, 0 broken refs)
│   └── 流行病传播动力学的可预测视界、极限机制与实证研究_期刊模版版.docx # Word docx
├── paper_cn/                      # Standard Chinese manuscript package
├── paper_en/                      # English manuscript package
├── docs/                          # Word manuscripts for editorial review
├── figures/                       # High-resolution publication figures (Figs 1-6, t3, t4, t5)
└── reports/                       # Cached JSON output artifacts and figures
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
# Option A: Using Conda (Recommended)
conda env create -f environment.yml
conda activate epidemic-predictability

# Option B: Using pip
pip install numpy scipy pandas matplotlib scikit-learn lightgbm pypdf python-docx pymupdf
```

### 3. End-to-End Extraction from Real CDC Surveillance Data
```bash
python scripts/extract_cdc_data.py
```
*Extracts growth rates, OLS standard errors, overdispersion parameters, and computes exact horizons from raw CDC weekly series.*

### 4. One-Click Reproduction of All Manuscript Tables (< 2 seconds)
```bash
python scripts/reproduce_all_tables.py
```
*Executes 40-node Gauss-Hermite quadrature and Brentq root finding to reproduce Tables 2, 3, 4, 5, and 6.*

### 5. Generate All Publication Figures
```bash
python scripts/make_all_figures.py
```
*Generates all 11 figures into both `reports/figures/` and `figures/`.*

### 6. Compile LaTeX Manuscripts
```bash
cd paper_cn_journal_template
tectonic main.tex
```

---

## 📊 Summary of Core Empirical Parameters & Results (Table 2 Aligned)

All random seeds are strictly standardized to `20260807`.

| Pathogen & Phase | $R$ | $\delta R$ | $k_{\text{agg}}$ | $I_0$ | $\mu_g$ | $h^*_{\text{exact}}$ (Gen / Wk) | $CV^2$ Share (%) | 3-Factor Est. | 95% CI | Seasonal Truncation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **COVID-19 Delta Outbreak** | 1.3149 | 0.0285 | 223.2 | 28,347 | 4.7 d | 20.1 gen / **13.5 wks** | 0.05% | 15.5 wks | 8.9–20.0 | -- |
| **COVID-19 Omicron Peak** | 1.1632 | 0.0762 | 27.4 | 66,275 | 3.0 d | 6.8 gen / **2.9 wks** | 0.04% | 3.3 wks | 1.8–6.0 | -- |
| **COVID-19 JN.1 Surge** | 1.0520 | 0.0557 | 60.5 | 31,453 | 3.5 d | 8.4 gen / **4.2 wks** | 0.25% | 4.7 wks | 2.6–8.5 | -- |
| **RSV 2024–25 Season** | 1.2404 | 0.0146 | 1000.0 | 4,409 | 8.4 d | 36.6 gen / **43.9 wks** | 0.38% | 51.0 wks | 27.9–65.0 | 16–20 wks physical cap |
| **RSV 2025–26 Season** | 1.2130 | 0.0089 | 1000.0 | 1,868 | 8.4 d | 58.4 gen / **70.1 wks** | 1.01% | 81.8 wks | 46.2–95.0 | 16–20 wks physical cap |
| **Influenza 2022–23 Early** | 1.4138 | 0.0557 | 50.2 | 3,116 | 3.2 d | 11.2 gen / **5.1 wks** | 0.32% | 5.8 wks | 3.3–10.2 | -- |
| **Influenza 2024–25 Season** | 1.4012 | 0.0388 | 111.7 | 7,586 | 3.2 d | 15.8 gen / **7.2 wks** | 0.13% | 8.3 wks | 4.8–14.0 | -- |

---

## 📜 Citation & License

Distributed under the [MIT License](LICENSE).