#!/usr/bin/env python3
"""Actual third-party system logs vs native SHTENCO codecs. Never use generated fixtures."""
import csv, hashlib, json, math, os, platform, statistics, sys, time, urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from shtenco_tier1_engines import tier1_engine_suite
from shtenco_tier1_v21 import tier1_v21_engine_suite
import brotli, zstandard as zstd, bz2, lzma, zlib, lz4.frame

# Small REAL captured log extracts published by LogPAI/Loghub. This is not a
# claim of access to private production data center data or entire 1+ GiB logs.
LOGS={
 "HDFS":"https://raw.githubusercontent.com/logpai/loghub/master/HDFS/HDFS_2k.log",
 "BGL":"https://raw.githubusercontent.com/logpai/loghub/master/BGL/BGL_2k.log",
 "OpenStack":"https://raw.githubusercontent.com/logpai/loghub/master/OpenStack/OpenStack_2k.log",
 "Hadoop":"https://raw.githubusercontent.com/logpai/loghub/master/Hadoop/Hadoop_2k.log",
 "Spark":"https://raw.githubusercontent.com/logpai/loghub/master/Spark/Spark_2k.log",
 "Zookeeper":"https://raw.githubusercontent.com/logpai/loghub/master/Zookeeper/Zookeeper_2k.log",
 "Linux":"https://raw.githubusercontent.com/logpai/loghub/master/Linux/Linux_2k.log",
}
LIMIT=131072
def sha(x):return hashlib.sha256(x).hexdigest()
def gm(xs):return math.exp(statistics.mean(math.log(x) for x in xs))
def codec(name,enc,dec):return (name,"WORLD",enc,dec)
def main():
 out=Path(os.getenv("BENCH_OUTPUT","compression_lab/real_datacenter_20261020"))
 out.mkdir(parents=True,exist_ok=True)
 samples={}
 manifest=[]
 for name,url in LOGS.items():
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"SYNERGY-Exact-Compression-Benchmark/1"})
   with urllib.request.urlopen(req,timeout=40) as response: data=response.read(LIMIT+1)
   data=data[:LIMIT]
   if len(data)<1024 or b"\n" not in data:raise ValueError("unexpectedly small/non-log content")
   samples[name]=data
   manifest.append({"dataset":name,"source":url,"sample_bytes":len(data),"sha256":sha(data),"sampling":"first 131072 bytes, no modification"})
  except Exception as e:
   manifest.append({"dataset":name,"source":url,"status":"DOWNLOAD_FAILED","error":str(e)})
 (out/"corpus_manifest.json").write_text(json.dumps(manifest,indent=2))
 if len(samples)<3:raise RuntimeError("Less than three real-world datasets downloaded; refusing synthetic substitution")
 native={}
 for suite in (tier1_engine_suite(),tier1_v21_engine_suite()):
  for name,family,engine in suite:native[name]=(family,engine)
 engines=[(name,fam,obj.compress,obj.decompress) for name,(fam,obj) in native.items()]
 c=zstd.ZstdCompressor(level=3);d=zstd.ZstdDecompressor()
 engines.extend([
  codec("Brotli-5",lambda x:brotli.compress(x,quality=5),brotli.decompress),
  codec("Brotli-11",lambda x:brotli.compress(x,quality=11),brotli.decompress),
  codec("Zstd-3",c.compress,d.decompress),
  codec("Zstd-19",zstd.ZstdCompressor(level=19).compress,d.decompress),
  codec("zlib-6",lambda x:zlib.compress(x,6),zlib.decompress),
  codec("xz-6",lambda x:lzma.compress(x,preset=6),lzma.decompress),
  codec("bzip2-9",lambda x:bz2.compress(x,compresslevel=9),bz2.decompress),
  codec("LZ4",lz4.frame.compress,lz4.frame.decompress)])
 rows=[]
 for name,fam,enc,dec in engines:
  for dataset,data in samples.items():
   start=time.perf_counter()
   try:
    t=time.perf_counter();archive=enc(data);enc_s=time.perf_counter()-t
    t=time.perf_counter();plain=dec(archive);dec_s=time.perf_counter()-t
    if plain!=data or sha(plain)!=sha(data):raise ValueError("exact roundtrip mismatch")
    row={"engine":name,"family":fam,"dataset":dataset,"status":"PASS","bytes_original":len(data),"bytes_archive":len(archive),"ratio":len(data)/len(archive),"encode_ms":enc_s*1000,"decode_ms":dec_s*1000,"sha256":sha(data)}
   except Exception as exc:
    row={"engine":name,"family":fam,"dataset":dataset,"status":"FAIL","error":repr(exc)}
   rows.append(row);print(name,dataset,row["status"],row.get("ratio"),flush=True)
 def save(path,records):
  fields=list(dict.fromkeys(k for row in records for k in row))
  with open(path,"w",newline="") as file:
   w=csv.DictWriter(file,fieldnames=fields);w.writeheader();w.writerows(records)
 save(out/"per_file.csv",rows)
 summaries=[]
 for name,fam,_,_ in engines:
  rr=[r for r in rows if r["engine"]==name]
  passed=[r for r in rr if r["status"]=="PASS"]
  summaries.append({"engine":name,"family":fam,"pass":len(passed),"total":len(samples),
   "geomean_ratio":gm([r["ratio"] for r in passed]) if len(passed)==len(samples) else "",
   "aggregate_ratio":sum(r["bytes_original"] for r in passed)/sum(r["bytes_archive"] for r in passed) if len(passed)==len(samples) else ""})
 save(out/"summary.csv",summaries)
 clean=sorted([x for x in summaries if x["pass"]==x["total"]],key=lambda x:-x["geomean_ratio"])
 md=["# Native SHTENCO vs global codecs on captured system logs","",
     "**Fresh execution only:** no historical 76-engine figures mixed into the new leaderboard.","",
     "Sources: [Loghub](https://github.com/logpai/loghub). These are genuine captured-log **small samples**, not full production storage traces; some originate from laboratory systems. Every downloaded file has a URL, byte count and SHA-256 in corpus_manifest.json.",
     "",f"Executed: {len(engines)} profiles, {len(samples)} datasets, {len(rows)} rows.","",
     "| Engine | Family | Exact | Geomean ratio | Aggregate ratio |","|---|---|---:|---:|---:|"]
 for x in clean:md.append(f"| {x['engine']} | {x['family']} | {x['pass']}/{x['total']} | {x['geomean_ratio']:.4f}× | {x['aggregate_ratio']:.4f}× |")
 md.extend(["","Profiles with any FAIL (excluded from leaderboard):",""])
 for x in summaries:
  if x["pass"]!=x["total"]:md.append(f"- {x['engine']}: {x['pass']}/{x['total']}")
 md+=["","**Method:** SHA-256 and exact byte equality after decompression; archive includes all codec headers; one run (speed exploratory only); no training; whole-sample first 128 KiB truncation without mutation. The 76 historical SHTENCO names are not 76 currently runnable implementations.","",
 "Full data: [per_file.csv](per_file.csv), [summary.csv](summary.csv), [corpus_manifest.json](corpus_manifest.json)."]
 (out/"README.md").write_text("\n".join(md)+"\n")
 print(json.dumps({"native":len(native),"world":len(engines)-len(native),"files":len(samples),"rows":len(rows),"pass":sum(x["status"]=="PASS" for x in rows)}))
if __name__=="__main__":main()
