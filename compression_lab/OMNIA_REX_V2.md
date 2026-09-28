# OMNIA-REX V2 — shared-memory accounting, ablation and MDL router

## Status

V2 extends V1 in three directions:

1. **QTD3 shared memory with honest accounting** — transport bytes are reported separately from model bytes, cold total and amortized cost.
2. **Ablation** — measure which predictor families actually move the compression frontier.
3. **MDL router** — predict per-family description length and evaluate only a small Top-K candidate set instead of exhaustive MAX.

The key scientific distinction remains:

- standalone codecs compete on complete stored bytes;
- QTD3 is a shared-model codec and its external model is never treated as free.

## 1. Ablation on frozen 11 x 32 KiB corpus

Internal REVERSE-EXP V3 family oracle:

```text
geomean ratio = 37.549249x
```

Winner count by dataset:

| family | wins |
|---|---:|
| Brotli-11 | 5 |
| spatial residual | 4 |
| BWT/MTF rank | 1 |
| RAW | 1 |

Remove-one-family ablation:

| removed family | geomean ratio | relative change |
|---|---:|---:|
| Brotli-11 | 32.492458x | -13.4671% |
| spatial residual | 33.317680x | -11.2694% |
| BWT/MTF rank | 36.071904x | -3.9344% |
| RAW | 37.548833x | -0.0011% |
| PPM anti-exp | 37.549249x | 0.0000% |
| spatial sparse | 37.549249x | 0.0000% |
| zlib-9 | 37.549249x | 0.0000% |
| LZMA-9 | 37.549249x | 0.0000% |

Interpretation: on this frozen corpus the frontier is currently carried mainly by three families:

```text
Brotli text backend
+ spatial predictive residual
+ BWT/MTF rank transform
```

PPM is still useful research infrastructure, but it does not win a full frozen dataset in this corpus.

## 2. MDL router — leave-one-dataset-out

The frozen 11 x 32 KiB corpus was split into 44 blocks of 8 KiB.

Features are cheap causal/static statistics:

- entropy;
- printable/zero fractions;
- adjacent equality;
- smoothness;
- 16-byte repetition;
- byte alphabet fraction;
- delta entropy;
- XOR-1 entropy;
- lag-16 equality;
- lag-256 equality.

For every block exhaustive MAX supplied the true byte cost of all eight families. An ExtraTrees regressor predicted `log2(bytes)` per family.

Evaluation protocol: **leave one entire dataset out**. No block from the held-out dataset is used for fitting.

### Result

| policy | families evaluated | family search reduction | byte regret vs oracle |
|---|---:|---:|---:|
| Top-1 | 1 / 8 | 87.5% | 10.2882% |
| **Top-2** | **2 / 8** | **75.0%** | **0.3599%** |
| Top-3 | 3 / 8 | 62.5% | 0.3599% |
| Top-4 | 4 / 8 | 50.0% | 0.3599% |

Top-2 is the useful operating point. Top-1 is too aggressive.

## 3. Frozen safety guards

Development error analysis exposed two cheap exceptional regimes:

```text
zero > 0.90
    -> always also evaluate BWT/MTF rank

entropy > 7.90
and repeat16 < 0.05
and lag256_equal < 0.05
    -> always also evaluate RAW
```

These guards were then frozen before the external test.

On the 44 development blocks, Top-2 + these guards reproduced the oracle byte total exactly while evaluating on average 2.18 of 8 families. This is post-development evidence only and is not used as an external claim.

## 4. External held-out test

The frozen router and guards were then evaluated on 11 blocks from the previously created REVERSE-EXP V3 corpus:

- Markdown;
- structured grayscale raster;
- random bytes;
- uploaded Markdown;
- source code.

These blocks were not used for router fitting.

Result:

```text
oracle bytes            = 33,130
router bytes            = 33,211
byte regret             = 0.244491%
average families tried  = 2.1818 / 8
family search reduction = 72.7273%
exact oracle-byte blocks= 9 / 11
```

The two misses were both on the highly regular synthetic raster, where the external oracle selected `spatial_sparse`. Text, source-code and random blocks matched the oracle.

This means the router result is promising but not yet a universal zero-regret claim.

## 5. QTD3 shared-memory accounting

V2 introduces `QTD3SharedLayer`.

For every shared-model result it records:

```text
target_bytes
container_bytes
model_bytes
cold_total_bytes = model_bytes + container_bytes
reuse_count
amortized_bytes = container_bytes + model_bytes / reuse_count
coverage_percent
break-even reuses vs standalone
exact round-trip
```

Therefore a QTD3 result can win only under an explicit reuse assumption. A 500-byte transport container backed by a 10 MB model is not reported as a 500-byte cold archive.

The historical QTD3 proof in `synergy_qr_compress` remains relevant external evidence: three real future Git targets totaled 10,011 source bytes and 2,392 QTD3 containers versus 3,195 bytes for direct Brotli-11, with exact byte/SHA restoration and strict temporal/leakage checks. That proof reported transport savings; V2 adds the missing generic model-amortization decision layer on top.

A fresh cross-repository V2 QTD3 run with full model-byte accounting is still required before promoting the shared layer to GREEN.

## Verdict

### GREEN

- exact V1 predictive/residual codec path;
- full-family ablation;
- leave-one-dataset-out MDL router methodology;
- external held-out router result;
- explicit QTD3 model-cost accounting API.

### OPEN

- fresh QTD3 cross-repository V2 execution with model bytes and reuse frontier;
- larger unrelated external corpus;
- direct wall-clock comparison of Top-2 router vs exhaustive MAX;
- retraining/freeze protocol on a larger corpus;
- integration of learned router into the final serialized archive format.

## Current practical result

The strongest V2 finding is not a new compression-ratio record. It is the computational result:

```text
exhaustive MAX: 8 candidate families
        ↓
MDL Top-2 + frozen guards
        ↓
~2.18 families evaluated on average
        ↓
72.7% search reduction
        ↓
0.244% byte regret on external held-out blocks
```

This is the first evidence that the OMNIA-REX frontier can potentially be made practical without paying the full exhaustive search cost.
