"""Independent numerical checks for the model-conditional rewrite."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from numpy.polynomial.hermite import hermgauss

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
REPORT = ROOT / "reports_v3" / "theory_verification.json"
sys.path.insert(0, str(SCRIPT_DIR))

from reframed_model import (  # noqa: E402
    ar1_sum_variance,
    conditional_ar1_sum_variance,
    horizon_set,
    lognormal_predictive_moments,
    macro_moments,
)
from reframed_statistics import (  # noqa: E402
    QUANTILES,
    bootstrap_ci,
    bootstrap_means,
    interval_wis,
    moving_block_bootstrap,
    quantile_wis,
)


def _assert_close(actual, expected, *, rtol=1e-10, atol=1e-11):
    np.testing.assert_allclose(actual, expected, rtol=rtol, atol=atol)


def _macro_recurrence(initial, growth, dispersion, horizons):
    mean = float(initial)
    variance = 0.0
    means = [mean]
    variances = [variance]
    for _ in range(int(max(horizons))):
        variance = (
            growth * mean
            + growth**2
            * ((1.0 + 1.0 / dispersion) * variance + mean**2 / dispersion)
        )
        mean *= growth
        means.append(mean)
        variances.append(variance)
    return np.asarray(means), np.asarray(variances)


def _conditional_mixture_quadrature(initial, mu, sigma, dispersion, h):
    nodes, weights = hermgauss(80)
    weights = weights / np.sqrt(np.pi)
    growths = np.exp(mu + np.sqrt(2.0) * sigma * nodes)
    means = []
    second_moments = []
    for growth in growths:
        mean, variance = _macro_recurrence(initial, growth, dispersion, [h])
        means.append(mean[h])
        second_moments.append(variance[h] + mean[h] ** 2)
    mean_mix = float(np.dot(weights, means))
    second_mix = float(np.dot(weights, second_moments))
    return mean_mix, second_mix - mean_mix**2


def _direct_conditional_ar1(phi, innovation_variance, h):
    if h == 0:
        return 0.0
    if abs(phi - 1.0) < 1e-12:
        coefficients = np.arange(1.0, h + 1.0)
    else:
        coefficients = np.asarray(
            [(1.0 - phi**n) / (1.0 - phi) for n in range(1, h + 1)],
            dtype=float,
        )
    return float(innovation_variance * np.dot(coefficients, coefficients))


def run_checks():
    checks = {}

    # Fixed-k macro moments: subcritical, critical, supercritical, and the
    # removable q=R root all agree with an independently coded recurrence.
    for growth in (0.5, 0.8, 1.0, 1.4):
        for dispersion in (0.2, 4.0, 1000.0):
            initial = 25.0
            horizons = np.arange(0, 9)
            expected_mean, expected_variance = _macro_recurrence(
                initial, growth, dispersion, horizons
            )
            observed = macro_moments(horizons, growth, dispersion, initial)
            _assert_close(observed["mean"], expected_mean)
            _assert_close(observed["variance"], expected_variance)
            _assert_close(observed["process_variance"], expected_variance)
            assert np.all(observed["variance"] >= 0.0)
    checks["macro_recurrence_R_lt_eq_gt_one"] = True

    root_k = 4.0
    root_growth = 1.0 / (1.0 + 1.0 / root_k)
    root_horizons = np.arange(0, 51)
    root_expected = _macro_recurrence(17.0, root_growth, root_k, root_horizons)
    root_observed = macro_moments(root_horizons, root_growth, root_k, 17.0)
    _assert_close(root_observed["variance"], root_expected[1], rtol=2e-10)
    near_root = macro_moments(
        root_horizons, root_growth * (1.0 + 1e-11), root_k, 17.0
    )
    assert np.isfinite(near_root["variance"]).all()
    checks["macro_q_equals_R_removable_limit"] = True

    # Shared-lognormal mixing: compare every reported moment to independent
    # Gauss-Hermite integration of the conditional macro recurrence.
    initial, mu, sigma, dispersion = 30.0, 0.1, 0.12, 12.0
    horizons = np.arange(0, 6)
    mixed = lognormal_predictive_moments(
        horizons, mu, sigma, dispersion, initial
    )
    for h in horizons:
        expected_mean, expected_variance = _conditional_mixture_quadrature(
            initial, mu, sigma, dispersion, int(h)
        )
        _assert_close(mixed["mean"][h], expected_mean, rtol=2e-9)
        _assert_close(mixed["variance"][h], expected_variance, rtol=2e-8)
    deterministic = lognormal_predictive_moments(
        horizons, mu, 0.0, dispersion, initial
    )
    fixed = macro_moments(horizons, np.exp(mu), dispersion, initial)
    _assert_close(deterministic["mean"], fixed["mean"])
    _assert_close(deterministic["variance"], fixed["variance"])
    _assert_close(deterministic["parameter_variance"], 0.0)
    checks["shared_lognormal_mixture_quadrature"] = True

    # Risk admissibility must retain separated segments and use their
    # supremum, rather than assuming the first threshold crossing is final.
    risk = np.array([0.10, 0.40, 0.80, 0.20, np.nan, 0.20])
    details = horizon_set(risk, tolerance=0.5, return_segments=True)
    assert details["supremum"] == 6.0
    assert details["segments"] == [(1.0, 1.0), (4.0, 4.0), (6.0, 6.0)]
    assert horizon_set(np.array([1.0, np.nan]), tolerance=0.5) is None
    checks["horizon_segments_and_supremum"] = True

    # Conditional AR(1) sum variance agrees with a direct innovation-weight
    # calculation; unconditional helper agrees with direct covariance sums.
    for phi in (-0.5, 0.0, 0.8, 1.0):
        for h in (0, 1, 4, 10):
            observed = conditional_ar1_sum_variance(phi, 0.07, h)
            expected = _direct_conditional_ar1(phi, 0.07, h)
            _assert_close(observed, expected, rtol=1e-11)
    phi, gamma0, h = 0.8, 0.13, 9
    expected_unconditional = gamma0 * (
        h + 2.0 * sum((h - lag) * phi**lag for lag in range(1, h))
    )
    _assert_close(ar1_sum_variance(phi, gamma0, h), expected_unconditional)
    checks["conditional_and_unconditional_ar1_variance"] = True

    # The quantile and paired-interval forms agree for the 23-quantile scale,
    # including vectorized truths and a degenerate forecast.
    predictions = 10.0 + 20.0 * QUANTILES
    truths = np.array([0.0, 12.0, 20.0, 100.0])
    q_scores = quantile_wis(np.broadcast_to(predictions, (4, 23)), truths)
    i_scores = interval_wis(np.broadcast_to(predictions, (4, 23)), truths)
    _assert_close(q_scores, i_scores, rtol=1e-12)
    _assert_close(quantile_wis(np.full(23, 5.0), 8.0), 3.0)
    checks["wis_23_quantile_vectorization"] = True

    # Moving blocks are reproducible, preserve multiplicity, and work with
    # both one-dimensional and matrix-valued observations.
    dates = np.arange(
        np.datetime64("2024-01-06"), np.datetime64("2024-03-02"), np.timedelta64(7, "D")
    )
    values = np.arange(len(dates), dtype=float)
    sampled_a = bootstrap_means(values, dates, block=2, replicates=2000, seed=41)
    sampled_b = bootstrap_means(values, dates, block=2, replicates=2000, seed=41)
    assert np.array_equal(sampled_a, sampled_b)
    assert len(np.unique(sampled_a)) > 15
    assert abs(sampled_a.mean() - values.mean()) < 0.2
    matrix_draws = moving_block_bootstrap(
        np.column_stack([values, values**2]), block=3, replicates=100, seed=9
    )
    assert matrix_draws.shape == (100, 2)
    ci = bootstrap_ci(sampled_a)
    assert ci.shape == (2,) and ci[0] <= ci[1]
    checks["moving_block_bootstrap_reproducibility_and_shape"] = True

    return checks


def main():
    checks = run_checks()
    payload = {
        "schema": "theory_verification_v1",
        "checks": checks,
        "all_passed": all(checks.values()),
    }
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
