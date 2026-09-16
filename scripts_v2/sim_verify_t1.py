"""T1 re-verification with the EXACT Gaussian parameter term (normal moments):
E[(Rhat^h - R^h)^2]/R^{2h} = sum_{j,k: j+k even} C(h,j)C(h,k) R^{-j-k} (j+k-1)!! dR^{j+k}."""
from __future__ import annotations
import json, sys, math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
rng = np.random.default_rng(20260807)


def normal_moment(m, mu, sig):
    """E[X^m] for X ~ N(mu, sig^2)."""
    s = 0.0
    for j in range(0, m // 2 + 1):
        s += math.comb(m, 2 * j) * math.prod(range(1, 2 * j, 2)) * sig ** (2 * j) * mu ** (m - 2 * j)
    return s

def gauss_param_term(h, R, dR):
    """E[(Rhat^h - R^h)^2]/R^{2h} for Rhat ~ N(R, dR^2)."""
    return (normal_moment(2 * h, R, dR) - 2 * R ** h * normal_moment(h, R, dR) + R ** (2 * h)) / R ** (2 * h)


def cv_formula(n, I0, R, k):
    return np.sqrt((1 + R / k) * (1 - R ** (-n)) / (I0 * (R - 1)))

def sim_gw(I0, R, k, n_max, reps=20000, seed=20260807):
    """Simulate Galton-Watson branching process trajectories."""
    rng_local = np.random.default_rng(seed)
    Z = np.zeros((reps, n_max + 1))
    Z[:, 0] = I0
    p = k / (k + R)
    for n in range(1, n_max + 1):
        m = Z[:, n - 1]
        Z[:, n] = np.where(m > 0, rng_local.negative_binomial(np.maximum(m * k, 1e-9), p), 0.0)
    return Z



def verify_case(R, k, I0, dR, n_max, reps=20000):
    Z = np.zeros((reps, n_max + 1))
    Z[:, 0] = I0
    p = k / (k + R)
    for n in range(1, n_max + 1):
        m = Z[:, n - 1]
        Z[:, n] = np.where(m > 0, rng.negative_binomial(np.maximum(m * k, 1e-9), p), 0.0)
    E = Z.mean(0)
    emp_cv = np.sqrt(Z.var(0)) / E
    theory_cv = np.array([cv_formula(n, I0, R, k) for n in range(n_max + 1)])
    Rhat = np.clip(rng.normal(R, dR, size=reps), 0.05, None)
    out = {}
    for h in range(1, n_max + 1):
        pred = I0 * Rhat ** h
        rel_mse = np.mean(((Z[:, h] - pred) / E[h]) ** 2)
        param_exact = gauss_param_term(h, R, dR)
        dem = (1 + R / k) * (1 - R ** (-h)) / (I0 * (R - 1))
        theory = np.sqrt(param_exact + dem)
        out[h] = {"emp_rel_rmse": float(np.sqrt(rel_mse)), "theory_exact": float(theory),
                  "ratio": float(np.sqrt(rel_mse) / theory)}
    return {"cv_ratio_median": float(np.median(emp_cv[1:] / theory_cv[1:])),
            "err_ratio_median": float(np.median([out[h]["ratio"] for h in out])),
            "err_ratio_range": [float(min(out[h]["ratio"] for h in out)), float(max(out[h]["ratio"] for h in out))],
            "per_h": {str(h): out[h] for h in out}}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    res = {}
    for cfg in [dict(R=1.5, k=5.0, I0=100, dR=0.10, n_max=12),
                dict(R=1.5, k=0.3, I0=100, dR=0.15, n_max=12),
                dict(R=1.1, k=1.0, I0=50, dR=0.05, n_max=15),
                dict(R=2.0, k=5.0, I0=30, dR=0.20, n_max=10)]:
        r = verify_case(**cfg)
        res[f"R{cfg['R']}_k{cfg['k']}"] = r
        print(f"R{cfg['R']}_k{cfg['k']}:", json.dumps({k2: v for k2, v in r.items() if k2 != "per_h"}), flush=True)
    (REPORTS / "verify_t1.json").write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    print("saved", flush=True)