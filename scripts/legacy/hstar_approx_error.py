"""Evaluate closed-form h* approximation error vs exact solution (analytic moments)."""

import numpy as np

from scipy.optimize import brentq


def _double_factorial(n):
    if n <= 0:
        return 1
    r = 1
    for i in range(n, 0, -2):
        r *= i
    return r


def exact_P_analytic(h, R, dR):
    """Exact P(h) = E[(Y^h - 1)^2] via normal-moment expansion.

    Y = Rhat/R with Rhat ~ N(R, dR^2), so Y ~ N(1, s^2), s = dR/R.
    P(h) = E[Y^{2h}] - 2E[Y^h] + 1, E[Y^m] = sum_k C(m,2k) (2k-1)!! s^{2k}.
    For s > 0.2 the lognormal approximation is used for stability.
    """
    s2 = (dR / R) ** 2
    if s2 > 0.04:
        mu = -0.5 * np.log(1 + s2)
        sg = np.sqrt(np.log(1 + s2))
        e2 = np.exp(2 * h * mu + (2 * h * sg) ** 2 / 2)
        e1 = np.exp(h * mu + (h * sg) ** 2 / 2)
        return e2 - 2 * e1 + 1
    from math import comb

    def moment(m):
        """E[Y^m] for Y ~ N(1, s^2): normal-moment expansion at integer m,
        lognormal interpolation at non-integer m (root finding passes floats)."""
        try:
            m_int = int(m)
        except (TypeError, ValueError):
            m_int = None
        if m_int is not None and abs(m - m_int) < 1e-9:
            try:
                mi = int(m)
            except (TypeError, ValueError):
                mi = 0
            return sum(
                comb(mi, 2 * k) * _double_factorial(2 * k - 1) * s2**k
                for k in range(20)
            )
        mu = -0.5 * np.log(1 + s2)
        sg = np.sqrt(np.log(1 + s2))
        return np.exp(m * mu + (m * sg) ** 2 / 2)

    m2 = moment(2 * h)
    m1 = moment(h)
    return m2 - 2 * m1 + 1


def exact_hstar(tau, R, k, I0, dR):
    """Solve tau^2 = CV2(h) + P(h) exactly."""

    def obj(h):
        cv2 = (
            (1 + R / k) * (1 - R**-h) / (I0 * (R - 1))
            if R != 1
            else h * (1 + 1 / k) / I0
        )
        return cv2 + exact_P_analytic(h, R, dR) - tau**2

    lo, hi = 0.01, 2.0
    f_lo = obj(lo)
    for _ in range(14):
        f_hi = obj(hi)
        if f_lo * f_hi < 0:
            break
        hi *= 2
    else:
        return None
    try:
        return brentq(obj, lo, hi)
    except Exception:
        return None


def closed_hstar(tau, R, k, I0, dR):
    """Closed form: h* = (R/dR) * sqrt(tau^2 - (1+R/k)/(I0(R-1)))."""
    floor = (1 + R / k) / (I0 * (R - 1)) if R != 1 else (1 + 1 / k) / I0
    arg = tau**2 - floor
    if arg <= 0:
        return None
    return (R / dR) * np.sqrt(arg)


configs = []
for R in [1.05, 1.1, 1.2, 1.5]:
    for dR in [0.01, 0.03, 0.05, 0.1]:
        for tau in [0.3, 0.5, 0.8]:
            configs.append((R, dR, tau))

k, I0 = 5, 100
results = []
for R, dR, tau in configs:
    hx = exact_hstar(tau, R, k, I0, dR)
    hc = closed_hstar(tau, R, k, I0, dR)
    if hx and hc:
        rel = abs(hc - hx) / hx * 100
        results.append((rel, hx * dR, hx, hc))

results.sort(reverse=True)
print(f"总配置数: {len(configs)}, 有效解: {len(results)}")
if results:
    print(f"最大相对误差: {results[0][0]:.1f}%")
    print(
        f"平均相对误差: {np.mean([r[0] for r in results]):.1f}%, P90: {np.percentile([r[0] for r in results], 90):.1f}%"
    )
    print("\n按 hδR 分组:")
    groups = {}
    for rel, hd, _hx, _hc in results:
        key = "hδR<0.1" if hd < 0.1 else ("0.1≤hδR<0.3" if hd < 0.3 else "hδR≥0.3")
        groups.setdefault(key, []).append(rel)
    for key, vals in sorted(groups.items()):
        print(
            f"  {key}: n={len(vals)}, 平均误差={np.mean(vals):.1f}%, 最大={max(vals):.1f}%"
        )
    print("\n误差最大的5个配置:")
    for rel, hd, hx, hc in results[:5]:
        print(f"  相对误差={rel:.1f}%, hδR={hd:.3f}, h*精确={hx:.2f}, h*闭式={hc:.2f}")
