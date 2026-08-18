# SINERGY Archive Manifest V1 — 2026-08-18

## Purpose

This additive protocol generalizes the existing immutable `source_snapshot` practice without changing any compressor, benchmark or historical snapshot.

The archive identity is the original source repository/ref/commit plus the ordered set of original file path/size/SHA-256 records. Compression is an optional storage representation and cannot change the identity of the source tree.

## Core rules

- every source file is identified by SHA-256;
- source Git commit is recorded explicitly;
- paths are normalized relative paths and must be unique;
- manifest and source-tree digests are deterministic;
- archive is always `immutable = true`;
- authority is always `ARCHIVE_ONLY`;
- compression codec and compressed-artifact SHA are optional but must be supplied together;
- verifying a snapshot checks original source identity independently of the chosen codec.

## What an archive does not prove

A preserved file or benchmark artifact does not become:

- current production code;
- Financial OS accounting truth;
- a valid live credential;
- a model-quality claim;
- an approved economic mechanism;
- an execution authorization.

The manifest preserves evidence and provenance; domain authorities interpret that evidence separately.

## Why this matters for SINERGY

The federation intentionally preserves Cashero, early AMM/QE/QT/MEV research, old Financial OS generations, NEXUS generations, public sites, compression generations and future superseded implementations. `archive.manifest/v1` gives these snapshots one reproducible content-addressed representation without moving them into a monorepo or deleting their original history.

## Non-destructive evolution

This protocol is stacked above `docs/sinergy-memory-archive-boundary-20260817`. The earlier documentation and every existing codec/snapshot remain unchanged. Future archive versions should be added side-by-side.
