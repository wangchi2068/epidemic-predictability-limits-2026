"""I0 caliber sensitivity: window mean vs last observation vs regression endpoint.

Recomputes the primary macro-exact weekly-clock horizon h*_week for each state
and phase under three definitions of the initial level I0, holding the fitted
growth parameters (R_week, s_week, k_agg) fixed from the baseline fit:

  mean   : I0 = mean of the 5-week window (paper main caliber)
  last   : I0 = last observed weekly count in the window (Markov state Z_t)
  fitend : I0 = fitted endpoint exp(a + 4b) of the log-linear regression

Writes reports_v3/i0_sensitivity.json with per-phase medians and the
cross-state median percent change of h* under each alternative caliber.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state_panel_v3 as sp

ROOT = Path(__file__).resolve().parents[1]


def analyze_segment_i0(counts, mu_g=None):
    """Fit one phase window and solve h* under three I0 calibers.

    Returns None when the baseline data requirements are not met (identical
    to state_panel_v3.analyze_segment, so the sample matches the main table).
    """
    counts = np.asarray(counts, dtype=float)
    if (counts.size < 5 or counts.sum() < sp.MIN_WINDOW_TOTAL
            or (counts < sp.MIN_WEEK_COUNT).any()):
        return None
    y = np.log(counts)
    b, se_b, a, sigma2, x = sp.fit_loglinear(y)
    k = sp.estimate_k(counts)
    R_w = float(np.exp(b))
    s_w = float(se_b)
    i0_mean = float(counts.mean())
    i0_last = float(counts[-1])
    i0_fitend = float(np.exp(a + b * x[-1]))
    out = {}
    for name, i0 in (("mean", i0_mean), ("last", i0_last), ("fitend", i0_fitend)):
        out[name] = sp.solve_hstar_macro(R_w, s_w, k, i0)
    return out


def main():
    panels = sp.load_panels()
    rows = []
    for key, src, w0, w1, mu_g, disp in sp.PHASES:
        panel = panels[src]
        for loc in sorted(sp.STATE_FIPS):
            seg = sp.window_values(panel, loc, w0, w1)
            if len(seg) != 5:
                continue
            rec = analyze_segment_i0(seg.values)
            if rec is None:
                continue
            rows.append({"phase": key, "loc": loc, **rec})
    df = pd.DataFrame(rows)

    report = {}
    for key, src, w0, w1, mu_g, disp in sp.PHASES:
        sub = df[df.phase == key].dropna(subset=["mean"])
        n = len(sub)
        if n == 0:
            continue
        med = {c: float(sub[c].median()) for c in ("mean", "last", "fitend")}
        pct_last = float(((sub["last"] - sub["mean"]) / sub["mean"] * 100).median())
        pct_fit = float(((sub["fitend"] - sub["mean"]) / sub["mean"] * 100).median())
        report[key] = {
            "display": disp,
            "n": n,
            "median_h": med,
            "median_pct_change_last": pct_last,
            "median_pct_change_fitend": pct_fit,
            "min_pct_change_last": float((sub["last"] / sub["mean"] - 1).min() * 100),
            "max_pct_change_last": float((sub["last"] / sub["mean"] - 1).max() * 100),
            "min_pct_change_fitend": float((sub["fitend"] / sub["mean"] - 1).min() * 100),
            "max_pct_change_fitend": float((sub["fitend"] / sub["mean"] - 1).max() * 100),
        }
    # cross-phase summary
    all_last = [abs(v["median_pct_change_last"]) for v in report.values()]
    all_fit = [abs(v["median_pct_change_fitend"]) for v in report.values()]
    report["_summary"] = {
        "max_abs_median_pct_change_last": max(all_last),
        "min_abs_median_pct_change_last": min(all_last),
        "max_abs_median_pct_change_fitend": max(all_fit),
        "min_abs_median_pct_change_fitend": min(all_fit),
    }
    out = ROOT / "reports_v3" / "i0_sensitivity.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
