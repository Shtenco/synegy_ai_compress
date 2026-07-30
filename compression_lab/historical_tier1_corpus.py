#!/usr/bin/env python3
"""Exact deterministic 11-dataset corpus from the 2026-07-30 Tier-1 run."""
from __future__ import annotations
import json, math, random
SEED = 20260730

def _repeat(seed: bytes, size: int) -> bytes:
    return (seed * (size // len(seed) + 1))[:size] if seed else bytes(size)

def build_corpus(size: int = 32768) -> dict[str, bytes]:
    rng = random.Random(SEED)
    code_seed = b'''\nclass GraphAIArchive:\n    def encode_node(self, node, graph):\n        route = node.simhash & 255\n        community = graph.communities[route]\n        parent = community.nearest(node)\n        return parent.xor_patch(node)\n\n    def verify(self, restored, source):\n        return sha256(restored).digest() == sha256(source).digest()\n'''
    source_code = _repeat(code_seed, size)
    records = [json.dumps({
        "timestamp": 1700000000+i, "node": i%97, "route": (i*29)%256,
        "community": (i*7)%31, "event": "graph-edge-verification",
        "status": "PASS" if i%19 else "WARN", "value": round(math.sin(i/17),10),
    }, separators=(",", ":")) for i in range(max(256, size//70))]
    json_logs = _repeat(("\n".join(records)+"\n").encode(), size)
    csv_seed = "time,node,route,price,volume,status\n" + "".join(
        f"{i},{i%43},{(i*17)%256},{100+math.sin(i/23):.8f},{1000+i%211},{'ok' if i%13 else 'warn'}\n"
        for i in range(max(512, size//40)))
    telemetry = _repeat(csv_seed.encode(), size)
    repeated = _repeat(b"SHTENCO-GRAPH-AI-SABF-X-EGD-256-HACE-X\0"*32, size)
    base = bytes((i*13+7)&255 for i in range(1024)); versions=[]
    for version in range(max(32, size//len(base))):
        block=bytearray(base)
        for edit in range(1+version%11):
            block[(version*37+edit*101)%len(block)] ^= (version+edit+1)&255
        versions.append(bytes(block))
    snapshots = _repeat(b"".join(versions), size)
    sparse=bytearray(size)
    for i in range(0,size,89): sparse[i]=rng.randrange(1,256)
    structured=bytearray()
    for i in range(max(512,size//16)):
        structured += i.to_bytes(4,"little")
        structured += ((i*17)%100000).to_bytes(4,"little")
        structured += int(1_000_000+1000*math.sin(i/21)).to_bytes(8,"little",signed=True)
    structured=bytes(structured[:size]).ljust(size,b"\0")
    image=bytearray(); side=max(32,int(math.sqrt(size)))
    for y in range(side+1):
        for x in range(side+1): image.append(((x//8)*11+(y//8)*7+((x+y)//32))&255)
    image_like=_repeat(bytes(image),size)
    words=("abandon ability able about above absent absorb abstract absurd abuse access accident "
           "account accuse achieve acid acoustic acquire across act action actor actress actual adapt ").encode()
    bip39=_repeat(words,size); random_bytes=bytes(rng.randrange(256) for _ in range(size))
    fifth=size//5
    mixed=(source_code[:fifth]+json_logs[:fifth]+structured[:fifth]+snapshots[:fifth]+
           random_bytes[:size-4*fifth])
    return {"source_code":source_code,"json_graph_logs":json_logs,"telemetry_csv":telemetry,
            "repeated_text":repeated,"version_snapshots":snapshots,"sparse_weights":bytes(sparse),
            "structured_binary":structured,"image_like":image_like,"bip39_text":bip39,
            "mixed":mixed,"random":random_bytes}
