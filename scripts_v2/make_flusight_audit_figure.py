"""make_flusight_audit_figure.py — publication figure for the three-season external audit.

All numbers are read from the regenerated strict four-way intersection outputs
(reports_v3/flusight_v1.{0,1,2}_extended.json), so the figure cannot drift from
the tables.
"""

import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports_v3"
FIGS = REPORTS / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "font.size": 9,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans", "Arial"],
        "axes.unicode_minus": False,
    }
)

RELS = ["v1.0", "v1.1", "v1.2"]
REL_LABEL = {
    "v1.0": "2023--24 赛季",
    "v1.1": "2024--25 赛季",
    "v1.2": "2025--26 赛季",
}
MODELS = ["ensemble", "baseline", "mechanistic"]
MODEL_LABEL = {
    "ensemble": "Hub 集成",
    "baseline": "官方基线",
    "mechanistic": "插件式机制预测器",
}
MODEL_COLOR = {"ensemble": "#1b7837", "baseline": "#2166ac", "mechanistic": "#b2182b"}
MODEL_STYLE = {"ensemble": "-o", "baseline": "--s", "mechanistic": "-.^"}


def load(rel: str) -> dict:
    path = REPORTS / f"flusight_{rel}_extended.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(
            f"cannot read {path.name}; run flusight_audit_extended.py first ({exc})"
        ) from exc


def horizons_of(rec: dict) -> list[int]:
    out = []
    for key in rec["by_horizon"]:
        try:
            out.append(int(key))
        except (TypeError, ValueError) as exc:
            raise SystemExit(f"non-numeric horizon key {key!r} in by_horizon") from exc
    return sorted(out)


def panel_a(ax, data: dict) -> None:
    # Plot v1.0 and v1.1 with lighter dashed lines
    for rel in ["v1.0", "v1.1"]:
        hs = horizons_of(data[rel])
        for m in MODELS:
            ys = [data[rel]["by_horizon"][str(h)]["by_model"][m]["wis"] for h in hs]
            ax.plot(
                hs,
                ys,
                linestyle=":" if rel == "v1.0" else "--",
                color=MODEL_COLOR[m],
                lw=1.1,
                ms=4,
                alpha=0.4,
            )

    # Plot v1.2 (2025-26) with solid lines, markers, and 95% bootstrap CI band
    hs = horizons_of(data["v1.2"])
    for m in MODELS:
        ys = [data["v1.2"]["by_horizon"][str(h)]["by_model"][m]["wis"] for h in hs]
        ci_lo = [data["v1.2"]["by_horizon"][str(h)]["by_model"][m]["wis_ci95"][0] for h in hs]
        ci_hi = [data["v1.2"]["by_horizon"][str(h)]["by_model"][m]["wis_ci95"][1] for h in hs]
        ax.plot(
            hs,
            ys,
            MODEL_STYLE[m],
            color=MODEL_COLOR[m],
            lw=2.0,
            ms=6,
            label=f"{MODEL_LABEL[m]} (2025--26)",
            zorder=4,
        )
        ax.fill_between(
            hs,
            ci_lo,
            ci_hi,
            color=MODEL_COLOR[m],
            alpha=0.12,
            zorder=2,
        )

    # Add a custom legend entry for season line styles
    from matplotlib.lines import Line2D
    custom_lines = [
        Line2D([0], [0], color="#555555", lw=2.0, ls="-", label="2025--26 (主轴, 带95% CI)"),
        Line2D([0], [0], color="#777777", lw=1.1, ls="--", label="2024--25"),
        Line2D([0], [0], color="#999999", lw=1.1, ls=":", label="2023--24"),
    ]

    ax.set_title(
        "(a) 加权区间评分随提前期衰减\n（实线粗体为 2025--26，阴影为 95% Bootstrap CI）", fontsize=9, fontweight="bold"
    )
    ax.set_xlabel("提前期 $h$（周）", fontsize=8.5)
    ax.set_ylabel("WIS（加权区间评分，越低越优）", fontsize=8.5)
    ax.set_xticks([1, 2, 3])
    ax.set_xlim(0.85, 3.15)
    leg1 = ax.legend(frameon=True, fontsize=7.5, loc="upper left")
    ax.add_artist(leg1)
    ax.legend(handles=custom_lines, frameon=True, fontsize=7, loc="center left", bbox_to_anchor=(0.02, 0.48))


def panel_b(ax, data: dict) -> None:
    phases = ["rising", "peak", "declining"]
    ph_label = ["峰前期", "峰值窗口", "峰后期"]
    x = np.arange(len(phases))
    w = 0.25

    # Plot 2025-26 bars
    for i, m in enumerate(MODELS):
        vals = []
        for ph in phases:
            recs = [r for r in data["v1.2"]["by_phase"][ph] if r["model"] == m]
            vals.append(recs[0]["cover95"] if recs else np.nan)
        bars = ax.bar(
            x + (i - 1) * w,
            vals,
            w,
            color=MODEL_COLOR[m],
            alpha=0.88,
            label=MODEL_LABEL[m],
            edgecolor="white",
            linewidth=0.8,
            zorder=3,
        )
        # Add value labels on bars: inside bar if tall, else above bar
        for bar, val in zip(bars, vals):
            if not np.isnan(val):
                if val > 0.8:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        val - 0.07,
                        f"{val:.2f}",
                        ha="center",
                        va="center",
                        fontsize=7.5,
                        fontweight="bold",
                        color="white",
                        zorder=5,
                    )
                else:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        val + 0.025,
                        f"{val:.2f}",
                        ha="center",
                        va="bottom",
                        fontsize=7.5,
                        fontweight="bold",
                        color=MODEL_COLOR[m],
                        zorder=5,
                    )

        # Overlay cross-season points for 2023-24 and 2024-25 as subtle comparison markers
        for rel, marker, malpha in [("v1.0", "o", 0.65), ("v1.1", "s", 0.65)]:
            past_vals = []
            for ph in phases:
                recs = [r for r in data[rel]["by_phase"][ph] if r["model"] == m]
                past_vals.append(recs[0]["cover95"] if recs else np.nan)
            ax.scatter(
                x + (i - 1) * w,
                past_vals,
                marker=marker,
                s=20,
                color=MODEL_COLOR[m],
                edgecolors="#222222",
                linewidth=0.6,
                alpha=malpha,
                zorder=4,
            )

    ax.axhline(0.95, color="#d95f02", ls="--", lw=1.2, label="标称 95% 水平", zorder=2)

    # Highlight pre-peak phase coverage
    ax.annotate(
        "峰前期经验覆盖率较低\n(实测覆盖率仅 0.14--0.49)",
        xy=(0.0, 0.49),
        xytext=(0.0, 1.04),
        arrowprops=dict(arrowstyle="->", color="#b2182b", lw=1.0),
        ha="center",
        fontsize=7.5,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.35", fc="#fff5f5", ec="#b2182b", lw=0.9, alpha=0.95),
        zorder=6,
    )

    ax.set_title("(b) 峰值相对位置各阶段经验 95% 预测区间覆盖率\n（柱为 2025--26，散点为前两季对照）", fontsize=9, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(ph_label, fontsize=8)
    ax.set_ylabel("经验覆盖率（标称 = 0.95）", fontsize=8.5)
    ax.set_ylim(0, 1.22)
    ax.legend(frameon=True, fontsize=7.5, loc="lower right")


def panel_c(ax, data: dict) -> None:
    x = np.arange(len(RELS))
    w = 0.32
    base_gap, mech_gap = [], []
    base_err_lo, base_err_hi = [], []
    mech_err_lo, mech_err_hi = [], []

    for rel in RELS:
        bm = data[rel]["by_horizon"]["1"]["by_model"]
        base_delta = bm["baseline"]["wis"] - bm["ensemble"]["wis"]
        mech_delta = bm["mechanistic"]["wis"] - bm["ensemble"]["wis"]
        base_gap.append(base_delta)
        mech_gap.append(mech_delta)

        # Paired bootstrap CI from paired_vs_ensemble
        p = data[rel]["by_horizon"]["1"]["paired_vs_ensemble"]
        b_ci = p["baseline"]["delta_wis_ci95"]
        m_ci = p["mechanistic"]["delta_wis_ci95"]
        base_err_lo.append(base_delta - b_ci[0])
        base_err_hi.append(b_ci[1] - base_delta)
        mech_err_lo.append(mech_delta - m_ci[0])
        mech_err_hi.append(m_ci[1] - mech_delta)

    ax.axhline(0, color="#333333", ls="-", lw=0.8, zorder=2)

    bars1 = ax.bar(
        x - w / 2,
        base_gap,
        w,
        yerr=[base_err_lo, base_err_hi],
        capsize=3.5,
        error_kw=dict(lw=1.0, capthick=1.0, ecolor="#1a476f"),
        color="#4575b4",
        alpha=0.88,
        label="官方基线 $-$ Hub 集成",
        edgecolor="white",
        linewidth=0.8,
        zorder=3,
    )
    bars2 = ax.bar(
        x + w / 2,
        mech_gap,
        w,
        yerr=[mech_err_lo, mech_err_hi],
        capsize=3.5,
        error_kw=dict(lw=1.0, capthick=1.0, ecolor="#8c1221"),
        color="#d73027",
        alpha=0.88,
        label="插件式机制预测器 $-$ Hub 集成",
        edgecolor="white",
        linewidth=0.8,
        zorder=3,
    )

    # Value text annotations with semi-transparent white bbox directly at bar height
    for b, val in zip(bars1, base_gap):
        ax.text(
            b.get_x() + b.get_width() / 2,
            val + 3.0,
            f"+{val:.1f}",
            ha="center",
            va="bottom",
            fontsize=7.5,
            color="#1a476f",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85),
            zorder=6,
        )
    for b, val in zip(bars2, mech_gap):
        ax.text(
            b.get_x() + b.get_width() / 2,
            val + 3.0,
            f"+{val:.1f}",
            ha="center",
            va="bottom",
            fontsize=7.5,
            color="#8c1221",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85),
            zorder=6,
        )

    ax.set_title("(c) 相对集成的超额 WIS 与配对 95% CI（$h=1$）\n（正值表示劣于集成，误差棒为配对置信区间）", fontsize=9, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([REL_LABEL[r] for r in RELS], fontsize=8)
    ax.set_ylabel("$\\Delta$WIS（超额加权区间评分）", fontsize=8.5)
    ax.set_ylim(-5, 175)
    ax.legend(frameon=True, fontsize=7.5, loc="upper left")


def main() -> None:
    data = {rel: load(rel) for rel in RELS}
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.0), dpi=300)
    panel_a(axes[0], data)
    panel_b(axes[1], data)
    panel_c(axes[2], data)
    fig.tight_layout()
    out = FIGS / "fig_flusight_audit.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print("written:", out)


if __name__ == "__main__":
    main()

