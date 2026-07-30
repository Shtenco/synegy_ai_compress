# SHTENCO Unified Tier-1 v2 — exact benchmark result

Date: 2026-07-30 UTC. Branch result commit: `dfef632984fde43c0c58da2782c0d433c28f9c91`.

## Scope and integrity

- frozen exact baseline: 69 systems;
- current exact rerun: 14 active Tier-1/Gabriel/OMNIA systems;
- combined unique inventory: 76 systems;
- deterministic corpus: 11 datasets × 32,768 bytes;
- current exact rows: 154/154 PASS;
- every accepted row: byte equality and SHA-256;
- legacy source commit: `c681ec94fe5194156b71fc304035f7aaff4d2327`;
- legacy full artifact SHA-256: `bb769fa6c1b65d697e66d79ac3275b1715ee0c77186669377e783734fcc47296`;
- unified GitHub Actions artifact digest: `f7542bdd2a08e4de3c6d04e484fd796beb126e42e77de639904216c5b4595aad`;
- packaged reproducibility ZIP SHA-256: `8c75264d4b9ffc45020f6ca1e853b2efe3aa59e803d11718a0f4e8e1d8e55230`.

Archive-size rankings are directly comparable because the frozen and current measurements use the same corpus bytes. Timing rankings are separated by run. Heavy `MAX` profiles use one exact measurement on every dataset and are excluded from score rankings; normal profiles use one warm-up plus three measured repetitions.

## Combined TOP-10 by geometric-mean compression ratio

| Rank | Engine | Ratio | Timing protocol |
|---:|---|---:|---|
| 1 | SHTENCO OMNIA TIER1 V2 MAX | **30.335995×** | single exact; not score-ranked |
| 2 | SHTENCO OMNIA TIER1 V2 BALANCED | **27.235040×** | warm-up + 3 |
| 3 | SHTENCO GABRIEL-HORN TIER1 MAX | **24.759551×** | single exact; not score-ranked |
| 4 | SHTENCO GABRIEL-HORN TIER1 BALANCED | **24.459013×** | warm-up + 3 |
| 5 | SHTENCO GRAAL-IGC TIER1 MAX | **22.633934×** | warm-up + 3 |
| 6 | SHTENCO TSC-X TIER1 SPATIAL | 22.114639× | warm-up + 3 |
| 7 | SHTENCO SABF-X ULTIMATE GRAPH-AI | 21.920991× | frozen exact run |
| 8 | SHTENCO TSC-X TURBOSPATIAL GRAPH-AI | 21.907299× | frozen exact run |
| 9 | SHTENCO HACE-X CASCADE GRAPH-AI | 21.021521× | frozen exact run |
| 10 | SHTENCO NEXUS-UMC TIER1 | 19.674641× | warm-up + 3 |

All five ratio TOP-5 positions are SHTENCO systems. Relative to the previous production ratio leader `GRAAL-IGC TIER1 MAX`, OMNIA MAX improves the geometric-mean ratio by about 34.03%, and OMNIA Balanced by about 20.33%.

## Current TOP-10 by ratio / encode-time score

| Rank | Engine | Ratio | Score | Total encode time, 11 datasets |
|---:|---|---:|---:|---:|
| 1 | SHTENCO SABF-X TIER1 SPEED | 16.500986× | **118.317876** | 1.642 ms |
| 2 | SHTENCO PBM-39X TIER1 | 16.500986× | **96.452109** | 2.517 ms |
| 3 | SHTENCO SABF-X TIER1 BALANCED | 17.093538× | **20.359616** | 9.286 ms |
| 4 | SHTENCO GRAAL-AIS TIER1 | 19.206956× | **14.675943** | 19.796 ms |
| 5 | SHTENCO NEXUS-UMC TIER1 | 19.674641× | **12.318960** | 22.290 ms |
| 6 | SHTENCO TSC-X TIER1 SPATIAL | 22.114639× | 7.863649 | 31.763 ms |
| 7 | SHTENCO OMNIA TIER1 V2 SPEED | 19.403181× | 4.621028 | 50.985 ms |
| 8 | SHTENCO GRAAL-IGC TIER1 MAX | 22.633934× | 4.429738 | 57.206 ms |
| 9 | SHTENCO OMNIA TIER1 V2 BALANCED | 27.235040× | 0.285008 | 9,837.787 ms |
| 10 | SHTENCO GABRIEL-HORN TIER1 SPEED | 12.445315× | 0.105844 | 1,325.464 ms |

All five current score TOP-5 positions are SHTENCO systems. The speed champion remains SABF-X Tier1 Speed; OMNIA is primarily the new ratio frontier rather than a replacement for the low-latency profiles.

## What OMNIA MAX actually selected

OMNIA MAX is a verified portfolio, not a new entropy coder pretending to beat information theory. On the exact corpus it selected:

- Brotli-11 for source code, JSON logs, BIP39 text and mixed content;
- Brotli-4 for repeated text;
- delta + Zstd-12 for version snapshots and image-like data;
- RLE + Zstd-3 for sparse weights;
- Gabriel MAX for structured binary data;
- RAW for pseudorandom bytes.

Each route is stored in one compact SHA-256 container and admitted only after exact decompression verification.

## Tier-1 v2 conclusions

1. The historical 69-system result was not discarded. It is preserved as a cryptographically identified frozen baseline and merged with current exact measurements on identical corpus bytes.
2. OMNIA MAX is the new byte-minimizing production frontier for this fixed benchmark.
3. OMNIA Balanced is the practical high-ratio profile: second overall ratio with bounded evidence-based routing.
4. SABF-X Tier1 Speed remains the score/speed leader.
5. Gabriel Horn is strongest as a structural expert inside the portfolio and as a dedicated numeric/versioned codec; it is not the universal text winner.
6. RAW remains mandatory for high-entropy input.
7. No universal superiority claim is made beyond this fixed reproducible corpus and methodology.

Full JSON, per-row CSV, combined summary, console log, source provenance and all active engine source files are contained in the GitHub Actions artifact `SHTENCO_UNIFIED_TIER1_V2_FULL_ARTIFACT`.
