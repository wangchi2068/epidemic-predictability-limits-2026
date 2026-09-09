# Peer Review Report — Round 15

**Manuscript.** 传染病动力学可预测视界、数理极限与实证分析 (*Predictability horizons, mathematical limits, and empirical analysis of infectious-disease dynamics*), round-14 revision, 42 pages, 1,038 lines of LaTeX source.

**Materials reviewed.** `main.tex`, `main.pdf`, and `Response_to_Reviewers.md` as submitted; and the public replication repository at https://github.com/wangchi2068/epidemic-predictability-limits-2026 (single commit `ecea80f`, 253 files). The repository copy `paper_cn_journal_template/main.tex` is byte-identical to the submitted source (md5 `77d96bf4ff0e62df222fe3f8b1ca1e7c`), so every repository observation below applies directly to the manuscript under review.

**Scope of this round.** The previous report raised three blocking findings, nineteen numbered corrections, and three process conditions. The response letter answers all twenty-five and asserts code-level repair with new regression guards. This report therefore does two things: it audits the twenty-five commitments against the manuscript and the repository, and it reviews the manuscript on its own merits. Section 4.6 contains the item-by-item adjudication.

Locations are given by section, table, figure, theorem name, or `file:line`. Chinese headings and table notes are quoted verbatim in the original so the authors can locate them.

---

## 1. Summary

The manuscript proposes a two-layer account of how far ahead an epidemic can be predicted, and separates that question into a theoretical limit and an operational one.

The theoretical layer is developed in Section 2 ("传播动力学可预测视界理论"). Under four stated assumptions — negative-binomial offspring `NB(R, k)`, constant `R` over the horizon, a mean generation interval `μ_g`, and conditional independence of the parameter estimator from the prediction-period realisation (A1)–(A4) — the relative mean squared error of an `h`-step-ahead forecast is decomposed additively into a microscopic term and a macroscopic term. Lemmas 1 and 2 give the intrinsic coefficient of variation `CV²(h) = (1 + R/k)(1 − R^(−h)) / [I₀(R − 1)]`; Lemma 3 gives the parameter-extrapolation amplification `P(h) = exp(2h²s²) − 2exp(h²s²/2) + 1` under log-normal propagation of `R̂`. Theorem 1 combines them as `relMSE²(h) = CV²(h) + P(h)` and defines the predictability horizon as the largest `h` at which this stays within a tolerance `τ`. Theorem 2 establishes strict monotonicity in `h`, so the horizon is unique and obtainable by root-finding. Three further results surround this core: Theorem 3 constructs a reflected-truncation quasi-stationary diffusion for finite host populations and reports an `O(N^(1/2))` near-critical relaxation scale; Theorem 4 derives the negative-binomial Fisher information `I(R) = Ck/[R(R + k)]` and a Cramér–Rao sample-size threshold; Theorems 5 and 5R give linear and AR(1) accumulation laws for environmental noise, with a cubic divergence at a unit root.

Section 3 checks these results by Monte Carlo simulation and asks whether machine-learning predictors can beat the derived bound. Section 4 applies the equations to three United States CDC weekly surveillance series (COVID-19, influenza, RSV) across seven epidemic phases, using a five-week inference window with three degrees of freedom, a tolerance `τ = 0.5`, and 2,000 bootstrap replicates. It reports theoretical horizons of 7.9 to 21.2 weeks for the five non-RSV phases and uncapped extrapolation roots of 41.5 and 67.8 weeks for the two RSV seasons, which it identifies as model artefacts exceeding the 16-to-20-week span of a respiratory season. It then builds a four-term error budget (intrinsic variance, drift, parameter error, unmodelled structural residual) and reports that the unattributed residual is positive in 10 of 12 configurations, ranging from 26.1% to 99.3%. Finally, a pseudo-real-time rolling backtest finds forecast skill degrading to parity with a persistence baseline at 1.8 to 5.3 weeks.

The headline conclusion is that the theoretical mechanistic horizon and the achievable operational lead time differ by a factor of 2.03 to 6.03, that the theoretical horizon functions as a loose upper bound rather than a forecast of achievable skill, and that measured error is dominated by structure the model does not attribute. Sections 5 and 6 translate this into tiered decision windows at four tolerance levels, an alerting rule, an equity argument that surveillance under-ascertainment converts directly into a predictability deficit, and three stated limitations.

---

## 2. Strengths

**The mathematics of the core decomposition survives independent re-derivation.** I re-derived Lemmas 1 through 3 and all four properties of Theorem 1 from the manuscript's own statements, without using any code or stored value from the authors' repository. The moment recursion, the closed form for `CV²(h)`, the L'Hôpital continuation at `R → 1`, the exact log-normal form of `P(h)`, and the supercritical closed form for the horizon all check out. Two specific decisions deserve credit. Property 1 states the existence condition as necessary and sufficient in its exact form and then explicitly demotes the first-order substitute to a necessary-only condition, giving the convexity reason; and Property 3 argues correctly that the floor function in `h*_stoch` is required rather than cosmetic, since rounding up would violate the tolerance. Theorem 5R was verified against 400,000 Monte Carlo paths across nine parameter combinations, with ratios between 0.999 and 1.001, and the unit-root `h³` identity was verified pointwise.

**The empirical numbers reproduce.** All seven rows of Table 2 ("美国三大呼吸道传染病典型阶段动力学参数与可预测视界测算") reproduce to printed precision from an independent root-solver: the approximate and exact horizons in generation units, the week-scale conversions, and the extrapolation multiples in the `h*/W` column (7 of 7). The claim in Section 4.2 that demographic stochasticity contributes at most 0.74% of `τ²` reproduces at 0.736% for the RSV 2025–26 phase, matching the manuscript's own sensitivity figure to three decimals. The bias band of 16.7%–16.9% between the first-order and exact roots, which the letter calls "analytically pinned", is genuinely pinned: at full precision the range is 16.7367%–16.9303%, and the mechanism is real, since fixing `τ = 0.5` locks the working point `hs` near 0.427 across all seven phases and the bias follows from that.

**The empirical headline is externally corroborated, not merely internally consistent.** The 1.8-to-5.3-week operational lead time is consistent with published forecast-hub experience and is positively confirmed by an independent institutional fact: the United States COVID-19 Forecast Hub shortened its official ensemble case forecasts to one to two weeks in September 2021 on calibration grounds (Lopez et al., *PLOS Computational Biology*, 2024, doi:10.1371/journal.pcbi.1011200). The European hub reports ensemble scaled relative WIS moving from 0.62 at one week to 0.9 at four weeks (Sherratt et al., *eLife*, 2023, doi:10.7554/eLife.81916). Both fall in the manuscript's interval. I found no published evidence that would falsify the claim.

**The round-14 verifiability commitments are substantially real, and three of them are unusual.** First, the build is genuinely a single command: `scripts_v2/make_all.py` sequences eight scripts, aborts on any non-zero exit, and terminates in a consistency suite that halts the build on failure. The master seed 20260807 is fixed identically across all five stochastic entry points. Second, the consistency suite exists and does more than the manuscript claims for it: I read all 165 lines statically and confirmed eight assertion classes, including the two physics-level guards the previous round demanded — a dimensional assertion that every `e_drift` row equals `h_week × v_drift`, and an assertion that the local-linear crossings for Delta and Omicron exist and are downward. The stale-literal blacklist holds 31 entries and all 31 are absent from `main.tex`. Third, and most creditably, negative results are reported rather than buried. Figure 3 panel (c) reports that the first-order theory for Corollary 2 falls inside the empirical interval in only 5 of 12 cells, and Corollary 2 is demoted to a directional claim in consequence; Section 3.2 reports the near-critical degradation of Theorem 3's ratios to 0.976 and 0.950; Section 4.4 reports two negative closure residuals without clipping them to zero. I independently recomputed the 5-of-12 coverage from the deposited `verify_t3.json` and confirm it, along with 12 of 12 cells showing empirical above theoretical.

**Several self-imposed limitations are correctly reasoned, not decorative.** The scale-invariance argument in Section 2.1 rests on the identity `h_gen · s_gen = h_week · SE_week`, which I verified symbolically and which holds independently of `Δ_g`; the manuscript correctly confines the invariance claim to working points where `CV²` is negligible, and its own data satisfy that condition (0.060% to 0.736% of `τ²`). Section 4.2 states plainly that the Cramér–Rao bound applies to an unbiased maximum-likelihood estimator on independent clusters while the quantity actually substituted is the standard error of an OLS slope on five aggregated weekly points, and downgrades the diagnostic to an order-of-magnitude heuristic on that basis. Theorem 3 declares itself a parallel model rather than the `N → ∞` limit of the branching model, which is the correct disclosure given that its diffusion coefficient carries no overdispersion parameter. Theorem 5R declares that it is not a strict generalisation of Theorem 5. These are the right calls, and they are stated where a reader will meet them.

**Bibliographic field accuracy is now clean.** Fabricated bibliographic fields were a blocking finding in the previous round. I re-verified fifteen high-risk entries against Crossref, PubMed, and publisher pages without relying on the letter's self-report: all fifteen pass on author list, year, journal, volume, issue, and pages or article number. The two previously defective entries are genuinely repaired (`ho2023simultaneous` pages 201–205, PubMed 36722802; `nemcova2026unjustified` author list and article number e79, PubMed 42178993). Volume-year self-consistency across five 2026 entries also checks out, which is where invented volume numbers usually show.

---

## 3. Weaknesses

Ordered by severity, most severe first. Each entry points to the numbered comment that carries the evidence.

### Blocking

**B1. The repository's own data contradicts the manuscript's disclosure of which COVID-19 indicator was analysed (comment 4.3, item (i)).** Section 4.1 and the data-availability statement both state that the Delta and Omicron phases use weekly confirmed cases and that only the JN.1 row splices in NHSN hospitalisations. The deposited analysis series is at hospitalisation scale across all three phases, differing from the archived confirmed-case dataset by a factor of 8.6 to 15.8. The initial condition `I₀` feeds `CV²` and `C_req` directly, and the Delta and Omicron rows are the two endpoints of the headline 7.9–21.2-week interval.

**B2. The manuscript's central framework has a 2012 epidemiological precedent that is not cited, and the increment claim is correspondingly over-stated (comment 4.4, item (i)).** Pérez-Reche et al. (2012) already state the existence of a prediction horizon, its dependence on the desired precision, monotone growth of uncertainty with look-ahead time, and the separation of parameter uncertainty from intrinsic stochasticity. Section 1.2 attributes the horizon concept entirely to ecology and claims the conversion of a static threshold into an explicit horizon as this paper's own step.

**B3. The previous round's first blocking finding is repaired numerically but not conceptually, and the incorrect form survives in two places (comment 4.3, item (ii)).** The Table 4 note still prints the dimensional form that Section 4.4 explicitly disowns two pages earlier, and the generator docstring argues that the two forms are equivalent, which they are not for any reading of the variance term.

### Major

**M1.** A newly written boundary-classification claim in Appendix C is mathematically false; the correct statement is both simpler and stronger (comment 4.1, item (i)).
**M2.** The robustness threshold newly added at Section 4.2 cannot be derived under either reading of the word it uses; the two defensible values are 2.58 and 1.22, not 1.4 (comment 4.1, item (iii)).
**M3.** Figure 1 prints the Theorem 4 sample-size threshold without the `R²` factor, so the figure's formula cannot produce either of the two thresholds the text reports (comment 4.1, item (ii)).
**M4.** Three separate demotions made this round — Theorem 3 to an analogy, Corollary 2 to a directional claim, Theorem 4 to a heuristic — did not propagate to the contribution list in Section 1.3, which still asserts all three at full strength (comment 4.1, item (iv)).
**M5.** The (A4) violation is disclosed correctly in five places but contribution four in Section 1.3 still describes the empirical work as validation without qualification (comment 4.1, item (v)).
**M6.** The Figure 3 caption reports an empirical-to-theoretical ratio band of 1.2–1.6 at `N = 500`; the deposited values give 1.07–1.61 (comment 4.2, item (i)).
**M7.** The ingest step from raw snapshots to analysis inputs is absent from the repository, which is precisely why B1 cannot be resolved by a third party (comment 4.3, item (iii)).
**M8.** The two new consistency guards are point regression locks, and every prose defect found this round lies outside their reach; the manuscript's own description of the suite is also out of date (comment 4.3, item (iv)).
**M9.** The repository README still presents three conclusions the manuscript has withdrawn, including one the consistency suite explicitly asserts against (comment 4.3, item (v)).
**M10.** The bootstrap intervals and valid-resample counts that the response letter offers as evidence for the local-linear crossings exist in the repository but never entered the manuscript, so the claim that the two baselines agree cannot be assessed by a reader (comment 4.1, item (vii)).
**M11.** A 2026 result establishing that the near-critical sensitivity peak holds only for overdispersion above `k = 0.3` is not cited, although it directly qualifies the paper's near-critical narrative and although the relevant reference already sits uncited in the bibliography (comment 4.4, item (iii)).

### Minor

**m1.** The 5/12 annotation inside Figure 3 panel (c) is overlapped by the plot legend and is only partly legible (comment 4.5, item (i)).
**m2.** Two quantitative bands (16.7%–16.9% and 2.82–2.87) are correct at full precision but cannot be reproduced from the figures the manuscript prints (comment 4.5, item (ii)).
**m3.** The combinatorial bound in Section 4.5 corresponds to a non-circular block bootstrap while the code implements a circular one; the true count is 36, not 16 (comment 4.1, item (viii)).
**m4.** Appendix B describes a random variable as a deterministic constant; the conclusion is right but the stated reason is not (comment 4.1, item (ix)).
**m5.** The DOI accounting in the letter is wrong in denominator and in category counts, and the disclosure location it names does not exist in the manuscript (comment 4.5, item (iii)).
**m6.** Dependency pins give lower bounds only, which does not support the bit-reproducibility that the reported integer resample counts require (comment 4.3, item (vi)).
**m7.** Declared snapshot dates precede the actual coverage of the deposited series by four and five months (comment 4.3, item (vii)).
**m8.** The letter's claim that four `references.bib` copies converged is a miscount; there are two (comment 4.5, item (iv)).
**m9.** Drake's coefficient of variation is that of final outbreak size, not of generation-`h` incidence, so the precedent holds at the level of idea rather than of quantity (comment 4.4, item (vi)).
**m10.** Twenty-three of sixty-six bibliography entries are uncited, six of which should be carrying argument (comment 4.4, item (v)).
**m11.** The ordering of bars in Figure 3 panel (a) runs opposite to the order of the caption's narration (comment 4.5, item (v)).
**m12.** The claim that machine-learning optimisation does not break the theoretical limit is stronger than the evidence a Cramér–Rao bound can supply, and the tuning budget is undisclosed (comment 4.1, item (vi)).

---

## 4. Detailed comments

### 4.1 Mathematics and theory

**(i) Appendix C, Theorem 3 supporting discussion: the Feller boundary classification is incorrect. Major.**

The passage at `main.tex:888` states that the classification of the boundary at the origin varies with the drift parameter, with a critical value at `λ = (R + 1)/2`, and is exit or absorbing in the setting relevant to Dolgoarshinnykh and Lalley.

For the limit diffusion the manuscript itself derives, `dy = (λy − Ry²)ds + sqrt((R+1)y) dW`, the scale density satisfies `s'(y) → 1` as `y → 0`, a finite non-zero limit that does not depend on `λ`. The speed density behaves as `C/y`. Applying the Karlin–Taylor criteria, the first integral is finite because the integrand tends to a constant, while the second diverges logarithmically. I evaluated both numerically at `λ` in {0.05, 0.5, 0.9, 1.0, 1.1, 2.0, 5.0}, with the alleged critical value 1.0 in the middle: the first integral stays finite throughout (0.456 to 2.907) and the second diverges linearly in the logarithm of the truncation (2.24, 3.91, 5.58, 7.25, 8.92 at cut-offs from 1e−3 to 1e−11). The classification does not change anywhere.

The correct statement is that the origin is an exit boundary for every positive `λ`. The likely source of the error is a transplanted Feller condition: `λ = (R + 1)/2` is where `2λ/(R+1) = 1`, the analogue of `2ab/σ² = 1` for a Cox–Ingersoll–Ross process. That condition governs CIR because CIR carries a non-zero constant in the drift at the origin; here the drift vanishes at the origin, and the boundary behaviour is fixed by the linear vanishing of the diffusion coefficient alone.

Nothing downstream depends on the false critical point, and the direction of the claim is right, which is why this is major rather than blocking. But the sentence was written this round, to support the withdrawal of the spectral-gap claim, and it replaces a determinate conclusion with an indeterminate and incorrect one.

*Action.* Replace with: by the Karlin–Taylor criteria the first integral converges while the second diverges, since the speed measure is logarithmically divergent at the origin, so `y = 0` is an exit boundary for every `λ`.

**(ii) Figure 1, lower-right cell (`main.tex:166`): the printed Theorem 4 threshold omits the `R²` factor. Major.**

The figure prints the sample-size threshold as `(1/R + 1/k)/ε²`. Theorem 4 at `main.tex:381` and Appendix D both give `(z_(1−α) + z_(1−β))² R² (1/R + 1/k)/ε²`, and both are correct. With the paper's own worked values (`R = 1.1`, `k = 1.0`, `ε = 0.1`), the text's form yields 231.00 and 1428.2, matching the printed thresholds of 231 and 1,428 exactly. The figure's form yields 190.91, short by the factor `R² = 1.21`; supplying the power coefficient gives 1,180 rather than 1,428.

The omission has a specific cause worth naming in the revision. The Cramér–Rao result bounds the *relative* variance, `Var(R̂)/R² ≥ (1/R + 1/k)/C`. Converting this into a threshold for detecting an absolute departure `ε` requires multiplying the numerator back by `R²`, because the test concerns `R̂ − 1`, a dimensional difference, rather than a relative one. The figure carries the relative-variance numerator directly across to an absolute `ε²`.

No downstream result uses the figure's form; Section 4.2 uses the text's. But Figure 1 is the paper's only theoretical schematic, and readers copy formulas from schematics.

**(iii) Section 4.2, aggregation-inflation robustness: the stated reversal threshold is not derivable. Major.**

The passage states that if aggregate smoothing depresses the RSV 2025–26 standard error by more than about 1.4 times relative to the unsmoothed case, the cross-season contrast reverses.

Write the true standard error as `x` times the observed one; then the true required-cluster ratio is the observed one divided by `x²`. The observed ratios are 0.2214 for RSV 2024–25 and 1.4758 for RSV 2025–26. Two readings of "reverses" are available, and I computed both. If it means the cross-season contrast inverts, so that the 2025–26 ratio falls below the 2024–25 ratio, the threshold is the square root of their quotient, 2.582. If it means the 2025–26 season simply ceases to be flagged as data-insufficient, so that its ratio falls below one, the threshold is the square root of 1.4758, or 1.215. Setting `x = 1.4` gives a 2025–26 ratio of 0.7529, still far above the 2024–25 ratio of 0.2214, so the contrast has not reversed; it has only crossed unity.

The value 1.4 sits between the two defensible thresholds and matches neither. The direction of the error is not neutral: under the sentence's literal reading the contrast is considerably more robust than the manuscript concedes, and under the other reading it is more fragile.

The surrounding argument is sound and should be kept. Smoothing depresses the residual standard error, which raises the required cluster count, so the direction of any inflation can only strengthen the doubt about 2025–26 data sufficiency. That weak conclusion is robust; the quantitative threshold attached to it is not.

*Action.* State which reversal is meant and use the corresponding value (2.58 or 1.22), or delete the numeric threshold and keep the directional argument.

**(iv) Section 1.3, contribution two (`main.tex:96`): three demotions made this round are not reflected. Major.**

The contribution list states that the paper "揭示了" a dynamical slowing mechanism in which the characteristic relaxation time diverges as `O(N^(1/2))`, attributing this jointly to Theorem 3 and Corollary 2, and separately describes Theorem 4 as delivering a rigid ("刚性") minimum-sample threshold.

Each of the three has been demoted elsewhere in this same revision. Theorem 3's scaling is now presented as a heuristic analogy to absorbed-boundary extinction times, with the manuscript explicitly declining to claim an independent spectral-gap proof and noting that Dolgoarshinnykh and Lalley themselves deny the connection to near-critical scaling. Corollary 2 is now a directional claim only, on the strength of 5-of-12 coverage. Theorem 4's empirical application is now an order-of-magnitude heuristic, with the manuscript stating that it does not use the language of an information-theoretic violation. I checked the propagation of the Theorem 3 demotion across eight locations: the abstract, the Figure 1 cell, the Figure 1 caption, the theorem statement, its proof sketch, Appendix C, Section 5.4, and the conclusion all carry it. Contribution two is the sole location that does not, and it also carries the strongest verb in the paper.

**(v) Section 1.3, contribution four (`main.tex:99`): the (A4) qualification is not reflected. Major.**

The (A4) disclosure added this round is substantively correct and well placed. At `main.tex:214`, immediately after the assumption is introduced, the manuscript states that `R̂_t` and `I_(0,t)` are estimated online from the same sliding window as the prediction period and therefore share historical randomness, that (A4) holds only approximately in finite samples, and that the theory-empirics pair is an exploratory contrast rather than a same-conditions validation. Section 4.5 repeats this, the abstract and conclusion both say "探索性", and Section 4.4 correctly labels the four-term budget a descriptive closure rather than the strict `L²` projection of Theorem 1. That last point matters, because the additivity in Theorem 1 depends on (A4); once (A4) fails, the observed relative error is not the sum of the modelled components, and the manuscript is right to say so.

Contribution four nonetheless describes the rolling pseudo-real-time work as "验证" with no qualifier. A reader who reads the contribution list and the abstract's opening will take the two-layer contrast to be an empirical validation of Theorem 1, which the manuscript denies in three other places.

**(vi) Section 3.3, machine-learning benchmark: the conclusion exceeds the evidence. Minor.**

The comparison itself is fair in construction: the generating mechanism is known, the bound is computed under the same mechanism, the truth is available, and there is no leakage. The reported MLP ratio of empirical variance to the Cramér–Rao bound is 6.69.

The inference drawn, that algorithmic optimisation approaches but does not break the theoretical limit, does not follow. A Cramér–Rao bound constrains unbiased estimators; end-to-end point prediction by an MLP or a gradient-boosted model is biased, and biased estimators can in principle fall below an unbiased bound. A ratio of 6.69 shows these two predictors are far from the bound in this setting; it is not evidence that the bound is unbreakable. The hyperparameter search budget and training sample size are also not disclosed, so weak tuning and a genuine limit are not distinguishable from what is reported.

*Action.* Restate as: under the tuning budget used here, neither benchmark approaches the theoretical lower bound. Disclose the search space, budget, and training sample size. If the stronger claim is wanted, it needs a bound that covers biased estimators, such as a Bayesian Cramér–Rao or van Trees inequality.

**(vii) Section 4.5 and Table 5: the two-baseline agreement cannot be assessed from the manuscript. Major.**

Section 4.5 concludes that the persistence up-crossings (3.52, 1.82, 5.34 weeks) and the local-linear down-crossings (5.33, 1.16 weeks) agree in magnitude, and therefore that the 1.8-to-5.3-week headline does not depend on baseline choice. For the persistence baseline the manuscript prints the bootstrap intervals and the valid-resample counts (975, 652, 907), and the Table 5 note explains that 652 is low enough that the Omicron interval, and its point estimate, should be read as indicative. For the local-linear baseline it prints point estimates only.

The corresponding quantities exist. `reports/rolling_results.json` records Delta at 5.33 with interval 2.91–7.39 and 773 valid resamples, and Omicron at 1.16 with interval 1.14–7.42 and 565 valid resamples, both flagged as downward. These are the figures the response letter quotes; they are real, and my independent recomputation of the crossing points from the deposited skill series reproduces them (the 5.32-versus-5.33 difference for Delta traces to three-decimal rounding at deposition, and disappears when the higher-precision mean-squared-error field is used).

Two consequences follow from their absence in the manuscript. A reader cannot judge whether the gap between 5.33 and 3.52 lies inside sampling noise, which is exactly what the agreement claim asserts. And the Omicron local-linear estimate rests on 565 valid resamples, fewer than the 652 for which the manuscript wrote an explicit censoring warning; by the manuscript's own standard, that warning applies here too and is not given.

*Action.* Print both intervals and both valid-resample counts in Section 4.5 or the Table 5 note, and extend the censoring caveat to the 565 case.

**(viii) Section 4.5, block-bootstrap combinatorics: the stated count corresponds to a different scheme than the one implemented. Minor.**

The manuscript argues that with block length 3 over `M = 6` origins there are only 4 possible starting blocks and at most 16 distinct ordered resamples, and uses this to justify reading the Omicron interval as indicative. Those numbers describe a non-circular moving block bootstrap, where the number of starting positions is `n − L + 1 = 4`.

The implementation is circular: starting indices are drawn over the full range 0 to 5, and block indices wrap modulo the series length; the function's own docstring says "circular wrap". Exhaustive enumeration gives 6 starting blocks and 36 distinct ordered resamples, so the manuscript understates by a factor of 2.25.

The methodological conclusion is unaffected — 36 is still small against 1,000 resamples, and the interval should still be read as indicative — which is why this is minor. But it is a factual description of the paper's own method that does not match the code, and a reviewer checking method details will land on it.

**(ix) Appendix B (`main.tex:800`): a random variable is described as a deterministic constant. Minor.**

The proof states that under (A4) the difference between the expected trajectory and the estimated trajectory "成为确定性常数". That difference equals `I₀(R^h − R̂^h)` and is a random variable, since `R̂` is random. Were it a constant, `P(h)` would be identically zero, contradicting Lemma 3.

The conclusion is nonetheless correct and the repair is one clause. The cross term vanishes because the two factors are independent under (A4) and the first has mean zero; degeneracy is not needed. Finiteness of the relevant moment is also required and is supplied automatically by the log-normal assumption, though Theorem 2 states its moment condition explicitly while Appendix B does not.

**Verified without objection.** The following were independently re-derived or re-computed and I found no problem: the scale-invariance identity of Section 2.1 and the condition under which the manuscript confines it; Lemmas 1 through 3 and all four properties of Theorem 1; the quasi-stationary density of Theorem 3 including the characteristic scale, the transition window, and the rescaling algebra; the withdrawal argument that the reflected speed measure diverges logarithmically so that no non-degenerate limiting stationary measure exists; the backward-equation solution behind Corollary 2; the Fisher information, the Cramér–Rao bound, the two sample-size thresholds, and the sparse-sampling inflation of Theorem 4, along with the self-imposed unbiasedness caveat; Theorems 5 and 5R and Corollary 3; the directional robustness of the RSV data-sufficiency conclusion under aggregation inflation; and the internal consistency of the constant interval multiplier that replaced the withdrawn degrees-of-freedom intervals.

### 4.2 Empirical method and error accounting

*Items (vi) through (viii) of Section 4.1 also bear on empirical method and are not repeated here.*

**(i) Figure 3 caption (`main.tex:483`): the empirical-to-theoretical band is wrong at the lower end. Major.**

The caption reports that at `N = 500` the ratio of empirical to first-order theoretical establishment probability reaches 1.2–1.6. Recomputing all six cells at `N = 500` from `reports/verify_t3.json` gives 1.4981, 1.6145, 1.0672, 1.2672, 1.1273, and 1.2322. The upper bound is right; the lower bound is not, since two cells fall below 1.2 and the minimum is 1.07. The true range is 1.07–1.61.

Everything else in that caption checks out: 12 cells, 5-of-12 coverage recomputed independently from the deposited intervals, 2,500 repetitions per cell, 400 per cell in panel (b), 7-of-8 coverage in panel (b), the panel (a) ratios of 0.9995, 0.9991, 0.976, and 0.950, and the qualitative statement that empirical exceeds theoretical in all twelve cells.

This band was written this round, as part of the disclosure that demotes Corollary 2. Widening it to 1.07–1.61 weakens the apparent strength of the systematic underestimate without disturbing the demotion, which rests on the 12-of-12 direction and the 5-of-12 coverage.

**(ii) Section 4.4 and Table 4: the error-accounting numbers are sound.** For completeness, since this was the previous round's first blocking finding: I recomputed the closure `e_misspec = obs_total − (cv2 + e_drift + p_param)` for all twelve rows from the deposited budget file and matched the stored values to within 1e−12; the tally of 10 positive residuals, the range 26.1432%–99.3086%, the count of 9 above 40%, and the two negative rows at −372.7938% (RSV 2024–25) and −178.5723% (RSV 2025–26) all hold, and the attribution of each negative value to the correct row is right in the manuscript and in the letter. The effective origin counts are deposited per row, with the value 3 appearing only on the two RSV 2024–25 rows, matching all three disclosure locations. The weekly drift variances printed in Section 4.4 match the deposited values, with one three-significant-figure truncation for influenza that has no consequence.

**(iii) Section 4.5, comparability of the operational lead time with published experience. Minor.**

Two differences in measurement convention affect how the 1.8-to-5.3-week result should be compared with hub literature, and neither is currently stated.

First, the published one-to-four-week experience is largely for case forecasts, whereas deaths remain more predictable at three to four weeks because they are a lagged smooth function of past infection. If the COVID series here is at hospitalisation scale, as comment 4.3, item (i) argues, its smoothing properties sit between the two, and its skill decay should be slower than the case literature would suggest. The manuscript places its result alongside the one-to-four-week range without distinguishing the target quantity.

Second, the persistence baseline degrades with horizon as well, so a relative skill ratio understates absolute decay. The manuscript already concedes one optimism source, noting that a frozen-vintage backtest gives an upper bound on lead time and that real-time initial reports would be shorter. The baseline-degradation effect is a second, independent source of optimism in the same direction and is not mentioned.

### 4.3 Reproducibility, code, and data

**(i) The deposited COVID-19 series is at hospitalisation scale across all three phases, contradicting three statements in the manuscript. Blocking.**

Section 4.1 states: "由于 COVID 确诊序列于 2023-05-10 联邦突发公共卫生事件到期后停报，JN.1 阶段改用 NHSN 周度呼吸道住院量，与 Delta/Omicron 的周度确诊量是不同观测……其余六阶段均用同一检测口径". The data-availability statement makes the same division, naming the confirmed-case dataset for the main series and NHSN hospitalisations for JN.1 only.

The repository archives the confirmed-case snapshot the manuscript names, so the comparison is direct. Summing that dataset over 51 states gives 242,485 cases in the Delta window and 1,047,558 in the Omicron window. The deposited analysis series carries 28,347 and 66,275 for the same windows, and those are exactly the values printed in the `I₀` column of Table 2 — so the analysis does read the deposited series, and the deposited series is roughly an order of magnitude below contemporaneous cases (median ratio 12.6 across 156 overlapping weeks).

Against NHSN total COVID-19 admissions, summed the same way, the correspondence is close in every period, including the two the manuscript describes as confirmed cases: Pearson correlation 0.99965 with median relative difference 0.069 in the Delta window, 0.99791 and 0.023 in the Omicron window, and 0.99355 and 0.064 in the JN.1 window. The Delta and Omicron windows track hospitalisations no less closely than the JN.1 window does. A separate corroborating detail: the deposited COVID series extends to 2024-04-20, forty-nine weeks past the reporting-cessation date the manuscript gives for confirmed cases, and the entire JN.1 inference window lies inside that extension.

Three consequences. The manuscript spends a paragraph confining the indicator splice to one row, declaring that row directionally interpretable and the other six cell-by-cell comparable; if all three COVID phases share an indicator, that confinement is misdescribed. The `I₀` values enter `CV²` in the denominator and enter `C_req`, and the Delta and Omicron rows supply both endpoints of the headline 7.9–21.2-week interval, so the premise of the argument that horizons are governed by parameter signal-to-noise is affected by an order of magnitude in `I₀`. And the finding may be favourable to the authors: if all three phases are on one indicator, the self-declared splice defect does not exist, the Section 4.1 disclaimer can be removed, and the JN.1 row need not be demoted to directional reading. Either way the current description does not match the deposited data.

*Limit of this check, stated plainly.* The deposited series does not equal any NHSN column week by week (0 exact matches out of 49 nationally; 4 out of 776 at state level, with California deviating by roughly 1 to 3 percent). I can therefore establish that the scale and trajectory are those of hospitalisations rather than confirmed cases, but not which column or aggregation it is. That ambiguity is itself a consequence of item (iii) below.

*Action.* Document the exact construction of the deposited COVID series — source dataset identifier, column names, aggregation and filtering rules — and correct Section 4.1 and the data-availability statement accordingly.

**(ii) Table 4's note prints the dimensional form that Section 4.4 disowns, and the generator's docstring defends that form with an invalid equivalence argument. Blocking.**

Section 4.4 item 2 (`main.tex:587`) states that because the drift variance is estimated on the weekly series, accumulation must be over calendar weeks rather than generation steps, notes that an earlier version multiplied the weekly variance by the generation step and thereby inflated the COVID and influenza rows by 1.5 to 2.3 times while deflating the RSV rows to 0.83 times, and states that the revision has unified everything to the weekly convention. I confirmed those conversion factors directly (`7/μ_g` gives 1.49, 2.33, 2.19, and 0.833).

The Table 4 note (`main.tex:604`) prints the generation-step form, which is the form the body text has just disowned, and which disagrees with all twelve rows of the table above it. The numerical repair is complete and verified: every row equals the weekly product to within 1e−12, and every row disagrees with the generation-step product.

What raises this above a stale-note oversight is the code. The generator docstring at `error_budget_v2.py:25–26` asserts that the implemented computation "matches the printed formula `E_drift = h_gen * v^2` with `v^2` read as the per-week environment-noise variance, converted consistently to week units." This is not true under any reading. If the variance term is per-week, then the generation-step product equals `(h_week/Δ_g)` times that variance, which differs from the weekly product by exactly `Δ_g = μ_g/7` — the same 1.49, 2.33, 2.19, and 0.833 that Section 4.4 identifies as the original defect. No phase has `μ_g = 7` days, so the two forms never coincide here.

The mechanism by which this survived is also identifiable. The table body is generated and byte-compared against JSON, but the table note is hand-written prose in `main.tex`, and the new dimensional assertion in the consistency suite compares JSON numbers only. This matches the manuscript's own statement that the suite does not audit prose semantics or physical dimensions.

The reason this is blocking rather than minor is not the two-page inconsistency, uncomfortable as that is for a reader. It is that the repair of the previous round's principal finding was accompanied by a written argument that the erroneous form was equivalent all along. The defect was routed around numerically without being resolved conceptually, which bears directly on how much confidence the letter's claim of propagation everywhere can carry.

*Action.* Correct the Table 4 note to the weekly form; delete or correct the docstring's equivalence sentence; and see item (iv) on bringing hand-written formulas into the checked surface.

**(iii) The step from raw snapshots to analysis inputs is not in the repository. Major.**

The eight scripts in `scripts_v2/` consume the three processed files and the report JSONs; the build sequence begins at the pipeline stage. No code anywhere in the repository produces `data/processed/` from `data/raw/`. The README structure notes label the processed directory as frozen analytical inputs and the manifest's step table also starts at the pipeline. The legacy extraction script is explicitly marked as not part of the build and has no verifiable correspondence to the current processed files.

The analysis stage is genuinely reproducible: the three processed inputs ship with the repository at 110 KB total, their SHA-256 checksums match the manifest, and the seed is fixed throughout, so a clone can rerun the chain without internal data or credentials. The construction stage is not reproducible. This is not a generic completeness complaint. The dispute in item (i) — whether the series is cases or admissions, and where the forty-nine extra weeks originate — lives precisely in the missing step, and no third party can settle it. For a package that describes itself in its README as a complete single-source-of-truth replication package and is in its fourteenth revision, that is a substantive gap.

**(iv) The two new consistency guards are point regression locks, and the manuscript's description of the suite is out of date. Major.**

Both guards exist, and the letter is accurate on that point. Reading the suite statically, the dimensional assertion is at `check_consistency.py:133–144` and the two-sided crossing assertion at `:146–152`.

The manuscript's code-availability statement lists four checks: fragment-to-JSON byte comparison, figure non-blankness, the stale-literal blacklist, and the abstract-interval and Cramér–Rao ratio assertions. The suite actually implements eight assertion classes, including the two new ones. So the disagreement noted in the previous round resolves in the authors' favour on substance: the guards were added and the manuscript's self-description was not updated.

The guards are nonetheless narrower than the claim they support. The letter presents them as evidence that the three blocking findings are guarded against regression. The dimensional assertion pins one specific equality on one specific JSON file; the crossing assertion pins the direction of two specific waves. Neither generalises. Every prose defect found this round lies outside both: the Table 4 note and its docstring in item (ii), which is the same dimensional problem in a different medium; the Figure 3 caption band in comment 4.2; the Figure 1 formula, the Appendix C boundary claim, and the Section 4.2 threshold in comment 4.1. That is five instances of a single failure mode, of which three were newly written this round in the course of responding to the review.

The suite's other structural limits, from source reading: it reads only `main.tex`, so no other reader-facing file in the repository is checked (see item (v)); the figure check tests only that more than 5% of pixels are non-background, so it cannot see occlusion or semantics (see comment 4.5, item (i)); the blacklist enumerates known retired literals rather than expressing an invariant, so it can only catch what a previous round already named; the abstract assertion is a single regular expression matching the first week-range in the file; and nothing anywhere asserts the identity of the indicator in a deposited series, which is why item (i) could persist.

*Action.* Update the code-availability statement to the eight classes actually implemented. To guard the class rather than the instance, bring hand-written formulas into the checked surface — for example by having the generator emit the formula strings used in table notes, captions, and figure cells — and add an indicator-identity assertion for each deposited series.

**(v) The repository README presents three conclusions the manuscript has withdrawn. Major.**

The manuscript itself is clean: all 31 blacklisted literals return zero occurrences in `main.tex`, which I verified entry by entry.

The blacklist scan reads one file. Scanning the same 31 entries across the repository's other reader-facing text finds 13 in `paper_cn/main.tex`, 7 in `Response_to_Reviewers.md`, and 2 in `paper_cn/main_final.tex`. More consequentially, the README's executive summary — labelled as containing numbers generated by the current chain — still states that unmodelled structural residuals account for 51.2%–99.6%, against the current 26.1%–99.3%, and still states an RSV 2025–26 cluster-count ratio of 2.46, against the deposited 1.476. Both retired values are on the blacklist; the ratio 1.476 is the subject of a dedicated assertion in the suite. The README escapes both because it is not the file being scanned.

The README is the first and often only file a reader of the public repository sees, and it currently contradicts the manuscript on three withdrawn conclusions, with the withdrawn version more prominent. This does not affect the manuscript's internal consistency, but it does defeat the single-source-of-truth claim at the repository level.

**(vi) Dependency specification does not support the reproducibility the results require. Minor.**

The environment file pins Python to a minor version and gives open lower bounds for numpy, scipy, pandas, matplotlib, scikit-learn, LightGBM, and PyTorch, with no lockfile and no upper bounds. Several reported quantities are integers that depend on bit-level generator behaviour: the valid-resample counts 773, 565, 975, 652, and 907 are printed in the manuscript and in Table 5, and two of them are the subject of consistency assertions. A fixed seed is necessary for these to reproduce but not sufficient across resolved environments. A lockfile, or at minimum upper bounds on the numerical dependencies, would close this.

**(vii) Declared snapshot dates precede the deposited coverage. Minor.**

The manuscript states in two places that the NHSN, influenza, and RSV snapshots are from March 2026. The deposited influenza series runs to 2026-07-04 and the RSV series to 2026-08-01, four and five months later; all four raw snapshot filenames carry 2026-09-07, and the repository manifest also records that date. Since the latest analysis window ends 2025-12-06, no result is affected. The most likely explanation is that the statement was not updated after the final data refresh.

### 4.4 Literature and citation

**(i) The horizon framework has a 2012 epidemiological precedent that is not cited. Blocking.**

Section 1.2 attributes the forecast-horizon concept to ecology (Petchey and colleagues, 2015) and presents the conversion of a static coefficient-of-variation threshold into an explicit horizon as this paper's own step, adding the parameter-extrapolation term to Drake's framework.

Pérez-Reche, Neri, Taraskin and Gilligan, "Prediction of invasion from the early stage of an epidemic", *Journal of the Royal Society Interface* 9:2085 (2012), doi:10.1098/rsif.2012.0130, states all four constituent elements in its discussion. I verified this against the article's full text rather than a search snippet. It states that a prediction horizon exists beyond which prediction uncertainty is unacceptable; that the location of the horizon is epidemic-dependent and depends on how precise the predictions are required to be; that prediction uncertainty grows monotonically with look-ahead time, which is the content of Theorem 2; and that parameter-estimation uncertainty and intrinsic stochasticity are two distinct and separately insufficient sources, since even exactly known parameters would not permit arbitrarily precise prediction. It also discusses when a horizon fails to exist.

Two corrections follow. The priority attribution in Section 1.2 is wrong: the concept was available inside epidemiology in 2012, in a form closer to this paper than the ecological version, three years before the ecological citation the manuscript relies on. And the increment claim is over-stated: converting a static threshold into an explicit horizon, with the two uncertainty sources separately named, was done in 2012.

**(ii) The residual increment, stated correctly, is real. Major as currently worded.**

Two rounds of searching found no work that gives the closed-form solution and root-finding equation for `CV²(h) + P(h) = τ²` under negative-binomial branching with log-normal parameter propagation. In hub-adjacent literature the forecast horizon appears only as an evaluation axis, never as a derived quantity. That increment stands.

The manuscript already contains the correct formulation, at the end of the Section 1.2 paragraph, where it describes its contribution as a specific analytical instantiation of a general framework. The revision should promote that sentence from a concessive closing clause to the increment claim itself, and remove the priority-flavoured wording that precedes it.

**(iii) A 2026 result that qualifies the paper's near-critical narrative is not cited, and the reference needed to locate the paper relative to it is already in the bibliography, uncited. Major.**

Boudreau et al., arXiv:2506.24103, establish that predictive sensitivity peaks at the epidemic threshold only when transmission is sufficiently homogeneous, specifically for overdispersion above `k = 0.3`; for more heterogeneous systems the sensitivity peak moves above threshold. Near-critical horizon contraction is one of this manuscript's central narratives, and empirical overdispersion for COVID-19 and influenza is commonly estimated well below 0.3. This is a published qualification of the paper's own main story, using the same parameterisation the paper adopts.

The bibliography already contains `endo2020overdispersion`, the estimate that would determine which side of that boundary the studied phases fall on, and `hebert-dufresne2020beyond`; neither is cited in the text.

**(iv) Two further omissions bear directly on stated contributions. Major.**

Steyn, Parag, Thompson and Donnelly, *Statistics in Medicine* 44:e70204 (2025), doi:10.1002/sim.70204, handle inference and prediction jointly under a renewal model, explicitly separating parameter uncertainty from observation-process stochasticity and propagating both forward by sequential Monte Carlo. This is the closest existing implementation of the paper's two-source forward propagation, and the manuscript needs to state its delta against it, which is presumably closed form against numerical.

Parag and Donnelly, *PLOS Computational Biology* 16:e1007990 (2020), doi:10.1371/journal.pcbi.1007990, is the origin of the Fisher-information route the paper's Theorem 4 follows; the manuscript cites only the later work in that line. Their *Systematic Biology* 69:1163 (2020) paper, doi:10.1093/sysbio/syaa035, is the direct precedent for using Fisher information as a precision measure and would be appropriate at Section 2.5.

Three further entries would be appropriate rather than required: the hub dataset paper (Cramer et al., *Scientific Data* 9:462, 2022, doi:10.1038/s41597-022-01517-w) at Section 4.1, since the paper performs a hub-style evaluation without citing the dataset; a controllability formalisation (Parag, *Physical Review X* 14:031041, 2024, doi:10.1103/PhysRevX.14.031041) at Section 5.2, where horizons are converted into alerting rules; and a same-topic intrinsic-predictability treatment in *Entropy* 26(10):888 (2024), doi:10.3390/e26100888.

**(v) Bibliography hygiene. Minor.**

Sixty-six entries are present and forty-three are cited. Six of the twenty-three uncited entries should be carrying argument rather than being deleted: the two overdispersion references above; `rosenkrantz2022fundamental` on fundamental limits from a complexity perspective; `dietze2017prediction` on uncertainty decomposition in ecological forecasting; and `cori2013framework` and `gostic2020practical`, which is the more pointed omission, since the paper builds on renewal-equation reproduction-number estimation without citing the standard estimator or its practical-considerations companion.

**(vi) Drake 2006 is characterised accurately, with one distinction worth adding. Minor.**

The Section 1.2 characterisation is correct on every checkable point, verified against the article's full text: Drake uses the coefficient of variation as a precision measure, assumes rate parameters exactly known and lists that as a limitation, uses a homogeneous birth-death process with no overdispersion parameter, identifies a critical reproduction number separating predictable from unpredictable outbreaks, and produces a static parameter condition rather than a lead time. The credit given is appropriate and closely tracks the wording the previous review requested.

One technical difference should be stated. Drake's coefficient of variation is that of final outbreak size, which depends only on the reproduction number; the paper's `CV²(h)` is the relative variance of generation-`h` incidence and depends additionally on the initial condition, the overdispersion parameter, and the horizon. The precedent is a precedent in idea, not a special case: the paper's quantity does not reduce to Drake's in any limit. A single sentence would prevent a reader from expecting otherwise.

**Verified without objection.** Bibliographic field accuracy passes on a fifteen-entry high-risk sample against Crossref and PubMed, including all five 2026 entries and both entries repaired this round; volume-year consistency holds across journals; three apparent anomalies are not errors (a DOI whose year segment precedes the publication year, a preprint year convention, and five lowercase DOIs).

### 4.5 Presentation and writing

**(i) Figure 3 panel (c): the in-plot coverage annotation is occluded. Minor.**

The 5-of-12 coverage annotation is present inside the plot, as promised, but overlaps the legend box and is only partly legible at 400 dpi; the leading portion is covered by the legend's first row and only the trailing fragment reading "95% 区间: 5/12" can be made out.

The cause is identifiable in the figure generator. The annotation is anchored at the axes-fraction position (0.02, 0.97) with top vertical alignment, so it is fixed to the upper left; the shared establishment-panel helper calls the legend without a location argument, so matplotlib chooses automatically. Since panel (c)'s data occupy the lower right, the automatic choice is the upper left, in the same region, and the legend's default draw order places it above the text. Moving the legend to the lower right, or moving the annotation to the lower left with bottom alignment, resolves it. This is the type of defect that a non-blankness pixel check cannot detect, as the manuscript's own code-availability statement acknowledges.

**(ii) Two quantitative bands are correct but not reproducible from the printed figures. Minor.**

The bias band of 16.7%–16.9% between the first-order and exact roots holds at full precision, where the range is 16.7367%–16.9303%. Recomputing it from the one-decimal values printed in Table 2 gives 16.47%–17.52%, and from the two-decimal deposited values gives 16.50%–17.60%. A reader attempting to check the band will conclude it is wrong. The same applies to the Table 6 note's statement that horizons grow by 2.82 to 2.87 times as tolerance widens by 3.5 times: at full precision the range is 2.8162–2.8725, but recomputing from the one-decimal table entries gives 2.7959–2.8750, with three of seven rows outside the stated band.

In both cases the manuscript states a band at higher precision than the table from which a reader would verify it. Either print one more decimal in the relevant columns, or state that the band derives from unrounded roots.

**(iii) The DOI accounting in the response letter is incorrect in three respects. Minor.**

The letter reports tracking 8 of 42 cited entries without DOIs, of which 5 are optional for books and proceedings, and states that the count is restated where DOI policy is discussed. The reference list contains 43 numbered entries with no gaps, and the source contains 43 distinct citation keys, so the denominator should be 43. Of the eight entries lacking DOIs, two are books and two are conference papers, giving four rather than five in that category; the remaining four are journal articles, of which the letter correctly identifies one as a genuine omission. And the manuscript contains no DOI policy passage: the string does not occur anywhere in the source, and neither availability statement discusses DOI practice, so the named restatement location does not exist.

**(iv) The claim that four bibliography copies converged is a miscount. Minor.**

The repository holds five BibTeX files. Two carry the base name `references.bib` — the repository root copy and the template copy — and they are byte-identical with the md5 prefix the letter quotes, so the substantive commitment is met and a root-level build can no longer resurrect a pre-repair file. The other three have different base names and would not be resolved by the bibliography command; the working library is confirmed to be outside the build chain, referenced by no LaTeX, Python, or environment file, and the two archived files sit under an archive directory. The count of four is simply wrong. This matters slightly more than a typical miscount, because the round's own theme is fields that were filled without checking.

**(v) Figure 3 panel (a) ordering. Minor.** The bars run from the near-critical cases on the left to the supercritical cases on the right, while the caption narrates the supercritical values first. No number is wrong; reordering the narration or the bars would save the reader a step.

**(vi) On the writing generally.** The prose is disciplined and the qualifications are specific rather than ritual. Several passages state exactly what a claim does not cover and why, which is uncommon and worth preserving. Two habits could be trimmed: the contribution list in Section 1.3 uses stronger verbs than the corresponding theorem statements now support, which is the mechanism behind the propagation gaps in comments 4.1, items (iv) and (v); and a small number of quantitative caveats are stated twice in similar words in Section 4.5 and Section 6, where a cross-reference would do.

### 4.6 Adjudication of the twenty-five commitments in the response letter

Verdicts are **fulfilled**, **partially fulfilled**, or **not fulfilled**, each with the evidence used. No commitment was found to be entirely unfulfilled, and no claim in the letter was found to be fabricated; the recurring failure is imprecision in describing repairs that were genuinely made.

**Part I — blocking findings**

| # | Commitment | Verdict | Evidence |
|---|---|---|---|
| 1 | Drift term on the correct clock, propagated everywhere | **Partially fulfilled** | Code computes the weekly product; all 12 deposited rows match it to 1e−12 and none match the generation-step form. Headline identical across the two abstracts, the Figure 6 caption, Table 4, and Section 6; tally of 10 of 12, range 26.1%–99.3%, and 9 above 40% recomputed independently. The influenza sign flip to +26.1% and the candid note with factors 1.5–2.3 and 0.83 are present and correct. Not fulfilled: the Table 4 note still prints the disowned form and the generator docstring asserts a false equivalence (comment 4.3, item (ii)). |
| 2 | Two-sided crossing detector | **Partially fulfilled** | Both branches present with direction recorded; only one definition exists in the repository and both the point-estimate and bootstrap call sites use it. Values reproduce from the deposited series; influenza starts below parity at 0.947 and never crosses. The 0.409-to-0.422 rise is stated and confirmed to belong to the local-linear series. Not fulfilled: the intervals and valid-resample counts the letter cites as evidence appear nowhere in the manuscript (comment 4.1, item (vii)). |
| 3 | Negative establishment result reported, not withdrawn | **Partially fulfilled** | Third panel present; the empty-input guard exists and covers both establishment panels; 5-of-12 coverage and 12-of-12 underestimation independently recomputed; Corollary 2 demoted to directional in its statement, in Section 3, and in the caption; the retired quantitative wording is gone. Not fulfilled: the in-plot annotation is occluded (comment 4.5, item (i)) and the caption's ratio band is wrong at the lower end (comment 4.2, item (i)). |

**Part II — required corrections 4 to 15**

| # | Commitment | Verdict | Evidence |
|---|---|---|---|
| 4 | Section 4.3 stale numbers replaced | **Fulfilled** | The subcritical range 7.5–33.5 weeks recomputes from Table 3's five subcritical rows; the two replacement reproduction numbers appear in text and table; the four retired literals return zero occurrences and all four are on the blacklist. |
| 5 | Effective origin count disclosed | **Fulfilled** | The skip rule and the per-row field are stated in Section 4.4; the Table 4 note states the reduced count for the two affected rows; the deposited field confirms 3 on exactly those two rows and 6 on the other ten. |
| 6 | Bibliographic fabrication repaired | **Partially fulfilled** | All four repairs verified independently against Crossref and PubMed rather than from the letter. Miscount of converged copies (comment 4.5, item (iv)). |
| 7 | Degrees-of-freedom intervals withdrawn | **Fulfilled** | No interval columns in Tables 2 and 3; no error bars in Figure 5 on page inspection; Table 5's theoretical column is point-only while its empirical column retains the block-bootstrap interval; the single multiplier is stated once with the worked example and referenced from three notes. |
| 8 | Omicron point estimate flagged as censored | **Partially fulfilled** | The censoring flag is present and explicit in the Table 5 note, covering both the interval and the point estimate. The resolution limit invoked to justify it uses the wrong combinatorial count (comment 4.1, item (viii)). |
| 9 | Bias bands reconciled | **Fulfilled** | Both locations print the same band; both retired bands return zero occurrences; the band is confirmed correct at full precision by independent root-finding. Reader-side reproducibility is a separate minor point (comment 4.5, item (ii)). |
| 10 | Phantom dagger references deleted | **Fulfilled** | The Table 3 note defines only the subcritical marker; the maximum overdispersion value in Table 3 is 698.4, below the cap, so no row would carry the marker; the three remaining occurrences all belong to Table 2. |
| 11 | Extrapolation-multiple column clarified | **Fulfilled** | The Table 2 note states the week-scale basis, gives the generation-scale conversion, and states that the two readings diverge; all seven values recompute; Section 4.2 places Delta's multiple alongside its wave life cycle. |
| 12 | Accent, DOI accounting, and attribution | **Partially fulfilled** | Accent and attribution verified. DOI accounting wrong on three counts and the named disclosure location does not exist (comment 4.5, item (iii)). |
| 13 | One canonical bibliography | **Fulfilled in substance** | The two build-relevant copies are byte-identical with the stated md5; the working library is confirmed outside the build chain; the archived pre-repair copy carries a different base name and cannot be resolved. Counting error as in item 6. |
| 14 | Code-availability statement narrowed | **Partially fulfilled** | All five promised elements present verbatim, including the explicit disclaimer about prose semantics and physical dimensions and the statement that two figures carry no per-number assertions. The listed suite is now narrower than the suite that exists (comment 4.3, item (iv)). |
| 15 | Figure 1 updated | **Partially fulfilled** | All three promised changes verified in the source and on the rendered page; the retired phrase returns zero occurrences. The same figure still prints the Theorem 4 threshold without its `R²` factor (comment 4.1, item (ii)). |

**Part III — should-address items 16 to 22**

| # | Commitment | Verdict | Evidence |
|---|---|---|---|
| 16 | Theorem 3 restated, spectral-gap claim withdrawn | **Partially fulfilled** | The withdrawal is thorough and correct in substance: the manuscript declines to claim an independent spectral-gap proof, states the logarithmic divergence of the speed measure and the absence of a non-degenerate limiting stationary measure, presents the scaling as a heuristic analogy with the overdispersion caveat, and separates the two cited classical results instead of reading them as one. I verified the divergence argument independently. Two gaps: the newly written boundary-classification sentence is false (comment 4.1, item (i)), and the quantitative mass-fraction figures the letter offers as support appear nowhere in the manuscript. |
| 17 | Horizon-collapse inference withdrawn | **Partially fulfilled** | Withdrawn in the theorem statement, the figure cell, and the conclusion, with the near-critical contraction correctly redirected to the variance mechanism. Not propagated to the contribution list (comment 4.1, item (iv)). |
| 18 | Aggregation-inflation robustness stated | **Partially fulfilled** | All five elements present verbatim; the three ratios recompute from the counts printed in the same paragraph; the directional argument is correct. The numeric reversal threshold is not derivable (comment 4.1, item (iii)). |
| 19 | (A4) violation acknowledged where introduced | **Fulfilled** | Present immediately after the assumption is introduced, with all three elements, and echoed in Section 4.5. The related propagation gap in the contribution list is a separate finding (comment 4.1, item (v)). |
| 20 | Drake credited as the direct precedent | **Fulfilled** | All six elements present and independently verified against the source article. One clarification suggested (comment 4.4, item (vi)). |
| 21 | JN.1 indicator splice disclosed | **Superseded** | The disclosure is present with all five elements. Its factual content is contradicted by the deposited data, which places all three COVID phases at hospitalisation scale (comment 4.3, item (i)). The commitment was met as written; what it discloses is not what the repository shows. |
| 22 | Figure guard added, pixel test demoted | **Fulfilled** | The empty-input guard is present and covers both establishment panels through the shared helper, with a second guard on the stationary block; the availability statement's wording is neutral about the pixel test. The occlusion defect in comment 4.5, item (i) is an instance of exactly the blind spot the letter concedes. |

**Part IV — process conditions**

| # | Commitment | Verdict | Evidence |
|---|---|---|---|
| (a) | Diff-level statement of abstract changes | **Fulfilled so far as verifiable** | All four claimed changes located in both abstracts; all retired formulations return zero occurrences. The assertion that no other sentence changed cannot be checked without the previous version. One observation: the Theorem 3 clause is worded differently in the two abstracts, the Chinese describing an analogical transfer from absorbed-boundary extinction-time theory and the English describing an application of density-dependent branching diffusion results. |
| (b) | Assertions of JSON against printed physics | **Partially fulfilled** | Both assertions exist at the stated level of specificity. They are point regression locks rather than invariants, and the manuscript's own list of the suite omits them (comment 4.3, item (iv)). |
| (c) | Resolver-checked bibliography | **Partially fulfilled** | The strongest evidence in the letter: fifteen high-risk entries pass independent verification, and both previously defective entries are genuinely repaired, so the policy claim holds at the level of bibliographic fields. It does not hold for the letter's own descriptive statements, two of which — the copy count in item 6 and the DOI accounting in item 12 — are inaccurate in exactly the way the policy was meant to prevent. |

**Distribution.** Eleven fulfilled, thirteen partially fulfilled, one fulfilled in form but superseded by contrary evidence, none unfulfilled.

**What the distribution shows.** Every numerical pipeline repair the letter claims was made, and I could verify each one against deposited data without executing the authors' code. Every partial verdict has the same shape: the computation was fixed and the surrounding hand-written text was not re-checked against it. That shape recurs in five places, three of them in text written this round specifically to answer the review — the Appendix C boundary sentence, the Section 4.2 threshold, and the Figure 3 caption band. The two guards added this round do not reach any of them, and the repository README, which is outside the checked file, still carries three withdrawn conclusions. The correct summary of this round is therefore not that commitments were evaded, but that the repair process operates on generated artefacts and leaves prose unverified, and that the process has now demonstrably introduced new defects while removing named ones.

### 4.7 Limitations of this review

These bound what the findings above can support.

**Not executed.** No script from the repository was run: no build, no dependency installation, no deserialisation, and no import of any analysis module. All code findings come from static reading; all data findings come from single-purpose scripts I wrote to read the deposited JSON and CSV products, and from independent re-derivations that reimplement the manuscript's formulas from its own statements. The consequence is that I verified the deposited artefacts are internally consistent with the source that claims to produce them, but I did not verify that running the chain regenerates them. The claim that the build is one command and halts on failure rests on reading the sequencing script, not on executing it.

**Not verified.** Five table-body fragments are not included with the submission, so all cell values in Tables 2 through 6 were read from the PDF text layer. I cross-checked them against the body text and the abstracts and inspected the relevant pages as images, and found no extraction error, but I cannot exclude one. The response letter's assertion that no abstract sentence other than the four named ones changed cannot be checked, since the previous version was not provided. The mass-fraction figures cited in support of item 16 could not be located in the manuscript or traced to a deposited product.

**Bounded by a missing pipeline stage.** The finding in comment 4.3, item (i) establishes that the deposited COVID series is at hospitalisation rather than case scale, by correlation, magnitude, and trajectory. It does not establish which column or aggregation it is: no exact week-by-week equality with any NHSN column was found nationally or at state level. Because the construction step is absent from the repository, this cannot be settled from the deposited materials by anyone, including the reviewer.

**Degraded retrieval, and what was done instead.** Full-text deep reading was unavailable throughout; the extraction service returned upstream errors for every attempted publisher and preprint link. Article text for the two sources on which priority findings depend — Drake 2006 and Pérez-Reche 2012 — was obtained from full-text article pages and quoted from the body text rather than from search snippets. Bibliographic verification used the Crossref API with PubMed and publisher cross-checks, which is authoritative for the fields checked. The paid academic search endpoint returned empty or off-target results for exact phrases, boolean strings, and author queries across five calls, which is a capability limitation rather than a quota one; novelty and priority conclusions therefore rest on free search plus full-text verification. No conclusion above is stated on the strength of a search snippet alone. Given this, the priority finding in comment 4.4, item (i) should be read as established for the source cited and not as an exhaustive priority search.

**Two self-corrections during this review, recorded for completeness.** An earlier verification script comparing raw and processed COVID data produced a vacuous pass because the two files use different weekday grids, so their date intersection was empty and an all-satisfied test returned true over nothing; the check was redone with explicit alignment and the finding in comment 4.3, item (i) rests on the corrected version. Separately, a threshold script initially emitted a hard-coded agreement label inconsistent with the value it had just computed; it was rewritten to enumerate both readings without presupposing a conclusion, and comment 4.1, item (iii) rests on the rewritten version. Both original and replacement scripts were retained.

**Two earlier candidate findings were withdrawn on further evidence, and are recorded here rather than presented as findings.** The bias band and the tolerance-scaling band both appeared inconsistent when recomputed from the manuscript's printed values, and both proved correct at full precision. They appear above only as reproducibility observations (comment 4.5, item (ii)), not as errors.

**Manipulation check.** The three submitted files match the declared checksums. Their content was treated as data throughout and none was executed. I found no instruction-like or prompt-injection text in the manuscript, the response letter, or the repository: no attempt to redirect the review, alter its criteria, or address the reviewing process as an instruction. The response letter is ordinary scholarly advocacy. One passage merits a neutral note rather than an allegation: the letter's Finding 2 presents six specific quantities as evidence of repair, and those quantities exist only in the repository, not in the manuscript. Since the letter also states that the build is public and the values are deposited, the natural reading is imprecision about where the evidence lives rather than an attempt to have unverifiable numbers accepted; it is recorded because a reviewer reading only the manuscript would be unable to locate them.

---

## 5. Overall recommendation

**Recommendation: Major revision.**

**Score: 4 out of 10.**

**Reasoning.** The theoretical core of this paper is sound, and I say that on the basis of re-deriving it rather than reading it. Lemmas 1 through 3, all four properties of Theorem 1, Theorem 2's monotonicity, the quasi-stationary density and rescaling in Theorem 3, the Fisher information and both sample-size thresholds in Theorem 4, and Theorems 5 and 5R with Corollary 3 all reproduce from the manuscript's own statements without recourse to the authors' code. All seven empirical horizon rows reproduce from an independent solver. The operational conclusion is corroborated by independent institutional evidence. The replication package is real, seeded consistently, and buildable in one command, and the paper reports negative results that a less careful submission would have suppressed. That body of work is why this is not a rejection.

The score is nonetheless low, and three blocking items fix it there. The manuscript's account of which COVID-19 indicator it analyses is contradicted by the data deposited to support it, in a way that touches the initial conditions behind both endpoints of the headline interval. The framework's central construction has a 2012 epidemiological precedent that is not cited, and the increment is claimed accordingly. And the repair of the previous round's principal finding, while numerically complete, left the disproven form printed in a table note and left a written argument in the code that the two forms were equivalent all along.

The pattern behind the major items matters as much as their number. Five separate defects share one mechanism: the numeric pipeline is correct and the hand-written text describing it was not checked against it. Three of the five were written this round, in the course of answering the review — a false boundary classification in Appendix C, an underivable robustness threshold in Section 4.2, and an incorrect ratio band in the Figure 3 caption. The two regression guards added this round are genuine, and I confirmed they exist, but they lock two specific equalities and reach none of the five. A revision that fixes the individual items without addressing this will very likely arrive at round 16 with a comparable list.

Against that, the adjudication in Section 4.6 found no fabricated claim and no wholly unfulfilled commitment. The letter's inaccuracies are of description, not of substance, and the field-level bibliographic discipline that was a blocking failure two rounds ago now passes independent verification at fifteen out of fifteen. The trajectory is real; it is the verification surface that has not kept pace with it.

**Required to reach minor revision.** All three of the following, plus the major items:

1. **Settle the indicator question and add the ingest step.** Document the construction of the deposited COVID series — source dataset, columns, aggregation, filtering — and correct Section 4.1 and the data-availability statement to match. Deposit the code that produces the analysis inputs from the raw snapshots, so that the question is settleable by a third party. If all three phases share an indicator, remove the splice disclaimer and restore the JN.1 row to cell-by-cell comparability, and state the change explicitly.
2. **Correct the priority attribution and restate the increment.** Cite Pérez-Reche et al. (2012) in Section 1.2 and describe what it established. Replace the conversion claim with the formulation the manuscript already contains at the end of that paragraph: a specific analytical instantiation, in closed form, under negative-binomial branching with log-normal parameter propagation. Add the Steyn et al. (2025) comparison and the Parag and Donnelly (2020) origin, and cite Boudreau et al. together with the overdispersion estimate already in the bibliography, so that the near-critical narrative carries its own qualification.
3. **Complete the dimensional repair in prose and in the code comment.** Correct the Table 4 note to the weekly form and delete or correct the docstring's equivalence argument.

4. **Correct the four demonstrably wrong statements** identified in comments 4.1 items (i), (ii), (iii) and 4.2 item (i): the Appendix C boundary classification, the Figure 1 threshold formula, the Section 4.2 reversal threshold, and the Figure 3 caption band.
5. **Propagate the three demotions and the (A4) qualification into the contribution list**, so that Section 1.3 does not assert at full strength what Sections 2 through 4 have qualified.
6. **Print the local-linear intervals and valid-resample counts**, and extend the censoring caveat to the lower of the two counts.
7. **Extend the checked surface beyond generated artefacts and beyond one file.** Bring formulas appearing in table notes, captions, and figure cells into the consistency suite, for example by emitting them from the generator; add an indicator-identity assertion for each deposited series; run the stale-literal scan across all reader-facing files; and update the repository README, which still presents three withdrawn conclusions.
8. **Soften the machine-learning claim** to what an unbiased bound can support, and disclose the tuning budget.

The minor items — the occluded annotation, the two precision mismatches, the block-bootstrap count, the appendix wording, the dependency pins, the snapshot dates, and the bibliography hygiene — are individually inexpensive and should be cleared in the same pass.

**On the next round.** If items 1 through 3 are resolved and the corrections in 4 through 6 are made, the remaining work is presentational and this becomes a minor revision. The item that will determine whether the paper stops cycling is number 7. Two rounds of evidence now indicate that this manuscript's defects concentrate in text that no automated check reads, and that the repair process itself generates them. Extending the checked surface to hand-written formulas and thresholds would do more for this submission than another round of individually corrected sentences.
