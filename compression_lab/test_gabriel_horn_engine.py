import os

import pytest

from compression_lab.gabriel_horn_engine import (
    GabrielHornEngine,
    MAGIC,
    _apply_transform,
    _invert_transform,
    _transform_specs,
)


def test_all_reversible_transforms():
    for size in list(range(0, 40)) + [63, 64, 65, 127, 128, 129, 257]:
        source = bytes((i * i + 17 * i + size) & 255 for i in range(size))
        for transform, parameter, _ in _transform_specs(size, "max"):
            transformed = _apply_transform(source, transform, parameter)
            assert _invert_transform(transformed, transform, parameter) == source


def test_roundtrip_progressive_and_random_access():
    engine = GabrielHornEngine(profile="balanced")
    samples = [
        b"",
        b"A" * 10000,
        b"ABCD" * 4096,
        bytes(range(256)) * 64,
        bytes((i * i + 3 * i) & 255 for i in range(16384)),
        os.urandom(4096),
    ]
    for source in samples:
        archive = engine.compress(source)
        assert archive.startswith(MAGIC)
        assert engine.decompress(archive) == source
        assert engine.decompress_progressive(archive, 8) == source
        left = len(source) // 3
        right = min(len(source), left + 777)
        assert engine.decompress_range(archive, left, right) == source[left:right]


def test_shell_codec_beats_raw_on_structured_sequence():
    engine = GabrielHornEngine(profile="max")
    source = bytes(range(256)) * 64
    archive = engine.compress(source)
    info = engine.inspect(archive)
    assert engine.decompress(archive) == source
    assert info.shell_blocks >= 1
    assert len(archive) < len(source) // 8


def test_exact_block_reference_and_range_decode():
    engine = GabrielHornEngine(profile="balanced")
    block = os.urandom(2048)
    source = block + block + block
    archive, _ = engine._build_archive(source, 2048)
    info = engine.inspect(archive)
    assert info.reference_blocks == 2
    assert engine.decompress(archive) == source
    assert engine.decompress_range(archive, 2048 + 100, 4096 + 100) == source[2148:4196]


def test_corruption_is_detected():
    engine = GabrielHornEngine(profile="balanced")
    archive = bytearray(engine.compress(b"SHTENCO-GABRIEL" * 1000))
    archive[-1] ^= 1
    with pytest.raises((ValueError, Exception)):
        engine.decompress(bytes(archive))


def test_tail_bound_is_monotone_and_exact_at_eight_bits():
    bounds = [GabrielHornEngine.shell_tail_bound(bits) for bits in range(9)]
    assert bounds == sorted(bounds, reverse=True)
    assert bounds[0] == 1.0
    assert bounds[-1] == 0.0
