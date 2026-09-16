# -*- coding: utf-8 -*-
"""Fetch a locked FluSight release snapshot for the versioned external audit.

Only two model directories are pulled -- the official ensemble and the official
baseline -- plus the final-vintage target file the hub ships in the same tag.
Every downloaded byte is hashed so the audit can be replayed from the tag alone.

The release tag is a full-repository snapshot: a later tag also contains the
earlier seasons.  We therefore filter by reference-date prefix so each local
directory holds exactly the season it audits.

Usage:
    python scripts_v2/fetch_flusight_release.py \
        --tag v1.2.0 --commit 18f68c23af1926e4808ee703221bea9fcb8befd6 \
        --date-prefix 2025- 2026- \
        --out data/flusight/v1.2.0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

REPO = "cdcepi/FluSight-forecast-hub"
# The hub names the directories FluSight-ensemble / FluSight-baseline; the audit
# scorer expects the short local names used by the v1.0.0 and v1.1.0 snapshots.
MODELS = {"FluSight-ensemble": "ensemble", "FluSight-baseline": "baseline"}
TARGET = "target-data/target-hospital-admissions.csv"


def _get(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()


def _tree(commit: str) -> list[dict]:
    url = f"https://api.github.com/repos/{REPO}/git/trees/{commit}?recursive=1"
    payload = json.loads(_get(url))
    if payload.get("truncated"):
        raise RuntimeError("GitHub tree listing was truncated; refusing a partial fetch")
    return payload["tree"]


def _raw(tag: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{REPO}/{tag}/{path}"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def fetch(tag: str, commit: str, prefixes: list[str], out: Path) -> list[dict]:
    blobs = [e["path"] for e in _tree(commit) if e.get("type") == "blob"]
    wanted = []
    for model in MODELS:
        stem = f"model-output/{model}/"
        wanted.extend(
            p for p in blobs
            if p.startswith(stem) and any(Path(p).name.startswith(pre) for pre in prefixes)
        )
    out.mkdir(parents=True, exist_ok=True)

    record = [(TARGET, out / "target-hospital-admissions.csv")]

    for path in sorted(wanted):
        payload = _get(_raw(tag, path))
        dest = out / MODELS[path.split("/")[1]] / Path(path).name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(payload)
        record.append((path, dest))

    manifest = []
    for path, dest in record:
        payload = dest.read_bytes()
        manifest.append({
            "release": tag,
            "path": str(dest).replace("\\", "/"),
            "source_path": path,
            "sha256": _sha256(payload),
            "bytes": len(payload),
        })
        print(f"{_sha256(payload)[:12]}  {len(payload):>9}  {dest}")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--date-prefix", nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path,
                        default=Path("data/flusight/file_hashes.json"))
    args = parser.parse_args()

    manifest = fetch(args.tag, args.commit, args.date_prefix, args.out)

    existing = json.loads(args.manifest.read_text(encoding="utf-8"))
    keep = [e for e in existing if e["release"] != args.tag]
    merged = keep + manifest
    merged.sort(key=lambda e: (e["release"], e["path"]))
    args.manifest.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print(f"\n{len(manifest)} files for {args.tag}; manifest now {len(merged)} entries")


if __name__ == "__main__":
    main()
