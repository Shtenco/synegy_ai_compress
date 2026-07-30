# Exact all-systems benchmark methodology

## Scope

The runner discovers every unique engine name from:

1. `egd256_web_app_v3.ENGINES` (35 Compression Lab systems);
2. `benchmark_graph_ai_v51.engine_suite()` (additional Graph-AI/GRAAL systems, duplicates removed);
3. UMC-256 in `fast`, `balanced`, and `max` modes;
4. RAW STORE as a reference baseline.

## Corpus

Eleven deterministic 32,768-byte datasets generated from seed `20260730`:

- source code;
- JSON graph logs;
- CSV telemetry;
- repeated text;
- related version snapshots;
- sparse model weights;
- fixed-width structured binary records;
- image-like spatial bytes;
- BIP39 word text;
- heterogeneous mixed content;
- pseudorandom bytes.

## Timing

- GitHub Actions `ubuntu-24.04`;
- Python 3.11;
- pinned dependencies from `requirements_v4.txt`;
- `PYTHONHASHSEED=0`;
- one untimed warm-up;
- three timed repetitions;
- `time.perf_counter_ns()`;
- garbage collection performed before and disabled during each timed operation;
- reported times and sizes are medians; min/max are preserved.

## Correctness

Every warm-up and timed repetition must satisfy:

```text
compress(source) -> archive
decompress(archive) -> restored
restored == source
SHA256(restored) == SHA256(source)
```

A system with one failed dataset is excluded from full-pass aggregate rankings but remains visible in raw reports.

## Rankings

No single metric is called universally best. Separate rankings are produced for:

- geometric-mean compression ratio;
- total median encoding time;
- geometric-mean `ratio / encode_ms` score;
- balanced encode/decode score;
- Pareto frontier of ratio versus encoding time;
- winner by dataset.

Archive byte hashes are compared across timed repetitions. Non-identical archives are reported as non-deterministic, with the byte-size variation retained.
