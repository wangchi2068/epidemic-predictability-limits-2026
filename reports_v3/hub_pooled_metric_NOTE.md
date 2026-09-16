# hub_pooled_metric_NOTE

## Reconstruction Validation Result: **FAILED**

The reconstruction could not be validated against the frozen `forecast_hub_operational_evaluation.json`
within the required ~5% tolerance.

### What Was Tried

The script `scripts_v2/hub_pooled_metric.py` implements the following convention (derived from
data inspection and the task description):

- **Forecast origin**: Monday `forecast_date` from the COVIDhub-ensemble CSV.
- **z (baseline)**: `weekly_admissions` for the week ending the Saturday immediately before the origin
  (e.g., for origin 2021-08-02 [Monday], z = week ending 2021-08-07).
- **Ensemble weekly forecast**: sum of daily `"N day ahead inc hosp"` point forecasts for
  days `7*(h-1)+1` through `7*h` from the origin.
  - h=1: days 1–7 → targets week ending Saturday + 1 week (e.g., 2021-08-14).
  - h=2: days 8–14 → targets week ending + 2 weeks (2021-08-21). And so on.
- **Persistence**: flat forecast = z (last observed weekly admissions at origin).
- **Per-state relMSE**: `(ensemble − truth)² / (z − truth)²`.
- **Frozen metric**: cross-state median of per-state relMSE values (`median_relMSE`).

### Validation Outcome

Computed vs. frozen `median_relMSE` for the first few entries:

| Origin      | Wave  | h | Frozen    | Computed  | Deviation |
|-------------|-------|---|-----------|-----------|-----------|
| 2021-08-02  | Delta | 1 | 0.939453  | 2.156134  | **129.5%** |
| 2021-08-02  | Delta | 2 | 0.920931  | 1.311605  | 42.4%     |
| 2021-08-09  | Delta | 1 | 1.000000  | 2.054628  | **105.5%** |
| 2021-09-06  | Delta | 1 | 4.000000  | 3.711278  | 7.2%      |

The **maximum deviation** across all 34 (origin × horizon) pairs is **167%**.
Only 5 of 34 pairs fall within 15%; none fall within 5%.

The best match is 2021-09-06 h=1 (7.2% deviation), but this appears to be coincidental.
The systematic pattern (computed values consistently higher or lower than frozen) suggests a
structural mismatch in the convention, not random error.

### Investigation of Alternative Hypotheses

All of the following were tested and did not resolve the mismatch:

1. **Using single daily forecast (`7 day ahead inc hosp`) as the weekly prediction directly** — far worse match.
2. **Median of daily forecasts as weekly ensemble** — far worse match.
3. **Days 2–8 alignment instead of days 1–7** — no improvement.
4. **Geometric mean instead of median** — no improvement.
5. **State-count filtering**: frozen uses 50 states for the first origin vs. 54 available — even after filtering, per-state median remains ~2.16 vs frozen 0.94.
6. **Alternative z-date definitions** (Saturday of origin week vs. prior week vs. different reference points) — none produced a substantial improvement.
7. **Un-normalized squared-error ratio** — did not reconcile the discrepancy.

### Diagnosis

The frozen `median_relMSE` is almost certainly computed with a convention that is not
fully recoverable from the current data files and the description provided. Possible
causes include:

- The weekly ensemble forecast may have been derived from a **different target** in the
  original evaluation (e.g., a weekly-level `"1 wk ahead inc hosp"` target that is not
  present in the archived CSV files used here).
- The **state set** (50 states) may have been curated differently (e.g., excluding
  specific jurisdictions with anomalous behavior), and the exact exclusion list is not
  documented.
- The frozen evaluation may have been produced by an **external script** (deleted from the
  repository in commit a190d13: "superseded national inputs, raw snapshots and old
  scripts/figures are removed"), making the exact formula unauditable from the repo.

### Consequence

Because the reconstruction cannot be validated, the **pooled metric was NOT computed**.
Per the task instructions: "If you cannot get within ~5%, STOP and report exactly what
you tried and where it diverges — do NOT fabricate a metric that disagrees with the
frozen numbers."

The script `scripts_v2/hub_pooled_metric.py` is written and functional for the intended
pooled formula (`pooled(h) = Σ((ens−truth)/z)² / Σ((z−truth)/z)²`), but it does not
write `reports_v3/hub_pooled_metric.json` when validation fails.

### Convention Used (for reference when the correct formula is identified)

Daily-to-weekly alignment: sum of 7 consecutive daily `"N day ahead inc hosp"` point
forecasts per horizon.  Horizon h=1 sums days 1–7, targeting the week ending on the
Saturday after the origin's Saturday-before baseline.
