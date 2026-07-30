#!/usr/bin/env python3
"""Federated exact benchmark: frozen 69-system result + current Tier-1 rerun.

Archive-size/ratio rankings are directly comparable because both runs use the
same deterministic 11x32768 corpus. Timing rankings are intentionally separated.
"""
from __future__ import annotations
import argparse,csv,gc,hashlib,json,math,os,platform,statistics,sys,time
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from frozen_tier1_summary import SOURCE_ARTIFACT_SHA256,SOURCE_COMMIT,load_frozen_tier1_summary
from historical_tier1_corpus import SEED,build_corpus
from shtenco_tier1_engines import tier1_engine_suite
from shtenco_tier1_v2 import tier1_v2_engine_suite
MIB=1024*1024

def _sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def _gm(values):
    values=[float(v) for v in values if v is not None and v>0]
    return math.exp(sum(map(math.log,values))/len(values)) if values else 0.0
def _timed(fn,arg):
    gc.collect();gc.disable();start=time.perf_counter_ns()
    try:return fn(arg),(time.perf_counter_ns()-start)/1e6
    finally:gc.enable()
def systems():
    out=[];seen=set()
    for suite in (tier1_engine_suite(),tier1_v2_engine_suite()):
        for name,family,engine in suite:
            if name not in seen:out.append((name,family,engine));seen.add(name)
    return out

def one(name,family,engine,dataset,data,repeats):
    digest=_sha(data)
    try:
        arc=engine.compress(data);rest=engine.decompress(arc)
        if rest!=data or _sha(rest)!=digest:raise ValueError("warm-up exactness failure")
        enc=[];dec=[];sizes=[];hashes=[];modes=[]
        for _ in range(repeats):
            arc,t1=_timed(engine.compress,data);rest,t2=_timed(engine.decompress,arc)
            if rest!=data or _sha(rest)!=digest:raise ValueError("timed exactness failure")
            enc.append(t1);dec.append(t2);sizes.append(len(arc));hashes.append(_sha(arc))
            modes.append(str(getattr(engine,"last_mode","native")))
        size=int(statistics.median(sizes));e=statistics.median(enc);d=statistics.median(dec)
        ratio=len(data)/max(1,size)
        return {"dataset":dataset,"engine":name,"family":family,"status":"PASS","sha256":"PASS",
                "original_bytes":len(data),"compressed_bytes_median":size,"compressed_bytes_min":min(sizes),
                "compressed_bytes_max":max(sizes),"ratio":ratio,"encode_ms_median":e,"decode_ms_median":d,
                "encode_mib_s":(len(data)/MIB)/max(e/1000,1e-12),"decode_mib_s":(len(data)/MIB)/max(d/1000,1e-12),
                "score_ratio_per_ms":ratio/max(e,.001),"balanced_score":ratio/math.sqrt(max(e,.001)*max(d,.001)),
                "archive_deterministic":len(set(hashes))==1,"archive_variation_bytes":max(sizes)-min(sizes),
                "mode":statistics.mode(modes),"repeats":repeats,"measurement_run":"current"}
    except Exception as exc:
        return {"dataset":dataset,"engine":name,"family":family,"status":"FAIL","sha256":"FAIL",
                "original_bytes":len(data),"compressed_bytes_median":None,"ratio":0.0,"encode_ms_median":None,
                "decode_ms_median":None,"score_ratio_per_ms":0.0,"balanced_score":0.0,
                "archive_deterministic":False,"mode":"—","repeats":repeats,"measurement_run":"current",
                "error":f"{type(exc).__name__}: {exc}"}

def summarize(rows,count):
    groups={}
    for row in rows:groups.setdefault(row["engine"],[]).append(row)
    out=[]
    for name,items in groups.items():
        good=[r for r in items if r["status"]=="PASS"]
        out.append({"engine":name,"family":items[0]["family"],"measurement_run":"current",
          "pass":len(good),"total":count,"full_pass":len(good)==count,
          "geomean_ratio":_gm(r["ratio"] for r in good),
          "geomean_encode_ms":_gm(r["encode_ms_median"] for r in good),
          "geomean_decode_ms":_gm(r["decode_ms_median"] for r in good),
          "geomean_score":_gm(r["score_ratio_per_ms"] for r in good),
          "geomean_balanced_score":_gm(r["balanced_score"] for r in good),
          "median_encode_mib_s":statistics.median([r["encode_mib_s"] for r in good]) if good else 0,
          "median_decode_mib_s":statistics.median([r["decode_mib_s"] for r in good]) if good else 0,
          "total_encode_ms":sum(float(r["encode_ms_median"] or 0) for r in good),
          "total_decode_ms":sum(float(r["decode_ms_median"] or 0) for r in good),
          "deterministic_datasets":sum(bool(r.get("archive_deterministic")) for r in good)})
    return out

def ranked(items,key,run=None):
    rows=[r for r in items if r.get("full_pass") and r.get("family")!="REFERENCE"]
    if run:rows=[r for r in rows if r.get("measurement_run")==run]
    return sorted(rows,key=lambda r:float(r.get(key) or 0),reverse=True)
def write_csv(path,rows):
    keys=sorted({k for r in rows for k in r})
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def table(title,items,metric):
    lines=[f"## {title}","","| Rank | Engine | Run | Ratio | Metric | Encode ms |","|---:|---|---|---:|---:|---:|"]
    for i,r in enumerate(items[:10],1):
        lines.append(f"| {i} | {r['engine']} | {r.get('measurement_run')} | {r['geomean_ratio']:.6f}× | {r[metric]:.6f} | {r['total_encode_ms']:.3f} |")
    return lines+[""]

def main():
    p=argparse.ArgumentParser();p.add_argument("--size",type=int,default=32768);p.add_argument("--repeats",type=int,default=3)
    p.add_argument("--output",type=Path,default=HERE/"output_unified_tier1_v2");a=p.parse_args()
    if a.size!=32768:raise SystemExit("frozen comparison requires --size 32768")
    corpus=build_corpus(a.size);suite=systems();rows=[]
    for dataset,data in corpus.items():
        print(f"\n=== {dataset}: {len(data):,} bytes SHA256={_sha(data)} ===",flush=True)
        for name,family,engine in suite:
            row=one(name,family,engine,dataset,data,a.repeats);rows.append(row)
            print(("PASS" if row["status"]=="PASS" else "FAIL"),name,
                  f"ratio={row['ratio']:.4f}",f"ms={row.get('encode_ms_median')}",flush=True)
    frozen=load_frozen_tier1_summary();meta=frozen["metadata"]
    if meta["dataset_size"]!=a.size or meta["dataset_count"]!=len(corpus) or meta["pass_rows"]!=meta["row_count"]:
        raise RuntimeError("frozen baseline integrity/dimensions mismatch")
    current=summarize(rows,len(corpus));names={r["engine"] for r in current}
    old=[]
    for item in frozen["summary"]:
        if item["engine"] not in names:
            item=dict(item);item["measurement_run"]="frozen-20260730";old.append(item)
    combined=old+current;ratio=ranked(combined,"geomean_ratio");score=ranked(combined,"geomean_score","current")
    balanced=ranked(combined,"geomean_balanced_score","current")
    frozen_score=ranked([{**r,"measurement_run":"frozen-20260730"} for r in frozen["summary"]],"geomean_score")
    report={"schema":"shtenco-unified-tier1-v2-federated","seed":SEED,"source_commit":SOURCE_COMMIT,
      "source_artifact_sha256":SOURCE_ARTIFACT_SHA256,"frozen_system_count":meta["system_count"],
      "current_system_count":len(current),"system_count":len(combined),"dataset_count":len(corpus),
      "dataset_size":a.size,"repeats":a.repeats,"current_row_count":len(rows),
      "current_pass_rows":sum(r["status"]=="PASS" for r in rows),"current_rows":rows,
      "current_summary":current,"summary":combined,"frozen_dataset_winners":frozen.get("dataset_winners",[]),
      "environment":{"utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"python":sys.version,
                     "platform":platform.platform(),"cpu_count":os.cpu_count()},
      "timing_note":"frozen/current speed rankings are separate; combined ratio uses identical corpus bytes"}
    top_ratio=sum(r["engine"].startswith("SHTENCO") for r in ratio[:5]);top_score=sum(r["engine"].startswith("SHTENCO") for r in score[:5])
    lines=["# SHTENCO Unified Tier-1 v2 Results","",f"- Frozen systems: **{meta['system_count']}**",
      f"- Current rerun: **{len(current)}**",f"- Combined unique systems: **{len(combined)}**",
      f"- Current exact rows: **{report['current_pass_rows']}/{report['current_row_count']}**",
      f"- SHTENCO in ratio TOP-5: **{top_ratio}**",f"- SHTENCO in current score TOP-5: **{top_score}**","",
      "Archive-size rankings are directly comparable. Timing rankings are separated by run.",""]
    lines+=table("Combined TOP-10 by compression ratio",ratio,"geomean_ratio")
    lines+=table("Current TOP-10 by ratio / encode-time",score,"geomean_score")
    lines+=table("Current TOP-10 by balanced score",balanced,"geomean_balanced_score")
    lines+=table("Frozen 69-system TOP-10 by original score",frozen_score,"geomean_score")
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/"all_systems_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True),encoding="utf-8")
    write_csv(a.output/"current_systems_rows.csv",rows);write_csv(a.output/"combined_systems_summary.csv",combined)
    (a.output/"UNIFIED_TIER1_FINDINGS.md").write_text("\n".join(lines),encoding="utf-8")
    positions={"system_count":len(combined),"dataset_count":len(corpus),"current_row_count":len(rows),
      "current_pass_rows":report["current_pass_rows"],"source_commit":SOURCE_COMMIT,
      "source_artifact_sha256":SOURCE_ARTIFACT_SHA256,"combined_ratio":ratio[:20],"current_score":score[:20],
      "current_balanced":balanced[:20],"frozen_score":frozen_score[:20]}
    (a.output/"UNIFIED_TIER1_POSITIONS.json").write_text(json.dumps(positions,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\n"+"\n".join(lines),flush=True)
if __name__=="__main__":main()
