# АУДИТ СОХРАННОСТИ ДВИЖКОВ SHTENCO — 20 октября 2026 года

## Проверенное заключение

**Ни один исходный файл компрессоров, существовавший до обновления README/бенчмарков, не удалён и не перезаписан.**

Сравнение Git-деревьев, не субъективный вывод:
- контрольный исходный commit: `10cee55081543c0f0152e6303e59013472d404ae`;
- полное дерево исходного состояния: 52 файлов и gitlink;
- полное дерево текущего состояния: 110 файлов и gitlink;
- удалено оригинальных файлов: **0**;
- модифицировано старых Python-файлов: **0**;
- исходный код компрессоров `compression_lab/*.py` сохранён byte-for-byte: **ДА**;
- изменённые старые файлы: `README.md`.
- gitlink `source_snapshot`: `c681ec94fe5194156b71fc304035f7aaff4d2327` без изменений.

## Где находятся исторические реализации

Фактическое новое имя репозитория-источника: [`Shtenco/synergy_agi_olga`](https://github.com/Shtenco/synergy_agi_olga).

**Оригинальный точный commit найден и дерево прочитано через GitHub API**: [исторический snapshot](https://github.com/Shtenco/synergy_agi_olga/tree/c681ec94fe5194156b71fc304035f7aaff4d2327).

В историческом snapshot 41 объектов, включая следующие исходники:
- [`compression_lab/__init__.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/__init__.py) (62 bytes)
- [`compression_lab/__main__.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/__main__.py) (70 bytes)
- [`compression_lab/benchmark_all_systems_exact.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/benchmark_all_systems_exact.py) (29470 bytes)
- [`compression_lab/benchmark_graph_ai_v5.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/benchmark_graph_ai_v5.py) (11770 bytes)
- [`compression_lab/benchmark_graph_ai_v51.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/benchmark_graph_ai_v51.py) (6408 bytes)
- [`compression_lab/benchmark_tier1_exact.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/benchmark_tier1_exact.py) (707 bytes)
- [`compression_lab/benchmark_v4.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/benchmark_v4.py) (11296 bytes)
- [`compression_lab/build_exact_v2_graph_ai.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/build_exact_v2_graph_ai.py) (1791 bytes)
- [`compression_lab/egd256_web_app_v3.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/egd256_web_app_v3.py) (70653 bytes)
- [`compression_lab/egd256_web_app_v5_graph_ai.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/egd256_web_app_v5_graph_ai.py) (1505 bytes)
- [`compression_lab/graph_ai_v2_integration.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/graph_ai_v2_integration.py) (5288 bytes)
- [`compression_lab/shtenco_graph_ai_core.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/shtenco_graph_ai_core.py) (28783 bytes)
- [`compression_lab/shtenco_graph_ai_v51.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/shtenco_graph_ai_v51.py) (11286 bytes)
- [`compression_lab/shtenco_graph_ai_v52.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/shtenco_graph_ai_v52.py) (3020 bytes)
- [`compression_lab/shtenco_tier1_engines.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/shtenco_tier1_engines.py) (11140 bytes)
- [`compression_lab/test_graph_ai_v5.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/test_graph_ai_v5.py) (5692 bytes)
- [`compression_lab/test_tier1_engines.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/test_tier1_engines.py) (542 bytes)
- [`compression_lab/test_umc.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/test_umc.py) (404 bytes)
- [`compression_lab/test_umc256_engine.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/test_umc256_engine.py) (1380 bytes)
- [`compression_lab/umc256_engine.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/umc256_engine.py) (11814 bytes)
- [`compression_lab/umd_selector.py`](https://github.com/Shtenco/synergy_agi_olga/blob/c681ec94fe5194156b71fc304035f7aaff4d2327/compression_lab/umd_selector.py) (580 bytes)

## Реальное число движков и профилей

**76 — это количество уникальных имён профилей в замороженном объединённом benchmark-реестре от 30.07.2026, а не количество отдельных Python-файлов/математически независимых кодеков.**

- старый benchmark baseline: 69 систем, агрегированные результаты внутри `compression_lab/frozen_tier1_summary.py`;
- старые исходники: отдельный исторический Git snapshot, теперь доступный по каноническому имени `synergy_agi_olga`;
- актуальные модули: `egd256_web_app_v5_graph_ai.py`, `shtenco_tier1_engines.py`, `shtenco_tier1_v2.py`, `shtenco_tier1_v21.py`, `gabriel_horn_engine.py`;
- **52×**: заявление владельца, точный протокол и входной корпус ещё не локализованы.

## Ошибка предыдущего бенчмарка

В `benchmarks/extended_80plus_20261020/` были заново запущены 38 **внешних** профилей на 11 входных файлах. Старые 69 профилей не были заново исполнены. Нельзя считать 38 внешних профилей новым полным benchmark 80+ SHTENCO.

## Что нужно для полного исполнения

1. Checkout исторического snapshot по точному SHA из канонического переименованного репозитория.
2. Запустить historical `benchmark_all_systems_exact.py` и `benchmark_graph_ai_v51.py`, проверить зависимости и реестры.
3. Запустить текущий `benchmark_unified_tier1.py` + внешние кодеки на идентичных dataset bytes.
4. Единый CSV должен помечать `historical_replayed`, `active_replayed`, `world_fresh`, `unavailable`, `failed`, исключая double-counting aliases.
5. Для 52× требуется конкретный датасет, архив, `source SHA256`, `restored SHA256` и реальный сжатый размер.

**Это аудит сохранности источников. Он не означает успешный повторный прогон всех исторических систем.**
