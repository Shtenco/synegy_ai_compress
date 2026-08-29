#!/usr/bin/env python3
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
import argparse,bz2,hashlib,json,lzma,math,struct,subprocess,time,zlib
import brotli

CASES=[
 {'name':'readme-evolution','base':'9832a2d424b8500bfcc01e088f6119f1419a09bb','target':'79915e036d80f98be9e72aa6dbd6b37a8d135f45','path':'README.md','qtd3_bytes':589},
 {'name':'new-tier1-v2-test','base':'0125f04cdaa350986c123b1208cd9623c372e886','target':'983d1c526c87e330f5cfca024dbfabda0c23dae4','path':'compression_lab/test_tier1_v2.py','qtd3_bytes':421},
 {'name':'new-unified-workflow','base':'983d1c526c87e330f5cfca024dbfabda0c23dae4','target':'3af005515e0148cd729a39e86b40dab0877157d5','path':'.github/workflows/unified_tier1_v2_benchmark.yml','qtd3_bytes':1382},
]
TEXT={'.py','.md','.txt','.json','.csv','.yml','.yaml','.toml','.ini','.cfg','.sh','.bat','.ps1','.gitmodules'}

def git(repo,*a):return subprocess.check_output(['git','-C',str(repo),*a])
def blob(repo,c,p):return git(repo,'show',f'{c}:{p}')
def ctime(repo,c):return int(git(repo,'show','-s','--format=%ct',c).strip())*1_000_000_000

def uv(n):
 o=bytearray()
 while n>=128:o.append((n&127)|128);n>>=7
 o.append(n);return bytes(o)
def ruv(b,p):
 n=s=0
 while 1:
  q=b[p];p+=1;n|=(q&127)<<s
  if q<128:return n,p
  s+=7

def eligible(path,size,maxb=262144):
 p=Path(path);return 0<=size<=maxb and (p.name=='.gitmodules' or p.suffix.lower() in TEXT)
def tree(repo,c,maxb=262144):
 out=[]
 for line in git(repo,'ls-tree','-r','-l',c).decode().splitlines():
  meta,path=line.split('\t',1);parts=meta.split()
  if len(parts)==4 and parts[1]=='blob':
   try:size=int(parts[3])
   except:continue
   if eligible(path,size,maxb):out.append((path,size))
 return out
def hist(repo,base,path,depth=2):return git(repo,'log',f'-n{depth}','--format=%H',base,'--',path).decode().split()

@dataclass(frozen=True)
class Entry:path:str;ts:int;digest:bytes;data:bytes
@dataclass(frozen=True)
class Model:
 entries:tuple[Entry,...]; model_id:bytes
 @property
 def max_ts(self):return max((e.ts for e in self.entries),default=0)
 @property
 def guard(self):return {e.digest for e in self.entries}
 def to_bytes(self):
  out=bytearray(b'QD4M'+struct.pack('>BI',1,len(self.entries)))
  for e in self.entries:
   path=e.path.encode();cand=[(0,e.data),(1,zlib.compress(e.data,9)),(2,brotli.compress(e.data,quality=11))]
   codec,p=min(cand,key=lambda x:len(x[1]))
   out+=struct.pack('>QH32sBII',e.ts,len(path),e.digest,codec,len(e.data),len(p))+path+p
  return bytes(out)
def train(repo,base,depth=2):
 rows=[];seen=set()
 for path,_ in tree(repo,base):
  cs=hist(repo,base,path,depth) or [base]
  for c in cs:
   try:d=blob(repo,c,path)
   except subprocess.CalledProcessError:continue
   dg=hashlib.sha256(d).digest();k=(path,dg)
   if k in seen:continue
   seen.add(k);rows.append(Entry(path,ctime(repo,c),dg,d))
 rows.sort(key=lambda e:(e.ts,e.path,e.digest));m=Model(tuple(rows),b'');mb=m.to_bytes();return Model(m.entries,hashlib.sha256(mb).digest())

GEAR=[int.from_bytes(hashlib.blake2s(bytes([i]),digest_size=8,person=b'QTD2GEAR').digest(),'big') for i in range(256)]
def fastcdc(data,mi=48,av=96,ma=192):
 if not data:return []
 bits=max(1,round(math.log2(av)));me=(1<<(bits+1))-1;ml=(1<<max(1,bits-1))-1;o=[];start=0
 while start<len(data):
  hard=min(start+ma,len(data))
  if hard-start<=mi:cut=hard
  else:
   i=start+mi;normal=min(start+av,hard);rolling=0;cut=None
   while i<normal:
    rolling=((rolling<<1)+GEAR[data[i]])&0xffffffffffffffff;i+=1
    if rolling&me==0:cut=i;break
   if cut is None:
    while i<hard:
     rolling=((rolling<<1)+GEAR[data[i]])&0xffffffffffffffff;i+=1
     if rolling&ml==0:cut=i;break
   if cut is None:cut=hard
  o.append(data[start:cut]);start=cut
 return o

COPY,LIT=0,1
def copy(sk,ei,off,n):sk.append(COPY);sk+=uv(ei)+uv(off)+uv(n)
def lit(sk,lits,d):
 if d:sk.append(LIT);sk+=uv(len(d));lits+=d

def decode_split(sk,lits,model,expected):
 out=bytearray();p=q=0
 while p<len(sk):
  op=sk[p];p+=1
  if op==COPY:
   ei,p=ruv(sk,p);off,p=ruv(sk,p);n,p=ruv(sk,p);out+=model.entries[ei].data[off:off+n]
  elif op==LIT:
   n,p=ruv(sk,p);out+=lits[q:q+n];q+=n
  else:raise ValueError('bad op')
 if len(out)!=expected or q!=len(lits):raise ValueError('split decode mismatch')
 return bytes(out)

def external(target,path,model,seed,mm):
 idx=defaultdict(list)
 for ei,e in enumerate(model.entries):
  for p in range(max(0,len(e.data)-seed+1)):
   if len(idx[e.data[p:p+seed]])<96:idx[e.data[p:p+seed]].append((ei,p))
 same={i for i,e in enumerate(model.entries) if e.path==path};sk=bytearray();ls=bytearray();pending=bytearray();covered=refs=0
 def flush():
  if pending:lit(sk,ls,bytes(pending));pending.clear()
 i=0
 while i<len(target):
  best=(0,0,0)
  if i+seed<=len(target):
   cand=sorted(idx.get(target[i:i+seed],()),key=lambda x:(0 if x[0] in same else 1,-model.entries[x[0]].ts))
   for ei,off in cand:
    src=model.entries[ei].data;n=seed;lim=min(len(target)-i,len(src)-off)
    while n<lim and target[i+n]==src[off+n]:n+=1
    if n>best[0]:best=(n,ei,off)
  if best[0]>=mm:flush();copy(sk,best[1],best[2],best[0]);covered+=best[0];refs+=1;i+=best[0]
  else:pending.append(target[i]);i+=1
 flush();return bytes(sk),bytes(ls),covered,refs

def lines(target,model):
 idx={}
 for ei,e in enumerate(model.entries):
  off=0
  for line in e.data.splitlines(keepends=True):
   if len(line)>=4:idx.setdefault(line,(ei,off,len(line)))
   off+=len(line)
 sk=bytearray();ls=bytearray();pending=bytearray();covered=refs=0
 def flush():
  if pending:lit(sk,ls,bytes(pending));pending.clear()
 for line in target.splitlines(keepends=True):
  r=idx.get(line)
  if r is None:pending+=line
  else:flush();copy(sk,*r);covered+=len(line);refs+=1
 flush();return bytes(sk),bytes(ls),covered,refs

def lineage(target,path,model):
 cand=[(i,e) for i,e in enumerate(model.entries) if e.path==path]
 if not cand:return None
 ei,e=max(cand,key=lambda x:x[1].ts);sk=bytearray();ls=bytearray();pos=0;covered=refs=0
 for b in SequenceMatcher(None,e.data,target,autojunk=False).get_matching_blocks():
  if not b.size:continue
  lit(sk,ls,target[pos:b.b]);copy(sk,ei,b.a,b.size);covered+=b.size;refs+=1;pos=b.b+b.size
 lit(sk,ls,target[pos:]);return bytes(sk),bytes(ls),covered,refs

def cdc(target,model,profile):
 idx={}
 for ei,e in enumerate(model.entries):
  off=0
  for ch in fastcdc(e.data,*profile):idx.setdefault(hashlib.blake2b(ch,digest_size=16).digest(),(ei,off,len(ch)));off+=len(ch)
 sk=bytearray();ls=bytearray();pending=bytearray();covered=refs=0
 def flush():
  if pending:lit(sk,ls,bytes(pending));pending.clear()
 for ch in fastcdc(target,*profile):
  r=idx.get(hashlib.blake2b(ch,digest_size=16).digest())
  if r is None:pending+=ch
  else:flush();copy(sk,*r);covered+=len(ch);refs+=1
 flush();return bytes(sk),bytes(ls),covered,refs

def delta8(d):
 o=bytearray(len(d));p=0
 for i,x in enumerate(d):o[i]=(x-p)&255;p=x
 return bytes(o)
def undelta8(d):
 o=bytearray(len(d));p=0
 for i,x in enumerate(d):p=(p+x)&255;o[i]=p
 return bytes(o)
def shuffle(d,w):return b''.join(d[j::w] for j in range(w)) if len(d)%w==0 else None
def unshuffle(d,w):
 n=len(d)//w;o=bytearray(len(d));p=0
 for j in range(w):
  lane=d[p:p+n];p+=n
  for i,x in enumerate(lane):o[i*w+j]=x
 return bytes(o)
TRANS={0:(lambda d:d,lambda d:d),1:(delta8,undelta8)}
for w,tid in [(2,2),(4,3),(8,4),(16,5)]:
 TRANS[tid]=(lambda d,w=w:delta8(shuffle(d,w)) if len(d)%w==0 else None,lambda d,w=w:unshuffle(undelta8(d),w))
TRANS[6]=(lambda d:delta8(delta8(d)),lambda d:undelta8(undelta8(d)))
CODEC={0:(lambda d:d,lambda d:d),1:(lambda d:zlib.compress(d,9),zlib.decompress),2:(lambda d:bz2.compress(d,9),bz2.decompress),3:(lambda d:lzma.compress(d,preset=9|lzma.PRESET_EXTREME),lzma.decompress),4:(lambda d:brotli.compress(d,quality=11),brotli.decompress)}
try:
 import zstandard as zstd
 CODEC[5]=(lambda d:zstd.ZstdCompressor(level=19,write_checksum=True,write_content_size=True).compress(d),lambda d:zstd.ZstdDecompressor().decompress(d))
except Exception:pass

def renc(d):
 cand=[]
 for t,(te,td) in TRANS.items():
  x=te(d)
  if x is None:continue
  for c,(ce,cd) in CODEC.items():
   if c==0 and t!=0:continue
   try:p=ce(x);r=td(cd(p))
   except Exception:continue
   if r==d:cand.append((len(p),t,c,p))
 return min(cand,key=lambda x:(x[0],x[1],x[2]))
def rdec(t,c,p):return TRANS[t][1](CODEC[c][1](p))

HDR=struct.Struct('>4sBBBBBBQII16s32s')
MAG=b'Q4S1'
def pack(target,path,model,ts):
 dg=hashlib.sha256(target).digest()
 if dg in model.guard or model.max_ts>=ts:raise ValueError('leakage')
 routes=[]
 for seed in (4,5,6,8,10):
  for mm in (8,10,12,16,24,32):
   if mm>=seed:routes.append((0,*external(target,path,model,seed,mm)))
 for prof in ((8,16,32),(16,32,64),(24,48,96),(48,96,192)):routes.append((1,*cdc(target,model,prof)))
 routes.append((2,*lines(target,model)));ln=lineage(target,path,model)
 if ln:routes.append((3,*ln))
 sk=bytearray();ls=bytearray();lit(sk,ls,target);routes.append((4,bytes(sk),bytes(ls),0,0))
 valid=[]
 for strategy,sk,ls,cov,refs in routes:
  se=renc(sk);le=renc(ls)
  hdr=HDR.pack(MAG,1,strategy,se[1],se[2],le[1],le[2],ts,len(target),len(se[3]),model.model_id[:16],dg)
  b=hdr+se[3]+le[3]
  try:
   if unpack(b,model)==target:valid.append((len(b),-cov,strategy,b,cov,refs,len(sk),len(ls),se,le))
  except Exception:pass
 if not valid:raise RuntimeError('no V4 shared route')
 return min(valid,key=lambda x:(x[0],x[1],x[2]))
def unpack(b,model):
 if len(b)<HDR.size:raise ValueError
 mag,v,strat,st,sc,lt,lc,ts,n,sn,mid,dg=HDR.unpack_from(b)
 if mag!=MAG or v!=1 or mid!=model.model_id[:16] or model.max_ts>=ts:raise ValueError
 sp=b[HDR.size:HDR.size+sn];lp=b[HDR.size+sn:]
 sk=rdec(st,sc,sp);ls=rdec(lt,lc,lp);out=decode_split(sk,ls,model,n)
 if hashlib.sha256(out).digest()!=dg:raise ValueError
 return out

def run(repo,case):
 m=train(repo,case['base'],2);target=blob(repo,case['target'],case['path']);ts=ctime(repo,case['target'])
 t0=time.perf_counter();best=pack(target,case['path'],m,ts);enc=(time.perf_counter()-t0)*1000
 b=best[3];out=unpack(b,m);assert out==target
 mb=len(m.to_bytes())
 return {'name':case['name'],'path':case['path'],'target_bytes':len(target),'container_bytes':len(b),'ratio':len(target)/len(b),'covered_bytes':best[4],'coverage_percent':100*best[4]/len(target),'refs':best[5],'skeleton_bytes':best[6],'literal_bytes':best[7],'model_serialized_bytes':mb,'cold_total_bytes':mb+len(b),'encode_ms':enc,'qtd3_baseline_bytes':case['qtd3_bytes'],'vs_qtd3_reduction_percent':100*(1-len(b)/case['qtd3_bytes']),'byte_equal':True,'sha256_equal':hashlib.sha256(out).digest()==hashlib.sha256(target).digest()}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('repo',type=Path,default=Path('.'),nargs='?');ap.add_argument('-o','--output',type=Path,default=Path('fusion_v4_shared.json'));a=ap.parse_args();repo=a.repo.resolve()
 rows=[run(repo,c) for c in CASES];src=sum(r['target_bytes'] for r in rows);tr=sum(r['container_bytes'] for r in rows);q3=sum(r['qtd3_baseline_bytes'] for r in rows)
 rep={'method':'Fusion V4 QTD3-prediction + split residual portfolio','header_bytes':HDR.size,'cases':rows,'aggregate':{'source_bytes':src,'container_bytes':tr,'ratio':src/tr,'transport_reduction_percent':100*(1-tr/src),'qtd3_baseline_bytes':q3,'vs_qtd3_reduction_percent':100*(1-tr/q3),'covered_bytes':sum(r['covered_bytes'] for r in rows),'coverage_percent':100*sum(r['covered_bytes'] for r in rows)/src,'cold_model_sum_bytes':sum(r['model_serialized_bytes'] for r in rows),'cold_total_sum_bytes':sum(r['cold_total_bytes'] for r in rows)}}
 a.output.write_text(json.dumps(rep,indent=2),encoding='utf-8');print(json.dumps(rep,indent=2))
if __name__=='__main__':main()
