"""Generate paper figures 1-4."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
FIGS = REPORTS / "figures"
FIGS.mkdir(exist_ok=True)
TAU, K, D_R_FRAC = 0.5, 1.0, 0.10


def h_star(R, I0, k=K, tau=TAU, dR_frac=D_R_FRAC):
    noise2 = (1 + R / k) / (I0 * (R - 1))
    disc = tau ** 2 - noise2
    return np.where(disc > 0, (R / (dR_frac * R)) * np.sqrt(np.maximum(disc, 0)), 0.0)


# Fig 1: horizon vs R
R = np.linspace(1.02, 2.2, 200)
plt.figure(figsize=(7, 4.5))
for I0 in [50, 500, 5000]:
    plt.plot(R, h_star(R, I0), label=f"I0={I0}")
plt.axvline(1 + (1 + 1 / K) / (TAU ** 2 * 50), ls="--", c="gray", lw=0.8)
plt.xlabel("Reproduction number R"); plt.ylabel("Horizon h* (generations, 50% error)")
# plt.title("Fig 1. Predictability horizon vs R (tau=0.5, k=1, dR/R=0.1)")
plt.legend(); plt.tight_layout(); plt.savefig(FIGS / "fig1_horizon.png", dpi=150); plt.close()

# Fig 2: T1 CV verification (recompute quick empirical curve)
import importlib.util
spec = importlib.util.spec_from_file_location("v", ROOT / "scripts" / "sim_verify_t1.py")
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
rng = np.random.default_rng(1)
R_c, k_c, I0_c, nmax = 1.5, 0.3, 100, 12
Z = v.sim_gw(I0_c, R_c, k_c, nmax, 20000)
E = Z.mean(0); Var = Z.var(0)
emp = np.sqrt(Var) / E
theo = np.array([v.cv_formula(n, I0_c, R_c, k_c) for n in range(nmax + 1)])
plt.figure(figsize=(7, 4.5))
plt.plot(range(nmax + 1), theo, "k-", label="theory")
plt.plot(range(nmax + 1), emp, "ro", ms=4, label="simulation")
plt.xlabel("Generation n"); plt.ylabel("CV")
# plt.title("Fig 2. Demographic variance floor: theory vs simulation (R=1.5, k=0.3, I0=100)")
plt.legend(); plt.tight_layout(); plt.savefig(FIGS / "fig2_cv_verify.png", dpi=150); plt.close()

# Fig 3: ML-2 saturation
ml2 = json.loads((REPORTS / "ml2_forecast_vs_bound.json").read_text(encoding="utf-8"))
plt.figure(figsize=(7, 4.5))
for name, style in [("R1.5_k0.3", "o-"), ("R1.3_k1.0", "s-"), ("R1.1_k5.0", "^-")]:
    hh = [int(h) for h in ml2[name]]
    th = [ml2[name][h]["theory_log_sd"] for h in ml2[name]]
    ml = [ml2[name][h]["ml_log_rmse"] for h in ml2[name]]
    plt.plot(hh, ml, style, label=f"{name} ML")
    plt.plot(hh, th, style.replace("-", "--"), alpha=0.6, label=f"{name} bound")
plt.xlabel("Horizon h"); plt.ylabel("log-RMSE")
# plt.title("Fig 3. ML forecaster saturates the theoretical bound")
plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIGS / "fig3_ml2_saturation.png", dpi=150); plt.close()

# Fig 4: real-data horizons + ML error growth
rd = json.loads((REPORTS / "real_data_illustration.json").read_text(encoding="utf-8"))
plt.figure(figsize=(8, 4.5))
labels, vals = [], []
for name in ["covid", "rsv", "flu"]:
    for w in rd[name]["windows"]:
        if w and w.get("predictable"):
            labels.append(f"{name}\n{w['window'][:10]}")
            vals.append(w["horizon_weeks_50pct"])
plt.bar(range(len(vals)), vals)
plt.xticks(range(len(vals)), labels, fontsize=7)
plt.ylabel("h* (weeks, 50% error)")  # plt.title("Fig 4a. Real-data horizons")
plt.tight_layout(); plt.savefig(FIGS / "fig4a_real_horizons.png", dpi=150); plt.close()

plt.figure(figsize=(7, 4.5))
for name, style in [("covid", "o-"), ("rsv", "s-"), ("flu", "^-")]:
    hh = [int(h) for h in rd[name]["ml_vs_h"]]
    ml = [rd[name]["ml_vs_h"][h]["ml_log_rmse"] for h in rd[name]["ml_vs_h"]]
    plt.plot(hh, ml, style, label=f"{name} ML")
plt.xlabel("Horizon h (weeks)"); plt.ylabel("log-RMSE")
# plt.title("Fig 4b. Real-data ML forecast error vs horizon")
plt.legend(); plt.tight_layout(); plt.savefig(FIGS / "fig4b_ml_real.png", dpi=150); plt.close()

print("figures written:", sorted(p.name for p in FIGS.glob("*.png")), flush=True)