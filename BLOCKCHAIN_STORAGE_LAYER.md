# SHTENCO AI Compress -> SYNERGY Storage Layer

## Purpose

Turn the existing lossless codecs into a verifiable storage-compute market for the SYNERGY blockchain without encoding any marketing compression factor into consensus.

## Core rule

For every object the protocol records measured evidence:

`raw_sha256, archive_sha256, raw_bytes, archive_bytes, codec_id, codec_version, chunk_root`

The chain can therefore compute actual storage savings object-by-object. A claim such as 10x, 100x or 1000x is valid only for data where the measured archive size demonstrates it.

## Codec side

`compression_lab/blockchain_storage_adapter.py`:

1. compresses the exact bytes;
2. decompresses the archive;
3. requires byte equality and SHA-256 equality;
4. measures actual archive size;
5. builds a chunk commitment for data availability/random access;
6. emits a canonical `SYNERGY-CODEC-EVIDENCE/1` receipt.

Gabriel Horn is immediately supported through the existing `GabrielHornEngine`. Additional EGD/SABF/HACE/TSC/AMCE/UMC/GRAAL engines can be registered only through adapters that satisfy the same exact-roundtrip contract.

## Blockchain side

SYNERGY PQ-EVM stores an `ArchiveReceipt` commitment with:

- content/object id;
- raw and archive hashes;
- codec id/version commitment;
- measured byte counts;
- chunk root;
- replication count;
- erasure coding `k/n`;
- random-access amplification;
- storage class/expiry.

Storage providers bid for replicas and submit periodic proof commitments. Payment is released for availability/proof policy, not merely for claiming the data was stored.

## Economic model

Let:

- `R` = raw bytes;
- `C` = compressed bytes;
- `r = C/R`;
- `p_raw` = ordinary storage cost per byte-epoch;
- `p_net` = SYNERGY provider price per compressed byte-epoch including replication/erasure overhead;
- `o` = total redundancy multiplier.

Then measured cost ratio is:

`cost_synergy / cost_raw = r * o * p_net / p_raw`

and saving factor is the reciprocal when the denominator is non-zero.

This makes the business claim auditable: extreme savings require both extreme measured compressibility and sufficiently low decentralized storage price/overhead.

## Data placement

Large payment receipts, invoices, AI traces, model artifacts, historical state snapshots and company documents should not all live in canonical EVM storage. Canonical state keeps only the commitments needed for ownership, integrity, policy and finality; bulk bytes live in this archival layer.

## Safety / availability

Compression does not replace redundancy. Production policy should combine:

- independent providers;
- erasure coding;
- geographic/failure-domain diversity;
- periodic challenge/proof;
- restore drills;
- codec-version pinning;
- archive/hash verification;
- migration before codec deprecation.

The protocol must always retain the ability to reconstruct the exact original bytes.
