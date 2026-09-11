# -*- coding: utf-8 -*-
"""coarsegrain_check.py — micro-to-macro coarse-graining check for the
dispersion parameter (reviewer item: the individual-level k and the aggregate
k_agg are different objects; is there a link?).

Theory.  If a state-week aggregate count is the sum of M independent individual
contributions each NB(R, k), the negative binomial is closed under convolution
and the sum is NB(M R, M k); the aggregate effective dispersion is therefore
k_agg = M k, with M the number of independent contributing units per week.
M is large and time-varying, so k_agg >> k and no fixed analytic mapping exists.

This script verifies the mechanism numerically: it simulates the *individual*
Galton-Watson process with offspring NB(R, k), maps generations onto calendar
weeks via the mean generation time, aggregates to weekly counts, and estimates
k_agg from the weekly log-differences with exactly the pipeline estimator. It
reports the implied aggregation factor M = k_agg / k.

Writes reports_v3/coarsegrain_check.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports_v3"

SEED = 20260807
N_REP = 1000
GENS = 24
I0 = 50
MIN_WEEK = 5.0


def simulate_weekly(R, k, mu_g, rng):
    """One replicate: branching process over GENS generations, aggregated into
    weekly counts via the mean generation time."""
    z = I0
    gen_counts = [z]
    for _ in range(GENS):
        if z <= 0:
            break
        z = int(rng.negative_binomial(k, k / (R + k), size=min(z, 200000)).sum())
        gen_counts.append(z)
    gen_counts = np.asarray(gen_counts, dtype=float)
    # week index of generation g: floor(g * mu_g / 7)
    week = np.floor(np.arange(len(gen_counts)) * mu_g / 7.0).astype(int)
    n_week = week[-1] + 1 if len(week) else 0
    w = np.zeros(n_week)
    for g, wk in enumerate(week):
        w[wk] += gen_counts[g]
    return w


def k_agg_from(series_list):
    """Pooled log-difference estimator, identical to the paper's pipeline."""
    dlog = []
    means = []
    for w in series_list:
        w = w[w >= MIN_WEEK]
        if len(w) < 3:
            continue
        dlog.extend(np.diff(np.log(w)).tolist())
        means.append(float(np.mean(w)))
    if len(dlog) < 10:
        return None, None, None
    var = float(np.var(dlog, ddof=1))
    mu = float(np.mean(means))
    return 1.0 / max(var - 1.0 / mu, 1e-3), var, mu


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rng = np.random.default_rng(SEED)
    out = {}
    for label, R, k, mu_g in [
        ("Delta-like", 1.20, 0.434, 4.7),
        ("flu-like", 1.22, 0.434, 3.2),
        ("Ebola-like", 1.10, 0.182, 12.0),
        ("RSV-like", 1.37, 0.434, 8.4),
    ]:
        series = [simulate_weekly(R, k, mu_g, rng) for _ in range(N_REP)]
        ka, var, mu = k_agg_from(series)
        if ka is None:
            out[label] = {"k": k, "k_agg": None}
            print(f"[{label}] no usable series")
            continue
        out[label] = {"R": R, "k": k, "mu_g": mu_g,
                      "k_agg_est": float(ka),
                      "implied_M": float(ka / k),
                      "pooled_logdiff_var": var,
                      "mean_weekly_count": mu,
                      "n_rep": N_REP}
        print(f"[{label:11s}] k={k:.3f} -> k_agg={ka:7.2f} "
              f"(implied M = k_agg/k = {ka/k:7.1f})   "
              f"mean weekly count={mu:8.0f}")
    (REPORTS / "coarsegrain_check.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nwrote reports_v3/coarsegrain_check.json")
    print("Observed empirical k_agg medians (state panel): "
          "Delta 56.6, Omicron 21.0, JN.1 29.5, flu22 11.2, flu24 17.4, "
          "rsv24 39.8, rsv25 23.7")


if __name__ == "__main__":
    main()
