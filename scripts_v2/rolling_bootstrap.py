# -*- coding: utf-8 -*-
"""rolling_bootstrap.py — origin-level bootstrap for the rolling-backtest
crossing points (reviewer item: crossing points from 6 weekly origins may be
unstable).

For each phase and state we recompute the per-origin normalized errors of the
model, persistence and local-linear forecasts, then resample the origins with
replacement B times, recompute the skill-ratio curve and its crossing of 1.0,
and report the bootstrap distribution of the crossing point. Because the skill
ratio is a *ratio of means over origins*, resampling origins is the natural
unit-level bootstrap.

Writes reports_v3/rolling_bootstrap.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts_v2"))
import state_panel_v3 as sp  # noqa: E402

REPORTS = ROOT / "reports_v3"
B = 2000
SEED = 20260807
STATE_FIPS = {f"{i:02d}" for i in range(1, 57)}


def crossing(vals, hs, direction):
    for i, h in enumerate(hs):
        v = vals[i]
        hit = v >= 1.0 if direction == "up" else v <= 1.0
        if hit:
            if i == 0:
                return float(h)
            x0, x1, y0, y1 = hs[i - 1], h, vals[i - 1], v
            if y1 == y0:
                return float(h)
            return float(x0 + (1 - y0) / (y1 - y0) * (x1 - x0))
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rng = np.random.default_rng(SEED)
    panels = sp.load_panels()
    phases = sp.PHASES

    out = {}
    for key, src, w0, w1, mu_g, disp in phases:
        panel = panels[src]
        per_state_pers, per_state_lin = {}, {}
        for loc in sorted(STATE_FIPS):
            s = sp.series_for(panel, loc)
            if len(s) < 6:
                continue
            win = s[(s.index >= w0) & (s.index <= w1)]
            if len(win) != 5 or win.sum() < sp.MIN_ROLL_TOTAL:
                continue
            origins = [d for d in s.index
                       if d >= pd.Timestamp(w0) and int((s.index < d).sum()) >= 4][:6]
            if len(origins) < 3:
                continue

            # per-origin errors at each h, per method
            err_by_origin = []  # list of dict h -> {model,pers,lin}
            for t0 in origins:
                hist = s[s.index <= t0].iloc[-4:]
                if (hist.values <= 0).any():
                    continue
                b = float(np.polyfit(np.arange(4), np.log(hist.values.astype(float)), 1)[0])
                z = float(hist.values[-1])
                if z <= 0:
                    continue
                ratio = z / max(float(hist.values[-2]), 1.0)
                rec = {}
                for h in range(1, 9):
                    tgt = t0 + pd.Timedelta(weeks=h)
                    i = int(s.index.get_indexer([tgt], method="nearest")[0])
                    if abs((s.index[i] - tgt).days) > 3:
                        continue
                    actual = float(s.values[i])
                    if actual <= 0:
                        continue
                    rec[h] = {"model": ((z * np.exp(b * h) - actual) / z) ** 2,
                              "pers": ((z - actual) / z) ** 2,
                              "lin": ((z * ratio ** h - actual) / z) ** 2}
                if rec:
                    err_by_origin.append(rec)

            if len(err_by_origin) < 3:
                continue

            def crossing_from_sample(sample_idx, direction):
                hs = [h for h in range(1, 9)
                      if all(h in err_by_origin[j] for j in sample_idx)]
                if len(hs) < 2:
                    return None
                vals = []
                for h in hs:
                    num = np.mean([err_by_origin[j][h]["model"] for j in sample_idx])
                    den = np.mean([err_by_origin[j][h]["pers" if direction == "up" else "lin"]
                                   for j in sample_idx])
                    if den <= 0:
                        return None
                    vals.append(num / den)
                return crossing(vals, hs, direction)

            n = len(err_by_origin)
            for direction, store in (("up", per_state_pers), ("down", per_state_lin)):
                base = crossing_from_sample(list(range(n)), direction)
                if base is None:
                    continue
                boots = []
                for _ in range(B):
                    idx = rng.integers(0, n, size=n).tolist()
                    c = crossing_from_sample(idx, direction)
                    if c is not None:
                        boots.append(c)
                if not boots:
                    continue
                store[loc] = {"crossing": base,
                              "ci": [float(np.percentile(boots, 2.5)),
                                     float(np.percentile(boots, 97.5))],
                              "n_origins": n}

        def summ(store):
            if not store:
                return None
            med = float(np.median([v["crossing"] for v in store.values()]))
            ci_lo = float(np.median([v["ci"][0] for v in store.values()]))
            ci_hi = float(np.median([v["ci"][1] for v in store.values()]))
            return {"n_states": len(store), "median_crossing": med,
                    "median_ci": [ci_lo, ci_hi]}

        out[key] = {"display": disp,
                    "persistence": summ(per_state_pers),
                    "local_linear": summ(per_state_lin)}
        pe, ll = out[key]["persistence"], out[key]["local_linear"]
        print(f"[{key:8s}] persistence median={pe['median_crossing']:.2f} "
              f"CI=[{pe['median_ci'][0]:.2f},{pe['median_ci'][1]:.2f}]  "
              f"local-linear median={ll['median_crossing']:.2f} "
              f"CI=[{ll['median_ci'][0]:.2f},{ll['median_ci'][1]:.2f}]", flush=True)

    (REPORTS / "rolling_bootstrap.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nwrote reports_v3/rolling_bootstrap.json")


if __name__ == "__main__":
    main()
