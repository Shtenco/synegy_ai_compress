# Реестр утверждений и научной проверки

| Утверждение | Основание | Статус | Что отсутствует |
|---|---|---|---|
| D(C(X))=X для принятых строк Tier-1 | Exact benchmark | Подтверждено в историческом отчёте | Новая независимая CI проверки на свежем main |
| 76 unique систем | Tier-1 inventory/result | Подтверждено по историческому реестру | Нельзя говорить, что все 76 повторно замерены одновременно |
| 154/154 PASS | Unified Tier-1 result 2026-07-30 | Подтверждено как сохранённый результат | Cross-machine replication |
| 30.336× для OMNIA MAX | Geometric mean на 11×32768 | Подтверждено для фиксированного набора | Другие домены/длинные потоки |
| Gabriel более силён на гладких int32 | Corpus exact report | Подтверждено для одного генератора | Реальные внешние поля telemetry |
| Gabriel быстрее Brotli на encoding | Corpus exact report | Ложно на данном корпусе | Новый быстрый native backend |
| Whole-row DWE 2445× с рабочей нейросетью | Real-weight quality | **Опровергнуто** | Принципиально новая репрезентация |
| PQ/RVQ 0.38–1.50 bpw сохраняет LLM | Sample quality | Не подтверждено | Full-model PPL/accuracy/VRAM/tokens/s |
| +30–50% Huffman выигрыша | Entropy indices | Не подтвердилось | Новые более предсказуемые коды |
| Экономия в дата-центрах/ЕАЭС | Рассуждение по рынку | Гипотеза | Пилоты, TCO, SLA, контракты |

## Строгая программа тестов

**Gate A — Safety:** fuzz decoder, malformed input, zip-bomb caps, allocation limits, protocol version, archive poisoning, decompression timeout.

**Gate B — Correctness:** byte equality, SHA-256, incremental and random-range restore, cross-platform endianness, reproducibility, content-addressing.

**Gate C — Performance:** actual size including metadata; encode/decode MB/s, RSS, cores/watts, cross-machine confidence, p50/p95 selective access.

**Gate D — Comparators:** pinned ZIP(zlib), Zstd, Brotli, LZMA/7-Zip; same input bytes, same core budget or explicit resource normalized report; compare both single-file and cross-version modes.

**Gate E — LLM quality:** PPL, task accuracy, real activation drift, tokens/s, VRAM, full-model byte representation and load path.

**Gate F — Independent users:** no claims of production readiness until permissions, compliance, DR runbook, upgrade compatibility, signed artifacts, recovery drills, legal review.

## Пять строго запрещённых подмен

1. Размер структурных индексов выдавать за рабочую модель.
2. Geomean частных ratios выдавать за общий savings дата-центра.
3. Успешный SHA исходного файла выдавать за защищённый от уязвимостей decoder.
4. Отдельный исторический GitHub Actions замер выдавать за свежий passing status.
5. RAW fallback на несжимаемых байтах выдавать за победу компрессора.

[Назад](../README.md).