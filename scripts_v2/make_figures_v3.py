# -*- coding: utf-8 -*-
"""make_figures_v3.py — figures for the rebuilt empirical section."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports_v3"
FIGS = ROOT / "reports_v3" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3})

PHASE_ORDER = ["Delta", "Omicron", "JN1", "flu22", "flu24", "rsv24", "rsv25"]
PHASE_LABEL = {"Delta": "Delta", "Omicron": "Omicron", "JN1": "JN.1",
               "flu22": "Flu 22--23", "flu24": "Flu 24--25",
               "rsv24": "RSV 24--25", "rsv25": "RSV 25--26"}


def fig_state_horizons(phases):
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    data, nat = [], []
    for k in PHASE_ORDER:
        rec = phases[k]
        hs = [v["h_week"] for v in rec["states"].values() if v.get("h_week")]
        data.append(hs)
        nat.append(rec["national"]["h_week"] if rec["national"] else np.nan)
    bp = ax.boxplot(data, tick_labels=[PHASE_LABEL[k] for k in PHASE_ORDER],
                    widths=0.55, showfliers=False, patch_artist=True,
                    medianprops=dict(color="black"))
    for p in bp["boxes"]:
        p.set_facecolor("#cfe3f5")
    ax.plot(range(1, len(nat) + 1), nat, "D", color="#b2182b",
            label="National aggregate", zorder=5)
    ax.axhspan(16, 20, color="grey", alpha=0.12)
    ax.text(0.6, 18, "single-season span", color="grey", fontsize=8, va="center")
    ax.set_ylabel(r"$h^*$ (weeks, exact root, $\tau=0.5$)")
    ax.set_yscale("log")
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_state_horizons.png", dpi=300)
    plt.close(fig)


def fig_micro(micro):
    fig, axes = plt.subplots(1, 3, figsize=(8.4, 2.8), sharey=False)
    series = [("Hong_Kong_COVID19_Local", "HK COVID-19 (local)", "#2166ac"),
              ("Hong_Kong_COVID19_All", "HK COVID-19 (all)", "#67a9cf"),
              ("Guinea_Ebola_2014", "Guinea Ebola 2014", "#b2182b")]
    for ax, (key, label, color) in zip(axes, series):
        rec = micro[key]
        # reconstruct offspring counts from the stored moments is not possible;
        # plot the fitted NB pmf over the observed mean/k with the empirical CV^2 marked
        R, k = rec["R_mle"], rec["k_mle"]
        xs = np.arange(0, 18)
        from scipy.stats import nbinom
        p = k / (k + R)
        pmf = nbinom.pmf(xs, k, p)
        ax.bar(xs, pmf, color=color, alpha=0.75, label="NB fit")
        ax.axhline(0, color="black", lw=0.5)
        ax.set_title(f"{label}\n$\\hat R$={R:.2f}, $\\hat k$={k:.2f}, "
                     f"$\\Delta$AIC={rec['delta_aic_poisson_vs_nb']:.0f}", fontsize=8)
        ax.set_xlabel("secondary cases")
        if ax is axes[0]:
            ax.set_ylabel("probability")
    fig.tight_layout()
    fig.savefig(FIGS / "fig_micro.png", dpi=300)
    plt.close(fig)


def fig_hub(hub):
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    for wave, color in [("Delta", "#2166ac"), ("Omicron", "#b2182b")]:
        recs = [r for r in hub if r["wave"] == wave]
        hs = sorted({h["h_weeks"] for r in recs for h in r["horizons"]})
        med = [np.median([h["median_relMSE"] for r in recs
                          for h in r["horizons"] if h["h_weeks"] == x])
               for x in hs]
        ax.plot(hs, med, "-o", color=color, label=f"{wave} (median across origins)")
    ax.axhline(1.0, color="black", ls="--", lw=0.9)
    ax.text(0.05, 1.05, "parity with persistence", fontsize=8, color="grey")
    ax.set_xlabel("forecast horizon (weeks)")
    ax.set_ylabel("median state-level relMSE")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_hub_skill.png", dpi=300)
    plt.close(fig)


def main():
    phases = json.loads((REPORTS / "state_phases.json").read_text(encoding="utf-8"))
    micro = json.loads((ROOT / "data" / "micro" /
                        "micro_branching_fit_results.json").read_text(encoding="utf-8"))
    hub = json.loads((ROOT / "data" / "hub" /
                      "forecast_hub_operational_evaluation.json").read_text(encoding="utf-8"))
    fig_state_horizons(phases)
    fig_micro(micro)
    fig_hub(hub)
    print("figures written to", FIGS)


if __name__ == "__main__":
    main()
