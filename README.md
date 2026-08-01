# SHTENCO AI Compress

Единый репозиторий технологий архивации и lossless-сжатия SHTENCO.

## Состав

- EGD-256, SABF-X, HACE-X, TSC-X, AMCE-100X;
- UMC-256 и MDL-маршрутизация;
- Graph-AI Compression V5.2 и GRAAL-IGC;
- **Gabriel Horn Codec (`SGH1`)**: многомасштабный lifting, significance-shells, дедупликация, random access и surface-aware MDL;
- **Math Portfolio v3 (`SMX3`)**: BytePoly, XOR/transpose, WholeINT, signed P2HF и опциональный обратимый EC-MATH;
- BIP39, Arithmetic, rANS, Huffman, Graph Delta;
- Tier-1 движки и Matrix web-приложение;
- воспроизводимые benchmark, round-trip и SHA-256 тесты.

Активные файлы хранятся в `compression_lab/`, CI — в `.github/workflows/`.

## Gabriel Horn

```python
from compression_lab.gabriel_horn_engine import GabrielHornEngine

engine = GabrielHornEngine(profile="max")
archive = engine.compress(source)
assert engine.decompress(archive) == source
fragment = engine.decompress_range(archive, 1000, 5000)
```

Математика, формат контейнера и ограничения описаны в `compression_lab/README_GABRIEL_HORN.md`.

## Math Portfolio v3

```python
from compression_lab.shtenco_math_portfolio_v3 import ShtencoOmniaMathV3

engine = ShtencoOmniaMathV3(profile="max")
archive = engine.compress(source)
assert engine.decompress(archive) == source
print(engine.last_mode)
```

Новый слой сравнивает существующую OMNIA v2.1 с проверенным математическим
экспертом. Специализированные модели допускаются только после полного обратного
декодирования и SHA-256; RAW и зрелые энтропийные маршруты остаются обязательным
fallback. Архитектура и контролируемый benchmark описаны в
`compression_lab/README_MATH_PORTFOLIO_V3.md`.

## Точный корпусный benchmark

```bash
python compression_lab/benchmark_gabriel_corpus.py \
  --size 16384 \
  --repeats 3 \
  --warmups 1 \
  --engines raw,gabriel-max,zstd-19,brotli-11,graal-igc \
  --output compression_lab/output_gabriel_corpus
```

Benchmark измеряет фактический размер архива, encode/decode throughput, peak RSS,
стоимость случайного доступа и access amplification. Каждое измерение выполняется
в новом процессе и принимается только после byte equality и SHA-256.

Исторический `UMC-256` добавляется только при наличии его точного snapshot-модуля;
другие UMC-движки не подставляются под это имя. Полная методология описана в
`compression_lab/GABRIEL_CORPUS_METHODOLOGY.md`.

`source_snapshot` — неизменяемый Git-snapshot commit `c681ec94fe5194156b71fc304035f7aaff4d2327` из прежнего репозитория. В нём сохранены все исторические compression-файлы, тесты и поколения V3/V4/V5.2/Tier-1. После клонирования с доступом к приватному `Shtenco/agi_olga` выполните:

```bash
git submodule update --init source_snapshot
```

Проект графового ИИ нового поколения, включая версию из статьи, проходившую AGI-бенчмарки, хранится отдельно в `Shtenco/agi_olga`.
