"""
Task 5.1 — Builds the UZLI composite index with Min-Max normalization.

Loads data/processed/daily_metrics.csv, normalizes each metric to [0, 100]
using the full historical sample, computes the weighted composite, assigns a
liquidity label, and saves data/processed/uzli_final.csv.

Weights:
  volume_norm    25%
  breadth_norm   20%
  turnover_norm  25%
  amihud_norm    20%
  spread_norm    10%

Output columns (in order):
  date, volume_norm, breadth_norm, turnover_norm, amihud_norm, spread_norm,
  uzli_score, liquidity_label
"""

import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

BASE_DIR    = Path(__file__).resolve().parent.parent
METRICS_CSV = BASE_DIR / "data" / "processed" / "daily_metrics.csv"
OUTPUT_CSV  = BASE_DIR / "data" / "processed" / "uzli_final.csv"
OUTPUT_TS   = BASE_DIR / "data" / "processed" / "uzli_final_timeseries.png"
OUTPUT_HIST = BASE_DIR / "data" / "processed" / "uzli_final_distribution.png"

RAW_COLS = [
    "volume_score",
    "breadth_score",
    "turnover_score",
    "amihud_score",
    "spread_score",
]

NORM_COLS = [
    "volume_norm",
    "breadth_norm",
    "turnover_norm",
    "amihud_norm",
    "spread_norm",
]

WEIGHTS = {
    "volume_norm":   0.25,
    "breadth_norm":  0.20,
    "turnover_norm": 0.25,
    "amihud_norm":   0.20,
    "spread_norm":   0.10,
}

LABEL_BINS   = [float("-inf"), 40.0, 70.0, float("inf")]
LABEL_NAMES  = ["Low Liquidity", "Moderate Liquidity", "High Liquidity"]
LABEL_COLORS = {"Low Liquidity": "#d9534f", "Moderate Liquidity": "#f0ad4e", "High Liquidity": "#5cb85c"}


def validate_weights(weights):
    total = sum(weights.values())
    if not abs(total - 1.0) < 1e-9:
        raise ValueError(
            f"Weights must sum to exactly 1.0, but got {total:.10f}. "
            f"Please check the WEIGHTS dictionary."
        )


def minmax_normalize(df, raw_cols, norm_cols):
    result = df.copy()
    for raw, norm in zip(raw_cols, norm_cols):
        col_min = df[raw].min()
        col_max = df[raw].max()
        if col_max == col_min:
            raise ValueError(
                f"Cannot normalize '{raw}': min and max are identical ({col_min}). "
                f"The column is constant across the full sample."
            )
        result[norm] = 100.0 * (df[raw] - col_min) / (col_max - col_min)
    return result


def main():
    validate_weights(WEIGHTS)
    print(f"Weights validated: sum = {sum(WEIGHTS.values()):.1f}")

    if not METRICS_CSV.exists():
        print(f"ERROR: input file not found: {METRICS_CSV}", file=sys.stderr)
        sys.exit(1)
    print(f"Input verified: {METRICS_CSV}")

    df = pd.read_csv(METRICS_CSV, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    print(f"Loaded {len(df)} rows  |  {df['date'].min().date()} to {df['date'].max().date()}")

    # Min-Max normalize each metric over the full sample
    df = minmax_normalize(df, RAW_COLS, NORM_COLS)

    # Weighted composite, rounded to 2 decimal places
    df["uzli_score"] = round(
        sum(df[col] * w for col, w in WEIGHTS.items()), 2
    )

    # Liquidity label
    df["liquidity_label"] = pd.cut(
        df["uzli_score"],
        bins=LABEL_BINS,
        labels=LABEL_NAMES,
        right=False,
    )

    # Save CSV in specified column order
    out_cols = ["date"] + NORM_COLS + ["uzli_score", "liquidity_label"]
    df[out_cols].to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved: {OUTPUT_CSV}")

    # Summary statistics
    valid = df.dropna(subset=["uzli_score"])
    avg   = valid["uzli_score"].mean()
    idx_max = valid["uzli_score"].idxmax()
    idx_min = valid["uzli_score"].idxmin()

    print(f"\nAverage UZLI : {avg:.2f}")
    print(f"Highest UZLI : {valid.loc[idx_max, 'date'].date()}  ->  {valid.loc[idx_max, 'uzli_score']:.2f}")
    print(f"Lowest  UZLI : {valid.loc[idx_min, 'date'].date()}  ->  {valid.loc[idx_min, 'uzli_score']:.2f}")

    # Label distribution
    print("\nLabel distribution:")
    print(df["liquidity_label"].value_counts().sort_index().to_string())

    # Time-series plot with label-zone reference lines
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df["date"], df["uzli_score"], linewidth=0.8, color="steelblue", zorder=3)
    ax.axhline(70, color=LABEL_COLORS["High Liquidity"],     linestyle="--", linewidth=0.9, label="High (>= 70)")
    ax.axhline(40, color=LABEL_COLORS["Moderate Liquidity"], linestyle="--", linewidth=0.9, label="Moderate (>= 40)")
    ax.set_title("Uzbekistan Liquidity Index (UZLI) — Min-Max Normalized, 2016–2026", fontsize=13)
    ax.set_xlabel("Date")
    ax.set_ylabel("UZLI Score (0–100)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTPUT_TS, dpi=150)
    print(f"\nTime-series plot saved: {OUTPUT_TS}")

    # Histogram coloured by label zone
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    bins = range(0, 102, 2)
    for label, color in LABEL_COLORS.items():
        subset = valid[valid["liquidity_label"] == label]["uzli_score"]
        ax2.hist(subset, bins=bins, color=color, edgecolor="white",
                 linewidth=0.3, alpha=0.85, label=label)
    ax2.axvline(40, color="black", linestyle="--", linewidth=0.8)
    ax2.axvline(70, color="black", linestyle="--", linewidth=0.8)
    ax2.set_title("Distribution of Daily UZLI Scores — Min-Max Normalized, 2016–2026", fontsize=12)
    ax2.set_xlabel("UZLI Score")
    ax2.set_ylabel("Number of trading days")
    ax2.legend(fontsize=9)
    ax2.grid(True, axis="y", alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUTPUT_HIST, dpi=150)
    print(f"Histogram saved: {OUTPUT_HIST}")


if __name__ == "__main__":
    main()
