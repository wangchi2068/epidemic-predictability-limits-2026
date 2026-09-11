# -*- coding: utf-8 -*-
"""macro_cv_check.py — does the fixed-k_agg macro update model obey Lemma 2?

Reviewer point: the CV^2(h) formula of Lemma 2 is derived from the micro
Galton-Watson branching process, whose conditional variance is LINEAR in the
current size, Var(Z_t | Z_{t-1}) = sigma^2 Z_{t-1}.  The Theorem 5 macro model
Z_t | F_{t-1} ~ NB(R Z_{t-1}, k_agg) instead has a QUADRATIC conditional
variance, Var = R Z_{t-1} + R^2 Z_{t-1}^2 / k_agg.  So plugging k_agg into the
Lemma-2 form need not be self-consistent.

This script simulates the macro model and compares the empirical CV^2(h) with
(i) the Lemma-2 form evaluated at k_agg and (ii) the model's own leading-order
law, which the recursion
    v_t = R m_{t-1} + (R^2/k) m_{t-1}^2 + R^2 (1 + 1/k) v_{t-1},  m_t = I0 R^t
suggests grows geometrically at rate R^2 (1 + 1/k_agg) in v_t, i.e.
CV^2(t) ~ (1/I0^2) c^t with c = (1 + 1/k_agg) after normalising by m_t^2.

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
        m = I0 * R ** H
        cv2_emp = Z.var(axis=1, ddof=1) / (Z.mean(axis=1) ** 2)
        cv2_lemma = (1 + R / k_agg) * (1 - R ** (-H)) / (I0 * (R - 1))
        c = 1.0 + 1.0 / k_agg
        cv2_macro = (R ** 2) / (I0 ** 2 * (1 - 1.0 / c / R ** 2)) if False else None
        out[label] = {
            "R": R, "k_agg": k_agg, "I0": I0,
            "cv2_emp": cv2_emp.tolist(),
            "cv2_lemma_with_kagg": cv2_lemma.tolist(),
            "ratio_emp_over_lemma": (cv2_emp / cv2_lemma).tolist(),
        }
        print(f"[{label}] R={R} k_agg={k_agg} I0={I0}")
        print("   h:      ", "  ".join(f"{h:9d}" for h in H))
        print("   emp:    ", "  ".join(f"{v:9.2e}" for v in cv2_emp))
        print("   lemma2: ", "  ".join(f"{v:9.2e}" for v in cv2_lemma))
        print("   emp/lem:", "  ".join(f"{v:9.2f}" for v in cv2_emp / cv2_lemma))
    (REPORTS / "macro_cv_check.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nwrote reports_v3/macro_cv_check.json")


if __name__ == "__main__":
    main()
