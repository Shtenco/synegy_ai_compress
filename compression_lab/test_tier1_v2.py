import os

from compression_lab.shtenco_tier1_v2 import (
    GabrielHornRandomAccessTier1,
    MAGIC,
    tier1_v2_engine_suite,
)


def samples():
    return [
        b"",
        b"SHTENCO OMNIA GRAPH VERSION " * 128,
        bytes(range(256)) * 8,
        b"\x00" * 4096 + b"ABCD" * 512,
        bytes((index // 4) & 255 for index in range(4096)),
        os.urandom(2048),
    ]


def test_tier1_v2_roundtrip_all_profiles():
    for name, _, engine in tier1_v2_engine_suite():
        for source in samples():
            archive = engine.compress(source)
            assert engine.decompress(archive) == source, name
            expected_magic = getattr(engine, "magic", MAGIC)
            assert archive.startswith(expected_magic), name


def test_random_access_profile_extracts_exact_range():
    source = (bytes(range(256)) * 64) + b"SHTENCO" * 1000
    engine = GabrielHornRandomAccessTier1(expected_range_bytes=512)
    archive = engine.compress(source)
    assert engine.decompress_range(archive, 317, 4401) == source[317:4401]
    info = engine.inspect(archive)
    assert info.block_size <= 4096
