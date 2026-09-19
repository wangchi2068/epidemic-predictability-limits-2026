# -*- coding: utf-8 -*-
"""build_input_hashes.py — SHA-256 manifest for every deposited input file.

Covers all raw inputs used by the empirical pipeline (state-level panels, both
micro transmission-chain cohorts, the COVIDhub historical origins, and the 204
version-locked FluSight files), so that the manuscript's availability statement
can claim byte-level pinning for *all* inputs rather than FluSight alone.

Writes data/input_hashes.json and prints a summary. Re-running is idempotent;
the gate in check_consistency.py re-verifies every entry against disk.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "input_hashes.json"

SKIP_NAMES = {"input_hashes.json", "file_hashes.json"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def main() -> None:
    rows = []
    for p in sorted(DATA.rglob("*")):
        if not p.is_file():
            continue
        if p.name in SKIP_NAMES or p.suffix == ".pyc":
            continue
        rows.append({
            "group": p.relative_to(DATA).parts[0],
            "path": str(p.relative_to(ROOT)).replace("\\", "/"),
            "bytes": p.stat().st_size,
            "sha256": sha256(p),
        })

    OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")

    by_group: dict[str, int] = {}
    for r in rows:
        by_group[r["group"]] = by_group.get(r["group"], 0) + 1
    total_mb = sum(r["bytes"] for r in rows) / 1e6
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"     {len(rows)} files, {total_mb:.1f} MB")
    for g, n in sorted(by_group.items()):
        print(f"       {g:10s} {n:4d} files")


if __name__ == "__main__":
    main()
