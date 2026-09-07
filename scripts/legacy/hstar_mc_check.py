"""Monte Carlo verification of exact P(h) and closed-form h* error."""

import numpy as np


sys = None  # noqa

rng = np.random.default_rng(20260807)


def P_mc(h, R, dR, n=2_000_000):
    """Monte Carlo P(h) = E[(Y^h - 1)^2], Y = Rhat/R ~ N(1, (dR/R)^2)."""
    y = 1 + rng.normal(0, dR / R, n)
    y = np.clip(y, 1e-6, None)
    return np.mean((y**h - 1) ** 2)


def P_linear(h, R, dR):
    return (h * dR / R) ** 2


def P_moment(h, R, dR):
    """Moment expansion used in hstar_approx_error."""
    s2 = (dR / R) ** 2
    if s2 > 0.04:
        mu = -0.5 * np.log(1 + s2)
        sg = np.sqrt(np.log(1 + s2))
        return (
            np.exp(2 * h * mu + (2 * h * sg) ** 2 / 2)
            - 2 * np.exp(h * mu + (h * sg) ** 2 / 2)
            + 1
        )
    from math import comb

    def dfac(n):
        r = 1
        for i in range(n, 0, -2):
            r *= i
        return r

    def moment(m):
        try:
            m_int = int(m)
        except (TypeError, ValueError):
            m_int = None
        if m_int is not None and abs(m - m_int) < 1e-9:
            mi = m_int
            return sum(comb(mi, 2 * k) * dfac(2 * k - 1) * s2**k for k in range(20))
        mu = -0.5 * np.log(1 + s2)
        sg = np.sqrt(np.log(1 + s2))
        return np.exp(m * mu + (m * sg) ** 2 / 2)

    return moment(2 * h) - 2 * moment(h) + 1


print(f"{'R':>5} {'dR':>5} {'h':>5} {'P_linear':>10} {'P_moment':>10} {'P_MC':>10}")
for R, dR, h in [
    (1.05, 0.01, 10),
    (1.05, 0.05, 5),
    (1.2, 0.03, 8),
    (1.5, 0.1, 4),
    (1.05, 0.01, 27),
]:
    pl = P_linear(h, R, dR)
    pm = P_moment(h, R, dR)
    pmc = P_mc(h, R, dR)
    print(f"{R:>5.2f} {dR:>5.2f} {h:>5.0f} {pl:>10.5f} {pm:>10.5f} {pmc:>10.5f}")
    print(f"       比值: linear/MC={pl / pmc:.3f}, moment/MC={pm / pmc:.3f}")
