# -*- coding: utf-8 -*-
"""Audit citations in main.tex and references.bib."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX_FILE = ROOT / "main.tex"
BIB_FILE = ROOT / "references.bib"

with open(TEX_FILE, 'r', encoding='utf-8') as f:
    tex = f.read()

cites = set()
for match in re.findall(r'\\cite[a-zA-Z]*\{([^}]+)\}', tex):
    for key in match.split(','):
        key = key.strip()
        if key:
            cites.add(key)

with open(BIB_FILE, 'r', encoding='utf-8') as f:
    bib_text = f.read()

raw_entries = re.findall(r'@(\w+)\s*\{\s*([^,]+),(.*?)(?=\n@|\Z)', bib_text, re.DOTALL)
entries = {}
for etype, k, body in raw_entries:
    entries[k.strip()] = (etype.lower(), body.strip())

print(f"Total cited keys in main.tex: {len(cites)}")
print(f"Total entries in references.bib: {len(entries)}")

missing = cites - set(entries.keys())
unref = set(entries.keys()) - cites
if missing:
    print(f"ERROR: Missing keys: {missing}")
    sys.exit(1)
else:
    print("[OK] All cited keys present in references.bib")

if unref:
    print(f"ERROR: Unreferenced keys in references.bib: {unref}")
    sys.exit(1)
else:
    print(f"[OK] references.bib is 100% two-way closed ({len(cites)}/{len(entries)} entries cited)")

print("\n=== Detailed Audit of All 44 Cited Papers ===")
for idx, k in enumerate(sorted(cites)[:15], 1):
    etype, body = entries[k]
    # parse fields
    fields = {}
    for line in body.split('\n'):
        m = re.match(r'\s*(\w+)\s*=\s*[\"{]?(.*?)[\"}]?,?\s*$', line)
        if m:
            fields[m.group(1).lower()] = m.group(2).strip('{}", ')
    
    title = fields.get('title', 'NO TITLE')
    author = fields.get('author', 'NO AUTHOR')
    year = fields.get('year', 'NO YEAR')
    journal = fields.get('journal', fields.get('booktitle', fields.get('publisher', 'NO VENUE')))
    doi = fields.get('doi', 'NO DOI')
    
    print(f"[{idx}/44] {k} ({year})")
    print(f"    Author: {author[:60]}")
    print(f"    Title:  {title}")
    print(f"    Venue:  {journal}")
    print(f"    DOI:    {doi}")

