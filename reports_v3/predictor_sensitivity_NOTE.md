# Predictor sensitivity — verification and results

## Monte-Carlo verification of the two closed forms

With `log Rhat ~ N(log R, s^2)` and the plug-in / mean-bias-corrected predictors,
the relative MSE contributions are

- `P_plug(h) = exp(2x) - 2 exp(x/2) + 1`,  `x = (h s)^2`
- `P_bc(h)   = exp(x) - 1`   (mean-unbiased predictor)

verified by Monte Carlo with n = 2,000,000 draws per grid point over
h = 1..10 and s ∈ {0.02, 0.05, 0.10}:

| statistic | max relative deviation |
|---|---|
| `P_plug` | 0.46% |
| `P_bc`   | 0.46% |

Both closed forms are therefore reliable.

## Per-phase horizons (weeks, τ = 0.5, macro-exact process variance)

| Phase | plug-in | bias-corrected | median bc/plug | per-state bc/plug range |
|---|---:|---:|---:|---|
| COVID-19 Delta 暴发期 | 7.12 | 7.27 | 1.015 | 1.000–1.079 |
| COVID-19 Omicron 达峰期 | 3.95 | 3.99 | 1.006 | 1.000–1.049 |
| COVID-19 JN.1 流行期 | 5.00 | 5.05 | 1.012 | 1.002–1.043 |
| 流感 2022--23 暴发早期 | 2.20 | 2.21 | 1.003 | 1.000–1.085 |
| 流感 2024--25 流行季 | 2.58 | 2.59 | 1.005 | 1.000–1.071 |
| RSV 2024--25 流行季 | 5.82 | 5.92 | 1.013 | 1.000–1.080 |
| RSV 2025--26 流行季 | 3.89 | 3.95 | 1.005 | 1.000–1.078 |

## Interpretation

`P_bc ≤ P_plug` pointwise (the plug-in rule inherits Jensen's inequality bias),
so the bias-corrected horizon is never shorter; the median extension is only
0.3%–1.5%. Under the macro-exact caliber the process-variance term occupies
0.73–0.89 of τ² at the working point, so the *form* of the parameter term has
little leverage on the horizon: the mechanism horizon is close to
predictor-independent here. This contrasts with the earlier heuristic caliber,
where parameter uncertainty dominated and the predictor choice would have
mattered more. Predictor dependence is therefore real in theory (the two rules
differ by the Jensen term) but numerically modest in the paper's regime.
