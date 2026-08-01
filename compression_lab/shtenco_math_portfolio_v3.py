#!/usr/bin/env python3
"""Exact mathematical expert layer for SHTENCO AI Compress.

Adds BytePoly, XOR/transpose, WholeINT, signed P2HF and optional reversible
secp256k1 EC-MATH. Every candidate is decoded and SHA-256 verified. The
production wrapper compares this expert with existing OMNIA v2.1, so normal
files cannot be forced through a worse mathematical representation.
"""
from __future__ import annotations
from dataclasses import dataclass
import collections, hashlib, lzma, math, struct

MAGIC=b"SMX3"; VERSION=1; HEADER=struct.Struct(">4sBBQ32s")
RAW,LZMA,BYTEPOLY,XOR,TRANSPOSE,WHOLEINT,P2HF,EC=range(8)
ROUTE_RAW,ROUTE_LZMA9,ROUTE_BYTEPOLY,ROUTE_XOR,ROUTE_TRANSPOSE,ROUTE_WHOLEINT,ROUTE_P2HF,ROUTE_EC_MATH = RAW,LZMA,BYTEPOLY,XOR,TRANSPOSE,WHOLEINT,P2HF,EC
NAMES={RAW:"raw",LZMA:"lzma9",BYTEPOLY:"bytepoly+lzma9",XOR:"xor-lag+lzma9",
       TRANSPOSE:"transpose+lzma9",WHOLEINT:"wholeint-formula+lzma9",
       P2HF:"p2hf-signed-formula+lzma9",EC:"ec-math-secp256k1+lzma9"}
EC_P=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
EC_B=7; EC_CHUNK=30; EC_X_BYTES=31

@dataclass(frozen=True)
class Features:
    entropy:float; zero:float; ff:float; smooth:float; adjacent:float
    atom_repeat:float; bit_density:float
@dataclass(frozen=True)
class Candidate:
    route:int; archive:bytes; work:int

def sha(data:bytes)->bytes:return hashlib.sha256(data).digest()
def uv(x:int)->bytes:
    if x<0:raise ValueError("negative varint")
    o=bytearray()
    while x>=128:o.append((x&127)|128);x>>=7
    o.append(x);return bytes(o)
def rv(data:bytes,p:int=0)->tuple[int,int]:
    x=s=0
    for _ in range(10):
        if p>=len(data):raise ValueError("truncated varint")
        b=data[p];p+=1;x|=(b&127)<<s
        if b<128:return x,p
        s+=7
    raise ValueError("varint too large")
def zz(x:int)->int:return x*2 if x>=0 else -x*2-1
def uz(x:int)->int:return x//2 if x%2==0 else -(x//2)-1

def features(data:bytes)->Features:
    a=data[:min(len(data),16384)];n=max(1,len(a));c=collections.Counter(a)
    ent=-sum((v/n)*math.log2(v/n) for v in c.values())
    smooth=sum(abs(a[i]-a[i-1])<=2 for i in range(1,len(a)))/n
    adjacent=sum(a[i]==a[i-1] for i in range(1,len(a)))/n
    atoms=[a[i:i+32] for i in range(0,len(a)-31,32)]
    repeat=1-len(set(atoms))/len(atoms) if atoms else 0.0
    density=sum(x.bit_count() for x in a)/(8*n)
    return Features(ent,a.count(0)/n,a.count(255)/n,smooth,adjacent,repeat,density)

def delta(data:bytes)->bytes:
    o=bytearray(len(data));p=0
    for i,x in enumerate(data):o[i]=(x-p)&255;p=x
    return bytes(o)
def undelta(data:bytes)->bytes:
    o=bytearray(len(data));p=0
    for i,x in enumerate(data):p=(p+x)&255;o[i]=p
    return bytes(o)
def diff(data:bytes,n:int)->bytes:
    for _ in range(n):data=delta(data)
    return data
def integrate(data:bytes,n:int)->bytes:
    for _ in range(n):data=undelta(data)
    return data
def xor_encode(data:bytes,lag:int)->bytes:
    if lag<=0 or lag>=len(data):return data
    o=bytearray(data)
    for i in range(len(o)-1,lag-1,-1):o[i]^=data[i-lag]
    return bytes(o)
def xor_decode(data:bytes,lag:int)->bytes:
    if lag<=0 or lag>=len(data):return data
    o=bytearray(data)
    for i in range(lag,len(o)):o[i]^=o[i-lag]
    return bytes(o)
def tr(data:bytes,w:int)->bytes:return b"".join(data[i::w] for i in range(w))
def untr(data:bytes,w:int)->bytes:
    n=len(data);lens=[(n-i+w-1)//w if i<n else 0 for i in range(w)]
    cols=[];p=0
    for ln in lens:cols.append(data[p:p+ln]);p+=ln
    if p!=n:raise ValueError("bad transpose")
    pos=[0]*w;o=bytearray(n)
    for i in range(n):j=i%w;o[i]=cols[j][pos[j]];pos[j]+=1
    return bytes(o)
def lz(data:bytes)->bytes:return lzma.compress(data,preset=9)

def encode_exps(exps:list[int])->bytes:
    o=bytearray(uv(len(exps)))
    if not exps:return bytes(o)
    o+=uv(exps[0]);g=[exps[i-1]-exps[i] for i in range(1,len(exps))];i=0
    while i<len(g):
        ce=i+1
        while ce<len(g) and g[ce]==g[i]:ce+=1
        clen=ce-i;alen=1;step=0
        if i+1<len(g):
            step=g[i+1]-g[i];ae=i+2
            while ae<len(g) and g[ae]==g[i]+step*(ae-i) and g[ae]>0:ae+=1
            alen=ae-i
        if clen>=4 and clen>=alen:o.append(1);o+=uv(clen)+uv(g[i]);i+=clen
        elif alen>=4:o.append(2);o+=uv(alen)+uv(g[i])+uv(zz(step));i+=alen
        else:o.append(0);o+=uv(g[i]);i+=1
    return bytes(o)
def decode_exps(data:bytes,p:int=0)->tuple[list[int],int]:
    count,p=rv(data,p)
    if not count:return [],p
    first,p=rv(data,p);out=[first]
    while len(out)<count:
        if p>=len(data):raise ValueError("truncated exponent grammar")
        t=data[p];p+=1
        if t==0:
            gap,p=rv(data,p);out.append(out[-1]-gap)
        elif t==1:
            run,p=rv(data,p);gap,p=rv(data,p)
            for _ in range(run):out.append(out[-1]-gap)
        elif t==2:
            run,p=rv(data,p);g0,p=rv(data,p);z,p=rv(data,p);step=uz(z)
            for j in range(run):
                gap=g0+step*j
                if gap<=0:raise ValueError("non-positive gap")
                out.append(out[-1]-gap)
        else:raise ValueError("unknown exponent token")
        if len(out)>count:raise ValueError("exponent overrun")
    return out,p

def binary_exps(n:int)->list[int]:
    out=[]
    while n:
        low=n&-n;out.append(low.bit_length()-1);n^=low
    out.reverse();return out
def naf(n:int)->list[tuple[int,int]]:
    out=[];e=0
    while n:
        if n&1:
            s=2-(n&3);out.append((e,s));n-=s
        n>>=1;e+=1
    out.sort(reverse=True);return out

def whole_enc(data:bytes)->bytes:return lz(encode_exps(binary_exps(int.from_bytes(data,"big"))))
def whole_dec(payload:bytes,size:int)->bytes:
    raw=lzma.decompress(payload);ex,p=decode_exps(raw)
    if p!=len(raw):raise ValueError("trailing WholeINT bytes")
    return sum(1<<e for e in ex).to_bytes(size,"big")
def p2hf_enc(data:bytes)->bytes:
    terms=naf(int.from_bytes(data,"big"));ex=[e for e,_ in terms];signs=bytearray((len(terms)+7)//8)
    for i,(_,s) in enumerate(terms):
        if s<0:signs[i>>3]|=1<<(i&7)
    grammar=encode_exps(ex);return lz(uv(len(grammar))+grammar+signs)
def p2hf_dec(payload:bytes,size:int)->bytes:
    raw=lzma.decompress(payload);ln,p=rv(raw);end=p+ln;ex,used=decode_exps(raw[p:end])
    if used!=ln or len(raw[end:])!=(len(ex)+7)//8:raise ValueError("bad P2HF stream")
    signs=raw[end:];n=0
    for i,e in enumerate(ex):n+=(-1 if signs[i>>3]&(1<<(i&7)) else 1)*(1<<e)
    if n<0:raise ValueError("negative P2HF")
    return n.to_bytes(size,"big")

def ec_is_x(x:int)->bool:
    r=(pow(x,3,EC_P)+EC_B)%EC_P
    return r==0 or pow(r,(EC_P-1)//2,EC_P)==1
def ec_enc(data:bytes)->bytes:
    rec=[]
    for i in range(0,len(data),EC_CHUNK):
        base=int.from_bytes(data[i:i+EC_CHUNK].ljust(EC_CHUNK,b"\0"),"big")*256
        for nonce in range(256):
            x=base+nonce
            if ec_is_x(x):rec.append(x.to_bytes(EC_X_BYTES,"big"));break
        else:raise RuntimeError("EC mapping failed")
    stream=b"".join(r[c:c+1] for c in range(EC_X_BYTES) for r in rec)
    return uv(len(rec))+lz(stream)
def ec_dec(payload:bytes,size:int)->bytes:
    count,p=rv(payload);s=lzma.decompress(payload[p:])
    if len(s)!=count*EC_X_BYTES:raise ValueError("bad EC stream")
    rec=[bytearray(EC_X_BYTES) for _ in range(count)];k=0
    for c in range(EC_X_BYTES):
        for r in range(count):rec[r][c]=s[k];k+=1
    out=bytearray()
    for r in rec:
        x=int.from_bytes(r,"big")
        if not ec_is_x(x):raise ValueError("invalid EC x")
        out+=(x//256).to_bytes(EC_CHUNK,"big")
    return bytes(out[:size])

class ShtencoMathExpertV3:
    family="SHTENCO-MATH-PORTFOLIO-V3"
    def __init__(self,profile:str="balanced",enable_ec:bool=False):
        if profile not in {"balanced","max"}:raise ValueError("bad profile")
        self.profile=profile;self.enable_ec=enable_ec;self.work_weight=.25 if profile=="balanced" else 0.0
        self.name=f"SHTENCO MATH PORTFOLIO V3 {profile.upper()}";self.last_mode="uninitialized"
    def pack(self,route:int,source:bytes,payload:bytes)->bytes:
        return HEADER.pack(MAGIC,VERSION,route,len(source),sha(source))+payload
    def parse(self,a:bytes)->tuple[int,int,bytes,bytes]:
        if len(a)<HEADER.size:raise ValueError("truncated Math v3 archive")
        m,v,r,n,d=HEADER.unpack_from(a)
        if m!=MAGIC or v!=VERSION:raise ValueError("bad Math v3 archive")
        return r,n,d,a[HEADER.size:]
    def candidate(self,route:int,source:bytes,param:int=0)->Candidate|None:
        try:
            if route==RAW:payload=source;work=0
            elif route==LZMA:payload=lz(source);work=40
            elif route==BYTEPOLY:payload=bytes([param])+lz(diff(source,param));work=44+param
            elif route==XOR:payload=uv(param)+lz(xor_encode(source,param));work=42
            elif route==TRANSPOSE:payload=uv(param)+lz(tr(source,param));work=42
            elif route==WHOLEINT:payload=whole_enc(source);work=180
            elif route==P2HF:payload=p2hf_enc(source);work=220
            elif route==EC:payload=ec_enc(source);work=500
            else:raise ValueError("unknown route")
            archive=self.pack(route,source,payload)
            if self.decompress(archive)!=source:raise ValueError("candidate failed")
            return Candidate(route,archive,work)
        except Exception:return None
    def specs(self,data:bytes,f:Features)->list[tuple[int,int]]:
        s=[(RAW,0),(LZMA,0)]
        if self.profile=="max" or f.smooth>=.18 or f.zero>=.05:
            s += [(BYTEPOLY,n) for n in ((1,2) if self.profile=="balanced" else (1,2,3,4))]
        if self.profile=="max" or f.atom_repeat>=.05 or f.adjacent>=.08:
            widths=(4,8,16,32) if self.profile=="balanced" else (2,4,8,16,30,32,64,128,256)
            lags=(1,4,16,64) if self.profile=="balanced" else (1,2,4,8,16,32,64,256,1024)
            s += [(TRANSPOSE,w) for w in widths if w<=len(data)]
            s += [(XOR,g) for g in lags if g<len(data)]
        if len(data)<=131072 and (f.bit_density<=.22 or self.profile=="max" and f.bit_density<=.35):s.append((WHOLEINT,0))
        if len(data)<=131072 and (f.ff>=.08 or f.bit_density<=.22):s.append((P2HF,0))
        if self.enable_ec and len(data)<=65536 and (self.profile=="max" or f.atom_repeat>=.12):s.append((EC,0))
        return list(dict.fromkeys(s))
    def compress(self,source:bytes)->bytes:
        source=bytes(source);f=features(source)
        c=[x for r,p in self.specs(source,f) if (x:=self.candidate(r,source,p)) is not None]
        if not c:raise RuntimeError("no verified Math v3 route")
        best=min(c,key=lambda x:(len(x.archive)+self.work_weight*x.work,len(x.archive),x.work,x.route))
        self.last_mode=NAMES[best.route]
        if self.decompress(best.archive)!=source:raise ValueError("final verification failed")
        return best.archive
    def decompress(self,a:bytes)->bytes:
        r,n,d,p=self.parse(a)
        if r==RAW:out=p
        elif r==LZMA:out=lzma.decompress(p)
        elif r==BYTEPOLY:
            if not p:raise ValueError("missing order")
            out=integrate(lzma.decompress(p[1:]),p[0])
        elif r==XOR:g,q=rv(p);out=xor_decode(lzma.decompress(p[q:]),g)
        elif r==TRANSPOSE:w,q=rv(p);out=untr(lzma.decompress(p[q:]),w)
        elif r==WHOLEINT:out=whole_dec(p,n)
        elif r==P2HF:out=p2hf_dec(p,n)
        elif r==EC:out=ec_dec(p,n)
        else:raise ValueError("unknown Math v3 route")
        if len(out)!=n or sha(out)!=d:raise ValueError("Math v3 SHA/size mismatch")
        return out

OMAGIC=b"SOM3"; OHEADER=struct.Struct(">4sBBQ32s"); BASE,MATH=0,1
class ShtencoOmniaMathV3:
    family="SHTENCO-OMNIA-MATH-V3"
    def __init__(self,profile:str="balanced",enable_ec:bool=False):
        if profile not in {"speed","balanced","max"}:raise ValueError("bad profile")
        try:
            try:
                from .shtenco_tier1_v2 import OmniaTier1Balanced,OmniaTier1Speed
                from .shtenco_tier1_v21 import OmniaTier1V21Max
            except ImportError:
                from shtenco_tier1_v2 import OmniaTier1Balanced,OmniaTier1Speed
                from shtenco_tier1_v21 import OmniaTier1V21Max
        except Exception as e:raise RuntimeError("OMNIA modules required") from e
        self.base={"speed":OmniaTier1Speed,"balanced":OmniaTier1Balanced,"max":OmniaTier1V21Max}[profile]()
        self.math=ShtencoMathExpertV3("max" if profile=="max" else "balanced",enable_ec)
        self.name=f"SHTENCO OMNIA-MATH V3 {profile.upper()}";self.last_mode="uninitialized"
    def compress(self,source:bytes)->bytes:
        source=bytes(source);choices=[]
        for r,p,decoder in ((BASE,self.base.compress(source),self.base.decompress),(MATH,self.math.compress(source),self.math.decompress)):
            restored=decoder(p)
            if restored==source and sha(restored)==sha(source):choices.append((r,OHEADER.pack(OMAGIC,VERSION,r,len(source),sha(source))+p))
        r,a=min(choices,key=lambda x:(len(x[1]),x[0]));self.last_mode="omnia-baseline" if r==BASE else f"math:{self.math.last_mode}"
        if self.decompress(a)!=source:raise ValueError("OMNIA-MATH verification failed")
        return a
    def decompress(self,a:bytes)->bytes:
        if len(a)<OHEADER.size:raise ValueError("truncated OMNIA-MATH")
        m,v,r,n,d=OHEADER.unpack_from(a);p=a[OHEADER.size:]
        if m!=OMAGIC or v!=VERSION:raise ValueError("bad OMNIA-MATH")
        out=self.base.decompress(p) if r==BASE else self.math.decompress(p) if r==MATH else None
        if out is None or len(out)!=n or sha(out)!=d:raise ValueError("OMNIA-MATH SHA/size mismatch")
        return out

def math_v3_engine_suite():
    engines=[ShtencoMathExpertV3("balanced"),ShtencoMathExpertV3("max")]
    try:engines += [ShtencoOmniaMathV3("speed"),ShtencoOmniaMathV3("balanced"),ShtencoOmniaMathV3("max")]
    except RuntimeError:pass
    return [(e.name,getattr(e,"family","SHTENCO-MATH-V3"),e) for e in engines]
