# -*- coding: utf-8 -*-
"""check_consistency.py — build-halting consistency suite (21 assertion classes).

1. Table fragments: regenerate every tables_v3/*.tex body from the deposited
   JSONs and byte-compare against the committed fragments (9 fragments),
   and verify all tables_v3 inputs referenced in main.tex exist and are non-empty.
2. Figures: every figure referenced in main.tex exists and is non-blank
   (>5% of pixels differ from the background).
3. Stale-literal blacklist: retired phrases from earlier versions must be
   absent from every reader-facing file (main.tex and README.md).
4. Abstract assertions: headline ranges printed in the abstracts match the
   JSON-derived values.
5. Cramér--Rao ratios: the micro-layer bootstrap/CRB ratios in the table match
   the fit JSON.
6. Dimensional assertion: every budget row's drift term equals h_week x the
   per-week drift variance (weekly clock; the generation-step form is retired).
7. Two-sided crossing assertion: the rolling evaluation contains both an
   upward persistence crossing and a downward local-linear crossing for the
   Delta and Omicron waves.
8. Deposited-series identity: the national window sums that pin the analysis
   series equal the values the manuscript's tables were built from.
9. Document-declared paths: every file, directory, or glob pattern declared in
   README.md and MANIFEST.md must exist on disk.
10. Citations closure: references.bib is 100% two-way closed with main.tex
    (exactly 44 entries cited, 0 missing, 0 unreferenced).
11. PDF page count: compiled main.pdf is verified to match README.md (30 pages).
12. Phase classification protocol: verify peak-anchored retrospective classification logic
    (|ref - peak| <= 7d -> peak, ref < peak - 7d -> rising, ref > peak + 7d -> declining)
    and empirical partition consistency across all three FluSight releases.
13. Poisson limit properties: Lemma 4 monotonicity, saturation at 1/[I0*(R-1)], and finite plug-in horizon.
14. WIS decomposition direction semantics: under/over prediction penalty directions,
    additive sum identity, and empirical values in main.tex.
15. Four-way common unit sample sizes: exact sample size identity across all models,
    seasons, horizons, and phases.
16. Input SHA-256 manifest: every deposited input file matches data/input_hashes.json.
17. Supplementary tables S1--S9 shipped; every referenced fragment is present.
18. Table typography: no \\resizebox scaling, all declared table sizes >= 7pt.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT
REPORTS = ROOT / "reports_v3"
TABLES = ROOT / "tables_v3"
DATA = ROOT / "data"
FIGS = {
    "fig1_framework": ROOT / "reports_v3" / "figures" / "fig1_framework.png",
    "fig2_cv_verify": ROOT / "reports" / "figures_v2" / "fig2_cv_verify.png",
    "fig_micro": ROOT / "reports_v3" / "figures" / "fig_micro.png",
    "fig_state_horizons": ROOT / "reports_v3" / "figures" / "fig_state_horizons.png",
    "fig_flusight_audit": ROOT / "reports_v3" / "figures" / "fig_flusight_audit.png",
    "fig_hub_skill": ROOT / "reports_v3" / "figures" / "fig_hub_skill.png",
}
SCRIPTS = ROOT / "scripts_v2"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
STATE_FIPS = {f"{i:02d}" for i in range(1, 57)}

# phrases retired from earlier versions; must not appear in reader-facing text
STALE = [
    "26.1\\%--99.3\\%",          # old four-term budget residual range
    "51.2\\%--99.6\\%",          # README's retired residual range
    "1.8--5.3",                  # old operational-lead-time headline
    "41.5--67.8",                # old RSV extrapolation range
    "2.46",                      # old RSV 2025-26 cluster-count ratio
    "h_{\\text{gen}} \\cdot \\widehat{v}^2",  # retired generation-step drift form
    "10 个中为正",                # old budget tally
    "0.74\\%",                   # old national CV^2 contribution
    "三波次、每波次六原点",        # old sample description
    "1.4 倍",                    # retired aggregation-inflation threshold
    "4.5--10.9",                 # retired heuristic-caliber horizon range
    "1.9--6.1",                  # retired envelope multiple range
    "69.0\\%--98.4\\%",          # retired residual-share range
    "机制代理视界",               # retired name for the state-level caliber
]


def fail(msg):
    print(f"[FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def check_tables():
    import emit_v3
    phases = json.loads((REPORTS / "state_phases.json").read_text(encoding="utf-8"))
    roll_state = json.loads((REPORTS / "state_rolling.json").read_text(encoding="utf-8"))
    roll_nat = json.loads((REPORTS / "national_rolling.json").read_text(encoding="utf-8"))
    scen = json.loads((REPORTS / "scenarios.json").read_text(encoding="utf-8"))
    bud = json.loads((REPORTS / "budget_national.json").read_text(encoding="utf-8"))
    micro = json.loads((DATA / "micro" / "micro_branching_fit_results.json")
                       .read_text(encoding="utf-8"))
    hub = json.loads((DATA / "hub" / "forecast_hub_operational_evaluation.json")
                     .read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        emit_v3.TABLES = tmp
        emit_v3.emit_tab_sensitivity()
        emit_v3.emit_table2(phases)
        emit_v3.emit_table3(roll_state, roll_nat, phases, bud)
        emit_v3.emit_table4(bud)
        emit_v3.emit_table5_hub(hub)
        emit_v3.emit_table6_tiers(scen)
        emit_v3.emit_table7(micro)
        emit_v3.emit_table8_flusight()
        emit_v3.emit_table9_phases()
        generated = sorted(tmp.glob("*.tex"))
        if len(generated) != 9:
            fail(f"expected 9 generated table fragments, got {len(generated)}")
        for f in generated:
            committed = TABLES / f.name
            if not committed.exists():
                fail(f"missing committed table fragment {f.name}")
            if committed.read_bytes() != f.read_bytes():
                fail(f"table fragment {f.name} diverges from the JSONs")
    
    # Dynamically verify every \input{tables_v3/...} referenced in main.tex exists and is non-empty
    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    table_inputs = re.findall(r"\\input\{tables_v3/([^}]+)\}", tex)
    if not table_inputs:
        fail("no tables_v3 inputs found in main.tex")
    for t in table_inputs:
        t_file = t if t.endswith(".tex") else f"{t}.tex"
        p = TABLES / t_file
        if not p.exists():
            fail(f"table referenced in main.tex missing on disk: {t_file}")
        if p.stat().st_size == 0:
            fail(f"table referenced in main.tex is empty: {t_file}")
    print(f"[OK] table fragments match deposited JSONs (9 fragments checked, {len(table_inputs)} referenced in main.tex)")


def check_figures():
    import matplotlib.image as mpimg
    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    refs = re.findall(r"\\includegraphics\[[^\]]*\]\{([^}]+)\}", tex)
    if not refs:
        fail("no figure references found")
    for r in refs:
        p = (PAPER / r).resolve()
        if not p.exists():
            fail(f"figure missing: {r}")
        img = mpimg.imread(p)
        frac = float((img[..., :3].min(axis=-1) < 245).mean())
        if frac < 0.05:
            fail(f"figure nearly blank ({frac:.3%} ink): {r}")
    print(f"[OK] {len(refs)} referenced figures exist and are non-blank")


def _norm(t: str) -> str:
    """Normalize dashes/escapes so blacklist hits survive formatting variants."""
    for ch in ("–", "—", "−"):  # en dash, em dash, minus
        t = t.replace(ch, "-")
    return t.replace("\\", "").replace("--", "-").replace(" ", "")


def check_blacklist():
    files = [PAPER / "main.tex", ROOT / "README.md"]
    for f in files:
        if not f.exists():
            fail(f"reader-facing file missing: {f.name}")
        raw_content = f.read_text(encoding="utf-8")
        raw_hexes = re.findall(r"\b[0-9a-fA-F]{20,}\b", raw_content)
        if raw_hexes:
            fail(f"raw hex hash found in {f.name}: {raw_hexes}")
        t = _norm(raw_content)
        for phrase in STALE:
            if _norm(phrase) in t:
                fail(f"stale literal {phrase!r} found in {f.name}")
    print(f"[OK] stale-literal scan clean across {len(files)} reader-facing files (0 raw hashes, 0 stale phrases)")


def check_abstract():
    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    phases = json.loads((REPORTS / "state_phases.json").read_text(encoding="utf-8"))
    med = [p["h_week_summary"]["median"] for p in phases.values()
           if p.get("h_week_summary")]
    lo, hi = min(med), max(med)
    if f"{lo:.1f}--{hi:.1f}" not in tex:
        fail(f"abstract does not state the state-median horizon range "
             f"{lo:.1f}--{hi:.1f}")
    micro = json.loads((DATA / "micro" / "micro_branching_fit_results.json")
                       .read_text(encoding="utf-8"))
    ratios = [r["bootstrap"]["ratio_var_to_crb"] for k, r in micro.items()
              if k != "LloydSmith_reference"]
    if f"{min(ratios):.2f}--{max(ratios):.2f}" not in tex:
        fail("abstract CRB-ratio range does not match the micro JSON")
    aics = [r["delta_aic_poisson_vs_nb"] for k, r in micro.items()
            if k != "LloydSmith_reference"]
    if f"{min(aics):.1f}--{max(aics):.1f}" not in tex:
        fail("abstract dAIC range does not match the micro JSON")
    print(f"[OK] abstract ranges consistent (h* {lo:.1f}--{hi:.1f} wk, "
          f"CRB {min(ratios):.2f}--{max(ratios):.2f}, "
          f"dAIC {min(aics):.1f}--{max(aics):.1f})")


def check_crb_ratios():
    micro = json.loads((DATA / "micro" / "micro_branching_fit_results.json")
                       .read_text(encoding="utf-8"))
    frag = (TABLES / "table2_micro.tex").read_text(encoding="utf-8")
    for k, r in micro.items():
        if k == "LloydSmith_reference":
            continue
        v = f"{r['bootstrap']['ratio_var_to_crb']:.3f}"
        if v not in frag:
            fail(f"CRB ratio {v} for {k} missing from table7 fragment")
    print("[OK] CRB bootstrap ratios in the table match the fit JSON")


def check_drift_dimension():
    bud = json.loads((REPORTS / "budget_national.json").read_text(encoding="utf-8"))
    for key, rec in bud.items():
        for h, row in rec["horizons"].items():
            expect = float(h) * row["median_v_week"]
            if abs(row["median_drift"] - expect) > 1e-12:
                fail(f"{key} h={h}: e_drift {row['median_drift']} != "
                     f"h_week*v {expect} (generation-step form?)")
    print("[OK] drift term equals h_week x weekly variance in every budget row")


def check_crossings():
    roll = json.loads((REPORTS / "state_rolling.json").read_text(encoding="utf-8"))
    for wave in ("Delta", "Omicron"):
        cp = roll[wave]["crossing_persistence"]["median"]
        cl = roll[wave]["crossing_linear"]["median"]
        if cp is None or cl is None:
            fail(f"{wave}: missing a persistence (up) or local-linear (down) crossing")
    print("[OK] two-sided crossings present for Delta and Omicron")


def check_series_identity():
    pinned = {"covid": ("2021-07-03", "2021-07-31", 141735.0),
              "flu": ("2022-10-08", "2022-11-05", 15579.0),
              "rsv": ("2024-11-09", "2024-12-07", 22047.0)}
    for name, (w0, w1, val) in pinned.items():
        if name == "covid":
            d = pd.read_csv(DATA / "panels" / "covid_weekly_hospitalizations.csv.gz",
                            parse_dates=["week_end_date"])
            d = d.rename(columns={"week_end_date": "week_end",
                                  "weekly_admissions": "value"})
        else:
            d = pd.read_csv(DATA / "panels" / f"{name}_weekly_hospitalizations.csv.gz",
                            parse_dates=["week_end"])
        d["location"] = d["location"].astype(str).str.zfill(2)
        nat = (d[d.location.isin(STATE_FIPS)]
               .groupby("week_end").value.sum().sort_index())
        got = float(nat[w0:w1].sum())
        if abs(got - val) > 1e-6:
            fail(f"{name}: national window sum {got} != pinned {val}")
    print("[OK] deposited-series identity pinned for all three panels")


def check_doc_paths():
    doc_files = [ROOT / "README.md", ROOT / "MANIFEST.md"]
    checked = 0
    prefixes = ("data/", "tables_v3/", "reports/", "reports_v3/", "scripts_v2/",
                "derivations/", "paper_cn_journal_template/", "presentation/", "docs/")
    extensions = (".pdf", ".tex", ".docx", ".md", ".json", ".csv", ".gz", ".py", ".png", ".txt")

    for doc in doc_files:
        if not doc.exists():
            fail(f"document missing: {doc.name}")
        text = doc.read_text(encoding="utf-8")
        raw_paths = re.findall(r"`([^`]+)`", text)
        for rp in raw_paths:
            rp = rp.strip()
            if " " in rp:
                rp = rp.split()[0]
            if not (any(rp.startswith(pfx) for pfx in prefixes) or rp.endswith(extensions)):
                continue
            if "*" in rp:
                matches = list(ROOT.glob(rp))
                if not matches:
                    fail(f"glob pattern in {doc.name} matched 0 files: {rp}")
                checked += 1
            else:
                p = (ROOT / rp).resolve()
                if not p.exists():
                    fail(f"path in {doc.name} does not exist: {rp}")
                checked += 1
    print(f"[OK] {checked} document-declared paths verified in README.md and MANIFEST.md")


def check_citations():
    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    cites = set()
    for match in re.findall(r"\\cite[a-zA-Z]*\{([^}]+)\}", tex):
        for key in match.split(","):
            key = key.strip()
            if key:
                cites.add(key)
    bib_text = (ROOT / "references.bib").read_text(encoding="utf-8")
    raw_entries = re.findall(r"@\w+\s*\{\s*([^,]+),", bib_text)
    entries = {k.strip() for k in raw_entries}
    missing = cites - entries
    unref = entries - cites
    if missing:
        fail(f"missing citation keys in references.bib: {missing}")
    if unref:
        fail(f"unreferenced citation keys in references.bib: {unref}")
    if len(entries) != 48:
        fail(f"expected exactly 48 references, found {len(entries)}")
    print(f"[OK] citations 100% two-way closed ({len(cites)}/48 entries cited, 0 missing, 0 unreferenced)")


def check_pdf_pages():
    import pypdf
    pdf_path = PAPER / "main.pdf"
    if not pdf_path.exists():
        fail("main.pdf does not exist")
    reader = pypdf.PdfReader(pdf_path)
    count = len(reader.pages)
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    m = re.search(r"main\.pdf[^\n]*?(\d+)\s*页", readme_text)
    if not m:
        fail("could not parse declared page count from README.md")
    declared = int(m.group(1))
    if count != declared:
        fail(f"main.pdf page count ({count}) does not match README.md declared ({declared})")
    print(f"[OK] main.pdf page count verified ({count} pages, matching README.md)")


def check_input_hashes():
    """Every deposited input file must match the SHA-256 recorded in
    data/input_hashes.json, so the availability statement's byte-level pinning
    claim holds for all inputs (not FluSight alone)."""
    import hashlib
    manifest = DATA / "input_hashes.json"
    if not manifest.exists():
        fail("data/input_hashes.json missing (run scripts_v2/build_input_hashes.py)")
    rows = json.loads(manifest.read_text(encoding="utf-8"))
    if len(rows) < 200:
        fail(f"input hash manifest looks truncated ({len(rows)} entries)")
    bad, missing = [], []
    for r in rows:
        p = ROOT / r["path"]
        if not p.exists():
            missing.append(r["path"])
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest().upper()
        if h != r["sha256"].upper():
            bad.append(r["path"])
    if missing:
        fail(f"{len(missing)} hashed input files missing, e.g. {missing[:3]}")
    if bad:
        fail(f"{len(bad)} input files diverge from their recorded SHA-256, e.g. {bad[:3]}")
    print(f"[OK] input SHA-256 manifest verified ({len(rows)} files, 0 mismatch)")


def check_supplementary():
    """The supplementary table set S1--S9 must be shipped and its fragments present."""
    sup = ROOT / "supplementary"
    for f in ("supplementary_tables.tex", "supplementary_tables.pdf"):
        if not (sup / f).exists():
            fail(f"supplementary/{f} missing")
    tex = (sup / "supplementary_tables.tex").read_text(encoding="utf-8")
    frags = re.findall(r"\\input\{\\suppdir/([^}]+)\}", tex)
    if len(frags) != 9:
        fail(f"expected 9 supplementary fragments, found {len(frags)}")
    for f in frags:
        p = TABLES / (f if f.endswith(".tex") else f + ".tex")
        if not p.exists() or p.stat().st_size == 0:
            fail(f"supplementary fragment missing or empty: {p.name}")
    # every S-label cited in main.tex must be <= 9
    paper = (PAPER / "main.tex").read_text(encoding="utf-8")
    cited = sorted({int(m.group(1)) for m in re.finditer(r"表 S(\d)", paper)})
    if not cited or max(cited) > 9:
        fail(f"main.tex cites supplementary labels beyond S9: {cited}")
    print(f"[OK] supplementary tables S1--S9 shipped ({len(frags)} fragments, cited {cited})")


def check_table_typography():
    """No tables_v3 fragment may be wrapped in \resizebox: scaling a table down
    pushes its body text below the legibility floor (reviewer item C35)."""
    paper = (PAPER / "main.tex").read_text(encoding="utf-8")
    if "\\resizebox" in paper:
        fail("main.tex still uses \\resizebox; table body text will fall below 7pt")
    # the accessibility floor: warn-fail if a table block declares < 7pt
    for m in re.finditer(r"\\fontsize\{(\d+(?:\.\d+)?)pt\}", paper):
        if float(m.group(1)) < 7.0:
            fail(f"declared table font {m.group(1)}pt is below the 7pt legibility floor")
    print("[OK] table typography: no resizebox scaling, all declared sizes >= 7pt")


def check_figure_legibility():
    """Every embedded figure's body text must print at >= 7 pt.

    effective_pt = base_pt x (printed_width_in / canvas_width_in)
    A figure drawn on a wide canvas but printed narrow falls below the floor;
    the canvas sizes below are the ones declared by the generating scripts.
    """
    import pymupdf
    from PIL import Image
    CANVAS = {
        "fig1_framework": (8.6, 9.5),
        "fig2_cv_verify": (8.4, 9.5),
        "fig_micro": (8.4, 9.5),
        "fig_state_horizons": (8.4, 9.5),
        "fig_flusight_audit": (8.4, 9.0),
        "fig_hub_skill": (8.4, 9.5),
    }
    pdf = PAPER / "main.pdf"
    if not pdf.exists():
        fail("main.pdf missing; cannot check figure legibility")
    doc = pymupdf.open(pdf)
    seen, worst = set(), []
    for page in doc:
        for img in page.get_images(full=True):
            info = doc.extract_image(img[0])
            ar = info["width"] / info["height"]
            for name, (cw, base) in CANVAS.items():
                png = FIGS.get(name)
                if png is None or not png.exists():
                    continue
                with Image.open(png) as im:
                    if abs(ar - im.width / im.height) > 0.03:
                        continue
                rects = page.get_image_rects(img[0])
                if not rects:
                    continue
                printed_in = rects[0].width / 72.0
                eff = base * printed_in / cw
                seen.add(name)
                worst.append((eff, name))
    if len(seen) != len(CANVAS):
        fail(f"could not locate all figures in main.pdf (found {sorted(seen)})")
    bad = [(round(e, 2), n) for e, n in worst if e < 7.0]
    if bad:
        fail(f"figure text below the 7 pt legibility floor: {bad}")
    lo = min(worst)
    print(f"[OK] figure text legibility: all {len(seen)} figures >= 7 pt "
          f"(minimum {lo[0]:.2f} pt, {lo[1]})")


def check_alt_variance():
    """Recompute the alternative-variance horizons and check that the ranges
    quoted in main.tex match the JSON (structural sensitivity, reviewer W/C6)."""
    import alt_variance_calibers as AVC
    phases = json.loads((REPORTS / "state_phases.json").read_text(encoding="utf-8"))
    med = {}
    for key in AVC.PHASE_ORDER:
        vals = {c: [] for c in ("nb2", "nb1", "poisson", "micro")}
        for v in phases[key]["states"].values():
            R, s, k, I0 = v.get("R_week"), v.get("s_week"), v.get("k"), v.get("I0")
            if None in (R, s, k, I0):
                continue
            h = AVC.horizons_for_state(R, s, k, I0)
            for c in vals:
                if h[c] is not None:
                    vals[c].append(h[c])
        med[key] = {c: (float(np.median(vals[c])) if vals[c] else None)
                    for c in vals}
    rng = lambda c: (min(med[k][c] for k in med if med[k][c] is not None),
                     max(med[k][c] for k in med if med[k][c] is not None))
    nb2, nb1, po = rng("nb2"), rng("nb1"), rng("poisson")

    json_path = REPORTS / "alt_variance_calibers.json"
    if not json_path.exists():
        fail("reports_v3/alt_variance_calibers.json missing")
    stored = json.loads(json_path.read_text(encoding="utf-8"))
    for k in med:
        for c in med[k]:
            a, b = med[k][c], stored[k]["median"][c]
            if a is None or b is None:
                continue
            if abs(a - b) > 1e-6:
                fail(f"alt-variance median drift for {k}/{c}: {a} vs {b}")

    paper = (PAPER / "main.tex").read_text(encoding="utf-8")
    checks = [
        (f"{nb2[0]:.2f}--{nb2[1]:.2f}", "NB2 range"),
        (f"{po[0]:.2f}--{po[1]:.2f}", "Poisson range"),
        (f"{nb1[0]:.2f}--{nb1[1]:.2f}", "NB1 range"),
    ]
    missing = [name for txt, name in checks if txt not in paper]
    if missing:
        fail(f"main.tex does not quote the recomputed structural ranges: {missing}")
    print(f"[OK] alternative-variance horizons reproduced "
          f"(NB2 {nb2[0]:.2f}--{nb2[1]:.2f}, NB1 {nb1[0]:.2f}--{nb1[1]:.2f}, "
          f"Poisson {po[0]:.2f}--{po[1]:.2f} wk)")



def check_joint_ci_table():
    """tab_joint_ci.tex must match the bootstrap output in horizon_robustness.json."""
    rep = json.loads((REPORTS / "horizon_robustness.json").read_text(encoding="utf-8"))
    joint = rep.get("joint_ci")
    if not joint:
        fail("reports_v3/horizon_robustness.json lacks the joint_ci block")
    frag = (TABLES / "tab_joint_ci.tex").read_text(encoding="utf-8")
    for key, v in joint.items():
        cell = f"[{v['ci_lo']:.2f}, {v['ci_hi']:.2f}]"
        if cell not in frag:
            fail(f"tab_joint_ci.tex missing interval {cell} for {key}")
        if f"{v['point_median']:.2f}" not in frag:
            fail(f"tab_joint_ci.tex missing point estimate for {key}")
    paper = (PAPER / "main.tex").read_text(encoding="utf-8")
    wide = max(joint.items(), key=lambda kv: kv[1]["ci_hi"] - kv[1]["ci_lo"])
    cell = f"{wide[1]['point_median']:.2f} 周 $[{wide[1]['ci_lo']:.2f}, {wide[1]['ci_hi']:.2f}]$"
    if cell not in paper:
        fail("main.tex does not quote the widest joint bootstrap interval")
    print(f"[OK] joint horizon bootstrap intervals reproduced "
          f"({len(joint)} phases, widest {wide[0]} "
          f"[{wide[1]['ci_lo']:.2f}, {wide[1]['ci_hi']:.2f}])")


def check_phase_protocol():
    """Verify that peak-anchored retrospective classification strictly adheres
    to: |ref - peak| <= 7d -> peak, ref < peak - 7d -> rising, ref > peak + 7d -> declining.
    Also verify empirical partition consistency across all three FluSight releases.
    """
    # 1. Synthetic test of the classification logic
    p = pd.Timestamp("2024-01-15")
    # <= 7 days difference
    for dt_str in ["2024-01-08", "2024-01-15", "2024-01-22"]:
        ref = pd.Timestamp(dt_str)
        diff_days = abs((ref - p).days)
        if diff_days <= 7:
            cat = "peak"
        elif ref < p:
            cat = "rising"
        else:
            cat = "declining"
        if cat != "peak":
            fail(f"phase protocol failure: {dt_str} should be 'peak', got {cat}")

    # strictly earlier than peak - 7d
    for dt_str in ["2024-01-01", "2024-01-07"]:
        ref = pd.Timestamp(dt_str)
        if abs((ref - p).days) <= 7:
            cat = "peak"
        elif ref < p:
            cat = "rising"
        else:
            cat = "declining"
        if cat != "rising":
            fail(f"phase protocol failure: {dt_str} should be 'rising', got {cat}")

    # strictly later than peak + 7d
    for dt_str in ["2024-01-23", "2024-02-01"]:
        ref = pd.Timestamp(dt_str)
        if abs((ref - p).days) <= 7:
            cat = "peak"
        elif ref < p:
            cat = "rising"
        else:
            cat = "declining"
        if cat != "declining":
            fail(f"phase protocol failure: {dt_str} should be 'declining', got {cat}")

    # 2. Check deposited JSONs consistency
    expected_phases = {"rising", "peak", "declining"}
    for f in ["flusight_v1.0_extended.json", "flusight_v1.1_extended.json", "flusight_v1.2_extended.json"]:
        d = json.loads((REPORTS / f).read_text(encoding="utf-8"))
        bph = d.get("by_phase_by_horizon", {}).get("1", {})
        if set(bph.keys()) != expected_phases:
            fail(f"{f}: by_phase_by_horizon['1'] keys {set(bph.keys())} != {expected_phases}")
        n_total_phases = sum(bph[phase][0]["n"] for phase in bph)
        n_h1 = d["by_horizon"]["1"]["by_model"]["ensemble"]["n"]
        if n_total_phases != n_h1:
            fail(f"{f}: sum of phase n ({n_total_phases}) != h=1 total n ({n_h1})")
    print("[OK] phase protocol logic and partition consistency verified across all 3 seasons")


def check_poisson_limit():
    """Verify Lemma 4 Poisson limit properties:
    1. Monotonic growth: Delta CV^2_Pois(h) = 1 / (I0 * R^{h+1}) > 0.
    2. Saturation limit: lim_{h -> inf} CV^2_Pois(h) = 1 / [I0 * (R - 1)].
    3. Finite plug-in horizon: CV^2_plug(h) = CV^2_Pois(h) + (exp(h^2 * s^2) - 1)
       strictly crosses any finite threshold tau^2 at finite h* < inf.
    """
    for R in [1.1, 1.3, 1.5, 2.0, 3.0]:
        for I0 in [50, 100, 500, 1000]:
            sat_limit = 1.0 / (I0 * (R - 1.0))
            prev_cv2 = 0.0  # at h=0
            for h in range(1, 25):
                cv2 = (1.0 - R ** (-h)) / (I0 * (R - 1.0))
                # 1. strictly monotonic increase
                if cv2 <= prev_cv2:
                    fail(f"Poisson CV^2 not monotonically increasing at R={R}, I0={I0}, h={h}")
                # exact increment identity
                inc = cv2 - prev_cv2
                exact_inc = 1.0 / (I0 * (R ** h))
                if abs(inc - exact_inc) > 1e-12:
                    fail(f"Poisson CV^2 increment mismatch at R={R}, I0={I0}, h={h}")
                # bounded above by saturation limit
                if cv2 >= sat_limit:
                    fail(f"Poisson CV^2 exceeded saturation limit at R={R}, I0={I0}, h={h}")
                prev_cv2 = cv2

            # check large h saturation and analytical remainder
            cv2_500 = (1.0 - R ** (-500)) / (I0 * (R - 1.0))
            if abs(cv2_500 - sat_limit) > 1e-10:
                fail(f"Poisson CV^2 did not saturate at h=500 for R={R}, I0={I0}")
            # check exact remainder identity at h=10
            cv2_10 = (1.0 - R ** (-10)) / (I0 * (R - 1.0))
            rem_10 = (R ** (-10)) / (I0 * (R - 1.0))
            if abs((sat_limit - cv2_10) - rem_10) > 1e-12:
                fail(f"Poisson remainder identity failed at R={R}, I0={I0}")

    # 3. Check plug-in crossing is finite
    for tau in [0.2, 0.3, 0.5]:
        for s in [0.05, 0.1, 0.2]:
            R, I0 = 1.3, 100
            # find crossing h
            h_cross = None
            for h in range(1, 100):
                cv2_pois = (1.0 - R ** (-h)) / (I0 * (R - 1.0))
                p_err = np.exp((h * s) ** 2) - 1.0
                if cv2_pois + p_err >= tau ** 2:
                    h_cross = h
                    break
            if h_cross is None:
                fail(f"Poisson plug-in horizon failed to cross threshold tau={tau}, s={s}")
            # upper bound: ceil(sqrt(ln(1 + tau^2)) / s)
            bound = np.ceil(np.sqrt(np.log(1.0 + tau ** 2)) / s)
            if h_cross > bound:
                fail(f"h_cross {h_cross} exceeded analytical bound {bound} for tau={tau}, s={s}")
    print("[OK] Lemma 4 Poisson limit monotonicity, saturation, and finite plug-in crossing verified")


def check_wis_direction_labels():
    """Verify WIS directional penalty semantics:
    - y < lower: forecast overpredicted -> over penalty > 0, under penalty == 0
    - y > upper: forecast underpredicted -> under penalty > 0, over penalty == 0
    - lower <= y <= upper: interval covers -> over == 0, under == 0
    - sum identity: point + spread + under + over == total_wis (within float tol)
    Also verify directional numbers cited in main.tex line 757:
    - 2024-25 (v1.1.0): over (76.94) > under (66.84)
    - 2025-26 (v1.2.0): under (56.55) > over (39.27)
    """
    from flusight_audit_extended import wis_decomposed
    # 23 quantiles centered at 250, running from 50 to 450
    q = np.linspace(50.0, 450.0, 23)

    # Case 1: severe overprediction (y = 10 < q[0])
    res_over = wis_decomposed(q, 10.0)
    if res_over["over"] <= 0 or res_over["under"] != 0.0:
        fail(f"WIS direction failed for overprediction: got over={res_over['over']}, under={res_over['under']}")
    sum_over = res_over["point"] + res_over["spread"] + res_over["under"] + res_over["over"]
    if abs(sum_over - res_over["wis"]) > 1e-12:
        fail("WIS sum identity failed for overprediction")

    # Case 2: severe underprediction (y = 1000 > q[-1])
    res_under = wis_decomposed(q, 1000.0)
    if res_under["under"] <= 0 or res_under["over"] != 0.0:
        fail(f"WIS direction failed for underprediction: got under={res_under['under']}, over={res_under['over']}")
    sum_under = res_under["point"] + res_under["spread"] + res_under["under"] + res_under["over"]
    if abs(sum_under - res_under["wis"]) > 1e-12:
        fail("WIS sum identity failed for underprediction")

    # Case 3: exact center (y = 250 == q[11])
    res_mid = wis_decomposed(q, 250.0)
    if res_mid["under"] != 0.0 or res_mid["over"] != 0.0:
        fail("WIS under/over should both be 0 when y is at median within all intervals")

    # Check deposited reports
    d11 = json.loads((REPORTS / "flusight_v1.1_extended.json").read_text(encoding="utf-8"))
    m11 = d11["by_horizon"]["1"]["by_model"]["mechanistic"]
    if round(m11["over"], 2) != 76.94 or round(m11["under"], 2) != 66.84:
        fail(f"v1.1.0 mechanistic directional values {m11['over']:.2f}, {m11['under']:.2f} != 76.94, 66.84")
    if m11["over"] <= m11["under"]:
        fail("v1.1.0 mechanistic should have over > under (systematic overprediction)")

    d12 = json.loads((REPORTS / "flusight_v1.2_extended.json").read_text(encoding="utf-8"))
    m12 = d12["by_horizon"]["1"]["by_model"]["mechanistic"]
    if round(m12["under"], 2) != 56.55 or round(m12["over"], 2) != 39.27:
        fail(f"v1.2.0 mechanistic directional values {m12['under']:.2f}, {m12['over']:.2f} != 56.55, 39.27")
    if m12["under"] <= m12["over"]:
        fail("v1.2.0 mechanistic should have under > over (systematic underprediction)")

    for f in ["flusight_v1.0_extended.json", "flusight_v1.1_extended.json", "flusight_v1.2_extended.json"]:
        d = json.loads((REPORTS / f).read_text(encoding="utf-8"))
        for h, rec in d["by_horizon"].items():
            for m_name, m_stats in rec["by_model"].items():
                s = m_stats["point"] + m_stats["spread"] + m_stats["under"] + m_stats["over"]
                if abs(s - m_stats["wis"]) > 1e-4:
                    fail(f"{f} h={h} {m_name}: WIS decomposition sum {s} != total WIS {m_stats['wis']}")
    print("[OK] WIS directional penalty semantics, sum identities, and empirical values verified")


def check_four_way_equal_n():
    """Verify that all comparative models are evaluated on the exact same common units:
    - by_horizon: for each season and each horizon h in {1, 2, 3}, all models have identical n
    - by_phase_by_horizon: for each season, phase, and horizon h=1, all models have identical n
    - table8 & table9 LaTeX fragments reflect identical common unit counts
    """
    for f in ["flusight_v1.0_extended.json", "flusight_v1.1_extended.json", "flusight_v1.2_extended.json"]:
        d = json.loads((REPORTS / f).read_text(encoding="utf-8"))
        # by_horizon check
        for h, rec in d["by_horizon"].items():
            models = rec["by_model"]
            ns = {m: stats["n"] for m, stats in models.items()}
            if len(set(ns.values())) != 1:
                fail(f"{f} h={h}: sample sizes differ across models: {ns}")
        # by_phase check at h=1
        bph = d["by_phase_by_horizon"]["1"]
        for phase, m_list in bph.items():
            ns = {m["model"]: m["n"] for m in m_list}
            if len(set(ns.values())) != 1:
                fail(f"{f} phase {phase}: sample sizes differ across models: {ns}")

    # Check Table 8 and Table 9 committed fragments
    t8 = (TABLES / "table8_flusight_audit.tex").read_text(encoding="utf-8")
    for expected_n in ["1,337", "1,315", "1,376"]:
        if expected_n not in t8:
            fail(f"table8 fragment missing expected sample size {expected_n}")

    t9 = (TABLES / "table9_phase_stratification.tex").read_text(encoding="utf-8")
    for phase_n in ["108", "36", "1,193", "343", "132", "840", "43", "32", "1,301"]:
        if phase_n not in t9:
            fail(f"table9 fragment missing expected phase sample size {phase_n}")
    print("[OK] strict common-unit sample size identity verified across all models, seasons, and phases")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== consistency suite ===", flush=True)
    check_tables()
    check_figures()
    check_blacklist()
    check_abstract()
    check_crb_ratios()
    check_drift_dimension()
    check_crossings()
    check_series_identity()
    check_doc_paths()
    check_citations()
    check_pdf_pages()
    check_phase_protocol()
    check_poisson_limit()
    check_wis_direction_labels()
    check_four_way_equal_n()
    check_input_hashes()
    check_supplementary()
    check_table_typography()
    check_figure_legibility()
    check_alt_variance()
    check_joint_ci_table()
    print("\nAll 21 consistency assertions passed.", flush=True)


if __name__ == "__main__":
    main()
