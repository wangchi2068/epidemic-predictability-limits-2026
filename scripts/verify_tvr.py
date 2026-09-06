"""Verify time-varying-R with iid logR noise: logvar(h) ~ h(v^2 + 1/k)."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
rng = np.random.default_rng(20260807)
G = np.array([0.7, 0.3])


def renewal_iidR(T, R0, v, k, I0=100.0, cap=1e7):
    I = np.zeros(T + 2)
    I[0] = I[1] = I0
    for t in range(2, T + 2):
        R = R0 * np.exp(rng.normal(0, v))
        mean = min(R * (G[0] * I[t - 1] + G[1] * I[t - 2]), cap)
        I[t] = rng.negative_binomial(k, k / (k + mean)) if mean > 0 else 0.0
        I[t] = min(I[t], cap)
    return np.maximum(I[2:], 0)


def verify(R0, v, k, T, reps, h_max=8):
    lam0 = max(R0 - 1, 0.0)
    err2 = np.zeros(h_max + 1)
    cnt = np.zeros(h_max + 1)
    for r in range(reps):
        I = renewal_iidR(T, R0, v, k)
        logc = np.log(I + 0.5)
        for t in range(8, T - h_max):
            pred = logc[t] + lam0 * np.arange(1, h_max + 1)
            err2[1:h_max + 1] += (logc[t + 1:t + 1 + h_max] - pred) ** 2
            cnt[1:h_max + 1] += 1
    emp = err2 / np.maximum(cnt, 1)
    out = {}
    for h in range(1, h_max + 1):
        theory = h * (v ** 2 + 1 / k)
        out[h] = {"emp_logvar": float(emp[h]), "theory": float(theory), "ratio": float(emp[h] / theory)}
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    res = {}
    for v in [0.0, 0.02, 0.05, 0.10]:
        res[f"k100_v{v}"] = verify(1.05, v, 100.0, 100, reps=300)
        print("v=", v, json.dumps(res[f"k100_v{v}"]), flush=True)
    (REPORTS / "verify_tvR.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("saved", flush=True)