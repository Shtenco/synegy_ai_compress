# SHTENCO Math Portfolio v3

`SHTENCO Math Portfolio v3` is an exact expert layer for `ai_compress`. It does
not replace OMNIA, Gabriel Horn, GRAAL, TSC-X or the mature entropy backends.
It adds the mathematical models developed in the P2HF experiments and admits
them only when the final verified container is smaller.

## Architecture

```text
FILE
 ├─ existing OMNIA Tier-1 v2.1
 └─ Math Portfolio v3
     ├─ byte LZMA9
     ├─ finite differences / BytePoly orders 1..4
     ├─ XOR-lag transforms
     ├─ byte-plane transpose
     ├─ WholeINT binary exponent grammar
     ├─ P2HF signed NAF exponent grammar
     └─ optional reversible secp256k1 EC-MATH

verified candidates → minimum stored bytes → SHA-256 container
```

The production wrapper `ShtencoOmniaMathV3` compares the existing OMNIA archive
with the mathematical expert archive. The wrapper stores only a six-byte selector
prefix above the already verified inner archive. Ordinary source code, text and
high-entropy files therefore keep the mature OMNIA route whenever it is shorter,
with a fixed six-byte format cost.

## Mathematical routes

### WholeINT

The whole file is interpreted as a non-negative integer:

```text
N = sum(2**e_i)
```

The descending exponent sequence is encoded with a small grammar containing:

- literal gaps;
- constant-gap runs;
- arithmetic-gap runs.

This route is feature-gated to sparse bit patterns and bounded file sizes.
Leading zero bytes are preserved by the archive header.

### P2HF signed formula

The integer is converted to canonical non-adjacent form:

```text
N = sum(s_i * 2**e_i),  s_i in {-1, +1}
```

This can be dramatically shorter for values close to a large power of two minus
a structured sparse residual. Exponents use the same grammar; signs use a bit
stream. P2HF is not forced onto arbitrary data.

### BytePoly

Modular finite differences preserve byte structure:

```text
x -> Delta(x) -> Delta^2(x) -> ... -> Delta^4(x)  (mod 256)
```

The selected residual is compressed and exactly integrated during decoding.
This route targets polynomial and smoothly evolving numeric byte sequences.

### EC-MATH

The optional research route uses a reversible Koblitz-style mapping on
`secp256k1`:

```text
x = 256*m + nonce
y^2 = x^3 + 7 mod p
```

where `m` is a 30-byte file block and the smallest nonce producing a curve point
is selected. Decoding is `m = floor(x / 256)`. Unlike SHA-256 mapping, this is
lossless. The route is disabled by default because ablation experiments showed
that curve membership itself did not create compression; it remains available
for mathematical verification and future research.

## Profiles

- `balanced`: feature-gated bounded search and a small work penalty;
- `max`: broader exact search, optimized for stored bytes;
- OMNIA wrapper profiles: `speed`, `balanced`, `max`.

## Usage

```python
from compression_lab.shtenco_math_portfolio_v3 import (
    ShtencoMathExpertV3,
    ShtencoOmniaMathV3,
)

expert = ShtencoMathExpertV3(profile="max")
archive = expert.compress(source)
assert expert.decompress(archive) == source
print(expert.last_mode)

production = ShtencoOmniaMathV3(profile="max")
archive = production.compress(source)
assert production.decompress(archive) == source
print(production.last_mode)
```

## Reproducible benchmark

```bash
python compression_lab/benchmark_math_portfolio_v3.py \
  --size 32768 \
  --output compression_lab/output_math_portfolio_v3
```

The deterministic corpus includes source-like text, JSON, repeated text, zeros,
pseudorandom bytes, `uint32` counters, cubic bytes, fixed records, a WholeINT
formula target, a signed P2HF target and mixed text/numeric content.

Every row is accepted only after byte equality and SHA-256. The benchmark is a
controlled applicability/falsification suite, not a universal superiority claim.

## Local reference result

On the deterministic 11 x 32,768-byte suite used while implementing this branch:

| Engine | Total archive bytes | Geometric-mean ratio | Exact rows |
|---|---:|---:|---:|
| LZMA9 Extreme | 41,680 | 44.75x | 11/11 |
| Math Portfolio v3 Balanced | 35,705 | 90.99x | 11/11 |
| Math Portfolio v3 Max | 35,617 | 94.29x | 11/11 |

These totals are dominated by deliberately structured mathematical datasets.
Production evaluation must also compare the OMNIA wrapper on the frozen and real
corpora already maintained by the repository.
