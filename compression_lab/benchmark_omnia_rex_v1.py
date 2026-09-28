#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,lzma,math,time,zlib
from pathlib import Path
import brotli

try: import zstandard as zstd
except Exception: zstd=None

HERE=Path(__file__).resolve().parent
import sys
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))

from historical_tier1_corpus import SEED, build_corpus
from omnia_rex_v1 import OmniaREXV1
from shtenco_tier1_engines import tier1_engine_suite
from shtenco_tier1_v21 import tier1_v21_engine_suite
try:
    from shtenco_math_portfolio_v3 import math_v3_engine_suite
except Exception:
    math_v3_engine_suite=lambda:[]

def gm(vals):
    vals=[x for x in vals if x>0]
    return math.exp(sum(math.log(x) for x in vals)/len(vals)) if vals else 0.0

def standard_suite():
    out=[
      ("RAW","BASELINE",type("E",(),{"compress":staticmethod(lambda d:d),"decompress":staticmethod(lambda d:d)})()),
      ("zlib-9","BASELINE",type("E",(),{"compress":staticmethod(lambda d:zlib.compress(d,9)),"decompress":staticmethod(zlib.decompress)})()),
      ("LZMA-9-EXTREME","BASELINE",type("E",(),{"compress":staticmethod(lambda d:lzma.compress(d,preset=9|lzma.PRESET_EXTREME)),"decompress":staticmethod(lzma.decompress)})()),
      ("Brotli-11","BASELINE",type("E",(),{"compress":staticmethod(lambda d:brotli.compress(d,quality=11)),"decompress":staticmethod(brotli.decompress)})()),
    ]
    if zstd is not None:
        zc=zstd.ZstdCompressor(level=22,write_checksum=True,write_content_size=True)
        zd=zstd.ZstdDecompressor()
        out.append(("Zstd-22","BASELINE",type("E",(),{"compress":staticmethod(zc.compress),"decompress":staticmethod(zd.decompress)})()))
    return out

def suites():
    out=[]; seen=set()
    rex=OmniaREXV1()
    for suite in (
        standard_suite(),
        tier1_engine_suite(),
        tier1_v21_engine_suite(),
        math_v3_engine_suite(),
        [(rex.name,rex.family,rex)]
    ):
        for name,fam,e in suite:
            if name not in seen:
                seen.add(name); out.append((name,fam,e))
    return out

def one(name,fam,e,dataset,data):
    h=hashlib.sha256(data).digest()
    t=time.perf_counter(); arc=e.compress(data); enc=time.perf_counter()-t
    t=time.perf_counter(); restored=e.decompress(arc); dec=time.perf_counter()-t
    if restored!=data or hashlib.sha256(restored).digest()!=h:
        raise RuntimeError("roundtrip")
    return {
      "dataset":dataset,"engine":name,"family":fam,"status":"PASS",
      "original_bytes":len(data),"compressed_bytes":len(arc),
      "ratio":len(data)/max(1,len(arc)),
      "encode_s":enc,"decode_s":dec,
      "mode":str(getattr(e,"last_mode","native"))
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--size",type=int,default=32768)
    ap.add_argument("--output",type=Path,default=HERE/"output_omnia_rex_v1")
    args=ap.parse_args()
    if args.size!=32768:
        raise SystemExit("frozen OMNIA comparison requires --size 32768")

    corpus=build_corpus(args.size); rows=[]; suite=suites()
    for ds,data in corpus.items():
        print("===",ds,len(data),flush=True)
        for name,fam,e in suite:
            try:
                r=one(name,fam,e,ds,data); rows.append(r)
                print("PASS",name,r["compressed_bytes"],f'{r["ratio"]:.4f}x',r["mode"],flush=True)
            except Exception as ex:
                rows.append({"dataset":ds,"engine":name,"family":fam,"status":"FAIL","error":repr(ex),"ratio":0,"original_bytes":len(data),"compressed_bytes":None})
                print("FAIL",name,ex,flush=True)

    summary=[]
    for name,fam,_ in suite:
        rr=[r for r in rows if r["engine"]==name and r["status"]=="PASS"]
        summary.append({
          "engine":name,"family":fam,"pass":len(rr),"total":len(corpus),
          "full_pass":len(rr)==len(corpus),
          "geomean_ratio":gm([r["ratio"] for r in rr]),
          "total_bytes":sum(r["compressed_bytes"] for r in rr),
          "total_encode_s":sum(r.get("encode_s",0) for r in rr),
        })
    summary.sort(key=lambda x:x["geomean_ratio"] if x["full_pass"] else -1,reverse=True)

    out={
      "schema":"omnia-rex-v1-frozen-multicorpus",
      "seed":SEED,"dataset_count":len(corpus),"dataset_size":args.size,
      "rows":rows,"summary":summary,
      "qtd3_note":"QTD3 is a separate shared-model track; model bytes/cold totals are not hidden inside the standalone ranking."
    }
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/"omnia_rex_v1.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    keys=sorted({k for r in rows for k in r})
    with (args.output/"omnia_rex_v1_rows.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rows)

    print("\nTOP")
    for i,x in enumerate(summary[:15],1):
        print(i,x["engine"],x["geomean_ratio"],x["pass"])

if __name__=="__main__":
    main()
