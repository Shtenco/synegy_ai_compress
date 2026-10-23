 <p align="center"><img src="assets/readme/hero-v2.svg" width="100%" alt="SHTENCO SYNERGY AI COMPRESS" /></p>

<h1 align="center">SHTENCO SYNERGY AI COMPRESS</h1>

<p align="center"><strong>Собственная архитектура lossless-компрессии для структурированных данных, архивов, версий и вычислительных артефактов.</strong></p>

<p align="center">Compression Research · Archival Systems · Entropy Coding · Reversible Data Modeling · Enterprise Storage</p>

<p align="center"><img src="assets/readme/family-v2.svg" width="100%" alt="SHTENCO compression technology portfolio" /></p>


## Полная таблица 81/81 систем — три независимых рейтинга

**Источник:** восстановленный артефакт GitHub Actions, запуск 23.10.2026; frozen baseline commit c681ec94fe5194156b71fc304035f7aaff4d2327; schema shtenco-unified-tier1-v2-federated; SHA-256 исходного frozen artifact: bb769fa6c1b65d697e66d79ac3275b1715ee0c77186669377e783734fcc47296.

Вместо одной сводки — три рейтинга одного и того же реестра из 81 системы, от лучшей к худшей по конкретному критерию. Все три таблицы содержат те же 81 системы и исходные значения PASS/total, коэффициента и времени.

**Важное ограничение сопоставимости:** реестр объединяет 69 замороженных исторических профилей (frozen-20260730) и текущие профили восстановленного прогона. У текущих измерений 209/209 PASS строк для 19 систем; это не означает 81 свежий независимый прогон. Каждый набор — 32 768 байт; текущие измерения выполнялись в 3 повторах. Поскольку происхождение и протоколы измерений смешанные, эти рейтинги — вычисляемая сортировка опубликованных значений, а не доказательство единого контрольного соревнования между всеми 81 системами. PASS/total означает точное восстановление на 11 наборах, а не число побед.

**Метод ранжирования:** (1) коэффициент — больше лучше; (2) суммарная задержка encode + decode — меньше лучше; (3) эффективность — коэффициент / (encode + decode) — больше лучше. Время и эффективность особенно чувствительны к разнице протоколов; смотрите колонку Measurement.

### 1. Максимальное сжатие

Сортировка по геометрическому среднему коэффициента сжатия — от максимального к минимальному.

| Rank | System | Family | Dataset PASS/total | Geomean ratio | Encode ms (geo mean) | Decode ms (geo mean) | Measurement | Ratio |
|---:|---|---|---|---|---|---|---|---:|
| 1 | SHTENCO OMNIA TIER1 V2 MAX | SHTENCO-OMNIA-TIER1-V2 | 11/11 | 30.34× | 2518 | 0.2817 | current | 30.340× |
| 2 | SHTENCO OMNIA-MATH V3 MAX | SHTENCO-OMNIA-MATH-V3 | 11/11 | 29.97× | 3547 | 0.2332 | current | 29.970× |
| 3 | SHTENCO OMNIA-MATH V3 BALANCED | SHTENCO-OMNIA-MATH-V3 | 11/11 | 28.06× | 409.4 | 0.3315 | current | 28.060× |
| 4 | SHTENCO OMNIA TIER1 V2 BALANCED | SHTENCO-OMNIA-TIER1-V2 | 11/11 | 27.24× | 91.94 | 0.2636 | current | 27.240× |
| 5 | SHTENCO OMNIA-MATH V3 SPEED | SHTENCO-OMNIA-MATH-V3 | 11/11 | 25.61× | 198.1 | 0.2457 | current | 25.610× |
| 6 | SHTENCO GABRIEL-HORN TIER1 MAX | SHTENCO-GABRIEL | 11/11 | 24.76× | 6891 | 0.3531 | current | 24.760× |
| 7 | SHTENCO GABRIEL-HORN TIER1 BALANCED | SHTENCO-GABRIEL | 11/11 | 24.46× | 2635 | 0.3523 | current | 24.460× |
| 8 | SHTENCO MATH PORTFOLIO V3 MAX | SHTENCO-MATH-PORTFOLIO-V3 | 11/11 | 22.67× | 480.3 | 0.5749 | current | 22.670× |
| 9 | SHTENCO GRAAL-IGC TIER1 MAX | SHTENCO-TIER1 | 11/11 | 22.63× | 4.858 | 0.1167 | current | 22.630× |
| 10 | SHTENCO TSC-X TIER1 SPATIAL | SHTENCO-TIER1 | 11/11 | 22.11× | 2.674 | 0.0949 | current | 22.110× |
| 11 | SHTENCO MATH PORTFOLIO V3 BALANCED | SHTENCO-MATH-PORTFOLIO-V3 | 11/11 | 21.96× | 189.4 | 0.3673 | current | 21.960× |
| 12 | SHTENCO SABF-X ULTIMATE GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 21.92× | 942.4 | 0.2621 | frozen-20260730 | 21.920× |
| 13 | SHTENCO TSC-X TURBOSPATIAL GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 21.91× | 91.11 | 0.4158 | frozen-20260730 | 21.910× |
| 14 | SHTENCO HACE-X CASCADE GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 21.02× | 137.5 | 0.3766 | frozen-20260730 | 21.020× |
| 15 | SHTENCO NEXUS-UMC TIER1 | SHTENCO-TIER1 | 11/11 | 19.67× | 1.461 | 0.08189 | current | 19.670× |
| 16 | SHTENCO OMNIA TIER1 V2 SPEED | SHTENCO-OMNIA-TIER1-V2 | 11/11 | 19.4× | 4.154 | 0.0581 | current | 19.400× |
| 17 | SHTENCO DDR-X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 19.21× | 51.73 | 0.1621 | frozen-20260730 | 19.210× |
| 18 | SHTENCO GRAAL-AIS TIER1 | SHTENCO-TIER1 | 11/11 | 19.21× | 1.311 | 0.1198 | current | 19.210× |
| 19 | SHTENCO CDC-RX GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 19.03× | 53.22 | 0.1635 | frozen-20260730 | 19.030× |
| 20 | SHTENCO UMC-256 MAX | SHTENCO-UMC | 11/11 | 18.88× | 1643 | 0.2694 | frozen-20260730 | 18.880× |
| 21 | SHTENCO AMCE-100X GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 18.79× | 166.4 | 0.153 | frozen-20260730 | 18.790× |
| 22 | SHTENCO SABF-X ULTIMATE | COMPRESSION-LAB | 11/11 | 18.72× | 480.6 | 0.4909 | frozen-20260730 | 18.720× |
| 23 | SABF-X + ZSTD | COMPRESSION-LAB | 11/11 | 18.64× | 22 | 0.276 | frozen-20260730 | 18.640× |
| 24 | SHTENCO RSX RECURSIVE SPATIAL GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 18.59× | 88.25 | 0.2443 | frozen-20260730 | 18.590× |
| 25 | SHTENCO ODC-XP GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 18.51× | 54.4 | 0.1799 | frozen-20260730 | 18.510× |
| 26 | SHTENCO DMB-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 18.48× | 54.4 | 0.1758 | frozen-20260730 | 18.480× |
| 27 | SHTENCO SECB-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 18.45× | 54.5 | 0.1752 | frozen-20260730 | 18.450× |
| 28 | HYBRID AI COMPRESSION ENGINE | COMPRESSION-LAB | 11/11 | 18.31× | 354 | 0.3295 | frozen-20260730 | 18.310× |
| 29 | SHTENCO PECB-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 18.26× | 54.41 | 0.173 | frozen-20260730 | 18.260× |
| 30 | SHTENCO UMC-256 BALANCED | SHTENCO-UMC | 11/11 | 18.19× | 250.5 | 0.2092 | frozen-20260730 | 18.190× |
| 31 | SHTENCO ODC-XC GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 17.89× | 55.78 | 0.1739 | frozen-20260730 | 17.890× |
| 32 | SHTENCO BPD-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 17.86× | 55.56 | 0.1739 | frozen-20260730 | 17.860× |
| 33 | SHTENCO UECB-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 17.83× | 55.56 | 0.176 | frozen-20260730 | 17.830× |
| 34 | SHTENCO ECBC-39 GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 17.47× | 59.62 | 0.1836 | frozen-20260730 | 17.470× |
| 35 | SHTENCO EGD-256 MAX GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 17.28× | 157.1 | 0.2105 | frozen-20260730 | 17.280× |
| 36 | SHTENCO GRAAL-AIS STORAGE GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 17.19× | 95.72 | 0.246 | frozen-20260730 | 17.190× |
| 37 | SHTENCO FAS-256 ATOM STORE GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 17.16× | 626.6 | 0.3963 | frozen-20260730 | 17.160× |
| 38 | SHTENCO GRAAL-IGC V5.2 | SHTENCO-GRAPH-V5.2 | 11/11 | 17.1× | 59.77 | 0.1842 | frozen-20260730 | 17.100× |
| 39 | SHTENCO SABF-X TIER1 BALANCED | SHTENCO-TIER1 | 11/11 | 17.1× | 0.8704 | 0.0416 | current | 17.100× |
| 40 | SHTENCO PBM-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 16.97× | 68.21 | 0.1906 | frozen-20260730 | 16.970× |
| 41 | SHTENCO MICA-39 GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 16.97× | 68.43 | 0.1912 | frozen-20260730 | 16.970× |
| 42 | SABF-X + ZSTD + LZMA9 | COMPRESSION-LAB | 11/11 | 16.96× | 24.15 | 0.4247 | frozen-20260730 | 16.960× |
| 43 | SABF-X + LZMA9 | COMPRESSION-LAB | 11/11 | 16.87× | 22.8 | 0.629 | frozen-20260730 | 16.870× |
| 44 | SHTENCO BLOCK_FAST X GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 16.76× | 83.17 | 0.1766 | frozen-20260730 | 16.760× |
| 45 | SHTENCO PBM-39X TIER1 | SHTENCO-TIER1 | 11/11 | 16.5× | 0.1266 | 0.04034 | current | 16.500× |
| 46 | SHTENCO SABF-X TIER1 SPEED | SHTENCO-TIER1 | 11/11 | 16.5× | 0.1322 | 0.0415 | current | 16.500× |
| 47 | SHTENCO HACE-X CASCADE | COMPRESSION-LAB | 11/11 | 16.42× | 41.01 | 1.723 | frozen-20260730 | 16.420× |
| 48 | SHTENCO AMCE-100X | COMPRESSION-LAB | 11/11 | 16.34× | 53.07 | 0.2567 | frozen-20260730 | 16.340× |
| 49 | SHTENCO BAPM-X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 16.05× | 77.93 | 0.2396 | frozen-20260730 | 16.050× |
| 50 | BROTLI-11 | COMPRESSION-LAB | 11/11 | 15.48× | 14.95 | 0.1143 | frozen-20260730 | 15.480× |
| 51 | SHTENCO SABF-X NEURAL SELECTOR | COMPRESSION-LAB | 11/11 | 15.23× | 30.18 | 0.2808 | frozen-20260730 | 15.230× |
| 52 | SHTENCO TSC-X TURBOSPATIAL | COMPRESSION-LAB | 11/11 | 14.44× | 16.8 | 2.398 | frozen-20260730 | 14.440× |
| 53 | ZSTD-22 | COMPRESSION-LAB | 11/11 | 14.07× | 3.646 | 0.07655 | frozen-20260730 | 14.070× |
| 54 | LZMA9 | COMPRESSION-LAB | 11/11 | 13.97× | 8.798 | 0.2992 | frozen-20260730 | 13.970× |
| 55 | SHTENCO UMC-256 FAST | SHTENCO-UMC | 11/11 | 13.77× | 57.25 | 0.09949 | frozen-20260730 | 13.770× |
| 56 | ZSTD-3 | COMPRESSION-LAB | 11/11 | 12.85× | 0.1211 | 0.06835 | frozen-20260730 | 12.850× |
| 57 | SHTENCO GABRIEL-HORN TIER1 SPEED | SHTENCO-GABRIEL | 11/11 | 12.45× | 113.5 | 0.3373 | current | 12.450× |
| 58 | SHTENCO SABF-X FAST | COMPRESSION-LAB | 11/11 | 11.73× | 21.16 | 0.3358 | frozen-20260730 | 11.730× |
| 59 | SHTENCO EGD-256 MAX | COMPRESSION-LAB | 11/11 | 11.47× | 38.72 | 0.4835 | frozen-20260730 | 11.470× |
| 60 | BZIP2-9 | COMPRESSION-LAB | 11/11 | 11.07× | 3.037 | 0.5497 | frozen-20260730 | 11.070× |
| 61 | GZIP-9 | COMPRESSION-LAB | 11/11 | 10.94× | 0.7156 | 0.1038 | frozen-20260730 | 10.940× |
| 62 | EGD256 + BROTLI | COMPRESSION-LAB | 11/11 | 10.68× | 18.11 | 0.7526 | frozen-20260730 | 10.680× |
| 63 | SHTENCO GRAAL-AIS STORAGE | COMPRESSION-LAB | 11/11 | 10.56× | 14.34 | 0.7364 | frozen-20260730 | 10.560× |
| 64 | SHTENCO GABRIEL-HORN TIER1 RANDOM-ACCESS | SHTENCO-GABRIEL | 11/11 | 10.21× | 3602 | 0.4957 | current | 10.210× |
| 65 | GRAPH DELTA ENCODING | COMPRESSION-LAB | 11/11 | 10.08× | 7.945 | 2.848 | frozen-20260730 | 10.080× |
| 66 | SHTENCO RSX RECURSIVE SPATIAL | COMPRESSION-LAB | 11/11 | 9.943× | 15.03 | 1.096 | frozen-20260730 | 9.9430× |
| 67 | EGD256 + LZMA | COMPRESSION-LAB | 11/11 | 9.888× | 10.29 | 1.08 | frozen-20260730 | 9.8880× |
| 68 | SHTENCO BLOCK_FAST X | COMPRESSION-LAB | 11/11 | 9.858× | 8.085 | 0.1943 | frozen-20260730 | 9.8580× |
| 69 | SHTENCO EGD-256 BIP39 GRAPH | COMPRESSION-LAB | 11/11 | 9.807× | 15.62 | 1.058 | frozen-20260730 | 9.8070× |
| 70 | EGD256 + ZSTD | COMPRESSION-LAB | 11/11 | 9.525× | 5.089 | 0.6827 | frozen-20260730 | 9.5250× |
| 71 | SHTENCO EGD-256 RECURSIVE GRAPH | COMPRESSION-LAB | 11/11 | 8.768× | 18.95 | 2.875 | frozen-20260730 | 8.7680× |
| 72 | rANS + DICTIONARY | COMPRESSION-LAB | 11/11 | 2.941× | 6.539 | 5.006 | frozen-20260730 | 2.9410× |
| 73 | SHTENCO FAS-256 ATOM STORE | COMPRESSION-LAB | 11/11 | 2.936× | 285.9 | 285.4 | frozen-20260730 | 2.9360× |
| 74 | INTEGER RANGE CODING | COMPRESSION-LAB | 11/11 | 2.612× | 508 | 519.1 | frozen-20260730 | 2.6120× |
| 75 | ADAPTIVE ARITHMETIC CODING | COMPRESSION-LAB | 11/11 | 1.929× | 568.6 | 579.6 | frozen-20260730 | 1.9290× |
| 76 | ARITHMETIC CODING | COMPRESSION-LAB | 11/11 | 1.866× | 527.9 | 536.6 | frozen-20260730 | 1.8660× |
| 77 | BIP39 + ARITHMETIC | COMPRESSION-LAB | 11/11 | 1.863× | 523.8 | 531 | frozen-20260730 | 1.8630× |
| 78 | rANS CODING | COMPRESSION-LAB | 11/11 | 1.853× | 9.163 | 7.648 | frozen-20260730 | 1.8530× |
| 79 | CANONICAL HUFFMAN | COMPRESSION-LAB | 11/11 | 1.683× | 28.72 | 37.75 | frozen-20260730 | 1.6830× |
| 80 | ADAPTIVE HUFFMAN | COMPRESSION-LAB | 11/11 | 1.679× | 28.44 | 37.71 | frozen-20260730 | 1.6790× |
| 81 | RAW STORE (reference) | REFERENCE | 11/11 | 1× | 0.0006836 | 0.0005698 | frozen-20260730 | 1.0000× |

### 2. Максимальная скорость

Сортировка по сумме геометрических средних времени кодирования и декодирования — от минимальной задержки к максимальной.

| Rank | System | Family | Dataset PASS/total | Geomean ratio | Encode ms (geo mean) | Decode ms (geo mean) | Measurement | Total latency ms |
|---:|---|---|---|---|---|---|---|---:|
| 1 | RAW STORE (reference) | REFERENCE | 11/11 | 1× | 0.0006836 | 0.0005698 | frozen-20260730 | 0.0012534 |
| 2 | SHTENCO PBM-39X TIER1 | SHTENCO-TIER1 | 11/11 | 16.5× | 0.1266 | 0.04034 | current | 0.16694 |
| 3 | SHTENCO SABF-X TIER1 SPEED | SHTENCO-TIER1 | 11/11 | 16.5× | 0.1322 | 0.0415 | current | 0.17370 |
| 4 | ZSTD-3 | COMPRESSION-LAB | 11/11 | 12.85× | 0.1211 | 0.06835 | frozen-20260730 | 0.18945 |
| 5 | GZIP-9 | COMPRESSION-LAB | 11/11 | 10.94× | 0.7156 | 0.1038 | frozen-20260730 | 0.81940 |
| 6 | SHTENCO SABF-X TIER1 BALANCED | SHTENCO-TIER1 | 11/11 | 17.1× | 0.8704 | 0.0416 | current | 0.91200 |
| 7 | SHTENCO GRAAL-AIS TIER1 | SHTENCO-TIER1 | 11/11 | 19.21× | 1.311 | 0.1198 | current | 1.4308 |
| 8 | SHTENCO NEXUS-UMC TIER1 | SHTENCO-TIER1 | 11/11 | 19.67× | 1.461 | 0.08189 | current | 1.5429 |
| 9 | SHTENCO TSC-X TIER1 SPATIAL | SHTENCO-TIER1 | 11/11 | 22.11× | 2.674 | 0.0949 | current | 2.7689 |
| 10 | BZIP2-9 | COMPRESSION-LAB | 11/11 | 11.07× | 3.037 | 0.5497 | frozen-20260730 | 3.5867 |
| 11 | ZSTD-22 | COMPRESSION-LAB | 11/11 | 14.07× | 3.646 | 0.07655 | frozen-20260730 | 3.7226 |
| 12 | SHTENCO OMNIA TIER1 V2 SPEED | SHTENCO-OMNIA-TIER1-V2 | 11/11 | 19.4× | 4.154 | 0.0581 | current | 4.2121 |
| 13 | SHTENCO GRAAL-IGC TIER1 MAX | SHTENCO-TIER1 | 11/11 | 22.63× | 4.858 | 0.1167 | current | 4.9747 |
| 14 | EGD256 + ZSTD | COMPRESSION-LAB | 11/11 | 9.525× | 5.089 | 0.6827 | frozen-20260730 | 5.7717 |
| 15 | SHTENCO BLOCK_FAST X | COMPRESSION-LAB | 11/11 | 9.858× | 8.085 | 0.1943 | frozen-20260730 | 8.2793 |
| 16 | LZMA9 | COMPRESSION-LAB | 11/11 | 13.97× | 8.798 | 0.2992 | frozen-20260730 | 9.0972 |
| 17 | GRAPH DELTA ENCODING | COMPRESSION-LAB | 11/11 | 10.08× | 7.945 | 2.848 | frozen-20260730 | 10.793 |
| 18 | EGD256 + LZMA | COMPRESSION-LAB | 11/11 | 9.888× | 10.29 | 1.08 | frozen-20260730 | 11.370 |
| 19 | rANS + DICTIONARY | COMPRESSION-LAB | 11/11 | 2.941× | 6.539 | 5.006 | frozen-20260730 | 11.545 |
| 20 | BROTLI-11 | COMPRESSION-LAB | 11/11 | 15.48× | 14.95 | 0.1143 | frozen-20260730 | 15.064 |
| 21 | SHTENCO GRAAL-AIS STORAGE | COMPRESSION-LAB | 11/11 | 10.56× | 14.34 | 0.7364 | frozen-20260730 | 15.076 |
| 22 | SHTENCO RSX RECURSIVE SPATIAL | COMPRESSION-LAB | 11/11 | 9.943× | 15.03 | 1.096 | frozen-20260730 | 16.126 |
| 23 | SHTENCO EGD-256 BIP39 GRAPH | COMPRESSION-LAB | 11/11 | 9.807× | 15.62 | 1.058 | frozen-20260730 | 16.678 |
| 24 | rANS CODING | COMPRESSION-LAB | 11/11 | 1.853× | 9.163 | 7.648 | frozen-20260730 | 16.811 |
| 25 | EGD256 + BROTLI | COMPRESSION-LAB | 11/11 | 10.68× | 18.11 | 0.7526 | frozen-20260730 | 18.863 |
| 26 | SHTENCO TSC-X TURBOSPATIAL | COMPRESSION-LAB | 11/11 | 14.44× | 16.8 | 2.398 | frozen-20260730 | 19.198 |
| 27 | SHTENCO SABF-X FAST | COMPRESSION-LAB | 11/11 | 11.73× | 21.16 | 0.3358 | frozen-20260730 | 21.496 |
| 28 | SHTENCO EGD-256 RECURSIVE GRAPH | COMPRESSION-LAB | 11/11 | 8.768× | 18.95 | 2.875 | frozen-20260730 | 21.825 |
| 29 | SABF-X + ZSTD | COMPRESSION-LAB | 11/11 | 18.64× | 22 | 0.276 | frozen-20260730 | 22.276 |
| 30 | SABF-X + LZMA9 | COMPRESSION-LAB | 11/11 | 16.87× | 22.8 | 0.629 | frozen-20260730 | 23.429 |
| 31 | SABF-X + ZSTD + LZMA9 | COMPRESSION-LAB | 11/11 | 16.96× | 24.15 | 0.4247 | frozen-20260730 | 24.575 |
| 32 | SHTENCO SABF-X NEURAL SELECTOR | COMPRESSION-LAB | 11/11 | 15.23× | 30.18 | 0.2808 | frozen-20260730 | 30.461 |
| 33 | SHTENCO EGD-256 MAX | COMPRESSION-LAB | 11/11 | 11.47× | 38.72 | 0.4835 | frozen-20260730 | 39.203 |
| 34 | SHTENCO HACE-X CASCADE | COMPRESSION-LAB | 11/11 | 16.42× | 41.01 | 1.723 | frozen-20260730 | 42.733 |
| 35 | SHTENCO DDR-X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 19.21× | 51.73 | 0.1621 | frozen-20260730 | 51.892 |
| 36 | SHTENCO AMCE-100X | COMPRESSION-LAB | 11/11 | 16.34× | 53.07 | 0.2567 | frozen-20260730 | 53.327 |
| 37 | SHTENCO CDC-RX GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 19.03× | 53.22 | 0.1635 | frozen-20260730 | 53.383 |
| 38 | SHTENCO DMB-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 18.48× | 54.4 | 0.1758 | frozen-20260730 | 54.576 |
| 39 | SHTENCO ODC-XP GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 18.51× | 54.4 | 0.1799 | frozen-20260730 | 54.580 |
| 40 | SHTENCO PECB-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 18.26× | 54.41 | 0.173 | frozen-20260730 | 54.583 |
| 41 | SHTENCO SECB-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 18.45× | 54.5 | 0.1752 | frozen-20260730 | 54.675 |
| 42 | SHTENCO BPD-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 17.86× | 55.56 | 0.1739 | frozen-20260730 | 55.734 |
| 43 | SHTENCO UECB-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 17.83× | 55.56 | 0.176 | frozen-20260730 | 55.736 |
| 44 | SHTENCO ODC-XC GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 17.89× | 55.78 | 0.1739 | frozen-20260730 | 55.954 |
| 45 | SHTENCO UMC-256 FAST | SHTENCO-UMC | 11/11 | 13.77× | 57.25 | 0.09949 | frozen-20260730 | 57.349 |
| 46 | SHTENCO ECBC-39 GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 17.47× | 59.62 | 0.1836 | frozen-20260730 | 59.804 |
| 47 | SHTENCO GRAAL-IGC V5.2 | SHTENCO-GRAPH-V5.2 | 11/11 | 17.1× | 59.77 | 0.1842 | frozen-20260730 | 59.954 |
| 48 | ADAPTIVE HUFFMAN | COMPRESSION-LAB | 11/11 | 1.679× | 28.44 | 37.71 | frozen-20260730 | 66.150 |
| 49 | CANONICAL HUFFMAN | COMPRESSION-LAB | 11/11 | 1.683× | 28.72 | 37.75 | frozen-20260730 | 66.470 |
| 50 | SHTENCO PBM-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 16.97× | 68.21 | 0.1906 | frozen-20260730 | 68.401 |
| 51 | SHTENCO MICA-39 GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 16.97× | 68.43 | 0.1912 | frozen-20260730 | 68.621 |
| 52 | SHTENCO BAPM-X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 16.05× | 77.93 | 0.2396 | frozen-20260730 | 78.170 |
| 53 | SHTENCO BLOCK_FAST X GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 16.76× | 83.17 | 0.1766 | frozen-20260730 | 83.347 |
| 54 | SHTENCO RSX RECURSIVE SPATIAL GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 18.59× | 88.25 | 0.2443 | frozen-20260730 | 88.494 |
| 55 | SHTENCO TSC-X TURBOSPATIAL GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 21.91× | 91.11 | 0.4158 | frozen-20260730 | 91.526 |
| 56 | SHTENCO OMNIA TIER1 V2 BALANCED | SHTENCO-OMNIA-TIER1-V2 | 11/11 | 27.24× | 91.94 | 0.2636 | current | 92.204 |
| 57 | SHTENCO GRAAL-AIS STORAGE GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 17.19× | 95.72 | 0.246 | frozen-20260730 | 95.966 |
| 58 | SHTENCO GABRIEL-HORN TIER1 SPEED | SHTENCO-GABRIEL | 11/11 | 12.45× | 113.5 | 0.3373 | current | 113.84 |
| 59 | SHTENCO HACE-X CASCADE GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 21.02× | 137.5 | 0.3766 | frozen-20260730 | 137.88 |
| 60 | SHTENCO EGD-256 MAX GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 17.28× | 157.1 | 0.2105 | frozen-20260730 | 157.31 |
| 61 | SHTENCO AMCE-100X GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 18.79× | 166.4 | 0.153 | frozen-20260730 | 166.55 |
| 62 | SHTENCO MATH PORTFOLIO V3 BALANCED | SHTENCO-MATH-PORTFOLIO-V3 | 11/11 | 21.96× | 189.4 | 0.3673 | current | 189.77 |
| 63 | SHTENCO OMNIA-MATH V3 SPEED | SHTENCO-OMNIA-MATH-V3 | 11/11 | 25.61× | 198.1 | 0.2457 | current | 198.35 |
| 64 | SHTENCO UMC-256 BALANCED | SHTENCO-UMC | 11/11 | 18.19× | 250.5 | 0.2092 | frozen-20260730 | 250.71 |
| 65 | HYBRID AI COMPRESSION ENGINE | COMPRESSION-LAB | 11/11 | 18.31× | 354 | 0.3295 | frozen-20260730 | 354.33 |
| 66 | SHTENCO OMNIA-MATH V3 BALANCED | SHTENCO-OMNIA-MATH-V3 | 11/11 | 28.06× | 409.4 | 0.3315 | current | 409.73 |
| 67 | SHTENCO MATH PORTFOLIO V3 MAX | SHTENCO-MATH-PORTFOLIO-V3 | 11/11 | 22.67× | 480.3 | 0.5749 | current | 480.87 |
| 68 | SHTENCO SABF-X ULTIMATE | COMPRESSION-LAB | 11/11 | 18.72× | 480.6 | 0.4909 | frozen-20260730 | 481.09 |
| 69 | SHTENCO FAS-256 ATOM STORE | COMPRESSION-LAB | 11/11 | 2.936× | 285.9 | 285.4 | frozen-20260730 | 571.30 |
| 70 | SHTENCO FAS-256 ATOM STORE GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 17.16× | 626.6 | 0.3963 | frozen-20260730 | 627.00 |
| 71 | SHTENCO SABF-X ULTIMATE GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 21.92× | 942.4 | 0.2621 | frozen-20260730 | 942.66 |
| 72 | INTEGER RANGE CODING | COMPRESSION-LAB | 11/11 | 2.612× | 508 | 519.1 | frozen-20260730 | 1027.1 |
| 73 | BIP39 + ARITHMETIC | COMPRESSION-LAB | 11/11 | 1.863× | 523.8 | 531 | frozen-20260730 | 1054.8 |
| 74 | ARITHMETIC CODING | COMPRESSION-LAB | 11/11 | 1.866× | 527.9 | 536.6 | frozen-20260730 | 1064.5 |
| 75 | ADAPTIVE ARITHMETIC CODING | COMPRESSION-LAB | 11/11 | 1.929× | 568.6 | 579.6 | frozen-20260730 | 1148.2 |
| 76 | SHTENCO UMC-256 MAX | SHTENCO-UMC | 11/11 | 18.88× | 1643 | 0.2694 | frozen-20260730 | 1643.3 |
| 77 | SHTENCO OMNIA TIER1 V2 MAX | SHTENCO-OMNIA-TIER1-V2 | 11/11 | 30.34× | 2518 | 0.2817 | current | 2518.3 |
| 78 | SHTENCO GABRIEL-HORN TIER1 BALANCED | SHTENCO-GABRIEL | 11/11 | 24.46× | 2635 | 0.3523 | current | 2635.4 |
| 79 | SHTENCO OMNIA-MATH V3 MAX | SHTENCO-OMNIA-MATH-V3 | 11/11 | 29.97× | 3547 | 0.2332 | current | 3547.2 |
| 80 | SHTENCO GABRIEL-HORN TIER1 RANDOM-ACCESS | SHTENCO-GABRIEL | 11/11 | 10.21× | 3602 | 0.4957 | current | 3602.5 |
| 81 | SHTENCO GABRIEL-HORN TIER1 MAX | SHTENCO-GABRIEL | 11/11 | 24.76× | 6891 | 0.3531 | current | 6891.4 |

### 3. Сбалансированная эффективность

Сортировка по отношению коэффициента сжатия к суммарному времени кодирования и декодирования — от максимального к минимальному.

| Rank | System | Family | Dataset PASS/total | Geomean ratio | Encode ms (geo mean) | Decode ms (geo mean) | Measurement | Ratio / total latency |
|---:|---|---|---|---|---|---|---|---:|
| 1 | RAW STORE (reference) | REFERENCE | 11/11 | 1× | 0.0006836 | 0.0005698 | frozen-20260730 | 797.83 |
| 2 | SHTENCO PBM-39X TIER1 | SHTENCO-TIER1 | 11/11 | 16.5× | 0.1266 | 0.04034 | current | 98.838 |
| 3 | SHTENCO SABF-X TIER1 SPEED | SHTENCO-TIER1 | 11/11 | 16.5× | 0.1322 | 0.0415 | current | 94.991 |
| 4 | ZSTD-3 | COMPRESSION-LAB | 11/11 | 12.85× | 0.1211 | 0.06835 | frozen-20260730 | 67.828 |
| 5 | SHTENCO SABF-X TIER1 BALANCED | SHTENCO-TIER1 | 11/11 | 17.1× | 0.8704 | 0.0416 | current | 18.750 |
| 6 | SHTENCO GRAAL-AIS TIER1 | SHTENCO-TIER1 | 11/11 | 19.21× | 1.311 | 0.1198 | current | 13.426 |
| 7 | GZIP-9 | COMPRESSION-LAB | 11/11 | 10.94× | 0.7156 | 0.1038 | frozen-20260730 | 13.351 |
| 8 | SHTENCO NEXUS-UMC TIER1 | SHTENCO-TIER1 | 11/11 | 19.67× | 1.461 | 0.08189 | current | 12.749 |
| 9 | SHTENCO TSC-X TIER1 SPATIAL | SHTENCO-TIER1 | 11/11 | 22.11× | 2.674 | 0.0949 | current | 7.9851 |
| 10 | SHTENCO OMNIA TIER1 V2 SPEED | SHTENCO-OMNIA-TIER1-V2 | 11/11 | 19.4× | 4.154 | 0.0581 | current | 4.6058 |
| 11 | SHTENCO GRAAL-IGC TIER1 MAX | SHTENCO-TIER1 | 11/11 | 22.63× | 4.858 | 0.1167 | current | 4.5490 |
| 12 | ZSTD-22 | COMPRESSION-LAB | 11/11 | 14.07× | 3.646 | 0.07655 | frozen-20260730 | 3.7797 |
| 13 | BZIP2-9 | COMPRESSION-LAB | 11/11 | 11.07× | 3.037 | 0.5497 | frozen-20260730 | 3.0864 |
| 14 | EGD256 + ZSTD | COMPRESSION-LAB | 11/11 | 9.525× | 5.089 | 0.6827 | frozen-20260730 | 1.6503 |
| 15 | LZMA9 | COMPRESSION-LAB | 11/11 | 13.97× | 8.798 | 0.2992 | frozen-20260730 | 1.5356 |
| 16 | SHTENCO BLOCK_FAST X | COMPRESSION-LAB | 11/11 | 9.858× | 8.085 | 0.1943 | frozen-20260730 | 1.1907 |
| 17 | BROTLI-11 | COMPRESSION-LAB | 11/11 | 15.48× | 14.95 | 0.1143 | frozen-20260730 | 1.0276 |
| 18 | GRAPH DELTA ENCODING | COMPRESSION-LAB | 11/11 | 10.08× | 7.945 | 2.848 | frozen-20260730 | 0.93394 |
| 19 | EGD256 + LZMA | COMPRESSION-LAB | 11/11 | 9.888× | 10.29 | 1.08 | frozen-20260730 | 0.86966 |
| 20 | SABF-X + ZSTD | COMPRESSION-LAB | 11/11 | 18.64× | 22 | 0.276 | frozen-20260730 | 0.83678 |
| 21 | SHTENCO TSC-X TURBOSPATIAL | COMPRESSION-LAB | 11/11 | 14.44× | 16.8 | 2.398 | frozen-20260730 | 0.75216 |
| 22 | SABF-X + LZMA9 | COMPRESSION-LAB | 11/11 | 16.87× | 22.8 | 0.629 | frozen-20260730 | 0.72005 |
| 23 | SHTENCO GRAAL-AIS STORAGE | COMPRESSION-LAB | 11/11 | 10.56× | 14.34 | 0.7364 | frozen-20260730 | 0.70043 |
| 24 | SABF-X + ZSTD + LZMA9 | COMPRESSION-LAB | 11/11 | 16.96× | 24.15 | 0.4247 | frozen-20260730 | 0.69014 |
| 25 | SHTENCO RSX RECURSIVE SPATIAL | COMPRESSION-LAB | 11/11 | 9.943× | 15.03 | 1.096 | frozen-20260730 | 0.61658 |
| 26 | SHTENCO EGD-256 BIP39 GRAPH | COMPRESSION-LAB | 11/11 | 9.807× | 15.62 | 1.058 | frozen-20260730 | 0.58802 |
| 27 | EGD256 + BROTLI | COMPRESSION-LAB | 11/11 | 10.68× | 18.11 | 0.7526 | frozen-20260730 | 0.56620 |
| 28 | SHTENCO SABF-X FAST | COMPRESSION-LAB | 11/11 | 11.73× | 21.16 | 0.3358 | frozen-20260730 | 0.54569 |
| 29 | SHTENCO SABF-X NEURAL SELECTOR | COMPRESSION-LAB | 11/11 | 15.23× | 30.18 | 0.2808 | frozen-20260730 | 0.49999 |
| 30 | SHTENCO EGD-256 RECURSIVE GRAPH | COMPRESSION-LAB | 11/11 | 8.768× | 18.95 | 2.875 | frozen-20260730 | 0.40174 |
| 31 | SHTENCO HACE-X CASCADE | COMPRESSION-LAB | 11/11 | 16.42× | 41.01 | 1.723 | frozen-20260730 | 0.38425 |
| 32 | SHTENCO DDR-X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 19.21× | 51.73 | 0.1621 | frozen-20260730 | 0.37019 |
| 33 | SHTENCO CDC-RX GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 19.03× | 53.22 | 0.1635 | frozen-20260730 | 0.35648 |
| 34 | SHTENCO ODC-XP GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 18.51× | 54.4 | 0.1799 | frozen-20260730 | 0.33914 |
| 35 | SHTENCO DMB-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 18.48× | 54.4 | 0.1758 | frozen-20260730 | 0.33861 |
| 36 | SHTENCO SECB-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 18.45× | 54.5 | 0.1752 | frozen-20260730 | 0.33745 |
| 37 | SHTENCO PECB-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 18.26× | 54.41 | 0.173 | frozen-20260730 | 0.33454 |
| 38 | SHTENCO BPD-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 17.86× | 55.56 | 0.1739 | frozen-20260730 | 0.32045 |
| 39 | SHTENCO UECB-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 17.83× | 55.56 | 0.176 | frozen-20260730 | 0.31990 |
| 40 | SHTENCO ODC-XC GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 17.89× | 55.78 | 0.1739 | frozen-20260730 | 0.31973 |
| 41 | SHTENCO AMCE-100X | COMPRESSION-LAB | 11/11 | 16.34× | 53.07 | 0.2567 | frozen-20260730 | 0.30641 |
| 42 | SHTENCO OMNIA TIER1 V2 BALANCED | SHTENCO-OMNIA-TIER1-V2 | 11/11 | 27.24× | 91.94 | 0.2636 | current | 0.29543 |
| 43 | SHTENCO EGD-256 MAX | COMPRESSION-LAB | 11/11 | 11.47× | 38.72 | 0.4835 | frozen-20260730 | 0.29258 |
| 44 | SHTENCO ECBC-39 GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 17.47× | 59.62 | 0.1836 | frozen-20260730 | 0.29212 |
| 45 | SHTENCO GRAAL-IGC V5.2 | SHTENCO-GRAPH-V5.2 | 11/11 | 17.1× | 59.77 | 0.1842 | frozen-20260730 | 0.28522 |
| 46 | rANS + DICTIONARY | COMPRESSION-LAB | 11/11 | 2.941× | 6.539 | 5.006 | frozen-20260730 | 0.25474 |
| 47 | SHTENCO PBM-39X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 16.97× | 68.21 | 0.1906 | frozen-20260730 | 0.24810 |
| 48 | SHTENCO MICA-39 GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 16.97× | 68.43 | 0.1912 | frozen-20260730 | 0.24730 |
| 49 | SHTENCO UMC-256 FAST | SHTENCO-UMC | 11/11 | 13.77× | 57.25 | 0.09949 | frozen-20260730 | 0.24011 |
| 50 | SHTENCO TSC-X TURBOSPATIAL GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 21.91× | 91.11 | 0.4158 | frozen-20260730 | 0.23939 |
| 51 | SHTENCO RSX RECURSIVE SPATIAL GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 18.59× | 88.25 | 0.2443 | frozen-20260730 | 0.21007 |
| 52 | SHTENCO BAPM-X GRAPH | SHTENCO-GRAPH-RESEARCH-V5.2 | 11/11 | 16.05× | 77.93 | 0.2396 | frozen-20260730 | 0.20532 |
| 53 | SHTENCO BLOCK_FAST X GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 16.76× | 83.17 | 0.1766 | frozen-20260730 | 0.20109 |
| 54 | SHTENCO GRAAL-AIS STORAGE GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 17.19× | 95.72 | 0.246 | frozen-20260730 | 0.17913 |
| 55 | SHTENCO HACE-X CASCADE GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 21.02× | 137.5 | 0.3766 | frozen-20260730 | 0.15246 |
| 56 | SHTENCO OMNIA-MATH V3 SPEED | SHTENCO-OMNIA-MATH-V3 | 11/11 | 25.61× | 198.1 | 0.2457 | current | 0.12912 |
| 57 | SHTENCO MATH PORTFOLIO V3 BALANCED | SHTENCO-MATH-PORTFOLIO-V3 | 11/11 | 21.96× | 189.4 | 0.3673 | current | 0.11572 |
| 58 | SHTENCO AMCE-100X GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 18.79× | 166.4 | 0.153 | frozen-20260730 | 0.11282 |
| 59 | rANS CODING | COMPRESSION-LAB | 11/11 | 1.853× | 9.163 | 7.648 | frozen-20260730 | 0.11023 |
| 60 | SHTENCO EGD-256 MAX GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 17.28× | 157.1 | 0.2105 | frozen-20260730 | 0.10985 |
| 61 | SHTENCO GABRIEL-HORN TIER1 SPEED | SHTENCO-GABRIEL | 11/11 | 12.45× | 113.5 | 0.3373 | current | 0.10937 |
| 62 | SHTENCO UMC-256 BALANCED | SHTENCO-UMC | 11/11 | 18.19× | 250.5 | 0.2092 | frozen-20260730 | 0.072554 |
| 63 | SHTENCO OMNIA-MATH V3 BALANCED | SHTENCO-OMNIA-MATH-V3 | 11/11 | 28.06× | 409.4 | 0.3315 | current | 0.068484 |
| 64 | HYBRID AI COMPRESSION ENGINE | COMPRESSION-LAB | 11/11 | 18.31× | 354 | 0.3295 | frozen-20260730 | 0.051675 |
| 65 | SHTENCO MATH PORTFOLIO V3 MAX | SHTENCO-MATH-PORTFOLIO-V3 | 11/11 | 22.67× | 480.3 | 0.5749 | current | 0.047143 |
| 66 | SHTENCO SABF-X ULTIMATE | COMPRESSION-LAB | 11/11 | 18.72× | 480.6 | 0.4909 | frozen-20260730 | 0.038912 |
| 67 | SHTENCO FAS-256 ATOM STORE GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 17.16× | 626.6 | 0.3963 | frozen-20260730 | 0.027369 |
| 68 | ADAPTIVE HUFFMAN | COMPRESSION-LAB | 11/11 | 1.679× | 28.44 | 37.71 | frozen-20260730 | 0.025382 |
| 69 | CANONICAL HUFFMAN | COMPRESSION-LAB | 11/11 | 1.683× | 28.72 | 37.75 | frozen-20260730 | 0.025320 |
| 70 | SHTENCO SABF-X ULTIMATE GRAPH-AI | SHTENCO-GRAPH-V5.2 | 11/11 | 21.92× | 942.4 | 0.2621 | frozen-20260730 | 0.023253 |
| 71 | SHTENCO OMNIA TIER1 V2 MAX | SHTENCO-OMNIA-TIER1-V2 | 11/11 | 30.34× | 2518 | 0.2817 | current | 0.012048 |
| 72 | SHTENCO UMC-256 MAX | SHTENCO-UMC | 11/11 | 18.88× | 1643 | 0.2694 | frozen-20260730 | 0.011489 |
| 73 | SHTENCO GABRIEL-HORN TIER1 BALANCED | SHTENCO-GABRIEL | 11/11 | 24.46× | 2635 | 0.3523 | current | 0.0092815 |
| 74 | SHTENCO OMNIA-MATH V3 MAX | SHTENCO-OMNIA-MATH-V3 | 11/11 | 29.97× | 3547 | 0.2332 | current | 0.0084488 |
| 75 | SHTENCO FAS-256 ATOM STORE | COMPRESSION-LAB | 11/11 | 2.936× | 285.9 | 285.4 | frozen-20260730 | 0.0051392 |
| 76 | SHTENCO GABRIEL-HORN TIER1 MAX | SHTENCO-GABRIEL | 11/11 | 24.76× | 6891 | 0.3531 | current | 0.0035929 |
| 77 | SHTENCO GABRIEL-HORN TIER1 RANDOM-ACCESS | SHTENCO-GABRIEL | 11/11 | 10.21× | 3602 | 0.4957 | current | 0.0028341 |
| 78 | INTEGER RANGE CODING | COMPRESSION-LAB | 11/11 | 2.612× | 508 | 519.1 | frozen-20260730 | 0.0025431 |
| 79 | BIP39 + ARITHMETIC | COMPRESSION-LAB | 11/11 | 1.863× | 523.8 | 531 | frozen-20260730 | 0.0017662 |
| 80 | ARITHMETIC CODING | COMPRESSION-LAB | 11/11 | 1.866× | 527.9 | 536.6 | frozen-20260730 | 0.0017529 |
| 81 | ADAPTIVE ARITHMETIC CODING | COMPRESSION-LAB | 11/11 | 1.929× | 568.6 | 579.6 | frozen-20260730 | 0.0016800 |


## Инвестиционный тезис

**SHTENCO SYNERGY AI COMPRESS — не один кодек и не оболочка над сторонними архиваторами. Это исследовательская и инженерная платформа, объединяющая собственные архивные форматы, обратимые преобразования, специализированные модели данных, энтропийное кодирование и стратегии выбора компрессионного конвейера.**

Проект исследует, как использовать структуру данных до этапа энтропийного кодирования: выявлять повторяемость, зависимости между блоками и версиями, закономерности представления, пространственную организацию и структуру бинарных объектов. Цель — уменьшать избыточность на уровне представления, а затем кодировать полученный поток с учётом ограничений по размеру архива, скорости, памяти и стоимости восстановления.

Вместо предположения, что один универсальный алгоритм одинаково хорошо работает на всех данных, SHTENCO развивает семейство профилей и методов для разных режимов хранения и вычисления.

> **Единый проверенный бенчмарк:** охвачены 81/81 профилей SYNERGY; 12/81 завершили весь синтетический корпус (11/11 файлов) с подтверждённым восстановлением. Профили с тайм-аутами не учитываются как полные результаты.

## Что создаётся

<p align="center"><img src="assets/readme/architecture-v2.svg" width="100%" alt="SHTENCO compression architecture" /></p>

### 1. Самостоятельные архиваторы и контейнеры

SHTENCO включает отдельные архивные конвейеры и контейнерные архитектуры, предназначенные для сохранения исходных данных, контроля целостности и применения специализированных режимов декодирования. Контейнер может хранить служебные параметры, режим преобразования, размеры и контрольные значения, необходимые для корректного восстановления.

### 2. Обратимые модели и преобразования

До энтропийного этапа данные могут преобразовываться в более удобное для кодирования представление. В исследуемых семействах используются дельта-представления, XOR-зависимости, byte-plane transforms, графовые связи, обработка блоков и версий, пространственные представления, разбиение на сегменты и другие обратимые схемы.

Преобразование считается пригодным для lossless-конвейера только при условии, что исходный поток можно восстановить без потерь. Эффективность конкретного метода зависит от структуры входа; преобразование не обязано улучшать каждый файл, поэтому важны измерение полной стоимости и безопасный fallback.

### 3. Энтропийное кодирование

Энтропийный уровень — самостоятельное направление разработки. В технологическом портфеле исследуются арифметическое кодирование, rANS, Huffman и специализированные варианты представления остаточных потоков. В отдельных профилях могут применяться также внешние entropy backend, включая Zstandard. Эти варианты следует различать в технических описаниях и benchmark-отчётах: использование стороннего backend в конкретном конвейере не означает, что вся платформа сводится к нему.

### 4. Маршрутизация и оптимизация под задачу

Разные профили ориентированы на различные компромиссы:

- **Speed-first** — ограничение задержки и вычислительных затрат;
- **Balanced** — компромисс между размером архива и временем;
- **Size-first** — более интенсивный поиск компактного представления;
- **Structure-aware** — использование известных свойств входных данных;
- **Version-aware** — эксплуатация сходства между версиями и блоками;
- **Random-access / progressive** — архитектуры, в которых важны выборочное чтение или поэтапное восстановление, если это поддерживается конкретным форматом.

Название профиля само по себе не является доказательством производительности. Выбор должен подтверждаться воспроизводимыми измерениями на соответствующей нагрузке.

## Технологический портфель

<p align="center"><img src="assets/readme/family-v2.svg" width="100%" alt="SHTENCO compression families" /></p>

### SABF-X

Семейство профилей, ориентированных на эффективный компрессионный конвейер с акцентом на скорость либо баланс размера и времени. Используется как один из основных ориентиров при сравнении практической эффективности.

### PBM-39X

Специализированный архивный маршрут для определённых структурированных представлений, включая отдельный путь для совместимого с BIP39 словарного текста при выполнении условий распознавания. Специализированная ветка применима только к соответствующему входу и не предполагает универсального преимущества на произвольных байтах.

### OMNIA

Семейство профилей, исследующих маршрутизацию и выбор между вариантами обработки с различными затратами на кодирование и декодирование. Режимы Speed, Balanced и MAX предназначены для разных ограничений; наиболее вычислительно дорогой режим не следует автоматически считать лучшим эксплуатационным выбором.

### Gabriel Horn

Отдельное направление архивной архитектуры, в котором исследуются обратимые преобразования, блоковая организация, оболочечные представления и индексируемая структура контейнера. Возможности выборочного доступа и progressive decoding относятся к конкретной реализации и должны проверяться соответствующими тестами.

### GRAAL / EGD / TSC-X / NEXUS-UMC

Семейства, охватывающие графовое моделирование, работу с похожими блоками и версиями, пространственные и byte-plane преобразования, а также специализированную маршрутизацию. Их потенциальная ценность заключается в использовании структуры данных до энтропийного кодирования, а не только в смене уровня компрессии.

### Энтропийные кодировщики

Arithmetic coding, adaptive arithmetic coding, range coding, rANS и Huffman представлены как отдельные направления и контрольные реализации в исследовательском портфеле. Для корректного сравнения должны учитываться не только размер битового потока, но и стоимость передачи модели, таблиц, заголовков и метаданных, а также время кодирования и декодирования.

## Принципы инженерной достоверности

SHTENCO ориентирован на проверяемую lossless-компрессию, где результат должен подтверждаться восстановлением, а не только заявленным коэффициентом сжатия.

- **Точное восстановление.** Сравнение восстановленного содержимого с исходными данными.
- **Контроль целостности.** Размер и криптографический digest могут использоваться для обнаружения повреждения или некорректного декодирования.
- **Полная стоимость архива.** Учитываются контейнер, заголовки, модели, словари, индексы и иные служебные данные.
- **Измерение двух направлений.** Важны как кодирование, так и декодирование.
- **Профильная оценка.** Размер, throughput, latency, RAM и доступ к данным рассматриваются как отдельные измерения.
- **Безопасный fallback.** Если специализированное представление не даёт выигрыша, система должна иметь возможность сохранить исходные данные или выбрать другой допустимый маршрут.
- **Разделение фактов и гипотез.** Внутренний тест, независимый benchmark и промышленный пилот — разные уровни доказательности.

## Проверка корректности: охват 81/81, полный PASS 12/81

В едином актуальном сравнительном прогоне **зарегистрированы и проверялись все 81 профиля SYNERGY**, но **полностью завершили 11/11 файлов только 12/81**. Среди 40 конфигураций WORLD — **24/40** полных PASS. Успешные декодирования проверялись сопоставлением исходных байтов и SHA-256; частичные результаты и тайм-ауты не считаются полным прохождением.

Число 81/81 означает **полноту реестра исследуемых конфигураций**, а не 81 успешный полный прогон, не 81 независимый алгоритм и не доказательство превосходства над мировыми решениями. Методика и весь перечень приведены в одной таблице ниже.

## Единый полный бенчмарк: 81 SYNERGY + 40 WORLD (121 профиль)

**Источник одного прогона:** `SHTENCO_81_WORLD40_11x5MiB_VERIFIED_121.csv` (SHA-256: `57e03e2f28ab2a3fec2eacbc13dbc41d4a955057e311021a5362e4c553b04ac9`), архив исследования `SHTENCO_81_WORLD40_11x5MiB_VERIFIED_REPORT.zip`. **81/81 профилей SYNERGY перечислены** в строках 1–81; строки 82–121 — **40 внешних конфигураций WORLD**. Это **одна таблица одного сопоставимого прогона**, без смешения исторических/других корпусов.

**Методика:** 11 синтетических файлов по 5 MiB каждый (**55 MiB = 57 671 680 байт**); однопроходное измерение сжатия/распаковки каждого файла, проверка полного восстановления байтов и SHA-256. Тест запускался в пяти параллельных процессах, закреплённых за CPU-ядрами. Ограничение времени на профиль: SYNERGY 16 секунд, WORLD 18 секунд; оно объясняет часть неполных результатов и не доказывает неисправность алгоритмов. Полный рейтинг и интегральные показатели относятся только к строкам **PASS 11/11**: **12 SYNERGY, 24 WORLD**. Остальные — 69 SYNERGY и 16 WORLD — отражены как `PARTIAL`/`TIMEOUT`, без вымышленных метрик полного корпуса. Реальные клиентские данные, энергопотребление, RAM и I/O в этом прогоне **не измерялись**.

**Как рассчитаны коэффициенты именно из измеренных байтов и секунд:**

- `R = original_bytes / archive_bytes` — коэффициент сжатия по сумме всех 11 файлов, включая измеренный размер контейнера;
- `K_ЦОД = 1 − archive_bytes / original_bytes` — **доля экономии payload-хранилища** для этого корпуса (не коэффициент снижения совокупной стоимости ЦОД);
- `Экономия байтов, % = 100 × K_ЦОД`; `TiB/1 PiB = 1024 × K_ЦОД` — *условно* высвобождаемые TiB на 1 PiB логических данных **при совпадении состава с тестовым корпусом и отсутствии других накладных расходов**;
- `SAEI хран., % = 100 × (1 − 1 / geomean(R_i))` — геометрический индикатор по файлам; он **не равен** фактически высвобождённой доле объёма;
- `Encode/Decode MiB/s = 55 MiB / sum(seconds)` соответствующей операции;
- `SAEI V10 = original_bytes / (archive_bytes + 10 MiB/s × (encode_seconds + decode_seconds))` — условная интегральная метрика размера и временного штрафа, **не измерение электричества, стоимости CPU или ROI**.

**Границы применения к ЦОД:** коэффициент `K_ЦОД` и пересчёт TiB отражают **только потенциальное сокращение сохраняемого payload** в модели одинакового состава данных. Они **не подтверждают** экономию денег, электричества, охлаждения, PUE или количества стоек. Для чистого эффекта необходимо отдельно измерять storage €/TiB-month, CPU/energy, RAM, сетевую нагрузку, резервирование, дедупликацию и частоту восстановления. WORLD — конфигурации общедоступных компрессоров, а не 40 независимых архитектур. SYNERGY-группа также содержит контрольный RAW STORE и адаптеры сторонних ZSTD/BZIP2/GZIP, обозначенные в именах и **не заявленные как собственные алгоритмы**.

### Полная таблица (81/81 SYNERGY и 40 WORLD)

| № | Архиватор / профиль | Статус | R, × | Encode, MiB/s | Decode, MiB/s | SAEI хран., % | Экономия байтов, % | K ЦОД (доля) | TiB/1 PiB | SAEI V10 |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | SYNERGY — RAW STORE (контроль) | PASS 11/11 | 1.000 | 328248.47 | 133075.89 | 0.00 | 0.00 | 0.0000 | 0.0 | 1.000 |
| 2 | SYNERGY — SABF-X ULTIMATE | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 3 | SYNERGY — SABF-X FAST | PARTIAL 1/11 | — | — | — | — | — | — | — | — |
| 4 | SYNERGY — SABF-X NEURAL SELECTOR | PARTIAL 1/11 | — | — | — | — | — | — | — | — |
| 5 | SYNERGY — EGD-256 MAX | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 6 | SYNERGY — EGD-256 RECURSIVE GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 7 | SYNERGY — EGD-256 BIP39 GRAPH | PARTIAL 1/11 | — | — | — | — | — | — | — | — |
| 8 | SYNERGY — HACE-X CASCADE | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 9 | SYNERGY — TSC-X TURBOSPATIAL | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 10 | SYNERGY — AMCE-100X | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 11 | SYNERGY — BLOCK_FAST X | PARTIAL 4/11 | — | — | — | — | — | — | — | — |
| 12 | SYNERGY — GRAAL-AIS STORAGE | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 13 | SYNERGY — RSX RECURSIVE SPATIAL | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 14 | SYNERGY — FAS-256 ATOM STORE | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 15 | SYNERGY — SABF-X + ZSTD | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 16 | SYNERGY — SABF-X + LZMA9 | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 17 | SYNERGY — SABF-X + ZSTD + LZMA9 | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 18 | SYNERGY — EGD256 + ZSTD | PARTIAL 1/11 | — | — | — | — | — | — | — | — |
| 19 | SYNERGY — EGD256 + BROTLI | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 20 | SYNERGY — EGD256 + LZMA | PARTIAL 2/11 | — | — | — | — | — | — | — | — |
| 21 | SYNERGY — ARITHMETIC CODING | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 22 | SYNERGY — ADAPTIVE ARITHMETIC CODING | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 23 | SYNERGY — INTEGER RANGE CODING | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 24 | SYNERGY — rANS CODING | PARTIAL 2/11 | — | — | — | — | — | — | — | — |
| 25 | SYNERGY — rANS + DICTIONARY | PARTIAL 3/11 | — | — | — | — | — | — | — | — |
| 26 | SYNERGY — ADAPTIVE HUFFMAN | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 27 | SYNERGY — CANONICAL HUFFMAN | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 28 | SYNERGY — BIP39 + ARITHMETIC | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 29 | SYNERGY — GRAPH DELTA ENCODING | PARTIAL 3/11 | — | — | — | — | — | — | — | — |
| 30 | SYNERGY — HYBRID AI COMPRESSION ENGINE | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 31 | SYNERGY — ZSTD-22 | PARTIAL 1/11 | — | — | — | — | — | — | — | — |
| 32 | SYNERGY — ZSTD-3 (сторонний кодек) | PASS 11/11 | 2.302 | 29.44 | 107.43 | 70.60 | 56.57 | 0.5657 | 579.2 | 1.153 |
| 33 | SYNERGY — LZMA9 | PARTIAL 1/11 | — | — | — | — | — | — | — | — |
| 34 | SYNERGY — BROTLI-11 | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 35 | SYNERGY — BZIP2-9 (сторонний кодек) | PASS 11/11 | 2.420 | 7.68 | 15.82 | 72.92 | 58.67 | 0.5867 | 600.8 | 0.426 |
| 36 | SYNERGY — GZIP-9 (сторонний кодек) | PASS 11/11 | 1.806 | 6.14 | 88.54 | 59.52 | 44.62 | 0.4462 | 457.0 | 0.436 |
| 37 | SYNERGY — HACE-X CASCADE GRAPH-AI | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 38 | SYNERGY — EGD-256 MAX GRAPH-AI | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 39 | SYNERGY — TSC-X TURBOSPATIAL GRAPH-AI | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 40 | SYNERGY — AMCE-100X GRAPH-AI | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 41 | SYNERGY — SABF-X ULTIMATE GRAPH-AI | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 42 | SYNERGY — BLOCK_FAST X GRAPH-AI | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 43 | SYNERGY — GRAAL-AIS STORAGE GRAPH-AI | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 44 | SYNERGY — RSX RECURSIVE SPATIAL GRAPH-AI | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 45 | SYNERGY — FAS-256 ATOM STORE GRAPH-AI | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 46 | SYNERGY — GRAAL-IGC V5.2 | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 47 | SYNERGY — MICA-39 GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 48 | SYNERGY — UECB-39X GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 49 | SYNERGY — DMB-39X GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 50 | SYNERGY — ECBC-39 GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 51 | SYNERGY — PECB-39X GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 52 | SYNERGY — SECB-39X GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 53 | SYNERGY — BAPM-X GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 54 | SYNERGY — PBM-39X GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 55 | SYNERGY — BPD-39X GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 56 | SYNERGY — CDC-RX GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 57 | SYNERGY — ODC-XC GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 58 | SYNERGY — ODC-XP GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 59 | SYNERGY — DDR-X GRAPH | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 60 | SYNERGY — UMC-256 FAST | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 61 | SYNERGY — UMC-256 BALANCED | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 62 | SYNERGY — UMC-256 MAX | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 63 | SYNERGY — SABF-X TIER1 SPEED | PASS 11/11 | 2.299 | 82.62 | 258.48 | 70.72 | 56.51 | 0.5651 | 578.7 | 1.682 |
| 64 | SYNERGY — SABF-X TIER1 BALANCED | PASS 11/11 | 2.276 | 67.50 | 322.58 | 69.81 | 56.07 | 0.5607 | 574.2 | 1.617 |
| 65 | SYNERGY — GRAAL-AIS TIER1 | PASS 11/11 | 2.297 | 101.90 | 253.85 | 70.70 | 56.47 | 0.5647 | 578.2 | 1.746 |
| 66 | SYNERGY — TSC-X TIER1 SPATIAL | PASS 11/11 | 2.389 | 8.70 | 45.75 | 71.98 | 58.14 | 0.5814 | 595.3 | 0.560 |
| 67 | SYNERGY — PBM-39X TIER1 | PASS 11/11 | 2.299 | 51.20 | 195.12 | 70.72 | 56.51 | 0.5651 | 578.7 | 1.467 |
| 68 | SYNERGY — NEXUS-UMC TIER1 | PASS 11/11 | 2.324 | 47.90 | 343.92 | 71.03 | 56.97 | 0.5697 | 583.4 | 1.497 |
| 69 | SYNERGY — GRAAL-IGC TIER1 MAX | PASS 11/11 | 2.416 | 5.31 | 103.99 | 72.46 | 58.61 | 0.5861 | 600.1 | 0.418 |
| 70 | SYNERGY — GABRIEL-HORN TIER1 MAX | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 71 | SYNERGY — OMNIA TIER1 V2 SPEED | PASS 11/11 | 2.359 | 7.50 | 33.52 | 71.89 | 57.62 | 0.5762 | 590.0 | 0.486 |
| 72 | SYNERGY — OMNIA TIER1 V2 BALANCED | PARTIAL 2/11 | — | — | — | — | — | — | — | — |
| 73 | SYNERGY — OMNIA TIER1 V2 MAX | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 74 | SYNERGY — GABRIEL-HORN TIER1 SPEED | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 75 | SYNERGY — GABRIEL-HORN TIER1 BALANCED | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 76 | SYNERGY — GABRIEL-HORN TIER1 RANDOM-ACCESS | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 77 | SYNERGY — MATH PORTFOLIO V3 BALANCED | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 78 | SYNERGY — MATH PORTFOLIO V3 MAX | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 79 | SYNERGY — OMNIA-MATH V3 SPEED | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 80 | SYNERGY — OMNIA-MATH V3 BALANCED | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 81 | SYNERGY — OMNIA-MATH V3 MAX | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 82 | WORLD — zlib-1 | PASS 11/11 | 1.759 | 24.49 | 165.27 | 55.47 | 43.14 | 0.4314 | 441.8 | 0.964 |
| 83 | WORLD — zlib-3 | PASS 11/11 | 1.783 | 22.81 | 169.58 | 56.90 | 43.91 | 0.4391 | 449.7 | 0.945 |
| 84 | WORLD — zlib-6 | PASS 11/11 | 1.798 | 12.50 | 108.78 | 58.90 | 44.39 | 0.4439 | 454.6 | 0.691 |
| 85 | WORLD — zlib-9 | PASS 11/11 | 1.806 | 7.17 | 127.98 | 59.52 | 44.63 | 0.4463 | 457.0 | 0.493 |
| 86 | WORLD — gzip-1 | PASS 11/11 | 1.759 | 26.57 | 107.55 | 55.47 | 43.14 | 0.4314 | 441.8 | 0.963 |
| 87 | WORLD — gzip-6 | PASS 11/11 | 1.798 | 19.08 | 185.15 | 58.90 | 44.39 | 0.4439 | 454.6 | 0.882 |
| 88 | WORLD — gzip-9 | PASS 11/11 | 1.806 | 9.43 | 157.41 | 59.52 | 44.63 | 0.4463 | 457.0 | 0.596 |
| 89 | WORLD — bzip2-1 | PARTIAL 9/11 | — | — | — | — | — | — | — | — |
| 90 | WORLD — bzip2-3 | PARTIAL 8/11 | — | — | — | — | — | — | — | — |
| 91 | WORLD — bzip2-6 | PASS 11/11 | 2.367 | 5.27 | 11.84 | 72.03 | 57.76 | 0.5776 | 591.4 | 0.316 |
| 92 | WORLD — bzip2-9 | PARTIAL 8/11 | — | — | — | — | — | — | — | — |
| 93 | WORLD — xz-LZMA2-0 | PASS 11/11 | 2.437 | 4.09 | 43.23 | 71.71 | 58.96 | 0.5896 | 603.7 | 0.324 |
| 94 | WORLD — xz-LZMA2-1 | PARTIAL 9/11 | — | — | — | — | — | — | — | — |
| 95 | WORLD — xz-LZMA2-2 | PARTIAL 8/11 | — | — | — | — | — | — | — | — |
| 96 | WORLD — xz-LZMA2-3 | PARTIAL 8/11 | — | — | — | — | — | — | — | — |
| 97 | WORLD — xz-LZMA2-4 | PARTIAL 3/11 | — | — | — | — | — | — | — | — |
| 98 | WORLD — xz-LZMA2-5 | PARTIAL 3/11 | — | — | — | — | — | — | — | — |
| 99 | WORLD — xz-LZMA2-6 | PARTIAL 2/11 | — | — | — | — | — | — | — | — |
| 100 | WORLD — xz-LZMA2-7 | PARTIAL 2/11 | — | — | — | — | — | — | — | — |
| 101 | WORLD — xz-LZMA2-8 | PARTIAL 3/11 | — | — | — | — | — | — | — | — |
| 102 | WORLD — xz-LZMA2-9 | PARTIAL 2/11 | — | — | — | — | — | — | — | — |
| 103 | WORLD — zstd-1 | PASS 11/11 | 2.299 | 167.62 | 613.84 | 70.73 | 56.51 | 0.5651 | 578.7 | 1.958 |
| 104 | WORLD — zstd-3 | PASS 11/11 | 2.303 | 62.15 | 143.05 | 70.61 | 56.57 | 0.5657 | 579.3 | 1.504 |
| 105 | WORLD — zstd-5 | PASS 11/11 | 2.343 | 37.95 | 357.29 | 71.30 | 57.31 | 0.5731 | 586.9 | 1.392 |
| 106 | WORLD — zstd-9 | PASS 11/11 | 2.408 | 47.31 | 817.07 | 72.53 | 58.48 | 0.5848 | 598.8 | 1.565 |
| 107 | WORLD — zstd-12 | PASS 11/11 | 2.425 | 13.36 | 418.53 | 72.88 | 58.77 | 0.5877 | 601.8 | 0.844 |
| 108 | WORLD — zstd-15 | PARTIAL 8/11 | — | — | — | — | — | — | — | — |
| 109 | WORLD — zstd-19 | PARTIAL 1/11 | — | — | — | — | — | — | — | — |
| 110 | WORLD — brotli-0 | PASS 11/11 | 2.085 | 148.67 | 144.65 | 64.08 | 52.03 | 0.5203 | 532.8 | 1.623 |
| 111 | WORLD — brotli-3 | PASS 11/11 | 2.297 | 96.39 | 270.98 | 70.38 | 56.47 | 0.5647 | 578.2 | 1.736 |
| 112 | WORLD — brotli-5 | PASS 11/11 | 2.418 | 26.70 | 252.72 | 72.86 | 58.64 | 0.5864 | 600.5 | 1.208 |
| 113 | WORLD — brotli-7 | PASS 11/11 | 2.455 | 5.49 | 148.60 | 73.55 | 59.26 | 0.5926 | 606.9 | 0.436 |
| 114 | WORLD — brotli-9 | PARTIAL 6/11 | — | — | — | — | — | — | — | — |
| 115 | WORLD — brotli-11 | TIMEOUT 0/11 | — | — | — | — | — | — | — | — |
| 116 | WORLD — lz4-0 | PASS 11/11 | 1.576 | 501.26 | 977.69 | 46.29 | 36.54 | 0.3654 | 374.2 | 1.504 |
| 117 | WORLD — lz4-3 | PASS 11/11 | 1.675 | 29.83 | 664.83 | 52.50 | 40.29 | 0.4029 | 412.6 | 1.056 |
| 118 | WORLD — lz4-9 | PASS 11/11 | 1.690 | 25.26 | 1135.88 | 53.48 | 40.84 | 0.4084 | 418.2 | 1.004 |
| 119 | WORLD — lz4-12 | PASS 11/11 | 1.694 | 7.72 | 939.76 | 53.74 | 40.96 | 0.4096 | 419.4 | 0.527 |
| 120 | WORLD — blosc2-LZ4 | PASS 11/11 | 1.542 | 332.39 | 1011.12 | 44.45 | 35.16 | 0.3516 | 360.0 | 1.453 |
| 121 | WORLD — blosc2-ZSTD | PASS 11/11 | 2.144 | 65.24 | 994.60 | 66.21 | 53.36 | 0.5336 | 546.4 | 1.588 |

*Обозначение «—» значит, что профиль не прошёл все 11 файлов; оценки для частично обработанного подмножества сознательно не переносятся на общий корпус. «TiB/1 PiB» — арифметическая экстраполяция из фактически полученного процента сжатых байтов, **не результат испытания настоящего PiB или промышленного ЦОД**.*

## Применимость в ЕАЭС и мире

Оценки ниже — аналитическая приоритизация пилотов, а не статистика спроса, сертификация или контракты. Шкала 1–5 означает относительный приоритет проверки: 5 — начать исследование раньше; 1 — низкий приоритет. Оценка учитывает возможную структурированность данных и реализуемость пилота, но не подтверждает конкретного заказчика.

### Таблица 10. Приоритет пилотов в ЕАЭС

| Рынок | Приоритет, 1–5 | Данные-кандидаты | Потенциальная ценность | Главный барьер |
|---|---:|---|---|---|
| Казахстан | **5/5** | Добыча и энергетика, геоданные, логистика, агротелеметрия, архивы ЦОД | Меньше передачи между площадками, архив сенсорных данных и версий | Нужны реальные данные и измерение CPU/storage TCO |
| Россия | **4/5** | Enterprise backup, промышленная телеметрия, версии ПО/CAD, локальные AI-артефакты | Снижение storage/replication TCO | Конкуренция, безопасность, интеграция, лицензии |
| Беларусь | **4/5** | Машиностроение, CAD/CAE, производственные журналы и бинарные версии | Эффективнее хранение версий и повторяющихся объектов | Совместимость с корпоративным ПО |
| Армения | **3/5** | R&D, исходный код, ML-наборы, исследовательские модели | SDK для разработчиков и научных групп | Абсолютная экономия может быть меньше из-за объёма пилота |
| Кыргызстан | **3/5** | Edge/телеком, удалённые архивы, агроданные и документы | Сокращение передачи по ограниченным каналам | Нужно доказать, что CPU/decode не создают новых ограничений |

### Таблица 11. Глобальные сегменты

| Сегмент | Приоритет, 1–5 | Первый продукт | Критерий успеха |
|---|---:|---|---|
| Backup / disaster recovery | **5/5** | SDK/sidecar для архивации и восстановления | Снижение полной TCO при неизменной надёжности restore |
| Логи и observability | **5/5** | Потоковый codec selector | Снижение retention и передачи без нарушения SLA |
| Версионные бинарные артефакты | **5/5** | Content-addressed version store | Меньше инкрементальный объём и быстрое восстановление версии |
| Научные массивы/временные ряды | **4/5** | Domain-specific reversible codec | Выигрыш на репрезентативных данных |
| AI checkpoints/model registry | **3/5 lossless** | Архивирование и delta storage | Снижение размера без изменения модели; lossy требует отдельного quality gate |
| CDN / edge delivery | **3/5** | Низколатентный декодер/SDK | Меньше сетевых байтов при соблюдении p95/p99 latency |
| Уже сжатые/зашифрованные данные | **1/5** | RAW/fallback | Не тратить CPU и не ухудшать размер |

## Коммерциализация и экспорт технологий

### Таблица 12. Готовность коммерческих форматов

| Продукт | Покупатель | Что продаётся | Текущая готовность | Обязательный gate |
|---|---|---|---|---|
| Платный compression audit | Enterprise storage, интеграторы, владельцы больших архивов | Отчёт на данных клиента: ratio, CPU, RAM, restore, TCO | **Наиболее реалистичный первый шаг** | NDA/права на данные, повторяемый harness, независимый baseline |
| SDK/CLI | Разработчики, R&D, industrial IoT | Интеграция, лицензия, поддержка | Ранняя инженерная стадия | Стабильный API, fuzzing, cross-platform builds, документация |
| Enterprise/on-prem engine | ЦОД, backup-операторы | Развёртывание внутри периметра | Промышленными пилотами не подтверждён | SLA, отказоустойчивость, безопасность, нагрузочные тесты |
| Version-aware backup/store | Backup-поставщики, dev platforms, model registries | Хранение блоков/дельт и версий | Гипотеза с понятной задачей | Сравнение с dedup + Zstd/LZMA и тест полного lifecycle |
| OEM/embedded licence | Вендоры инфраструктурного ПО | Встраиваемая библиотека/формат | Среднесрочный путь | ABI/API, лицензии зависимостей, security review |
| Лицензирование IP/know-how | Производители storage/compute | Право использования конкретных IP-объектов | Зависит от IP-аудита | Prior art, цепочка прав, лицензии компонентов |

### Таблица 13. Экспортная стратегия

| Направление | Формат экспорта | Потенциальное преимущество | Основные препятствия | Этап |
|---|---|---|---|---|
| ЕАЭС | SDK, CLI, on-prem licence | Цифровая поставка и локальное развёртывание | Договоры, локальные требования, поддержка и лицензии | Пилоты с интеграторами |
| Глобальный рынок | Developer SDK, enterprise engine, hosted evaluation | Универсальная задача хранения и передачи данных | Конкуренция, доказательство преимущества, документация и SLA | После независимого benchmark |
| OEM | Embedded library/codec | Вендор может встроить компонент в свой стек | ABI/API, безопасность формата, стабильность декодера | Среднесрочно |
| Специализированные преобразования | IP/know-how licence, если юридически обосновано | Узкий метод может иметь нишевую ценность | Новизна, freedom-to-operate, права на код | Только после IP-аудита |
| Сервис benchmark/оптимизации | Платная диагностика | Можно продавать измерение эффекта до замены стека | Нужны воспроизводимый ROI и доверие | Наиболее доступный коммерческий вход |

### Таблица 14. Сводная оценка проекта

| Измерение | Оценка | Основание |
|---|---|---|
| Lossless-ядро | Предварительно подтверждено | Есть точные round-trip проверки; нужны fuzzing и внешний повтор |
| Преимущество по размеру | Частично подтверждено | Сильные значения на фиксированных малых корпусах; общего промышленного корпуса нет |
| Преимущество по скорости | Ограниченные данные | Профили существенно различаются; некоторые MAX-режимы медленные |
| Экономия ЦОД | Не подтверждена в эксплуатации | Нет опубликованного завершённого real-DC результата с энергетическими измерениями |
| Первый платный проект | Средняя готовность при узком scope | Аудит/пилот легче продать, чем замену production backup stack |
| Массовая лицензия | Ранняя стадия | Нужны стабильный API/формат, совместимость, безопасность и поддержка |
| Экспорт технологий | Ранняя стадия с потенциалом после валидации | Нужны IP-, лицензионный и compliance-аудиты |
| Научная/патентная новизна | Не установлена | Требуются prior-art search и юридическая экспертиза |

**Коммерческое позиционирование:** продавать не обещание «сжимает любой ЦОД в 30 раз», а воспроизводимое измерение на конкретном корпусе и затем лицензию на профиль, который выигрывает у действующего baseline после учёта CPU, энергии, хранения, передачи и восстановления.


## Где технология может создавать ценность

### Объектное хранение и резервное копирование

Уменьшение объёма архивных объектов может сокращать расходы на ёмкость, репликацию и передачу. Экономический эффект определяется не только коэффициентом сжатия, но и CPU overhead, частотой восстановления, политикой хранения и совместимостью с существующими процессами.

### Базы данных, журналы и телеметрия

Структурированные события, временные ряды и повторяющиеся записи могут содержать закономерности, которые выгодно использовать на уровне представления данных. Для таких сценариев важны пропускная способность, обработка потоков, диапазонное чтение и задержка восстановления.

### Версии файлов и вычислительные артефакты

Сходство между версиями бинарных объектов, моделями, сборками и наборами данных может использоваться для хранения различий и повторно встречающихся блоков. Здесь следует отдельно измерять стоимость первичной архивации, инкрементального обновления, восстановления полной версии и выборочного восстановления.

### AI/ML-инфраструктура

Модели, checkpoints и массивы параметров имеют различные структуры и режимы доступа. Специализированные преобразования могут быть полезны для определённых представлений, но результаты необходимо проверять на реальных форматах и рабочих нагрузках. Lossless-компрессию нельзя смешивать с квантованием или иными lossy-методами: это разные продуктовые обещания и разные критерии качества.

### Edge, промышленность и сети

При ограниченной пропускной способности или ресурсах устройства компрессия может снижать стоимость передачи и хранения. Практическая пригодность зависит от CPU/RAM, энергопотребления, задержки, устойчивости к повреждениям и доступности декодера на целевой платформе.

## Коммерческая модель

Платформа может развиваться как набор продуктов, а не как один универсальный архиватор:

- **SDK и API** для интеграции в приложения;
- **On-premise engine** для корпоративных сред;
- **OEM-лицензирование** для производителей ПО и систем хранения;
- **Storage optimization pilot** с измерением экономического эффекта на данных заказчика;
- **Специализированные профили** для логов, версий, структурированных бинарных объектов и архивного хранения;
- **Enterprise support**: внедрение, сопровождение, аудит совместимости и SLA.

Возможные модели оплаты — лицензия на развёртывание, годовая поддержка, оплата по объёму обработанных данных или коммерческое OEM-соглашение. Конкретная модель должна соответствовать фактической зрелости продукта, стоимости поддержки и требованиям клиента.

## Как измеряется ROI

Коммерческий пилот должен сравнивать SHTENCO с действующей системой заказчика на одном и том же корпусе и при одинаковых требованиях к восстановлению.

Основные показатели:

- общий объём исходных и архивных данных;
- фактическая экономия дискового пространства;
- скорость кодирования и декодирования;
- CPU time, пиковая RAM и энергопотребление;
- время полного и выборочного восстановления;
- стоимость репликации и передачи;
- совместимость с retention, backup и disaster-recovery процессами;
- частота ошибок, целостность и воспроизводимость.

Упрощённая модель:

```text
Net benefit =
  storage savings
  + replication and transfer savings
  - incremental CPU and energy cost
  - deployment and migration cost
  - support and operational overhead
```

Синтетические коэффициенты не следует напрямую превращать в прогноз выручки или обещание экономии. Экономический результат определяется на данных и инфраструктуре конкретного клиента.

## Техническая структура репозитория

Ключевые исходные материалы расположены в `compression_lab/`. В зависимости от доступности в текущей ветке, изучение следует начинать с:

- [Tier-1 compression engines](compression_lab/shtenco_tier1_engines.py)
- [Tier-1 V2](compression_lab/shtenco_tier1_v2.py)
- [Gabriel Horn engine](compression_lab/gabriel_horn_engine.py)
- [Unified Tier-1 benchmark runner](compression_lab/benchmark_unified_tier1.py)

Реализации, интерфейсы и возможности следует проверять по исходному коду конкретного файла. Наличие имени алгоритма в реестре не означает, что каждый профиль использует один и тот же entropy backend или реализует одинаковый набор возможностей.

## План технологической валидации

1. **Воспроизводимость:** единая команда запуска, зафиксированные зависимости, контрольные суммы входов и исходников.
2. **Реальные корпуса:** документы, исходный код, логи, базы данных, временные ряды, модели и смешанные архивы.
3. **Сильные базовые линии:** сопоставление с актуальными версиями широко используемых компрессоров при корректно выбранных настройках.
4. **Полная стоимость:** размер контейнера, модели, индексы, RAM, CPU time, throughput и восстановление.
5. **Внешнее воспроизведение:** независимый запуск без участия автора и публикация сырых наблюдений.
6. **Прикладные пилоты:** тестирование на репрезентативных данных потенциальных заказчиков с согласованными критериями успеха.
7. **Продуктовая готовность:** стабильный формат, документация, совместимость платформ, fuzzing, обработка повреждённых архивов и политика версий.

## Для инвесторов и технологических партнёров

SHTENCO предлагает портфель компрессионных технологий с несколькими возможными направлениями коммерциализации: собственные архивные форматы, специализированные обратимые преобразования, энтропийное кодирование и оптимизация хранения структурированных данных.

Главный предмет технической проверки — не количество названий алгоритмов и не один агрегированный коэффициент. Это воспроизводимая способность конкретных конвейеров уменьшать полную стоимость хранения или передачи при сохранении точности данных и приемлемой стоимости восстановления.

Мы заинтересованы в предметном обсуждении лицензирования, независимой технической оценке, совместной разработке и пилотах с операторами хранения, разработчиками баз данных, инфраструктурными компаниями и производителями корпоративного ПО.

## Статус доказательств

- **Текущий единый бенчмарк:** все 81 профиля SYNERGY включены в реестр; полный PASS 11/11 у 12 из 81, у WORLD — 24 из 40. Восстановление в успешных испытаниях проверено байт-в-байт и SHA-256.
- **Сравнительная эффективность:** должна интерпретироваться в контексте конкретного корпуса, протокола и аппаратной среды.
- **Универсальное превосходство:** не заявляется без независимого подтверждения на репрезентативных внешних данных.
- **Экономический эффект:** подтверждается только измерениями на нагрузке заказчика.
- **Научная новизна и патентоспособность:** требуют отдельного анализа prior art и юридической экспертизы.

**SHTENCO SYNERGY AI COMPRESS — исследовательская и инженерная платформа, нацеленная на следующий уровень lossless-компрессии: моделировать структуру данных, выбирать подходящее представление и измерять результат на уровне полной стоимости хранения и восстановления.**

---

<p align="center"><strong>Technology licensing · Research collaboration · Enterprise pilots</strong></p>
