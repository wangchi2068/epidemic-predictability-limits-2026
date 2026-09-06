"""Quantify when 1/E[Z_h] term in T5 cross-covariance is negligible."""

import numpy as np

rng = np.random.default_rng(20260807)


def cross_term_share(v, k, I0, h, reps=20000):
    """Estimate 2Cov(log E[Zh], log(Zh/E[Zh])) / Var(log Zh) via simulation."""
    cov_sum = 0.0
    var_sum = 0.0
    for _ in range(reps):
        # log R innovation iid
        etas = rng.normal(0, v, h)
        logR = np.log(1.05) + etas
        # E[Zh] = I0 * prod(R_t)
        logEZ = np.log(I0) + logR.sum()
        # demographic noise: NB with mean EZh, dispersion k
        EZh = np.exp(logEZ)
        # Zh ~ NB(mean=EZh, k): var = mean + mean^2/k
        if EZh > 1e-5:
            # sample Zh
            p = k / (k + EZh)
            Zh = rng.negative_binomial(k, p) if k > 0 else EZh
            if Zh > 0:
                logZ = logEZ + np.log(Zh / EZh)
                # target: Var(log Z) approx Var(logEZ) + CV^2 where CV^2 = 1/EZh + 1/k
                # cross term contribution
                m1 = np.log(Zh / EZh)  # log(Zh/EZh)
                cov_sum += (logEZ - np.mean(logEZ)) * m1
                var_sum += (logZ - np.mean(logZ)) ** 2
    # cov_sum is biased estimator; use direct
    return None


def cross_term_sim(v, k, I0, h, reps=20000):
    logEZs = np.zeros(reps)
    logZs = np.zeros(reps)
    for i in range(reps):
        etas = rng.normal(0, v, h)
        logEZ = np.log(I0) + etas.sum()
        EZh = np.exp(logEZ)
        p = k / (k + EZh)
        Zh = rng.negative_binomial(k, p)
        Zh = max(Zh, 1)
        logZs[i] = logEZ + np.log(Zh / EZh)
        logEZs[i] = logEZ
    varZ = np.var(logZs)
    cov = np.cov(logEZs, np.log(np.exp(logZs - logEZs)))[0, 1] if reps > 2 else 0
    # cov(logEZ, log(Zh/EZh))
    ratio = abs(2 * cov) / varZ
    return ratio, varZ


print(f"{'v':>5} {'k':>5} {'I0':>5} {'h':>3} {'E[Zh]':>10} {'交叉项占比':>10}")
for v, k, I0, h in [
    (0.05, 5, 100, 2),
    (0.05, 5, 100, 4),
    (0.05, 5, 1000, 4),
    (0.05, 5, 10000, 4),
    (0.1, 5, 100, 4),
    (0.05, 1, 100, 4),
]:
    EZh = I0 * 1.05**h
    ratio, _ = cross_term_sim(v, k, I0, h, reps=10000)
    print(f"{v:>5.2f} {k:>5.1f} {I0:>5.0f} {h:>3.0f} {EZh:>10.1f} {ratio:>10.2%}")
