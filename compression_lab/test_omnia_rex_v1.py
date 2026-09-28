import os, random
from omnia_rex_v1 import OmniaREXV1

def cases():
    rng=random.Random(7)
    yield b""
    yield b"A"*10000
    yield b"alpha beta gamma\n"*1000
    yield bytes(range(256))*20
    yield bytes(rng.randrange(256) for _ in range(8192))

def test_roundtrip_builtin():
    e=OmniaREXV1(include_legacy=False)
    for data in cases():
        arc=e.compress(data)
        assert e.decompress(arc)==data

def test_corruption_rejected():
    e=OmniaREXV1(include_legacy=False)
    arc=bytearray(e.compress(b"abc"*3000))
    arc[20]^=1
    try:
        e.decompress(bytes(arc))
    except Exception:
        return
    raise AssertionError("corruption accepted")

def test_candidate_verification_and_raw_fallback():
    e=OmniaREXV1(include_legacy=False)
    data=os.urandom(4096)
    arc=e.compress(data)
    assert e.decompress(arc)==data
    assert e.inspect_candidates(data)
