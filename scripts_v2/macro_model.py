# -*- coding: utf-8 -*-
"""macro_model.py — the fixed-k_agg macro negative-binomial update model.

Single source of truth for the aggregate (state-level) mechanism caliber.

Model (weekly clock, because k_agg is estimated from weekly log-differences):

    Z_t | F_{t-1} ~ NB(mu_t, k_agg),   mu_t = R_week * Z_{t-1},
    Var(Z_t | F_{t-1}) = R_week Z_{t-1} + R_week^2 Z_{t-1}^2 / k_agg,

so the conditional variance carries a QUADRATIC state term, unlike the
individual-level Galton-Watson process whose conditional variance is linear
in Z_{t-1}.  The two models therefore have different multi-step variance laws.

Exact finite-step variance (Cor. 5 in the manuscript): with m_t = I0 R_week^t,
V_t = Var(Z_t), q = R_week^2 (1 + 1/k_agg),

    V_h = I0 R_week (q^h - R_week^h)/(q - R_week) + I0^2 (q^h - R_week^{2h}),

    CV^2_macro(h) = V_h / (I0 R_week^h)^2
                  = [(1 + 1/k_agg)^h - 1]
                    + (1/I0) (q^h - R_week^h) / ((q - R_week) R_week^{2h-1}).

Its h/k_agg << 1 leading order is h/k_agg, i.e. it reproduces the leading-order
law used before; the geometric correction is what the micro closed form misses.
"""
from __future__ import annotations

import numpy as np


def cv2_macro(h, R, k, I0):
    """Relative variance CV^2 of the fixed-k_agg macro NB update model.

    h : horizon in the update clock (weeks), scalar or array.
    R : one-step growth multiplier on that clock (e.g. exp(b_week)).
    k : aggregate dispersion k_agg (> 0).
    I0: initial level (window mean).
    """
    h = np.asarray(h, dtype=float)
    if R <= 0 or k <= 0 or I0 <= 0:
        return np.full_like(h, np.nan)
    q = R * R * (1.0 + 1.0 / k)
    if abs(R - 1.0) < 1e-9:
        # limit of the general closed form as R -> 1
        return (k / I0 + 1.0) * ((1.0 + 1.0 / k) ** h - 1.0)
    if abs(q - R) < 1e-12:
        first = I0 * R * h * R ** (h - 1.0)
    else:
        first = I0 * R * (q ** h - R ** h) / (q - R)
    second = I0 * I0 * (q ** h - R ** (2.0 * h))
    return (first + second) / (I0 * R ** h) ** 2


def cv2_micro(h, R, k, I0):
    """Individual-level Galton-Watson relative variance (lemmas 1-2).

    h in generations; this is the manuscript's previous state-level caliber
    when evaluated at k = k_agg, retained only as a scale-mapping sensitivity.
    """
    h = np.asarray(h, dtype=float)
    if R > 1.0:
        return (1.0 + R / k) * (1.0 - R ** (-h)) / (I0 * (R - 1.0))
    if abs(R - 1.0) < 1e-9:
        return (1.0 + 1.0 / k) * h / I0
    return (1.0 + R / k) * (R ** (-h) - 1.0) / (I0 * (1.0 - R))


def cv2_macro_leading(h, R, k, I0):
    """h/k_agg leading order of cv2_macro (Cor. 4), kept for comparison."""
    h = np.asarray(h, dtype=float)
    return h / k
