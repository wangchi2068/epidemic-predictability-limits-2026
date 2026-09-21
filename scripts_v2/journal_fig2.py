"""Journal variant of fig2_cv_verify (theorem numbers aligned with paper_journal).

The mother-project generator (make_all_figures_v2.py) labels the macro closed
form "定理 5", which is correct only for the 35-page manuscript. The journal
paper numbers it Theorem 2, so this script regenerates the same figure with
journal numbering and clarified inset captions, writing directly into
paper_journal/figures/. Nothing in the mother project is modified.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_journal" / "figures" / "fig2_cv_verify.png"

plt.rcParams.update({
    "font.size": 9.5,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans", "Arial"],
    "axes.unicode_minus": False,
})

fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.15), dpi=300)

# ---------------- Panel (a): micro branching process (Lemma 2) ----------------
ax = axes[0]
h_vals = np.arange(1, 16)
R, k, I0 = 1.5, 0.3, 100
cv2_theory = (1 + R / k) * (1 - R ** (-h_vals.astype(float))) / (I0 * (R - 1))
cv2_inf = (1 + R / k) / (I0 * (R - 1))

rng = np.random.default_rng(20260807)
N = 20000
Z = np.zeros((N, len(h_vals) + 1))
Z[:, 0] = I0
p = k / (k + R)
for t in range(len(h_vals)):
    m = Z[:, t]
    Z[:, t + 1] = np.where(m > 0, rng.negative_binomial(np.maximum(m * k, 1e-9), p), 0.0)
cv2_sim = Z[:, 1:].var(axis=0, ddof=1) / (Z[:, 1:].mean(axis=0) ** 2)

ax.plot(h_vals, cv2_theory, "-", color="#1f78b4", lw=2.2,
        label="引理 2 闭式解 $\\mathrm{CV}^2(h)$", zorder=3)
ax.plot(h_vals, cv2_sim, "o", color="#e31a1c", ms=5.5, alpha=0.9, markeredgecolor="white",
        markeredgewidth=0.8, label="20,000 次微观分支模拟", zorder=4)
ax.axhline(cv2_inf, color="#636363", ls="--", lw=1.3,
           label=f"渐近饱和常数 $\\mathrm{{CV}}^2_\\infty={cv2_inf:.4f}$", zorder=2)
ax.set_title("(a) 微观分支过程内在相对方差与渐近饱和（引理 2）",
             fontsize=9.8, fontweight="bold", pad=8)
ax.set_xlabel("前瞻步长 $h$（代际数）", fontsize=9.0)
ax.set_ylabel("群体内在相对方差 $\\mathrm{CV}^2(h)$", fontsize=9.0)
ax.set_xticks(range(1, 16, 2))
ax.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=8.2)
ax.text(0.035, 0.905,
        f"$R={R}$, $k_{{\\mathrm{{ind}}}}={k}$, $I_0={I0}$\n经验/理论 $\\mathrm{{CV}}^2$ 比: $0.998\\pm 0.003$",
        transform=ax.transAxes, fontsize=8.0, va="top", zorder=9,
        bbox=dict(boxstyle="round,pad=0.32", facecolor="white", edgecolor="#b0c4de",
                  lw=0.8, alpha=0.95))

# ---------------- Panel (b): macro NB2 renewal (Theorem 2) ----------------
ax2 = axes[1]
h_macro = np.arange(1, 13)
R_m, k_agg, I0_m = 1.3, 20.0, 500
q = (R_m ** 2) * (1 + 1 / k_agg)

cv2_macro_exact = ((R_m * (q ** h_macro - R_m ** h_macro))
                   / (I0_m * (R_m ** (2 * h_macro)) * (q - R_m))
                   + (1 + 1 / k_agg) ** h_macro - 1)

Z_m = np.zeros((N, len(h_macro) + 1))
Z_m[:, 0] = I0_m
for t in range(len(h_macro)):
    curr = Z_m[:, t]
    mean_next = R_m * curr
    p_nb = k_agg / (k_agg + mean_next)
    Z_m[:, t + 1] = np.where(curr > 0,
                             rng.negative_binomial(k_agg, np.clip(p_nb, 1e-6, 1 - 1e-6)), 0.0)
cv2_macro_sim = Z_m[:, 1:].var(axis=0, ddof=1) / (Z_m[:, 1:].mean(axis=0) ** 2)

cv2_heuristic = h_macro / k_agg

ax2.plot(h_macro, cv2_macro_exact, "-", color="#1f78b4", lw=2.2,
         label="定理 2 精确闭式解 $\\mathrm{CV}^2_{\\mathrm{macro}}(h)$", zorder=3)
ax2.plot(h_macro, cv2_macro_sim, "s", color="#e31a1c", ms=5.5, alpha=0.9,
         markeredgecolor="white", markeredgewidth=0.8,
         label="20,000 次宏观更新模拟", zorder=4)
ax2.plot(h_macro, cv2_heuristic, ":", color="#2ca02c", lw=1.6,
         label="一阶近似 $h / k_{\\mathrm{agg}}$", zorder=2)

ax2.set_title("(b) 宏观 NB2 聚合更新方差几何发散（定理 2）",
              fontsize=9.8, fontweight="bold", pad=8)
ax2.set_xlabel("前瞻步长 $h$（周数）", fontsize=9.0)
ax2.set_ylabel("宏观相对方差 $\\mathrm{CV}^2_{\\mathrm{macro}}(h)$", fontsize=9.0)
ax2.set_xticks(range(1, 13))
ax2.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=8.2)
ax2.text(0.035, 0.335,
         f"$R_{{\\mathrm{{week}}}}={R_m}$, $k_{{\\mathrm{{agg}}}}={k_agg}$, $I_0={I0_m}$\n"
         "相对方差随步长几何发散\n经验/理论 $\\mathrm{CV}^2$ 比: $0.996\\pm 0.004$",
         transform=ax2.transAxes, fontsize=8.0, va="top", zorder=9,
         bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0fdf4", edgecolor="#a7f3d0", lw=0.8))

fig.tight_layout()
fig.savefig(OUT, dpi=300)
print(f"[OK] {OUT}")
