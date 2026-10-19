# Инженерная дорожная карта — от архиватора к проверяемому продукту

## R0 — Truth first
Закрепить pinned historical result, SHA-256, все отрицательные verdict, copy-of-evidence файлы. Протоколы метрик и трактовки должны быть доступны без GitHub Actions artifact.

## R1 — Действительно независимый corpus
Сформировать corpora: промышленные CSV/Parquet, видео и JPEG (проверка отсутствия выигрыша), код, JSON, инженерные версии, model checkpoints, уже сжатые потоковые данные. Все лицензии и provenance фиксировать. Длина файлов от 1 КБ до многогигабайтных потоков.

## R2 — Безопасный формат и верификация
Archive format versioning, streaming decoder, error handling, caps RAM/time, fuzz, отказ от несогласованных внешних библиотек, manifest content-addressed, cross-platform binary roundtrip.

## R3 — Быстрые нативные реализации
Вынести bottlenecks MAX/блочный обход из Python; профили CPU AVX/ARM, SIMD, streaming. Любое ускорение только после повторной проверки полного декодирования.

## R4 — Рабочий ModelStore
Content-defined boundaries for GGUF/ONNX/NPZ, tensor manifest, intra/inter-checkpoint refs, lazy restoration, exact model hash. Отдельная quantization branch не должна смешиваться с lossless-контейнером.

## R5 — Neural weight compression
Activation-aware training/packing, calibration OOS, full-model deployment, PPL, accuracy, VRAM, tokens/s. Применять контрольную модель известного качества, сравнивать с внешними quantization baselines при одинаковом bpw.

## R6 — Пилоты ЕАЭС и международный продукт
Workload owner consent, private corpus NDA, enterprise SLA, TCO before/after, legal review, security audit, backup/restore drill. Интеграция с SYNERGY NET, NEXUS, EURASIAN — только после корректного интерфейсного handoff.

## Как измерять успех

**Lossless**: median aggregate savings across holdouts, speed/RSS, exact integrity, p95 range, decoder safety, deterministic artifact. **ModelStore**: valid artifact and time-to-load. **LLM**: PPL delta, downstream score delta, VRAM and tokens/s. **Economics**: total cost-of-ownership delta; no guaranteed percent.

[Назад](../README.md).