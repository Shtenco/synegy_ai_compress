# SHTENCO AI Compress

Единый репозиторий технологий архивации и lossless-сжатия SHTENCO.

## Состав

- EGD-256, SABF-X, HACE-X, TSC-X, AMCE-100X;
- UMC-256 и MDL-маршрутизация;
- Graph-AI Compression V5.2 и GRAAL-IGC;
- BIP39, Arithmetic, rANS, Huffman, Graph Delta;
- Tier-1 движки и Matrix web-приложение;
- воспроизводимые benchmark, round-trip и SHA-256 тесты.

Активные файлы хранятся в `compression_lab/`, CI — в `.github/workflows/`.

`source_snapshot` — неизменяемый Git-snapshot commit `c681ec94fe5194156b71fc304035f7aaff4d2327` из прежнего репозитория. В нём сохранены все исторические compression-файлы, тесты и поколения V3/V4/V5.2/Tier-1. После клонирования с доступом к приватному `Shtenco/agi_olga` выполните:

```bash
git submodule update --init source_snapshot
```

Проект графового ИИ нового поколения, включая версию из статьи, проходившую AGI-бенчмарки, хранится отдельно в `Shtenco/agi_olga`.
