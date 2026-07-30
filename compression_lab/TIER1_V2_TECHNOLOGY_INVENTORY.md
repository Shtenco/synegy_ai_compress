# SHTENCO Compression Technology Inventory — Tier-1 v2

This inventory consolidates the complete archive/compression lineage recovered from the project history, Library artifacts and the immutable historical snapshot `c681ec94fe5194156b71fc304035f7aaff4d2327`.

## Integrity boundary

Every ranked implementation must satisfy, for every warm-up and timed repetition:

```text
archive = compress(source)
restored = decompress(archive)
restored == source
SHA256(restored) == SHA256(source)
```

High-entropy input is allowed to select RAW. No mnemonic, curve, graph or Gabriel-Horn construction is treated as a way around information theory.

## Production engine lineage

- **SHTENCO HACE-X** — cascade/hyper-adaptive routing.
- **SHTENCO EGD-256** — multi-engine verified tournament and compact archive selection.
- **SHTENCO TSC-X** — spatial, byte-plane and structured-record transforms.
- **SHTENCO AMCE-100X** — high-strength multi-codec candidate evaluation.
- **SHTENCO SABF-X** — fast adaptive block filtering and low-latency route selection.
- **SHTENCO GRAAL-AIS** — AI-model/object/version storage and selective restoration.
- **SHTENCO RSX** — reversible structure transforms.
- **SHTENCO UMC-256** — MDL mixture of verified compression experts.
- **SHTENCO GRAAL-IGC** — Infoton/graph compression with content-defined blocks and version links.
- **SHTENCO Gabriel Horn** — indexed multi-scale residual shells, exact references and progressive structure.

## Reversible primitives recovered

- EAPR-8
- GFD-256
- RGD-X
- HGD-256
- BPF-X
- ADBF
- GCDC
- SDC
- SEM
- DCT-X
- CDF-X
- FAS-256
- APK-X
- ADS-X
- BXS
- BDR-X
- RSD-256
- MTS-X
- QBS-X
- HCC-X

The production v2 synthesis preserves the useful reversible ideas behind these names as explicit transforms or routing features rather than keeping unverifiable branding-only variants.

## BIP39 / SLOTA / SHTZIP lineage

- MICA-39
- UECB-39X
- DMB-39X
- ECBC-39
- PECB-39X
- SECB-39X
- BAPM-X
- PBM-39X
- BPD-39X
- CDC-RX
- ODC-XC
- ODC-XP
- DDR-X

Tier-1 v2 uses BIP39 only when the complete ASCII token stream consists of exact words from the official 2048-word dictionary. The reversible mapping is:

```text
word -> index 0..2047 -> exact 11-bit stream
```

For arbitrary bytes the route is unavailable. This removes the historical failure modes caused by unknown codes, truncated restoration and non-invertible mnemonic/curve assumptions.

## Graph and version technology

Recovered and retained ideas:

- content-defined chunking;
- chunk graphs and 256 route/community proposals;
- exact block references;
- XOR edges to parents or earlier versions;
- prefix/suffix patches;
- SimHash-style proposal features;
- graph-of-versions storage;
- verified executor after proposal;
- byte-plane transforms;
- stable object keys;
- independent block restoration;
- selective extraction;
- GGUF tensor segmentation;
- ONNX initializer segmentation;
- NPZ object-name segmentation;
- cross-version deduplication;
- XOR and XOR + byte-plane paths.

Graph-AI is used as a proposal mechanism. The final stored route is always selected and verified by an exact deterministic executor.

## Gabriel-Horn technology

The engineering interpretation is finite and lossless:

- dyadic modular lifting;
- first- and second-order deltas;
- lag-XOR predictors;
- byte shuffles;
- significance shells;
- exact repeated-block references;
- indexed blocks;
- progressive shell decoding;
- exact `decompress_range()`;
- SHA-256 archive verification.

Tier-1 v2 adds three separate profiles:

- **SPEED** — reduced transform and block search;
- **BALANCED** — bounded search with work/surface priors;
- **RANDOM-ACCESS** — explicit expected range-inflation penalty and a 4096-byte maximum candidate block.

The existing **MAX** profile remains a byte-minimizing reference.

## Tier-1 v1 engines preserved

- SHTENCO SABF-X TIER1 SPEED
- SHTENCO SABF-X TIER1 BALANCED
- SHTENCO PBM-39X TIER1
- SHTENCO GRAAL-AIS TIER1
- SHTENCO TSC-X TIER1 SPATIAL
- SHTENCO NEXUS-UMC TIER1
- SHTENCO GRAAL-IGC TIER1 MAX
- SHTENCO GABRIEL-HORN TIER1 MAX

These remain separate benchmark participants so improvements cannot erase or silently rewrite the historical result.

## Tier-1 v2 production synthesis

### SHTENCO OMNIA TIER1 V2 SPEED

A minimal verified portfolio:

- RAW;
- Zstd-1;
- Zstd-3;
- at most one feature-supported delta, shuffle or version route.

Goal: retain the SABF-X speed/score position without running expensive candidates.

### SHTENCO OMNIA TIER1 V2 BALANCED

A deterministic bounded selector using:

```text
F(x) = (entropy, printable ratio, zero ratio, adjacent repeats,
        local smoothness, block similarity, repeated 16-byte atoms)
```

Eligible paths include Zstd, Brotli for text, delta/shuffle for numeric data, version-XOR for related blocks, exact BIP39, GRAAL/NEXUS and Gabriel Balanced where structural evidence justifies the work.

### SHTENCO OMNIA TIER1 V2 MAX

A fixed exhaustive portfolio over:

- RAW;
- Zstd levels 1/3/7/12/19;
- Brotli qualities 4/9/11;
- zlib 1/9;
- LZMA 6/Extreme;
- delta-1 and delta-2;
- byte shuffle widths 2/4/8/16;
- lag-XOR 1/4/16/64/256/1024;
- version-XOR block sizes 512/1024/4096;
- RLE;
- exact BIP39;
- Tier-1 GRAAL/NEXUS/TSC;
- Gabriel Balanced/Max.

It minimizes actual final archive bytes inside a single SHA-256 container. It is intentionally slower and is not used to claim a speed victory.

## Mathematical objective

Tier-1 v2 separates objectives instead of calling one scalar universally optimal:

```text
J(c | x, Q) = B(c)
            + lambda_work * W(c)
            + lambda_surface * S(c)
            + lambda_access * E_Q[inflated bytes]
            + lambda_variance * Var(|archive|)
```

- `B(c)` — stored archive bytes;
- `W(c)` — deterministic route-work prior;
- `S(c)` — active shell/dependency surface;
- `E_Q[inflated bytes]` — expected random-access work;
- `Var(|archive|)` — run-to-run archive-size instability.

Profiles use different fixed weights. Benchmark rankings remain separate for ratio, speed, ratio/time, balanced score and Pareto position.

## Full benchmark inventory

The unified runner loads:

1. 35 historical Matrix/EGD profiles;
2. all extra Graph-AI/GRAAL systems from V5.2;
3. UMC-256 Fast/Balanced/Max;
4. RAW reference;
5. all preserved Tier-1 v1 engines;
6. Gabriel MAX;
7. all Tier-1 v2 OMNIA and Gabriel profiles.

Expected unique system count: at least **76**.

The runner keeps the original deterministic eleven-dataset, 32 KiB, one-warm-up plus three-repeat methodology. A verified per-dataset oracle envelope is reported only as a research lower bound and is not inserted into the production ranking.

## Repository boundary

- Active compression code, tests, documentation, benchmark workflows and results: `Shtenco/ai_compress`.
- Immutable historical compression snapshot: `Shtenco/agi_olga@c681ec94fe5194156b71fc304035f7aaff4d2327`, referenced only for reproducibility.
- Active next-generation graph AI and AGI benchmark project: `Shtenco/agi_olga` main tree, kept separate from active compression development.
