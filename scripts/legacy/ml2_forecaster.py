"""ML-2 v4: GW DGP; LightGBM log-scale forecast RMSE vs empirical conditional
log-variance floor (tightness demonstration)."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import lightgbm as lgb

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
rng = np.random.default_rng(20260807)


def gw_series(T, R, k, I0, seed):
    r = np.random.default_rng(seed)
    Z = np.zeros(T + 1)
    Z[0] = I0
    p = k / (k + R)
    for n in range(1, T + 1):
        m = Z[n - 1]
        Z[n] = r.negative_binomial(np.maximum(m * k, 1e-9), p) if m > 0 else 0.0
    return Z


def make_data(seqs, h_max, n_lags=6, min_z=100.0):
    X, y, zt, hcol = [], [], [], []
    for s in seqs:
        logc = np.log(s + 0.5)
        T = len(logc)
        for t in range(n_lags, T - h_max):
            if s[t] < min_z:
                continue
            feat = list(logc[t - n_lags + 1:t + 1])
            for h in range(1, h_max + 1):
                X.append(feat + [h / h_max]); y.append(logc[t + h]); zt.append(s[t]); hcol.append(h)
    return np.array(X), np.array(y), np.array(zt), np.array(hcol)


def run_ml2(R, k, I0, T, n_train, n_test, h_max):
    tr = [gw_series(T, R, k, I0, i) for i in range(n_train)]
    te = [gw_series(T, R, k, I0, 100000 + i) for i in range(n_test)]
    Xtr, ytr, _, htr = make_data(tr, h_max)
    Xte, yte, zt, hte = make_data(te, h_max)
    model = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, num_leaves=15,
                              min_child_samples=50, verbosity=-1, n_jobs=4)
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)
    out = {}
    for h in range(1, h_max + 1):
        mm = hte == h
        a = yte[mm]; p = pred[mm]; z = zt[mm]
        ml_rmse = float(np.sqrt(np.mean((p - a) ** 2)))
        # theory conditional log-SD per sample (delta method, GW):
        # Var(log Z_{t+h} | Z_t) ~ (1+R/k)(1-R^{-h}) / (Z_t * R * (R-1))
        theo_per = np.sqrt((1 + R / k) * (1 - R ** (-h)) / (z * R * (R - 1)))
        theo = float(np.sqrt(np.mean(theo_per ** 2)))
        # empirical conditional floor: fine bins (20) on Z_t
        edges = np.quantile(z, np.linspace(0, 1, 21))
        wsum, wvar = 0.0, 0.0
        for i in range(20):
            m = (z >= edges[i]) & (z < edges[i + 1])
            if m.sum() < 20:
                continue
            v = a[m].var(ddof=1)
            wsum += m.sum(); wvar += m.sum() * v
        floor = float(np.sqrt(wvar / max(wsum, 1)))
        out[h] = {"ml_log_rmse": ml_rmse, "emp_floor": floor, "theory_log_sd": theo,
                  "ml_over_floor": ml_rmse / max(floor, 1e-9),
                  "ml_over_theory": ml_rmse / max(theo, 1e-9), "n": int(mm.sum())}
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    res = {}
    for R, k, I0, T in [(1.5, 0.3, 500, 15), (1.3, 1.0, 500, 20), (1.1, 5.0, 500, 25)]:
        r = run_ml2(R, k, I0, T, n_train=500, n_test=200, h_max=8)
        print(f"R{R}_k{k}:", json.dumps(r), flush=True)
        res[f"R{R}_k{k}"] = r
    (REPORTS / "ml2_forecast_vs_bound.json").write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    print("saved", flush=True)