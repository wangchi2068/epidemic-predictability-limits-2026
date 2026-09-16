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
    "v1.0": "2023--24 (v1.0.0)",
    "v1.1": "2024--25 (v1.1.0)",
    "v1.2": "2025--26 (v1.2.0)",
}
MODELS = ["ensemble", "baseline", "mechanistic"]
MODEL_LABEL = {
    "ensemble": "Hub 集成",
    "baseline": "官方基线",
    "mechanistic": "机制基准",
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
    for rel in RELS:
        hs = horizons_of(data[rel])
        for m in MODELS:
            ys = [data[rel]["by_horizon"][str(h)]["by_model"][m]["wis"] for h in hs]
            ax.plot(
                hs,
                ys,
                MODEL_STYLE[m],
                color=MODEL_COLOR[m],
                lw=1.5,
                ms=5,
                alpha=0.45 if rel != "v1.2" else 1.0,
                label=MODEL_LABEL[m] if rel == "v1.2" else None,
            )
    ax.set_title(
        "(a) 加权区间评分随提前期\n（粗线为 2025--26，淡线为前两季）", fontsize=9
    )
    ax.set_xlabel("提前期 $h$（周）")
    ax.set_ylabel("WIS（越低越优）")
    ax.set_xticks([1, 2, 3])
    ax.legend(frameon=True, fontsize=8)


def panel_b(ax, data: dict) -> None:
    phases = ["rising", "peak", "declining"]
    ph_label = ["上升期", "达峰期", "下降期"]
    x = np.arange(len(phases))
    w = 0.26
    for i, m in enumerate(MODELS):
        vals = []
        for ph in phases:
            recs = [r for r in data["v1.2"]["by_phase"][ph] if r["model"] == m]
            vals.append(recs[0]["cover95"] if recs else np.nan)
        ax.bar(
            x + (i - 1) * w,
            vals,
            w,
            color=MODEL_COLOR[m],
            alpha=0.85,
            label=MODEL_LABEL[m],
        )
    ax.axhline(0.95, color="#e41a1c", ls=":", lw=1.2, label="标称 95%")
    ax.set_title("(b) 2025--26 各阶段经验 95% 覆盖率\n（$h=1$）", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(ph_label)
    ax.set_ylabel("经验覆盖率")
    ax.set_ylim(0, 1.05)
    ax.legend(frameon=True, fontsize=7.5, loc="lower right")


def panel_c(ax, data: dict) -> None:
    x = np.arange(len(RELS))
    w = 0.34
    base_gap, mech_gap = [], []
    for rel in RELS:
        bm = data[rel]["by_horizon"]["1"]["by_model"]
        base_gap.append(bm["baseline"]["wis"] - bm["ensemble"]["wis"])
        mech_gap.append(bm["mechanistic"]["wis"] - bm["ensemble"]["wis"])
    ax.bar(x - w / 2, base_gap, w, color="#4575b4", alpha=0.9, label="基线 $-$ 集成")
    ax.bar(
        x + w / 2, mech_gap, w, color="#d73027", alpha=0.9, label="机制基准 $-$ 集成"
    )
    ax.set_title("(c) 相对集成的超额 WIS（$h=1$）", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels([REL_LABEL[r] for r in RELS], fontsize=7.5)
    ax.set_ylabel("$\\Delta$WIS（正 = 更差）")
    ax.legend(frameon=True, fontsize=8)


def main() -> None:
    data = {rel: load(rel) for rel in RELS}
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.5), dpi=300)
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
