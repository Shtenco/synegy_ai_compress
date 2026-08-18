from __future__ import annotations

from .blockchain_storage_adapter import gabriel_receipt
from .gabriel_horn_engine import GabrielHornEngine


def test_gabriel_receipt_roundtrip_and_measured_sizes() -> None:
    source = (b"SYNERGY-ARCHIVE-" * 4096) + bytes(range(256)) * 8
    archive, receipt = gabriel_receipt(source, profile="balanced", chunk_size=4096)
    assert receipt.exact_roundtrip is True
    assert receipt.raw_bytes == len(source)
    assert receipt.archive_bytes == len(archive)
    assert receipt.compression_factor == len(source) / len(archive)
    assert GabrielHornEngine(profile="balanced").decompress(archive) == source


def test_incompressible_or_tiny_data_is_not_falsely_claimed() -> None:
    source = b"abc"
    archive, receipt = gabriel_receipt(source, profile="speed", chunk_size=4096)
    assert receipt.archive_bytes == len(archive)
    # The adapter records expansion honestly; it never clamps the ratio to a
    # marketing-friendly value.
    assert receipt.archive_to_raw_ratio == len(archive) / len(source)
