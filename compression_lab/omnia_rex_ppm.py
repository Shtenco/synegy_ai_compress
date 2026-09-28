from __future__ import annotations

TOP=(1<<32)-1
HALF=1<<31
Q1=1<<30
Q3=Q1*3

class BitOut:
    def __init__(self): self.out=bytearray(); self.acc=0; self.n=0; self.bits=0
    def write(self,b):
        self.acc=(self.acc<<1)|(b&1); self.n+=1; self.bits+=1
        if self.n==8:
            self.out.append(self.acc); self.acc=0; self.n=0
    def finish(self):
        if self.n: self.out.append(self.acc<<(8-self.n))
        return bytes(self.out)

class BitIn:
    def __init__(self,data): self.data=data; self.i=0; self.bit=0
    def read(self):
        if self.i>=len(self.data): return 0
        b=(self.data[self.i]>>(7-self.bit))&1; self.bit+=1
        if self.bit==8: self.bit=0; self.i+=1
        return b

class ArithEnc:
    def __init__(self,bw): self.low=0; self.high=TOP; self.pending=0; self.bw=bw
    def _bit_plus_pending(self,b):
        self.bw.write(b)
        for _ in range(self.pending): self.bw.write(1-b)
        self.pending=0
    def encode(self,cum_lo,cum_hi,total):
        r=self.high-self.low+1
        self.high=self.low+(r*cum_hi//total)-1
        self.low=self.low+(r*cum_lo//total)
        while True:
            if self.high<HALF:
                self._bit_plus_pending(0)
            elif self.low>=HALF:
                self._bit_plus_pending(1); self.low-=HALF; self.high-=HALF
            elif self.low>=Q1 and self.high<Q3:
                self.pending+=1; self.low-=Q1; self.high-=Q1
            else: break
            self.low=(self.low<<1)&TOP; self.high=((self.high<<1)&TOP)|1
    def finish(self):
        self.pending+=1
        if self.low<Q1: self._bit_plus_pending(0)
        else: self._bit_plus_pending(1)

class ArithDec:
    def __init__(self,br):
        self.low=0; self.high=TOP; self.br=br; self.code=0
        for _ in range(32): self.code=((self.code<<1)|br.read())&TOP
    def target(self,total):
        r=self.high-self.low+1
        return (((self.code-self.low+1)*total-1)//r)
    def update(self,cum_lo,cum_hi,total):
        r=self.high-self.low+1
        self.high=self.low+(r*cum_hi//total)-1
        self.low=self.low+(r*cum_lo//total)
        while True:
            if self.high<HALF: pass
            elif self.low>=HALF:
                self.code-=HALF; self.low-=HALF; self.high-=HALF
            elif self.low>=Q1 and self.high<Q3:
                self.code-=Q1; self.low-=Q1; self.high-=Q1
            else: break
            self.low=(self.low<<1)&TOP; self.high=((self.high<<1)&TOP)|1
            self.code=((self.code<<1)&TOP)|self.br.read()

class PPM:
    def __init__(self,max_order=6):
        self.max_order=max_order
        self.ctx=[{} for _ in range(max_order+1)]
        self.prefix=bytearray()
    def _key(self,o): return b'' if o==0 else bytes(self.prefix[-o:])
    def update(self,x):
        mo=min(self.max_order,len(self.prefix))
        for o in range(mo+1):
            key=self._key(o); d=self.ctx[o].get(key)
            if d is None: d={}; self.ctx[o][key]=d
            d[x]=d.get(x,0)+1
            if sum(d.values())>8192:
                for k in list(d): d[k]=(d[k]+1)//2
        self.prefix.append(x)

def _avail(counts,excluded):
    if not counts: return []
    return [(s,c) for s,c in sorted(counts.items()) if s not in excluded]

def encode(data:bytes,max_order=6):
    bw=BitOut(); ac=ArithEnc(bw); m=PPM(max_order); escapes=0; used_orders=[0]*(max_order+2)
    for x in data:
        excluded=set(); done=False
        mo=min(max_order,len(m.prefix))
        for o in range(mo,-1,-1):
            counts=m.ctx[o].get(m._key(o)); av=_avail(counts,excluded)
            if not av: continue
            sm=sum(c for _,c in av); esc=max(1,len(av)); total=sm+esc
            cum=0; found=False
            for s,c in av:
                if s==x:
                    ac.encode(cum,cum+c,total); found=True; done=True; used_orders[o]+=1; break
                cum+=c
            if found: break
            ac.encode(sm,total,total); escapes+=1
            excluded.update(s for s,_ in av)
        if not done:
            rem=[s for s in range(256) if s not in excluded]
            idx=rem.index(x); ac.encode(idx,idx+1,len(rem)); used_orders[-1]+=1
        m.update(x)
    ac.finish(); payload=bw.finish()
    return payload, {'bits':bw.bits,'escapes':escapes,'used_orders':used_orders,'max_order':max_order}

def decode(payload:bytes,n:int,max_order=6):
    br=BitIn(payload); ac=ArithDec(br); m=PPM(max_order); out=bytearray()
    for _ in range(n):
        excluded=set(); sym=None
        mo=min(max_order,len(m.prefix))
        for o in range(mo,-1,-1):
            counts=m.ctx[o].get(m._key(o)); av=_avail(counts,excluded)
            if not av: continue
            sm=sum(c for _,c in av); esc=max(1,len(av)); total=sm+esc; t=ac.target(total)
            cum=0; chosen=None
            for s,c in av:
                if t<cum+c: chosen=(s,cum,cum+c); break
                cum+=c
            if chosen is not None:
                s,lo,hi=chosen; ac.update(lo,hi,total); sym=s; break
                cum+=c
            if sym is not None: break
            ac.update(sm,total,total); excluded.update(s for s,_ in av)
        if sym is None:
            rem=[s for s in range(256) if s not in excluded]
            t=ac.target(len(rem)); sym=rem[t]; ac.update(t,t+1,len(rem))
        out.append(sym); m.update(sym)
    return bytes(out)
