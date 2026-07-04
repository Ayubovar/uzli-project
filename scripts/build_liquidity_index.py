"""
Builds the UZLI (Uzbekistan Liquidity Index) composite from the five pre-computed
daily scores in data/processed/daily_metrics.csv.

Weights (as specified):
  volume_score   25%
  breadth_score  20%
  turnover_score 25%
  amihud_score   20%
  spread_score   10%

Outputs:
  data/processed/uzli_daily.csv        — date + five scores + uzli
  data/processed/uzli_daily.png        — time-series plot of uzli
  data/processed/uzli_distribution.png — histogram of uzli values
"""

import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

BASE_DIR     = Path(__file__).resolve().parent.parent
METRICS_CSV  = BASE_DIR / "data" / "processed" / "daily_metrics.csv"
OUTPUT_CSV   = BASE_DIR / "data" / "processed" / "uzli_daily.csv"
OUTPUT_PLOT  = BASE_DIR / "data" / "processed" / "uzli_daily.png"
OUTPUT_HIST  = BASE_DIR / "data" / "processed" / "uzli_distribution.png"

WEIGHTS = {
    "volume_score":   0.25,
    "breadth_score":  0.20,
    "turnover_score": 0.25,
    "amihud_score":   0.20,
    "spread_score":   0.10,
}


def validate_weights(weights):
    total = sum(weights.values())
    if not abs(total - 1.0) < 1e-9:
        raise ValueError(
            f"Weights must sum to exactly 1.0, but got {total:.10f}. "
            f"Please check the WEIGHTS dictionary."
        )


def main():
    # Verify weights sum to 1.0 before doing anything else
    validate_weights(WEIGHTS)
    print(f"Weights validated: sum = {sum(WEIGHTS.values()):.1f}")

    # Verify input file exists
    if not METRICS_CSV.exists():
        print(f"ERROR: input file not found: {METRICS_CSV}", file=sys.stderr)
        sys.exit(1)
    print(f"Input verified: {METRICS_CSV}")

    df = pd.read_csv(METRICS_CSV, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Weighted composite — NaN propagates if any component is missing
    df["uzli"] = sum(df[col] * w for col, w in WEIGHTS.items())

    # Save output CSV
    out_cols = ["date"] + list(WEIGHTS.keys()) + ["uzli"]
    df[out_cols].to_csv(OUTPUT_CSV, index=False)
    print(f"Saved: {OUTPUT_CSV}")
    print(f"Rows : {len(df)}  |  date range: {df['date'].min().date()} -> {df['date'].max().date()}")

    null_count = df["uzli"].isna().sum()
    if null_count:
        print(f"WARNING: {null_count} day(s) have NaN uzli (missing component score).")

    # Summary statistics
    print("\nUZLI summary statistics:")
    print(df["uzli"].describe().to_string())

    # Lowest and highest UZLI day
    valid = df.dropna(subset=["uzli"])
    idx_min = valid["uzli"].idxmin()
    idx_max = valid["uzli"].idxmax()
    print(f"\nLowest  UZLI day: {valid.loc[idx_min, 'date'].date()}  ->  {valid.loc[idx_min, 'uzli']:.6f}")
    print(f"Highest UZLI day: {valid.loc[idx_max, 'date'].date()}  ->  {valid.loc[idx_max, 'uzli']:.6f}")

    # Top 10 highest and lowest liquidity days
    top10_high = valid.nlargest(10, "uzli")[["date", "uzli"]].reset_index(drop=True)
    top10_low  = valid.nsmallest(10, "uzli")[["date", "uzli"]].reset_index(drop=True)
    top10_high.index += 1
    top10_low.index  += 1

    print("\nTop 10 highest-liquidity days:")
    print(top10_high.to_string())

    print("\nTop 10 lowest-liquidity days:")
    print(top10_low.to_string())

    # Time-series plot
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df["date"], df["uzli"], linewidth=0.8, color="steelblue")
    ax.set_title("Uzbekistan Liquidity Index (UZLI) — 2016–2026", fontsize=13)
    ax.set_xlabel("Date")
    ax.set_ylabel("UZLI (composite score)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTPUT_PLOT, dpi=150)
    print(f"\nPlot saved: {OUTPUT_PLOT}")

    # Histogram of UZLI values
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.hist(valid["uzli"], bins=60, color="steelblue", edgecolor="white", linewidth=0.4)
    ax2.set_title("Distribution of Daily UZLI Values — 2016–2026", fontsize=13)
    ax2.set_xlabel("UZLI")
    ax2.set_ylabel("Number of trading days")
    ax2.grid(True, axis="y", alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUTPUT_HIST, dpi=150)
    print(f"Histogram saved: {OUTPUT_HIST}")


if __name__ == "__main__":
    main()
