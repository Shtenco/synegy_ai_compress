<p align="center"><img src="assets/readme/hero-v2.svg" width="100%" alt="SHTENCO AI COMPRESS" /></p>

# SHTENCO SYNERGY AI COMPRESS

**Международная компрессионная платформа · Universal Archiving · Version-Aware Storage · Enterprise Data Optimization**

<p align="center"><img src="assets/readme/family-v2.svg" width="100%" alt="SHTENCO compression portfolio"/></p>

> [!IMPORTANT]
> **Единственный источник сравнительных цифр на этой странице:** присланные владельцем `SHTENCO_TIER1_COMPRESSION_FULL(1).zip` и `SHTENCO_UNIFIED_TIER1_V2_FINAL(1).zip`. В первом — 69 профилей и журналы/таблицы, во втором — объединённый реестр 76 профилей и оригинальные Python-файлы. Здесь **не выдаются** прошлые посторонние тесты на Linux/PyTorch или 38 мировых режимов за результаты этих двух архивов. Это архивные доказательства от 30 июля 2026 г. плюс текущие результаты составления Unified V2, а не новый полный прогон 76 кодеков.

<p align="center"><img src="assets/readme/evidence-status-20261020.svg" width="100%" alt="evidence registry"/></p>

## Executive summary

| 76 профилей | 14 current-кодеков | 62 frozen-записи | 11 наборов данных |
|:---:|:---:|:---:|:---:|
| Сводный реестр, включая мировые кодеки и RAW | Исполнение из архива Unified Tier-1 V2 | Исторический снимок от 30.07.2026 | Детерминированный корпус по 32768 байт |

**Сжатие измерено вместе со временем:** исходный архив содержит `all_systems_rows.csv`, `all_systems_summary.csv`, `environment.json`; второй — `current_systems_rows.csv`, `combined_systems_summary.csv`, `SOURCE_COMMITS.txt`. Метрики приводятся с происхождением, а frozen и current не становятся сопоставимым свежим speed-test от их объединения.

## Основные технологии

| Семейство | Роль | Применимость |
|---|---|---|
| **SABF-X Speed / Balanced** | Быстрое Zstd-кодирование и выбор преобразований | Логи, быстрые бэкапы, горячее хранение |
| **PBM-39X** | Потоковая архивация с опциональным BIP39-маршрутом | Структурные текстовые словари, стандартные данные |
| **OMNIA Speed / Balanced / MAX** | Маршрутизация нескольких кодеков по размеру и вычислительным затратам | Offline / cold storage; MAX требует контроля CPU |
| **Gabriel-Horn** | Обратимые lifting, XOR, shells, индекс блоков | Структурные данные, выборочное восстановление |
| **GRAAL / TSC-X / NEXUS-UMC** | Version-aware transforms, byte planes и смесь экспертов | Версионные объекты, структурные бинарные данные |

<p align="center"><img src="assets/readme/architecture-v2.svg" width="100%" alt="Compression engine architecture"/></p>

## SHTENCO vs WORLD — полный проверяемый реестр 76 профилей

**Строки ниже — фактическая сводка из присланного архива Unified Tier-1 V2**, отсортированная по геометрическому среднему коэффициенту. `current` относится к 14 текущим профилям архива, `frozen-20260730` — к 62 архивным записям. Каждый показатель времени — суммарное время обработки 11 файлов, миллисекунды, **из исходного CSV**. Тестовый корпус структурирован и сгенерирован детерминированно, он **не является** выборкой реальных корпоративных данных.

| № | Профиль | Источник | Сжатие × | Encode ms | Decode ms |
|---:|---|---|---:|---:|---:|
| 1 | SHTENCO OMNIA TIER1 V2 MAX | current | 30.336 | 52497 | 35 |
| 2 | SHTENCO OMNIA TIER1 V2 BALANCED | current | 27.235 | 9838 | 36 |
| 3 | SHTENCO GABRIEL-HORN TIER1 MAX | current | 24.760 | 78084 | 40 |
| 4 | SHTENCO GABRIEL-HORN TIER1 BALANCED | current | 24.459 | 30241 | 39 |
| 5 | SHTENCO GRAAL-IGC TIER1 MAX | current | 22.634 | 57 | 6 |
| 6 | SHTENCO TSC-X TIER1 SPATIAL | current | 22.115 | 32 | 5 |
| 7 | SHTENCO SABF-X ULTIMATE GRAPH-AI | frozen | 21.921 | 11143 | 6 |
| 8 | SHTENCO TSC-X TURBOSPATIAL GRAPH-AI | frozen | 21.907 | 1166 | 10 |
| 9 | SHTENCO HACE-X CASCADE GRAPH-AI | frozen | 21.022 | 1965 | 9 |
| 10 | SHTENCO NEXUS-UMC TIER1 | current | 19.675 | 22 | 4 |
| 11 | SHTENCO OMNIA TIER1 V2 SPEED | current | 19.403 | 51 | 2 |
| 12 | SHTENCO DDR-X GRAPH | frozen | 19.214 | 658 | 2 |
| 13 | SHTENCO GRAAL-AIS TIER1 | current | 19.207 | 20 | 6 |
| 14 | SHTENCO CDC-RX GRAPH | frozen | 19.027 | 677 | 2 |
| 15 | SHTENCO UMC-256 MAX | frozen | 18.876 | 20494 | 6 |
| 16 | SHTENCO AMCE-100X GRAPH-AI | frozen | 18.787 | 2127 | 2 |
| 17 | SHTENCO SABF-X ULTIMATE | frozen | 18.720 | 5985 | 9 |
| 18 | SABF-X + ZSTD | frozen | 18.642 | 296 | 7 |
| 19 | SHTENCO RSX RECURSIVE SPATIAL GRAPH-AI | frozen | 18.593 | 1149 | 6 |
| 20 | SHTENCO ODC-XP GRAPH | frozen | 18.508 | 684 | 2 |
| 21 | SHTENCO DMB-39X GRAPH | frozen | 18.478 | 683 | 2 |
| 22 | SHTENCO SECB-39X GRAPH | frozen | 18.448 | 686 | 2 |
| 23 | HYBRID AI COMPRESSION ENGINE | frozen | 18.308 | 4617 | 7 |
| 24 | SHTENCO PECB-39X GRAPH | frozen | 18.262 | 709 | 2 |
| 25 | SHTENCO UMC-256 BALANCED | frozen | 18.189 | 6066 | 4 |
| 26 | SHTENCO ODC-XC GRAPH | frozen | 17.887 | 721 | 2 |
| 27 | SHTENCO BPD-39X GRAPH | frozen | 17.860 | 720 | 2 |
| 28 | SHTENCO UECB-39X GRAPH | frozen | 17.833 | 718 | 2 |
| 29 | SHTENCO ECBC-39 GRAPH | frozen | 17.465 | 825 | 3 |
| 30 | SHTENCO EGD-256 MAX GRAPH-AI | frozen | 17.280 | 2087 | 3 |
| 31 | SHTENCO GRAAL-AIS STORAGE GRAPH-AI | frozen | 17.194 | 1358 | 5 |
| 32 | SHTENCO FAS-256 ATOM STORE GRAPH-AI | frozen | 17.161 | 8864 | 673 |
| 33 | SHTENCO GRAAL-IGC V5.2 | frozen | 17.103 | 827 | 3 |
| 34 | SHTENCO SABF-X TIER1 BALANCED | current | 17.094 | 9 | 0.47 |
| 35 | SHTENCO PBM-39X GRAPH | frozen | 16.973 | 976 | 3 |
| 36 | SHTENCO MICA-39 GRAPH | frozen | 16.973 | 978 | 3 |
| 37 | SABF-X + ZSTD + LZMA9 | frozen | 16.963 | 272 | 8 |
| 38 | SABF-X + LZMA9 | frozen | 16.868 | 254 | 9 |
| 39 | SHTENCO BLOCK_FAST X GRAPH-AI | frozen | 16.760 | 1225 | 3 |
| 40 | SHTENCO SABF-X TIER1 SPEED | current | 16.501 | 1.64 | 0.47 |
| 41 | SHTENCO PBM-39X TIER1 | current | 16.501 | 2.52 | 0.47 |
| 42 | SHTENCO HACE-X CASCADE | frozen | 16.416 | 584 | 20 |
| 43 | SHTENCO AMCE-100X | frozen | 16.337 | 707 | 4 |
| 44 | SHTENCO BAPM-X GRAPH | frozen | 16.055 | 1083 | 3 |
| 45 | BROTLI-11 | frozen | 15.477 | 315 | 1.39 |
| 46 | SHTENCO SABF-X NEURAL SELECTOR | frozen | 15.234 | 334 | 7 |
| 47 | SHTENCO TSC-X TURBOSPATIAL | frozen | 14.444 | 201 | 26 |
| 48 | ZSTD-22 | frozen | 14.070 | 156 | 0.87 |
| 49 | LZMA9 | frozen | 13.966 | 101 | 4 |
| 50 | SHTENCO UMC-256 FAST | frozen | 13.773 | 758 | 1 |
| 51 | ZSTD-3 | frozen | 12.854 | 1.47 | 0.77 |
| 52 | SHTENCO GABRIEL-HORN TIER1 SPEED | current | 12.445 | 1325 | 39 |
| 53 | SHTENCO SABF-X FAST | frozen | 11.727 | 234 | 7 |
| 54 | SHTENCO EGD-256 MAX | frozen | 11.473 | 627 | 5 |
| 55 | BZIP2-9 | frozen | 11.072 | 39 | 8 |
| 56 | GZIP-9 | frozen | 10.938 | 16 | 1 |
| 57 | EGD256 + BROTLI | frozen | 10.684 | 387 | 9 |
| 58 | SHTENCO GRAAL-AIS STORAGE | frozen | 10.560 | 175 | 10 |
| 59 | SHTENCO GABRIEL-HORN TIER1 RANDOM-ACCESS | current | 10.210 | 40732 | 38 |
| 60 | GRAPH DELTA ENCODING | frozen | 10.080 | 89 | 31 |
| 61 | SHTENCO RSX RECURSIVE SPATIAL | frozen | 9.943 | 178 | 14 |
| 62 | EGD256 + LZMA | frozen | 9.888 | 119 | 13 |
| 63 | SHTENCO BLOCK_FAST X | frozen | 9.858 | 89 | 4 |
| 64 | SHTENCO EGD-256 BIP39 GRAPH | frozen | 9.807 | 184 | 13 |
| 65 | EGD256 + ZSTD | frozen | 9.525 | 75 | 8 |
| 66 | SHTENCO EGD-256 RECURSIVE GRAPH | frozen | 8.768 | 225 | 33 |
| 67 | rANS + DICTIONARY | frozen | 2.941 | 83 | 67 |
| 68 | SHTENCO FAS-256 ATOM STORE | frozen | 2.936 | 4027 | 4027 |
| 69 | INTEGER RANGE CODING | frozen | 2.612 | 5604 | 5724 |
| 70 | ADAPTIVE ARITHMETIC CODING | frozen | 1.929 | 6270 | 6388 |
| 71 | ARITHMETIC CODING | frozen | 1.866 | 5824 | 5917 |
| 72 | BIP39 + ARITHMETIC | frozen | 1.863 | 5784 | 5857 |
| 73 | rANS CODING | frozen | 1.853 | 101 | 85 |
| 74 | CANONICAL HUFFMAN | frozen | 1.683 | 334 | 449 |
| 75 | ADAPTIVE HUFFMAN | frozen | 1.679 | 332 | 446 |
| 76 | RAW STORE (reference) | frozen | 1.000 | 0.01 | 0.01 |

**Все 76 записей имеют exact 11/11 в сводном файле архива**, но `frozen` — ранее сохранённые измерения. Рейтинг размера не означает превосходство по CPU; изменение среды и протокола исключает точное сравнение скорости разных runs как одного запуска.

## Международное сравнение — профиль за профилем

| Движок | Тип | Geomean × | Полная упаковка 11 файлов |
|---|---|---:|---:|
| SHTENCO OMNIA V2 MAX | SHTENCO current | 30.336 | 52.50 с |
| SHTENCO OMNIA V2 Balanced | SHTENCO current | 27.235 | 9.84 с |
| SHTENCO GRAAL-IGC MAX | SHTENCO current | 22.634 | 57 мс |
| SHTENCO SABF-X Speed | SHTENCO current | 16.501 | 1.64 мс |
| SHTENCO PBM-39X | SHTENCO current | 16.501 | 2.52 мс |
| Brotli-11 | World frozen | 15.477 | 314.85 мс |
| Zstd-22 | World frozen | 14.070 | 156.25 мс |
| LZMA9 | World frozen | 13.966 | 100.82 мс |
| Zstd-3 | World frozen | 12.854 | 1.47 мс |
| bzip2-9 | World frozen | 11.072 | 38.50 мс |
| gzip-9 | World frozen | 10.938 | 16.12 мс |

**Осторожно с интерпретацией:** это сравнительный исторический реестр, а не независимый промышленный тест. Задача свежего прогона на больших настоящих файлах остаётся отдельной.

## Integrated Efficiency — SAEI

**SHTENCO Archival Efficiency Index:**

```text
SAEI(V) = original_bytes / (archive_bytes + V * (encode_seconds + decode_seconds))
V = 10 MiB/s — пример стоимости CPU в эквивалентных байтах
```

Для точного расчёта SAEI по всему корпусу требуется **суммировать исходные байты, архивные байты и времена по индивидуальным строкам**. В этих ZIP есть подробные строки старого и нового прогона, поэтому единый рейтинг SAEI необходимо рассчитывать раздельно по протоколу `frozen/current`; подстановка `geomean_ratio` в формулу недопустима.

| Режим оптимизации | Главная цель | Кому подходит |
|---|---|---|
| Высокий V (CPU дорогой) | Наименьшее время + приемлемое сжатие | Streaming, hot storage, низкая задержка |
| Средний V | Минимум суммарных издержек | Cloud backups, корпоративные ЦОД |
| Низкий V (CPU дешёвый) | Минимальный размер архива | Cold archives, редкие восстановления |

<p align="center"><img src="assets/readme/speed-vs-ratio-v2.svg" width="100%" alt="Compression Pareto trade-offs"/></p>

## Экономия средств для ЦОД и дата-центров

### Экономика хранения и вычислений

Пусть `D` — исходный объём, `R_a` и `R_b` — коэффициенты сжатия кандидата и действующей системы. Разница в занятом объёме:

```text
Saved_GiB = D_GiB * (1/R_b - 1/R_a)
Storage_savings = Saved_GiB * storage_price_per_GiB_month * months
CPU_cost_delta = (CPU_seconds_a - CPU_seconds_b) * cpu_price_per_second
Net_benefit = Storage_savings + reduced_egress_and_replication
              - CPU_cost_delta - deployment - license - migration - recovery_overhead
```

**Модельный сценарий, не коммерческое обещание:** 1 PiB исходных данных = 1 048 576 GiB, текущее сжатие 2.0×, новое 2.5×, условный тариф 0.02 USD/GiB-month:

| Показатель | Значение |
|---|---:|
| Занято до изменения | 524 288 GiB |
| Занято после изменения | 419 430 GiB |
| Освобождено | 104 858 GiB |
| Валовая экономия хранения/месяц | **2 097 USD** |
| Валовая экономия хранения/год | **25 166 USD** |
| Чистая экономия | Нужны счета за CPU, egress, SLA и эксплуатацию |

Экономика зависит от доступного объёма, репликации, tiering, энергопотребления, профиля восстановлений и фактических тарифов. На уже сжатых фотографиях, ZIP и видео выигрыш может быть нулевым или отрицательным. Для лицензирования и ROI важнее воспроизводимые испытания на данных потенциального клиента, чем синтетический коэффициент 30×.

<p align="center"><img src="assets/readme/eaes-market-v2.svg" width="100%" alt="EAEU and global compression markets"/></p>

## ЕАЭС: применимость и выход на рынок

| Сегмент | Задача | Приоритет эксперимента | Модель продаж |
|---|---|---|---|
| Банки и финтех | Долговременные журналы, архивные выгрузки | Integrity, audit, hot/cold split | Лицензия on-prem |
| Телкомы | Network telemetry, CDR, структурные события | Throughput, восстановление | Плата по объёму |
| Государственные архивы | Документы, долгий retention | Форматы, миграция, SHA-256 | Пилот + поддержка |
| ЦОД и облака | Backup, object store, snapshots | SAEI, TCO, скорость | Storage optimization / OEM |
| Промышленные предприятия | Временные ряды и сенсоры | TSC-X, GRAAL, streaming | Подписка + внедрение |

Рынок ЕАЭС: Казахстан, Россия, Беларусь, Армения, Кыргызстан. Для регионального развёртывания проверяются локальные требования к информационной безопасности, совместимость с существующими средствами и права на сторонние библиотеки/алгоритмы.

## Международный рынок

**Target buyers:** data-center operators, cloud backup vendors, MSP, enterprise storage, CDN/edge platforms, AI training pipelines.

**Продуктовая стратегия:** экспорт SDK/API, Linux service, enterprise on-prem image, OEM integration; paid pilot на репрезентативной выборке; SLA и воспроизводимые результаты; отдельные версии для speed-first и size-first.

**Критерии успешного PoC:** снижение `total cost per restored GiB`, ускорение restore, допустимый CPU/RAM, стабильность, compatibility, безопасность, воспроизводимые SHA-256 и полное отсутствие потерь.

## Доказательная база и воспроизведение

- Исходный ZIP Tier-1: 69 профилей, `all_systems_rows.csv`, `all_systems_summary.csv`, `environment.json`; 2026-07-30.
- Unified Tier-1 V2 ZIP: 76 профилей, `combined_systems_summary.csv`, 14 current профилей, `current_systems_rows.csv`, исходники и `SOURCE_COMMITS.txt`.
- Архивные source hashes и SHA256 исходных артефактов находятся в приложенных файлах; не подменяются новыми.
- [Оригинальный код Tier-1](compression_lab/shtenco_tier1_engines.py) · [Tier-1 V2](compression_lab/shtenco_tier1_v2.py) · [Gabriel-Horn](compression_lab/gabriel_horn_engine.py) · [Воспроизводимый runner](compression_lab/benchmark_unified_tier1.py).
- **SABF-X/PBM-39X оптимизации из других пакетов не добавлены в таблицу выше**, потому что владелец потребовал использовать **только эти два ZIP**; в них нет новых измерений этих внешних V2/V3-оптимизаций.

## Инженерная дорожная карта

1. Re-run исходников из двух исходных ZIP на одинаковом корпусе с новым run ID и SHA.
2. Раздельный SAEI для 14 current и исторического 69-run.
3. Enterprise dataset validation: документы, БД, модели, логи, медиа с текущей лицензией.
4. Реальный PoC ЦОД: CPU, RAM, архивные байты, egress, restore, TCO, SLA.
5. Публикация только воспроизводимого evidence с сохранёнными отрицательными результатами.

**Лицензирование:** Proprietary / All Rights Reserved.