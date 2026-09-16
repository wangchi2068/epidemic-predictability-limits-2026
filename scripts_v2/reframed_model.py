"""Stable conditional moments, parameter mixtures, and horizon helpers."""
from __future__ import annotations

from typing import Any

import numpy as np


def _horizons(value: Any) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.ndim == 0:
        result = result.reshape(1)
    if result.ndim != 1 or np.any(~np.isfinite(result)) or np.any(result < 0):
        raise ValueError("horizon must be a finite, non-negative scalar or vector")
    if np.any(np.abs(result - np.rint(result)) > 1e-10):
        raise ValueError("moment horizons must be integer-valued")
    return np.rint(result).astype(int)


def _parameters(initial: float, growth: float, dispersion: float) -> None:
    if not np.isfinite(initial) or initial <= 0:
        raise ValueError("initial must be positive and finite")
    if not np.isfinite(growth) or growth <= 0:
        raise ValueError("growth must be positive and finite")
    if not np.isfinite(dispersion) or dispersion <= 0:
        raise ValueError("dispersion must be positive and finite")


def _fixed_moments(max_horizon: int, growth: float, dispersion: float, initial: float):
    """Exact recurrence, stable at R=1 and at q=R."""
    _parameters(initial, growth, dispersion)
    mean = np.empty(max_horizon + 1, dtype=float)
    variance = np.empty(max_horizon + 1, dtype=float)
    mean[0], variance[0] = initial, 0.0
    for h in range(1, max_horizon + 1):
        previous_mean, previous_variance = mean[h - 1], variance[h - 1]
        mean[h] = growth * previous_mean
        variance[h] = growth * previous_mean + growth**2 * (
            (1.0 + 1.0 / dispersion) * previous_variance
            + previous_mean**2 / dispersion
        )
    return mean, variance


def macro_moments(horizon: Any, growth: float, dispersion: float, initial: float):
    """Fixed-k aggregate NB moments for R<1, R=1, and R>1.

    The recurrence is algebraically identical to the geometric closed form,
    but explicitly evaluates its q=R removable limit without cancellation.
    """
    hs = _horizons(horizon)
    all_mean, all_variance = _fixed_moments(
        int(hs.max()) if len(hs) else 0, float(growth), float(dispersion), float(initial)
    )
    mean, variance = all_mean[hs], all_variance[hs]
    return {
        "horizon": hs,
        "mean": mean,
        "variance": variance,
        "process_variance": variance,
        "cv2": variance / mean**2,
    }


def _lognormal_moment(mu: float, sigma: float, power: int) -> float:
    exponent = power * mu + 0.5 * (power * sigma) ** 2
    if exponent > np.log(np.finfo(float).max):
        return float("inf")
    return float(np.exp(exponent))


def lognormal_predictive_moments(
    horizon: Any,
    mu_log_growth: float,
    sigma_log_growth: float,
    dispersion: float,
    initial: float,
):
    """Exact moments for one shared lognormal R across a forecast trajectory.

    This is a parameter mixture, not independent step-specific lognormal
    noise.  It returns E[Var(Z_h|R)] and Var(E[Z_h|R)] separately.
    """
    hs = _horizons(horizon)
    if not np.isfinite(mu_log_growth) or not np.isfinite(sigma_log_growth):
        raise ValueError("log-growth parameters must be finite")
    if sigma_log_growth < 0:
        raise ValueError("sigma_log_growth must be non-negative")
    _parameters(initial, 1.0, dispersion)
    max_h = int(hs.max()) if len(hs) else 0

    # V_h(R) is a polynomial in R.  Store its coefficients, then integrate
    # each monomial with E[R^p] under the lognormal mixing law.
    polynomials: list[dict[int, float]] = [{0: 0.0}]
    factor = 1.0 + 1.0 / dispersion
    for h in range(max_h):
        next_polynomial: dict[int, float] = {h + 1: float(initial)}
        for power, coefficient in polynomials[-1].items():
            next_polynomial[power + 2] = (
                next_polynomial.get(power + 2, 0.0) + factor * coefficient
            )
        power = 2 * h + 2
        next_polynomial[power] = (
            next_polynomial.get(power, 0.0) + float(initial) ** 2 / dispersion
        )
        polynomials.append(next_polynomial)

    mixed_process = np.empty(max_h + 1, dtype=float)
    for h, polynomial in enumerate(polynomials):
        mixed_process[h] = sum(
            coefficient * _lognormal_moment(mu_log_growth, sigma_log_growth, power)
            for power, coefficient in polynomial.items()
        )
    raw_moments = np.asarray(
        [_lognormal_moment(mu_log_growth, sigma_log_growth, int(h)) for h in range(2 * max_h + 1)]
    )
    mean_full = float(initial) * raw_moments[: max_h + 1]
    parameter_variance_full = float(initial) ** 2 * (
        raw_moments[::2][: max_h + 1] - raw_moments[: max_h + 1] ** 2
    )
    mean = mean_full[hs]
    process_variance = mixed_process[hs]
    parameter_variance = parameter_variance_full[hs]
    variance = process_variance + parameter_variance
    plugin = float(initial) * raw_moments[1] ** hs
    squared_bias = (plugin - mean) ** 2
    return {
        "horizon": hs,
        "mean": mean,
        "plugin": plugin,
        "process_variance": process_variance,
        "parameter_variance": parameter_variance,
        "variance": variance,
        "squared_bias": squared_bias,
        "parameter_risk": parameter_variance + squared_bias,
        "risk": (variance + squared_bias) / float(initial) ** 2,
        "mean_predictor_risk": variance / float(initial) ** 2,
    }


def horizon_set(
    risk: Any,
    tolerance: float,
    *,
    horizons: Any | None = None,
    return_segments: bool = False,
):
    """Return the supremum of all threshold-admissible horizon segments.

    This does not assume a unique crossing; NaN values split segments.
    ``return_segments`` exposes every inclusive ``(start, end)`` segment.
    """
    values = np.asarray(risk, dtype=float)
    if values.ndim != 1:
        raise ValueError("risk must be one-dimensional")
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and non-negative")
    if horizons is None:
        axis = np.arange(1, len(values) + 1, dtype=float)
    else:
        axis = np.asarray(horizons, dtype=float)
        if axis.ndim != 1 or len(axis) != len(values) or np.any(~np.isfinite(axis)):
            raise ValueError("horizons must be finite and match risk")
    admissible = np.isfinite(values) & (values <= tolerance**2)
    segments: list[tuple[float, float]] = []
    start = None
    for index, valid in enumerate(admissible):
        if valid and start is None:
            start = index
        if start is not None and (not valid or index == len(admissible) - 1):
            end = index if valid and index == len(admissible) - 1 else index - 1
            segments.append((float(axis[start]), float(axis[end])))
            start = None
    supremum = max((end for _, end in segments), default=None)
    if return_segments:
        return {
            "segments": segments,
            "supremum": supremum,
            "threshold": float(tolerance**2),
            "n_admissible": int(admissible.sum()),
        }
    return supremum


def prefix_horizon(risk: Any, tolerance: float) -> int:
    """Compatibility function: number of valid initial risk values."""
    values = np.asarray(risk, dtype=float)
    if values.ndim != 1:
        raise ValueError("risk must be one-dimensional")
    for index, value in enumerate(values):
        if not np.isfinite(value) or value > tolerance**2:
            return index
    return len(values)


def conditional_ar1_sum_variance(phi: float, innovation_variance: float, horizon: Any):
    """Conditional variance of sum_{j=1}^h x_{t+j} in an AR(1) process."""
    if not np.isfinite(phi) or not np.isfinite(innovation_variance) or innovation_variance < 0:
        raise ValueError("invalid AR(1) parameters")
    hs = _horizons(horizon)
    out = np.empty(len(hs), dtype=float)
    for index, h in enumerate(hs):
        if h == 0:
            out[index] = 0.0
        elif abs(phi - 1.0) <= 1e-12:
            out[index] = innovation_variance * h * (h + 1) * (2 * h + 1) / 6.0
        else:
            coefficients = (1.0 - phi ** np.arange(1, h + 1)) / (1.0 - phi)
            out[index] = innovation_variance * np.dot(coefficients, coefficients)
    return float(out[0]) if np.ndim(horizon) == 0 else out


def ar1_sum_variance(phi: float, gamma0: float, horizon: Any):
    """Unconditional AR(1) summed variance for a specified marginal gamma0."""
    if not np.isfinite(phi) or not np.isfinite(gamma0) or gamma0 < 0:
        raise ValueError("invalid AR(1) parameters")
    hs = _horizons(horizon)
    out = np.empty(len(hs), dtype=float)
    for index, h in enumerate(hs):
        out[index] = gamma0 * (
            h**2 if abs(phi - 1.0) <= 1e-12 else h + 2.0 * sum((h - lag) * phi**lag for lag in range(1, h))
        )
    return float(out[0]) if np.ndim(horizon) == 0 else out


def forecast_moments(initial, log_growth, uncertainty, dispersion, horizon):
    """Backward-compatible name for the shared-lognormal moment function."""
    return lognormal_predictive_moments(
        horizon, log_growth, uncertainty, dispersion, initial
    )
