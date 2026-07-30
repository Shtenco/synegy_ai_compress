import os
from compression_lab.shtenco_tier1_engines import tier1_engine_suite


def test_tier1_roundtrip_all_engines():
    samples = [
        b"",
        b"SHTENCO-GRAPH-AI-TIER1 " * 1000,
        bytes(range(256)) * 64,
        b"\x00" * 8192 + b"ABCD" * 2048,
        os.urandom(8192),
    ]
    for name, _, engine in tier1_engine_suite():
        for source in samples:
            archive = engine.compress(source)
            assert engine.decompress(archive) == source, name
            expected_magic = getattr(engine, "magic", b"ST1\x01")
            assert archive.startswith(expected_magic), name
