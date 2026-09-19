# -*- coding: utf-8 -*-
"""horizon_robustness.py — two reviewer-requested robustness analyses.

(A) Inclusion-threshold sensitivity. The state panel admits a jurisdiction to a
    phase only when the 5-week inference window totals >= 50 reported cases and
    every week is a positive count. That rule necessarily drops low-incidence
    jurisdictions, which are exactly the ones with small I0 and large macro
    CV^2, i.e. the shortest mechanistic horizons; the rule therefore biases the
    reported median horizon upward. We re-run the whole state panel at
    thresholds of 30/20/10 cases and report how the phase medians move.

(B) Per-state paired horizon ratio. The manuscript's headline envelope statement
    previously divided a median from one state set by a median from another.
    Here h*_i and the observed horizon h^obs_i are computed on the *same*
    jurisdiction i, so Ratio_i = h*_i / h^obs_i is a genuine paired quantity.
    The observed horizon uses each state's own rolling origins evaluated on a
    weekly grid, and units whose observed error never crosses tau are reported
    as censored rather than silently dropped.

Writes reports_v3/horizon_robustness.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts_v2"))

import state_panel_v3 as SP
import emit_v3 as E

REPORTS = ROOT / "reports_v3"
TAU = 0.5
OBS_GRID = list(range(1, 13))     # weekly forward horizons used for h^obs
MAX_ORIGINS = 6


def threshold_sweep(panels, thresholds=(50.0, 30.0, 20.0, 10.0)):
    out = {}
    for thr in thresholds:
        SP.MIN_WINDOW_TOTAL = float(thr)
        res = SP.state_phase_analysis(panels)
        per = {}
        for key, rec in res.items():
            vals = [s["h_week"] for s in rec["states"].values()
                    if s.get("h_week") is not None]
            if not vals:
                continue
            per[key] = {"n": len(vals), "median": float(np.median(vals))}
        out[str(int(thr))] = per
    SP.MIN_WINDOW_TOTAL = 50.0
    return out


def observed_horizons(panel, w0, w1):
    """Per-state observed horizon for one phase, weekly grid, own rolling origins."""
    out = {}
    for loc in sorted(E.STATE_FIPS):
        s = panel[panel.location == loc].set_index("week_end").value.sort_index()
        win = s[(s.index >= w0) & (s.index <= w1)]
        if len(win) != 5 or win.sum() < 50 or (win.values <= 0).any():
            continue
        origins = [d for d in s.index
                   if d >= pd.Timestamp(w0) and int((s.index < d).sum()) >= 4][:MAX_ORIGINS]
        pts = []
        for h in OBS_GRID:
            errs = []
            for t0 in origins:
                hist = s[s.index <= t0].iloc[-4:]
                if (hist.values <= 0).any():
                    continue
                b = E.fit4(np.log(hist.values.astype(float)))
                z = float(hist.values[-1])
                tgt = t0 + pd.Timedelta(weeks=h)
                i = int(s.index.get_indexer([tgt], method="nearest")[0])
                if abs((s.index[i] - tgt).days) > 3:
                    continue
                pred = z * np.exp(b * h)
                errs.append(((pred - float(s.values[i])) / pred) ** 2)
            if len(errs) >= 3:
                pts.append((h, float(np.sqrt(np.mean(errs)))))
        if len(pts) < 3:
            continue
        h_obs = None
        for i, (h, rm) in enumerate(pts):
            if rm >= TAU:
                if i == 0:
                    h_obs = float(h)
                else:
                    h0, r0 = pts[i - 1]
                    h_obs = float(h0 + (TAU - r0) / (rm - r0) * (h - h0))
                break
        if h_obs is None or h_obs <= 0:
            out[loc] = None          # censored: never crosses tau within the grid
        else:
            out[loc] = h_obs
    return out


def paired_ratios(panels, phases_json):
    per_phase = {}
    pooled = []
    for key, src, w0, w1, mu_g, disp in E.PHASES:
        obs = observed_horizons(panels[src], w0, w1)
        states = phases_json[key]["states"]
        ratios, censored = [], 0
        for loc, h_obs in obs.items():
            p = states.get(loc)
            if p is None or p.get("h_week") is None:
                continue
            if h_obs is None:
                censored += 1
                continue
            ratios.append(p["h_week"] / h_obs)
        r = np.array(ratios, dtype=float)
        per_phase[key] = {
            "display": disp,
            "n_paired": int(r.size),
            "n_censored": int(censored),
            "median": float(np.median(r)),
            "q25": float(np.percentile(r, 25)),
            "q75": float(np.percentile(r, 75)),
            "frac_gt1": float((r > 1).mean()),
        }
        pooled.append(r)

    allr = np.concatenate(pooled)
    # exact two-sided sign test against median 1, ignoring ties at exactly 1
    nz = allr[allr != 1.0]
    k = int((nz > 1).sum())
    n = int(nz.size)
    from math import comb
    tail = sum(comb(n, i) for i in range(k, n + 1)) / (2 ** n)
    p_two = min(1.0, 2 * tail)

    return {
        "per_phase": per_phase,
        "pooled": {
            "n_paired": int(allr.size),
            "median": float(np.median(allr)),
            "q25": float(np.percentile(allr, 25)),
            "q75": float(np.percentile(allr, 75)),
            "frac_gt1": float((allr > 1).mean()),
            "frac_lt1": float((allr < 1).mean()),
            "sign_test_n": n,
            "sign_test_k_gt1": k,
            "sign_test_p_two_sided": float(p_two),
        },
    }


def emit_threshold_table(sweep, phases_json) -> None:
    """LaTeX fragment: per-phase median horizon under four inclusion thresholds."""
    thresholds = ["50", "30", "20", "10"]
    rows = []
    for key, rec in phases_json.items():
        disp = rec["display"]
        cells = []
        for t in thresholds:
            r = sweep.get(t, {}).get(key)
            cells.append(f"{r['median']:.2f} ({r['n']})" if r else "---")
        rows.append(f"{disp} & " + " & ".join(cells) + r" \\")
    body = ("\\begin{tabular}{lcccc}\n"
            "\\toprule\n"
            "阶段 & $\\ge 50$ 例（主口径） & $\\ge 30$ 例 & $\\ge 20$ 例 & $\\ge 10$ 例 \\\\\n"
            "\\midrule\n" + "\n".join(rows) + "\n"
            "\\bottomrule\n\\end{tabular}\n")
    (ROOT / "tables_v3" / "tab_threshold_sweep.tex").write_text(body, encoding="utf-8")
    print("[OK] tables_v3/tab_threshold_sweep.tex")



def _solve_h(f, hi_cap=400.0):
    """Robust root find on a bounded horizon grid (P_exact overflows for large h)."""
    from scipy.optimize import brentq as _bq
    lo = 1e-3
    if not np.isfinite(f(lo)) or f(lo) > 0:
        return None
    hi = 2.0
    while hi < hi_cap:
        val = f(hi)
        if np.isfinite(val) and val >= 0:
            return float(_bq(f, lo, hi, xtol=1e-5))
        hi *= 1.5
    return None


def joint_horizon_ci(phases_json, B=1000, seed=20260919, ngrid=41):
    """Bootstrap interval for each phase's median mechanistic horizon.

    Two uncertainty sources are propagated jointly:
      (1) jurisdiction resampling (states drawn with replacement within a phase);
      (2) estimation error in the growth multiplier: R is redrawn lognormal
          with log-scale standard error s_week (the fitted weekly slope SE).

    For speed the per-state horizon is tabulated on a grid of R multipliers
    (log spaced, 0.60x to 1.67x) and interpolated inside the bootstrap loop.

    k_agg and I0 uncertainty are NOT included here; they are quantified
    separately by the window and truncation sweeps in section 5.6.
    """
    import macro_model
    import state_panel_v3 as SP
    rng = np.random.default_rng(seed)
    mult = np.exp(np.linspace(np.log(0.60), np.log(1.67), ngrid))
    out = {}
    for key, rec in phases_json.items():
        rows = [v for v in rec["states"].values()
                if None not in (v.get("R_week"), v.get("s_week"), v.get("k"), v.get("I0"))]
        n = len(rows)
        if n < 5:
            continue
        tables = []
        for v in rows:
            R0, s, k, I0 = float(v["R_week"]), float(v["s_week"]), v["k"], v["I0"]
            hs = []
            for m in mult:
                f = lambda h: float(macro_model.cv2_macro(h, R0 * m, k, I0)) \
                    + float(SP.p_lognorm(h, min(s, 1.0))) - TAU ** 2
                hs.append(_solve_h(f))
            arr = np.array([h if h is not None else np.nan for h in hs])
            tables.append(arr)
        tables = np.vstack(tables)
        meds = []
        for _ in range(B):
            idx = rng.integers(0, n, n)
            jit = rng.normal(0.0, np.array([rows[i]["s_week"] for i in idx]),
                             n)
            pos = np.clip(jit, np.log(0.60), np.log(1.67))
            frac = (pos - np.log(0.60)) / (np.log(1.67) - np.log(0.60)) * (ngrid - 1)
            j0 = np.floor(frac).astype(int)
            j1 = np.minimum(j0 + 1, ngrid - 1)
            w = frac - j0
            sub = tables[idx]
            vals = sub[np.arange(n), j0] * (1 - w) + sub[np.arange(n), j1] * w
            vals = vals[np.isfinite(vals)]
            if vals.size:
                meds.append(float(np.median(vals)))
        if meds:
            meds = np.array(meds)
            out[key] = {
                "display": rec["display"], "n_states": n, "B": B,
                "point_median": float(np.median([v["h_week"] for v in rows])),
                "ci_lo": float(np.percentile(meds, 2.5)),
                "ci_hi": float(np.percentile(meds, 97.5)),
            }
    return out


def emit_joint_ci_table(joint, phases_json):
    """LaTeX fragment: per-phase point median and joint bootstrap interval."""
    order = [k for k in phases_json if k in joint]
    rows = []
    for k in order:
        v = joint[k]
        rows.append(f"{v['display']} & {v['n_states']} & {v['point_median']:.2f} & "
                    f"[{v['ci_lo']:.2f}, {v['ci_hi']:.2f}] & "
                    f"{v['ci_hi'] - v['ci_lo']:.2f} \\\\")
    body = ("\\begin{tabular}{@{}lrrrr@{}}\n"
            "\\toprule\n"
            "阶段 & $n_{\\text{州}}$ & 点估计 & 95\\% 联合自助区间 & 区间宽度 \\\\\n"
            "\\midrule\n" + "\n".join(rows) + "\n"
            "\\bottomrule\n\\end{tabular}\n")
    (ROOT / "tables_v3" / "tab_joint_ci.tex").write_text(body, encoding="utf-8")
    print("[OK] tables_v3/tab_joint_ci.tex")


def main() -> None:
    panels = {
        "covid": SP.load_panels()["covid"],
        "flu": SP.load_panels()["flu"],
        "rsv": SP.load_panels()["rsv"],
    }
    phases_json = json.loads((REPORTS / "state_phases.json").read_text(encoding="utf-8"))

    print("=== (A) 纳入门槛敏感性 ===")
    sweep = threshold_sweep(panels)
    keys = list(sweep["50"].keys())
    print(f"{'阶段':<10s} " + " ".join(f"{t:>7s}" for t in ["50", "30", "20", "10"]))
    for k in keys:
        row = []
        for t in ["50", "30", "20", "10"]:
            rec = sweep[t].get(k)
            row.append(f"{rec['median']:5.2f}({rec['n']:2d})" if rec else "   —   ")
        print(f"{k:<10s} " + " ".join(f"{x:>7s}" for x in row))
    emit_threshold_table(sweep, phases_json)

    print("\n=== (B) 逐州配对比率 ===")
    paired = paired_ratios(panels, phases_json)
    for k, v in paired["per_phase"].items():
        print(f"  {k:<9s} n={v['n_paired']:3d} 删失={v['n_censored']:2d} "
              f"中位={v['median']:.3f} IQR=[{v['q25']:.3f},{v['q75']:.3f}] "
              f">1占比={v['frac_gt1']:.3f}")
    p = paired["pooled"]
    print(f"  全样本 n={p['n_paired']} 中位={p['median']:.3f} "
          f"IQR=[{p['q25']:.3f},{p['q75']:.3f}] >1={p['frac_gt1']:.3f} <1={p['frac_lt1']:.3f}")

    print("\n=== (C) h* 的联合自助区间 ===")
    joint = joint_horizon_ci(phases_json)
    for k, v in joint.items():
        print(f"  {k:<9s} n={v['n_states']:3d} 点估计={v['point_median']:5.2f} "
              f"95% CI=[{v['ci_lo']:5.2f},{v['ci_hi']:5.2f}]")

    emit_joint_ci_table(joint, phases_json)
    out = {"threshold_sweep": sweep, "paired_ratio": paired, "joint_ci": joint}
    (REPORTS / "horizon_robustness.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\n[OK] reports_v3/horizon_robustness.json")


if __name__ == "__main__":
    main()
