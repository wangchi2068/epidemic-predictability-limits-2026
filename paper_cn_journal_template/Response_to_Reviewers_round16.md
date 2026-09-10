# Response to Reviewers — Round 16

**Manuscript.** 传染病动力学可预测视界、数理极限与实证分析 (round-15 revision).

We thank the reviewer for a review that re-derived the mathematical core, recomputed
every deposited number, and identified a single underlying failure mode. This
response documents (i) the resolution of the three blocking findings, (ii) the
item-by-item disposition of the major and minor items, and (iii) the largest
change in this revision: the empirical layer has been **rebuilt on a three-tier
data design** and every empirical number in the manuscript was regenerated from
the new chain.

---

## 1. The blocking findings

### B1 — Indicator identity (comment 4.3(i)): resolved, with a favourable outcome

The reviewer established that the deposited analysis series is at
hospitalisation rather than confirmed-case scale. We traced the construction
end-to-end and confirmed the reviewer's inference, and the finding extends
further than the deposited COVID series:

- **All three pathogen series are NHSN weekly hospital admissions**, obtained
  through the terminal target data of the three CDC forecast hubs: COVID-19
  (`reichlab/covid19-forecast-hub`, hospitalisation truth, final release
  2024-04-28, commit `e9db0366`), influenza (FluSight), and RSV (RSV Forecast
  Hub). The deposited COVID weekly series is reproduced from the hub's daily
  truth file by Saturday-ending aggregation; the 51-state Delta-window sum is
  141,735, exactly the value the manuscript's tables were built from.
- Section 4.1 and the Data Availability statement now describe this
  construction; the JN.1 splice disclaimer is **deleted** (it no longer applies —
  there is no indicator splice at all), and the JN.1 row is restored to
  cell-by-cell comparability.
- The missing ingest step is now deposited as
  `scripts_v2/ingest_and_aggregate.py`, which re-derives the weekly COVID panel
  from the daily file, asserts structural invariants, and pins each series by its
  national window sum (COVID-19 Delta 141,735; influenza 2022–23 15,579; RSV
  2024–25 22,047). A silent series swap now fails the build.

Because the underlying data are unchanged in scale and trajectory, the
previously reported horizon and error-accounting results reproduce; what changes
is that the manuscript now describes the data truthfully, and the state-level
panel below supersedes the national-only analysis.

### B2 — Priority and increment (comment 4.4(i)): corrected

Section 1.2 now cites Pérez-Reche et al. (2012, *J. R. Soc. Interface* 9:2085)
and states what it established: existence of a prediction horizon, its
dependence on the required precision, monotone growth of uncertainty with
look-ahead time (our Theorem 2), and the separation of parameter uncertainty
from intrinsic stochasticity. The priority-flavoured wording is removed and the
increment claim is now the sentence the reviewer asked us to promote: a specific
analytical instantiation, in closed form, under negative-binomial branching with
log-normal parameter propagation. We also add the requested comparisons and
qualifications: Steyn et al. (2025, *Stat. Med.* 44:e70204) as the closest
existing implementation of two-source forward propagation (numerical, versus our
closed form); Parag & Donnelly (2020, *PLoS Comput. Biol.* 16:e1007990 and
*Syst. Biol.* 69:1163) as the Fisher-information route and its precision-measure
precedent; and Boudreau et al. (2026, arXiv:2506.24103) together with
`endo2020overdispersion` and `hebert-dufresne2020beyond`, so that the
near-critical narrative carries its own qualification (the sensitivity peak at
threshold requires overdispersion above k ≈ 0.3, while empirical COVID-19 and
influenza overdispersion is often below it). Drake's coefficient of variation is
now explicitly distinguished from CV²(h) (final-size versus generation-h
incidence; the precedent is one of idea, not a special case). The previously
uncited entries `cori2013framework`, `gostic2020practical`,
`rosenkrantz2022fundamental` and `dietze2017prediction` now carry argument.

### B3 — Dimensional repair completed in prose and code (comment 4.3(ii))

The Table 4 note now prints the weekly form
`E_drift(h) = h_week × v²_week` (with the equivalent
`h_gen × Δ_g × v²_week` given parenthetically), and the generator docstring's
false-equivalence sentence is deleted and replaced by an explicit statement that
the generation-step form is dimensionally different and retired. The
consistency suite now contains a dimensional assertion that every budget row
equals `h_week ×` the per-week drift variance.

---

## 2. Major items

- **M1 (Appendix C boundary classification).** Replaced with the correct
  statement: by the Karlin–Taylor criteria the first integral converges and the
  second diverges logarithmically, so y = 0 is an exit boundary for every λ > 0;
  the transplanted CIR critical point is explicitly identified as inapplicable.
- **M2 (Section 4.2 reversal threshold).** The passage carrying the underivable
  1.4× threshold belonged to the superseded national RSV data-sufficiency
  analysis and was removed with it in the empirical rebuild; no numeric
  threshold of that kind remains anywhere in the manuscript (the stale-literal
  scan now includes it). The substantive point — that the RSV 2025–26
  sufficiency doubt is robust in direction — is retained qualitatively in the
  new Section 4.3, and the Cramér–Rao bound is now validated at the individual
  level instead (Section 4.2).
- **M3 (Figure 1 Theorem 4 threshold).** The R² factor is restored; the printed
  form now matches Theorem 4 and Appendix D.
- **M4/M5 (contribution list).** Contribution 2 no longer claims a "revealed"
  O(N^{1/2}) mechanism or a "rigid" threshold: Theorem 3 is an analogy-scale
  claim, Corollary 2 is directional, and Theorem 4's empirical use is a
  magnitude heuristic. Contribution 4 now states the (A4) exploratory-contrast
  qualification.
- **M6 (Figure 3 ratio band).** 1.2–1.6 is corrected to 1.07–1.61 in all three
  locations (Corollary 2 statement, Section 3.2, figure caption).
- **M7 (missing ingest step).** Deposited; see B1.
- **M8 (checked surface).** `check_consistency.py` now implements eight
  assertion classes (table-fragment byte comparison, figure non-blankness,
  stale-literal blacklist across `main.tex` **and** `README.md`, abstract-range
  assertions, CRB-ratio assertions, the drift dimensional assertion, two-sided
  crossing assertions, and deposited-series identity pins). The code-availability
  statement is updated to match.
- **M9 (README).** Rewritten for the new architecture; the three withdrawn
  conclusions are gone, and the stale-literal scan now covers it.
- **M10 (local-linear intervals).** Printed with the valid-resample counts
  (Delta 5.33 [2.91–7.39], 773; Omicron 1.16 [1.14–7.42], 565), and the
  censoring caveat is extended to the 565 case.
- **M11 (near-critical qualification).** Cited and discussed; see B2.

## 3. Minor items

Occluded Figure-3 annotation moved; precision bands now state their unrounded
provenance; the circular block-bootstrap combinatorics corrected to 6 starting
blocks / 36 ordered resamples; Appendix-B wording fixed (conditioning, not
degeneracy); dependency upper bounds added; snapshot dates corrected; Figure 3
panel (a) narration reordered to match the bars; the machine-learning claim
softened to the tuning budget used, with the single-configuration budget
disclosed.

**Bibliography accounting (m5, m8).** The current bibliography in `references.bib`
has been thoroughly pruned and finalized to exactly 57 entries, all 57 of which are cited in the
manuscript (0 uncited entries), completely eliminating all key/year conflicts and unused bib warnings.
The build-relevant `references.bib` copies remain byte-identical across the repository.

---

## 4. The empirical rebuild (three-tier design)

The reviewer's central diagnosis — that the empirical layer forced one national
weekly series to carry every theorem — is addressed structurally. Section 4 now
uses three tiers matched to the theory:

1. **Individual transmission chains** (Hong Kong COVID-19, N=355 local /
   N=1,038 all; Guinea Ebola, N=152) directly test the negative-binomial
   generating assumption and, via parametric bootstrap, the Cramér–Rao bound at
   the individual level (ΔAIC 93.9–244.0; k̂ = 0.11–0.43; bootstrap/CRB
   0.98–1.06). This removes the previous layer mismatch for Theorem 4 and gives
   an empirical near-critical anchor (Ebola R̂ = 0.954).
2. **A 51-jurisdiction state panel** across seven phases gives the *spatial
   distribution* of the theoretical horizon. State-level median horizons
   (4.5–10.9 weeks) are systematically shorter than the national aggregates
   (7.9–67.8 weeks): aggregation smooths the series and inflates horizons. The
   four-term error accounting is now executed per state (median residual share
   21%→97%; positive in 62%–100% of states).
3. **The COVIDhub-ensemble archive** (12 real forecast origins) provides an
   external operational benchmark: top-tier ensemble skill also degrades to
   parity within 1–2 weeks, indicating that the short operational lead time is
   not merely an artifact of the finite tuning budget of our exploratory baseline models.

Every empirical number in the abstract, Section 4, Section 5 and the conclusion
was regenerated from this chain; the old national-only tables and their figures
have been removed. All numerical results are produced by
`python scripts_v2/make_all.py`, which halts on any consistency failure.
