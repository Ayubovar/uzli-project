# UZLI Project Brief
**Uzbekistan Liquidity Index — Briefing Notes**
*Prepared for: Task 6 | Date: 4 July 2026*

---

## 1. Project Objective

The Uzbekistan Liquidity Index (UZLI) is a composite daily measure of market-wide liquidity on the Tashkent Stock Exchange (TSE / UZSE). The index is constructed from five independently computed metrics that capture different dimensions of liquidity — trading activity, market participation, turnover efficiency, price-impact cost, and bid-ask spread — each normalized and combined into a single score on a 0–100 scale.

The index was built to answer a specific empirical question: **how liquid is the Uzbek capital market, and how has that liquidity evolved from market inception (November 2016) through June 2026?** It serves as a baseline instrument for capital market development analysis in the context of Uzbekistan's ongoing financial sector reform programme.

No commercial or vendor data was used. All data was sourced directly from the UZSE's own public trade-results endpoint.

---

## 2. Dataset Summary

### 2a. Raw Data

| Parameter | Value |
|---|---|
| Source | UZSE public endpoint: `uzse.uz/test_history_trade.xlsx` |
| Coverage | 1 November 2016 – 23 June 2026 |
| Instrument universe | Equities only (`mkt_id=STK`); bonds, repo, and futures excluded |
| Unique tickers | 290 listed securities |
| Raw observation rows | 73,613 (ticker × trading day) |
| Scraping unit | One XLSX request per calendar day; individual trades aggregated to OHLCV per ticker |
| Missing data | None — scraper records only days with confirmed trades; 100% of rows have `traded=1` |
| Scraping errors | Zero errors across all backfill runs |

### 2b. Processed Datasets

| File | Rows | Description |
|---|---|---|
| `tse_clean.csv` | 73,613 | Cleaned OHLCV, zero volumes → NaN, deduped |
| `daily_metrics.csv` | 2,373 | Five raw metric scores, one row per trading day |
| `uzli_daily.csv` | 2,373 | Pre-normalization composite (weighted sum of raw scores) |
| `uzli_final.csv` | 2,373 | Min-Max normalized scores + final UZLI + liquidity label |

---

## 3. Methodology Summary

### 3a. Data Collection

The UZSE does not publish daily OHLC tables in machine-readable form. The scraper downloads individual trade-level Excel files from the exchange's internal history endpoint, one day at a time, then aggregates: open = first trade price, close = last trade price, high/low = max/min trade price, volume = sum of shares and UZS value, num_trades = count of transactions. A 1-second crawl delay is observed per the exchange's `robots.txt` specification.

### 3b. Metric Construction

Five metrics are computed from the cleaned daily data:

**1. Volume Score** (weight: 25%)
Daily total trading volume in UZS relative to its own 90-day rolling average. Clipped at [0, 3]. A score of 1.0 means today's volume equals the rolling average; >1 is above average.

**2. Breadth Score** (weight: 20%)
Number of tickers that traded on a given day divided by the all-time total of 290 listed tickers. Ranges from 0 to ~0.29. Measures the share of the market that is actively participating.

**3. Turnover Score** (weight: 25%)
For each ticker: daily volume in shares divided by a 30-day rolling average volume-based proxy for market capitalisation (`close × avg_volume_30d`). Cross-sectional mean taken across all tickers per day. Intended to capture how efficiently the float turns over relative to its size.

**4. Amihud Illiquidity Score** (weight: 20%)
For each ticker: `|daily_return| / volume_UZS`, then cross-sectional daily average, then transformed to `1 / (1 + amihud)` so that higher scores = more liquid. A high Amihud score indicates low price impact per unit of trading volume.

**5. Spread Score** (weight: 10%)
Market-wide average of a simplified single-day Corwin-Schultz (2012) spread estimator based on high-low ratio: `2·tanh(√β/2)` where `β = ln(high/low)²`. Transformed to `1 - spread` so that higher scores = tighter spreads = more liquid.

### 3c. Normalization and Composite Construction

**Stage 1 (intermediate):** Raw weighted composite `uzli_daily` = sum of `metric × weight` across all five metrics.

**Stage 2 (final):** Each raw metric is Min-Max normalized over the full historical sample to [0, 100]:
`norm = 100 × (x − min) / (max − min)`

Final UZLI score = weighted sum of the five normalized metrics, bounded [0, 100].

**Weights:** Volume 25%, Breadth 20%, Turnover 25%, Amihud 20%, Spread 10%. Weights are fixed and validated to sum to exactly 1.0.

**Liquidity Labels:** Low (<40), Moderate (40–69), High (≥70).

---

## 4. Key Statistics

### Index-Level (uzli_final.csv, n=2,373 trading days)

| Statistic | Value |
|---|---|
| Mean UZLI | 41.20 |
| Median UZLI | 40.06 |
| Standard deviation | 8.35 |
| 25th percentile | 35.00 |
| 75th percentile | 45.04 |
| Minimum | 16.36 (1 Nov 2019) |
| Maximum | 76.41 (20 Dec 2023) |

### Label Distribution

| Label | Days | Share |
|---|---|---|
| Low Liquidity (<40) | 1,179 | 49.7% |
| Moderate Liquidity (40–69) | 1,186 | 49.9% |
| High Liquidity (≥70) | 8 | 0.3% |

### Annual Averages

| Year | Mean | Min | Max |
|---|---|---|---|
| 2016 | 36.11 | 30.42 | 56.71 |
| 2017 | 35.30 | 29.96 | 57.48 |
| 2018 | 38.25 | 20.56 | 64.14 |
| 2019 | 38.57 | 16.36 | 60.83 |
| 2020 | 38.23 | 26.76 | 60.94 |
| 2021 | 39.58 | 29.51 | 63.55 |
| 2022 | 41.20 | 31.87 | 65.74 |
| 2023 | 46.07 | 38.39 | 76.41 |
| 2024 | 45.76 | 31.04 | 71.20 |
| 2025 | 45.24 | 39.60 | 71.29 |
| 2026 | 48.55 | 37.07 | 70.54 |

### Raw Metric Ranges (before normalization)

| Metric | Mean | Std | Min | Max | Notes |
|---|---|---|---|---|---|
| volume_score | 0.47 | 0.85 | 0.00 | 3.00 | Clipped at 3.0 |
| breadth_score | 0.107 | 0.072 | 0.003 | 0.286 | Max = 83/290 tickers active |
| turnover_score | 0.587 | 2.07 | 0.000 | 45.85 | Severely right-skewed |
| amihud_score | 1.000 | 0.0003 | 0.990 | 1.000 | Essentially constant |
| spread_score | 0.965 | 0.054 | −0.231 | 1.000 | 2 days negative |

---

## 5. Important Findings Visible in the Data

**Finding 1 — The market is chronically illiquid by any standard definition.**
Only 8 of 2,373 trading days (0.3%) reached "High Liquidity" status. The median score of 40.06 places the market perpetually on the Low/Moderate boundary. This is not a measurement artefact — the breadth score confirms that fewer than 10% of listed securities trade on a typical day (median ~9 of 290 tickers active).

**Finding 2 — A structural break is visible around 2022–2023.**
Annual mean UZLI rises from a flat 35–41 range (2016–2022) to a sustained 45–48 range (2023–2026). The highest single-day score ever recorded (76.41, 20 December 2023) falls within this new regime. The five highest UZLI days all occur in 2023 or later. This shift warrants explanation — likely connected to capital market liberalisation measures introduced in that period, but the data alone cannot confirm causation.

**Finding 3 — Market breadth is the tightest structural constraint on liquidity.**
Even on the highest-UZLI days, breadth_score peaks at 0.286 (83 of 290 tickers trading). On median days only ~26 tickers are active. This means liquidity — whatever its level — is concentrated in a thin subset of the listed universe. The remaining ~200 tickers are essentially dormant on any given day.

**Finding 4 — The top-5 lowest UZLI days cluster around two identifiable events.**
The lowest day (16.36, 1 November 2019) and third-lowest (26 November 2019) point to a severe temporary illiquidity episode in Q4 2019. The fourth and fifth lowest days (21 April 2020 and 27 March 2020) coincide with the early COVID-19 shock. The 2018 low (20 March 2018) likely reflects an earlier market disruption episode.

**Finding 5 — Liquidity shows strong positive trend from 2022 onwards but remains fragile.**
Within the improved 2023–2026 period, the minimum score is still as low as 31.04 (September 2024), and 2026 year-to-date already has a minimum of 37.07. High-liquidity days remain exceptional rather than routine, suggesting the structural improvement is real but shallow.

**Finding 6 — 2026 YTD shows the highest annual average (48.55) of the entire sample.**
With only partial-year data through June 2026, the mean already exceeds all full-year means. Whether this represents a continued trend or a seasonal effect cannot be determined without a full year.

---

## 6. Known Limitations

**L1 — Turnover score is unbounded and right-skewed (critical).**
The market-cap proxy (`close × 30-day avg volume in shares`) is not a true market capitalisation. It conflates share price with float size, producing a price-level bias that favours cheap, high-share-count securities. On 292 of 2,373 days (12.3%), the turnover score exceeds 1.0, reaching as high as 45.85 — far outside its intended [0, 1] range. Although Min-Max normalization at the final stage contains the damage, the turnover component introduces significant noise into the raw composite and distorts the pre-normalization index values.

**L2 — Amihud metric carries near-zero information content (significant).**
The Amihud score has a standard deviation of 0.0003 across 2,373 days (mean 1.000, range 0.990–1.000). The UZS magnitudes of trading volume are so large relative to the daily returns that the denominator effectively dominates, producing a near-constant score. Despite a 20% weight in the composite, this component contributes almost no discriminating signal. Its influence on the final UZLI is negligible in practice.

**L3 — Breadth score uses a look-ahead-biased denominator (moderate).**
The denominator of 290 represents the all-time unique ticker count as of June 2026. This is applied retroactively to 2016–2017 data when fewer securities were listed. The 2016–2017 breadth scores are therefore understated relative to the market's actual universe size at that time. The magnitude of this bias is unknown without a time-varying listed-company count.

**L4 — Spread estimator is a significant simplification (moderate).**
The Corwin-Schultz estimator requires two consecutive days of high-low data to produce a statistically valid spread estimate. This implementation applies the formula to single-day data, which produces two negative observations and inflates spread estimates on high-volatility days. The true effective spread for TSE securities is unknown.

**L5 — Holiday calendar is incomplete (minor).**
The scraper excludes only five fixed-date public holidays per year. Uzbekistan observes several moveable religious holidays (Eid al-Fitr, Eid al-Adha) whose dates vary annually. These are not excluded, meaning a small number of days with zero trading activity may have been improperly treated as regular non-trading days rather than holidays. No scraping errors occurred, suggesting these days simply returned empty trade files and were correctly dropped.

**L6 — Min-Max normalization is sensitive to outliers.**
The maximum and minimum values used for normalization are drawn from the full sample. Extreme outliers — particularly the turnover_score spike of 45.85 — anchor the normalization scale and compress all other observations. The turnover spike day (if it is an anomaly) becomes the reference maximum for all subsequent scores.

**L7 — Equities only; bonds and money market excluded.**
The full picture of TSE market liquidity would include government bonds, corporate bonds, and repo activity, all of which are excluded from the current index (`mkt_id=STK` filter).

---

## 7. Information Gaps Requiring Additional Research

**G1 — Policy and regulatory event timeline.**
The structural break in 2022–2023 is clearly visible in the data but cannot be explained without an external timeline of capital market reforms — changes to listing requirements, foreign investor access rules, trading fee structures, margin trading introduction, or index inclusion events. A chronology of regulatory actions from the Capital Markets Development Agency (CMDA) or the Ministry of Finance is needed to attribute causation.

**G2 — Time-varying listed company universe.**
The total number of listed securities on the TSE has changed over time. Without a year-by-year count of listed equities, the breadth score's look-ahead bias cannot be corrected. UZSE's annual reports or the CMDA's statistical bulletins likely contain this information.

**G3 — True market capitalisation data.**
The turnover score's core deficiency is the absence of real market capitalisation data. Share counts outstanding, not trading volume, is the correct denominator for turnover ratio. This data may be available from the UZSE or from company annual reports (mandatory filings for listed entities under Uzbek securities law).

**G4 — Identification of the November 2019 liquidity collapse.**
The two lowest UZLI days in the entire 9-year sample (1 November 2019 and 21 November 2019) represent an anomalous episode that is not explained by the data. Possible causes — a trading halt, a regulatory intervention, a macro shock, or a data artefact — cannot be determined from trade data alone. Contemporaneous news or exchange notices are needed.

**G5 — Benchmark comparison.**
There is no external benchmark against which UZLI can be validated. Comparable emerging frontier market indices (e.g., Kazakhstan's KASE, Georgia's GSE, or the MSCI Frontier Markets liquidity sub-indices) would allow calibration of whether a mean score of 41 represents the expected range for a market at Uzbekistan's stage of development, or whether it is anomalously low or high.

**G6 — Foreign investor participation data.**
A significant driver of liquidity improvement in frontier markets is the entry of foreign portfolio investors. Whether the 2023 structural break coincides with measurable foreign inflows — available from the Central Bank of Uzbekistan's balance of payments statistics — would substantially strengthen or weaken a reform-impact narrative.

**G7 — Intraday trading structure.**
The current methodology treats each trading day as a single session. The UZSE operates with discrete auction windows, not continuous trading. The meaning of "spread" in a non-continuous, order-driven market with few participants per stock is materially different from its meaning in a continuous dealer market. The true market microstructure requires documentation to interpret the spread score appropriately.

---

*All statistics computed directly from `uzli_final.csv` and `daily_metrics.csv` as at repository commit `a125f99`. No data has been modified for this brief.*
