"""Generate additional figures for Main Results section."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
FIGS = REPORTS / "figures"
FIGS.mkdir(exist_ok=True)


def fig_t3_quasistationary():
    """Fig: canonical Theorem 3 quasi-stationary densities."""
    with open(REPORTS / "verify_t3.json", encoding="utf-8") as f:
        data = json.load(f)

    x = np.linspace(0.1, 1000, 2000)
    plt.figure(figsize=(7, 4.5))

    for key, result in data["stationary_cv"].items():
        eps = float(key.removeprefix("eps"))
        R = result["R"]
        N = result["N"]
        c1 = 2 * eps / (R + 1)
        c2 = R / (N * (R + 1))
        pi = (1 / x) * np.exp(c1 * x - c2 * x**2)
        pi /= np.trapz(pi, x)  # normalize
        plt.plot(x, pi, label=f"ε={eps:g}, R={R:g}")

    plt.xlabel("Population x")
    plt.ylabel("Quasi-stationary density π(x)")
#     plt.title("Theorem 3: Near-critical quasi-stationary distribution")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGS / "fig_t3_quasistationary.png", dpi=150)
    plt.close()
    print("✓ fig_t3_quasistationary.png")


def fig_t4_fisher_bound():
    """Fig: Theorem 4 Fisher information Cramér-Rao bound vs empirical variance."""
    with open(REPORTS / "verify_t4.json", encoding="utf-8") as f:
        data = json.load(f)

    plt.figure(figsize=(7, 4.5))

    # Extract data
    configs = []
    for key, val in data.items():
        if key.startswith("R"):
            R, k, cum = [
                float(x)
                for x in key.replace("R", "")
                .replace("_k", " ")
                .replace("_cum", " ")
                .split()
            ]
            ratio = val["mle_var_over_bound"]
            configs.append((R, k, cum, ratio, key))

    # Sort by R then k
    configs.sort()

    x_pos = range(len(configs))
    ratios = [c[3] for c in configs]
    labels = [f"R={c[0]:.2f}\nk={c[1]:.1f}" for c in configs]

    colors = ["C0" if r < 1 else "C3" for r in ratios]
    plt.bar(x_pos, ratios, color=colors, alpha=0.7)
    plt.axhline(1.0, color="k", linestyle="--", linewidth=1, label="Cramér-Rao bound")
    plt.xticks(x_pos, labels, fontsize=8)
    plt.ylabel("Empirical Var / CR Bound")
    plt.xlabel("Parameter regime")
#     plt.title("Theorem 4: MLE variance vs Cramér-Rao bound")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGS / "fig_t4_fisher_bound.png", dpi=150)
    plt.close()
    print("✓ fig_t4_fisher_bound.png")


def fig_t5_timevarying():
    """Fig: Theorem 5/5R variance scaling with horizon."""
    with open(REPORTS / "verify_tvR.json", encoding="utf-8") as f:
        tvR = json.load(f)
    with open(REPORTS / "verify_t5R.json", encoding="utf-8") as f:
        t5R = json.load(f)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    # Left: T5 independent innovations
#     ax1.set_title("Theorem 5: Independent innovations")
    for key in sorted(tvR.keys()):
        if key.startswith("h"):
            h = int(key[1:])
            emp = tvR[key]["empirical_log_var"]
            theo = tvR[key]["theory_log_var"]
            ax1.plot(h, emp, "o", color="C0", markersize=6)
            ax1.plot(h, theo, "s", color="C1", markersize=6)

    ax1.plot([], [], "o", color="C0", label="Empirical")
    ax1.plot([], [], "s", color="C1", label="Theory")
    ax1.set_xlabel("Horizon h (generations)")
    ax1.set_ylabel("Var(log Î_h)")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Right: T5R AR(1) persistence
#     ax2.set_title("Theorem 5R: AR(1) persistent growth")
    phi_vals = sorted({v["phi"] for v in t5R.values() if isinstance(v, dict)})

    for phi in phi_vals:
        h_vals, emp_vals, theo_vals = [], [], []
        for _key, val in t5R.items():
            if isinstance(val, dict) and val.get("phi") == phi:
                h = val["h"]
                h_vals.append(h)
                emp_vals.append(val["empirical_var"])
                theo_vals.append(val["theory_var"])

        if h_vals:
            sort_idx = np.argsort(h_vals)
            h_vals = np.array(h_vals)[sort_idx]
            emp_vals = np.array(emp_vals)[sort_idx]
            theo_vals = np.array(theo_vals)[sort_idx]

            ax2.plot(h_vals, emp_vals, "o-", label=f"φ={phi} emp", alpha=0.7)
            ax2.plot(h_vals, theo_vals, "s--", label=f"φ={phi} theo", alpha=0.5)

    ax2.set_xlabel("Horizon h (generations)")
    ax2.set_ylabel("Var(Σ r_j)")
    ax2.legend(fontsize=7, ncol=2)
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGS / "fig_t5_timevarying.png", dpi=150)
    plt.close()
    print("✓ fig_t5_timevarying.png")


def main():
    print("Generating new figures for Main Results...")
    fig_t3_quasistationary()
    fig_t4_fisher_bound()
    fig_t5_timevarying()
    print("\nAll figures generated in:", FIGS)
    print("Files:", sorted(p.name for p in FIGS.glob("fig_t*.png")))


if __name__ == "__main__":
    main()
