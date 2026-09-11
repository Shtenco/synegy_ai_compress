#!/usr/bin/env python3
"""Real-weight DWE/MDL falsification benchmark for Mistral-Nemo 12B.

The benchmark intentionally reads selected byte ranges from the official
Safetensors shards instead of downloading the full 24.5 GB checkpoint.
It tests the row-prototype idea from the proposed DWE++ pipeline on real BF16
weights and reports both compression arithmetic and reconstruction error.

It also compares the literal pasted 2-bit centroid quantizer (which clips
negative values) with a corrected symmetric 2-bit quantizer, and optionally
runs SHTENCO OMNIA/Gabriel lossless storage on the packed representation.
"""
from __future__ import annotations

import argparse
import heapq
import json
import math
import os
import struct
import time
import urllib.request
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from sklearn.cluster import MiniBatchKMeans

MODEL = "mistralai/Mistral-Nemo-Base-2407"
REVISION = "2045759120154383da48ee84ce4bf2f90cc6ec1f"
BASE = f"https://huggingface.co/{MODEL}/resolve/{REVISION}"
SHARDS = [f"model-{i:05d}-of-00005.safetensors" for i in range(1, 6)]
DTYPE_BYTES = {"BF16": 2, "F16": 2, "F32": 4}


@dataclass
class QuantResult:
    tensor: str
    shape: list[int]
    sample_rows: int
    input_dim: int
    k: int
    centroid_mode: str
    norm_bits: int
    row_cosine_mean: float
    row_cosine_p05: float
    nmse: float
    output_rel_l2: float
    sample_index_entropy_bits: float
    sample_huffman_bits_per_index: float
    structural_bytes_fixed_index: int
    structural_ratio_vs_bf16: float
    estimated_bytes_huffman: int
    estimated_ratio_huffman_vs_bf16: float
    packed_sample_bytes: int
    best_lossless_route: str
    lossless_bytes: int
    lossless_ratio_on_packed_sample: float


def _url(path: str) -> str:
    return f"{BASE}/{path}?download=true"


def _read_prefix(url: str, n: int) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "nexus-dwe-probe/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        out = bytearray()
        while len(out) < n:
            chunk = r.read(min(1 << 20, n - len(out)))
            if not chunk:
                break
            out += chunk
        return bytes(out)


def _read_range(url: str, start: int, n: int) -> bytes:
    end = start + n - 1
    req = urllib.request.Request(
        url,
        headers={
            "Range": f"bytes={start}-{end}",
            "User-Agent": "nexus-dwe-probe/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        status = getattr(r, "status", 200)
        cr = r.headers.get("Content-Range", "")
        if start > 0 and status != 206 and not cr.startswith(f"bytes {start}-"):
            raise RuntimeError(
                f"HTTP range not honored for {url}: status={status}, Content-Range={cr!r}"
            )
        data = r.read(n + 1)
    if len(data) != n:
        raise RuntimeError(f"short range read: wanted {n}, got {len(data)}")
    return data


def safetensors_header(shard: str) -> tuple[dict, int]:
    url = _url(shard)
    first = _read_prefix(url, 8)
    if len(first) != 8:
        raise RuntimeError(f"cannot read header length for {shard}")
    hlen = struct.unpack("<Q", first)[0]
    if hlen <= 0 or hlen > 16_000_000:
        raise RuntimeError(f"implausible safetensors header length {hlen} for {shard}")
    blob = _read_prefix(url, 8 + hlen)
    header = json.loads(blob[8 : 8 + hlen])
    return header, 8 + hlen


def bf16_to_f32(raw: bytes) -> np.ndarray:
    u16 = np.frombuffer(raw, dtype="<u2")
    u32 = (u16.astype(np.uint32) << 16)
    return u32.view(np.float32)


def decode_values(raw: bytes, dtype: str) -> np.ndarray:
    if dtype == "BF16":
        return bf16_to_f32(raw)
    if dtype == "F16":
        return np.frombuffer(raw, dtype="<f2").astype(np.float32)
    if dtype == "F32":
        return np.frombuffer(raw, dtype="<f4").astype(np.float32)
    raise ValueError(f"unsupported dtype {dtype}")


def tensor_rows(shard: str, entry: dict, data_start: int, rows: int) -> tuple[np.ndarray, int]:
    shape = entry["shape"]
    if len(shape) != 2:
        raise ValueError("only 2D tensors supported")
    out_dim, in_dim = map(int, shape)
    dtype = entry["dtype"]
    bpe = DTYPE_BYTES[dtype]
    rows = min(rows, out_dim)
    # Deterministic central contiguous sample: efficient one-range read and avoids
    # privileging the first rows of embeddings/projections.
    row0 = max(0, (out_dim - rows) // 2)
    rel0, rel1 = map(int, entry["data_offsets"])
    row_bytes = in_dim * bpe
    start = data_start + rel0 + row0 * row_bytes
    raw = _read_range(_url(shard), start, rows * row_bytes)
    x = decode_values(raw, dtype).reshape(rows, in_dim)
    return x, row0


def row_normalize(w: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    norms = np.linalg.norm(w, axis=1).astype(np.float32)
    norms = np.maximum(norms, 1e-12)
    return (w / norms[:, None]).astype(np.float32), norms


def quantize_norms(norms: np.ndarray, bits: int) -> tuple[np.ndarray, np.ndarray, float, float]:
    lo = float(norms.min())
    hi = float(norms.max())
    levels = (1 << bits) - 1
    if hi <= lo:
        q = np.zeros_like(norms, dtype=np.uint8)
        return q, np.full_like(norms, lo), lo, 0.0
    scale = (hi - lo) / levels
    q = np.rint((norms - lo) / scale).clip(0, levels).astype(np.uint8)
    deq = lo + q.astype(np.float32) * scale
    return q, deq.astype(np.float32), lo, float(scale)


def literal_pasted_2bit(c: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Implements the sign-destroying quantizer exactly as in the pasted sketch."""
    scale = float(np.max(np.abs(c))) or 1.0
    q = np.rint(c / scale * 3.0).clip(0, 3).astype(np.uint8)
    deq = q.astype(np.float32) / 3.0 * scale
    return q, deq, scale


def symmetric_2bit(c: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    scale = float(np.max(np.abs(c))) or 1.0
    levels = np.asarray([-1.0, -1.0 / 3.0, 1.0 / 3.0, 1.0], dtype=np.float32)
    z = (c / scale).astype(np.float32)
    # Process flattened data in chunks so very wide codebooks do not allocate
    # a K x D x 4 temporary tensor all at once.
    flat = z.ravel()
    codes = np.empty(flat.size, dtype=np.uint8)
    chunk = 1_000_000
    for i in range(0, flat.size, chunk):
        s = flat[i : i + chunk]
        d = np.abs(s[:, None] - levels[None, :])
        codes[i : i + len(s)] = np.argmin(d, axis=1).astype(np.uint8)
    q = codes.reshape(c.shape)
    deq = levels[q].astype(np.float32) * scale
    return q, deq, scale


def entropy_bits(labels: np.ndarray) -> float:
    counts = np.bincount(labels)
    counts = counts[counts > 0].astype(np.float64)
    p = counts / counts.sum()
    return float(-(p * np.log2(p)).sum())


def huffman_lengths(labels: Iterable[int], k: int) -> list[int]:
    freq = Counter(int(x) for x in labels)
    heap: list[tuple[int, list[int]]] = []
    for sym in range(k):
        if freq.get(sym, 0):
            heap.append((freq[sym], [sym]))
    if not heap:
        return [0] * k
    if len(heap) == 1:
        lengths = [0] * k
        lengths[heap[0][1][0]] = 1
        return lengths
    heapq.heapify(heap)
    lengths = [0] * k
    while len(heap) > 1:
        w1, s1 = heapq.heappop(heap)
        w2, s2 = heapq.heappop(heap)
        for s in s1:
            lengths[s] += 1
        for s in s2:
            lengths[s] += 1
        heapq.heappush(heap, (w1 + w2, s1 + s2))
    return lengths


def pack_nbit(values: np.ndarray, bits: int) -> bytes:
    vals = np.asarray(values, dtype=np.uint8).ravel()
    mask = (1 << bits) - 1
    out = bytearray((len(vals) * bits + 7) // 8)
    bitpos = 0
    for v in vals:
        x = int(v) & mask
        byte = bitpos >> 3
        shift = bitpos & 7
        out[byte] |= (x << shift) & 0xFF
        if shift + bits > 8:
            out[byte + 1] |= x >> (8 - shift)
        bitpos += bits
    return bytes(out)


def pack_huffman(labels: np.ndarray, lengths: list[int]) -> bytes:
    # Canonical code construction from code lengths.
    pairs = sorted((l, s) for s, l in enumerate(lengths) if l > 0)
    code = 0
    prev = 0
    codes: dict[int, tuple[int, int]] = {}
    for l, s in pairs:
        code <<= l - prev
        codes[s] = (code, l)
        code += 1
        prev = l
    bits = []
    for lab in labels:
        c, l = codes[int(lab)]
        bits.append((c, l))
    nbits = sum(l for _, l in bits)
    out = bytearray((nbits + 7) // 8)
    pos = 0
    for c, l in bits:
        for b in range(l - 1, -1, -1):
            if (c >> b) & 1:
                out[pos >> 3] |= 1 << (7 - (pos & 7))
            pos += 1
    return bytes(lengths) + struct.pack("<I", nbits) + bytes(out)


def choose_lossless(blob: bytes) -> tuple[str, int]:
    candidates: list[tuple[str, bytes]] = [("RAW", blob)]
    import zlib, lzma
    candidates += [("zlib9", zlib.compress(blob, 9)), ("lzma9", lzma.compress(blob, preset=9))]
    try:
        from compression_lab.shtenco_tier1_v2 import OmniaTier1Speed, OmniaTier1Balanced, GabrielHornRandomAccessTier1
        for name, engine in (
            ("OMNIA_SPEED", OmniaTier1Speed()),
            ("OMNIA_BALANCED", OmniaTier1Balanced()),
            ("GABRIEL_RA", GabrielHornRandomAccessTier1(expected_range_bytes=4096, access_weight=24.0)),
        ):
            try:
                arc = engine.compress(blob)
                if engine.decompress(arc) == blob:
                    candidates.append((name, arc))
            except Exception:
                pass
    except Exception:
        pass
    name, payload = min(candidates, key=lambda x: len(x[1]))
    return name, len(payload)


def kmeans_full_centroids(v: np.ndarray, k: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    # Cluster on a deterministic column projection, then recompute centroids in
    # the full input dimension from assignments.
    rng = np.random.default_rng(seed)
    d = v.shape[1]
    proj_dim = min(768, d)
    cols = np.sort(rng.choice(d, size=proj_dim, replace=False))
    km = MiniBatchKMeans(
        n_clusters=k,
        random_state=seed,
        batch_size=min(256, len(v)),
        n_init=3,
        max_iter=60,
        reassignment_ratio=0.0,
    )
    labels = km.fit_predict(v[:, cols])
    centroids = np.zeros((k, d), dtype=np.float32)
    counts = np.bincount(labels, minlength=k)
    for i in range(k):
        if counts[i]:
            centroids[i] = v[labels == i].mean(axis=0)
        else:
            centroids[i] = v[rng.integers(0, len(v))]
    return labels.astype(np.int32), centroids


def metrics(w: np.ndarray, recon: np.ndarray, seed: int) -> tuple[float, float, float, float]:
    eps = 1e-12
    wn = np.linalg.norm(w, axis=1)
    rn = np.linalg.norm(recon, axis=1)
    cos = np.sum(w * recon, axis=1) / np.maximum(wn * rn, eps)
    nmse = float(np.sum((w - recon) ** 2) / max(float(np.sum(w ** 2)), eps))
    rng = np.random.default_rng(seed)
    errs = []
    for _ in range(8):
        x = rng.standard_normal(w.shape[1], dtype=np.float32)
        y = w @ x
        yr = recon @ x
        errs.append(float(np.linalg.norm(y - yr) / max(float(np.linalg.norm(y)), eps)))
    return float(np.mean(cos)), float(np.quantile(cos, 0.05)), nmse, float(np.mean(errs))


def tensor_benchmark(name: str, shape: list[int], w: np.ndarray, ks: list[int], seed: int) -> list[QuantResult]:
    out_dim, in_dim = map(int, shape)
    v, norms = row_normalize(w)
    raw_full = out_dim * in_dim * 2
    results: list[QuantResult] = []
    for k in ks:
        if k >= len(w):
            continue
        labels, centroids = kmeans_full_centroids(v, k, seed + k)
        H = entropy_bits(labels)
        lens = huffman_lengths(labels, k)
        avg_huff = float(np.mean([lens[int(x)] for x in labels]))
        for centroid_mode in ("fp16", "literal-pasted-2bit", "symmetric-2bit"):
            if centroid_mode == "fp16":
                cq = centroids.astype(np.float16).astype(np.float32)
                cbytes = centroids.astype(np.float16).tobytes()
            elif centroid_mode == "literal-pasted-2bit":
                codes, cq, cscale = literal_pasted_2bit(centroids)
                cbytes = struct.pack("<f", cscale) + pack_nbit(codes, 2)
            else:
                codes, cq, cscale = symmetric_2bit(centroids)
                cbytes = struct.pack("<f", cscale) + pack_nbit(codes, 2)
            for norm_bits in (4, 8):
                nq, ndeq, nlo, nscale = quantize_norms(norms, norm_bits)
                recon = cq[labels] * ndeq[:, None]
                cmean, cp05, nmse, oerr = metrics(w, recon, seed + k + norm_bits)
                hblob = pack_huffman(labels, lens)
                nblob = struct.pack("<ff", nlo, nscale) + pack_nbit(nq, norm_bits)
                packed = cbytes + hblob + nblob
                route, lbytes = choose_lossless(packed)

                centroid_bits = 16 if centroid_mode == "fp16" else 2
                fixed_index_bits = math.ceil(math.log2(k))
                fixed_bytes = math.ceil(k * in_dim * centroid_bits / 8) + math.ceil(out_dim * fixed_index_bits / 8) + math.ceil(out_dim * norm_bits / 8) + 128
                # Extrapolated from sampled Huffman code lengths. Add K code-length bytes.
                huff_bytes = math.ceil(k * in_dim * centroid_bits / 8) + math.ceil(out_dim * avg_huff / 8) + math.ceil(out_dim * norm_bits / 8) + k + 128
                results.append(
                    QuantResult(
                        tensor=name,
                        shape=[out_dim, in_dim],
                        sample_rows=len(w),
                        input_dim=in_dim,
                        k=k,
                        centroid_mode=centroid_mode,
                        norm_bits=norm_bits,
                        row_cosine_mean=cmean,
                        row_cosine_p05=cp05,
                        nmse=nmse,
                        output_rel_l2=oerr,
                        sample_index_entropy_bits=H,
                        sample_huffman_bits_per_index=avg_huff,
                        structural_bytes_fixed_index=fixed_bytes,
                        structural_ratio_vs_bf16=raw_full / fixed_bytes,
                        estimated_bytes_huffman=huff_bytes,
                        estimated_ratio_huffman_vs_bf16=raw_full / huff_bytes,
                        packed_sample_bytes=len(packed),
                        best_lossless_route=route,
                        lossless_bytes=lbytes,
                        lossless_ratio_on_packed_sample=len(packed) / max(lbytes, 1),
                    )
                )
    return results


def choose_tensors(headers: dict[str, tuple[dict, int]], max_tensors: int) -> list[tuple[str, str, dict, int]]:
    entries = []
    for shard, (header, data_start) in headers.items():
        for name, e in header.items():
            if name == "__metadata__" or not isinstance(e, dict):
                continue
            if len(e.get("shape", [])) != 2 or e.get("dtype") not in DTYPE_BYTES:
                continue
            entries.append((name, shard, e, data_start))
    by_name = {x[0]: x for x in entries}
    wanted = [
        "model.embed_tokens.weight",
        "model.layers.0.self_attn.q_proj.weight",
        "model.layers.0.mlp.gate_proj.weight",
        "model.layers.10.mlp.down_proj.weight",
        "model.layers.20.self_attn.o_proj.weight",
        "model.layers.20.mlp.up_proj.weight",
        "model.layers.39.self_attn.q_proj.weight",
        "model.layers.39.mlp.down_proj.weight",
        "lm_head.weight",
    ]
    chosen = [by_name[n] for n in wanted if n in by_name]
    if len(chosen) < max_tensors:
        seen = {x[0] for x in chosen}
        for x in sorted(entries):
            if x[0] not in seen and "model.layers." in x[0]:
                chosen.append(x)
                seen.add(x[0])
            if len(chosen) >= max_tensors:
                break
    return chosen[:max_tensors]


def structural_whole_model(headers: dict[str, tuple[dict, int]], k: int, centroid_bits: int, norm_bits: int) -> dict:
    total_raw = 0
    total_struct = 0
    matrices = 0
    vectors_raw = 0
    for header, _ in headers.values():
        for name, e in header.items():
            if name == "__metadata__" or not isinstance(e, dict):
                continue
            shape = e.get("shape", [])
            dtype = e.get("dtype")
            if dtype not in DTYPE_BYTES:
                continue
            n = int(np.prod(shape)) if shape else 0
            raw = n * DTYPE_BYTES[dtype]
            total_raw += raw
            if len(shape) == 2:
                out_dim, in_dim = map(int, shape)
                idx_bits = math.ceil(math.log2(k))
                total_struct += math.ceil(k * in_dim * centroid_bits / 8)
                total_struct += math.ceil(out_dim * idx_bits / 8)
                total_struct += math.ceil(out_dim * norm_bits / 8)
                total_struct += 128
                matrices += 1
            else:
                # Keep 1D/other tensors BF16/native in this arithmetic rather than
                # silently claiming extra compression.
                total_struct += raw
                vectors_raw += raw
    return {
        "k": k,
        "centroid_bits": centroid_bits,
        "norm_bits": norm_bits,
        "raw_checkpoint_bytes_from_headers": total_raw,
        "structural_bytes_fixed_index": total_struct,
        "structural_ratio": total_raw / max(total_struct, 1),
        "matrix_count": matrices,
        "non_matrix_bytes_kept_native": vectors_raw,
    }


def write_markdown(report: dict, path: Path) -> None:
    rows = report["results"]
    # Best symmetric 2-bit / 4-bit norm row for each tensor at each K.
    filt = [r for r in rows if r["centroid_mode"] == "symmetric-2bit" and r["norm_bits"] == 4]
    lines = [
        "# NEXUS DWE real 12B weight probe",
        "",
        f"Model: `{report['model']}` @ `{report['revision']}`",
        "",
        "Real BF16 tensor byte ranges were read from official Safetensors shards. No synthetic weights are used in the distortion table.",
        "",
        "## Whole-model structural arithmetic",
        "",
        "| K | centroid bits | norm bits | projected bytes | ratio vs BF16 |",
        "|---:|---:|---:|---:|---:|",
    ]
    for x in report["whole_model_structural"]:
        lines.append(f"| {x['k']} | {x['centroid_bits']} | {x['norm_bits']} | {x['structural_bytes_fixed_index']:,} | {x['structural_ratio']:.2f}x |")
    lines += [
        "",
        "This table is only the representation-size arithmetic. It says nothing about model quality; the distortion table below is the falsification gate.",
        "",
        "## Real-weight distortion: symmetric 2-bit centroids + 4-bit row norms",
        "",
        "| tensor | K | sample rows | cosine mean | cosine p05 | NMSE | random-activation rel L2 | index H | Huffman b/index | packed lossless |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in filt:
        lines.append(
            f"| `{r['tensor']}` | {r['k']} | {r['sample_rows']} | {r['row_cosine_mean']:.4f} | {r['row_cosine_p05']:.4f} | {r['nmse']:.4f} | {r['output_rel_l2']:.4f} | {r['sample_index_entropy_bits']:.3f} | {r['sample_huffman_bits_per_index']:.3f} | {r['lossless_ratio_on_packed_sample']:.2f}x ({r['best_lossless_route']}) |"
        )
    literal = [r for r in rows if r["centroid_mode"] == "literal-pasted-2bit" and r["norm_bits"] == 4]
    lines += [
        "",
        "## Literal quantizer from the pasted sketch",
        "",
        "The pasted code rounds signed centroids and then clamps to `[0,3]`, which destroys all negative centroid values. The benchmark keeps this path as a control instead of silently fixing it.",
        "",
        "| tensor | K | cosine mean | NMSE | random-activation rel L2 |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in literal:
        lines.append(f"| `{r['tensor']}` | {r['k']} | {r['row_cosine_mean']:.4f} | {r['nmse']:.4f} | {r['output_rel_l2']:.4f} |")
    lines += [
        "",
        "## Interpretation rule",
        "",
        "A tiny projected file is not a success if real-weight cosine/output error is destructive. Promotion requires both a storage win and a preregistered quality gate on full-model perplexity/tasks.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=384)
    ap.add_argument("--ks", type=int, nargs="+", default=[16, 32, 64, 128])
    ap.add_argument("--max-tensors", type=int, default=8)
    ap.add_argument("--out-json", default="benchmarks/NEXUS_DWE_REAL_12B.json")
    ap.add_argument("--out-md", default="benchmarks/NEXUS_DWE_REAL_12B.md")
    args = ap.parse_args()

    t0 = time.time()
    headers: dict[str, tuple[dict, int]] = {}
    for shard in SHARDS:
        print(f"[header] {shard}", flush=True)
        headers[shard] = safetensors_header(shard)

    structural = []
    for k in args.ks:
        structural.append(structural_whole_model(headers, k, 2, 4))
        structural.append(structural_whole_model(headers, k, 2, 8))
        structural.append(structural_whole_model(headers, k, 16, 4))

    chosen = choose_tensors(headers, args.max_tensors)
    all_results: list[dict] = []
    sampled = []
    for idx, (name, shard, entry, data_start) in enumerate(chosen):
        rows = min(args.rows, int(entry["shape"][0]))
        print(f"[tensor] {name} {entry['shape']} from {shard}, rows={rows}", flush=True)
        w, row0 = tensor_rows(shard, entry, data_start, rows)
        sampled.append({"name": name, "shape": entry["shape"], "dtype": entry["dtype"], "shard": shard, "row0": row0, "rows": rows})
        for r in tensor_benchmark(name, entry["shape"], w, args.ks, 1701 + idx * 1000):
            all_results.append(asdict(r))

    report = {
        "schema": "shtenco.nexus-dwe-real-12b/v1",
        "model": MODEL,
        "revision": REVISION,
        "source": "official Hugging Face Safetensors byte ranges",
        "elapsed_seconds": time.time() - t0,
        "sampled_tensors": sampled,
        "whole_model_structural": structural,
        "results": all_results,
        "notes": [
            "Distortion is measured on real BF16 weight rows, not synthetic tensors.",
            "Whole-model size rows are structural arithmetic from all five Safetensors headers; they are not quality claims.",
            "The literal pasted 2-bit quantizer is intentionally tested despite its sign-clipping bug.",
            "Random-activation relative L2 uses deterministic Gaussian probe vectors, not calibration-text activations.",
            "Full-model perplexity/task evaluation is required before any method can be promoted.",
        ],
    }
    outj = Path(args.out_json)
    outm = Path(args.out_md)
    outj.parent.mkdir(parents=True, exist_ok=True)
    outj.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, outm)
    print(json.dumps({"elapsed_seconds": report["elapsed_seconds"], "results": len(all_results), "json": str(outj), "md": str(outm)}, indent=2))


if __name__ == "__main__":
    main()
