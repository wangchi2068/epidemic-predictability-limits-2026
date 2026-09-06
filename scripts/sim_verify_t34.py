"""Run legacy secondary T4/T3 diagnostics.

The canonical Theorem 3 verification is scripts/sim_verify_t3.py, which writes
reports/verify_t3.json. This combined logistic birth-death experiment is kept
only as a secondary diagnostic and must not be used as the source for the
paper's Theorem 3 configuration or reported values.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
rng = np.random.default_rng(20260807)


# ---------- T4: identification limit ----------
def sim_gw_mle(R, k, I0, T, reps):
    """Return MLE error vs cumulative-infection formula."""
    p = k / (k + R)
    rel_errors = []
    cums = []
    for _ in range(reps):
        Z = np.zeros(T + 1)
        Z[0] = I0
        parents_total = 0.0
        off_total = 0.0
        for n in range(1, T + 1):
            m = Z[n - 1]
            if m <= 0:
                break
            off = rng.negative_binomial(np.maximum(m * k, 1e-9), p)
            Z[n] = off
            parents_total += m
            off_total += off
        if parents_total > 0:
            Rhat = off_total / parents_total
            rel_errors.append(abs(Rhat - R) / R)
            cums.append(parents_total)
    rel_errors = np.array(rel_errors)
    cums = np.array(cums)
    # binned comparison: theory delta_R/R ~ sqrt((1+R/k)/cum)
    bins = np.quantile(cums, [0.2, 0.4, 0.6, 0.8])
    out = []
    edges = [0] + list(bins) + [np.inf]
    for i in range(len(edges) - 1):
        m = (cums >= edges[i]) & (cums < edges[i + 1])
        if m.sum() < 20:
            continue
        emp = rel_errors[m].std()
        theo = np.sqrt((1 + R / k) / np.mean(cums[m]))
        out.append(
            {
                "cum_min": float(edges[i]),
                "cum_max": float(edges[i + 1]),
                "n": int(m.sum()),
                "emp_sd_rel": float(emp),
                "theory": float(theo),
                "ratio": float(emp / theo),
            }
        )
    return out


def verify_t4() -> dict:
    res = {}
    for R, k, I0, T in [(1.3, 1.0, 20, 25), (1.5, 0.3, 30, 20), (1.05, 1.0, 50, 40)]:
        res[f"R{R}_k{k}"] = sim_gw_mle(R, k, I0, T, reps=800)
    # sign-resolution check: for epsilon, required cumulative = (1+R/k)/eps^2
    sig = {}
    for eps in [0.02, 0.05, 0.1]:
        for k in [0.3, 1.0, 5.0]:
            R = 1 + eps
            sig[f"eps{eps}_k{k}"] = {"required_cumulative": (1 + R / k) / eps**2}
    return {"mle_binned": res, "sign_resolution": sig}


# ---------- Legacy secondary T3 diagnostics (logistic birth-death) ----------
def logistic_bd_sim(N, R, i0, T_max, rep):
    """Gillespie logistic birth-death: births R*i*(1-i/N), deaths i.
    Returns (established, ext_time_or_T, final_size, history_lengths)."""
    i = i0
    t = 0.0
    hist = [i]
    established = False
    while t < T_max and i > 0:
        if i >= 0.05 * N:
            established = True
        birth = R * i * (1 - i / N)
        death = i
        rate = birth + death
        if rate <= 0:
            break
        t += rng.exponential(1.0 / rate)
        if rng.random() < birth / rate:
            i += 1
        else:
            i -= 1
        if len(hist) < 20000:
            hist.append(i)
        if established and t > 5 * N:
            break
    return established, t, i, hist


def verify_t3() -> dict:
    # (a) establishment probability vs 2 eps / R
    estab = {}
    for N in [1000, 5000]:
        for eps in [0.02, 0.05, 0.10, 0.20]:
            R = 1 + eps
            reps = 400
            ok = sum(logistic_bd_sim(N, R, 1, 1e7, r)[0] for r in range(reps))
            estab[f"N{N}_eps{eps}"] = {
                "emp": ok / reps,
                "theory_2eps_over_R": 2 * eps / R,
            }
    # (b) extinction time scaling: critical (eps=0) vs subcritical (eps<0)
    ext = {}
    for N in [100, 300, 1000]:
        for eps in [-0.05, 0.0, 0.03]:
            R = 1 + eps
            times = []
            for r in range(150):
                _, t, i, _ = logistic_bd_sim(N, R, max(2, int(0.02 * N)), 5e6, r)
                if i == 0:
                    times.append(t)
            ext[f"N{N}_eps{eps}"] = {
                "median_ext_time": float(np.median(times)) if times else None,
                "n_extinct": len(times),
            }
    # (c) stationary CV vs sqrt((R+1)/(2 eps))
    cv = {}
    for eps in [0.05, 0.10, 0.20]:
        R = 1 + eps
        N = 2000
        i0 = int(eps * N / R)
        ok = 0
        hist_full = []
        while ok < 50:
            est, t, i, hist = logistic_bd_sim(N, R, i0, 2e7, ok)
            if est:
                hist_full.append(hist)
                ok += 1
        lens = min(len(h) for h in hist_full)
        hh = np.array([h[-lens:] for h in hist_full])
        burn = lens // 2
        st = hh[:, burn:].mean(axis=0)
        cv_emp = st.std() / st.mean()
        cv[f"eps{eps}"] = {
            "emp_cv": float(cv_emp),
            "theory": float(np.sqrt((R + 1) / (2 * eps))),
        }
    return {"establishment": estab, "extinction": ext, "stationary_cv": cv}


if __name__ == "__main__":
    r4 = verify_t4()
    print("T4:", json.dumps(r4, indent=1)[:2200], flush=True)
    r3 = verify_t3()
    print("T3:", json.dumps(r3, indent=1)[:2600], flush=True)
    report = {
        "metadata": {
            "status": "legacy_secondary",
            "canonical_t3_report": "reports/verify_t3.json",
            "note": "Do not use this experiment as the source for paper T3 values.",
        },
        "t4": r4,
        "t3": r3,
    }
    (REPORTS / "verify_t34.json").write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )
    print("saved", flush=True)
