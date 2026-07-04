# TSE Liquidity Index — Project Handoff

_Last updated: 2026-06-26_

## 1. Completed tasks

1. Modified `scripts/tse_scraper.py` to resume from the day after the latest date in the CSV, append instead of overwrite, and accept optional `--start-date`/`--end-date` overrides. Verified resume logic against the live CSV before running.
2. Ran forward backfill 2023-12-14 → 2026-06-23 (today). Completed with 0 errors.
3. Probed the UZSE xlsx endpoint for pre-2023 viability (2018–2022 sample dates): confirmed schema match and data availability.
4. Probed 2016–2018 specifically across multiple weekdays: found real trading activity starts appearing around **November 2016**; earlier dates return empty results due to market inactivity, not a scraper/endpoint problem.
5. Ran historical backfill **2016-11-01 → 2023-01-03**, appended after confirming no date overlap with the existing earliest row (2023-01-04). Completed with 0 errors.
6. Created `scripts/sort_raw_data.py` — sorts the raw CSV chronologically (date asc, ticker asc) without adding/removing/modifying any observation. Verified row count unchanged before/after. Checked for date gaps at the backfill join point; confirmed the only gap there (2023-01-02/03) reflects genuine non-trading days (re-verified live against the endpoint), not a scraping defect.
7. Created `scripts/clean_data.py` — parses dates, dedupes on (ticker, date), converts numeric columns, standardizes ticker/company name text, adds `traded` flag, replaces zero volumes with NaN, checks OHLC consistency (reports only, does not auto-fix). Ran successfully: 0 duplicates, 0 OHLC violations.
8. Created `scripts/compute_metrics.py` — computes 5 daily liquidity metrics (volume, breadth, turnover, Amihud, spread) exactly per spec, with NaN/inf-safe handling and a validation step that **reports** out-of-range values rather than silently clipping them. Ran successfully.
9. Reviewed all 5 metric formulas for assumptions/limitations before running (see §4) — flagged turnover's price-level bias and missing upper bound, breadth's look-ahead-biased denominator, Amihud's near-zero variance, and spread's unbounded-below behavior, all *before* execution.
10. Ran a read-only period comparison (2016–2018 vs 2019–2026) to test whether the turnover/spread issues are early-liquidity artifacts. **Conclusion: they are not** — see §4.
11. Created `scripts/build_liquidity_index.py` — loads `data/processed/daily_metrics.csv`, validates that weights sum to 1.0 (raises `ValueError` if not), computes the weighted composite UZLI, saves `data/processed/uzli_daily.csv` (2,373 rows), and saves two figures (`uzli_daily.png`, `uzli_distribution.png`). Ran successfully with 0 NaN rows.

No formulas or data have been modified since the issues were identified; current state reflects formulas exactly as originally specified.

## 2. Files created/modified

- `scripts/tse_scraper.py` — modified (resume/append logic, `--start-date`/`--end-date` args)
- `scripts/sort_raw_data.py` — new
- `scripts/clean_data.py` — new
- `scripts/compute_metrics.py` — new
- `data/raw/tse_raw_data.csv` — extended (backfilled) and sorted in place
- `data/raw/tse_raw_data.unsorted.bak.csv` — backup of the raw CSV taken immediately before sorting
- `data/processed/tse_clean.csv` — new (cleaned dataset)
- `data/processed/daily_metrics.csv` — new (5 daily liquidity metrics)
- `data/raw/scraper_errors.log` — never created; no scraping errors occurred across any backfill run
- `scripts/build_liquidity_index.py` — new (composite index builder)
- `data/processed/uzli_daily.csv` — new (composite UZLI, one row per trading day)
- `data/processed/uzli_daily.png` — new (time-series plot)
- `data/processed/uzli_distribution.png` — new (histogram of UZLI values)

## 3. Current datasets and row counts

| Dataset | Rows | Date range | Unique tickers |
|---|---|---|---|
| `data/raw/tse_raw_data.csv` | 73,613 | 2016-11-01 → 2026-06-23 | 290 |
| `data/processed/tse_clean.csv` | 73,613 (0 duplicates removed) | 2016-11-01 → 2026-06-23 | 290 |
| `data/processed/daily_metrics.csv` | 2,373 trading days | 2016-11-01 → 2026-06-23 | n/a (one row per day) |
| `data/processed/uzli_daily.csv` | 2,373 trading days | 2016-11-01 → 2026-06-23 | n/a (one row per day) |

Clean dataset: 100% `traded=1` (expected — the scraper only ever records days a ticker actually traded), 0 OHLC consistency violations.

## 4. Metrics results and methodological concerns

### Full-sample results (2,373 trading days, 0 missing values in any metric)

| Metric | Min | Max | Mean | Median |
|---|---|---|---|---|
| volume_score | 0.000001 | 3.000000 | 0.4665 | 0.0820 |
| breadth_score | 0.003448 | 0.286207 | 0.1070 | 0.0897 |
| turnover_score | ~0 | 45.8548 | 0.5873 | 0.0868 |
| amihud_score | 0.989605 | 1.000000 | 0.999976 | 1.000000 |
| spread_score | -0.230809 | 1.000000 | 0.9649 | 0.9759 |

### Validation warnings (values left unmodified)

- **turnover_score**: 292/2,373 days (12.3%) exceed the expected [0,1] range, up to 45.85. Root cause: `market_cap_proxy = close × 30-day avg volume_shares` is not a true market cap, creating a price-level bias (favors cheap, high-share-count tickers) and no formula-imposed upper bound.
- **spread_score**: 2/2,373 days are negative (min -0.23). Root cause: the single-day Corwin-Schultz simplification has `spread = 2·tanh(√beta/2)`, which can exceed 1.0 for extreme high/low ratios in a single day, pushing `spread_score = 1 - spread` negative.
- **breadth_score**: no range violation, but the denominator (290, the all-time unique-ticker count) is look-ahead-biased — it applies the eventual 2026 universe size to 2017 data, understating early breadth relative to the market's actual size at the time.
- **amihud_score**: no range violation, but the metric is nearly constant (mean 0.999976, std ≈ 0.0003) because `volume_uzs` magnitudes dwarf typical daily returns — it carries very little discriminating signal anywhere in the sample.

### Period comparison (2016–2018 vs 2019–2026) — read-only analysis, no data changed

| | 2016–2018 (n=526) | 2019–2026 (n=1,847) |
|---|---|---|
| turnover_score >1.0 violations | 10 (1.90%) | 282 (15.27%) |
| spread_score out-of-[0,1] violations | 1 (0.19%) | 1 (0.05%) |
| amihud_score std dev | 0.0000028 | 0.000333 |

**Conclusions reached:**
- Turnover and spread problems are **not** concentrated in the early low-liquidity years — turnover violations are actually 8x more frequent in 2019–2026, and spread violations are roughly proportional across both periods.
- Amihud is near-constant in **both** periods, slightly more so in 2016–2018, but the structural flatness exists throughout the full sample.
- Dropping 2016–2018 would **not** materially change these conclusions — it would slightly raise the turnover violation rate and leave Amihud's flatness and spread's rare negative values essentially unchanged.

## 5. Composite index results (UZLI)

Weights applied exactly as specified — no formulas modified.

| Stat | Value |
|---|---|
| Trading days | 2,373 |
| Mean | 0.5813 |
| Median | 0.4156 |
| Std dev | 0.5581 |
| Min | 0.1811 (2018-03-30) |
| Max | 11.7928 (2025-08-05) |

The high maximum (11.79 vs median 0.42) is driven by the unbound `turnover_score` on spike days — consistent with the known methodology concern documented in §4. No values were clipped or modified.

## 6. What remains to be done next

The baseline composite index is complete. Open methodological decisions — none have been acted on:

1. **Decide whether/how to bound turnover_score and spread_score.** No caps have been applied. Options: cap turnover_score (similar to volume_score's 3.0 cap), floor spread_score at 0, or revisit the underlying formulas (e.g., true two-day Corwin-Schultz, or a turnover proxy that doesn't conflate price level with float).
2. **Decide whether to address the breadth_score look-ahead bias**, e.g. by computing a time-varying "listed universe" denominator instead of the static all-time count of 290.
3. **Decide whether to rescale or replace the Amihud metric**, since it contributes almost no signal at its 20% weight (std ≈ 0.0003).
4. **Robustness evaluation and methodological improvements** — deferred until after baseline index was confirmed.
