# OMNIA-REX V3 — mathematical limits and constructive huge-compression theorem

## 1. What cannot be proved

No lossless codec can compress every arbitrary n-bit string.

There are 2^n possible n-bit inputs, while the total number of binary strings
strictly shorter than n bits is only

```text
1 + 2 + 4 + ... + 2^(n-1) = 2^n - 1.
```

Therefore an injective lossless mapping cannot assign a shorter representation
to all n-bit strings.

More generally, asking every input to save at least s bits leaves fewer than
2^(n-s+1) possible short codewords. Thus universal 100x/1000x lossless
compression of arbitrary data is impossible.

OMNIA-REX makes no such claim.

## 2. Conditional candidate-set theorem

Let encoder and decoder share model M. Suppose M and the already decoded
context reduce the possible source objects to a finite candidate set C of size
|C| = K.

Then an enumerative exact code can identify the source with

```text
ceil(log2 K)
```

bits, plus model/format metadata.

Conversely, any fixed-length injective identifier for all K candidates needs at
least ceil(log2 K) bits.

Therefore the correct target is not to "beat information theory", but to make

```text
K << 2^N
```

using structure that is already available to the decoder.

This is the compression form of REVERSE-EXP candidate collapse.

## 3. Predict-and-correct theorem

Consider n symbols from an alphabet of size q. Encoder and decoder use the same
causal predictor. The predictor is correct everywhere except m positions.

Once the error positions and their correction symbols are known, the full
source is reconstructed exactly because decoder and encoder replay the same
causal history.

The number of possible error patterns with exactly m errors is at most

```text
C(n,m) * (q-1)^m.
```

Hence a constructive enumerative residual exists with length

```text
L(n,m,q)
 <= log2 C(n,m) + m log2(q-1) + O(log n)
```

bits.

Using

```text
C(n,m) <= (e n / m)^m
```

gives

```text
L <= m log2(e n/m) + m log2(q-1) + O(log n).
```

For bytes q=256.

If p=m/n is a fixed error fraction, the asymptotic rate is bounded by

```text
H2(p) + p log2(255)
```

bits per source byte, where H2 is binary entropy.

Therefore an asymptotic compression-ratio lower bound for this structured class is

```text
CR >= 8 / (H2(p) + p log2(255)).
```

This is a worst-case bound for arbitrary error positions and arbitrary nonzero
byte corrections. Real residuals can be much smaller because their positions
and values are themselves structured.

## 4. Unbounded-ratio corollary for increasingly predictable classes

If

```text
m(n) = o(n / log n)
```

and model/parameter description is O(log n), then

```text
L(n) = o(n)
```

and therefore

```text
8n / L(n) -> infinity.
```

So arbitrarily large exact compression ratios are mathematically possible on a
sequence of increasingly predictable structured objects.

This is not universal compression. It is a theorem about a restricted source
class whose number of exceptions grows sufficiently slowly.

Examples include long deterministic arrays with finitely many edits, versioned
objects mostly copied from a shared model, and generated fields with sparse
corrections.

## 5. Model-selection theorem

Suppose a portfolio contains K exact models/codecs with complete description
lengths L_1(x), ..., L_K(x).

An exhaustive OMNIA selector that stores the chosen route can achieve

```text
L_MAX(x) <= min_j L_j(x) + ceil(log2 K) + O(format metadata).
```

When the route identifier and integrity header are already included in each
candidate container, the implementation can simply choose the smallest complete
archive. Therefore MAX is provably the byte-minimum member of the finite tested
portfolio.

This does not prove global optimality over all possible compressors.

## 6. Shared-model amortization theorem

Let:

- B_M = serialized shared-model bytes;
- B_C = per-object QTD3 container bytes;
- R = number of objects sharing the model.

The effective per-object storage cost is

```text
B_eff(R) = B_C + B_M / R.
```

Against a standalone baseline of B_D bytes, shared-model compression wins iff

```text
R > B_M / (B_D - B_C)
```

when B_C < B_D.

As R grows,

```text
B_eff(R) -> B_C.
```

Therefore very large transport compression can be economically real when a
model is reused many times, but it is dishonest to quote B_C alone for the
first object.

## 7. Connection to the measured spatial result

For the structured 128x128 grayscale experiment:

```text
n = 16384 bytes
Paeth prediction errors = 599
p = 0.03656
complete REX3 archive = 81 bytes
raw/archive ratio = 202.27x
```

The generic arbitrary-error bound is much weaker because it assumes the 599
positions and values are arbitrary. In this raster they are not: the gap stream
and correction values are highly compressible after the predictor.

A more local 8192-byte block had only 25 errors under its best causal predictor:

```text
p = 25/8192 = 0.003052.
```

The generic enumerative bound is about 55.1 bytes before metadata; the measured
complete spatial-sparse candidate was 36 bytes because the errors themselves
have additional structure.

The measured result therefore does not contradict the theorem. It shows that a
second structural layer exists inside the residual.

## 8. Hierarchical-search theorem

Let F be the number of candidate families and S(x) the subset selected by a
router.

Exhaustive MAX evaluates F families. V3 FAST evaluates approximately |S(x)|
families and then still verifies the chosen archive exactly.

The byte regret is

```text
regret(x) = L_router(x) / L_MAX(x) - 1.
```

The router cannot be proved universally zero-regret unless it evaluates every
possible winner. Its quality is therefore an empirical out-of-sample property,
not an information-theoretic theorem.

What is provable is exactness: routing can change archive size and search work,
but it cannot change the decoded bytes because every admitted candidate is
reversible and SHA-verified.

## 9. Scientific claim boundary

Mathematically proved:

- universal shortening of arbitrary data is impossible;
- candidate-set size determines the exact identifying information needed;
- sparse predictive exceptions admit sublinear codes when m=o(n/log n);
- under those source conditions compression ratio can grow without bound;
- MAX is the smallest complete archive inside its finite evaluated portfolio;
- shared-model amortization obeys B_C + B_M/R.

Empirically measured, not universally proved:

- which real corpora satisfy those structural assumptions;
- whether OMNIA-REX beats every external compressor;
- router regret on future unrelated data;
- wall-clock speedup on other machines.

This separation is mandatory for every future OMNIA-REX claim.
