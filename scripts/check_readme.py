#!/usr/bin/env python3
"""Readme integrity checker; standard library only."""
from pathlib import Path
import re, xml.etree.ElementTree as ET, sys
root=Path(__file__).resolve().parents[1]
text=(root/'README.md').read_text(encoding='utf-8')
paths=set(re.findall(r'(?:src|href)="([^"]+)"',text))
paths.update(re.findall(r'\]\(([^)#]+)(?:#[^)]+)?\)',text))
missing=[];images=0
for p in paths:
 if p.startswith(('http://','https://','#','mailto:','data:')):continue
 pp=root/p
 if not pp.exists():missing.append(p);continue
 if pp.suffix=='.svg':ET.parse(pp);images+=1
if missing:print('BROKEN LINKS:',missing);sys.exit(1)
print(f'README CHECK PASS: {len(paths)} internal/external references, {images} SVG references')