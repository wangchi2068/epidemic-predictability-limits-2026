"""Recompute journal Table 4 under the P_exact caliber (replacing P_quad).

Reviewer M9/口径 request: unify the P term of Eq.(10) with Theorem 4's
P_exact and recompute the state-level accounting. Everything else
(observed rolling-origin RelMSE, CV^2_macro, state filters) is reused
verbatim from emit_v3.budget().
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import emit_v3 as E  # noqa: E402


def p_exact(h: float, s: float) -> float:
    x = (h * s) ** 2
    return float(np.exp(2 * x) - 2 * np.exp(0.5 * x) + 1)


def budget_pexact(phases_json):
    out = {}
    for key, src, w0, w1, mu_g, disp in E.PHASES:
        if key not in E.BUDGET_PHASES:
            continue
        panel = E.load_panel(src)
        v_phase = E.pooled_causal_drift(panel, w0)
        per_h = {h: [] for h in E.BUDGET_HORIZONS[key]}
        for loc in sorted(E.STATE_FIPS):
            s = panel[panel.location == loc].set_index("week_end").value.sort_index()
            win = s[(s.index >= w0) & (s.index <= w1)]
            if len(win) != 5 or win.sum() < 50 or (win.values <= 0).any():
                continue
            p = phases_json[key]["states"].get(loc)
            if p is None:
                continue
            k, I0 = p["k"], p["I0"]
            R_w = p.get("R_week", float(np.exp(p["b_week"])))
            s_w = p.get("s_week", float(p["se_slope"]))
            origins = [d for d in s.index
                       if d >= pd.Timestamp(w0) and int((s.index < d).sum()) >= 4][:6]
            v = v_phase
            if not np.isfinite(v):
                continue
            for h_wk in E.BUDGET_HORIZONS[key]:
                errs = []
                for t0 in origins:
                    hist = s[s.index <= t0].iloc[-4:]
                    if (hist.values <= 0).any():
                        continue
                    b = E.fit4(np.log(hist.values.astype(float)))
                    z = float(hist.values[-1])
                    tgt = t0 + pd.Timedelta(weeks=h_wk)
                    i = int(s.index.get_indexer([tgt], method="nearest")[0])
                    if abs((s.index[i] - tgt).days) > 3:
                        continue
                    pred = z * np.exp(b * h_wk)
                    errs.append(((pred - float(s.values[i])) / pred) ** 2)
                if len(errs) < 3:
                    continue
                obs = float(np.mean(errs))
                cv = float(E.macro_model.cv2_macro(h_wk, R_w, k, I0))
                p_err = p_exact(h_wk, s_w)
                resid = obs - (cv + p_err)
                per_h[h_wk].append({"obs": obs, "cv2": cv,
                                    "p_param": p_err, "e_misspec": resid,
                                    "share_misspec": resid / obs if obs > 0 else None})
        summary = {}
        for h_wk, rows in per_h.items():
            if not rows:
                continue
            shares = [r["share_misspec"] for r in rows if r["share_misspec"] is not None]
            summary[h_wk] = {
                "n": len(rows),
                "obs_med": float(np.median([r["obs"] for r in rows])) * 1e4,
                "cv2_med": float(np.median([r["cv2"] for r in rows])) * 1e4,
                "p_med": float(np.median([r["p_param"] for r in rows])) * 1e4,
                "resid_med": float(np.median([r["e_misspec"] for r in rows])) * 1e4,
                "share_med": float(np.median(shares)) if shares else None,
                "share_q25": float(np.percentile(shares, 25)) if shares else None,
                "share_q75": float(np.percentile(shares, 75)) if shares else None,
                "share_pos_frac": float(np.mean([x > 0 for x in shares])) if shares else None,
            }
        out[key] = {"display": disp, "horizons": summary}
    return out


def main():
    phases = json.loads((E.REPORTS / "state_phases.json").read_text(encoding="utf-8"))
    bud = budget_pexact(phases)
    (E.REPORTS / "budget_pexact.json").write_text(
        json.dumps(bud, indent=2, ensure_ascii=False), encoding="utf-8")
    print("stage/h | n | obs | cv2 | P_exact | resid | share[Q25,Q75] | pos%")
    all_med = []
    for key, rec in bud.items():
        for h, s in rec["horizons"].items():
            print(f"{rec['display'][:14]:14s} h={h} | {s['n']:2d} | {s['obs_med']:9.2f} | "
                  f"{s['cv2_med']:8.2f} | {s['p_med']:7.2f} | {s['resid_med']:9.2f} | "
                  f"{s['share_med']*100:6.1f}% [{s['share_q25']*100:6.1f}, {s['share_q75']*100:6.1f}] | "
                  f"{s['share_pos_frac']*100:4.0f}%")
            all_med.append(s["share_med"])
    print(f"\n中位数的中位数: {np.median(all_med)*100:.1f}%  (21 配置中为正: "
          f"{sum(1 for m in all_med if m > 0)}/{len(all_med)})")


if __name__ == "__main__":
    main()
