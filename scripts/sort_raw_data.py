"""
Sorts data/raw/tse_raw_data.csv chronologically (date asc, then ticker asc).

The raw CSV was built by running the scraper in three separate passes
(forward backfill, then a historical backfill, then more forward backfill),
so rows are not in date order on disk even though each individual run wrote
sequentially. This script only reorders rows - it does not add, drop, or
modify any observation - and sanity-checks for date gaps that the historical
append might have introduced (e.g. a gap right at the 2023-01-03/2023-01-04
join point between the two backfill runs).
"""

import csv
import shutil
from datetime import datetime
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tse_scraper import CSV_COLUMNS, build_holiday_set, daterange_weekdays_excluding_holidays

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_CSV = BASE_DIR / "data" / "raw" / "tse_raw_data.csv"
BACKUP_CSV = BASE_DIR / "data" / "raw" / "tse_raw_data.unsorted.bak.csv"


def load_rows(csv_path):
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def verify_no_gaps(rows):
    """Compares actual trading dates against the full set of weekdays
    (excluding fixed holidays) in range. Missing weekdays are expected
    in low-liquidity periods (pre-2019), so this reports rather than fails -
    but it specifically calls out gaps spanning the backfill join point."""
    actual_dates = {datetime.strptime(r["date"], "%Y-%m-%d").date() for r in rows}
    start, end = min(actual_dates), max(actual_dates)
    holidays = build_holiday_set(start, end)
    expected_weekdays = set(daterange_weekdays_excluding_holidays(start, end, holidays))
    missing = sorted(expected_weekdays - actual_dates)

    join_point_gap = [d for d in missing if datetime(2022, 12, 20).date() <= d <= datetime(2023, 1, 10).date()]

    return missing, join_point_gap


def main():
    rows = load_rows(RAW_CSV)
    total_before = len(rows)

    for row in rows:
        row["_parsed_date"] = datetime.strptime(row["date"], "%Y-%m-%d").date()

    rows.sort(key=lambda r: (r["_parsed_date"], r["ticker"]))

    missing_weekdays, join_point_gap = verify_no_gaps(rows)

    for row in rows:
        del row["_parsed_date"]

    total_after = len(rows)
    first_date = rows[0]["date"]
    last_date = rows[-1]["date"]

    if total_before != total_after:
        raise AssertionError(f"Row count changed during sort: {total_before} -> {total_after}")

    shutil.copy2(RAW_CSV, BACKUP_CSV)

    with RAW_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"First date: {first_date}")
    print(f"Last date: {last_date}")
    print(f"Total rows before sorting: {total_before}")
    print(f"Total rows after sorting: {total_after}")
    print(f"Unsorted backup written to: {BACKUP_CSV}")

    print(f"\nMissing weekdays (excl. fixed holidays) in range: {len(missing_weekdays)}")
    if join_point_gap:
        print(f"WARNING: missing dates near the backfill join point (2022-12-20 to 2023-01-10): {join_point_gap}")
    else:
        print("No missing dates around the backfill join point (2022-12-20 to 2023-01-10) - join looks clean.")


if __name__ == "__main__":
    main()
