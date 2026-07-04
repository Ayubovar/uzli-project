"""
Cleans the raw TSE scrape (data/raw/tse_raw_data.csv) into an analysis-ready
dataset at data/processed/tse_clean.csv.
"""

import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_CSV = BASE_DIR / "data" / "raw" / "tse_raw_data.csv"
CLEAN_CSV = BASE_DIR / "data" / "processed" / "tse_clean.csv"

PRICE_VOLUME_COLUMNS = ["open", "high", "low", "close", "volume_shares", "volume_uzs", "num_trades"]
VOLUME_COLUMNS = ["volume_shares", "volume_uzs"]


def clean_numeric_column(series):
    cleaned = series.astype(str).str.replace(",", "", regex=False).str.replace(" ", "", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


def standardize_text(series):
    return series.astype(str).str.strip().str.upper().str.replace(r"\s+", " ", regex=True)


def check_ohlc_consistency(df):
    violations = df[
        (df["low"] > df["open"])
        | (df["low"] > df["high"])
        | (df["low"] > df["close"])
        | (df["high"] < df["open"])
        | (df["high"] < df["close"])
    ]
    return violations


def main():
    df = pd.read_csv(RAW_CSV)
    total_before = len(df)

    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

    df = df.drop_duplicates(subset=["ticker", "date"], keep="first")
    duplicates_removed = total_before - len(df)

    for col in PRICE_VOLUME_COLUMNS:
        df[col] = clean_numeric_column(df[col])

    df["ticker"] = standardize_text(df["ticker"])
    df["company_name"] = standardize_text(df["company_name"])

    df["traded"] = (df["volume_shares"] > 0).astype(int)

    for col in VOLUME_COLUMNS:
        df.loc[df[col] == 0, col] = pd.NA

    ohlc_violations = check_ohlc_consistency(df)

    CLEAN_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_CSV, index=False)

    total_after = len(df)
    pct_traded = 100 * df["traded"].mean()

    print(f"Total rows before cleaning: {total_before}")
    print(f"Duplicate rows removed: {duplicates_removed}")
    print(f"Total rows after cleaning: {total_after}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Unique tickers: {df['ticker'].nunique()}")
    print(f"Percentage of rows where trading happened: {pct_traded:.2f}%")
    print(f"Cleaned data saved to: {CLEAN_CSV}")

    print(f"\nOHLC consistency check: {len(ohlc_violations)} violation(s) found (data left unmodified)")
    if len(ohlc_violations):
        print(ohlc_violations[["ticker", "date", "open", "high", "low", "close"]].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
