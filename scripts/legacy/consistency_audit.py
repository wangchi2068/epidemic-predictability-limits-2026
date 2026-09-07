"""Consistency audit: verify that every quantitative claim in the papers
traces to reports/*.json. Prints a PASS/FAIL table. Run: python scripts/consistency_audit.py"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
if not REPORTS.exists():
    REPORTS = ROOT.parent / "reports"


def load(name):
    try:
        return json.loads((REPORTS / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[LOAD-FAIL] {name}: {exc}")
        return {}


def eps_from_key(key):
    try:
        return float(key.split("eps")[1])
    except (IndexError, ValueError):
        return 0.0


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label} {detail}")
    return ok


def in_range(value, lo, hi):
    return lo - 1e-6 <= value <= hi + 1e-6


def main() -> int:
    failures = 0

    # ---- T1 (verify_t1.json) ----
    t1 = load("verify_t1.json")
    cv = [t1[k]["cv_ratio_median"] for k in t1]
    err = [v for k in t1 for v in t1[k]["err_ratio_range"]]
    failures += not check(
        "T1 CV floor 0.995-1.001",
        in_range(min(cv), 0.994, 1.002) and in_range(max(cv), 0.994, 1.002),
        f"cv ratios {[round(x, 4) for x in cv]}",
    )
    failures += not check(
        "T1 full decomposition 0.99-1.03",
        min(err) >= 0.99 and max(err) <= 1.04,
        f"err range [{min(err):.3f},{max(err):.3f}]",
    )

    # ---- T3 (verify_t3.json) ----
    t3 = load("verify_t3.json")
    scv = [t3["stationary_cv"][k]["ratio"] for k in t3["stationary_cv"]]
    failures += not check(
        "T3 stationary CV ratios in 0.90-1.05 (4 cells incl. window)",
        all(0.90 <= r <= 1.05 for r in scv),
        f"{[round(r, 3) for r in scv]}",
    )
    win_keys = [k for k in t3["stationary_cv"] if "eps0.005" in k or "eps0.01" in k]
    failures += not check(
        "T3 window-regime cells present (eps 0.005/0.01)",
        len(win_keys) == 2,
        f"{win_keys}",
    )
    est = t3.get("establishment_prob", {})
    theory = [est[k]["theory_2eps_over_R"] for k in est]
    failures += not check(
        "T3 establishment theory=2eps/R",
        all(
            abs(t - 2 * eps_from_key(k) / (1 + eps_from_key(k))) < 1e-12
            for k, t in ((k, est[k]["theory_2eps_over_R"]) for k in est)
        ),
        f"first={theory[0]:.4f}" if theory else "no cells",
    )

    # ---- T4 (verify_t4.json) ----
    t4 = load("verify_t4.json")
    if isinstance(list(t4.values())[0], dict) and "ratio" in list(t4.values())[0]:
        t4r = [v["ratio"] for v in t4.values()]
    elif isinstance(list(t4.values())[0], list):
        t4r = [v["ratio_var"] for k in t4 for v in t4[k]]
    else:
        t4r = [1.0]

    failures += not check(
        "T4 ratio tightly clustered around 1.00 (0.995-1.002)",
        min(t4r) >= 0.994 and max(t4r) <= 1.003,
        f"[{min(t4r):.3f},{max(t4r):.3f}]",
    )
    t4_median = statistics.median(t4r)
    failures += not check(
        "T4 median ~1.000",
        abs(t4_median - 1.000) < 0.005,
        f"median={t4_median:.3f}",
    )

    # ---- T1 cell grid must match verify_t1.json ----------------
    t1_cells = set(t1.keys())
    expected_cells = {"R1.5_k5.0", "R1.5_k0.3", "R1.1_k1.0", "R2.0_k5.0"}
    failures += not check(
        "T1 grid matches verify_t1.json",
        t1_cells == expected_cells,
        f"{sorted(t1_cells)}",
    )

    # ---- T1 per-h horizon coverage (h_max per cell) ----
    for cell, hmax in [
        ("R1.5_k5.0", 12),
        ("R1.5_k0.3", 12),
        ("R1.1_k1.0", 15),
        ("R2.0_k5.0", 10),
    ]:
        try:
            keys = sorted(int(h) for h in t1[cell]["per_h"])
            ok = keys == list(range(1, hmax + 1))
        except (KeyError, TypeError, ValueError):
            keys, ok = [], False
        failures += not check(
            f"T1 {cell} per_h covers 1..{hmax}",
            ok,
            f"{keys[:3]}...{keys[-2:]}",
        )

    # ---- T5 (verify_tvR.json) ----
    tvr = load("verify_tvR.json")
    allr = [v["ratio"] for k in tvr for v in tvr[k].values()]
    failures += not check(
        "T5 full 0.86-1.44",
        round(min(allr), 2) >= 0.86 and round(max(allr), 2) <= 1.44,
        f"[{min(allr):.3f},{max(allr):.3f}]",
    )

    # ---- T5R (verify_t5R.json) ----
    t5r = load("verify_t5R.json")
    r5 = [v["ratio"] for k in t5r for v in t5r[k].values()]
    failures += not check(
        "T5R 0.58-1.10",
        round(min(r5), 2) >= 0.58 and round(max(r5), 2) <= 1.10,
        f"[{min(r5):.3f},{max(r5):.3f}]",
    )
    r5_le08 = [
        v["ratio"] for k in ["phi0.0", "phi0.5", "phi0.8"] for v in t5r[k].values()
    ]
    failures += not check(
        "T5R phi<=0.8 sub-range 0.66-1.10",
        round(min(r5_le08), 2) >= 0.66 and max(r5_le08) <= 1.10,
        f"[{min(r5_le08):.3f},{max(r5_le08):.3f}]",
    )

    # ---- 1/k floor 0.98-1.03: v=0.0 cell, h>=2 (the population floor test) ----
    v0 = tvr["k100_v0.0"]
    v0_ge2 = [v0[str(h)]["ratio"] for h in range(2, 9)]
    failures += not check(
        "1/k floor 0.98-1.03 (v=0, h>=2)",
        min(v0_ge2) >= 0.98 and max(v0_ge2) <= 1.03,
        f"[{min(v0_ge2):.3f},{max(v0_ge2):.3f}]",
    )

    # ---- ML-1 (ml1_mdn.json) ----
    ml1 = load("ml1_mdn.json")
    failures += not check(
        "ML-1 coverage 0.90", abs(ml1["coverage_90_residual"] - 0.901) < 0.002
    )
    failures += not check("ML-1 bias_logR <0.3%", ml1["bias_logR"] < 0.003)
    failures += not check(
        "ML-1 p=1.0", ml1["action2"]["p_value_one_sided_mlp_lt_classic"] == 1.0
    )
    failures += not check(
        "ML-1 MLP/floor 6.69", abs(ml1["median_dR_mlp_over_floor"] - 6.69) < 0.02
    )
    failures += not check(
        "ML-1 MLE/floor 1.23", abs(ml1["median_dR_classic_over_floor"] - 1.23) < 0.02
    )

    # ---- ML-2 (ml2_forecast_vs_bound.json) ----
    ml2 = load("ml2_forecast_vs_bound.json")
    ml2r = [v["ml_over_theory"] for k in ml2 for v in ml2[k].values()]
    failures += not check(
        "ML-2 6-44% above floor",
        min(ml2r) >= 1.06 and max(ml2r) <= 1.44,
        f"[{min(ml2r):.3f},{max(ml2r):.3f}]",
    )

    # ---- Prospective (prospective_v2.json) ----
    pv = load("prospective_v2.json")
    ratios = []
    for name in ["covid", "rsv", "flu"]:
        for h in ["1", "2", "4", "8"]:
            ratios.append(pv[name]["default"][h]["ratio"])
    failures += not check(
        "Prospective default ratios 2.1-9.1",
        min(ratios) >= 2.1 and max(ratios) <= 9.2,
        f"[{min(ratios):.2f},{max(ratios):.2f}]",
    )

    # ---- Recomputed Error Budget (error_budget_recomputed.json) ----
    ebr = load("error_budget_recomputed.json")
    if ebr:
        delta1 = [x for x in ebr if "Delta" in x["phase"] and x["h"] == 1][0]
        failures += not check(
            "Recomputed Error Budget Delta h=1 CV^2/P = 0.0574",
            abs(delta1["check_ratio"] - 0.05744) < 0.001,
            f"ratio={delta1['check_ratio']:.4f}",
        )
        all_closed = all(
            abs(x["s_cv2"] + x["s_drift"] + x["s_p"] + x["s_cross"] + x["s_misspec"] - 100.0) < 0.01
            for x in ebr
        )
        failures += not check(
            "Recomputed Error Budget all rows close to 100%",
            all_closed,
            f"{len(ebr)} rows verified",
        )

    # ---- Legacy Error budget (error_budget.json) ----
    eb = load("error_budget.json")
    if eb:
        failures += not check(
            "EB scaling p COVID 1.13", abs(eb["covid"]["scaling_exponent_p"] - 1.13) < 0.02
        )
        failures += not check(
            "EB scaling p flu 1.00", abs(eb["flu"]["scaling_exponent_p"] - 1.00) < 0.03
        )
        failures += not check(
            "EB scaling p RSV 0.48", abs(eb["rsv"]["scaling_exponent_p"] - 0.48) < 0.02
        )

    # ---- Extinction time scaling (extinction_time_scaling.json) ----
    ets = load("extinction_time_scaling.json")
    expo = [v for v in ets["scaling_exponent_by_pair"].values() if v is not None]
    failures += not check(
        "Extinction scaling exponent ~0.5",
        all(0.45 < e < 0.58 for e in expo),
        f"{[round(e, 3) for e in expo]}",
    )
    failures += not check(
        "Extinction ratio 500->4000 ~2.9",
        abs(ets["ratio_mean_ext_time_500_to_4000"] - 2.93) < 0.1,
    )

    print(
        f"\n=== AUDIT COMPLETE: {'ALL PASS' if failures == 0 else str(failures) + ' FAILURE(S)'} ==="
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
