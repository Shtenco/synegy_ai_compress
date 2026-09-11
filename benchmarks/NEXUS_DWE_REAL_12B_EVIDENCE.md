# NEXUS DWE real 12B falsification evidence

Model: `mistralai/Mistral-Nemo-Base-2407`
Pinned revision: `2045759120154383da48ee84ce4bf2f90cc6ec1f`
Checkpoint dtype: BF16
Official checkpoint bytes: `24,495,564,800`

Provenance: a public GitHub Actions runner on temporary branch `Shtenco/binary_quantum_theory:exp/nexus-dwe-real-12b` read real byte ranges from the official five Safetensors shards and committed the raw JSON/Markdown evidence. Benchmark job `34556362131` completed successfully. The public runner is used only as compute/evidence transport; compression authority remains `Shtenco/ai_compress`.

## What was tested

The supplied DWE++ hypothesis represents each complete matrix row as:

`row ~= quantized_norm[row] * quantized_centroid[index[row]]`

with K in {16,32,64,128}, row normalization, MiniBatchKMeans, 4/8-bit row norms, and either FP16 centroids, the literal supplied 2-bit centroid quantizer, or a corrected signed symmetric 2-bit centroid quantizer.

Real BF16 samples were read from embeddings, lm_head, attention and MLP matrices across layers 0, 10, 20 and 39. The benchmark also used all five Safetensors headers to compute exact whole-model representation arithmetic.

## Exact whole-model structural arithmetic

| K | Centroid bits | Norm bits | Projected size | Ratio vs BF16 | Effective bpw |
|---:|---:|---:|---:|---:|---:|
| 16 | 2 | 4 | 9.552 MiB | 2445.6x | 0.00654 |
| 32 | 2 | 4 | 16.556 MiB | 1411.0x | 0.01134 |
| 64 | 2 | 4 | 30.318 MiB | 770.5x | 0.02076 |
| 128 | 2 | 4 | 57.595 MiB | 405.6x | 0.03945 |
| 64 | 16 | 4 | 219.536 MiB | 106.4x | 0.15036 |
| 128 | 16 | 4 | 436.032 MiB | 53.6x | 0.29864 |

These are representation sizes, not quality claims. Their extreme smallness is itself a warning: complete high-dimensional rows are being forced through only 16-128 directions per tensor.

## Real-weight quality gate: corrected symmetric 2-bit centroids + 4-bit norms

Selected results:

| Tensor | K | Mean row cosine | NMSE | Random-activation relative L2 |
|---|---:|---:|---:|---:|
| embed_tokens | 64 | 0.3266 | 2.5444 | 1.4269 |
| embed_tokens | 128 | 0.4861 | 2.5365 | 1.9389 |
| layer0 q_proj | 16 | 0.3656 | 5.8731 | 2.2934 |
| layer0 q_proj | 64 | 0.4691 | 17.6963 | 4.3117 |
| layer0 q_proj | 128 | 0.5244 | 36.8776 | 6.6973 |
| layer0 gate_proj | 16 | 0.1925 | 1.8316 | 1.1722 |
| layer20 o_proj | 64 | 0.3237 | 6.3597 | 2.1854 |
| layer20 up_proj | 32 | 0.2113 | 2.6581 | 1.3776 |
| layer39 q_proj | 64 | 0.3606 | 6.0246 | 2.2859 |
| layer39 down_proj | 64 | 0.3052 | 166.5266 | 11.0738 |
| lm_head | 64 | 0.4225 | 13.5040 | 3.0230 |

This fails the quality gate decisively. The row-prototype representation is too restrictive before any full-model perplexity evaluation is warranted.

## Literal supplied 2-bit quantizer bug

The supplied sketch computes a signed value and then clamps it to `[0,3]`. Negative centroid components are therefore destroyed. On real weights the control generally produced NMSE around 0.9-1.0 and random-activation relative L2 near 1.0. It must not be used.

## Additional storage observation

The packed 2-bit centroid / index / norm sample streams still had measurable redundancy: standard LZMA generally reduced the packed sample by roughly 1.76x-1.92x in the corrected symmetric-2bit table. This supports keeping a second-stage lossless ModelStore layer, but only after the primary numeric representation passes quality gates.

## Verdict

**FALSIFIED as a whole-row 16-128 prototype compressor.**

Do not promote the original DWE++ formula to NEXUS. Preserve the useful MDL concept, entropy-coded indices and model-aware storage, but replace whole-row prototypes with a higher-capacity representation such as block/product VQ, residual/additive VQ, low-rank-plus-residual, or proven sub-1/2-bit quantization. Re-run on real weights before full-model evaluation.
