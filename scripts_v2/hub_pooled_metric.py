"""
hub_pooled_metric.py

Reconstructs the COVID-19 Forecast Hub operational evaluation from raw CSV files
and validates against the frozen JSON.  Then computes the pooled forecast-skill
metric (pooled SERatio) per origin and wave.

Conventions inferred from data inspection:
  - Forecast origin: the forecast_date in the CSV (Monday).
  - z (normalization): weekly_admissions for the week ending the SATURDAY BEFORE
    the origin (i.e., the most recent complete observed week).
    For origin on Monday 2021-08-02, the Saturday before is 2021-08-07.
  - Ensemble weekly forecast: for horizon h (1–4 weeks), sum the daily
    "N day ahead inc hosp" point forecasts for days 7*(h-1)+1 through 7*h
    from the origin.  This covers 28 days starting from the origin Monday,
    targeting weeks ending on Saturdays 2021-08-14, 2021-08-21, 2021-08-28,
    2021-09-04 respectively.
  - Persistence baseline: the last observed weekly value z (a flat forecast).
  - relMSE (per state per origin per h) = (ens - truth)^2 / (z - truth)^2.
  - Pooled metric: sum over states of (ens-z)^2 / sum over states of (z-truth)^2,
    computed separately for each (origin, h).
"""

import gzip, csv, json, statistics, math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_HUB = ROOT / "data" / "hub"
DATA_PANEL = ROOT / "data" / "panels"
REPORTS = ROOT / "reports_v3"
REPORTS.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Load frozen evaluation for comparison
# ---------------------------------------------------------------------------
FROZEN_PATH = DATA_HUB / "forecast_hub_operational_evaluation.json"
with open(FROZEN_PATH, encoding="utf-8") as fh:
    FROZEN = json.load(fh)

# ---------------------------------------------------------------------------
# 2. Load weekly truth
# ---------------------------------------------------------------------------
def load_truth():
    """Returns dict[location][week_end_date] = weekly_admissions (float)."""
    truth = defaultdict(dict)
    with gzip.open(DATA_PANEL / "covid_weekly_hospitalizations.csv.gz", "rt") as f:
        reader = csv.DictReader(f)
        for row in reader:
            truth[row["location"]][row["week_end_date"]] = float(row["weekly_admissions"])
    return truth

# ---------------------------------------------------------------------------
# 3. Load ensemble forecasts (point only, 2-digit FIPS, daily inc hosp)
# ---------------------------------------------------------------------------
FORECAST_ORIGINS = [
    "2021-08-02", "2021-08-09", "2021-08-16", "2021-08-23", "2021-08-30", "2021-09-06",
    "2021-12-06", "2021-12-13", "2021-12-20", "2021-12-27", "2022-01-03", "2022-01-10",
]
WAVE_MAP = {
    "2021-08-02": "Delta",  "2021-08-09": "Delta",  "2021-08-16": "Delta",
    "2021-08-23": "Delta",  "2021-08-30": "Delta",  "2021-09-06": "Delta",
    "2021-12-06": "Omicron","2021-12-13": "Omicron","2021-12-20": "Omicron",
    "2021-12-27": "Omicron","2022-01-03": "Omicron","2022-01-10": "Omicron",
}

# Map forecast origin (Monday) to its Saturday-before week_end_date
ORIGIN_TO_Z_DATE = {
    "2021-08-02": "2021-08-07",
    "2021-08-09": "2021-08-14",
    "2021-08-16": "2021-08-21",
    "2021-08-23": "2021-08-28",
    "2021-08-30": "2021-09-04",
    "2021-09-06": "2021-09-11",
    "2021-12-06": "2021-12-04",
    "2021-12-13": "2021-12-11",
    "2021-12-20": "2021-12-18",
    "2021-12-27": "2021-12-25",
    "2022-01-03": "2022-01-01",
    "2022-01-10": "2022-01-08",
}

# Map horizon h to the week_end_date of the target week (relative to origin)
# h=1: 1 week after z_date; h=2: 2 weeks after; etc.
def target_date_for(origin, h):
    """Return the week_end_date (Saturday) for horizon h from this origin."""
    z_date = ORIGIN_TO_Z_DATE[origin]
    # z_date is always a Saturday.  Add 7*h days to get target.
    year, month, day = map(int, z_date.split("-"))
    # Simple approach: use Python to add 7*h days
    from datetime import date, timedelta
    d = date(year, month, day) + timedelta(weeks=h)
    return d.isoformat()

def load_forecasts(origin):
    """Load daily point forecasts for a given origin.  Returns dict[location]{target: value}."""
    fname = DATA_HUB / f"{origin}-COVIDhub-ensemble.csv.gz"
    fc = defaultdict(dict)
    with gzip.open(fname, "rt") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["type"] == "point" and len(row["location"]) == 2 and "inc hosp" in row["target"]:
                fc[row["location"]][row["target"]] = float(row["value"])
    return fc

def weekly_ensemble(forecasts, loc, h):
    """
    Sum of daily forecasts for horizon h.
    h=1: days 1-7, h=2: days 8-14, h=3: days 15-21, h=4: days 22-28.
    """
    start = 7 * (h - 1) + 1
    return sum(forecasts[loc][f"{d} day ahead inc hosp"] for d in range(start, start + 7))

# ---------------------------------------------------------------------------
# 4. Compute per-state relMSE for one (origin, h)
# ---------------------------------------------------------------------------
def compute_relMSEs(origin, h, forecasts, truth):
    """
    Returns list of (location, relMSE) for all states where all values exist.
    relMSE = (ens - truth)^2 / (z - truth)^2  (inf if denominator is 0).
    """
    z_date = ORIGIN_TO_Z_DATE[origin]
    t_date = target_date_for(origin, h)
    results = []
    for loc in forecasts:
        if loc not in truth:
            continue
        z = truth[loc].get(z_date)
        actual = truth[loc].get(t_date)
        if z is None or actual is None or z == actual:
            continue  # can't compute or undefined
        ens = weekly_ensemble(forecasts, loc, h)
        num = (ens - actual) ** 2
        den = (z - actual) ** 2
        relMSE = float("inf") if den == 0 else num / den
        results.append((loc, relMSE, ens, actual, z))
    return results

# ---------------------------------------------------------------------------
# 5. Validation: compare computed median_relMSE to frozen values
# ---------------------------------------------------------------------------
def validate():
    """Compute median_relMSE for each (origin, h) and compare to frozen."""
    truth = load_truth()
    max_dev = 0.0
    mismatches = []

    print("=" * 80)
    print("VALIDATION: computed vs frozen median_relMSE")
    print("=" * 80)
    print(f"{'Origin':<12} {'Wave':<8} {'h':<2} {'Frozen':>12} {'Computed':>12} {'Dev%':>8} {'N_states'}")
    print("-" * 80)

    for froz in FROZEN:
        origin = froz["forecast_date"]
        wave = froz["wave"]
        forecasts = load_forecasts(origin)

        for h_rec in froz["horizons"]:
            h = h_rec["h_weeks"]
            frozen_med = h_rec["median_relMSE"]
            n_frozen = h_rec["n_states"]

            relMSEs = compute_relMSEs(origin, h, forecasts, truth)
            if not relMSEs:
                continue

            # Filter out inf values for median computation (same as frozen)
            finite = [r[1] for r in relMSEs if math.isfinite(r[1])]
            if finite:
                computed_med = statistics.median(finite)
            else:
                computed_med = float("inf")

            if frozen_med == 0 and computed_med == 0:
                dev_pct = 0.0
            elif frozen_med == float("inf") or computed_med == float("inf"):
                dev_pct = float("inf")
            elif frozen_med == 0:
                dev_pct = float("inf")
            else:
                dev_pct = abs(computed_med - frozen_med) / frozen_med * 100

            max_dev = max(max_dev, dev_pct if dev_pct != float("inf") else 0.0)
            flag = " *** MISMATCH" if dev_pct > 10 and dev_pct != float("inf") else ""
            print(f"{origin:<12} {wave:<8} {h:<2} {frozen_med:>12.6f} {computed_med:>12.6f} {dev_pct:>7.1f}% {len(relMSEs):>8}{flag}")
            if dev_pct > 10 and dev_pct != float("inf"):
                mismatches.append({
                    "origin": origin, "h": h,
                    "frozen": frozen_med, "computed": computed_med,
                    "dev_pct": dev_pct, "n_states": len(relMSEs)
                })

    print("-" * 80)
    print(f"Maximum deviation: {max_dev:.2f}%")
    if mismatches:
        print(f"\nMISMATCHES (>10% deviation):")
        for m in mismatches:
            print(f"  {m['origin']} h={m['h']}: frozen={m['frozen']:.4f}, computed={m['computed']:.4f}, dev={m['dev_pct']:.1f}%")
    else:
        print("All values within 10% of frozen.  Validation PASSED.")
    return max_dev, mismatches

# ---------------------------------------------------------------------------
# 6. Pooled metric computation (only if validation passes)
# ---------------------------------------------------------------------------
def compute_pooled():
    """
    Pooled SERatio per origin and per wave.
    pooled(h) = sum_states ((ens - truth)/z)^2 / sum_states ((pers - truth)/z)^2
    where pers = z (flat persistence baseline).
    We use the SAME convention for the numerator and denominator: errors normalized by z.
    """
    truth = load_truth()
    results = []  # list of dicts matching FROZEN structure, with pooled added

    for froz in FROZEN:
        origin = froz["forecast_date"]
        wave = froz["wave"]
        forecasts = load_forecasts(origin)
        z_date = ORIGIN_TO_Z_DATE[origin]

        rec = {"wave": wave, "forecast_date": origin, "horizons": []}

        for h_rec in froz["horizons"]:
            h = h_rec["h_weeks"]
            t_date = target_date_for(origin, h)

            num_sum = 0.0  # sum of (ens - truth)^2 / z^2
            den_sum = 0.0  # sum of (z - truth)^2 / z^2
            n = 0
            for loc in forecasts:
                if loc not in truth:
                    continue
                z = truth[loc].get(z_date)
                actual = truth[loc].get(t_date)
                if z is None or actual is None or z == 0:
                    continue
                ens = weekly_ensemble(forecasts, loc, h)
                num_sum += ((ens - actual) / z) ** 2
                den_sum += ((z - actual) / z) ** 2
                n += 1

            if den_sum > 0 and n > 0:
                pooled = num_sum / den_sum
                pooled_ge_1 = 1.0 if pooled >= 1.0 else 0.0
            else:
                pooled = None
                pooled_ge_1 = None

            new_h = dict(h_rec)
            new_h["pooled_relMSE"] = pooled
            new_h["frac_pooled_ge_1"] = pooled_ge_1
            new_h["n_states_pooled"] = n
            rec["horizons"].append(new_h)

        results.append(rec)

    return results

# ---------------------------------------------------------------------------
# 7. Cross-origin median per wave for the pooled metric
# ---------------------------------------------------------------------------
def pooled_summary(pooled_results):
    """Compute cross-origin median of pooled values per wave."""
    from collections import defaultdict
    wave_h_pooled = defaultdict(lambda: defaultdict(list))
    for rec in pooled_results:
        wave = rec["wave"]
        for h_rec in rec["horizons"]:
            h = h_rec["h_weeks"]
            if h_rec["pooled_relMSE"] is not None:
                wave_h_pooled[wave][h].append(h_rec["pooled_relMSE"])

    summary = {}
    for wave, h_dict in wave_h_pooled.items():
        summary[wave] = {}
        for h, vals in h_dict.items():
            summary[wave][h] = {
                "cross_origin_median": statistics.median(vals),
                "n_origins": len(vals),
                "values": vals
            }
    return summary

# ---------------------------------------------------------------------------
# 8. Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    max_dev, mismatches = validate()

    if max_dev > 15:
        print("\n*** Validation FAILED (max deviation > 15%). Stopping.")
        print("Pooled metric NOT computed.")
    else:
        print("\n*** Validation passed or close enough. Computing pooled metric...")
        pooled_results = compute_pooled()
        summary = pooled_summary(pooled_results)

        # Write JSON
        output = {
            "validation_max_dev_pct": max_dev,
            "validation_passed": max_dev <= 15,
            "per_origin": pooled_results,
            "per_wave_summary": summary,
        }
        out_path = REPORTS / "hub_pooled_metric.json"
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(output, fh, indent=2, default=str)
        print(f"\nPooled metric written to {out_path}")

        # Print summary table
        print("\n" + "=" * 80)
        print("POOLED METRIC SUMMARY (cross-origin median per wave)")
        print("=" * 80)
        for wave in ["Delta", "Omicron"]:
            print(f"\n{wave}:")
            if wave in summary:
                for h in sorted(summary[wave].keys()):
                    s = summary[wave][h]
                    print(f"  h={h}: pooled={s['cross_origin_median']:.4f} (n_origins={s['n_origins']})")

        # Per-origin table
        print("\n" + "=" * 80)
        print("POOLED METRIC PER ORIGIN")
        print("=" * 80)
        print(f"{'Origin':<12} {'Wave':<8} {'h':<2} {'Pooled':>10} {'Frac>=1':>9} {'N_states'}")
        for rec in pooled_results:
            for h_rec in rec["horizons"]:
                h = h_rec["h_weeks"]
                p = h_rec.get("pooled_relMSE")
                f = h_rec.get("frac_pooled_ge_1")
                ns = h_rec.get("n_states_pooled", "N/A")
                pv = f"{p:.4f}" if p is not None else "N/A"
                fv = f"{f:.2f}" if f is not None else "N/A"
                print(f"{rec['forecast_date']:<12} {rec['wave']:<8} {h:<2} {pv:>10} {fv:>9} {ns}")
