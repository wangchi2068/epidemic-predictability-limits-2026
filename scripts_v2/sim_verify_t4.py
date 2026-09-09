# -*- coding: utf-8 -*-
"""sim_verify_t4.py — Monte-Carlo verification of the Theorem-4 Cramér–Rao bound.

For NB(R, k) the profile score in R is k(Xbar − R)C / [R(R+k)], so the joint MLE
of R is the sample mean (independently of how k is estimated). The experiment
therefore measures the sampling variance of the MLE of R over 50,000 replicate
samples of size C and compares it with the analytic bound
CRB_var = R(R+k)/(Ck) = (R + R²/k)/C. Ratios fluctuate around 1 by Monte-Carlo
noise at this replication count; the report states the observed range.

Outputs: reports/verify_t4.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
SEED = 20260807
REPS = 50000

COMBOS = [
    ("R1.05_k1.0_C200", 1.05, 1.0, 200),
    ("R1.05_k1.0_C1428", 1.05, 1.0, 1428),
    ("R1.10_k1.0_C231", 1.10, 1.0, 231),
    ("R1.10_k1.0_C1428", 1.10, 1.0, 1428),
    ("R1.30_k1.0_C500", 1.30, 1.0, 500),
    ("R1.30_k1.0_C2000", 1.30, 1.0, 2000),
    ("R1.50_k0.3_C500", 1.50, 0.3, 500),
    ("R1.50_k0.3_C2000", 1.50, 0.3, 2000),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rng = np.random.default_rng(SEED)
    out = {}
    for name, R, k, C in COMBOS:
        p = k / (k + R)
        chunk = max(1, 5_000_000 // C)
        rhat = np.empty(REPS)
        done = 0
        while done < REPS:
            m = min(chunk, REPS - done)
            x = rng.negative_binomial(k, p, size=(m, C))
            rhat[done:done + m] = x.mean(axis=1)
            done += m
        emp_var = float(rhat.var(ddof=1))
        crb = float(R * (R + k) / (C * k))
        out[name] = {"R": R, "k": k, "C": C, "reps": REPS,
                     "emp_var": emp_var, "crb": crb,
                     "ratio": emp_var / crb,
                     "bias": float(rhat.mean() - R)}
        print(f"[{name}] ratio={out[name]['ratio']:.6f} "
              f"bias={out[name]['bias']:+.2e}", flush=True)
    (REPORTS / "verify_t4.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    ratios = [v["ratio"] for v in out.values()]
    print(f"\nratio range: {min(ratios):.4f}--{max(ratios):.4f} "
          f"(CRB verified up to Monte-Carlo noise)")
    print("saved reports/verify_t4.json")


if __name__ == "__main__":
    main()
