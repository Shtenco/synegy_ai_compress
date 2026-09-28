import hashlib
import lzma
import random
import struct

from shtenco_math_portfolio_v3 import (
    HEADER,
    ROUTE_BYTEPOLY,
    ROUTE_P2HF,
    ROUTE_WHOLEINT,
    ShtencoMathExpertV3,
)


def roundtrip(data: bytes, profile: str = "max"):
    engine = ShtencoMathExpertV3(profile)
    archive = engine.compress(data)
    restored = engine.decompress(archive)
    assert restored == data
    assert hashlib.sha256(restored).digest() == hashlib.sha256(data).digest()
    return engine, archive


def test_roundtrip_many_sizes():
    rng = random.Random(123)
    for size in [0, 1, 2, 7, 31, 255, 1024, 4097, 16384]:
        data = bytes(rng.randrange(256) for _ in range(size))
        roundtrip(data, "balanced")


def test_bytepoly_structured():
    data = bytes((i**3 + 5 * i * i + 17 * i + 29) & 255 for i in range(32768))
    engine, archive = roundtrip(data)
    route = HEADER.unpack_from(archive)[2]
    assert route in {ROUTE_BYTEPOLY, 3, 4, 1}
    assert len(archive) < len(lzma.compress(data, preset=9))


def test_wholeint_sparse_formula():
    size = 8192
    exponents = []
    current = size * 8 - 2
    gap = 3
    while current > 10:
        exponents.append(current)
        current -= gap
        gap += 2
    value = sum(1 << exponent for exponent in exponents)
    data = value.to_bytes(size, "big")
    engine, archive = roundtrip(data)
    route = HEADER.unpack_from(archive)[2]
    assert route in {ROUTE_WHOLEINT, ROUTE_P2HF}
    assert len(archive) < 512


def test_p2hf_near_power_minus_quadratic_sparse():
    size = 8192
    top = size * 8 - 1
    subtract = 0
    index = 0
    while True:
        exponent = 3 * index * index + 7 * index + 11
        if exponent >= top - 2:
            break
        subtract |= 1 << exponent
        index += 1
    value = (1 << top) - subtract
    data = value.to_bytes(size, "big")
    engine, archive = roundtrip(data)
    assert HEADER.unpack_from(archive)[2] == ROUTE_P2HF
    assert len(archive) < len(lzma.compress(data, preset=9))


def test_counter_uses_structural_route():
    data = b"".join(struct.pack(">I", index) for index in range(8192))
    engine, archive = roundtrip(data)
    assert engine.last_mode != "raw"
    assert len(archive) < len(data) // 4


def test_corruption_detected():
    engine, archive = roundtrip(b"correct data" * 100)
    broken = bytearray(archive)
    broken[-1] ^= 1
    try:
        engine.decompress(bytes(broken))
    except Exception:
        pass
    else:
        raise AssertionError("corruption was not detected")


def test_omnia_wrapper_when_repository_modules_are_available():
    from shtenco_math_portfolio_v3 import ShtencoOmniaMathV3

    engine = ShtencoOmniaMathV3("balanced")
    data = b'{"route":"omnia-math","value":42}\n' * 400
    archive = engine.compress(data)
    assert engine.decompress(archive) == data
