# NEXUS block PQ / residual VQ — real Mistral-Nemo 12B evidence

Model: `mistralai/Mistral-Nemo-Base-2407`
Pinned revision: `2045759120154383da48ee84ce4bf2f90cc6ec1f`
Checkpoint: BF16, 24,495,564,800 bytes.

Provenance: public compute-only experiment branch `Shtenco/binary_quantum_theory:exp/nexus-dwe-real-12b`, GitHub Actions run `34556590571`, SUCCESS. Real BF16 byte ranges were read from the official five Safetensors shards. Compression authority remains `Shtenco/ai_compress`.

## Why this experiment exists

The previous whole-row DWE test was falsified: forcing a 5k-14k dimensional row to one of only 16-128 directions destroys the matrix. This experiment retains the useful MDL/codebook idea but moves vector quantization to short subvectors and optionally quantizes residuals.

Each stage uses K=256 direction codewords, one 8-bit index per block, one 4-bit log-norm per block, INT8 codebooks and one FP16 scale per codeword.

## Whole-model structural arithmetic

| config | block | stages | size | effective bpw | BF16 ratio |
|---|---:|---:|---:|---:|---:|
| PQ8x1 | 8 | 1 | 2.140 GiB | 1.501 | 10.7x |
| PQ16x1 | 16 | 1 | 1.071 GiB | 0.751 | 21.3x |
| RVQ16x2 | 16 | 2 | 2.142 GiB | 1.502 | 10.7x |
| RVQ32x2 | 32 | 2 | 1.075 GiB | 0.754 | 21.2x |
| RVQ64x2 | 64 | 2 | 0.544 GiB | 0.382 | 41.9x |

For a 70B model, 0.754 bpw corresponds to about 6.6 GB of raw parameter payload before container/runtime overhead, so the target capacity region is arithmetically reachable.

## Real-weight quality

Representative random-activation relative L2 error:

| tensor | PQ8x1 1.50 bpw | PQ16x1 0.75 bpw | RVQ16x2 1.50 bpw | RVQ32x2 0.75 bpw | RVQ64x2 0.38 bpw |
|---|---:|---:|---:|---:|---:|
| embedding | 0.5602 | 0.7225 | 0.5364 | 0.6944 | 0.8318 |
| layer0 q_proj | 0.4265 | 0.6249 | 0.5086 | 0.6799 | 0.7246 |
| layer0 gate_proj | 0.5344 | 0.7410 | 0.5728 | 0.7692 | 0.8303 |
| layer20 up_proj | 0.5188 | 0.7673 | 0.5325 | 0.7409 | 0.8332 |
| layer39 down_proj | 0.5200 | 0.7294 | 0.5850 | 0.7350 | 0.8611 |

At 1.50 bpw, mean row cosine is roughly 0.83-0.91 depending on tensor. At 0.75 bpw it falls to roughly 0.66-0.77. This is substantially better than whole-row DWE but still far from a safe inference representation without calibration-aware optimization and a full-model quality test.

## Entropy / second-stage compression result

Index entropy is typically ~7.9-8.0 bits for the K=256 codebooks. Therefore the supplied hypothesis that Huffman would remove 30-50% of code-index bytes is not supported on these real samples: assignments are close to uniform. Standard lossless compression of the packed samples is modest, typically ~1.05x-1.22x.

This means future capacity improvements must come primarily from the numeric representation itself, not from optimistic entropy coding of near-uniform code indices.

## Verdict

- Whole-row DWE K=16-128: **FALSIFIED**.
- Naive block PQ/RVQ: **GEOMETRY WORKS BETTER, QUALITY STILL INSUFFICIENT IN THE 0.38-1.50 BPW REGION**.
- Huffman 30-50% index saving: **NOT OBSERVED**.
- Lossless wrapper remains useful opportunistically, but is a secondary gain.

## Next candidate

Use activation/calibration-aware distortion rather than Euclidean K-means, shared/blockwise affine scales, additive codebooks with a fixed total bit budget, explicit outlier residuals, and/or a proven sub-1/2-bit primary method. Keep the same real-weight and full-model falsification gates.
