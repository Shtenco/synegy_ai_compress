# AI Compress as SINERGY memory and archive layer

Status: additive integration document. Existing compression engines, benchmarks, source snapshots and historical generations remain unchanged.

## Repository role

`Shtenco/ai_compress` owns lossless compression, MDL-routing and archive technologies that can support long-horizon SINERGY memory.

It does not become the canonical financial ledger and does not infer accounting truth merely from compression ratios.

## Existing preservation model

The repository already demonstrates the desired non-destructive pattern through its immutable `source_snapshot`, which retains historical compression files, tests and V3/V4/V5.2/Tier-1 generations.

The wider SINERGY federation should follow the same principle:

```text
new canonical layer
    |
    +-- references immutable historical source
    +-- preserves original evidence
    +-- adds new adapters/tests side-by-side
```

## Economic-memory direction

Potential inputs include high-volume, append-only or time-series data such as:

- canonical ledger event exports;
- market and macro snapshots;
- economic telemetry;
- goods/inventory/project evidence;
- settlement summaries;
- AI proposal/evaluation traces;
- public audit artifacts;
- historical simulation states.

Sensitive data remains subject to privacy, legal and security policy before archival or model use.

## Memory tiers

Reference architecture:

```text
HOT
recent canonical state / active graph

WARM
compressed episodic state + indexes + provenance

COLD
immutable historical archives / snapshots / raw evidence bundles
```

Compression must remain lossless when the archive is used as audit evidence.

## MDL / Compression State research

Compression length, route choice, residual structure and cross-compression similarity may be useful features for regime/state research. They are model-derived descriptors, not semantic or financial truth by themselves.

Reference distinction:

```text
compressed length -> compressor-dependent description-length signal
HardNAV           -> accounting value from external assets/liabilities
```

The two concepts must not be conflated.

## Provenance requirements

A federation archive object should ideally record:

- source repository/system;
- schema/version;
- source sequence/time range;
- codec/route/version;
- uncompressed byte count;
- archive byte count;
- SHA-256 or stronger content digest;
- exact round-trip verification status;
- privacy/classification metadata;
- retention policy.

## AI integration

OLGA/NEXUS may retrieve relevant compressed historical state through an approved memory layer. Retrieval should retain provenance to the original source and schema. A compressed or summarized memory cannot silently override a newer canonical FinancialSnapshot or external settlement record.

## Audit direction

For audit-critical archives, acceptance requires exact decompression and digest equality. Approximate semantic summaries may coexist but are not substitutes for the underlying exact archive.
