# -*- coding: utf-8 -*-
"""make_figures_v3.py — Publication-grade figures for the rebuilt empirical section.

Generates:
1. fig_micro.png: Micro-layer offspring distributions with Negative Binomial vs Poisson overlay
   and Cramér-Rao lower bound efficiency verification.
2. fig_state_horizons.png: Dual-panel state-level macro mechanistic horizons with jittered state
   points, pathogen grouping, national aggregates, and process variance dominance.
3. fig_hub_skill.png: Dual-panel COVIDhub-ensemble forecast evaluation showing SERatio decay
   with interquartile bands and absolute WIS expansion across lead times.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import macro_model
import pandas as pd
from scipy.stats import nbinom, poisson

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports_v3"
FIGS = ROOT / "reports_v3" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.size": 9.5,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans", "Arial"],
    "axes.unicode_minus": False
})

PHASE_ORDER = ["Delta", "Omicron", "JN1", "flu22", "flu24", "rsv24", "rsv25"]
PHASE_LABEL = {
    "Delta": "Delta", "Omicron": "Omicron", "JN1": "JN.1",
    "flu22": "流感 22-23", "flu24": "流感 24-25",
    "rsv24": "RSV 24-25", "rsv25": "RSV 25-26"
}
PATHOGEN_COLOR = {
    "Delta": "#1f78b4", "Omicron": "#1f78b4", "JN1": "#1f78b4",
    "flu22": "#ff7f00", "flu24": "#ff7f00",
    "rsv24": "#33a02c", "rsv25": "#33a02c"
}


def fig_micro(micro: dict):
    fig, axes = plt.subplots(1, 3, figsize=(8.6, 2.75), dpi=300)
    
    # Load empirical raw data
    sec = pd.read_csv(ROOT / "data" / "micro" / "hong_kong_adam2020" /
                      "secondary_cases.csv")["secondary.cases"].values
    hk_local = np.concatenate([sec, np.zeros(256)])
    hk_all = np.concatenate([sec, np.zeros(1038 - 99)])
    eb = pd.read_csv(ROOT / "data" / "micro" / "guinea_ebola_faye2015" /
                     "ebola_conakry_offspring.csv")["secondary_cases"].values
    
    datasets = {
        "Hong_Kong_COVID19_Local": ("香港 COVID-19（本地）", hk_local),
        "Hong_Kong_COVID19_All": ("香港 COVID-19（全体）", hk_all),
        "Guinea_Ebola_2014": ("几内亚埃博拉 2014", eb)
    }
    
    xs = np.arange(0, 16)
    
    for ax, (key, (label, raw_x)) in zip(axes, datasets.items()):
        rec = micro[key]
        R, k = rec["R_mle"], rec["k_mle"]
        crb_ratio = rec["bootstrap"]["ratio_var_to_crb"]
        daic = rec["delta_aic_poisson_vs_nb"]
        
        # Empirical PMF
        counts = np.bincount(raw_x.astype(int))
        emp_pmf = np.zeros(len(xs))
        for v in range(min(len(counts), len(xs))):
            emp_pmf[v] = counts[v] / len(raw_x)
            
        p_nb = k / (k + R)
        pmf_nb = nbinom.pmf(xs, k, p_nb)
        pmf_poi = poisson.pmf(xs, R)
        
        # 1. Empirical observed frequencies as bars
        ax.bar(xs, emp_pmf, width=0.60, color="#3b6998", alpha=0.72,
               edgecolor="#1d3d60", linewidth=0.8, label="实测经验频率", zorder=2)
        # 2. Negative Binomial MLE fit as dark solid curve with dots
        ax.plot(xs, pmf_nb, "-o", color="#0f172a", ms=4.2, lw=1.8,
                label="负二项拟合 (NB)", zorder=4)
        # 3. Poisson comparison as distinct red dashed line with square markers
        ax.plot(xs, pmf_poi, "--s", color="#dc2626", ms=3.8, lw=1.5,
                label="Poisson 对照", zorder=3)
        
        ax.axhline(0, color="black", lw=0.6)
        ax.set_title(f"{label}", fontsize=9.8, fontweight="bold", pad=8)
        ax.set_xlabel("二代病例数 (Offspring Count)", fontsize=8.8)
        if ax is axes[0]:
            ax.set_ylabel("概率质量 (PMF)", fontsize=8.8)
        
        ax.set_xticks(range(0, 16, 2))
        ax.set_xlim(-0.7, 15.7)
        ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=7.8)
        
        # Statistics Box with publication-grade font >= 8.2pt
        info_text = (
            f"$\\hat{{R}} = {R:.2f}$\n"
            f"$\\hat{{k}}_{{\\mathrm{{ind}}}} = {k:.3f}$\n"
            f"$\\Delta\\mathrm{{AIC}} = {daic:.1f}$\n"
            f"$\\mathrm{{Var}}_{{\\mathrm{{boot}}}} / \\mathrm{{CRB}} = {crb_ratio:.3f}$"
        )
        ax.text(0.44, 0.62, info_text, transform=ax.transAxes, fontsize=8.2, va="top",
                bbox=dict(boxstyle="round,pad=0.35", facecolor="#f8fafc", edgecolor="#cbd5e1", lw=0.8))
        
    fig.tight_layout()
    fig.savefig(FIGS / "fig_micro.png", dpi=300)
    plt.close(fig)
    print("[OK] fig_micro.png upgraded to publication-grade with empirical bars")


def fig_state_horizons(phases: dict):
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.03), dpi=300)
    
    # ------------------ Panel (a): State-level Horizon Distribution & National Aggregate
    ax = axes[0]
    data, nat, labels = [], [], []
    rng = np.random.default_rng(20260914)
    
    for idx, k in enumerate(PHASE_ORDER):
        rec = phases[k]
        hs = [v["h_week"] for v in rec["states"].values() if v.get("h_week")]
        data.append(hs)
        nat_val = rec["national"]["h_week"] if rec["national"] else np.nan
        nat.append(nat_val)
        labels.append(PHASE_LABEL[k])
        
        # Plot individual jittered state points
        x_jitter = rng.normal(idx + 1, 0.08, size=len(hs))
        ax.scatter(x_jitter, hs, color=PATHOGEN_COLOR[k], alpha=0.55, s=20,
                   edgecolors="none", zorder=3)
    
    bp = ax.boxplot(data, widths=0.52, showfliers=False,
                    patch_artist=True, medianprops=dict(color="#0f172a", lw=1.8), zorder=4)
    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels, rotation=22, ha="right", fontsize=7.0)
    for p in bp["boxes"]:
        p.set_facecolor("#e2e8f0")
        p.set_alpha(0.65)
        p.set_edgecolor("#475569")
        p.set_linewidth(1.1)
    
    # National Aggregate Diamond Markers
    ax.plot(range(1, len(nat) + 1), nat, "D", color="#b91c1c", ms=7.5,
            markeredgecolor="white", markeredgewidth=1.0, label="国家级聚合视界", zorder=6)
    
    # Single-season natural span band (16--20 weeks)
    ax.axhspan(16, 20, color="#64748b", alpha=0.15, zorder=1)
    ax.text(0.55, 18.0, "单流行季跨度 (16--20 周)", color="#475569", fontsize=8.0, va="center")
    
    ax.set_title("(a) 各阶段宏观机制视界的州级分布与国家级聚合对比", fontsize=9.8, fontweight="bold", pad=8)
    ax.set_ylabel(r"宏观机制视界 $h^*$（周，精确数值根，$\tau=0.5$）", fontsize=8.8)
    ax.set_yscale("log")
    ax.set_ylim(0.8, 80)
    ax.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=8.2)
    
    # ------------------ Panel (b): Dominance of Macro Process Variance
    ax2 = axes[1]
    # Macro process variance share at horizon: CV^2_macro / tau^2
    tau = 0.5
    tau2 = tau ** 2
    cv2_shares = []
    cv2_medians = []
    for k in PHASE_ORDER:
        rec = phases[k]
        # exact macro process variance share at the working point h*,
        # computed from the Theorem 2 closed form (not the h/k_agg heuristic)
        shares = []
        for v in rec["states"].values():
            h_w = v.get("h_week")
            k_a = v.get("k")
            r_w = v.get("R_week")
            i_0 = v.get("I0")
            if None in (h_w, k_a, r_w, i_0):
                continue
            # exact macro process variance share at the working point h*,
            # computed from the Theorem 2 closed form (not the h/k_agg heuristic)
            shares.append(macro_model.cv2_macro(h_w, r_w, k_a, i_0) / tau2)
        cv2_shares.append(shares if shares else [np.nan])
        cv2_medians.append(float(np.nanmedian(shares)) if shares else float("nan"))

    bp2 = ax2.boxplot(cv2_shares, widths=0.52, showfliers=False,
                      patch_artist=True, medianprops=dict(color="#0f172a", lw=1.8), zorder=4)
    ax2.set_xticks(range(1, len(labels) + 1))
    ax2.set_xticklabels(labels, rotation=22, ha="right", fontsize=7.0)
    for idx, p in enumerate(bp2["boxes"]):
        k = PHASE_ORDER[idx]
        p.set_facecolor(PATHOGEN_COLOR[k])
        p.set_alpha(0.35)
        p.set_edgecolor(PATHOGEN_COLOR[k])
        p.set_linewidth(1.1)

    # Band over the cross-state median range, computed from the data itself
    # (never hardcoded: the figure must stay consistent with the text).
    lo, hi = float(np.nanmin(cv2_medians)), float(np.nanmax(cv2_medians))
    ax2.axhline(1.0, color="#b91c1c", ls="--", lw=1.2, label=r"临界方差总预算 $\tau^2$", zorder=2)
    ax2.axhspan(lo, hi, color="#94a3b8", alpha=0.20,
                label=f"跨州中位数区间 ({lo*100:.0f}%--{hi*100:.0f}%)", zorder=1)
    print(f"[OK] panel (b) median share range {lo:.4f}--{hi:.4f}")

    ax2.set_title("(b) 宏观过程内在方差占视界工作点预算之比重", fontsize=9.8, fontweight="bold", pad=8)
    ax2.set_ylabel(r"过程方差占比 $\mathrm{CV}^2_{\mathrm{macro}}(h^*) / \tau^2$", fontsize=8.8)
    ax2.set_ylim(0.4, 1.05)
    ax2.legend(loc="lower left", frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=8.0)
    
    fig.tight_layout()
    fig.savefig(FIGS / "fig_state_horizons.png", dpi=300)
    plt.close(fig)
    print("[OK] fig_state_horizons.png upgraded to publication-grade")


def fig_hub(hub: list):
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 2.95), dpi=300)
    
    # ------------------ Panel (a): SERatio relative to persistence baseline
    ax = axes[0]
    waves = [("Delta", "#1f78b4", "o"), ("Omicron", "#b91c1c", "s")]
    
    for wave, color, marker in waves:
        recs = [r for r in hub if r["wave"] == wave]
        hs = sorted({h["h_weeks"] for r in recs for h in r["horizons"]})
        
        meds = []
        q25s = []
        q75s = []
        for x in hs:
            vals = [h["median_relMSE"] for r in recs for h in r["horizons"] if h["h_weeks"] == x]
            meds.append(np.median(vals))
            q25s.append(np.percentile(vals, 25))
            q75s.append(np.percentile(vals, 75))
            
        ax.plot(hs, meds, f"-{marker}", color=color, lw=2.0, ms=6.0,
                markeredgecolor="white", markeredgewidth=0.8,
                label=f"{wave} 波（跨 6 个原点中位数）", zorder=4)
        ax.fill_between(hs, q25s, q75s, color=color, alpha=0.18, zorder=2)
        
    ax.axhline(1.0, color="#334155", ls="--", lw=1.3, label="持续性基线平价线 (SERatio = 1)", zorder=3)
    ax.axhspan(1.0, 4.5, color="#fecaca", alpha=0.25, zorder=1)
    ax.text(1.05, 3.8, "无技能优势区 (丧失超额预测价值)", color="#991b1b", fontsize=8.0, va="center")
    
    ax.set_title("(a) COVIDhub-ensemble 相对持续性基线的误差比", fontsize=9.8, fontweight="bold", pad=8)
    ax.set_xlabel("前瞻步长 $h$（周）", fontsize=8.8)
    ax.set_ylabel("州级中位 MSE 比率 (SERatio)", fontsize=8.8)
    ax.set_xticks([1, 2, 3, 4])
    ax.set_ylim(0.4, 4.5)
    ax.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=8.0)
    
    # ------------------ Panel (b): Absolute WIS lead-time expansion
    ax2 = axes[1]
    for wave, color, marker in waves:
        recs = [r for r in hub if r["wave"] == wave]
        hs = sorted({h["h_weeks"] for r in recs for h in r["horizons"]})
        
        wis_med = []
        wis_q25 = []
        wis_q75 = []
        for x in hs:
            vals = [h["median_WIS"] for r in recs for h in r["horizons"] if h["h_weeks"] == x and "median_WIS" in h]
            if vals:
                wis_med.append(np.median(vals))
                wis_q25.append(np.percentile(vals, 25))
                wis_q75.append(np.percentile(vals, 75))
            else:
                wis_med.append(np.nan)
                wis_q25.append(np.nan)
                wis_q75.append(np.nan)
                
        ax2.plot(hs, wis_med, f"-{marker}", color=color, lw=2.0, ms=6.0,
                 markeredgecolor="white", markeredgewidth=0.8,
                 label=f"{wave} 波（中位 WIS）", zorder=4)
        ax2.fill_between(hs, wis_q25, wis_q75, color=color, alpha=0.18, zorder=2)
        
    ax2.set_title("(b) 加权区间评分 (WIS) 随提前期的绝对发散", fontsize=9.8, fontweight="bold", pad=8)
    ax2.set_xlabel("前瞻步长 $h$（周）", fontsize=8.8)
    ax2.set_ylabel("加权区间评分 (WIS，越低越优)", fontsize=8.8)
    ax2.set_xticks([1, 2, 3, 4])
    ax2.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=8.0)
    
    fig.tight_layout()
    fig.savefig(FIGS / "fig_hub_skill.png", dpi=300)
    plt.close(fig)
    print("[OK] fig_hub_skill.png upgraded to publication-grade")


def main():
    phases = json.loads((REPORTS / "state_phases.json").read_text(encoding="utf-8"))
    micro = json.loads((ROOT / "data" / "micro" /
                        "micro_branching_fit_results.json").read_text(encoding="utf-8"))
    hub = json.loads((ROOT / "data" / "hub" /
                      "forecast_hub_operational_evaluation.json").read_text(encoding="utf-8"))
    fig_state_horizons(phases)
    fig_micro(micro)
    fig_hub(hub)
    print("All figures in reports_v3/figures/ regenerated successfully.")


if __name__ == "__main__":
    main()
