"""xmin sensitivity analysis for Theorem 3 quasi-stationary CV."""

import numpy as np
from scipy.integrate import quad


def qs_cv(xmin, R, N, eps):
    """Compute CV of quasi-stationary density pi(x) ~ x^-1 exp(c1 x - c2 x^2) on (xmin, inf)."""
    c1 = 2 * eps / (R + 1)
    c2 = R / (N * (R + 1))

    def pi(x):
        return np.exp(-np.log(x) + c1 * x - c2 * x**2)

    # mean and second moment via numerical integration
    Z, _ = quad(lambda x: pi(x), xmin, np.inf, limit=200)
    m1, _ = quad(lambda x: x * pi(x), xmin, np.inf, limit=200)
    m2, _ = quad(lambda x: x * x * pi(x), xmin, np.inf, limit=200)
    mean = m1 / Z
    var = m2 / Z - mean**2
    return np.sqrt(max(var, 0)) / mean


def main():
    N = 2000
    print("xmin sensitivity for canonical T3(a) cells (N=2000):")
    print(
        f"{'eps':>5} {'R':>5} {'xmin=0.05':>12} {'xmin=0.1':>12} {'xmin=0.2':>12} {'xmin=0.5':>12} {'max change %':>14}"
    )
    for eps in [0.2, 0.4]:
        R = 1 + eps
        vals = [qs_cv(xm, R, N, eps) for xm in [0.05, 0.1, 0.2, 0.5]]
        base = vals[1]  # xmin=0.1 reference
        max_change = max(abs(v - base) / base * 100 for v in vals)
        print(
            f"{eps:>5} {R:>5.1f} "
            + " ".join(f"{v:>12.4f}" for v in vals)
            + f" {max_change:>13.2f}%"
        )


if __name__ == "__main__":
    main()
