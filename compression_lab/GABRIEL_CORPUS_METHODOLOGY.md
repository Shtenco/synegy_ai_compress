# Gabriel Horn corpus benchmark methodology

## Purpose

This benchmark compares `GabrielHornEngine(profile="max")` with Zstandard 19,
Brotli 11, the active GRAAL-IGC Tier-1 engine and the exact historical UMC-256
snapshot. It does not claim a universally best compressor. The result is valid
only for the declared corpus, versions, parameters and machine.

## Correctness gate

Every measured repetition must complete:

1. compression;
2. decompression;
3. byte-for-byte equality;
4. SHA-256 equality;
5. verified random-range extraction.

A failed row is excluded from ranking and recorded in the JSON report. UMC-256
is included only if the exact `umc256_engine.py` snapshot can be imported. The
benchmark never substitutes NEXUS-UMC or another similarly named engine.

## Corpus

The built-in deterministic corpus contains seven equal-size streams:

- English-like text;
- newline-delimited JSON records;
- smooth little-endian signed 32-bit integers;
- versioned 1 KiB blocks with sparse edits;
- sparse binary data;
- Python-like source code;
- seeded high-entropy bytes.

`--corpus-dir` adds real files. Each input and its SHA-256 are written to report
metadata. Built-in generators and PRNG seeds are fixed in source.

## Parameters

Canonical exact comparison:

- Gabriel Horn: `profile=max`, `surface_weight=0`, `work_weight=0`;
- Zstandard: level 19, content size and checksum enabled;
- Brotli: quality 11, generic mode;
- GRAAL-IGC: active `GRAALIGCTier1Max` implementation;
- UMC-256: historical v2, `mode=max`, `latency_weight=0`.

Setting UMC latency weight to zero makes the MAX comparison size-oriented and
removes timing noise from its internal MDL selector. The original engine and
all its expert implementations still remain unchanged.

## Isolation and timing

Each warm-up and measured repetition runs in a fresh Python process. Reported
encode/decode values are medians. Throughput is calculated from uncompressed
bytes. Archive size must be deterministic across repetitions.

## Memory

`peak_rss_mib` is the absolute peak resident set size of the fresh worker,
including Python, imported libraries and native codec allocations. This is more
honest than Python-only allocation tracing, but it is machine-dependent.

## Random access

For Gabriel Horn the benchmark calls `decompress_range()` and estimates the
logical block bytes touched. For codecs without native range extraction, each
query performs a full decompression and then slices the requested bytes.

Reported metrics:

- median query latency in microseconds;
- access amplification = logical bytes inflated / requested bytes;
- native range support flag.

## Outputs

The harness produces:

- `gabriel_corpus_report.json` — complete machine-readable report;
- `gabriel_corpus_rows.csv` — every dataset/engine row;
- `gabriel_corpus_summary.csv` — aggregate ranking;
- `GABRIEL_CORPUS_BENCHMARK.md` — readable tables and configuration.

Lower archive ratio, random latency, amplification and RAM are better. Higher
throughput is better. No single combined score is used because weighting these
objectives would hide engineering trade-offs.
