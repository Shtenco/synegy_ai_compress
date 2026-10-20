#!/usr/bin/env python3
"""Validate this documentation bundle and stable benchmark constants.
Does not claim to run the original codec benchmarks.
"""
from pathlib import Path
import csv, re, xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
readme=(root/'README.md').read_text(encoding='utf-8')
assert len(readme)>12000
paths=[]
for x,y in re.findall(r'(?:src="([^\"]+)"|\]\(([^)]+)\))',readme):
 z=x or y
 if z.startswith(('http://','https://','mailto:','#')):continue
 z=z.split('#')[0]
 if z:paths.append(z)
missing=[]
for p in paths:
 if (root/p).exists():continue
 if p.startswith(('compression_lab/','benchmarks/','.github/workflows/')) or p=='LICENSE' or p=='MIGRATION_MANIFEST.md' or p=='docs/TECHNOLOGY_FAMILY_RU.md' or p=='docs/BENCHMARKS_EXPLAINED_RU.md' or p=='docs/VALIDATION_AND_CLAIMS_RU.md' or p=='docs/EAES_GLOBAL_MARKET_RU.md' or p=='docs/ROADMAP_RU.md':continue
 missing.append(p)
assert not missing,missing
for svg in (root/'assets/readme').glob('*.svg'):ET.parse(svg)
def rows(name):
 with (root/'data'/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
a=rows('GABRIEL_CORPUS_FULL_PER_DATASET_20260730.csv')
assert len(a)==11
assert sum(int(q['source_bytes']) for q in a)==139762
assert [sum(int(q[k]) for q in a) for k in ('brotli11_bytes','gabriel_max_bytes','umc256_max_bytes','graal_igc_max_bytes','zstd19_bytes','raw_bytes')]==[33728,35372,35983,36483,36813,139762]
assert len(rows('UNIFIED_TIER1_TOP10_RATIO_20260730.csv'))==10
assert len(rows('UNIFIED_TIER1_TOP10_SPEED_SCORE_20260730.csv'))==10
assert '30.335995' in readme and '33 728' in readme
print(f'PASS: README, {len(list((root/"assets/readme").glob("*.svg")))} SVG, {len(paths)} links, 11x6 source math, two TOP-10')