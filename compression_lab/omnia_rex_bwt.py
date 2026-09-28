from __future__ import annotations
import struct

def bwt(data:bytes):
    # Suffix-array BWT of data + unique sentinel 256. Return BWT bytes without sentinel and its row.
    seq=[b for b in data]+[256]; n=len(seq)
    sa=list(range(n)); rank=seq[:] ; k=1
    while k<n:
        sa.sort(key=lambda i:(rank[i], rank[i+k] if i+k<n else -1))
        nr=[0]*n; classes=0; prev=None
        for i in sa:
            key=(rank[i],rank[i+k] if i+k<n else -1)
            if prev is not None and key!=prev: classes+=1
            nr[i]=classes; prev=key
        rank=nr
        if classes==n-1: break
        k*=2
    L=[]; sentinel_row=None
    for row,i in enumerate(sa):
        x=seq[i-1] if i>0 else 256
        if x==256: sentinel_row=row
        else: L.append(x)
    assert sentinel_row is not None and len(L)==len(data)
    return bytes(L),sentinel_row

def ibwt(last_no_sentinel:bytes,sentinel_row:int):
    # reinsert sentinel value 256 in L and invert via LF mapping
    L=list(last_no_sentinel); L.insert(sentinel_row,256); n=len(L)
    occ=[]; cnt={}
    for x in L:
        j=cnt.get(x,0); occ.append(j); cnt[x]=j+1
    first={}; total=0
    for x in sorted(cnt): first[x]=total; total+=cnt[x]
    row=sentinel_row; out=[]
    for _ in range(n-1):
        row=first[L[row]]+occ[row]
        x=L[row]
        if x==256: raise ValueError('early sentinel')
        out.append(x)
    out.reverse()
    return bytes(out)

def mtf_encode(data:bytes):
    table=list(range(256)); out=bytearray()
    for b in data:
        i=table.index(b); out.append(i)
        if i: table.pop(i); table.insert(0,b)
    return bytes(out)

def mtf_decode(ranks:bytes):
    table=list(range(256)); out=bytearray()
    for i in ranks:
        b=table[i]; out.append(b)
        if i: table.pop(i); table.insert(0,b)
    return bytes(out)

def transform(data:bytes):
    x,row=bwt(data); return struct.pack('>I',row)+mtf_encode(x)

def inverse(t:bytes):
    row=struct.unpack('>I',t[:4])[0]; return ibwt(mtf_decode(t[4:]),row)
