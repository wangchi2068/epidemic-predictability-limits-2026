"""Theorem 5R verification (clean): logvar(h) ~ h(1/k + 1/m_t) + Var(sum_{j=1..h} r_{t+j})
with the exact AR(1) closed form. Reports realised vs theory ratio."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
rng = np.random.default_rng(20260807)
G = np.array([0.7, 0.3])


def ar1_sum_var(phi, gamma0, h):
    if abs(phi - 1) < 1e-9:
        return gamma0 * h * (h + 1) * (2 * h + 1) / 6.0
    s1 = (1 - phi ** (h - 1)) / (1 - phi) if h > 1 else 0.0
    s2 = (1 - h * phi ** (h - 1) + (h - 1) * phi ** h) / (1 - phi) ** 2 if h > 1 else 0.0
    S = h * phi * s1 - phi * s2
    return gamma0 * (h + 2 * S)


def renewal_ar1(T, mu, phi, se, k, I0=100.0, cap=1e7):
    r = np.zeros(T + 2)
    r[0] = mu
    for t in range(1, T + 2):
        r[t] = mu + phi * (r[t - 1] - mu) + rng.normal(0, se)
    I = np.zeros(T + 2)
    I[0] = I[1] = I0
    for t in range(2, T + 2):
        mean = min(np.exp(r[t]) * (G[0] * I[t - 1] + G[1] * I[t - 2]), cap)
        I[t] = rng.negative_binomial(k, k / (k + mean)) if mean > 0 else 0.0
        I[t] = min(I[t], cap)
    return np.maximum(I[2:], 0)


def verify(phi, se, k, T, reps, h_max=10):
    mu = np.log(1.05)
    gamma0 = se ** 2 / (1 - phi ** 2)
    realised = np.zeros(h_max + 1)
    theory = np.zeros(h_max + 1)
    cnt = np.zeros(h_max + 1)
    for r_ in range(reps):
        I = renewal_ar1(T, mu, phi, se, k)
        logc = np.log(I + 0.5)
        for t in range(8, T - h_max):
            m_bar = np.mean(I[max(0, t - 4):t + 1])
            if m_bar <= 0.5:
                continue
            for h in range(1, h_max + 1):
                realised[h] += (logc[t + h] - (logc[t] + mu * h)) ** 2
                theory[h] += h * (1.0 / k + 1.0 / m_bar) + ar1_sum_var(phi, gamma0, h)
                cnt[h] += 1
    out = {}
    for h in range(1, h_max + 1):
        out[str(h)] = {"realised": float(realised[h] / cnt[h]),
                       "theory": float(theory[h] / cnt[h]),
                       "ratio": float(realised[h] / max(theory[h], 1e-12))}
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    res = {}
    for phi in [0.0, 0.5, 0.8, 0.95]:
        r = verify(phi, 0.05, k=100.0, T=120, reps=400)
        res[f"phi{phi}"] = r
        med = float(np.median([r[h]["ratio"] for h in r]))
        print(f"phi={phi}: median ratio={med:.3f} | h=1:{r['1']['ratio']:.2f} h=2:{r['2']['ratio']:.2f} h=4:{r['4']['ratio']:.2f} h=8:{r['8']['ratio']:.2f}", flush=True)
    (REPORTS / "verify_t5R.json").write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    print("saved", flush=True)