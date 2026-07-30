# Compression migration manifest

## Source

- Repository: `Shtenco/agi_olga`
- Exact compression snapshot commit: `c681ec94fe5194156b71fc304035f7aaff4d2327`
- Pre-compression AGI baseline: `9bddab2d78f8f981c7f4cc380798c41ff88bc837`

The source snapshot contains all 34 compression additions: four CI workflows and thirty files under `compression_lab/`, including V3, V4/UMC-256, Graph-AI V5.2, Tier-1 engines, tests, benchmarks and documentation.

## Destination

- Repository: `Shtenco/ai_compress`
- Immutable gitlink: `source_snapshot` -> source commit above
- Active standalone Tier-1 engine: `compression_lab/shtenco_tier1_engines.py`

## AGI repository cleanup

`Shtenco/agi_olga/main` cleanup commit: `473cf199d3e6d4c559f5bb5ed0449026ba91cd3a`.

A GitHub tree comparison between the AGI baseline and cleaned `main` reports zero changed files. Therefore the article/AGI-benchmark graph-AI version is preserved byte-for-byte in the active AGI tree.
