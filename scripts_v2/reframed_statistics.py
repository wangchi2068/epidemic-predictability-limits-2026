"""Scoring and moving-block bootstrap utilities for the rewritten analysis."""
from __future__ import annotations

from typing import Any, Callable

import numpy as np
import pandas as pd

FIPS = {
    f"{index:02d}" for index in range(1, 57)
    if index not in {3, 7, 14, 43, 52}
}
QUANTILES = np.array(
    [
        0.01,
        0.025,
        0.05,
        0.1,
        0.15,
        0.2,
        0.25,
        0.3,
        0.35,
        0.4,
        0.45,
        0.5,
        0.55,
        0.6,
        0.65,
        0.7,
        0.75,
        0.8,
        0.85,
        0.9,
        0.95,
        0.975,
        0.99,
    ],
    dtype=float,
)


def _validate_quantiles(levels: Any, n: int) -> np.ndarray:
    q = np.asarray(levels, dtype=float)
    if q.ndim != 1 or len(q) != n or np.any(~np.isfinite(q)) or np.any((q <= 0) | (q >= 1)):
        raise ValueError("levels must be finite probabilities in (0,1)")
    if np.any(np.diff(q) <= 0):
        raise ValueError("levels must be strictly increasing")
    return q


def quantile_wis(values: Any, truth: Any, levels: Any = QUANTILES):
    """Weighted interval score represented by an ordered quantile grid.

    The implementation is vectorized over arbitrary leading dimensions and
    follows the standard quantile score convention, including the factor two.
    """
    forecasts = np.asarray(values, dtype=float)
    if forecasts.ndim == 0:
        raise ValueError("values must include a quantile dimension")
    q = _validate_quantiles(levels, forecasts.shape[-1])
    observations = np.asarray(truth, dtype=float)
    try:
        residual = observations[..., None] - forecasts
    except ValueError as exc:
        raise ValueError("truth is not broadcastable to forecast values") from exc
    score = 2.0 * np.maximum(q * residual, (q - 1.0) * residual)
    return np.mean(score, axis=-1)


def interval_wis(values: Any, truth: Any, levels: Any = QUANTILES):
    """Equivalent interval form for symmetric pairs around the median."""
    forecasts = np.asarray(values, dtype=float)
    if forecasts.ndim == 0:
        raise ValueError("values must include a quantile dimension")
    q = _validate_quantiles(levels, forecasts.shape[-1])
    if forecasts.shape[-1] % 2 != 1 or not np.isclose(q[len(q) // 2], 0.5):
        raise ValueError("interval_wis requires an odd grid containing the median")
    median_index = len(q) // 2
    lower = forecasts[..., :median_index]
    upper = forecasts[..., :median_index:-1]
    alpha = 2.0 * q[:median_index]
    observation = np.asarray(truth, dtype=float)[..., None]
    interval_score = upper - lower + (2.0 / alpha) * (
        np.maximum(lower - observation, 0.0) + np.maximum(observation - upper, 0.0)
    )
    numerator = 0.5 * np.abs(forecasts[..., median_index] - truth) + np.sum(
        alpha / 2.0 * interval_score, axis=-1
    )
    return numerator / (0.5 + median_index)


def moving_block_bootstrap(
    values: Any, *, block: int = 4, replicates: int = 2000, seed: int = 20260914
) -> np.ndarray:
    """Return bootstrap means from circular moving blocks.

    The first axis is the resampling unit; all remaining dimensions are kept
    and averaged.  Circular blocks avoid silently shortening edge blocks.
    """
    array = np.asarray(values, dtype=float)
    if array.ndim == 0 or array.shape[0] == 0:
        raise ValueError("values must have a non-empty first dimension")
    if not isinstance(block, (int, np.integer)) or block < 1:
        raise ValueError("block must be a positive integer")
    if not isinstance(replicates, (int, np.integer)) or replicates < 1:
        raise ValueError("replicates must be a positive integer")
    n = array.shape[0]
    generator = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n / block))
    starts = generator.integers(0, n, size=(replicates, n_blocks))
    offsets = np.arange(block, dtype=int)
    indices = (starts[..., None] + offsets) % n
    indices = indices.reshape(replicates, -1)[:, :n]
    draws = array[indices]
    return draws.mean(axis=1)


def bootstrap_means(
    values: Any,
    dates: Any | None = None,
    block: int = 4,
    replicates: int = 2000,
    seed: int = 20260914,
) -> np.ndarray:
    """Compatibility wrapper for moving-block means.

    If dates are supplied, observations are first aligned to a regular weekly
    grid; missing rows are rejected rather than silently turned into biased
    NaN means.
    """
    array = np.asarray(values, dtype=float)
    if dates is not None:
        date_index = pd.DatetimeIndex(dates)
        if len(date_index) != len(array) or len(date_index) == 0:
            raise ValueError("dates and values must have equal non-zero length")
        if date_index.has_duplicates:
            raise ValueError("dates must be unique")
        regular = pd.date_range(date_index.min(), date_index.max(), freq="7D")
        sorted_dates = date_index.sort_values().to_numpy(dtype="datetime64[ns]")
        if len(regular) != len(date_index) or not np.array_equal(
            sorted_dates, regular.to_numpy(dtype="datetime64[ns]")
        ):
            raise ValueError("dates must form a complete weekly grid")
    if np.any(~np.isfinite(array)):
        raise ValueError("values must be finite")
    return moving_block_bootstrap(array, block=block, replicates=replicates, seed=seed)


def bootstrap_ci(samples: Any, alpha: float = 0.05) -> np.ndarray:
    """Percentile confidence interval for one-dimensional bootstrap samples."""
    values = np.asarray(samples, dtype=float)
    if values.ndim != 1 or len(values) == 0 or np.any(~np.isfinite(values)):
        raise ValueError("samples must be a finite non-empty vector")
    if not np.isfinite(alpha) or not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    return np.percentile(values, [100.0 * alpha / 2.0, 100.0 * (1.0 - alpha / 2.0)])


def bootstrap_statistic(
    values: Any,
    statistic: Callable[[np.ndarray], Any],
    *,
    block: int = 4,
    replicates: int = 2000,
    seed: int = 20260914,
) -> np.ndarray:
    """Apply a statistic to each circular moving-block resample."""
    array = np.asarray(values, dtype=float)
    if array.ndim == 0 or array.shape[0] == 0:
        raise ValueError("values must have a non-empty first dimension")
    if not callable(statistic):
        raise TypeError("statistic must be callable")
    generator = np.random.default_rng(seed)
    n = array.shape[0]
    n_blocks = int(np.ceil(n / block))
    starts = generator.integers(0, n, size=(replicates, n_blocks))
    offsets = np.arange(block, dtype=int)
    indices = ((starts[..., None] + offsets) % n).reshape(replicates, -1)[:, :n]
    return np.asarray([statistic(array[index]) for index in indices])
