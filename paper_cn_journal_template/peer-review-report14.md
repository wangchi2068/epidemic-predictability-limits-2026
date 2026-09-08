# Peer Review Report

**Manuscript:** 《传染病动力学可预测视界、数理极限与实证分析》 (Predictability Horizons, Mathematical Limits and Empirical Analysis of Infectious-Disease Dynamics)

**Round:** 13 — review of the revision and of the accompanying response letter (19 Major + 18 Minor items)

**Materials examined:** `main.pdf` (40 pp.), `main.tex` (1,040 lines), `Response_to_Reviewers.md`, and the authors' public repository `epidemic-predictability-limits-2026` (single commit `50feeab`, cloned successfully, read as text only — no script was executed)

**Date:** 2026-09-08

Locations are cited by section number, table number, theorem number, environment name, or repository file and function, following the convention the authors themselves adopted in this round (Minor 18). Line numbers are used only for repository source files, where they are stable within the audited commit.

---

## 1. Summary

The manuscript proposes a two-tier framework for the predictability of respiratory-epidemic forecasts. The theoretical tier models incidence as a negative-binomial Galton–Watson branching process and decomposes the relative mean-squared forecast error at horizon $h$ into two additive components: a demographic-stochasticity term $\mathrm{CV}^2(h)$ arising from the branching process, and a parameter-extrapolation term $P(h)$ arising from lognormal propagation of uncertainty in the estimated reproduction number. Under assumptions (A1)–(A4) the cross term vanishes, giving

$$\mathrm{relMSE}^2(h) = \mathrm{CV}^2(h) + P(h),$$

and the predictability horizon $h^*$ is defined as the largest $h$ satisfying $\mathrm{CV}^2(h)+P(h)\le\tau^2$ for a stated tolerance $\tau$ (baseline 0.5). Around this core the paper assembles three lemmas, five theorems plus a starred parallel extension, and three corollaries: strict monotonicity of the error in $h$ (Theorem 2), a near-critical quasi-stationary diffusion with $O(N^{1/2})$ critical slowing down (Theorem 3), a Fisher-information and Cramér–Rao minimum-sample threshold for identifying $R$ (Theorem 4), and a variance-accumulation law for macro-scale renewal dynamics with an AR(1) parallel extension (Theorem 5 / 5R, Corollary 3).

The empirical tier calibrates the framework on US CDC national weekly surveillance for COVID-19, influenza and RSV across seven epidemic phases, adds a four-term error budget, and runs a pseudo-real-time rolling out-of-sample evaluation against persistence and local-linear baselines. The headline claims are: demographic stochasticity contributes at most 0.74% of $\tau^2$, so horizons are governed almost entirely by inference signal-to-noise; theoretical horizons run 7.9–21.2 weeks for the non-RSV phases; an unattributed structural residual dominates observed error in most configurations; and operational skill against a persistence baseline decays to parity within 1.8–5.3 weeks. The paper positions itself as an exploratory two-tier benchmark framework, not an established one, and states its sample scope (three waves, six origins) in the abstract.

This round delivered a large and genuine body of repair. The previous round's structural root cause — a single-source table mechanism that validated a file which never entered the compilation — has been correctly fixed, and the response letter's self-reported list of what it did not do is accurate rather than evasive. Against that, this review identifies two live code defects that no clean rebuild would remove, both of which propagate into both abstracts, and one instance of selective reporting of a negative result that the authors' own repository contains.

---

## 2. Strengths

These are the findings I was able to establish positively, by recomputation or by reading the source rather than by taking the letter's word.

**The core mathematics is sound.** Every derivation I re-did independently is exact. Theorem 1's additive decomposition holds with the cross term at Monte Carlo noise level in all three configurations tested (2×10⁶ draws each; measured cross term 1.8×10⁻⁵ against noise 8.7×10⁻⁶ at the Delta working point), given (A4). Theorem 2's monotonicity verifies strictly increasing on $(0,200]$ for all seven supercritical phases and for the subcritical Table 3 rows, confirming the sketch's claim that the $(R-1)$ factor cancels. Theorem 3's quasi-stationary density solves the zero-flux equation with residual identically zero under symbolic re-derivation; its $I_{\rm char}\propto\sqrt N$ scaling, its transition-window constant (ratio to the printed value exactly 1) and its rescaling to the limit diffusion all reproduce. Theorem 5R's AR(1) variance sum and unit-root cubic verify. Dimensional consistency holds for every displayed formula except $\mathcal{E}_{\rm drift}$ (§3.1).

**The empirical numbers reproduce.** Working from the paper's own printed equations and its deposited JSON, I recomputed Tables 2, 4, 5 and 6 cell by cell. All seven exact horizon roots match to ≤0.6%; the $h^*_{\rm approx}$ column evaluates to 37.0/21.5/25.2/27.7/39.9/40.3/66.4 generations, matching every printed cell and confirming that the column bug the letter reports (approximate column filled with exact values) is genuinely fixed; $C_{\rm req}$ is exact for all seven phases with the 1.48 and 0.22 ratios reproducing to three decimals; Table 6's four tolerance columns and the 2.82–2.87× sublinearity reproduce; the $\tau=0.50$ column is row-for-row identical to Table 2; and the residual tally is verified cell by cell (nine positives, minimum 6.20%, maximum 99.17%, eight of nine above 40%). Abstract and conclusion headline figures match their table cells in every location.

**The single-source mechanism is real and correctly wired into the compiled document.** All five `\input{tables/table*_body}` statements are present, each inside its `\resizebox` wrapper, each fragment a complete `tabular` environment carrying a generated-file header; every fragment traces to `table2_params.json` or `table4_budget.json`; no hand-typed data rows survive for Tables 2–6 (Table 1 is the sole hand-typed table, correctly so). The consistency suite runs as step 8 of `make_all.py` with fail-fast, and its fragment-against-JSON byte-equality assertion is real. This was the previous round's root-cause finding and it is properly repaired.

**Figure 3 is genuinely fixed.** The blank-figure failure is resolved. The figure is non-blank and data-bearing across two panels; the rewritten generator raises an uncaught `SystemExit` on empty input, which `make_all.py` propagates as a build failure; and all four caption ratios (0.9995, 0.9991, 0.976, 0.950) match `verify_t3.json` exactly, as does the stated 7-of-8 interval coverage.

**Candour in several places that most manuscripts would not volunteer.** The Theorem-3 spectral-gap concession appears in four locations. Theorem 5R is explicitly labelled a parallel extension that does not reduce to Theorem 5 at $\phi=0$, which is arithmetically correct. Corollary 3 is downgraded from a bound to a first-order asymptotic with the remainder sign declared uncontrolled. Corollary 1's unflattering full-domain error (−48.6%) is printed alongside the narrow-band 15.8%, and both numbers reproduce exactly from the authors' own deposited grid. The Omicron bootstrap discard is disclosed together with its direction of bias. The finalized-vintage upper-bound caveat appears in four locations. The paper repeatedly reports its own weak results rather than suppressing them — the 0.27 skill ratio in the Theorem 5R renewal check is another example.

**The bibliography count is exactly as claimed.** 66 entries stored, 42 cited, 0 dangling, 24 orphans, corroborated against the compiled PDF (42 numbered items, zero `[?]`). The letter's claimed 24 orphans is right, and its "38 cited" is a correct description of the pre-revision state.

**The originality claim, as restated after Major 15, is honest.** Downgrading the contribution to a specific analytical instantiation of an existing architecture is a fair characterization of its size (§4.1). Major 15 was answered in good faith.

---

## 3. Weaknesses

Ranked by consequence.

### 3.1 The $\mathcal{E}_{\rm drift}$ term is on the wrong clock — a second dimensional error in the line that was supposed to fix the first

Major 1 corrected the exponent (`h_gen * v_drift ** 2` → `h_gen * v_drift` at `scripts_v2/error_budget_v2.py:134`), and that fix is real: the first power reproduces all 12 printed Table 4 cells to ≤0.6×10⁻⁴, and the squared form reproduces none. But the same expression carries a second, undisclosed error of the same class. `drift_volatility` (`error_budget_v2.py:86`) computes `np.diff(np.log(...))` on the **weekly** series, so $\hat v^2$ is a per-week log-scale variance — §4.4 item 2 says so itself. Theorem 5 accumulates $v^2$ over $h$ counted in **generations**. Under Theorem 5's own independent-increment premise the dimensionally correct accumulation is $h_{\rm gen}\Delta_g v^2_{\rm week} = h_{\rm week}v^2_{\rm week}$, whereas the code computes $h_{\rm gen}v^2_{\rm week}$ — too large by $7/\mu_g$.

This is not a uniform rescaling. It inflates the COVID and influenza rows by 1.49–2.33× and deflates the two RSV rows to 0.83×, because $\mu_g$ crosses 7 days between pathogens. It therefore distorts exactly the cross-pathogen comparison the error budget exists to make.

The consequence reaches both abstracts. Recomputing the closure with a consistent time scale:

| Row | Observed relMSE² (×10⁻⁴) | Residual as coded | Residual with consistent units |
|---|---|---|---|
| flu22 $h=1$ | 337.1 | −182.9 (−54.2%) | **+88.1 (+26.1%)** — sign flips |
| rsv24 $h=2$ | 33.8 | −100.5 (−297.5%) | −125.9 (−372.8%) |
| rsv25 $h=2$ | 22.1 | −30.5 (−138.2%) | −39.4 (−178.6%) |

The −54% negative residual quoted in both abstracts is an artefact of the unit error and becomes positive when the units are fixed; the other two worsen. The headline "9 of 12 positive, 6.2%–99.2%" and "−54% to −297%" do not survive the correction. The docstring at `error_budget_v2.py:19-24` asserts that the implemented form matches the printed formula, which is true of the power and silently false of the scale.

A further point about the interpretation. §4.4 attributes the negative residuals to a substantive cause — a 16-week drift-calibration band too wide at short-horizon working points. All three negatives are indeed drift-dominated (drift shares 148.0%, 377.1%, 202.1%), so the diagnosis is directionally right. But for flu22 $h=1$ the proximate cause is arithmetic, not physical, and attributing an arithmetic defect to a mechanism makes the defect look like a result. The remaining two negatives get larger under correction and are not explained by the calibration-band story either: at rsv24 $h=2$ the modelled terms exceed the observed total by a factor of about 4.7, which is not a local over-estimate but a failure of the identity to close in any useful sense on that row.

### 3.2 The "no crossing" result is an artefact of a one-sided detector

`scripts_v2/rolling_eval_v2.py:88` fires only on the predicate `s0 <= 1.0 < s1` — a rising curve. There is no `abs()`, no sign-change test, no downward branch anywhere in the file, and the same function serves both baselines, the point estimate (`:175`) and the bootstrap loop (`:160`). The local-linear skill curves fall, so the detector can never fire, and `rolling_results.json` records `crossing.lin` as `{"point": null, "ci95": null, "n_boot_ok": 0}` for all three waves. The `n_boot_ok: 0` field is the signature: it is not that zero resamples crossed, it is that the detector never fired at all.

Applying the manuscript's own interpolation formula to the manuscript's own deposited series gives crossings:

| Wave | Skill vs local-linear, $h=1\to8$ | Crosses 1.0 | Interpolated crossing |
|---|---|---|---|
| Delta | 3.112 → 0.711 (through 1.050 at $h=5$, 0.896 at $h=6$) | yes, downward | $h = 5.33$ weeks |
| Omicron | 1.062 → 0.076 | yes, downward | $h = 1.16$ weeks |
| flu22 | 0.947 → 0.160 | no — starts below 1 | — |

A missing value produced by an inapplicable detector was reported as an established negative result, in §4.5, the Figure 7 caption, the Table 5 note, both abstracts, and the response letter under Major 10. The rendered Figure 7 shows both crossings plainly; the contradiction is visible without any data at all, because the same sentence states that the model is worse at short range and better at long range, and a curve that goes from worse to better must cross.

Two further errors sit in that sentence. The claim of monotone decrease is false for flu22 ($h=3$ 0.409 → $h=4$ 0.422 rises), and the claim that the model is worse than this baseline at short range is false for flu22 (0.947 at $h=1$).

The corrected result also undercuts the paper's own framing. The true local-linear crossings (5.33 and 1.16 weeks) are comparable to the persistence crossings (3.52 and 1.82 weeks), so the two baselines agree far better than the manuscript claims, which weakens the baseline-sensitivity argument built on the erroneous nulls. The 1.8–5.3-week headline itself survives: it derives from `crossing.pers`, which is a genuine and correctly detected upward crossing in all three waves, and the manuscript now names persistence explicitly in all four locations.

### 3.3 Corollary 2's negative-binomial content is computed, fails, and goes unreported

This is the most serious scientific finding of the round. `scripts_v2/sim_verify_t3.py:161` computes Corollary 2's actual negative-binomial establishment probability $2\varepsilon/(R(1+R/k))$ and deposits 12 cells to `verify_t3.json["establishment_nb"]`. No script in the repository reads that key. Figure 3(b) plots `theory_2eps_over_R`, the Poisson limit $2\varepsilon/R$, from a Poisson-branch simulation (`sim_verify_t3.py:83`, called with `k=None`).

The unread block is exactly where agreement fails. The NB theory value falls inside the empirical 95% Beta interval in only 5 of 12 cells — all six `N500` cells fail, plus two `N1000` cells — with theory systematically below empirical. The plotted Poisson block passes 7 of 8.

Corollary 2 asserts that under substantial overdispersion ($k<1$) establishment probability is strongly nonlinearly suppressed. That $k$-dependence is the corollary's entire novel content over the classical $2\varepsilon/R$, and it is contradicted by the authors' own unreported data. The Figure 3(b) caption is honest about plotting the Poisson case, so this is not mislabelling. It is selective reporting of a negative result, which is materially more serious than a plotting error, and it is not mentioned anywhere in the manuscript or the letter.

### 3.4 Theorem 3's borrowed scaling is licensed for the exponent, not the mechanism

I obtained the Dolgoarshinnykh–Lalley full text (arXiv math/0512252, matching the published *J. Appl. Prob.* 43:892–898 version) and checked the transfer argument against verbatim source. Theorem 3 needs a relaxation time for a reflecting-boundary process. The cited literature supplies a first-passage excursion duration to extinction for an absorbing-boundary process.

- D&L §2.1: "The epidemic ends at the first time $T = T_N = t$ when $X_t = 0$ (note that state 0 is absorbing)."
- D&L's own Feller classification of the limit generator: "0 is an **exit** boundary and ∞ is a natural boundary in both cases." The manuscript's Major-9 concession calls $y=0$ a natural **entrance** boundary — the opposite type. My own independent Feller-index computation found the type varies with $\lambda$, changing character at $\lambda=(R+1)/2$; the primary source resolves it at the relevant $\lambda$ as exit/absorbing.
- The words `spectral`, `relaxation`, `eigenvalue`, `gap` and `reflecting` occur **zero** times in the whole D&L paper. Neither cited work computes a spectral gap. In Nåsell's framework the relevant eigenvalue is the decay parameter of the killed (Dirichlet) generator — a conditioned extinction rate, not the relaxation rate of a reflected process.
- D&L pre-emptively deny the merger the manuscript performs: "This phenomenon does not seem to be directly linked to the critical scaling in our Theorem 1", referring to precisely the Nåsell QSD scaling transition that the manuscript cites jointly with theirs as one result.
- The match with D&L's attenuated Feller generator is real and in fact better than the authors claim — but it holds only with $k$ set aside, because $(R+1)I$ is the bare Poisson birth–death variance. With overdispersion restored, nothing in the cited literature covers the limit.
- The reflecting wall is a singular perturbation, not a vanishing detail. The reflected speed density $m(y)\propto e^{\lambda y - y^2/2}/y$ is non-integrable at 0: total mass diverges like $\tfrac12\log N$ and concentrates at the wall (mass fraction below $y=0.01$ rises from 0.00 at $y_{\min}=10^{-2}$ to 0.83 at $10^{-12}$). There is no non-degenerate limiting stationary distribution for a gap to belong to. Numerically the reflecting gap is order 1 but drifts with the cutoff (2.51 at $y_{\min}=10^{-1}$, 1.18 at $10^{-12}$), while the Dirichlet decay parameter is stable at 1.1113. The claim is not numerically absurd, merely unproved and wall-dependent.

Separately, the inference from critical slowing down to horizon collapse is directionally backwards. A longer relaxation time means autocorrelation decays more slowly, which is stronger memory; in the early-warning-signals literature critical slowing down is detected as rising lag-1 autocorrelation, and stronger persistence makes short-horizon forecasting easier. The inference is also dimensionally inconsistent: $t_{\rm relax}\sim O(N^{1/2})$ grows with $N$, while a collapsing horizon requires a quantity that shrinks, and no normalization converting one into the other is exhibited. The genuine near-critical bad news is variance inflation, and the paper's own $\mathrm{CV}^2$ machinery already supplies that argument.

### 3.5 The bootstrap intervals carry no phase-specific information, yet are printed as 95% CIs

The letter's explanation of the df=3 mechanism is accurate; the consequence has not been drawn. Across seven phases spanning three pathogens, a 35× range of $I_0$ and a 50× range of $k_{\rm agg}$, the relative interval widths are constant to four significant figures: lower/point 0.5471–0.5476, upper/point 3.7558–3.7706. Total spread across all seven phases is 0.0006 on the lower ratio and 0.0148 on the upper. Simulating the pivotal quantity $1/\sqrt{\chi^2_3/3}$ over 4×10⁵ draws reproduces them (2.5th percentile 0.5671, 97.5th 3.7327). Multiplying $I_0$ by ten moves $h^*$ by 0.02%–0.26%, so the data essentially does not enter the horizon.

A quantity constant across every phase in the study is not an uncertainty interval for a phase; it is a redisplay of "df = 3" multiplied by the point estimate. Publishing it in a column headed 95% CI in Tables 2, 3 and 5, and drawing it as error bars in Figure 5, communicates phase-specific uncertainty that provably is not present, and invites exactly the cross-phase reading the text forbids one paragraph later. The authors' stated reason for not fixing this — declining to destabilize a frozen protocol mid-review — is a good reason not to re-estimate; it is not a reason to keep printing a column whose header means something other than its contents.

### 3.6 Text-versus-artefact desynchronization persists in the prose that interprets the tables

The single-source mechanism covers the five table fragments and nothing else. The prose is still hand-maintained and still drifting.

- **§4.3 carries three stale numbers, not one.** Table 3 was correctly regenerated (the flu22 decline row now prints 11.1 weeks, and 34.5 does not appear in the table). But §4.3's prose still prints the subcritical root range "11.6--34.5 周" — true range from the deposited JSON is 7.5–33.5, and neither printed endpoint is a Table 3 root: 34.5 is the retired hand-typed value the letter says was eliminated, and 11.6 is Delta's bootstrap CI lower bound from Table 2. The same sentence attributes $R=0.9570$ to the Omicron decline (deposited value 0.8690) and $R=0.9621$ to the influenza decline (deposited value 0.8359). Neither $R$ value appears in any row of any deposited file.
- **Two mutually inconsistent bias bands.** Lemma 3 prints the first-order bias as 16.7%–18.0%; §4.2 prints 16.5%–17.6% for the same quantity. The true per-phase values are 16.737%–16.930%. The band is analytically pinned: with $\mathrm{CV}^2$ negligible the exact root solves $P(x)=\tau^2$ in $x=h^*s$ alone, giving $x=0.427575$ — which is the paper's own $hs\approx0.43$ invariant — while the first-order counterpart gives $hs=\tau=0.5$, so the bias tends to 16.94% as $\mathrm{CV}^2\to0$ and a positive $\mathrm{CV}^2$ moves it slightly down. Neither printed band can reach 18.0%.
- **A phantom marker.** The Table 3 note defines `‡` and §4.2 directs readers to the `‡` rows of Table 3, but no cell in Table 3 reaches the 1000 cap (maximum $k_{\rm agg}$ is 698.4). Both references point at an empty set. The generator can emit the marker; the condition never fires.
- **Figure 1, inline TikZ and therefore outside the fragment mechanism entirely, still carries the pre-repair claim.** Its Theorem-5R cell asserts cross-scale invariance unconditionally, while §2.1's revised text makes that invariance conditional on $\mathrm{CV}^2(h^*)\ll\tau^2$ with $O(10\%)$ error otherwise. §2.1's own illustrative example for the $O(10\%)$ case points at Table 3 decline rows, where $R<1$, $\mathrm{CV}^2_\infty$ is undefined and the table prints `--`.

The consistency suite cannot catch any of this. Its body-text coverage is one abstract range plus an 18-item literal blacklist, and the blacklist is a patch log of prior rounds rather than a test: every entry is a specific literal from a previous review, so it asserts that last round's errors are gone and cannot detect a new one. It also cannot catch wrong-but-consistent numbers, because fragment-against-JSON equality is preserved when the JSON itself is wrong — which is exactly the situation in §3.1.

### 3.7 An undisclosed sample-size reduction, and a verification gate below its own floor

`table4_budget.json` records `n_origins: 3` for both rsv24 rows, while §4.4 states $M=6$ flatly for every phase. `error_budget_v2.py:121-123` silently skips an origin whose target week is more than 3 days from the requested date. The row carrying the paper's largest negative residual (−297%) therefore averages over three origins, not six, and neither Table 4, its note, §4.4 nor the letter discloses it.

The non-blank-pixel test the letter cites as a safety net (`check_consistency.py:96-100`) takes the modal RGB triple as background and requires the remainder to exceed 5%. A fully decorated but data-free reconstruction of `gen_fig_t3`'s exact geometry — same figure size and dpi, same CJK tick labels, both subplot titles, suptitle, grid, reference line, legend entries built from empty arrays — measures 0.0580 and **passes**. Decoration alone contributes about 5.8% ink, so the threshold sits below the floor it is meant to exceed, with a 16% margin. The specific bug the test was added to catch (zero-height bars) scores 0.0461 in a single-panel reconstruction and would have been caught; adding the second panel to Figure 3 raised the decoration floor above the gate, making the test weaker on the rewritten figure than on the original. The actual protection for Figure 3 is the `raise`, not the pixel test. And panel (b) is gated by `if elabels:` with no `else` clause, so the original failure mode — a fully decorated blank subplot in a figure that is still written, with a zero exit code — remains live in the second half of the same function.

### 3.8 Citation-integrity defects introduced by the Major-15 fix

Two of the four newly added references carry fabricated bibliographic detail (§4.3 below). The most serious is `nemcova2026unjustified`, which misstates three of five author given names in a way that makes the compiled PDF misattribute a real paper to two uninvolved, well-known researchers in this field. A third defect — the Kéfi accent — is claimed in the letter as completed and was never made.

---

## 4. Detailed comments

### Major

#### M-1. Verdict table over the Round-13 response letter — Major items

Verdict key: **Resolved** — the repair is real and I verified it. **Relabelled** — the wording or presentation changed while the underlying defect stands, and the letter says so. **Open** — the item is not resolved, or the repair introduced or left a defect of comparable weight.

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 1 | `E_drift` dimensional error | **Open** | Exponent fix real and verified (first power reproduces all 12 cells, squared form reproduces none). A second dimensional error of the same class survives in the same line: $\hat v^2$ is per-week, $h$ is in generations. Inflates COVID/flu rows 1.49–2.33×, deflates RSV rows to 0.83×. §3.1 |
| 2 | Printed Table 4 was not the JSON's table | **Resolved, but its numbers are invalidated by item 1** | Headline range identical across Chinese abstract, English abstract, Fig 6 caption and §6; verified cell by cell (9 positives, min 6.20, max 99.17, 8 above 40%); neither retired range appears in `main.tex`. The range itself must be regenerated once item 1 is fixed |
| 3 | P column low by 10× in nine rows | **Resolved** | $P=(h_{\rm gen}s)^2$ reproduces every printed cell (Delta $h=1$: 4.04 vs 4.0; Omicron $h=4$: 468.87 vs 468.9). Fragment now `\input` from generated source |
| 4 | Three incompatible definitions of $I_0$ | **Resolved** | One definition per quantity, both stated as an intentional contrast in §4.4 and the Table 4 note. My CV² recomputation reproduces the printed cells only with window-mean $I_0$, confirming which definition the generator uses |
| 5 | Single-source mechanism disconnected from the compiled document | **Resolved** | Five `\input`s present, all fragments trace to JSON, byte-equality assertion is real, no hand-typed Table 2–6 rows survive, `h*_approx` column bug genuinely fixed. Correct structural fix for the previous round's root cause |
| 6 | Extra $R^2$ in `C_req` | **Resolved** | `pipeline.py:230` carries no $R^2$; $C_{\rm req}$ exact for all seven phases; ratios 1.476→1.48 and 0.221→0.22. Reinstating the old $R^2$ reproduces the retired 2.46 exactly, corroborating the diagnosis |
| 7 | Cramér–Rao category mismatch | **Relabelled** (acceptable, with one required addition) | "违背" appears in `main.tex` only inside its own negation; bridging paragraph present and accurate. The category error itself is untouched and conceded. §4.4 below: the aggregation-inflation term is unbounded and the diagnostic's single conclusion sits on it |
| 8 | Figure 3 blank | **Resolved** — but see §3.3 | Non-blank, two panels, `raise` guard real and build-fatal, all four caption ratios match `verify_t3.json`. The adjacent finding (unreported `establishment_nb`) is a separate and more serious defect |
| 9 | Spectral gap asserted, boundary lost in the limit | **Relabelled, and the relabelling does not hold** | Concession present in all four locations and the theorem title downgraded. But the concession names the wrong boundary type, neither cited work computes a spectral gap, the $\sqrt N$ quantity in D&L is an excursion duration, and D&L expressly deny the link to Nåsell. §3.4 |
| 10 | Local-linear baseline read backwards; null crossings undisclosed | **Open — the claim is false** | Persistence-relative naming correctly applied in all four locations, and seasonal-naive crossings now reported. But "no crossing" is an artefact of a one-sided detector; Delta crosses at 5.33 wk and Omicron at 1.16 wk on the authors' own data and formula. The letter reproduces the error. §3.2 |
| 11 | Theorem 5R does not generalize Theorem 5 | **Resolved** | Environment title, bridging paragraph and object label all corrected; non-reduction at $\phi=0$ verified arithmetically ($s_e^2h$ against $h(v^2+1/k)$). Coherence is purchased by making 5R inert — no $\phi$ is estimated and it feeds no reported number |
| 12 | Bootstrap intervals carry no phase-specific information | **Relabelled** | The explanation and the prohibition are present and the claimed constants check out. But the intervals are still printed under a 95% CI header in three tables and drawn as error bars in Figure 5. Withdrawal is a presentational change requiring no re-estimation. §3.5 |
| 13 | Extrapolation up to 13.6× the window | **Open (definitional)** | The column exists with the stated values and the uniform natural-span concession is present. But the Table 2 note says "精确根" without saying which root; only the week reading reproduces the printed cells, while §2.1 argues the generation scale is the invariant cross-pathogen unit. On the generation reading six of seven phases breach the paper's own 4× doubt rule instead of three |
| 14 | MBB on 6 origins / 4 blocks; 34.8% Omicron discard | **Relabelled, incomplete** | Column present (975/652/907), direction-of-bias disclosure present verbatim, degeneracy stated and combinatorially correct (4 admissible blocks, ≤16 ordered resamples for $M=6$, $\ell=3$). But only the *interval* is flagged; the Omicron point estimate 1.82 wk inherits the same right-censoring, feeds Table 5's ratio column and supplies the abstract's lower endpoint |
| 15 | Precedents uncited | **Resolved for the precedents; two new citation defects introduced** | Wesselkamp and Castro cited in §1.2 with an explicit increment statement; Ho and Němcová cited at the $k_{\rm agg}$ paragraph. But two of the four new entries carry fabricated bibliographic detail (§4.3), and Drake 2006 remains under-credited (§4.1) |
| 16 | Abstract claims real-time skill from a finalized-vintage backtest | **Resolved** | Persistence-relative and upper-bound wording verified verbatim in the Chinese abstract, the English abstract, §6 and the Table 5 note |
| 17 | Chinese abstract lacked 探索性 | **Resolved** | Present, with 提出 rather than 确立 and the sample scope stated in-abstract; 探索性 occurs four times in `main.tex`; conclusion matches |
| 18 | Ceiling-truncated $k$ printed as a point estimate | **Resolved for Table 2; open for Table 3** | Table 2's rsv25 cell prints the marker with the note defining it as non-identifiability, and the sensitivity recomputes exactly (0.736% → 0.735% as $k\to\infty$). But the claimed extension to Table 3's decline-phase hits describes a repair to an empty set — no cell in Table 3 reaches the cap |
| 19 | Rounding direction in $h^*_{\rm stoch}$ | **Resolved** | Floor printed with the justification and the explicit note that the ceiling would overstate predictability. Note the property is never exercised empirically — it requires $\tau^2\le\mathrm{CV}^2_\infty$, false in all seven phases |

**Major tally: 9 resolved (3, 4, 5, 6, 8, 11, 16, 17, 19), 1 resolved but pending regeneration (2), 4 relabelled with the underlying defect disclosed and standing (7, 9, 12, 14), 5 open (1, 10, 13, 15, 18).**

#### M-2. Verdict table over the Round-13 response letter — Minor items

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 1 | "Orthogonal" misuse | **Resolved** | Exactly five occurrences of 正交 remain, all legitimate (total-variance decomposition at Lemma 1 and Appendix A; martingale-difference orthogonality at Theorem 1 sketch, Theorem 5 sketch, Appendix E). The letter says three were retained; five survive because two usages appear in both a body sketch and its appendix. A miscount, not a defect |
| 2 | Theorem 1 property 1 | **Resolved** | The exact iff condition and the explicit necessary-not-sufficient label for the $s^2$ form are both present, with the <0.2% gap at $s\le0.04$ |
| 3 | $\sigma^2$ three definitions | **Resolved** | Theorem 3's relationship paragraph is present verbatim in substance, including the deliberate omission of $k$ and the parallel-model statement. The consequence the letter does not draw: Theorem 3 therefore cannot describe the near-critical behaviour of the paper's own generating process |
| 4 | Lemma 2 $R>1$ qualification | **Resolved** | Moved into the statement, with divergence noted for $R\le1$ and the near-critical clause reading $R\to1^+$ |
| 5 | Table 3 CV² column | **Resolved** | All four $R<1$ rows print `--`; the three $R>1$ rows print 0.06/0.09/0.23/0.64%; the unreproducible 1.34% plateau row is gone |
| 6 | Decline-phase roots as horizons | **Open** | The table was regenerated as claimed (11.1 weeks, markers and regime-shift note present, 34.5 absent from the table). The prose was not: §4.3 still carries the retired range and, beyond what the letter or any prior round recorded, two $R$ values that appear in no deposited file. §3.6 |
| 7 | Cross-scale equivalence overstated | **Resolved with a dangling example** | The conditional restatement is present with both error figures and the $k$ caveat. Its $O(10\%)$ illustration points at Table 3 decline rows where the quantity is undefined and printed `--`. Figure 1 was not updated alongside the prose |
| 8 | Unbiased vs lognormal estimator | **Resolved** | Figure 1 carries the lognormal label, Lemma 3 builds $P$ from the lognormal moment identity, and the §4.2 bridging sentence makes the unbiased-MLE distinction |
| 9 | Theorem 5 conditioning unused | **Resolved** | The independence premise is stated explicitly in the sketch, with the geometric-decay argument for the non-extinction conditioning; Appendix E repeats the convention |
| 10 | Corollary 3 | **Resolved** | Symbol split present; the downgrade to a first-order asymptotic in the $\sim$ sense appears in statement, sketch and Appendix E; Lemma 2's title corrected from a lower bound to an asymptotic saturation limit |
| 11 | Table 6 $\tau=0.50$ column vs Table 2 | **Resolved** | Row-for-row identity verified; summary row reads 7.9–21.2; the sublinearity re-derives as 2.816–2.873× against the printed 2.82–2.87 |
| 12 | Four vs five weeks | **Resolved** | §4.1 states both windows and names them two protocols with different purposes; each table's note states its own window |
| 13 | Figure 2 / 6 captions | **Resolved** | Verified by looking at the rendered pages: Figure 2's colours, marker and axes match its caption; Figure 6's stacked bars match, with $\mathcal{E}_{\rm misspec}$ correctly absent from the stack and the bars exceeding 100% at exactly the three negative-residual configurations |
| 14 | New overstatements | **Resolved** | 严密自洽 and 完全实测 both have zero occurrences; Corollary 1's fidelity claim is qualified |
| 15 | 第一性原理 | **Resolved** | Zero occurrences; §1.3 bullet 1, §5.2 and the §6 opening all reworded to model-scoped framing |
| 16 | Corollary 1 full-domain error | **Open** | Both figures are printed as claimed and both reproduce exactly from the deposited grid, and the separator sentence distinguishing the two approximations is present. But the supercritical bias band is printed twice with mutually inconsistent values, neither of which is the true 16.74%–16.93%. §3.6 |
| 17 | Bibliographic errors | **Open** | `parag2026threshold` pages 185 confirmed; `chan2026estimating` article number 16890 confirmed; the Lloyd-Smith rejoinder is correct and should be accepted; the brace repair is real in the compiled copy. But the Kéfi accent repair was never made, and the three-missing-DOI count understates the true 8 of 42. §4.3 |
| 18 | Line numbers in the response letter | **Resolved** | No line-number citations anywhere; all references by section, table, theorem, environment or script name. One section-number slip: Major 10 attributes the local-linear disclosure to §4.4 when it is in §4.5 |

**Minor tally: 14 resolved (1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 18), 1 resolved with a dangling example (7), 3 open (6, 16, 17).**

#### M-3. Is the authors' own honest-limitations accounting acceptable at this stage?

The letter's Part III is accurate rather than evasive. I verified each concession against the manuscript's actual state, and every one of them describes the manuscript correctly. That is worth stating plainly, because it is not the norm at round 13. My judgement on each:

| Deferred item | Letter's position | My judgement |
|---|---|---|
| **Major 7** — no NB-likelihood re-estimation of $\hat R$ | Repaired at the wording and bridging level plus the quantitative correction to 1.48; model-matched estimator declared future work | **Acceptable, with one required addition.** The diagnostic now carries proportionate language, draws only a weak conclusion, and is not load-bearing for any headline. An NB-GLM or renewal MLE would be a methodological upgrade, not a defect repair. But the one conclusion drawn — rsv25 at 1.48 against rsv24 at 0.22, a factor of about 6.7 — rests on an aggregation-inflation term the authors identify and do not bound. Require either a bound or an explicit statement that the contrast is not robust to it. That is a one-paragraph fix |
| **Major 12 / 14** — window widening, Bayesian propagation, block-length sensitivity, per-origin crossings | Disclosed as limitations rather than implemented, to avoid destabilizing a frozen protocol mid-review | **Acceptable for the redesign; not acceptable for the presentation**, and the letter conflates the two. Declining to re-estimate is defensible. But withdrawing the df=3 intervals (§3.5) and flagging the Omicron point estimate as censored (§3.2, §M-1 item 14) require no re-estimation at all, and deleting a column is a smaller change than the re-analysis the authors declined. Block-length sensitivity may be deferred, but the ≤16-resample support size should be stated as a hard resolution limit rather than a caveat: with at most 16 atoms, no block length rescues a 2.5th percentile |
| **Major 18** — raw pre-truncation second moments and SEs | Estimator returns the capped value and discards the raw quantity | **Acceptable.** `pipeline.py:85` confirms the estimator genuinely discards it, so the self-report is accurate, and the sensitivity argument is sound and recomputes exactly. The truncation does not matter for any reported number. But the *related* claim is not deferrable: the phantom Table 3 marker references must be deleted or the prose corrected, because that is a dangling reference, not a deferred analysis |
| **Major 3 legacy** — byte-exact raw-vintage reconstruction, prospective multi-season evaluation | Unchanged declared limitations | **Acceptable.** Prospective multi-season validation is future work by definition, and both are declared in §4.5 and §6 with the finalized-vintage upper-bound caveat attached |
| **Minor 17** — three DOIs left blank | Not added rather than filled from memory | **The policy is right and should be commended.** Declining to guess a DOI is the correct call. But the accounting is understated: 8 of 42 cited entries lack a DOI, not 3. Four of the additional five are books or proceedings where a DOI is optional; `grassberger1983critical` is a journal article and a genuine omission. And the policy was not applied to author names — see §3.8 and §4.3, which is the more serious failure of the same kind |
| **Reference hygiene** — 24 remaining orphans | Untouched, documentation work not bundled into a numerical repair commit | **Acceptable as housekeeping.** 24 is exactly right, and orphan entries are invisible in the compiled document (`unsrtnat` emits only cited entries; the PDF renders exactly 42 numbered items with zero unresolved markers). But the four-way `.bib` desynchronization is not housekeeping and should be a required fix (§4.3) |
| **Self-reported mid-revision source corruption** | Restored from commit `4035821`, every change re-applied and re-verified | **The disclosure is creditable and the predicted failure mode is exactly what this review found.** Manual re-application after a restore is precisely the process that produces regenerated-table-versus-stale-prose desynchronization, and §3.6's defects are all of that class. However, the two most serious findings here are not of that class: the drift time-scale error and the one-sided crossing detector are live code defects that would survive any number of clean rebuilds. The corruption narrative explains the text defects; it does not account for the two that matter most, and the editor should not accept it as covering them |

**Summary judgement on the deferrals: acceptable in substance, not in presentation.** Every deferral of *new analysis* is defensible and honestly declared. What is not acceptable is the use of "frozen protocol" reasoning to defer changes that require no analysis at all — withdrawing a misleading column, flagging a censored point estimate, deleting a reference to rows that do not exist, and correcting a bibliography entry against a resolver.

#### M-4. On the contribution claim as restated after Major 15 — real, but thinner than the paper implies

The revised §1.2 states the increment as a specific analytical instantiation, assembling the potential-versus-relative forecast-limit architecture (Wesselkamp et al. 2025) and the narrow-probabilistic-window picture (Castro et al. 2020) into one solvable closed form under NB branching with lognormal parameter propagation, with seven-phase calibration and a sample-size diagnostic. I searched the ecological forecast-horizon literature, the epidemic forecastability literature and the near-critical branching literature, and read the closest priors in full where the abstract did not settle the question.

| Prior | Already establishes | Does not contain |
|---|---|---|
| **Petchey et al. 2015**, *Ecol. Lett.* 18(7):597–611 | The horizon concept itself: the lead time at which a forecast-proficiency measure first crosses an application-relevant threshold | Any epidemic generating process; no closed form; no NB or parameter-propagation term |
| **Wesselkamp et al. 2025**, *Methods Ecol. Evol.* 16(7):1521–1541 | The architecture the manuscript borrows: potential, absolute and relative forecast limits, unified, plus the triad — verification reference, scoring function, error tolerance — required to define any limit | Not epidemiological; the potential limit is obtained by simulation and ensembles, not by an analytic CV² |
| **Drake 2006**, *PLoS Med.* 3(1):e3 | **The closest ancestor.** An analytic CV-based predictability limit derived from a stochastic branching epidemic, with closed-form mean and variance of final outbreak size and a critical $R_0^*$ separating predictable from unpredictable outbreaks | No horizon — the CV=1 benchmark is a condition on parameters, not a lead time. No parameter uncertainty in the limit: explicitly, the measure assumes the rate parameters are known exactly. No overdispersion; $k$ is absent |
| **Castro et al. 2020**, *PNAS* 117(42):26190–26196 | The narrow-probabilistic-window picture — the qualitative content of $P(h)$ | Numerical sensitivity on SIR-type dynamics only; no closed-form $P(h)$, no propagation law, no tolerance equation |
| **Penn et al. 2023**, *Commun. Phys.* 6:146 | The split between intrinsic randomness and statistical uncertainty — the same conceptual division as CV² versus $P$ | Never converted into a horizon, a tolerance, or a closed-form $h^*$ |
| **Parag & Donnelly 2022** | Fisher-information limits on inferring $R_t$ from noisy epidemic curves — the ancestor of Theorem 4 | Bounds inference precision, not forecast lead time; no $h^*$ |

I could not find a prior work that writes $\mathrm{CV}^2(h)+P(h)\le\tau^2$ under NB branching with lognormal propagation and solves it for $h^*$. The assembly appears to be the authors' own, and the revised wording is a fair characterization of its size. But it is thin in three specific ways the paper should concede rather than leave a reader to infer.

1. **The assembly is mathematically light.** Given a textbook Galton–Watson second-moment recursion and the lognormal moment identity, both terms are two lines of algebra, and the assembly is a single addition — which, as §3.4 of my technical audit establishes, is not orthogonality earned from the model but independence assumed into existence by (A4). Strip (A4) and the closed form does not exist.
2. **The closed form is not what is used.** Theorem 1's headline analytic $h^*$ is biased by 16.7%–16.9% against the exact root, and Corollary 1's near-critical form errs by up to 48.6% on the authors' own grid. Every empirical number in the paper comes from a Brent numerical root of two elementary functions, which required no new theory.
3. **The NB half contributes nothing to any reported horizon.** With $\mathrm{CV}^2$ at most 0.74% of $\tau^2$ and $h^*\approx\tau/s$ throughout, the epidemiologically distinctive half of the increment — the half carrying $k$ and superspreading — is inert at every working point in the paper. What determines all seven horizons is $\tau$ divided by an OLS slope standard error.

**One precedent is under-credited.** Drake 2006 is cited only in a subordinate clause. But Drake already derived an analytic CV-based predictability limit from a stochastic branching epidemic and already identified a critical $R_0$ separating predictable from unpredictable outbreaks — structurally the same move as the paper's CV²-floor existence condition, and the single most direct precedent for Lemma 2 and Theorem 1 property 1. The honest framing is statable in one sentence: Drake bounds predictability by demographic noise alone at known parameters and produces no lead time; this paper adds the estimation-error term and thereby converts a static CV threshold into a horizon. That sentence belongs in §1.2.

What is genuinely left over after the five priors is: the explicit lognormal $P(h)$ and its exact-versus-first-order gap; the $hs\approx0.43$ tolerance invariant at $\tau=0.5$; the seven-phase cross-pathogen empirical calibration on one common footing; and the $h^*/W$ extrapolation diagnostic. The last two are the strongest genuinely new material and they are empirical. The contribution is empirical calibration wearing a theoretical frame, and the paper would be stronger for saying so.

#### M-5. Theorem 3 — required changes

Both entries are bibliographically exact and were verified against Crossref: Nåsell 1999, *Math. Biosci.* 156(1-2):21–40; Dolgoarshinnykh & Lalley 2006, *J. Appl. Prob.* 43(3):892–898. This is not a citation-integrity problem but an attribution-of-content problem, developed in §3.4. Note also that D&L themselves rely on a **different** Nåsell 1999 paper (*JRSS-B* 61:309–330, on time to extinction) than the one cited here.

Required: correct the boundary type from entrance to exit/absorbing; restate Theorem 3 as identifying the critical time scale $\sqrt N$ by analogy with D&L; and either remove the $O(1)$ spectral-gap claim, prove it directly for the reflected generator with honest treatment of the log-divergent speed measure, or flag it explicitly as a conjecture. Stop citing Nåsell and D&L jointly as establishing one result, since D&L expressly deny the link. State that the D&L match requires setting $k$ aside, so the borrowed theory does not cover the paper's own model. Withdraw or re-derive the horizon-collapse inference, using the paper's own CV² machinery, which supplies the correct near-critical argument.

#### M-6. Citation integrity

All four newly added citations resolve to real, extant, correctly dated publications. Nothing is fabricated at the work level. But two of the four carry fabricated bibliographic detail.

| Entry | Verdict |
|---|---|
| `wesselkamp2025forecast` | **Clean.** DOI `10.1111/2041-210x.70049` resolves to *Methods Ecol. Evol.* 16(7):1521–1541, 2025; all six authors, volume, pages and year match the stored entry exactly |
| `castro2020predictability` | **Clean.** DOI `10.1073/pnas.2007868117` resolves to *PNAS* 117(42):26190–26196, 2020; every stored field matches |
| `ho2023simultaneous` | **Mis-paginated.** Real paper, correct title, journal, volume, year and all six authors. But the entry gives issue 1 and pages 62–70 where the record is **issue 2, pages 201–205**. A ~140-page displacement is not a typo; it is a different location. The BibTeX key also does not match the title. The wrong pages print in the compiled PDF |
| `nemcova2026unjustified` | **Not fabricated, not mis-dated — but three of five author given names are wrong.** Title, journal (*Epidemiology and Infection*), volume 154, year 2026 and DOI `10.1017/s0950268826101605` are all correct. However, Goldstein is **Isaac H.**, not Edward; Sebastian is **Jessalyn**, not Tom; Minin is **Volodymyr M.**, not Vladimir N. The article number is **e79**, not e12 |

The Němcová case deserves emphasis. Edward Goldstein and Vladimir Minin are both real, well-known researchers in epidemiology and statistics who are not authors of this paper. Under `unsrtnat` these names print in the compiled bibliography, so the shipped PDF misattributes a paper to two uninvolved researchers. This is the same "filled in from memory" failure mode the letter says it guarded against for DOIs; the guard was applied to DOIs and not to author names. The record is open-access CC-BY with 49 references and is trivially checkable.

Minor-17 spot-checks against Crossref: `parag2026threshold` pages→185 **confirmed** (*Commun. Phys.* 9, article 185, 2026); `chan2026estimating` article number 16890 **confirmed** (*Sci. Rep.* 16, 2026); `white2026forecastability` **confirmed** exact; Petchey's volume, issue, pages and year **confirmed**. The three admitted missing DOIs are an accurate self-report, though the true count is **8 of 42 cited entries**, not 3. The **Kéfi accent repair was never made**: `references.bib:393` still reads `K{'e}fi` with no backslash, `K{\'e}fi` has zero occurrences, and the shipped PDF reference [19] prints "Sonia K'efi". This is the letter's one outright false repair claim, and it is visible in the compiled artefact.

**The Lloyd-Smith rejoinder is correct and should be accepted.** `lloyd-smith2005superspreading` (*Nature* 438(7066):355–359, Lloyd-Smith, Schreiber, Kopp & Getz) and `lloydsmith2005should` (*TREE* 20(9):511–519, Lloyd-Smith, Cross, Briggs, Daugherty, Getz et al.) are two genuinely distinct 2005 papers — different titles, journals, volumes, page ranges and coauthor sets. No merge is warranted and the original objection was mistaken. There is, however, a point the letter does not make and that cuts the other way: **both entries are orphans**, cited nowhere in `main.tex`, so neither appears in the compiled bibliography. Given that the paper's entire overdispersion apparatus — Lemma 2's $1+R/k$, Corollary 3's $1/k$ floor, $k_{\rm agg}$ — descends from the superspreading construct, Lloyd-Smith 2005 (Nature) going uncited is itself a defect. The authors won a correct argument about two entries that do no work in the paper, while the paper uses the concept without crediting its source.

**A live desynchronization hazard.** Four `.bib` files share the basename `references` in the repository, and only the copy colocated with the journal template carries the Minor-17 repairs. The repo-root copy has the same 66 keys but is the pre-repair version: every entry still carries the stray duplicate brace, `parag2026threshold` still has `pages={45}` — the exact error the letter says was fixed — and `chan2026estimating` has no `pages` field at all. `references_working_library.bib` has zero key overlap with the compiled bib and does not contain the 24 orphans, so the "move uncited entries to a working library" step was half-executed. Two of the three `main.tex` variants in the repository write `\bibliography{references}` with no sibling `.bib` and therefore resolve to the stale root file. Any build from the repo root silently reintroduces the error. Make one file canonical.

### Minor

The items below are individually correctable and do not affect the recommendation, but each is a concrete defect with a located source.

- **(A4) is the load-bearing assumption of the whole paper, and §4.5 concedes it is violated in the empirical evaluation.** Both $\hat R_t$ and $I_{0,t}$ are estimated online from the same rolling window, so they share history in finite samples. The decomposition on which Table 4's accounting identity rests is derived under an assumption the paper's own protocol breaks. This is disclosed and the two-tier comparison is labelled exploratory, which is an acceptable disclosure — but §2.2 should acknowledge it where the assumption is introduced, not only in §4.5. Readers should note the theory-to-data gap is assumption-level, not merely statistical.
- **Theorem 4's unbiasedness premise is contradicted elsewhere in the paper.** The bound is stated for an unbiased $\hat R$. Minor 8's own repair establishes that $\hat R=\exp(\Delta_g\hat b)$ is lognormal with $\mathbb E[Y]=e^{s^2/2}\ne1$, i.e. explicitly biased, with the $O(s^2)$ bias absorbed into $P(h)$. At $s\le0.023$ the bias is numerically negligible (below $3\times10^{-4}$) and changes no number, but the bridging paragraph should name unbiasedness as the specific broken premise rather than saying only that the estimators differ.
- **$C_{\rm req}$ is compared against a non-commensurable denominator.** The requirement is a count of independent, fully observed transmission clusters; the comparison quantity is the sum of five weekly aggregate case counts under an explicitly most-optimistic mapping of one case to one cluster. The paper states this and states the direction, which is correct and honest, but the resulting "1.48×" is a ratio of a cluster-count requirement to a case count — a bound on a bound — and the phrasing invites over-reading.
- **The aggregation-inflation term is unbounded.** §4.2 correctly states that weekly aggregation and testing smoothing depress the OLS residual and therefore inflate $C_{\rm req}$, but gives no magnitude. The diagnostic's only substantive conclusion is that rsv25 exceeds 1 while rsv24 does not, a factor of about 6.7. If aggregation inflates $C_{\rm req}$ by more than about 1.5× for rsv25, the qualitative finding reverses. Bound it, or state that the contrast is not robust to it.
- **$h^*/W$ is week-based while the paper argues the generation scale is the invariant unit.** Only the week reading reproduces the printed cells (21.2/5→4.2 through 67.8/5→13.6). On the generation reading the factors are 6.3, 3.7, 4.3, 4.7, 6.8, 6.9 and 11.4, so six of seven phases breach the paper's own "doubt it above 4×" rule rather than three, with only Omicron surviving. There is a second reason to prefer the generation reading: three of the seven $\mu_g$ values are literature proxies from other lineages, and week-scale horizons scale strictly linearly in $\mu_g$ by the paper's own sensitivity result, so the week column carries the proxy's error directly while the generation column does not.
- **Theorem 5R is now coherent but inert.** It shares no parameter with anything estimated, no $\phi$ is fitted anywhere, and it feeds no number in Tables 2–6. Its asymptotic form also overestimates substantially at finite $h$ for large $\phi$ (at $\phi=0.9$, $h=20$: exact 11.68 against asymptotic 20.00), which the manuscript does not flag; this affects no reported number precisely because 5R is inert. The Major-11 resolution is presentational.
- **Corollary 1's error grid is one-sided.** Both printed figures reproduce exactly from the deposited grid, but the grid samples only supercritical $\varepsilon>0$, while Corollary 1 is stated for the near-critical regime generally and §4.3 applies near-critical reasoning to windows with $R<1$. On a grid extended to negative $\varepsilon$ the error reaches +124.6%. Since the paper commits to the exact root in all empirics — which I verified — this propagates into no reported number, but the declared 48.6% is the worst case of a one-sided grid, not of the corollary's stated domain.
- **The JN.1 indicator splice is undisclosed as a limitation and unaddressed.** Table 2 treats JN.1 on the same footing as Delta and Omicron with $I_0$ labelled as weekly reported cases, but §4.1 states that JN.1 uses NHSN hospitalizations while the others use confirmed cases. These are different observables with different ascertainment and different clustering, receiving identical downstream treatment through the CV² and $C_{\rm req}$ machinery, with no sensitivity analysis. Neither the manuscript nor the letter raises it.
- **Two irreconcilable archival dates.** §4.1 gives a March 2026 snapshot for all three series; the Data Availability statement gives 2023-05-10 for the COVID series alongside the March 2026 snapshot. Not necessarily contradictory, but never reconciled, and the RSV 2025–26 window post-dates the 2023 archive.
- **The conclusion prints "Cram'er--Rao"** with a bare apostrophe where every other occurrence uses the correct accent macro. Cosmetic, but it is in the concluding sentence.
- **The Code Availability statement overstates the consistency suite's coverage.** It describes `check_consistency.py` as a consistency test between the body text and the JSON outputs. Its actual body-text coverage is one abstract range plus 18 literal strings; everything else it checks is fragment against fragment. Narrow the description, and state that Figures 3 and 7 carry no numerical assertion of any kind. Relatedly, a `--fast` build skips the verification suites and the Figure-3 simulator but still runs and passes step 8, so a fast build green-lights Figures 3 and 7 against arbitrarily stale JSON.
- **`make_all_figures_v2.py` advertises figures its `main()` does not generate** (Figures 6 and 7 are side effects of other pipeline steps), so the file header's claim that every figure has exactly one generator is only accidentally true.

### Required corrections, ranked

**Must fix — affects reported numbers.**

1. Correct $\mathcal{E}_{\rm drift}$ to a consistent time scale and regenerate `table4_budget.json`, `tables/table4_body.tex`, Table 4, Figure 6 and its caption, §4.4, §6, and **both abstracts**. The 9-of-12 tally, the 6.2%–99.2% range and the −54%-to−297% range all change.
2. Fix `cross_point` in `rolling_eval_v2.py` to detect crossings in both directions; report Delta at 5.33 weeks and Omicron at 1.16 weeks against the local-linear baseline; correct the no-crossing claim in §4.5, the Figure 7 caption, the Table 5 note and **both abstracts**. Also correct the false monotone-decrease and short-range-inferiority claims for flu22 in the same sentence. The corrected finding is more interesting than the erroneous null and should be presented as such.
3. Report or withdraw `establishment_nb`. Either plot or tabulate Corollary 2's NB predictions with the 5-of-12 agreement stated, or withdraw the $k$-dependence claim in the corollary.
4. Correct §4.3's three stale numbers: the subcritical root range, and the two $R$ values that appear in no deposited file.
5. Disclose the $M=3$ origin count on the two rsv24 rows of Table 4, or drop those rows.
6. Correct `nemcova2026unjustified` (three author given names, article number) and `ho2023simultaneous` (issue and pages), and re-verify every remaining entry against a resolver rather than from memory.

**Must fix — presentational, requiring no re-analysis.**

7. Withdraw the df=3 intervals from Tables 2, 3 and 5 and from Figure 5, replacing them with a single stated multiplier reported once in the text.
8. Flag the Omicron Tier-2 point estimate as censored, not only its interval, and state the ≤16-resample support size as a hard resolution limit.
9. Reconcile the two supercritical bias bands to the true 16.74%–16.93%.
10. Delete the phantom Table 3 marker references in §4.2 and the Table 3 note.
11. State which root $h^*/W$ uses in the Table 2 note, and report the generation-scale factors alongside.
12. Fix the Kéfi accent; restate the missing-DOI count as 8 of 42; cite Lloyd-Smith 2005 (Nature) where the overdispersion machinery is introduced.
13. Make one `.bib` file canonical, since the repo-root copy still contains `pages={45}` and the brace corruption.
14. Narrow the Code Availability description of `check_consistency.py`, and state that Figures 3 and 7 have no numerical check.
15. Update Figure 1's TikZ to carry the conditional scale-invariance claim, and replace §2.1's $O(10\%)$ example with rows where the quantity is defined.

**Should address — framing and interpretation.**

16. Theorem 3: correct the boundary type, restate the borrow as a time-scale analogy, resolve the spectral-gap claim, and stop citing Nåsell and D&L jointly (§M-5).
17. Withdraw or re-derive the horizon-collapse inference using the CV² machinery.
18. Bound the aggregation-inflation term, or state that the rsv25/rsv24 contrast is not robust to it.
19. Acknowledge (A4)'s empirical violation in §2.2, where the assumption is introduced.
20. Credit Drake 2006 as the direct precedent it is, with the one-sentence increment statement in §M-4.
21. Address the JN.1 indicator splice with a sensitivity analysis or an explicit limitation.
22. Fix the unguarded panel (b) in `gen_fig_t3`, and stop citing the pixel test as a data-integrity check.

### Where I could not verify, and why

Stated explicitly so the editor can weigh what is established against what is taken on trust.

- **The estimation step itself is unverified.** `data/processed/*_final_weekly.csv.gz` are present in the repository, but I did not re-derive $R$, $s$, $k_{\rm agg}$ or $I_0$ from the raw CDC series. Everything downstream of Table 2 is verified against the deposited parameters; the map from surveillance data to those parameters is taken as given. The JN.1 indicator splice is therefore a data-provenance question I could not settle and that the authors must answer.
- **All of Table 3's parameters are internal-consistency checks only**, for the same reason: they come from per-window re-estimation on series I did not re-analyse. What I could check — that the flu22 growth row is identical to Table 2's, that all subcritical rows carry the correct markers, and that the prose range contradicts the printed roots — I did check.
- **I did not run `check_consistency.py` or any other repository script.** I read what the suite asserts and reasoned about what it cannot catch. Given the stale literals in §4.3 and the phantom marker, the suite would pass on a manuscript containing them, which is the point of §3.6 rather than a gap in this review.
- **The body of Nåsell (1999), *Math. Biosci.* 156:21–40, is paywalled and could not be retrieved.** Conclusions about Nåsell rest on D&L's characterization and on the standard absorbing-origin, QSD, killed-generator construction of that framework. The Theorem-3 finding does not depend on it: it turns on D&L's own verbatim sentences, which I have in full text.
- **Several prose-level quantities are unverifiable from any available artefact**, including the window case totals 9,341 and 22,047, the MLP and LightGBM benchmark ratios reported in §3.3 with no supporting figure or table, and the asserted 16–20-week natural single-season span, which carries no citation anywhere in the paper.
- **DOI resolution covered the load-bearing entries, not all 42.** The four Major-15 additions, the Minor-17 spot-checks and both Theorem-3 attributions were resolved against Crossref. The remaining entries were not, so the letter's claim that all 30 previously cited DOIs re-resolve is not independently confirmed here.
- **The rendered figures were inspected visually at 130 dpi**, which is how the Figure 7 crossings and the Figure 3 panels were confirmed. Rendering artefacts below that resolution would not have been caught.

---

## 5. Overall recommendation

### Major revision — score 4 / 10

**Rationale.** This round delivered a large body of genuine repair. The single-source table mechanism is the correct structural fix for the previous round's root cause and it works; Figure 3 is really fixed; nine Major items and fourteen Minor items verify cleanly, several by independent recomputation; the underlying mathematics is exact everywhere I re-derived it; and the response letter is honest about what it did not do — a claim I tested item by item rather than accepted. On the terms the previous round set, the authors did the work.

Three findings nonetheless block acceptance, and all three are new this round rather than carried over.

1. **A second dimensional error of the same class as Major 1, in the same line of code, surviving the round that fixed Major 1** — and it manufactures the −54% residual that both abstracts quote.
2. **A null result produced by a detector structurally incapable of firing on the curve it was applied to, reported as an established finding** in four manuscript locations plus both abstracts plus the letter.
3. **A negative result computed by the authors, deposited in their own repository, contradicting a headline claim of Corollary 2, and never reported.**

Item 3 is the most serious, because it is a reporting decision rather than a build artefact and the contrary evidence sits in the authors' own `verify_t3.json`. Items 1 and 2 are correctable, and in both cases the corrected version is more interesting than what is printed: crossings at 5.33 and 1.16 weeks are a better result than a null, and a positive residual at flu22 $h=1$ is a cleaner story than a sign anomaly attributed to a calibration band. But both propagate into both abstracts, which means the paper's summary-level claims are currently wrong in two independent places, for the third consecutive round.

**Why 4 rather than higher or lower.** The theory is correct, the empirical apparatus is careful and largely reproducible, the disclosure culture is better than most manuscripts at this stage, and the required work is bounded and specific — no new theory, no new data collection, and the largest single task is regenerating one table and one figure after a one-line unit correction. That rules out rejection. What rules out minor revision is that both abstracts currently carry wrong numbers arising from live code defects, that a headline theoretical claim is contradicted by unreported data in the authors' own repository, and that the verification apparatus the paper relies on cannot detect any of these classes: it checks fragment against JSON but never JSON against the physics, and its stale-literal blacklist is a record of past reviews rather than a test.

**Conditions for acceptance.** All items 1–15 in the required-corrections list above. In addition I ask the editor to require three process conditions: (a) a diff-level statement of every abstract sentence changed, since both abstracts have now carried erroneous headline numbers for three consecutive rounds; (b) a verification step that checks deposited JSON against the manuscript's own printed equations, including a dimensional check, rather than only fragment against JSON — the current suite would pass a manuscript containing every defect in §3; and (c) confirmation that every bibliography entry has been checked against a resolver rather than reconstructed from memory, with the same policy the authors correctly applied to DOIs extended to author names, issues and page ranges.

**What would move the score.** Fixing items 1–6 and correcting both abstracts moves this to 6. Adding the presentational fixes 7–15, particularly withdrawing the df=3 intervals, moves it to 7. Reaching 8 or above additionally requires the framing items — restating Theorem 3's borrow honestly, withdrawing the horizon-collapse inference, and stating plainly in §1.2 that the contribution is an empirical calibration within a borrowed architecture, with Drake 2006 credited as its direct precedent. A score above 8 would require the substantive analyses the authors have reasonably deferred: a model-matched NB-likelihood standard error for $\hat R$, and a prospective multi-season evaluation on real-time rather than finalized vintages.

I would be glad to review a revised version.

---

## Limitations of this review

**What was available.** The clone of the authors' public repository succeeded (single commit `50feeab`, no network degradation), and `uploads/main.tex` is byte-identical to `paper_cn_journal_template/main.tex` in that repository. This lifted the reproducibility ceiling that constrained earlier assessments: the five generated table fragments, all seven figures, the analysis scripts, the deposited JSON outputs and `references.bib` were all in hand. Every question previously marked as answerable only with the repository is decided in this report.

**What I ran and what I only read.** Every recomputation used code I wrote from scratch, operating on numbers transcribed out of the authors' JSON and `.tex` files. No script from the authors' repository was executed, imported or installed: `make_all.py`, `check_consistency.py`, `pipeline.py`, `error_budget_v2.py`, `verify_suite.py`, `sim_verify_t3.py`, `rolling_eval_v2.py`, `make_tables_v2.py` and `make_all_figures_v2.py` were read as text only. No serialized object was deserialized. Findings attributed to those scripts are therefore based on reading the source and on recomputing what the source claims to produce, not on running them — which means I can state what the code computes and what its outputs are, but not that the pipeline currently executes end to end.

**What I verified positively.** Tables 2, 4, 5 and 6 recomputed cell by cell from the paper's printed equations; Theorem 1's cross term by Monte Carlo; Theorems 2, 3, 5R and Corollaries 1 and 3 by symbolic or numerical re-derivation; the df=3 degeneracy by three independent routes; the moving-block combinatorics; the bibliography counts against the compiled PDF; the local-linear crossings from the authors' deposited rolling results using the authors' own interpolation formula; and the Dolgoarshinnykh–Lalley quotations from the full text of the preprint.

**What I could not verify** is set out in full in the "Where I could not verify, and why" subsection of §4: the estimation step from raw CDC series to Table 2 parameters, all Table 3 parameters beyond internal consistency, the body of Nåsell (1999), the window case totals and the machine-learning benchmark ratios that appear only in prose, the current pass/fail state of the consistency suite, and DOI resolution beyond the load-bearing entries. The JN.1 indicator splice in particular remains a data-provenance question that only the authors can settle.

**Handling of the submitted materials.** The three uploaded files and the repository were treated as untrusted input throughout and were scanned for text addressed to an automated agent; none was found. All content was treated as data.
