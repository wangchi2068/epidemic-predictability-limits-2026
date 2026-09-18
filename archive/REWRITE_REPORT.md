# Reframed manuscript audit and rewrite report

## Decision

The paper is salvageable after changing the estimand. The defensible contribution is a model-conditional forecast-error benchmark plus a separate operational loss audit. The phrase “fundamental predictability limit” is removed from the title, abstract, results, and conclusion.

## Retained

- Exact conditional squared-loss identity.
- Exact finite-step variance of the fixed-`k_agg` macro negative-binomial update.
- Seven frozen state-panel phase calibrations.
- Micro transmission-chain fits as working-model evidence.
- Same-origin paired rolling losses and state-block bootstrap intervals.

## Downgraded or removed

- A4 is replaced by the conditional expectation identity; posterior parameter uncertainty is stated explicitly.
- The old three/four-component budget is removed because its predictors, windows, denominators, and variance objects were mixed.
- The “loose envelope” and “business upper bound” claims are removed.
- Opposite-direction crossing points are not combined into one horizon.
- The frozen Forecast Hub aggregate and its plot are removed from the evidence chain. The associated failure note remains as an audit artifact.
- QSD, environmental-noise extension, one-shot MLP/LightGBM comparison, health-equity prescription, and CRB-to-detection-time conversion are excluded from the main narrative.

## Verified local outputs

- `scripts_v2/reframed_analysis.py` completed with exit code 0.
- `reports_v3/reframed_summary.json` contains seven mechanistic horizon summaries and paired loss differences with 2,000 state-block bootstrap replicates.
- `reports_v3/reframed_verification.json` records five independent numerical checks, including the repeated-root macro variance case, WIS equivalence, horizon censoring, and moving-block bootstrap multiplicity.
- State median mechanistic roots: 2.20--7.12 weeks.
- Pairwise loss differences change sign across phases; this supports a calibration audit, not a universal ordering.

## External audit status

FluSight releases `v1.0.0` (primary, commit `dde0d620d349854266c5a0217df9956ae17670f9`) and `v1.1.0` (cross-season audit, commit `1b5b615312eb3a9ebb3fa5fe0e2e123e45258bdc`) are downloaded and scored against the official baseline. Strict final-vintage results are reported in `reports_v3/flusight_v1.0_strict.json` and `reports_v3/flusight_v1.1_strict.json`; they use common origin--state--horizon cells and moving-block bootstrap. They are historical audits, not real-time skill estimates. A future extension should add report-date target archives before making a real-time-vintage claim.

## Round 2: theory strengthening

After the reframe, the theory was strengthened from a single orthogonal-decomposition assumption (old A4) into a stated conditional-risk program. The manuscript, the proof manual, and the numerics were changed together:

- `main_reframed.tex` states the sharp conditional squared-loss floor (Thm. 1) and its attained-at-the-conditional-mean property, replaces A4 with the conditional-expectation identity, and adds an explicit posterior total-variance decomposition (Prop. 2) that separates process variance, parameter mixing, and plug-in excess risk.
- The fixed-`k` aggregate negative-binomial update is given an exact finite-step variance with the `q=r` removable limit and the `R=1` boundary, all as boundary cases of one finite-step solution rather than extra asymptotics.
- A shared-lognormal growth-rate mixture is worked out in exact closed form, and the conditional (not unconditional) AR(1) summed variance plus the `phi -> 1` unit-root boundary are stated so the two cannot be mixed in one horizon calculation.
- `derivations/derivations_manual.tex` was extended to prove every one of these results, and now compiles cleanly (`derivations/derivations_manual.pdf`).
- `scripts_v2/reframed_model.py` and `scripts_v2/reframed_statistics.py` expose the corresponding interfaces (`macro_moments`, `lognormal_predictive_moments`, `horizon_set`, `conditional_ar1_sum_variance`, `ar1_sum_variance`, `quantile_wis`/`interval_wis`, moving-block bootstrap).

## Verification status (final)

- `scripts_v2/verify_reframed.py` -> `reports_v3/theory_verification.json`: 7/7 independent checks pass (macro recurrence across `R<1,=1,>1`, the `q=r` removable limit, shared-lognormal mixture against 80-node Gauss-Hermite quadrature, separated horizon segments and supremum, conditional/unconditional AR(1), 23-quantile WIS vectorization, moving-block bootstrap reproducibility).
- `scripts_v2/reframed_analysis.py` reproduces the seven state-median mechanistic roots (7.12, 3.95, 5.00, 2.20, 2.58, 5.82, 3.89 weeks) and state counts in `main_reframed.tex`.
- `scripts_v2/score_flusight.py` reproduces `reports_v3/flusight_v1.0_strict.json` and `flusight_v1.1_strict.json` byte-for-byte from the downloaded release files.
- `tectonic main_reframed.tex` and `tectonic derivations/derivations_manual.tex` both compile with 0 undefined references and 0 overfull boxes.
- `scripts_v2/macro_model.py` now evaluates the `q=r` removable limit instead of returning NaN.
