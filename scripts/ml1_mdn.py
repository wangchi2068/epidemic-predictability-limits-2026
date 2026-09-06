"""ML-1 v3: MLP point estimator + residual-based calibrated intervals.
Claims: unbiased point estimates; uncertainty reaches (not crosses) the T4
floor; horizon extension vs short-window classical estimator."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
torch.manual_seed(20260807)
rng = np.random.default_rng(20260807)

T = 12


def sim_traj(R, k, I0, T):
    p = k / (k + R)
    Z = np.zeros(T + 1)
    Z[0] = I0
    for n in range(1, T + 1):
        m = Z[n - 1]
        Z[n] = rng.negative_binomial(np.maximum(m * k, 1e-9), p) if m > 0 else 0.0
    return Z


OBS_NOISE = 0.30

def features(Z):
    Z = np.maximum(Z * np.exp(rng.normal(0, OBS_NOISE / 2, Z.shape)), 0.5)  # observation noise
    logc = np.log(Z + 0.5)
    steps = np.diff(logc)
    g = np.mean(steps)
    v = np.var(steps) + 1e-8
    cum = np.log(np.sum(Z) + 1)
    return np.array([g, np.log(v), cum]), Z


def gen_batch(n):
    R = rng.uniform(1.05, 2.0, n)
    k = np.exp(rng.uniform(np.log(0.1), np.log(5.0), n))
    I0 = np.exp(rng.uniform(np.log(50), np.log(2000), n))
    X = np.zeros((n, 3))
    Zobs = []
    for i in range(n):
        Z = sim_traj(R[i], k[i], I0[i], T)
        X[i], Zo = features(Z)
        Zobs.append(Zo)
    Zobs = np.array(Zobs)
    y = np.stack([np.log(R), np.log(k)], axis=1)
    return X.astype(np.float32), y.astype(np.float32), R, k, I0, Zobs


class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(3, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(),
                                 nn.Linear(64, 2))

    def forward(self, x):
        return self.net(x)


def train():
    Xtr, ytr, _, _, _, _ = gen_batch(40000)
    Xcal, ycal, Rcal, kcal, I0cal, Zcal = gen_batch(8000)
    Xte, yte, Rte, kte, I0te, Zte = gen_batch(8000)
    mu_f, sd_f = Xtr.mean(0), Xtr.std(0) + 1e-6
    Xtr = (Xtr - mu_f) / sd_f
    Xcal = (Xcal - mu_f) / sd_f
    Xte_raw = Xte.copy()
    Xte = (Xte - mu_f) / sd_f
    model = MLP()
    opt = torch.optim.Adam(model.parameters(), lr=3e-3)
    Xt = torch.from_numpy(Xtr); yt = torch.from_numpy(ytr)
    for ep in range(40):
        model.train()
        perm = torch.randperm(len(Xt))
        tot = 0.0
        for i in range(0, len(Xt), 512):
            idx = perm[i:i + 512]
            pred = model(Xt[idx])
            loss = ((pred - yt[idx]) ** 2).mean()
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item() * len(idx)
        if ep % 10 == 0:
            print(f"epoch {ep} loss {tot / len(Xt):.5f}", flush=True)
    model.eval()
    with torch.no_grad():
        pred_cal = model(torch.from_numpy(Xcal)).numpy()
        pred_te = model(torch.from_numpy(Xte)).numpy()
    res_cal = ycal - pred_cal          # residuals on (logR, logk)
    # feature-adaptive residual SD: bin by the log-cumulative feature (Xcal[:,2], standardized)
    edges = np.quantile(Xcal[:, 2], [0.25, 0.5, 0.75])
    sd_logR = np.std(res_cal[:, 0])
    sd_logk = np.std(res_cal[:, 1])
    bin_sd = []
    for i in range(4):
        lo = -np.inf if i == 0 else edges[i - 1]
        hi = np.inf if i == 3 else edges[i]
        m = (Xcal[:, 2] >= lo) & (Xcal[:, 2] < hi)
        bin_sd.append(np.std(res_cal[m, 0]) if m.sum() > 50 else sd_logR)
    bin_id = np.digitize(Xte[:, 2], edges)
    sd_logR_adapt = np.array([bin_sd[i] for i in bin_id])
    # residual-based 90% interval coverage
    lo = np.quantile(res_cal[:, 0], 0.05); hi = np.quantile(res_cal[:, 0], 0.95)
    cover = float(np.mean((yte[:, 0] >= pred_te[:, 0] + lo) & (yte[:, 0] <= pred_te[:, 0] + hi)))
    Rhat = np.exp(pred_te[:, 0]); khat = np.exp(pred_te[:, 1])
    dR_mlp = Rhat * sd_logR_adapt
    cum = np.exp(Xte_raw[:, 2])
    parents = Zte[:, :-1].sum(1); off = Zte[:, 1:].sum(1)
    Rmle = off / np.maximum(parents, 1)
    keep = cum > 5000
    Rte, kte, cum, Rhat, khat, dR_mlp = Rte[keep], kte[keep], cum[keep], Rhat[keep], khat[keep], dR_mlp[keep]
    Rmle, parents = Rmle[keep], parents[keep]
    floor = Rte * np.sqrt((1 / Rte + 1 / kte) / cum)
    # classical MLE on the noisy trajectory (best case: true k used)
    dR_classic = Rmle * np.sqrt((1 / Rmle + 1 / kte) / np.maximum(parents, 1))
    out = {"n": len(Xte), "coverage_90_residual": cover,
           "sd_logR": float(sd_logR), "sd_logk": float(sd_logk),
           "median_dR_mlp_over_floor": float(np.median(dR_mlp / floor)),
           "median_dR_classic_over_floor": float(np.median(dR_classic / floor)),
           "median_horizon_ratio_mlp_vs_classic": float(np.median(dR_classic / np.maximum(dR_mlp, 1e-9))),
           "bias_logR": float(np.mean(Rhat - Rte) / np.mean(Rte)),
           "bias_logk": float(np.mean(khat - kte) / np.mean(kte))}
    # Action 2: paired bootstrap significance of the delta_R / horizon advantage
    rng = np.random.default_rng(11)
    diff = dR_classic - dR_mlp          # positive = MLP better
    n = len(diff)
    bs_med = []
    for _ in range(3000):
        s = rng.integers(0, n, n)
        bs_med.append(np.median(diff[s]))
    bs_med = np.array(bs_med)
    p_lt = float(np.mean(bs_med <= 0))
    out["action2"] = {"median_dR_classic_minus_mlp": float(np.median(diff)),
                      "ci95": [float(np.quantile(bs_med, 0.025)), float(np.quantile(bs_med, 0.975))],
                      "p_value_one_sided_mlp_lt_classic": p_lt,
                      "median_horizon_ratio": float(np.median(dR_classic / np.maximum(dR_mlp, 1e-9)))}
    (REPORTS / "ml1_mdn.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2), flush=True)
    print("saved", flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    train()