# OMNIA-REX V1 — predictive/residual frontier

## Goal

OMNIA-REX V1 combines the existing exact SHTENCO compression portfolio with
new REVERSE-EXP predictors. It is a verified meta-codec, not a universal
compression claim.

Pipeline:

```text
input
  -> conventional baselines
  -> PPM arithmetic prediction
  -> BWT/MTF rank transform
  -> spatial causal predictors
  -> sparse prediction residual
  -> exact OMNIA / Gabriel Horn / Math V3 adapters
  -> decode + byte equality + SHA-256
  -> minimum complete archive
```

QTD3 remains a separate shared-model track. Its model bytes and cold-start cost
must be reported; the shared model is never counted as free in the standalone
leaderboard.

## Correctness invariant

A candidate can win only after:

1. complete decode;
2. exact byte equality;
3. original-size equality;
4. SHA-256 equality.

High-entropy input can fall back to RAW.

## Preliminary frozen-corpus probe

A standalone probe was run on the same deterministic 11 x 32 KiB corpus used by
the 2026-07-30 Tier-1 benchmark. This probe used the complete OMNIA-REX outer
container, including its SHA-256 header.

Preliminary OMNIA-REX geomean ratio:

```text
32.6620465x
```

Historical exact result on the same frozen corpus:

```text
SHTENCO OMNIA TIER1 V2 MAX = 30.335995x
```

Relative geomean improvement of the preliminary probe:

```text
+7.67%
```

This is not yet the final repository-native ranking because the local probe did
not have the full private repository dependency environment. The CI benchmark
in this branch is the promotion gate: it imports the actual OMNIA, Gabriel Horn
and Math V3 engines from the repository and runs them together with OMNIA-REX.

### Strong preliminary REX cases

| dataset | raw | best complete OMNIA-REX probe archive | route |
|---|---:|---:|---|
| version_snapshots | 32,768 B | 388 B | REX spatial residual |
| sparse_weights | 32,768 B | 517 B | REX BWT/MTF rank |
| structured_binary | 32,768 B | 1,366 B | REX spatial residual |
| image_like | 32,768 B | 219 B | REX spatial residual |
| mixed | 32,768 B | 9,231 B | REX spatial residual |
| random | 32,768 B | 32,813 B | RAW fallback |

For text-heavy rows Brotli-11 often remains the winning internal route. That is
intentional: OMNIA-REX is a portfolio search for minimum stored uncertainty, not
an attempt to force REVERSE-EXP onto every corpus.

## Shared-model track

QTD3 should be benchmarked separately:

```text
past corpus/history
    -> shared temporal model
    -> external-LZ / candidate chunks
    -> references + literal residual
    -> verified target
```

Required reporting:

- target bytes;
- QTD3 container bytes;
- model serialized bytes;
- cold total = model + first target;
- model coverage;
- amortized target count;
- exact byte/SHA round-trip.

No shared-model result is allowed into the standalone ranking without charging
the model.

## Promotion criteria

OMNIA-REX becomes GREEN only if the repository-native run shows:

- 11/11 exact datasets;
- zero SHA failures;
- complete baselines for Brotli, Zstd, LZMA and current OMNIA;
- actual legacy expert imports, not substitute implementations;
- geomean and total-byte frontier reported separately;
- runtime cost reported next to ratio;
- high-entropy fallback does not hide expansion.

## Next steps

1. Run the repository-native CI suite.
2. Add strict QTD3 shared-model benchmark as a second leaderboard.
3. Add ablation: remove PPM, BWT, spatial, Gabriel, Math and QTD3 one at a time.
4. Build a learned/MDL router only after the exhaustive MAX frontier is frozen.
5. Extend to real external corpora after the deterministic 11-dataset regression is stable.
