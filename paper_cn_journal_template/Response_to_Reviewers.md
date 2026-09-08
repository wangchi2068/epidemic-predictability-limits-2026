# Response to Reviewers — Round 14

**Manuscript:** 传染病动力学可预测视界、数理极限与实证分析 (Predictability horizons, mathematical limits, and empirical analysis of infectious-disease dynamics)

**Revision base:** commit `50feeab` → this revision (peer-review report 14: 3 blocking findings, 22 required-correction items ranked 1–22, plus process conditions).

We thank the reviewer for a third consecutive audit of unusual depth. The three blocking findings were all verified against our own repository before repair: recomputing the closure under a consistent time scale reproduces the reviewer's table exactly (flu22 h=1 flips to +26.1%, rsv24 h=2 deepens to −372.8%); applying a two-sided crossing detector to our own deposited skill series reproduces the 5.33-week and 1.16-week local-linear crossings; and the unreported `establishment_nb` block indeed shows 5-of-12 coverage. This letter follows the established convention of citing locations by section/table/theorem/environment name.

**Verification of this letter's own claims.** Build remains one command (`python scripts_v2/make_all.py`). The consistency suite was extended this round with two physics-level guards the reviewer's process condition (b) asked for: (i) a dimensional assertion that every `e_drift` in `table4_budget.json` equals `h_week × v_drift` (catching a regression to the generation-scale multiplication), and (ii) an assertion that the local-linear crossings exist and are downward for Delta and Omicron (catching a regression to a one-sided detector). A further 14 new stale literals (the retired −54%/−297% ranges, the 9-of-12 tally, the retired R values, the inconsistent bias bands, "均无穿越" and its variants) were added to the blacklist. All checks pass; the PDF compiles clean (42 pages, XeTeX chain); both abstracts were regenerated from the corrected JSONs and re-verified cell-by-cell against them.

---

## Part I — The three blocking findings

### Finding 1 (§3.1) — E_drift on the wrong clock
**Fixed at the code level and propagated everywhere.** `error_budget_v2.py` now computes `e_drift = h_week * v_drift` (v_drift is measured on the weekly series, so accumulation is over calendar weeks; equivalently `h_gen · Δ_g · v²_week`). The docstring now states the dimensional reasoning explicitly. The chain was rerun; Table 4, Figure 6, §4.4, §6, and both abstracts were regenerated from the corrected `table4_budget.json`. The new headline, identical across all four locations and asserted against the JSON by the build: **positive unattributed residuals in 10 of 12 configurations (26.1%–99.3%, 9 of the 10 above 40%); two negative rows, both short-horizon low-count RSV (−178.6% and −372.8%), reported unclipped as calibration-band diagnostics.** Per the reviewer's interpretation point: the flu22 h=1 sign flip is explicitly attributed in both abstracts to the arithmetic defect (previous reporting was a dimensional artifact, not a mechanism overestimate), and §4.4's calibration-band diagnosis now claims only the two RSV rows, where it is directionally sound. §4.4 item 2 also carries a candid note stating the defect, its magnitude (COVID/flu inflated 1.5–2.3×, RSV deflated to 0.83×), and the correction.

### Finding 2 (§3.2) — One-sided crossing detector
**Fixed at the code level.** `cross_point` in `rolling_eval_v2.py` now detects crossings in both directions and records the direction (`up`/`down`); both the point estimates and the bootstrap loop use the two-sided version. The rolling evaluation was rerun: **Delta 5.33 weeks (95% interval 2.91–7.39, 773/1000 valid resamples), Omicron 1.16 weeks (1.14–7.42, 565/1000), influenza no crossing (curve starts below parity)**. §4.5 now presents the corrected result as the reviewer suggested — the two baselines agree in magnitude, which strengthens rather than weakens the operational conclusion: persistence up-crossings at 3.52/1.82/5.34 weeks and local-linear down-crossings at 5.33/1.16 weeks are consistent, so the 1.8–5.3-week headline no longer depends on baseline choice. The false monotone-decrease claim is corrected (flu22's 0.409→0.422 rise is now stated), and the false short-range-inferiority claim is gone. Figure 7's caption and plot legend label the down-crossings; Table 5's note reports all three baselines. Both abstracts state the two-baseline agreement.

### Finding 3 (§3.3) — Unreported establishment_nb negative result
**Reported, not withdrawn.** Figure 3 gained a third panel: Corollary 2's actual NB predictions 2ε/[R(1+R/k)] against the empirical Beta intervals across all 12 cells, with the 5/12 coverage printed inside the plot. The generator now raises if the NB block is empty, so it can no longer be silently dropped. §3 and the Figure 3 caption report the result exactly as the reviewer characterized it: the k-suppression direction is confirmed empirically (k=0.5 systematically below k=1.0), but the first-order theory sits below the data everywhere (emp/theory 1.2–1.6 at N=500), so **Corollary 2 is downgraded to a directional claim only**; its statement and §3 now say so in terms, and the corollary's quantitative k-dependence assertion ("strongly nonlinearly suppressed") is retired. The h*/W-style disclosure logic the reviewer asked for — negative results reported with their magnitude — is applied here in full.

---

## Part II — Required corrections 4–15 (must-fix list)

4. **§4.3 stale numbers.** All three repaired: the subcritical range now cites the deposited 7.5–33.5 weeks from Table 3's own rows; the two R values that appeared in no deposited file (0.9570/0.9621) are replaced by the deposited Omicron-decline 0.8690 and flu22-decline 0.8359. All four literals are on the consistency blacklist.

5. **M=3 origin count.** Disclosed in three places: §4.4 now states the skip rule (targets more than 3 days from the requested date are dropped) and that effective origin counts M_eff are recorded per row in `table4_budget.json` (`n_origins`); the Table 4 note states explicitly that the two rsv24 rows have M_eff=3 and all other rows M_eff=6. The rows were kept rather than dropped because they carry the paper's most diagnostic negative residual; both the note and §4.4 flag the reduced support.

6. **Bibliographic fabrication repair.** `nemcova2026unjustified`: given names corrected (Isaac H. Goldstein, Jessalyn Sebastian, Volodymyr M. Minin), article number e79. `ho2023simultaneous`: issue 2, pages 201–205. The Kéfi accent is now actually repaired (`K{\'e}fi`; the round-13 letter claimed this and had not done it — we verified the bytes this time). All four `references.bib` basename copies are converged: the repaired template copy is now byte-identical to the repo-root copy (`md5 16d9f176b5` both), so a root-level build can no longer resurrect the pre-repair file; `references_working_library.bib` is documented as a non-build side library. Lloyd-Smith 2005 (Nature) is now cited at (A1), where the overdispersion machinery is introduced.

7. **df=3 intervals withdrawn.** The 95% CI columns are gone from Tables 2 and 3; Figure 5's error bars are removed; Table 5's theoretical column prints point estimates only (its empirical column keeps the MBB interval, which is genuinely data-dependent). §4.2 states the mechanism once and gives the single multiplier: approximate 95% interval = [0.55·h*, 3.77·h*], with the Delta example (≈11.7–80.0 weeks). The Table 2 note, Table 6 note, and §4.1 protocol paragraph all reference the multiplier instead of per-column intervals.

8. **Omicron point estimate flagged as censored.** Table 5's note now states that the 1.82-week point estimate inherits the same right-censoring as its interval and should be read as indicative. The ≤16-ordered-resample support is stated as a hard resolution limit in §4.5.

9. **Bias bands reconciled** to the analytically pinned 16.7%–16.9% in both Lemma 3 and §4.2 (the two inconsistent bands 16.5–17.6 and 16.7–18.0 are blacklisted).

10. **Phantom ‡ references deleted.** §4.2 no longer points at Table 3 ‡ rows; the Table 3 note's ‡ definition is removed (no cell in Table 3 reaches the cap — max k_agg 698.4).

11. **h*/W root identified.** Table 2's note states the column uses the week-scale exact root, gives the generation-scale conversion (multiply by 7/μ_g), and notes the two readings diverge across pathogens; §4.2 flags Delta's week-reading 4.2× alongside its ~19-week wave life cycle.

12. **Kéfi accent + DOI accounting + Lloyd-Smith credit** — see item 6. The missing-DOI count is restated where DOI policy is discussed: we now track 8 of 42 cited entries without DOIs (5 optional for books/proceedings, `grassberger1983critical` a genuine journal omission, left for the camera-ready pass rather than filled from memory).

13. **One canonical .bib** — see item 6.

14. **Code Availability narrowed.** The statement now says the suite checks fragment↔JSON byte equality, figure non-blankness, stale literals, and two headline assertions — and explicitly that it does not independently audit prose semantics or physical dimensions, and that Figures 3 and 7 carry no per-number assertions. The data-availability statement also reconciles the archival dates (COVID confirmed-case series ended 2023-05-10; NHSN/flu/RSV snapshots March 2026).

15. **Figure 1 TikZ updated:** the Theorem-5R cell now states the conditional scale-invariance (CV²(h*) ≪ τ² working points); the Theorem-3 cell drops "视界坍塌" and points to the CV²-based argument. §2.1's O(10%) example now points at low-I₀ RSV working points in Table 2, where CV² is defined, instead of the undefined R<1 decline rows.

---

## Part III — Should-address framing items 16–22

16. **Theorem 3 restated.** Boundary type corrected: the statement no longer calls y=0 a natural entrance boundary; Appendix C now says the Feller type varies with λ (critical at λ=(R+1)/2) and is exit/absorbing in the D&L-relevant setting. The O(1) spectral-gap claim is **withdrawn as a theorem and not merely relabeled**: Appendix C now states the reflected speed measure is log-divergent at 0 (mass fraction below y=0.01 rises from 0.00 at y_min=10⁻² to 0.83 at 10⁻¹²), that no non-degenerate limiting stationary measure exists for a gap to belong to, and that the numerically observed gap drifts with the cutoff — so the O(N^{1/2}) claim is presented as a heuristic time-scale analogy to D&L's extinction-excision scaling, with its k-set-aside caveat stated. Nåsell and D&L are no longer cited jointly as one result (§1.2 now describes what each establishes).

17. **Horizon-collapse inference withdrawn.** Theorem 3's item 2 no longer claims horizon collapse; it states the quantity measures near-critical fluctuation persistence and that the near-critical horizon contraction is argued by the paper's own CV² machinery (Corollary 1). Figure 1's cell and the conclusion were updated to match.

18. **Aggregation-inflation robustness stated.** §4.2 now says explicitly: the single cross-season contrast drawn from the diagnostic (rsv25 1.48 vs rsv24 0.22, ~6.7×) is not robust to the unbounded aggregation-inflation term — if smoothing depresses rsv25's s by more than ~1.4× relative to the unsmoothed case the contrast reverses — so the paper draws only the direction-robust weak conclusion (inflation can only raise C_req, so "data sufficiency in doubt" for rsv25 survives any amount of smoothing).

19. **(A4) violation acknowledged at introduction.** §2.2 now carries the disclosure where the assumption is introduced: online estimation shares history with the prediction period, (A4) holds only approximately in finite samples, and the theory/empirics pair is an exploratory contrast rather than a same-conditions validation.

20. **Drake 2006 credited as the direct precedent.** §1.2 now states, in the reviewer's own terms: Drake derived an analytic CV-based predictability limit from a stochastic branching epidemic at known parameters and identified a critical R₀ — the direct precedent for Lemma 2 and Theorem 1's property 1 — but produced no lead time and explicitly assumed exactly known rates; this paper adds the estimation-error term P(h), converting the static CV threshold into a horizon. §1.3's increment statement is unchanged (a specific analytical instantiation).

21. **JN.1 indicator splice disclosed.** §4.1 now states that JN.1 uses NHSN weekly hospitalizations while all other phases use confirmed-case or lab-positive series, that these observables differ in ascertainment and clustering yet enter identical CV²/C_req machinery with no sensitivity analysis, and that the JN.1 row should be read directionally rather than compared cell-by-cell with the others. (A full indicator-mismatch sensitivity analysis remains future work; the disclosure removes the silent-equivalence defect the review identified.)

22. **gen_fig_t3 panel (b) guarded + pixel test demoted.** Both establishment panels now raise on empty input (shared `_panel_est` helper); the Figure-3 guarantee is the raise, not the pixel test, and the Code Availability statement no longer cites the pixel test as a data-integrity check. The reviewer's stronger point stands and is conceded in §3.6 of our own verification notes: a decorated-but-empty reconstruction measures ~5.8% ink, above the 5% gate — the pixel test is decoration-level screening only.

---

## Part IV — Process conditions (a)–(c)

**(a) Diff-level abstract change statement.** Both abstracts changed in exactly these claims this round: (1) residual tally "9 of 12 positive, 6.2%–99.2%, −54% to −297%" → "10 of 12 positive, 26.1%–99.3%, two RSV rows −178.6%/−372.8%"; (2) new sentence attributing the flu22 h=1 sign flip to the corrected dimensional defect; (3) baseline sentence "no crossing against local-linear within h≤8" → "down-crossings at 5.3/1.2 weeks for Delta/Omicron, influenza below parity throughout, two baselines agree in magnitude"; (4) Theorem-3 clause "critical slowing-down scaling" → "analogy-migrated O(N^{1/2}) scaling from absorbed-boundary extinction-time theory". All other abstract sentences are unchanged from round 13.

**(b) JSON-vs-printed-equation verification.** Added to `check_consistency.py` this round: the dimensional assertion (e_drift = h_week·v_drift for every row) and the two-sided-crossing assertion. These are the first two checks in the suite that test JSON contents against the manuscript's own physics rather than fragment-against-fragment; the reviewer's point that the previous suite would have passed every defect in §3 of their report is correct and is why these guards were written first.

**(c) Resolver-checked bibliography.** All bibliographic corrections this round were made from the reviewer's verified values (which we spot-checked against Crossref), not from memory; the policy of never filling a field from memory is extended from DOIs to author given names, issues, and page ranges. The two defects the review caught (Němcová names, Ho pagination) were exactly of the from-memory class and are now repaired; the remaining 8 DOI-less entries will be resolved in the camera-ready pass with the same policy.

---

## Part V — Honest accounting of what remains open

- **Items deferred with reviewer agreement from round 13, unchanged:** NB-likelihood re-estimation of R̂ (now additionally motivated by item 18's robustness caveat); block-length sensitivity; prospective multi-season real-time-vintage evaluation.
- **Minor observations we did not act on, with reasons:** Corollary 1's one-sided grid (extending to ε<0 reaches +124.6% — the exact root is used in all empirics so nothing propagates; the stated domain of the corollary will be narrowed to ε>0 in the camera-ready to make grid and domain agree); Theorem 5R's asymptotic overshoot at large φ (the theorem feeds no reported number and now carries the parallel-extension label; a finite-h exact form is printed in the statement itself); the JN.1 sensitivity analysis (disclosed as a limitation this round; the analysis itself is future work).
- **A self-audit note.** While verifying the final numbers for this letter we discovered the package-external directory `D:\trae\epidemic_predictability_paper_2026_final\reports\` still holds pre-repair copies of several JSONs (e.g., a `table4_budget.json` with the old E_drift bug). These are outside the submitted package (the build chain reads only `final_submission_package/reports/`, and the nested git repo does not track the outer directory), but we flag their existence for completeness since this round's theme is desynchronization.

The three blocking findings are fixed at the code level, verified by recomputation, and guarded against regression by new physics-level build assertions. We believe the manuscript now satisfies conditions 1–15 and the three process requirements, and we would welcome a fourth-round verification on the same terms.
