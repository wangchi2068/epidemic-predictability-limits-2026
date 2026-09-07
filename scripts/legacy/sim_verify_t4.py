"""T4 re-verification: proper signed-error variance, conditional on total parents.
Reports ratio; if < 1, T4 is restated as a conservative sufficient bound."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
rng = np.random.default_rng(20260807)


def sim_gw_mle(R, k, I0, T, reps):
    p = k / (k + R)
    signed, cums = [], []
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
            signed.append(off_total / parents_total - R)
            cums.append(parents_total)
    signed = np.array(signed); cums = np.array(cums)
    out = []
    for lo, hi in [(100, 1000), (1000, 5000), (5000, 20000), (20000, np.inf)]:
        m = (cums >= lo) & (cums < hi)
        if m.sum() < 20:
            continue
        emp_var = signed[m].var(ddof=1)
        theo_var = (R + R ** 2 / k) / np.mean(cums[m])
        out.append({"cum_range": f"{lo}-{hi}", "n": int(m.sum()),
                    "emp_var": float(emp_var), "theory_var": float(theo_var),
                    "ratio_var": float(emp_var / theo_var),
                    "emp_sd_rel": float(np.sqrt(emp_var) / R),
                    "theory_sd_rel": float(np.sqrt(theo_var) / R)})
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    res = {}
    for R, k, I0, T in [(1.3, 1.0, 20, 30), (1.5, 0.3, 30, 25), (1.05, 1.0, 50, 50)]:
        res[f"R{R}_k{k}"] = sim_gw_mle(R, k, I0, T, reps=2500)
        print(f"R{R}_k{k}:", json.dumps(res[f"R{R}_k{k}"]), flush=True)
    (REPORTS / "verify_t4.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("saved", flush=True)