"""Check which ref targets have no matching label (would render as ??)."""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
for ver in ["paper_cn", "paper_en"]:
    tex = ROOT / ver / "main.tex"
    s = tex.read_text(encoding="utf-8")
    refs = set(re.findall(r"\\ref\{([^}]+)\}", s))
    labels = set(re.findall(r"\\label\{([^}]+)\}", s))
    undef = sorted(refs - labels)
    print(
        f"{ver}: refs={len(refs)} labels={len(labels)} UNDEFINED: {undef if undef else 'none'}"
    )
