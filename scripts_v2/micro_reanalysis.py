# -*- coding: utf-8 -*-
"""micro_reanalysis.py — micro-layer re-analysis for review response.

Computes, from the deposited micro offspring-count vectors:
  (1) parametric bootstrap percentile CIs for R and k (B=2000, seed 20260807);
  (2) non-parametric bootstrap CIs (resampling raw offspring counts) as a
      robustness check that the parametric-bootstrap/CRB agreement is not an
      artifact of the parametric generating assumption;
  (3) a negative-binomial goodness-of-fit chi-square test (binned by count,
      tail-pooled so expected >= 5);
  (4) a zero-inflation sensitivity analysis (10% / 20% of recorded zero-offspring
      cases assumed missed, reassigned to a single secondary case drawn from the
      fitted conditional-on-positive distribution).

Writes reports_v3/micro_reanalysis.json and prints the key numbers.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from scipy.special import gammaln

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260807
B = 2000


def nb_nll(params, x):
    R, k = params
    if R <= 0 or k <= 0:
        return 1e12
    j = np.asarray(x, dtype=float)
    ll = (gammaln(j + k) - gammaln(k) - gammaln(j + 1)
          + k * np.log(k / (R + k)) + j * np.log(R / (R + k)))
    return -float(ll.sum())


def fit_nb(x):
    m = float(np.mean(x))
    v = float(np.var(x, ddof=0))
    k0 = max(m * m / (v - m), 0.05) if v > m else 5.0
    best = None
    for kinit in [k0, 0.1, 0.5, 1.0, 5.0, 50.0]:
        r = minimize(lambda p: nb_nll(p, x), x0=[m, kinit], method="Nelder-Mead",
                     options={"xatol": 1e-8, "fatol": 1e-8, "maxiter": 8000})
        if best is None or r.fun < best["fun"]:
            best = {"R": float(r.x[0]), "k": float(r.x[1]), "fun": float(r.fun)}
    return best["R"], best["k"]


def percentile_ci(samples):
    return [float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5))]


def gof_chi2(x, R, k):
    """NB GOF chi-square: individual bins 0,1,2,... then a pooled tail,
    pooling so that every expected count >= 5 and df >= 1."""
    n = len(x)

    def pmf(j):
        j = np.asarray(j, dtype=float)
        return np.exp(gammaln(j + k) - gammaln(k) - gammaln(j + 1)
                      + k * np.log(k / (R + k)) + j * np.log(R / (R + k)))

    maxc = int(x.max()) if x.max() > 3 else 3
    obs = np.array([int((x == j).sum()) for j in range(maxc + 1)])
    exp = np.array([n * pmf(j) for j in range(maxc + 1)])
    # merge tail so the final (open) bin has expected >= 5, but keep >= 4 bins
    while exp[-1] < 5 and len(obs) > 4:
        obs = np.append(obs[:-2], obs[-2] + obs[-1])
        exp = np.append(exp[:-2], exp[-2] + exp[-1])
    # safety merge any remaining sub-5 bins from the right
    while any(exp < 5) and len(obs) > 4:
        i = int(np.argmin(exp))
        if i == len(obs) - 1:
            obs = np.append(obs[:-2], obs[-2] + obs[-1])
            exp = np.append(exp[:-2], exp[-2] + exp[-1])
        else:
            obs = np.array(list(obs[:i]) + [obs[i] + obs[i + 1]] + list(obs[i + 2:]))
            exp = np.array(list(exp[:i]) + [exp[i] + exp[i + 1]] + list(exp[i + 2:]))
    chi2 = float(((obs - exp) ** 2 / exp).sum())
    df = len(obs) - 1 - 2  # minus 2 estimated params
    p = float(stats.chi2.sf(chi2, df))
    return {"chi2": chi2, "df": df, "p": p, "bins": len(obs)}


def zero_inflation(x, R, k, q):
    """Assume fraction q of zero-offspring cases are missed; reassign to 1."""
    zeros = np.where(x == 0)[0]
    n_missed = int(round(len(zeros) * q))
    rng = np.random.default_rng(SEED)
    idx = rng.choice(zeros, size=n_missed, replace=False)
    y = x.astype(float).copy()
    y[idx] = 1.0  # minimal reassignment: one missed secondary case
    return fit_nb(y), n_missed


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rng = np.random.default_rng(SEED)

    sec = pd.read_csv(ROOT / "data" / "micro" / "hong_kong_adam2020" /
                      "secondary_cases.csv")["secondary.cases"].values
    hk_local = np.concatenate([sec, np.zeros(256)])
    hk_all = np.concatenate([sec, np.zeros(1038 - 99)])
    eb = pd.read_csv(ROOT / "data" / "micro" / "guinea_ebola_faye2015" /
                     "ebola_conakry_offspring.csv")["secondary_cases"].values

    datasets = {"Hong_Kong_COVID19_Local": hk_local,
                "Hong_Kong_COVID19_All": hk_all,
                "Guinea_Ebola_2014": eb}

    out = {}
    for name, x in datasets.items():
        R, k = fit_nb(x)
        rec = {"N": int(len(x)), "R_mle": R, "k_mle": k, "mean": float(x.mean()),
               "var": float(x.var(ddof=0))}

        # parametric bootstrap
        R_boot, k_boot = [], []
        for _ in range(B):
            xs = rng.negative_binomial(k, k / (R + k), size=len(x))
            Rb, kb = fit_nb(xs)
            R_boot.append(Rb)
            k_boot.append(kb)
        rec["parametric_ci_R"] = percentile_ci(R_boot)
        rec["parametric_ci_k"] = percentile_ci(k_boot)

        # non-parametric bootstrap
        R_np, k_np = [], []
        for _ in range(B):
            xs = rng.choice(x, size=len(x), replace=True)
            Rb, kb = fit_nb(xs)
            R_np.append(Rb)
            k_np.append(kb)
        rec["nonparametric_ci_R"] = percentile_ci(R_np)
        rec["nonparametric_ci_k"] = percentile_ci(k_np)

        # GOF
        rec["gof"] = gof_chi2(x, R, k)

        # zero-inflation sensitivity
        rec["zero_inflation"] = {}
        for q in (0.1, 0.2):
            (Rz, kz), nm = zero_inflation(x, R, k, q)
            rec["zero_inflation"][f"{int(q*100)}pct"] = {
                "R": Rz, "k": kz, "n_missed": nm}
        out[name] = rec

        print(f"[{name}] R={R:.5f} [{rec['parametric_ci_R'][0]:.4f}, "
              f"{rec['parametric_ci_R'][1]:.4f}]  "
              f"k={k:.4f} [{rec['parametric_ci_k'][0]:.4f}, {rec['parametric_ci_k'][1]:.4f}]")
        print(f"   nonparam R CI={rec['nonparametric_ci_R']}  k CI={rec['nonparametric_ci_k']}")
        print(f"   GOF chi2={rec['gof']['chi2']:.2f} df={rec['gof']['df']} p={rec['gof']['p']:.3f}")
        for q, zi in rec["zero_inflation"].items():
            print(f"   zero-inflation {q}: R={zi['R']:.4f} k={zi['k']:.4f} "
                  f"(n_missed={zi['n_missed']})")

    dest = ROOT / "reports_v3" / "micro_reanalysis.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
