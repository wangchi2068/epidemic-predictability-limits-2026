# FluSight versioned external-scoring protocol

This directory records the external validation protocol and downloaded final-vintage inputs for the reframed manuscript.

## Locked releases

- Primary season: `cdcepi/FluSight-forecast-hub` release `v1.0.0`, commit `dde0d620d349854266c5a0217df9956ae17670f9` (2023--24).
- Cross-season audit: release `v1.1.0`, commit `1b5b615312eb3a9ebb3fa5fe0e2e123e45258bdc` (2024--25).
- Second cross-season audit: release `v1.2.0` (2025--26, 28 forecast origins, 2025-11-22 to 2026-05-30).
- Repository README: <https://github.com/cdcepi/FluSight-forecast-hub/tree/dde0d620d349854266c5a0217df9956ae17670f9>.

## Scoring lock

For each forecast file, retain `model_id`, `reference_date`, `target`, `horizon`, `location`, `target_end_date`, `output_type`, `output_type_id`, `quantile`, and `value`. Align observations by `target_end_date`; evaluate horizons 1--3 for the weekly laboratory-confirmed influenza hospitalization target. Preserve the final target file; report-date archives can be added for a separate real-time-vintage analysis.

Report the 23-quantile weighted interval score and point MAE for the ensemble and official FluSight-baseline on common origin--state--horizon cells. Exclude horizon 0. Persistence is recorded using the latest target strictly before the forecast origin minus seven days. Estimate uncertainty with a 2,000-replicate four-week moving block bootstrap over origin weeks. Store SHA-256 hashes for every forecast and target file and record the exact scoring command.

The included scores are final-vintage historical audits: `reports_v3/flusight_v1.0_strict.json`, `flusight_v1.1_strict.json` and `flusight_v1.2_strict.json`, with cell-level CSVs beside them. They are not real-time evaluations. The old `forecast_hub_operational_evaluation.json` is excluded because `hub_pooled_metric.py` could not reproduce it from the archived CSV files.

The extended palette lives in `reports_v3/flusight_v1.*_extended.json` (produced by `scripts_v2/flusight_audit_extended.py`). It adds, on the identical locked cells, the WIS decomposition (sharpness / under- / over-prediction), 50/80/95% coverage, mean interval width, a randomized-PIT mean, stratification by horizon, epidemic phase and state, and — as a fourth forecaster on the same cells — this paper's own fixed-`k` mechanistic predictor. The mechanistic entry is a hindsight-fit benchmark (parameters estimated from the final-vintage target file truncated to `reference_date - 7 days`); every record carries `vintage = "final"`. Dropped cells are counted in the `dropped` field, never silently discarded.

## Input hashes

The target-file hashes are `7B28FD296F64132476C6192054F259311872B3A077E61DE444CE4B5323DBA41A` for v1.0.0, `A4993774BD1C2AC358B04A61DEA5CB5C8BAD6373C409068C141D49C31BE519CB` for v1.1.0, and `DC1BCEFFFD8284E4D7C7FF3DFBAE5FD0A9E8DDD2AA5D015275076001B24D2CB4` for v1.2.0. Run `python scripts_v2/score_flusight.py data/flusight/v1.0.0 --start-date 2023-10-14 --end-date 2024-05-04 --output reports_v3/flusight_v1.0_strict.json --csv reports_v3/flusight_v1.0_strict.csv` and the analogous v1.1.0 (`2024-11-23` to `2025-05-31`) and v1.2.0 (`2025-11-22` to `2026-05-30`) commands to reproduce the summaries; all three reproduce byte-for-byte. The v1.1.0 release has no ensemble file for 2025-01-25; that origin is omitted. The extended palette is reproduced with the same three date ranges passed to `scripts_v2/flusight_audit_extended.py`.
