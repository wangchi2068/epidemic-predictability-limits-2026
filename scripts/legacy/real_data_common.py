"""Shared, unit-explicit calculations for manuscript tables and figures."""


def generation_horizon_to_weeks(h_gen: float, mean_generation_days: float) -> float:
    return h_gen * mean_generation_days / 7.0


def cumulative_case_relative_variance_bound(R: float, k: float, epsilon: float) -> float:
    """CRB variance bound expressed using cumulative offspring cases C≈nR."""
    return R * R * (1.0 + R / k) / (epsilon * epsilon)


def close_budget(*components: float):
    total = sum(components)
    if total == 0:
        raise ValueError("budget total must be non-zero")
    return tuple(value / total for value in components)
