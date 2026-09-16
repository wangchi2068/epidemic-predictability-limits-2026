# -*- coding: utf-8 -*-
"""macro_cv_check.py — does the fixed-k_agg macro update model obey Lemma 2?

Reviewer point: the CV^2(h) formula of Lemma 2 is derived from the micro
Galton-Watson branching process, whose conditional variance is LINEAR in the
current size, Var(Z_t | Z_{t-1}) = sigma^2 Z_{t-1}.  The Theorem 5 macro model
Z_t | F_{t-1} ~ NB(R Z_{t-1}, k_agg) instead has a QUADRATIC conditional
variance, Var = R Z_{t-1} + R^2 Z_{t-1}^2 / k_agg.  So plugging k_agg into the
Lemma-2 form need not be self-consistent.

This script simulates the macro model and compares the empirical CV^2(h) with
(i) the Lemma-2 form evaluated at k_agg, (ii) the model's own exact finite-step
closed form (Corollary 5): with q = R^2 (1 + 1/k_agg), m_t = I0 R^t,
    V_h = I0 R (q^h - R^h)/(q - R) + I0^2 (q^h - R^{2h}),
    CV^2_macro(h) = V_h / (I0 R^h)^2
                  = [(1 + 1/k_agg)^h - 1] + (1/I0)(q^h - R^h)/((q - R) R^{2h-1}),
whose h/k_agg << 1 leading order recovers the h/k_agg law of Corollary 4.

Writes reports_v3/macro_cv_check.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports_v3"

SEED = 20260807
N_REP = 20000
GENS = 14
H = np.arange(1, GENS + 1)


def simulate(R, k_agg, I0, reps, rng):
    z = np.full(reps, float(I0))
    out = np.zeros((GENS, reps))
    for t in range(GENS):
        mu = R * z
        z = rng.negative_binomial(k_agg, k_agg / (k_agg + mu))
        out[t] = z
    return out


def closed_form_cv2(R, k_agg, I0, h):
    """Exact CV^2 of the fixed-k_agg macro NB update model (Corollary 5)."""
    q = R * R * (1.0 + 1.0 / k_agg)
    V = (I0 * R * (q ** h - R ** h) / (q - R)
         + I0 * I0 * (q ** h - R ** (2 * h)))
    return V / (I0 * R ** h) ** 2


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rng = np.random.default_rng(SEED)
    out = {}
    for label, R, k_agg, I0 in [
        ("Delta-state", 1.175, 56.6, 297.0),
        ("flu-state", 1.223, 11.2, 55.0),
        ("RSV-state", 1.430, 39.8, 76.0),
    ]:
        Z = simulate(R, k_agg, I0, N_REP, rng)
        cv2_emp = Z.var(axis=1, ddof=1) / (Z.mean(axis=1) ** 2)
        cv2_lemma = (1 + R / k_agg) * (1 - R ** (-H)) / (I0 * (R - 1))
        cv2_closed = closed_form_cv2(R, k_agg, I0, H)
        out[label] = {
            "R": R, "k_agg": k_agg, "I0": I0,
            "cv2_emp": cv2_emp.tolist(),
            "cv2_lemma_with_kagg": cv2_lemma.tolist(),
            "cv2_macro_closed": cv2_closed.tolist(),
            "ratio_emp_over_lemma": (cv2_emp / cv2_lemma).tolist(),
            "ratio_emp_over_closed": (cv2_emp / cv2_closed).tolist(),
        }
        print(f"[{label}] R={R} k_agg={k_agg} I0={I0}")
        print("   h:        ", "  ".join(f"{h:9d}" for h in H))
        print("   emp:      ", "  ".join(f"{v:9.2e}" for v in cv2_emp))
        print("   lemma2:   ", "  ".join(f"{v:9.2e}" for v in cv2_lemma))
        print("   closed:   ", "  ".join(f"{v:9.2e}" for v in cv2_closed))
        print("   emp/closed:", "  ".join(f"{v:9.3f}" for v in cv2_emp / cv2_closed))
        print("   emp/lemma: ", "  ".join(f"{v:9.2f}" for v in cv2_emp / cv2_lemma))
    (REPORTS / "macro_cv_check.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nwrote reports_v3/macro_cv_check.json")


if __name__ == "__main__":
    main()
