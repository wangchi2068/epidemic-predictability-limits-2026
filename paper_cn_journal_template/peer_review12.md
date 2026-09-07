# Peer Review of “Predictability Horizons, Fundamental Limits, and Empirical Analysis of Epidemic Transmission Dynamics”

## 1. Short Summary

This manuscript develops a two-layer account of epidemic predictability. The first layer derives a tolerance-dependent forecast horizon under a negative-binomial branching-process model by decomposing relative forecast error into intrinsic population stochasticity and propagated uncertainty in the reproduction number. The manuscript then extends the analysis to quasi-stationary finite-population behavior, Fisher-information and Cramér–Rao limits, and time-varying transmission. The second layer compares the theoretical horizon with rolling out-of-sample forecast performance on finalized CDC surveillance series for selected COVID-19, influenza, and RSV phases.

The topic is important, the central question is clearly posed, and the manuscript contains substantial mathematical and computational work. Several parts withstand independent scrutiny: the branching-process moment recursion and closed-form intrinsic coefficient of variation are correct; the reported roots in Tables 2, 3, and 6 can be reproduced when the printed parameters are taken as inputs; three core scripts execute deterministically in a sandbox and reproduce their committed JSON outputs byte-for-byte; the Table 4 intrinsic, drift, and parameter-propagation components can be independently recalculated; and the persistence/local-linear benchmark construction and threshold interpolation are reasonable in principle.

However, the present revision is not publishable. The most consequential empirical quantities do not have a reproducible generation path: the Table 2 confidence intervals and the Table 4 observed total-error column are hard-coded, and the methods described for them do not match the available code. The PDF embeds an outdated Figure 7 that contradicts Table 5 and the committed rolling results. The data-to-parameter chain remains incomplete and the main horizon calculations use pre-entered publication parameters rather than the fitted values. There are also substantive theoretical/numerical inconsistencies, including the RSV Cramér–Rao comparison, the reported Theorem 5R simulation behavior, and the stated error domain of Corollary 1. Finally, the bibliography includes at least one highly likely nonexistent citation and several materially incorrect records.

My assessment is based on the supplied 42-page PDF, the response letter, and the repository at commit `85d7a84b874fbefeeaeb388c8b6143018d34b56c`. I treated the response letter as a list of claims to verify, not as evidence. I did run sandboxed smoke tests of `extract_cdc_data.py`, `prospective_rolling.py`, and `reproduce_all_tables.py`, and I independently recalculated selected formulas and table entries. I did not rerun the high-throughput Monte Carlo or machine-learning experiments. LaTeX recompilation could not be completed in the available environment because the source hard-codes unavailable Windows CJK fonts. The automated figure-QA tool also did not complete because `pdftotext -bbox` produced malformed XML; review of rendered pages is therefore not equivalent to a passed automated figure gate.

## 2. Strengths

1. **The research question is important and well motivated.** Separating uncertainty that is intrinsic to transmission from uncertainty induced by parameter estimation is useful for both forecast evaluation and public-health interpretation.

2. **The principal branching-process derivations have a sound core.** The moment recursion, the closed-form expression for intrinsic relative variance, and the tolerance-root calculation are algebraically coherent under the stated assumptions. The monotonicity argument is broadly valid, subject to the non-degeneracy qualifications noted below.

3. **Several numerical results are genuinely reproducible.** Given the printed parameter values, the exact roots in Tables 2, 3, and 6 agree with independent Gauss–Hermite quadrature and root finding. The intrinsic, time-varying drift, and parameter-error columns of Table 4 also agree with independent calculations to the printed precision.

4. **The repository contains meaningful executable material.** The data-extraction, rolling-evaluation, and table-reproduction scripts run successfully and deterministically in a separate sandbox. Their regenerated JSON files match the committed outputs. This is a valuable foundation, even though the current scripts do not yet generate all headline results.

5. **The empirical benchmark is not obviously biased against the baselines.** Persistence and local-linear extrapolation are implemented on comparable windows, and the linear interpolation used to define threshold crossings is transparent.

6. **The manuscript acknowledges important limitations.** The discussion recognizes the use of finalized rather than real-time vintages, the small number of forecast origins, the omission of interval scores, and several model restrictions. These acknowledgments should be propagated more consistently into the abstract and conclusions.

7. **The health-equity discussion is thoughtful.** The argument that sparse surveillance can shorten an estimated predictability horizon and thereby reinforce under-allocation of resources is a substantive public-health contribution. The recommendation to separate predictability assessment from minimum resource guarantees is well taken.

8. **Several requested corrections were made successfully.** The broken in-text citation is repaired, the CV² maximum is consistently reported as no more than 1.01%, the spurious `±1.82%`, `±0.4 week`, and `0.0574` remnants are absent from the manuscript, Table 5 matches the committed rolling-results JSON, the MLP ratio is consistently reported as 6.69 for the tested model, and both Sections 5.1 and 5.2 contain non-prescriptive disclaimers.

## 3. Weaknesses

The main weakness is not a lack of analysis but a loss of synchronization among the manuscript, response letter, code, data, figures, and cached outputs. This affects the evidentiary status of the headline findings.

1. **Headline empirical results are not generated by the submitted code.** Table 2 confidence intervals are literal values that do not match the interval output of `extract_cdc_data.py`. The observed total errors in Table 4 are likewise literals with no identified generator. The percentages highlighted in the abstract and conclusion depend on these values.

2. **The submitted PDF is internally contradictory.** Figure 7 reports old crossing values, while Table 5, the text, and the rolling-results JSON report a different set. The old Omicron value also preserves the very theoretical/empirical reversal the revision claims to have removed.

3. **The data provenance and parameter-estimation chain is incomplete.** Raw CDC files, complete source URLs, download dates, checksums, and raw-to-processed transformation code are absent. The extraction script reads processed files and uses hard-coded publication parameters for the main calculations.

4. **Some central theoretical-to-empirical interfaces are incorrect or overstated.** The printed Cramér–Rao sample-size formula omits a factor, the RSV comparison mixes independent-cluster requirements with a weekly mean or five-week total, and the “theoretical envelope” claim is contradicted by the influenza row of Table 5.

5. **Some numerical validation statements conflict with the committed results.** The text’s description of Theorem 5R simulation behavior is opposite to the pattern in the cached JSON. The declared approximation-error bound for Corollary 1 is not supported over the stated parameter domain.

6. **The literature record is not yet reliable enough for publication.** The bibliography contains damaged records, material metadata errors, 33 uncited entries, and at least one citation whose title, authors, pagination, and DOI could not be verified across multiple independent search routes.

7. **The response letter repeatedly claims complete resolution where the submitted artifacts show otherwise.** This makes the revision difficult to audit and raises concern about the quality-control process. I do not infer intent, but the next submission must use generated artifacts and exact source locations rather than broad completion claims.

## 4. Detailed Comments

### Major Comments

#### Major Comment 1 — Table 2 confidence intervals are not reproducible

**Location:** Section 2.1 and its uncertainty description (PDF pp. 5–6); Section 4.1 and Table 2 (PDF pp. 22–24); Figure 5 (PDF p. 24); abstract and conclusion; `scripts/extract_cdc_data.py`; `scripts/reproduce_all_tables.py`.

**Issue and reason:** The manuscript states that the 95% confidence intervals were obtained using 2,000 parametric-bootstrap replicates with a fixed seed. No such resampling procedure appears in the submitted scripts. `extract_cdc_data.py` instead forms a Student-t interval for `R` and solves the horizon at the interval endpoints. Its results do not match Table 2: for example, the script reports approximately 18.1–19.9 weeks for Delta, whereas Table 2 reports 8.9–20.0 weeks. The printed intervals are supplied as literal tuples in `reproduce_all_tables.py`.

**Impact:** These intervals feed Figure 5, the theoretical intervals in Table 5, the abstract’s reported 1.8–20.0-week union, and the conclusion. They cannot presently be treated as inferential results because neither their generator nor their sampling model is available.

**Required revision:** Implement the stated parametric bootstrap end to end, including the fitted sampling model, all parameters varied, dependence assumptions, seed, failure handling, and percentile or pivotal interval rule. Generate Table 2, Figure 5, Table 5’s theoretical intervals, and the corresponding prose from a single machine-readable output. If the intended method is instead the existing t-endpoint calculation, remove the bootstrap claim and regenerate all intervals consistently. Add tests that compare the generated values with the manuscript tables and fail on divergence.

#### Major Comment 2 — Table 4’s observed total error and headline decomposition percentages have no generator

**Location:** Section 4.3, Table 4, and Figure 6 (PDF pp. 25–27); Chinese and English abstracts; conclusion; `scripts/error_budget.py`; `scripts/reproduce_all_tables.py`; cached `error_budget_4term.json` and `error_budget_recomputed.json`.

**Issue and reason:** The intrinsic, drift, and parameter-propagation components in Table 4 are reproducible from the printed inputs. The “observed total relative mean squared error” column is not. Its values appear as literals in the table-generation script, and no submitted script produces them from forecast errors and the normalization stated in the table note. The `observed` quantity in `error_budget.py` is log-scale RMSE squared and differs substantially in magnitude; for Delta at one week it is about 0.1891, whereas Table 4 reports 0.0213. Two cached JSON files contain the table totals, but no code in the repository writes those files. In addition, `error_budget.py` introduces an unexplained cross term with coefficient −0.05 and clips residual misspecification at zero.

**Impact:** Every reported contribution share depends on this denominator, including the headline 5.9%–27.4%, 72.6%–94.2%, and up-to-88.7% claims. Until the observed-error column is regenerated transparently, these percentages are unsupported.

**Required revision:** Provide a script that starts from the submitted forecast-origin predictions and observations, applies the exact printed normalization, and generates every Table 4 row and uncertainty estimate. Reconcile or rename the incompatible log-scale measure in `error_budget.py`. Remove the −0.05 term unless it is derived or externally justified, and report negative residuals rather than clipping them, because negative closure is itself an important diagnostic. Make Figure 6 and all percentage statements consume the generated table output rather than duplicated literals.

#### Major Comment 3 — The data-to-parameter path is not closed, and the time-scale transformation is inconsistent

**Location:** Section 2.1 (PDF pp. 5–6); Table 2; data-availability statement (PDF p. 35); `scripts/extract_cdc_data.py`; `data/processed/`; repository documentation.

**Issue and reason:** The response claims that the extraction script reads raw CDC files, applies date slices, fits regressions with `scipy.stats.linregress`, converts weekly growth to generation-scale `R`, and asserts equality with Table 2. The submitted repository has no `data/cdc_raw/`; it contains only three processed long-form series and no complete raw-to-processed transformation. The script uses `np.polyfit`, has no `assert`, and calculates the published horizons from hard-coded `R_pub`, `dR_pub`, `k_pub`, and `I0_pub` values rather than the fitted estimates. Several fitted and published values differ. The manuscript presents the first-order relation involving `μg/7`, while the response gives an exponential expression; the script uses `R_fit = 1 + slope` without the `μg/7` factor. Plausible conventions produce materially different Delta horizons (approximately 13.5, 15.2, 18.4, or 20.1 weeks).

**Impact:** The main theoretical-horizon values are not shown to arise from the deposited surveillance data under a uniquely specified time-scale convention. Because the choice changes a headline result by nearly 50%, this is not a minor implementation detail.

**Required revision:** Deposit or programmatically retrieve immutable raw data, and provide exact source URLs, dataset/version identifiers, retrieval dates, checksums, and the complete transformation to each processed series. Define whether the fitted slope is per week, per day, or per generation. Implement one mathematically justified conversion for both the estimate and its uncertainty, and use the resulting fitted quantities to generate the main table. If calibrated publication parameters are intentionally substituted, label them as such and provide the calibration procedure. Add assertions or regression tests that compare data-derived parameters and manuscript values. Report sensitivity to the alternate defensible time-scale convention in the abstract or main results, not only in a methods aside.

#### Major Comment 4 — Figure 7 is stale, and the rolling-evaluation protocol differs from the manuscript

**Location:** Section 4.4, Figure 7, and Table 5 (PDF pp. 27–29); `main.tex` figure include near the Section 4.4 figure; `scripts/prospective_rolling.py`; `reports/prospective_rolling_results.json`; the two copies of `fig_oos_skill_decay.png`.

**Issue and reason:** The PDF embeds the copy under `reports/figures/`, whose legend gives crossings of roughly 4.5, 4.1, and 3.8 weeks. Table 5, the prose, and the rolling-results JSON give Delta 3.52, Omicron 1.82, and influenza 5.34 weeks. A newer image with those values exists elsewhere but is not the file included by the manuscript. The code also evaluates horizons 1–8 rather than the stated 1–10 weeks; resamples six origins independently rather than using the stated four-week block bootstrap; and implements persistence and local-linear baselines but not the claimed seasonal-naive baseline. The text does not state that 1,000 resamples are used.

**Impact:** The paper contains mutually exclusive empirical results. The stale Omicron legend also retains an empirical crossing above the 2.9-week theoretical horizon, contrary to the claimed resolution. The iid resampling is particularly problematic because adjacent weekly origins have overlapping future targets, so the stated standard errors may be too small.

**Required revision:** Make one script generate the rolling JSON, Figure 7, Table 5, and their captions into the exact paths consumed by LaTeX. Choose and document either 1–8 or 1–10 weeks. Implement dependence-aware resampling at the level justified by the origin structure, or provide a defensible alternative such as a moving-block procedure and explain the effective sample size. Implement the seasonal baseline or delete every claim that it was evaluated. Report interval estimates rather than only `estimate ± SE`; for Omicron, explicitly discuss that the current 95% interval spans the full evaluated range. Add a build check that fails if duplicate figure names differ across output directories.

#### Major Comment 5 — The RSV Cramér–Rao argument contains a formula error and an invalid comparison

**Location:** Theorem 4 and Section 4.1 (PDF pp. 15–16 and 22–23); Table 2; `scripts/extract_cdc_data.py`; `scripts/real_data_common.py`.

**Issue and reason:** The manuscript prints `C_req = (1/R + 1/k)/δR²`, while the code that generates 5,826 and 15,332 uses `(1/R + 1/k)/(δR/R)²`, which includes an additional factor of `R²`. The latter follows from the stated relative-variance bound; the printed formula would produce about 3,787 and 10,420. A third formula appears in `real_data_common.py`. The subsequent comparison is also not like-for-like: 4,409 and 1,868 are five-week window means from `seg.mean()`, not cumulative case counts. The five-week totals are 22,047 and 9,341. Under that aggregation, the 2024–25 required count is below rather than above the observed total. Moreover, reported cases are not automatically equivalent to independent transmission clusters.

**Impact:** The current claim that both RSV seasons violate an information-theoretic requirement is not established. The long mathematical roots may still be operationally implausible and reasonably truncated by season length, but the submitted quantitative proof of that proposition is not valid.

**Required revision:** Derive `C_req` once from Theorem 4, define whether `δR` is absolute or relative, and use the same tested function everywhere. Define the observation unit represented by `C`, explain how surveillance cases map to independent clusters, and compare counts over the same estimation window. Recompute the conclusion for both seasons and distinguish a model-based seasonal truncation from a demonstrated Cramér–Rao violation.

#### Major Comment 6 — Theorem 5R validation and Corollary 1 accuracy claims conflict with the submitted numerical evidence

**Location:** Sections 2.3 and 2.7; numerical validation in Section 3 (especially PDF pp. 19–21); `reports/verify_t5R.json`; `reports/verify_tvR.json`; the code and discussion associated with Corollary 1.

**Issue and reason:** For Theorem 5R, the manuscript states that the ratio at `φ = 0.8, h = 1` is about 0.58 and then rises toward 0.92–1.08 for `h = 4, 8`. The committed JSON gives approximately 0.982 at `φ = 0.8, h = 1`; the `h = 4, 8` values lie around 0.581–0.741 and decrease rather than recover. The broader time-varying report spans about 0.859–1.440, not the stated 0.98–1.03. Separately, the near-critical approximation formula in Corollary 1 is algebraically correct as the positive root of its approximate quadratic, but its claimed error bound does not hold over the stated domain. Independent grid checks found errors far above 13.6% for `k ≥ 0.5` and `|R−1| ≤ 0.2`, and still above that threshold in a much narrower near-critical band.

**Impact:** These are not stylistic disagreements: the text describes trends opposite to the submitted results and gives an unsupported approximation domain. They weaken the numerical validation of two theoretical claims.

**Required revision:** Rerun these experiments from a clean environment, generate plots and summary text directly from the outputs, and determine whether the formulas, simulation initialization, conditioning, or prose is wrong. For Corollary 1, define an empirically and analytically defensible validity region and report maximum/quantile errors over a predeclared grid. Reframe `h/k` as a conditional asymptotic approximation rather than a universal irreducible lower bound unless a proof covering the stated regime is supplied. Also clarify that Monte Carlo recovery of the sample-mean Cramér–Rao variance is a numerical sanity check, not a “strict validation” of the theorem.

#### Major Comment 7 — The claimed theoretical envelope is contradicted by Table 5 and uncertainty is overinterpreted

**Location:** Section 4.4 and Table 5 (PDF pp. 28–29); Sections 5.1–5.2; abstract and conclusion.

**Issue and reason:** Table 5 gives an influenza theoretical horizon of 5.1 weeks and an empirical crossing of 5.34 weeks, a ratio of 0.95. This directly contradicts categorical statements that the theoretical horizon provides an upper envelope for every pathogen and “robustly” bounds operational usefulness. For Omicron, the point estimate is 1.82 weeks with SE 2.25 weeks and a reported 95% interval spanning 1–8 weeks. Calling this “highly consistent” with a 2.9-week theoretical horizon is much stronger than the data permit. Finalized, backfilled series also do not establish real-time operational performance.

**Impact:** The central two-layer interpretation is stated as a general empirical finding despite only three comparisons, one point estimate in the opposite direction, and very wide uncertainty in another.

**Required revision:** Present the comparison as exploratory. State that two point estimates fall below the theoretical horizon and one slightly exceeds it, with uncertainty too large for a general envelope claim. Predefine what empirical result would support or falsify an envelope, propagate uncertainty from both layers, and avoid treating finalized-vintage backtests as estimates of attainable real-time performance. A larger, prospectively versioned evaluation would be needed to support a general operational-bound conclusion.

#### Major Comment 8 — Assumptions and estimands need tighter qualification

**Location:** Assumptions A1–A4 and Theorems 1–3 (PDF pp. 6–15); Section 4.4; limitations.

**Issue and reason:** The additive decomposition is valid when the cross term vanishes under A4, but “orthogonal” is stronger and potentially misleading. Non-overlap between estimation and forecast windows does not imply independence when both share latent epidemic state, interventions, reporting processes, or autocorrelated environment. The manuscript mentions an empirical perturbation below 1.5%, but no corresponding script or result was located. Theorem 2’s strict monotonicity statement omits non-degeneracy conditions. The intrinsic-CV saturation statement needs an explicit `R > 1` qualifier because the manuscript also includes subcritical phases. The reflecting-boundary diffusion in Theorem 3 is not automatically the quasi-stationary distribution of the original absorbing process. Finally, normalization by the squared mean can diverge near extinction and should not be casually interpreted as a variance “share.”

**Impact:** Readers may infer a broader theorem than has been established and may apply the decomposition in settings where shared latent variation creates a nonzero covariance term.

**Required revision:** Replace “orthogonal” with “additive under A4,” display the covariance term before imposing A4, and either provide the claimed 1.5% sensitivity analysis or remove it. State all non-degeneracy and supercriticality conditions explicitly. Present the reflecting-boundary construction as an approximation to quasi-stationary behavior unless an error result is supplied. Clarify the estimand and interpretation in near-extinction/subcritical regimes.

#### Major Comment 9 — Novelty attribution and bibliography integrity require a full correction

**Location:** Introduction and Related Work (PDF pp. 2–4); Table 2 notes; references (PDF pp. 36–42); `references.bib`.

**Issue and reason:** The manuscript’s strongest novelty language is not sufficiently qualified. Petchey et al. define a forecast horizon as the first crossing of an application-relevant proficiency threshold, which is operationally very close to the manuscript’s first crossing of an error tolerance. The defensible contribution is the analytical instantiation under the specified branching-process assumptions, not invention of the threshold-horizon concept. Penn et al. already distinguish aleatoric and epistemic uncertainty and permit negative-binomial offspring distributions, although they do not derive this manuscript’s cross-source sum and tolerance root. Parag and Donnelly provide quantitative detection-delay limits, which differ from a multi-step forecast horizon but should be acknowledged. Drake’s branching-process analysis of forecast precision is directly relevant and is present in the bibliography but not cited. Relevant public links include https://pmc.ncbi.nlm.nih.gov/articles/PMC11041706/ , https://pmc.ncbi.nlm.nih.gov/articles/PMC9022826/ , https://www.biorxiv.org/content/10.1101/013441v2.full , and https://pmc.ncbi.nlm.nih.gov/articles/PMC1288026/ .

More seriously, the bibliography is not reliable. The `taylor2016stochasticity` record could not be found by exact-title, author/topic, journal-issue, Crossref, web, or academic-index searches; its DOI returns no record and its pages do not fit the stated issue. It should be treated as unverified and removed unless the authors provide the source. The `suez2026baseline` record uses an incorrect author forename, a different title, and a nonexistent identifier; the likely real work has DOI https://doi.org/10.64898/2026.03.18.26348748 . The Petchey BibTeX record is syntactically damaged, causing the rendered reference to omit journal, volume, pages, and DOI. The Chan record mixes a 2026 journal publication with a 2024 preprint DOI; the journal version is https://doi.org/10.1038/s41598-026-46596-6 . Other checked records have incorrect author names, article numbers, issues, or pages. The repository contains 99 entries, the manuscript cites 66, 33 are orphaned, and the README says there are 48 verified entries.

**Impact:** An unverifiable citation is used to support a novelty claim, and incorrect metadata prevents readers from locating sources. This alone requires correction before the work can enter the scholarly record.

**Required revision:** Audit every cited record against Crossref, PubMed, the publisher, or another authoritative source. Remove any record that cannot be verified and rewrite claims it supported. Separate preprint and journal versions rather than combining fields. Prune unused entries or clearly separate a working library from the manuscript bibliography. Recast novelty as a specific analytical extension and cite the closest prior work, including Drake. Correct generation-interval attributions: Park’s Omicron estimate is based on Dutch transmission-pair data rather than a US household cohort; Hart does not support an Omicron intrinsic interval of 3.4 days; and Chan’s XBB estimate should be labeled as a proxy assumption when applied to JN.1.

#### Major Comment 10 — The manuscript, repository, and response need a single-source-of-truth workflow

**Location:** Throughout the response letter; manuscript source; duplicate figure directories; table scripts; README; data and code availability statements.

**Issue and reason:** The response states that numerous items were “completely” or “strictly” resolved, yet the submitted artifacts show otherwise: six of seven stated windows differ from the manuscript/code; Table 2 has no date column; `data/cdc_raw/`, bootstrap code, and extraction assertions are absent; old Figure 7 remains embedded; and language said to be removed remains in the PDF. Multiple figure directories contain different files with the same names. This pattern appears to result from manual duplication and incremental patching rather than one reproducible build graph.

**Impact:** Even correct calculations cannot be evaluated reliably when the publication artifact may consume stale files or prose not tied to outputs. Continued line-by-line patching is likely to create further contradictions.

**Required revision:** Rebuild the submission around one manifest and one command that: records immutable input hashes; derives processed data; estimates parameters; produces all JSON results; generates every table and figure into one canonical directory; compiles the manuscript; and runs consistency tests against printed claims. The response should cite exact revised page/line locations and generated artifact names, avoid superlatives, and distinguish implemented changes from planned or unverified ones. The clean build should fail on hard-coded headline values, duplicate divergent figures, missing provenance, or manuscript/output mismatches.

### Minor Comments

#### Minor Comment 1 — Align repeated numerical summaries

**Location:** Numerical-validation text on PDF pp. 19–21 and conclusion pp. 33–34.

**Issue and reason:** The MLE/CRB ratio is reported once as 0.995–1.002 with mean 1.000 and elsewhere as 0.996–1.002 with median 1.001. The cached eight scenarios have a minimum near 0.995589 and median near 1.000010. Residual-error ranges also alternate between 72.6%–94.2% and “up to 95.4%.”

**Impact:** Small discrepancies reduce confidence because they occur in text presented as precision validation.

**Action:** Generate all repeated summaries from the same result file and use one definition and rounding rule throughout.

#### Minor Comment 2 — Explain parameter differences between Tables 2 and 3

**Location:** Tables 2 and 3 (PDF pp. 24–25).

**Issue and reason:** The same named phases use different `k` and `I0` values; for example, influenza 2022–23 uses `k = 50.2, I0 = 3,116` in Table 2 and `k = 38.6, I0 = 21,568` in Table 3. Omicron likewise uses different `k` values while producing the same rounded horizon.

**Impact:** The horizon’s low sensitivity to these inputs hides a definition or data-selection inconsistency.

**Action:** Use one parameter set or label the tables as using different estimands/windows and explain why.

#### Minor Comment 3 — Correct `I0` and origin-count terminology

**Location:** Section 2.1, Table 4 notes, and limitations.

**Issue and reason:** The code defines `I0` using the mean of five weekly observations, while the text describes an effective daily incidence level. The limitations and Table 4 refer to `M = 5`, whereas the rolling code and JSON use six origins per wave.

**Impact:** Units and sample sizes are easy to misinterpret.

**Action:** State `I0` in the units actually used and make all origin counts agree with generated metadata.

#### Minor Comment 4 — Align the Chinese and English abstracts

**Location:** Chinese abstract on PDF p. 1 and English abstract on p. 36.

**Issue and reason:** The English abstract omits several Chinese-abstract quantities and qualifications, including the no-more-than-1.01% result, the RSV roots and caveat, and the pathogen-specific crossings, while introducing “up to 95.4%.”

**Impact:** Readers receive materially different summaries depending on language.

**Action:** Use a shared claim checklist and make the two abstracts semantically equivalent, while keeping both concise.

#### Minor Comment 5 — Remove residual overstatement and duplicated prose

**Location:** PDF pp. 2, 3, 10, 17, 19, 21, 29, 31, 32, and 34.

**Issue and reason:** Terms equivalent to “physical hard upper limit,” “first principles,” “objective physical yardstick,” “physical-mechanism ceiling,” and “strict validation” remain. A sentence describing the empirical proxy for time-varying transmission is duplicated on p. 17.

**Impact:** The language exceeds the conditional model result and the duplication suggests incomplete source cleanup.

**Action:** Use “model- and tolerance-dependent error horizon” or similarly scoped wording, and remove the duplicate sentence.

#### Minor Comment 6 — Qualify generation-interval labels

**Location:** Table 2 notes and related sensitivity discussion.

**Issue and reason:** Credible intervals and confidence intervals are conflated; intrinsic, realized forward, and household generation intervals are placed side by side without sufficient warning; the RSV source supports a household-estimated generation interval but not necessarily the precise “forward” label used.

**Impact:** Time-scale inputs can appear more comparable than they are.

**Action:** Label each estimand, study population, geography, and uncertainty type explicitly; treat cross-variant substitutions as assumptions with sensitivity analyses.

#### Minor Comment 7 — Improve repository and build portability

**Location:** `main.tex`, environment files, README, and code-availability statement.

**Issue and reason:** The LaTeX source hard-codes a Windows CJK font set and did not compile in the review environment. The README’s installation example omits `torch` even though it is in the environment file. The claim of an approximately 15-minute “full reproduction” should specify which simulations and ML jobs it includes.

**Impact:** Independent users cannot reproduce the PDF with the documented instructions.

**Action:** Provide a container or portable font configuration, test the documented command in CI, and publish expected run times and resource needs by stage.

#### Minor Comment 8 — Distinguish project QA from journal formatting requirements

**Location:** Manuscript formatting and source.

**Issue and reason:** Automated manuscript QA reports numerous manual-bold and font/style findings. Some may reflect the target journal template rather than scientific defects, while others may be unintended.

**Impact:** It is unclear which typography is deliberate and which is accidental.

**Action:** State the authoritative journal style, remove unnecessary manual formatting, and validate the final PDF against that style rather than relying on undocumented overrides.

### Verification of the Previous-Round Response

The statuses below reflect the current PDF and fixed repository commit, not the response letter’s self-assessment.

#### Core acceptance conditions

| Previous condition | Status | Verification |
|---|---|---|
| 1. Real rolling evaluation, per-origin outputs, corrected Figure 7/Table 5, defensible uncertainty | **Partially resolved** | The rolling script and per-origin JSON exist, and Table 5 matches the JSON. The PDF embeds an old Figure 7; the horizon range, bootstrap method, and claimed baselines differ from the implementation; Table 2 and Table 4 uncertainty generation is still missing. |
| 2. Clarify weekly/generation time units and implement the conversion | **Partially resolved** | The manuscript adds a first-order discussion and calendar conversion. The response’s exponential relation is absent from the PDF, the code uses `1 + slope` without `μg/7`, and headline values remain convention-sensitive. |
| 3. Correct `δR` estimation and uncertainty; add a valid RSV CRB analysis | **Partially resolved** | `df = 3`, `t(3)`, and the RSV discussion are present. The main column still uses the residual-mean SE, the claimed bootstrap is absent, and the CRB formula/comparison are inconsistent. |
| 4. Provide exact windows, raw-data provenance, true extraction, assertions, and dependencies | **Unresolved** | The `torch` dependency was added, but the table lacks dates; six stated response-letter windows disagree with the manuscript/code; raw data, source manifest, cleaning code, and assertions are absent; main results use literal parameters. |
| 5. Unify numerical claims, moderate interpretation, and repair citations | **Partially resolved** | Several numerical remnants and the broken in-text citation were fixed. Overstated terminology, a duplicate sentence, bibliography corruption, metadata errors, and unverifiable references remain. |

#### Items resolved

The following prior items are substantively resolved in the current artifacts: W-M4 (CV² maximum), W-M6 (removal of the obsolete precision statement and presence of short/long-horizon ranges), W-m3 (population-size scaling in Theorem 3), W-m4 (the `1−φ²` first-step variance relation), W-m7 (Table 6’s 2.85–2.91 multiplier), W-m12 (MLP ratio 6.69), W-m13 (removal of `0.0574` from the manuscript), D1 (broken citation repaired), D6 (Wesselkamp pagination), D8 (Table 6 note), D10 (`torch` added to the environment), D12 (Table 5 agrees with the rolling JSON), D13 (obsolete `±1.82%` removed), and D14 (non-prescriptive statements in both requested sections).

#### Items partially resolved

The following have meaningful changes but remain incomplete or inconsistent: W-M1–W-M3; W-M5; W-M7–W-M8; W-M10–W-M14; W-m5–W-m6; W-m10–W-m11; W-m15; and D2–D5 and D11. Important examples are the time-scale explanation without matching code, the RSV discussion with mismatched formulas/units, corrected Table 5 but stale Figure 7, corrected authors displayed for Petchey but a damaged rendered record, and two non-prescriptive statements whose exact wording differs from the response but whose substance is adequate.

#### Items unresolved

The following remain unresolved: W-M9 (overstated “hard physical”/“first-principles” language), W-m1 (the claimed 2,000-replicate parametric bootstrap), W-m2 (the stated approximation-error range), W-m14 (bilingual abstract equivalence), D7 (removal of “strict validation” and related wording), and D9 (raw-data extraction and assertions). Core acceptance condition 4 is therefore also unresolved.

#### Items not verifiable from the supplied history

W-m8 and W-m9 concern whether earlier figures were visually improved. The current figures can be inspected, but the repository is a one-commit shallow clone and no prior figure version was supplied. The historical change itself cannot be verified. Automated figure QA also did not complete because of a parser error, so visual inspection must not be represented as an automated pass.

The response letter should therefore be rewritten. Its repeated claims of “complete,” “strict,” and “thorough” resolution are not supported by the submitted artifacts. A factual response should use the statuses above, identify exact file/line or page locations, and state remaining limitations without rhetorical amplification.

## 5. Overall Recommendation

**Recommendation: Reject**

**Score: 3/10**

The manuscript has a worthwhile question, a substantial mathematical core, and several calculations that can be independently reproduced. I would encourage a thoroughly rebuilt resubmission. Nevertheless, the present version has multiple publication-blocking defects: two sets of headline empirical numbers lack generators; Figure 7 contradicts the accompanying table and committed results; the data-to-parameter chain is incomplete and partly hard-coded; the rolling protocol differs from its description; the RSV information-limit argument uses inconsistent formulas and comparison units; numerical claims for Theorem 5R and Corollary 1 conflict with the available evidence; and the bibliography contains unverifiable or materially incorrect records. Because these problems affect central results and persist after an extensive prior revision, they require reconstruction and re-audit rather than another narrow editorial pass. If the journal’s policy favors revision over rejection, the only defensible alternative would be a tightly scoped Major Revision with all ten major comments treated as mandatory acceptance conditions.
