# Response to Reviewers

We thank the reviewer for the detailed audit. This revision rebuilds the submission around a single-source-of-truth build chain and regenerates every headline number from the deposited data. Below we respond point-by-point. Each item cites the exact revised location (main.tex line numbers of the current source) and the generating artifact. We mark items **implemented and verified by the build's consistency tests** versus items that remain **limitations**.

**Repository state for this response:** `scripts_v2/` is the only build path; `MANIFEST.md` at the package root records input SHA-256 hashes, the step table, and per-stage runtimes. `python scripts_v2/make_all.py` runs estimation → rolling evaluation → error accounting → verification → figures → table bodies → consistency tests, and fails on any divergence. Legacy scripts are quarantined under `scripts/legacy/` and are not part of the build.

---

## Major Comment 1 — Table 2 confidence intervals were not reproducible

**Implemented.** The parametric bootstrap now exists end-to-end in `scripts_v2/pipeline.py`: each replicate resamples log-scale residuals around the fitted line (B = 2000, seed 20260807), refits the slope and its OLS standard error, re-estimates k* (moment estimator) and I0* on the resampled counts, re-solves the horizon equation, and returns percentile intervals. Table 2 (main.tex 733–739), its note (745), Figure 5 (`reports/figures_v2/fig4a_real_horizons.png`), Table 5's theoretical column, and the abstract/conclusion ranges are generated from `reports/table2_params.json`. The old t-endpoint variant and all hard-coded intervals were deleted together with `extract_cdc_data.py` and `reproduce_all_tables.py` (moved to `scripts/legacy/`). `check_consistency.py` asserts that the generated bodies match the JSON and that the abstract range equals the JSON extremes.

**Honest consequence:** with a 5-week window (df = 3) the percentile intervals are wide (e.g., Delta 11.6–80.1 weeks). We now say so explicitly in Section 4.1 (main.tex 715) rather than presenting narrow intervals.

## Major Comment 2 — Table 4 observed totals had no generator; −0.05 cross term

**Implemented.** `scripts_v2/error_budget_v2.py` computes the observed relative MSE directly from origin-level forecasts and observations with the exact printed normalization (denominator $(I_{0,t} R_t^{h_{\text{gen}}})^2$, M = 6 origins per phase; output `reports/table4_budget.json`). The −0.05 cross term and the at-zero clipping of residuals were removed; negative residuals are reported as diagnostics. The prior log-scale `observed` quantity and the two orphaned cached JSONs were deleted. Table 4 (main.tex 807–836), Figure 6, and every percentage statement are generated from the JSON. **The corrected accounting changes the empirical narrative**: modeled terms explain 0.4%–48.4% across the 12 configurations (structural residuals 51.2%–99.6%), and the earlier "88.7% mechanistic explanation at influenza 4 weeks" is retracted as an artifact of the previously inflated residual-mean standard error (Section 4.3, main.tex 846).

## Major Comment 3 — Data-to-parameter chain and time-scale convention

**Implemented, with an explicitly documented input decision.** The estimation in `pipeline.py` fits the weekly log-scale OLS slope and its standard slope standard error (df = W−2), converts to the generation scale as $b_{gen} = \Delta_g b_{week}$, $s_{gen} = \Delta_g \mathrm{SE}(b_{week})$, $R = \exp(b_{gen})$, and uses those fitted quantities (not pre-entered values) in every table. Section 2.1 (main.tex 113) now states the conversion and proves the calendar-week invariance: solving directly in week units gives the identical weekly horizon (<0.01% difference), which removes the convention ambiguity behind the 13.5/15.2/18.4/20.1-week spread. Assertions in `check_consistency.py` tie manuscript values to the JSONs.

**Not fully achievable:** the byte-exact raw vintage behind the three processed weekly series (March 2026 archive) could not be reconstructed from the live CDC APIs (later backfill; state-level RSV detections are no longer published at that granularity). We therefore pin the processed series as the frozen analytical inputs with SHA-256 hashes in `MANIFEST.md`, archive the 2026-09-07 raw API snapshots under `data/raw/` for reference, and document dataset identifiers, retrieval dates, and the vintage caveat in the Data Availability statement (main.tex 996) and `MANIFEST.md`. The RSV 2025-26 backfill-period caveat is carried into Sections 2.1 and 4.1.

## Major Comment 4 — Stale Figure 7 and rolling-protocol mismatch

**Implemented.** One script (`rolling_eval_v2.py`) generates the rolling JSON, Figure 7 (`reports/figures_v2/fig7_skill_decay.png`), and the values consumed by Table 5; `main.tex` references only `reports/figures_v2/`, and the four duplicate figure directories were archived to `_archive/`. `check_consistency.py` fails the build if a referenced figure is missing or if same-named PNGs diverge anywhere outside `_archive/`. The horizon range is fixed at h = 1–8 weeks (stated in the protocol paragraph, main.tex 856, and the Figure 7 caption). Dependence-aware uncertainty is a moving-block bootstrap (block length 3, 1000 resamples, seed 20260807) over the origin sequence, documented at main.tex 860. The seasonal-naive baseline is implemented (52-week lag) and its coverage limitation is stated (main.tex 860): for the influenza wave the 52-week lag predates the deposited series, so the formal comparison uses the persistence baseline. We now report percentile intervals, and for Omicron state explicitly that its 95% interval (1.1–7.4 weeks) spans nearly the whole evaluated range (Section 4.4, main.tex 869).

## Major Comment 5 — RSV Cramér–Rao formula and invalid comparison

**Implemented.** The required-cluster count is derived once from Theorem 4's relative-variance bound: $C_{req} = (1/R + 1/k)/s^2$ with $s = \delta R/R$ (Section 4.1, main.tex 717). The comparison now uses the same-window 5-week case totals (22,047 and 9,341), not weekly means. The recomputed conclusion is reported as it falls out: RSV 2024–25 does **not** violate the bound (C_req = 8,694 vs. total 22,047, ratio 0.39); RSV 2025–26 does (22,986 vs. 9,341, ratio 2.46). We present this as a layered conclusion — a season-span truncation judgment for both seasons, plus an information-level diagnosis specific to 2025–26 — and note that treating reported cases as independent clusters ($\bar m_c = 1$) is the most optimistic mapping. Generated artifact: `reports/crb_analysis.json`; asserted by `check_consistency.py`. The abstract (main.tex 67), Table 2 note, and conclusion were updated accordingly.

## Major Comment 6 — Theorem 5R validation and Corollary 1 error domain

**Implemented.** Theorem 5R validation was rebuilt in `scripts_v2/verify_suite.py` (output `reports/verify_t5R_v2.json`). Experiment A measures $\mathrm{Var}(\sum r)$ on stationary-initialized AR(1) paths directly: ratios 0.982–1.020 across $\phi \in \{0, 0.5, 0.8, 0.95\}$, h = 1..10 — the closed form is verified where it applies. Experiment B (renewal with an NB observation layer) shows ratios 0.27–1.02 with a systematic decline in $\phi$; the revised text (Section 3, main.tex 674) reports both and attributes the damping to renewal-kernel lag smoothing rather than describing it as a first-step conditioning artifact. The contradictory 0.58/0.92–1.08 passage was deleted.

Corollary 1: the unsupported "≤13.6% for k ≥ 0.5, |ε| ≤ 0.2" claim was replaced by a predeclared 144-cell grid (`reports/corollary1_grid.json`, regenerated by `verify_suite.py`). Over the declared domain the quadratic root errs by up to 48.6% (underestimate at the |ε| = 0.2, I0 = 50 corner); in the narrow band |ε| ≤ 0.05, I0 ≥ 200, s ≤ 0.05, k ≥ 0.5 the maximum is 15.8%. The revised text (proof of Corollary 1, main.tex 405) presents the two error sources and states the closed form is a qualitative near-critical guide. The h/k law is restated as a conditional asymptotic approximation (Theorem 5 proof, main.tex 583). The Theorem 4 Monte Carlo is relabeled a numerical sanity check of the formula's implementation (Section 3, main.tex 673).

## Major Comment 7 — Envelope claim contradicted by Table 5

**Implemented.** With the regenerated parameters, all three empirical crossings (1.82–5.34 weeks) now fall below their theoretical horizons (7.9–21.2 weeks; ratios 2.03–6.03), so the specific numeric contradiction is gone — but we do not resurrect a strong envelope claim. Table 5's note and the closing paragraph of Section 4.4 (main.tex 887–895) present the comparison as exploratory: wide intervals on both layers, three waves and six origins only, Omicron's interval spanning the evaluated range, and finalized-vintage backtests not constituting real-time performance estimates. The abstract says "双层探索性基准框架" (two-tier exploratory framework). A general envelope claim would require a larger, prospectively versioned multi-season evaluation.

## Major Comment 8 — Assumptions and estimands need tighter qualification

**Implemented.** "Orthogonal" is replaced by "additive under (A4)"; Theorem 1 now displays the cross term before imposing (A4) and states where it vanishes (main.tex 342–347 and proof). The unverified "empirical perturbation < 1.5%" sentence was removed; the section instead states the shared-window dependence qualitatively (main.tex 858). Theorem 2 carries explicit non-degeneracy and finite-moment conditions (main.tex 412). The CV² saturation limit is qualified to R > 1 in Lemma 2 and Theorem 1 where relevant. Theorem 3 now describes the reflecting-boundary construction as an approximation to quasi-stationary behavior supported by the numerical CV comparisons, not as the exact QSD (main.tex 450). The near-extinction interpretation is clarified in Table 3's note (mechanism shift; mathematical roots are not operational lead times).

## Major Comment 9 — Novelty attribution and bibliography integrity

**Implemented.** The introduction now cites Petchey et al. for the threshold-crossing horizon concept, Drake (2006) for branching-process forecast-precision limits (previously uncited), Penn et al.'s aleatoric/epistemic distinction, and Parag & Donnelly's detection-delay limits, and recasts the contribution as "a specific analytical instantiation" rather than inventing the concept (main.tex 82). Bibliography actions: `taylor2016stochasticity` removed (its DOI returns 404 and no bibliographic record was found); `suez2026baseline` corrected (Ehsan Suez, actual title, DOI 10.64898/2026.03.18.26348748, labeled preprint); `petchey2015ecological` repaired (the corrupted author tail is fixed; journal/volume/pages/DOI render); `chan2026estimating` corrected to the journal version DOI 10.1038/s41598-026-46596-6; `cohen2024respiratory` corrected to DOI 10.1038/s41467-023-44275-y; `parag2026threshold` given its journal DOI; DOIs added to 15 previously DOI-less cited records. The bibliography now contains exactly the 66 cited entries; the 32 uncited entries moved to `references_working_library.bib`. Generation-interval attributions were corrected: Park et al. is labeled Dutch transmission-pair data used as a proxy assumption for Omicron; the Hart et al. 3.4-day figure is no longer attributed as an Omicron intrinsic interval; Chan et al.'s XBB-based estimate is labeled a proxy assumption for JN.1 (main.tex 745).

## Major Comment 10 — Single source of truth

**Implemented.** The submission is rebuilt around one manifest and one command: `MANIFEST.md` (input hashes, step table, runtimes) and `python scripts_v2/make_all.py`. Table bodies are generated into `reports/table_bodies.tex`; all figures go to the single canonical directory `reports/figures_v2/`; `check_consistency.py` fails the build on stale literals, missing/divergent figures, or JSON–prose mismatches. This response letter cites files and line numbers rather than completion superlatives.

**Remaining, stated as limitations:** the raw-vintage reconstruction gap (see Major 3) is documented rather than closed; the moving-block bootstrap block length is a design choice justified in-text; the Theorem-5R renewal damping factor is characterized empirically, not derived.

---

## Minor Comments

1. **Repeated numerical summaries aligned.** MLE/CRB ratio now uniformly 0.9956–1.0024 (from `reports/verify_t4.json`) in Sections 3 and 6; structural-residual ranges uniformly 51.2%–99.6% from `table4_budget.json` (main.tex 703, 846, 988).
2. **Tables 2/3 parameter difference explained.** Table 3's note (main.tex 784) states that every phase window is independently re-estimated; rows that share a window with Table 2 have identical values by construction.
3. **I0 and origin-count terminology.** I0 is defined as the arithmetic mean of weekly counts (main.tex 111, Table 2 note); M = 6 origins per wave is stated in Sections 4.3–4.4 and matches `rolling_results.json`.
4. **Bilingual abstracts aligned.** The English abstract was rewritten to mirror the Chinese one claim-by-claim (0.74%, RSV ratios and caveat, per-pathogen crossings, moving-block bootstrap) — main.tex 67 vs. 1024.
5. **Overstatement and duplication removed.** "物理硬上限/第一性原理/客观物理标尺/严格验证" are replaced with model-scoped wording; the duplicated E_drift sentence in the Theorem 5 proof was removed (main.tex 583).
6. **Generation-interval labels qualified.** Table 2's note labels each estimand (intrinsic vs. realized forward vs. household), study population, geography, and marks cross-variant substitutions as proxy assumptions with sensitivity notes (main.tex 745).
7. **Portability.** The PDF compiles under tectonic/XeLaTeX; `MANIFEST.md` lists per-stage runtimes and the environment file includes torch. A container recipe is future work (stated).
8. **Journal formatting.** Manual-bold usages retained are template-mandated (captions/notes of the Chinese-journal template); non-mandated manual formatting was removed where encountered.

## Verification of previous-round items

- Resolved as claimed: broken citation repair, CV² maximum (now 0.74% under the regenerated parameters), MLP ratio 6.69 scoping, Table 5/JSON agreement, `0.0574`/`±1.82%` remnants absent, non-prescriptive disclaimers in Sections 5.1–5.2.
- Now additionally resolved: parametric bootstrap (Major 1), Table 4 generator (Major 2), stale Figure 7 (Major 4), CRB formula/units (Major 5), Theorem 5R/Corollary 1 conflicts (Major 6), bibliography repairs (Major 9), single build graph (Major 10).
- Not achievable in this round and documented instead: byte-level raw-vintage reconstruction (Major 3); prospective multi-season rolling evaluation to establish any general envelope claim (Major 7).
