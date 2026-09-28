#!/usr/bin/env python3
"""OMNIA-REX V1 — verified predictive/residual meta-codec.

Every candidate is decoded and checked before it can win. The standalone
leaderboard never treats a shared QTD model as free; shared-model experiments
belong to a separate track with model/cold-total accounting.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, lzma, math, struct, zlib
from typing import Any
import brotli

try:
    import zstandard as zstd
except Exception:
    zstd = None

try:
    from . import omnia_rex_ppm as ppm
    from . import omnia_rex_bwt as bwt
except ImportError:
    import omnia_rex_ppm as ppm
    import omnia_rex_bwt as bwt

MAGIC=b"ORX1"; VERSION=1
HEADER=struct.Struct(">4sBBQ32s")
R_RAW=0; R_ZLIB=1; R_LZMA=2; R_BROTLI=3; R_ZSTD=4
R_PPM4=10; R_PPM6=11; R_PPM8=12; R_BWT=13
R_SP_SPARSE=14; R_SP_BROTLI=15
R_OMNIA=30; R_GABRIEL=31; R_MATH=32

@dataclass(frozen=True)
class Candidate:
    route:int
    name:str
    archive:bytes
    family:str="builtin"

@dataclass(frozen=True)
class Features:
    entropy:float
    printable:float
    zero:float
    smooth:float
    repeat16:float

def _sha(x:bytes)->bytes:
    return hashlib.sha256(x).digest()

def _putv(o:bytearray,x:int)->None:
    while x>=128:
        o.append((x&127)|128); x>>=7
    o.append(x)

def _getv(b:bytes,i:int)->tuple[int,int]:
    x=s=0
    while True:
        if i>=len(b): raise ValueError("truncated varint")
        q=b[i]; i+=1; x|=(q&127)<<s
        if not q&128: return x,i
        s+=7
        if s>63: raise ValueError("varint too large")

def _pack(route:int,source:bytes,payload:bytes)->bytes:
    return HEADER.pack(MAGIC,VERSION,route,len(source),_sha(source))+payload

def _parse(blob:bytes)->tuple[int,int,bytes,bytes]:
    if len(blob)<HEADER.size: raise ValueError("truncated OMNIA-REX")
    m,v,r,n,d=HEADER.unpack_from(blob)
    if m!=MAGIC or v!=VERSION: raise ValueError("bad OMNIA-REX header")
    return r,n,d,blob[HEADER.size:]

def _verify(out:bytes,n:int,d:bytes)->bytes:
    if len(out)!=n or _sha(out)!=d:
        raise ValueError("OMNIA-REX SHA/size mismatch")
    return out

def features(data:bytes)->Features:
    s=data[:min(8192,len(data))]; n=max(1,len(s)); cnt=[0]*256
    for x in s: cnt[x]+=1
    e=-sum((c/n)*math.log2(c/n) for c in cnt if c)
    printable=sum(x in (9,10,13) or 32<=x<127 for x in s)/n
    zero=s.count(0)/n
    smooth=sum(abs(s[i]-s[i-1])<=2 for i in range(1,len(s)))/n
    atoms=[s[i:i+16] for i in range(0,max(0,len(s)-15),16)]
    repeat16=1-len(set(atoms))/len(atoms) if atoms else 0.0
    return Features(e,printable,zero,smooth,repeat16)

def _paeth(a:int,b:int,c:int)->int:
    p=a+b-c; pa=abs(p-a); pb=abs(p-b); pc=abs(p-c)
    return a if pa<=pb and pa<=pc else b if pb<=pc else c

def _spatial_residual(data:bytes,w:int,filt:int)->bytes:
    out=bytearray(len(data))
    for i,x in enumerate(data):
        col=i%w
        l=data[i-1] if col else 0
        u=data[i-w] if i>=w else 0
        ul=data[i-w-1] if i>=w and col else 0
        pred=l if filt==0 else u if filt==1 else _paeth(l,u,ul)
        out[i]=(x-pred)&255
    return bytes(out)

def _spatial_restore(res:bytes,w:int,filt:int)->bytes:
    out=bytearray(len(res))
    for i,r in enumerate(res):
        col=i%w
        l=out[i-1] if col else 0
        u=out[i-w] if i>=w else 0
        ul=out[i-w-1] if i>=w and col else 0
        pred=l if filt==0 else u if filt==1 else _paeth(l,u,ul)
        out[i]=(r+pred)&255
    return bytes(out)

def _sparse_encode(res:bytes)->bytes:
    out=bytearray(); last=-1
    for i,x in enumerate(res):
        if x:
            _putv(out,i-last-1); out.append(x); last=i
    _putv(out,len(res)-last-1)
    return bytes(out)

def _sparse_decode(src:bytes,n:int)->bytes:
    out=bytearray(n); last=-1; i=0
    while True:
        gap,i=_getv(src,i); pos=last+gap+1
        if pos>=n:
            if pos!=n: raise ValueError("sparse overflow")
            break
        if i>=len(src): raise ValueError("truncated sparse value")
        out[pos]=src[i]; i+=1; last=pos
    if i!=len(src): raise ValueError("trailing sparse data")
    return bytes(out)

def _widths(n:int)->list[int]:
    s=set(); q=math.isqrt(n)
    if q*q==n: s.add(q)
    for w in (8,16,32,64,128,256,512,1024,2048,4096):
        if n>=2*w and n%w==0: s.add(w)
    return sorted(s)

def _with_params(params:bytes,payload:bytes)->bytes:
    out=bytearray(); _putv(out,len(params)); out+=params; out+=payload
    return bytes(out)

def _split_params(src:bytes)->tuple[bytes,bytes]:
    n,i=_getv(src,0)
    return src[i:i+n],src[i+n:]

def _sp_params(w:int,f:int)->bytes:
    out=bytearray(); _putv(out,w); out.append(f)
    return bytes(out)

def _sp_parse(p:bytes)->tuple[int,int]:
    w,i=_getv(p,0)
    if i>=len(p): raise ValueError("bad spatial params")
    return w,p[i]

class QTD3ExternalAdapter:
    """Adapter only. Caller must account model bytes/cold total separately."""
    family="QTD3-SHARED"
    def __init__(self,model:Any,path:str="object.bin",unix_ns:int=1):
        from qr_temporal.qtd3 import pack_blind_v3, unpack_v3
        self.model=model; self.path=path; self.unix_ns=unix_ns
        self._pack=pack_blind_v3; self._unpack=unpack_v3
        self.name="QTD3 EXTERNAL SHARED MODEL"
    def compress(self,data:bytes)->bytes:
        return self._pack(data,self.path,self.model,unix_ns=self.unix_ns).blob
    def decompress(self,blob:bytes)->bytes:
        return self._unpack(blob,self.model)

class OmniaREXV1:
    name="SHTENCO OMNIA-REX V1 MAX"
    family="SHTENCO-OMNIA-REX"

    def __init__(self,include_legacy:bool=True,include_math:bool=True,profile:str="max"):
        self.include_legacy=include_legacy
        self.include_math=include_math
        self.profile=profile
        self.last_mode="uninitialized"
        self._external={}
        if include_legacy: self._load_legacy()

    def _load_legacy(self)->None:
        try:
            try: from .shtenco_tier1_v21 import OmniaTier1V21Max
            except ImportError: from shtenco_tier1_v21 import OmniaTier1V21Max
            self._external[R_OMNIA]=(OmniaTier1V21Max.name,OmniaTier1V21Max())
        except Exception: pass
        try:
            try: from .gabriel_horn_engine import GabrielHornEngine
            except ImportError: from gabriel_horn_engine import GabrielHornEngine
            self._external[R_GABRIEL]=("SHTENCO GABRIEL-HORN MAX",GabrielHornEngine(profile="max"))
        except Exception: pass
        if self.include_math:
            try:
                try: from .shtenco_math_portfolio_v3 import ShtencoMathExpertV3
                except ImportError: from shtenco_math_portfolio_v3 import ShtencoMathExpertV3
                self._external[R_MATH]=(ShtencoMathExpertV3("max").name,ShtencoMathExpertV3("max"))
            except Exception: pass

    def _candidate(self,route:int,name:str,source:bytes,payload:bytes,family:str="builtin")->Candidate|None:
        try:
            arc=_pack(route,source,payload)
            if self.decompress(arc)!=source: return None
            return Candidate(route,name,arc,family)
        except Exception:
            return None

    def _builtin_candidates(self,source:bytes)->list[Candidate]:
        out=[]
        def add(r,n,p):
            c=self._candidate(r,n,source,p)
            if c: out.append(c)
        add(R_RAW,"raw",source)
        add(R_ZLIB,"zlib-9",zlib.compress(source,9))
        add(R_LZMA,"lzma-9-extreme",lzma.compress(source,preset=9|lzma.PRESET_EXTREME))
        add(R_BROTLI,"brotli-11",brotli.compress(source,quality=11))
        if zstd is not None:
            add(R_ZSTD,"zstd-22",zstd.ZstdCompressor(level=22,write_checksum=True,write_content_size=True).compress(source))

        f=features(source)
        incompressible=f.entropy>7.95 and f.repeat16<.005 and f.smooth<.02 and f.zero<.01
        allow_heavy=(not incompressible) and (
            self.profile=="max" or f.entropy<7.85 or f.repeat16>.01 or f.smooth>.08 or f.zero>.01
        )
        if allow_heavy:
            for order,route in ((4,R_PPM4),(6,R_PPM6),(8,R_PPM8)):
                payload,_=ppm.encode(source,order)
                add(route,f"ppm-rex-o{order}",payload)

            if len(source)<=100_000:
                t,row=bwt.bwt(source)
                ranks=bwt.mtf_encode(t)
                add(R_BWT,"bwt-mtf-brotli",_with_params(struct.pack(">I",row),brotli.compress(ranks,quality=11)))

            for w in _widths(len(source)):
                for filt in (0,1,2):
                    res=_spatial_residual(source,w,filt)
                    params=_sp_params(w,filt)
                    add(R_SP_BROTLI,f"spatial-{w}-{filt}-brotli",_with_params(params,brotli.compress(res,quality=11)))
                    add(R_SP_SPARSE,f"spatial-{w}-{filt}-sparse",_with_params(params,zlib.compress(_sparse_encode(res),9)))
        return out

    def _legacy_candidates(self,source:bytes)->list[Candidate]:
        out=[]
        for route,(name,engine) in self._external.items():
            try:
                payload=engine.compress(source)
                if engine.decompress(payload)!=source: continue
                c=self._candidate(route,name,source,payload,"legacy")
                if c: out.append(c)
            except Exception:
                continue
        return out

    def compress(self,source:bytes)->bytes:
        source=bytes(source)
        candidates=self._builtin_candidates(source)+self._legacy_candidates(source)
        if not candidates: raise RuntimeError("no verified OMNIA-REX candidate")
        best=min(candidates,key=lambda x:(len(x.archive),x.route,x.name))
        self.last_mode=best.name
        return best.archive

    def decompress(self,archive:bytes)->bytes:
        r,n,d,p=_parse(archive)
        if r==R_RAW: out=p
        elif r==R_ZLIB: out=zlib.decompress(p)
        elif r==R_LZMA: out=lzma.decompress(p)
        elif r==R_BROTLI: out=brotli.decompress(p)
        elif r==R_ZSTD:
            if zstd is None: raise ValueError("zstd backend unavailable")
            out=zstd.ZstdDecompressor().decompress(p,max_output_size=n)
        elif r in (R_PPM4,R_PPM6,R_PPM8):
            out=ppm.decode(p,n,{R_PPM4:4,R_PPM6:6,R_PPM8:8}[r])
        elif r==R_BWT:
            params,payload=_split_params(p)
            row=struct.unpack(">I",params)[0]
            out=bwt.ibwt(bwt.mtf_decode(brotli.decompress(payload)),row)
        elif r in (R_SP_SPARSE,R_SP_BROTLI):
            params,payload=_split_params(p); w,f=_sp_parse(params)
            res=_sparse_decode(zlib.decompress(payload),n) if r==R_SP_SPARSE else brotli.decompress(payload)
            out=_spatial_restore(res,w,f)
        elif r in self._external:
            out=self._external[r][1].decompress(p)
        else:
            raise ValueError(f"unknown OMNIA-REX route {r}")
        return _verify(out,n,d)

    def inspect_candidates(self,source:bytes)->list[dict[str,Any]]:
        c=self._builtin_candidates(bytes(source))+self._legacy_candidates(bytes(source))
        return sorted(
            [{"name":x.name,"family":x.family,"route":x.route,"bytes":len(x.archive)} for x in c],
            key=lambda x:(x["bytes"],x["route"])
        )

def omnia_rex_v1_engine_suite():
    e=OmniaREXV1()
    return [(e.name,e.family,e)]
