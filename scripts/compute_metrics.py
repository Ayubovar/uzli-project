"""
Computes 5 daily liquidity metrics from data/processed/tse_clean.csv and
saves them to data/processed/daily_metrics.csv.

See the conversation / PR notes for a full discussion of assumptions and
limitations (breadth score denominator, turnover proxy units, rolling
windows over trading days rather than calendar days, etc). This script
implements the formulas exactly as specified and reports rather than
silently fixes any out-of-range results.
"""

import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_CSV = BASE_DIR / "data" / "processed" / "tse_clean.csv"
METRICS_CSV = BASE_DIR / "data" / "processed" / "daily_metrics.csv"

EXPECTED_RANGES = {
    "volume_score": (0.0, 3.0),
    "breadth_score": (0.0, 1.0),
    "turnover_score": (0.0, 1.0),
    "amihud_score": (0.0, 1.0),
    "spread_score": (0.0, 1.0),
}


def safe_divide(numerator, denominator):
    result = numerator / denominator
    return result.replace([np.inf, -np.inf], np.nan)


def compute_volume_score(df):
    daily_total = df.groupby("date")["volume_uzs"].sum(min_count=1)
    rolling_avg = daily_total.rolling(window=90, min_periods=1).mean()
    score = safe_divide(daily_total, rolling_avg)
    score = score.clip(lower=0.0, upper=3.0)
    return score.rename("volume_score")


def compute_breadth_score(df):
    total_tickers = df["ticker"].nunique()
    active_per_day = df.groupby("date")["ticker"].nunique()
    score = active_per_day / total_tickers
    return score.rename("breadth_score")


def compute_turnover_score(df):
    ticker_df = df.sort_values(["ticker", "date"]).copy()
    avg_volume_30d = (
        ticker_df.groupby("ticker")["volume_shares"]
        .rolling(window=30, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )
    market_cap_proxy = ticker_df["close"] * avg_volume_30d
    market_cap_proxy = market_cap_proxy.clip(lower=1.0)
    ticker_turnover = safe_divide(ticker_df["volume_shares"], market_cap_proxy)
    ticker_df["ticker_turnover"] = ticker_turnover
    score = ticker_df.groupby("date")["ticker_turnover"].mean()
    return score.rename("turnover_score")


def compute_amihud_score(df):
    amihud_df = df.copy()
    open_safe = amihud_df["open"].replace(0, np.nan)
    daily_return = safe_divide(amihud_df["close"] - amihud_df["open"], open_safe)
    volume_safe = amihud_df["volume_uzs"].replace(0, np.nan)
    amihud = safe_divide(daily_return.abs(), volume_safe)
    amihud_df["amihud"] = amihud
    daily_avg_amihud = amihud_df.groupby("date")["amihud"].mean()
    score = 1.0 / (1.0 + daily_avg_amihud)
    score = score.replace([np.inf, -np.inf], np.nan)
    return score.rename("amihud_score")


def compute_spread_score(df):
    daily = df.groupby("date").agg(avg_high=("high", "mean"), avg_low=("low", "mean"))
    low_safe = daily["avg_low"].replace(0, np.nan)
    ratio = safe_divide(daily["avg_high"], low_safe)
    ratio = ratio.where(ratio > 0)
    beta = np.log(ratio) ** 2
    sqrt_beta = np.sqrt(beta)
    exp_sqrt_beta = np.exp(sqrt_beta)
    spread = 2 * (exp_sqrt_beta - 1) / (1 + exp_sqrt_beta)
    score = 1 - spread
    return score.rename("spread_score")


def validate_ranges(metrics_df):
    print("\nRange validation:")
    for col, (low, high) in EXPECTED_RANGES.items():
        series = metrics_df[col].dropna()
        violations = series[(series < low) | (series > high)]
        if len(violations) == 0:
            print(f"  {col}: OK, all {len(series)} non-null values within [{low}, {high}]")
        else:
            print(
                f"  {col}: WARNING - {len(violations)} of {len(series)} non-null values "
                f"outside [{low}, {high}] (min={violations.min():.4f}, max={violations.max():.4f}). "
                f"Values left unmodified."
            )


def main():
    df = pd.read_csv(CLEAN_CSV)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

    volume_score = compute_volume_score(df)
    breadth_score = compute_breadth_score(df)
    turnover_score = compute_turnover_score(df)
    amihud_score = compute_amihud_score(df)
    spread_score = compute_spread_score(df)

    metrics_df = pd.concat(
        [volume_score, breadth_score, turnover_score, amihud_score, spread_score], axis=1
    )
    metrics_df = metrics_df.sort_index().reset_index().rename(columns={"index": "date"})

    METRICS_CSV.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(METRICS_CSV, index=False)

    print(f"Saved daily metrics to: {METRICS_CSV}")
    print(f"Total trading days: {len(metrics_df)}")
    print(f"Date range: {metrics_df['date'].min()} to {metrics_df['date'].max()}")

    print("\nFirst 10 rows:")
    print(metrics_df.head(10).to_string(index=False))

    print("\nSummary statistics:")
    print(metrics_df[list(EXPECTED_RANGES.keys())].describe().to_string())

    validate_ranges(metrics_df)


if __name__ == "__main__":
    main()
