#!/usr/bin/env python3
"""Independent baseline benchmark on the exact SHTENCO deterministic 20260730 corpus.
Built from the repository's historical_tier1_corpus.py generator.
This file benchmarks only the STANDARD codecs available in the execution environment.
It DOES NOT substitute for rerunning the historical 69 SHTENCO engines.
"""
import argparse, bz2, csv, gc, hashlib, json, lzma, math, os, platform, random, statistics, subprocess, time, zlib
from pathlib import Path
import brotli
import blosc2
import lz4.frame

SEED=20260730

def _repeat(s:bytes,n:int)->bytes: return (s*(n//len(s)+1))[:n] if s else bytes(n)
def build_corpus(size:int=32768):
    rng=random.Random(SEED)
    code_seed=b'''\nclass GraphAIArchive:\n    def encode_node(self, node, graph):\n        route = node.simhash & 255\n        community = graph.communities[route]\n        parent = community.nearest(node)\n        return parent.xor_patch(node)\n\n    def verify(self, restored, source):\n        return sha256(restored).digest() == sha256(source).digest()\n'''
    source_code=_repeat(code_seed,size)
    records=[json.dumps({'timestamp':1700000000+i,'node':i%97,'route':(i*29)%256,'community':(i*7)%31,'event':'graph-edge-verification','status':'PASS' if i%19 else 'WARN','value':round(math.sin(i/17),10)},separators=(',',':')) for i in range(max(256,size//70))]
    json_logs=_repeat(('\n'.join(records)+'\n').encode(),size)
    csv_seed='time,node,route,price,volume,status\n'+''.join(f"{i},{i%43},{(i*17)%256},{100+math.sin(i/23):.8f},{1000+i%211},{'ok' if i%13 else 'warn'}\n" for i in range(max(512,size//40)))
    telemetry=_repeat(csv_seed.encode(),size)
    repeated=_repeat(b'SHTENCO-GRAPH-AI-SABF-X-EGD-256-HACE-X\0'*32,size)
    base=bytes((i*13+7)&255 for i in range(1024));versions=[]
    for version in range(max(32,size//len(base))):
        block=bytearray(base)
        for edit in range(1+version%11):block[(version*37+edit*101)%len(block)]^=(version+edit+1)&255
        versions.append(bytes(block))
    snapshots=_repeat(b''.join(versions),size)
    sparse=bytearray(size)
    for i in range(0,size,89):sparse[i]=rng.randrange(1,256)
    structured=bytearray()
    for i in range(max(512,size//16)):
        structured+=i.to_bytes(4,'little')
        structured+=((i*17)%100000).to_bytes(4,'little')
        structured+=int(1_000_000+1000*math.sin(i/21)).to_bytes(8,'little',signed=True)
    structured=bytes(structured[:size]).ljust(size,b'\0')
    image=bytearray();side=max(32,int(math.sqrt(size)))
    for y in range(side+1):
        for x in range(side+1):image.append(((x//8)*11+(y//8)*7+((x+y)//32))&255)
    image_like=_repeat(bytes(image),size)
    words=('abandon ability able about above absent absorb abstract absurd abuse access accident '
          'account accuse achieve acid acoustic acquire across act action actor actress actual adapt ').encode()
    bip39=_repeat(words,size)
    random_bytes=bytes(rng.randrange(256) for _ in range(size))
    fifth=size//5
    mixed=source_code[:fifth]+json_logs[:fifth]+structured[:fifth]+snapshots[:fifth]+random_bytes[:size-4*fifth]
    return {'source_code':source_code,'json_graph_logs':json_logs,'telemetry_csv':telemetry,'repeated_text':repeated,'version_snapshots':snapshots,'sparse_weights':bytes(sparse),'structured_binary':structured,'image_like':image_like,'bip39_text':bip39,'mixed':mixed,'random':random_bytes}

def codec_specs():
    out=[]
    def add(name,fam,fn,dn):out.append((name,fam,fn,dn))
    for level in [0,1,3,6,9]:add(f'ZLIB-{level}','zlib',lambda x,L=level:zlib.compress(x,L),zlib.decompress)
    for level in [1,3,6,9]:add(f'BZ2-{level}','bzip2',lambda x,L=level:bz2.compress(x,compresslevel=L),bz2.decompress)
    for level in [0,3,6,9]:add(f'LZMA-XZ-{level}','lzma',lambda x,L=level:lzma.compress(x,preset=L,format=lzma.FORMAT_XZ),lzma.decompress)
    for level in [0,1,3,5,7,9,11]:add(f'BROTLI-{level}','brotli',lambda x,L=level:brotli.compress(x,quality=L),brotli.decompress)
    for level in [1,3,6,9,12,15,19,22]:
        def zc(x,L=level):
            p=subprocess.run(['zstd',f'-{L}','--stdout','--no-progress','--quiet'],input=x,capture_output=True,check=True)
            return p.stdout
        def zd(x):return subprocess.run(['zstd','--decompress','--stdout','--quiet'],input=x,capture_output=True,check=True).stdout
        add(f'ZSTD-{level}','zstd',zc,zd)
    for level in [0,1,3,9,12]:add(f'LZ4-FRAME-{level}','lz4',lambda x,L=level:lz4.frame.compress(x,compression_level=L),lz4.frame.decompress)
    for level in [1,3,6,9]:add(f'BLOSC2-ZSTD-{level}','blosc2',lambda x,L=level:blosc2.compress(x,typesize=1,clevel=L,codec=blosc2.Codec.ZSTD),blosc2.decompress)
    add('RAW','none',lambda x:x,lambda x:x)
    return out

def run(output, repeats=3):
    corpus=build_corpus()
    out=[];specs=codec_specs()
    for idx,(name,family,compress,decompress) in enumerate(specs,1):
        for dname,raw in corpus.items():
            a=[];z=[];encoded=[];passed=True;error=''
            try:
                warm=compress(raw)
                if decompress(warm)!=raw:raise ValueError('warmup not exact')
                for j in range(repeats):
                    gc.collect(); t=time.perf_counter_ns();arc=compress(raw);a.append((time.perf_counter_ns()-t)/1e6)
                    t=time.perf_counter_ns();dec=decompress(arc);z.append((time.perf_counter_ns()-t)/1e6)
                    if dec!=raw or hashlib.sha256(dec).digest()!=hashlib.sha256(raw).digest():raise ValueError('roundtrip not exact')
                    encoded.append(arc)
                if len(set(map(hashlib.sha256,encoded)))!=1:raise ValueError('non-deterministic archive')
                arc=encoded[0]
            except Exception as exc:
                passed=False;error=repr(exc);arc=b''
            out.append(dict(profile=name,family=family,dataset=dname,original_bytes=len(raw),archive_bytes=len(arc) if passed else None,ratio=len(raw)/len(arc) if passed else None,encode_ms_median=statistics.median(a) if a else None,decode_ms_median=statistics.median(z) if z else None,lossless_sha256_pass=passed,source_sha256=hashlib.sha256(raw).hexdigest(),archive_sha256=hashlib.sha256(arc).hexdigest() if passed else '',error=error,run_class='FRESH_EXECUTED_STANDARDS',measurement_repetitions=repeats))
        print(idx,'/',len(specs),name,flush=True)
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    with (output/'fresh_world_38_profiles_x11.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=out[0]);w.writeheader();w.writerows(out)
    summary=[]
    for name,family,_,_ in specs:
        subset=[x for x in out if x['profile']==name]
        ok=all(x['lossless_sha256_pass'] for x in subset)
        summary.append(dict(profile=name,family=family,data_count=len(subset),passed=sum(x['lossless_sha256_pass'] for x in subset),geometric_mean_ratio=math.exp(sum(math.log(x['ratio']) for x in subset)/len(subset)) if ok else None,total_input_bytes=sum(x['original_bytes'] for x in subset),total_archive_bytes=sum(x['archive_bytes'] for x in subset) if ok else None,sum_encode_ms=sum(x['encode_ms_median'] for x in subset if x['encode_ms_median'] is not None),sum_decode_ms=sum(x['decode_ms_median'] for x in subset if x['decode_ms_median'] is not None),ratio_aggregate=sum(x['original_bytes'] for x in subset)/sum(x['archive_bytes'] for x in subset) if ok else None,status='PASS' if ok else 'FAIL',run_class='FRESH_EXECUTED_STANDARDS'))
    summary.sort(key=lambda x:x['geometric_mean_ratio'] or 0,reverse=True)
    with (output/'fresh_world_38_summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=summary[0]);w.writeheader();w.writerows(summary)
    obj=dict(schema_version='1.0',date_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),seed=SEED,corpus_count=len(corpus),bytes_per_dataset=32768,profiles=len(specs),round_trip_rows=sum(x['lossless_sha256_pass'] for x in out),attempted_rows=len(out),python=platform.python_version(),machine=platform.machine(),system=platform.system(),library_versions={'brotli':getattr(brotli,'__version__','unknown'),'blosc2':getattr(blosc2,'__version__','unknown')},scope_note='Fresh STANDARD codec profiles ONLY; historical SHTENCO engine records are separate and must not be mixed as freshly run.',data_sha256={k:hashlib.sha256(v).hexdigest() for k,v in corpus.items()})
    (output/'environment.json').write_text(json.dumps(obj,indent=2,ensure_ascii=False))
    return summary,obj
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='results');ap.add_argument('--repeats',type=int,default=3);ns=ap.parse_args();sm,meta=run(ns.out,ns.repeats);print(json.dumps(meta,indent=2));print('TOP',[(x['profile'],round(x['geometric_mean_ratio'],4)) for x in sm[:10]])