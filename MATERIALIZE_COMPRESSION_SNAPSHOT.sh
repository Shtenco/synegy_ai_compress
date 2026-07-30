#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

git submodule update --init source_snapshot
mkdir -p compression_lab legacy_workflows
cp -a source_snapshot/compression_lab/. compression_lab/
for file in \
  benchmark-all-compression-systems-exact.yml \
  shtenco-graph-ai-v5.yml \
  shtenco_archiver_v4.yml \
  tier1_compression_benchmark.yml; do
  cp "source_snapshot/.github/workflows/$file" "legacy_workflows/$file"
done

echo "Materialized all historical compression sources from c681ec94fe5194156b71fc304035f7aaff4d2327"
