#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, lzma, random, struct, time
from pathlib import Path

from shtenco_math_portfolio_v3 import ShtencoMathExpertV3


def corpus(size: int):
    rng = random.Random(20260801)
    source = (b'def compress(data):\n    return selector.choose(data)\n' * (size // 48 + 2))[:size]
    json_log = (b'{"ts":1720000000,"level":"INFO","route":"p2hf","ok":true}\n' * (size // 64 + 2))[:size]
    repeated = (b'SHTENCO-SYNERGY-P2HF-' * (size // 22 + 2))[:size]
    zeros = bytes(size)
    random_bytes = bytes(rng.randrange(256) for _ in range(size))
    counter = b''.join(struct.pack('>I', i) for i in range((size + 3)//4))[:size]
    cubic = bytes((i**3 + 5*i*i + 17*i + 29) & 255 for i in range(size))
    records = b''.join(i.to_bytes(4,'big') + b'P2HF' + bytes([i & 255])*23 for i in range((size+31)//32))[:size]
    exps=[]; current=size*8-2; gap=3
    while current>10:
        exps.append(current); current-=gap; gap+=2
    sparse=sum(1<<e for e in exps).to_bytes(size,'big')
    top=size*8-1; sub=0; i=0
    while True:
        e=3*i*i+7*i+11
        if e>=top-2: break
        sub|=1<<e; i+=1
    signed=((1<<top)-sub).to_bytes(size,'big')
    mixed=(source[:size//2]+counter[:size-size//2])[:size]
    return {
        'source_code':source,'json_log':json_log,'repeated_text':repeated,'zeros':zeros,
        'random':random_bytes,'counter_u32':counter,'cubic_bytes':cubic,'fixed_records':records,
        'wholeint_sparse_formula':sparse,'p2hf_signed_formula':signed,'mixed_text_numeric':mixed,
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--size',type=int,default=32768); ap.add_argument('--output',default='output_math_v3')
    a=ap.parse_args(); out=Path(a.output); out.mkdir(parents=True,exist_ok=True)
    engines=[ShtencoMathExpertV3('balanced'),ShtencoMathExpertV3('max')]
    rows=[]
    for name,data in corpus(a.size).items():
        t=time.perf_counter(); base=lzma.compress(data,preset=9|lzma.PRESET_EXTREME); base_enc=time.perf_counter()-t
        t=time.perf_counter(); base_restored=lzma.decompress(base); base_dec=time.perf_counter()-t
        base_ok=base_restored==data and hashlib.sha256(base_restored).digest()==hashlib.sha256(data).digest()
        rows.append({'dataset':name,'engine':'LZMA9_EXTREME','archive_bytes':len(base),'ratio':len(data)/len(base),'encode_s':base_enc,'decode_s':base_dec,'mode':'lzma9','pass':base_ok})
        for engine in engines:
            t=time.perf_counter(); archive=engine.compress(data); enc=time.perf_counter()-t
            t=time.perf_counter(); restored=engine.decompress(archive); dec=time.perf_counter()-t
            ok=restored==data and hashlib.sha256(restored).digest()==hashlib.sha256(data).digest()
            rows.append({'dataset':name,'engine':engine.name,'archive_bytes':len(archive),'ratio':len(data)/len(archive),'encode_s':enc,'decode_s':dec,'mode':engine.last_mode,'pass':ok})
            print(name,engine.name,len(archive),engine.last_mode,ok)
    fields=list(rows[0]);
    with (out/'MATH_V3_ROWS.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    summary={}
    for engine in sorted({r['engine'] for r in rows}):
        rr=[r for r in rows if r['engine']==engine]
        summary[engine]={
            'geomean_ratio':math_prod([r['ratio'] for r in rr])**(1/len(rr)),
            'total_bytes':sum(r['archive_bytes'] for r in rr),
            'pass_rows':sum(bool(r['pass']) for r in rr),'row_count':len(rr),
            'total_encode_s':sum(r['encode_s'] for r in rr),'total_decode_s':sum(r['decode_s'] for r in rr),
        }
    report={'size':a.size,'rows':rows,'summary':summary}
    (out/'MATH_V3_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    if any(not r['pass'] for r in rows): raise SystemExit('round-trip failure')


def math_prod(values):
    p=1.0
    for v in values:p*=v
    return p

if __name__=='__main__': main()
