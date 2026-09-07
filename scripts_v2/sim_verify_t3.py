"""Verify Theorem 3's quasi-stationary CV and establishment probability.

The stationary-density coefficient is c1=2eps/(R+1). Establishment is a
separate Poisson-offspring Galton-Watson calculation with approximation
2eps/R; keeping the two coefficients separate is essential.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import integrate
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
SEED = 20260807
XMIN = 0.1
CV_CONFIG = {"N": 2000, "dt": 0.05, "steps": 100000, "burn": 50000, "reps": 30}
ESTABLISHMENT_REPS = 400
rng_cv, rng_est = [
    np.random.default_rng(s) for s in np.random.SeedSequence(SEED).spawn(2)
]


def density_moments(eps, R, N, xmin=XMIN):
    c1 = 2 * eps / (R + 1)
    c2 = R / (N * (R + 1))

    def density_kernel(x):
        return x**-1 * np.exp(c1 * x - c2 * x**2)

    z = integrate.quad(density_kernel, xmin, np.inf, limit=400)[0]
    m1 = integrate.quad(lambda x: x * density_kernel(x), xmin, np.inf, limit=400)[0] / z
    m2 = (
        integrate.quad(lambda x: x**2 * density_kernel(x), xmin, np.inf, limit=400)[0]
        / z
    )
    return np.sqrt(max(m2 - m1**2, 0)) / m1


def sim_cv(eps, R, N, dt=0.05, steps=100000, burn=50000, reps=30, xmin=XMIN):
    """Vectorized Euler-Maruyama paths reflected at the density cutoff."""
    x = np.full(reps, eps * N / R, dtype=float)
    sum_x = np.zeros(reps)
    sum_x2 = np.zeros(reps)
    kept = 0
    sqrt_dt = np.sqrt(dt)
    for step in range(steps):
        mu = x * (eps - R * x / N)
        sd = np.sqrt((R + 1) * x)
        proposal = x + mu * dt + sd * sqrt_dt * rng_cv.standard_normal(reps)
        x = xmin + np.abs(proposal - xmin)
        if step >= burn:
            sum_x += x
            sum_x2 += x**2
            kept += 1
    means = sum_x / kept
    variances = np.maximum(sum_x2 / kept - means**2, 0)
    cvs = np.sqrt(variances) / means
    try:
        return float(cvs.mean()), float(cvs.std(ddof=1) / np.sqrt(reps))
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"sim_cv failed for eps={eps}, R={R}") from exc


def establishment(N, eps, k=None, reps=ESTABLISHMENT_REPS):
    """Probability that one seed reaches 5% of N before extinction under Poisson (k=None) or NB(R, k)."""
    R = 1 + eps
    try:
        threshold = int(np.ceil(0.05 * N))
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"invalid N={N}") from exc
    established = 0
    p_succ = (k / (k + R)) if (k is not None and not np.isinf(k)) else None
    for _ in range(reps):
        population = 1
        while 0 < population < threshold:
            try:
                if p_succ is None:
                    population = int(rng_est.poisson(R * population))
                else:
                    population = int(rng_est.negative_binomial(population * k, p_succ))
            except (TypeError, ValueError) as exc:
                raise RuntimeError("offspring draw failed") from exc
        established += population >= threshold
    lo = beta.ppf(0.025, established + 1, reps - established + 1)
    hi = beta.ppf(0.975, established + 1, reps - established + 1)
    return established / reps, lo, hi


def cutoff_sensitivity(eps, R, N):
    cutoffs = [0.05, 0.1, 0.2, 0.5]
    values = [density_moments(eps, R, N, xmin) for xmin in cutoffs]
    reference = values[1]
    max_change_pct = max(abs(value - reference) / reference * 100 for value in values)
    return {"cutoffs": cutoffs, "theory_cv": values, "max_change_pct": max_change_pct}


if __name__ == "__main__":

    def _f(v, label):
        try:
            return float(v)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(f"invalid float for {label}: {v!r}") from exc

    stationary_cv = {}
    # near-critical window: (R+1)/N ~ 0.001 at N=2000; eps=0.005/0.01 lie just
    # inside this window, so they directly verify the predictability-collapse claim
    # (the QSD mixing time is longer there, hence the extended burn-in)
    for eps in [0.005, 0.01, 0.20, 0.40]:
        R = 1 + eps
        N = CV_CONFIG["N"]
        theory = density_moments(eps, R, N)
        if eps < 0.05:
            # longer burn-in for the slowly-mixing near-critical regime
            empirical, se = sim_cv(
                eps, R, N, dt=CV_CONFIG["dt"], steps=300000, burn=250000, reps=60
            )
        else:
            empirical, se = sim_cv(
                eps, R, N, **{k: CV_CONFIG[k] for k in ("dt", "steps", "burn", "reps")}
            )
        stationary_cv[f"eps{eps}"] = {
            "R": R,
            "N": N,
            "xmin": XMIN,
            "theory_cv_quadratic_exp": _f(theory, "theory"),
            "emp_cv": empirical,
            "emp_se": se,
            "ratio": _f(empirical / theory, "ratio"),
            "cutoff_sensitivity": cutoff_sensitivity(eps, R, N),
        }
        print("eps", eps, json.dumps(stationary_cv[f"eps{eps}"]), flush=True)

    establishment_results = {}
    for N in [500, 1000]:
        for eps in [0.02, 0.05, 0.10, 0.20]:
            probability, lo, hi = establishment(N, eps)
            R = 1 + eps
            threshold = int(np.ceil(0.05 * N))
            establishment_results[f"N{N}_eps{eps}"] = {
                "reps": ESTABLISHMENT_REPS,
                "threshold": threshold,
                "emp": _f(probability, "emp"),
                "ci": [_f(lo, "lo"), _f(hi, "hi")],
                "theory_2eps_over_R": _f(2 * eps / R, "theory"),
            }
            print("est", establishment_results[f"N{N}_eps{eps}"], flush=True)

    establishment_nb_results = {}
    for N in [500, 1000]:
        for eps in [0.05, 0.10, 0.20]:
            for k_val in [1.0, 0.5]:
                probability, lo, hi = establishment(N, eps, k=k_val, reps=2500)
                R = 1 + eps
                threshold = int(np.ceil(0.05 * N))
                theo_nb = (2 * eps) / (R * (1.0 + R / k_val))
                establishment_nb_results[f"N{N}_eps{eps}_k{k_val}"] = {
                    "reps": 2500,
                    "threshold": threshold,
                    "k": k_val,
                    "emp": _f(probability, "emp"),
                    "ci": [_f(lo, "lo"), _f(hi, "hi")],
                    "theory_nb": _f(theo_nb, "theory_nb"),
                }
                print("est_nb", establishment_nb_results[f"N{N}_eps{eps}_k{k_val}"], flush=True)

    report = {
        "metadata": {
            "seed": SEED,
            "stationary_process": "logistic diffusion with reflecting boundary at xmin",
            "stationary_config": CV_CONFIG,
            "establishment_process": "Poisson and Negative-Binomial offspring Galton-Watson from one seed",
            "establishment_nb_reps": 2500,
            "establishment_reps_per_cell": ESTABLISHMENT_REPS,
        },
        "stationary_cv": stationary_cv,
        "establishment": establishment_results,
        "establishment_nb": establishment_nb_results,
    }
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "verify_t3.json").write_text(
        json.dumps(report, indent=2, allow_nan=False), encoding="utf-8"
    )
    print("saved", flush=True)
