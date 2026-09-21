"""Numerical verification for the journal paper (Section 3).

Three checks, all with fixed seeds:
  (1) algebraic identity: step recursion vs closed form (Theorem 2);
  (2) Monte Carlo consistency on the feasible domain (theoretical CV^2 <= 20),
      plus convergence probes on high-CV^2 cells (honest precision limits);
  (3) lognormal amplification law (Lemma 3);
  (4) conditional-orthogonality cross-term magnitude (Assumption 1).

Run:  python scripts_v2/verify_journal_claims.py
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq

SEED = 20260921


def cv2_macro(h, R, k, I0):
    q = R * R * (1 + 1 / k)
    return (R / I0) * (q ** h - R ** h) / (R ** (2 * h) * (q - R)) + (1 + 1 / k) ** h - 1


def p_exact(h, s):
    x = h * h * s * s
    return float(np.exp(2 * x) - 2 * np.exp(0.5 * x) + 1)


def check_identity(n_draws=10000, seed=SEED):
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(n_draws):
        R = 10 ** rng.uniform(np.log10(0.5), np.log10(3.0))
        k = 10 ** rng.uniform(np.log10(0.1), np.log10(50))
        I0 = 10 ** rng.uniform(1, 3)
        h = int(rng.integers(1, 13))
        q = R * R * (1 + 1 / k)
        V = 0.0
        for t in range(h):
            V = q * V + I0 * R ** (t + 1) + I0 ** 2 * R ** (2 * t + 2) / k
        Vc = I0 * R * (q ** h - R ** h) / (q - R) + I0 ** 2 * (q ** h - R ** (2 * h))
        worst = max(worst, abs(V - Vc) / max(abs(V), 1e-300))
    print(f"(1) 递推 vs 闭式, {n_draws} 组随机参数: 最大相对偏差 = {worst:.2e}")
    return worst


def simulate_paths(R, k, I0, h, n, rng):
    Z = np.full(n, float(I0))
    for _ in range(h):
        lam = rng.gamma(shape=k, scale=R * Z / k)
        Z = rng.poisson(lam).astype(float)
    return Z


def check_mc(seed=SEED):
    rng = np.random.default_rng(seed)
    cells = []
    for R in [0.8, 1.05, 1.5, 2.0, 3.0]:
        for k in [0.3, 0.5, 1.0, 2.0, 5.0, 10.0]:
            for I0 in [10, 100, 1000]:
                for h in [1, 2, 4]:
                    th = cv2_macro(h, R, k, I0)
                    if 1e-4 < th <= 20:
                        cells.append((R, k, I0, h, th))
    devs = []
    for (R, k, I0, h, th) in cells:
        Z = simulate_paths(R, k, I0, h, 200000, rng)
        if Z.mean() < 0.5:
            continue
        devs.append(abs(Z.var() / Z.mean() ** 2 / th - 1) * 100)
    devs = np.array(devs)
    print(f"(2) MC 可行域 (理论CV²<=20): {len(devs)} 格子, n=2e5")
    print(f"    |偏差| 中位={np.median(devs):.2f}%  90分位={np.percentile(devs, 90):.2f}%  "
          f"99分位={np.percentile(devs, 99):.2f}%  最大={devs.max():.2f}%")
    for (R, k, I0, h) in [(1.5, 1.0, 100, 8), (3.0, 0.3, 1000, 4), (0.8, 1.0, 10, 8)]:
        th = cv2_macro(h, R, k, I0)
        ratios = []
        for n in (20000, 200000, 2000000):
            Z = simulate_paths(R, k, I0, h, n, rng)
            ratios.append(Z.var() / Z.mean() ** 2 / th)
        print(f"    收敛探针 R={R},k={k},I0={I0},h={h} (理论CV²={th:.0f}): "
              + "  ".join(f"n={n:.0e}:{r:.3f}" for n, r in zip((2e4, 2e5, 2e6), ratios)))


def check_lemma3(seed=SEED):
    rng = np.random.default_rng(seed + 1)
    print("(3) 引理3 放大律 (4e5 样本):")
    for h, s in [(1, 0.05), (4, 0.05), (4, 0.08), (8, 0.05)]:
        logRhat = rng.normal(0, s, 400000)
        emp = np.mean((np.exp(h * logRhat) - 1) ** 2)
        th = p_exact(h, s)
        print(f"    h={h}, s={s}: 经验={emp:.5f} 理论={th:.5f} 比={emp / th:.4f}")


def sample_nb(mean, k, rng):
    lam = rng.gamma(shape=k, scale=mean / k)
    return rng.poisson(lam)


def check_orthogonality(seed=SEED + 2, nrep=20000):
    rng = np.random.default_rng(seed)
    print(f"(4) 假定1 交叉项数值检查 (5周窗口估参, n={nrep}/配置):")
    for R, k, I0, label in [(1.27, 56.6, 297, "Delta"),
                            (1.10, 21.0, 758, "Omicron"),
                            (1.55, 11.2, 55, "Flu22-23")]:
        for h in (1, 2, 4):
            acc = np.zeros(4)
            cnt = 0
            for _ in range(nrep):
                Z = np.zeros(5 + 1 + h)
                Z[0] = I0
                for t in range(len(Z) - 1):
                    Z[t + 1] = sample_nb(R * Z[t], k, rng)
                w = Z[:5]
                if np.any(w <= 0):
                    continue
                b, a = np.polyfit(np.arange(5), np.log(w), 1)
                Rhat = np.exp(b)
                cnt += 1
                t0 = 4
                m_true = Z[t0] * R ** h
                m_plug = Z[t0] * Rhat ** h
                Y = Z[t0 + h]
                acc += np.array([(Y - m_plug) ** 2 / m_true ** 2,
                                 (Y - m_true) ** 2 / m_true ** 2,
                                 (m_plug - m_true) ** 2 / m_true ** 2,
                                 (Y - m_true) * (m_plug - m_true) / m_true ** 2])
            rel, proc, P, cross = acc / cnt
            print(f"    {label:8s} h={h}: 交叉/过程 = {cross / proc:+.4f}")


def horizon_accuracy():
    stages = [("Delta", 1.271, 0.0373, 56.6, 297), ("Omicron", 1.099, 0.0482, 21.0, 758),
              ("JN1", 1.044, 0.0447, 29.5, 391), ("Flu22-23", 1.554, 0.0726, 11.2, 55),
              ("Flu24-25", 1.605, 0.0637, 17.4, 96), ("RSV24-25", 1.347, 0.0433, 39.8, 76),
              ("RSV25-26", 1.302, 0.0546, 23.7, 38)]
    tau = 0.5
    print("(5) 线性化闭式 vs 精确根 (τ=0.5, 表3中位参数):")
    ratios = []
    for name, R, s, k, I0 in stages:
        root = brentq(lambda h: cv2_macro(h, R, k, I0) + p_exact(h, s) - tau * tau,
                      1e-6, 30, xtol=1e-9)
        b = 1 / k
        approx = (np.sqrt(b * b + 4 * s * s * tau * tau) - b) / (2 * s * s)
        ratios.append(approx / root)
        print(f"    {name:9s} 精确={root:5.2f}  线性化={approx:5.2f}  比={approx / root:.3f}")
    print(f"    -> 线性化根为精确根的 {min(ratios) * 100:.0f}%--{max(ratios) * 100:.0f}%"
          f"（即高估 {(min(ratios) - 1) * 100:.0f}%--{(max(ratios) - 1) * 100:.0f}%，中位 {(np.median(ratios) - 1) * 100:.0f}%）；"
          "仅参数项领先阶 h≈τ/s 高估 1.70--2.94 倍")


if __name__ == "__main__":
    check_identity()
    check_mc()
    check_lemma3()
    check_orthogonality()
    horizon_accuracy()
