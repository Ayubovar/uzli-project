"""
Scrapes daily trading data from the Tashkent Republican Stock Exchange (uzse.uz)
to build a raw dataset for a market liquidity index.

Data source note: uzse.uz does not expose daily OHLC tables via plain HTML pages.
The site's "/trade_results" history search form (mkt_id, begin, end) posts to
"/test_history_trade.xlsx", which returns an Excel file of every individual trade
in the date range. This script downloads that file one day at a time and
aggregates the individual trades into a per-ticker daily OHLCV row:
  - open  = price of the first trade of the day
  - close = price of the last trade of the day
  - high  = max trade price
  - low   = min trade price
  - volume_shares = sum of quantity traded
  - volume_uzs    = sum of trade value (UZS)
  - num_trades    = count of trades

Note: robots.txt on uzse.uz specifies "Crawl-delay: 60" for general user agents.
This script uses a 1-second delay per the task spec; lower this risk by running
it once and caching results rather than re-running it often.
"""

import argparse
import csv
import io
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
import openpyxl

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_CSV = BASE_DIR / "data" / "raw" / "tse_raw_data.csv"
ERROR_LOG = BASE_DIR / "data" / "raw" / "scraper_errors.log"

HISTORY_XLSX_URL = "https://uzse.uz/test_history_trade.xlsx"
MARKET_ID = "STK"  # stocks only; use "ALL" to include bonds/repo/futures
START_DATE = date(2023, 1, 1)
REQUEST_DELAY_SECONDS = 1
REQUEST_TIMEOUT_SECONDS = 30

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

CSV_COLUMNS = [
    "ticker",
    "company_name",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume_shares",
    "volume_uzs",
    "num_trades",
]


def fixed_holidays(year):
    return {
        date(year, 1, 1),    # New Year
        date(year, 3, 21),   # Navruz
        date(year, 9, 1),    # Independence Day
        date(year, 10, 1),   # Teachers Day
        date(year, 12, 8),   # Constitution Day
    }


def build_holiday_set(start, end):
    holidays = set()
    for year in range(start.year, end.year + 1):
        holidays |= fixed_holidays(year)
    return holidays


def daterange_weekdays_excluding_holidays(start, end, holidays):
    current = start
    while current <= end:
        if current.weekday() < 5 and current not in holidays:
            yield current
        current += timedelta(days=1)


def log_error(message):
    timestamp = datetime.utcnow().isoformat()
    with ERROR_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def latest_date_in_csv(csv_path):
    if not csv_path.exists():
        return None
    latest = None
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_date = datetime.strptime(row["date"], "%Y-%m-%d").date()
            if latest is None or row_date > latest:
                latest = row_date
    return latest


def resolve_start_date(csv_path, default_start):
    latest = latest_date_in_csv(csv_path)
    if latest is None:
        return default_start
    return latest + timedelta(days=1)


def fetch_day_trades(day):
    date_str = day.strftime("%d.%m.%Y")
    params = {"mkt_id": MARKET_ID, "begin": date_str, "end": date_str}
    response = requests.get(
        HISTORY_XLSX_URL, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS
    )
    response.raise_for_status()
    workbook = openpyxl.load_workbook(io.BytesIO(response.content), data_only=True)
    worksheet = workbook.active

    rows = list(worksheet.iter_rows(min_row=2, values_only=True))
    return [row for row in rows if row and row[0] is not None]


def aggregate_day(trade_rows):
    """trade_rows columns: time, isin, ticker, issuer, sec_type, market, platform, price, qty, value"""
    by_ticker = {}
    for trade_time, _isin, ticker, issuer, *_rest, price, qty, value in trade_rows:
        bucket = by_ticker.setdefault(ticker, {"company_name": issuer, "trades": []})
        bucket["trades"].append((trade_time, price, qty, value))

    aggregated_rows = []
    for ticker, data in by_ticker.items():
        trades = sorted(data["trades"], key=lambda t: t[0])
        prices = [t[1] for t in trades]
        aggregated_rows.append(
            {
                "ticker": ticker,
                "company_name": data["company_name"],
                "open": prices[0],
                "high": max(prices),
                "low": min(prices),
                "close": prices[-1],
                "volume_shares": sum(t[2] for t in trades),
                "volume_uzs": sum(t[3] for t in trades),
                "num_trades": len(trades),
            }
        )
    return aggregated_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
    parser.add_argument("--end-date", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
    args = parser.parse_args()

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    end_date = args.end_date or date.today()
    start_date = args.start_date or resolve_start_date(OUTPUT_CSV, START_DATE)
    holidays = build_holiday_set(start_date, end_date)

    if start_date > end_date:
        print(f"Nothing to do; start date {start_date.isoformat()} is after end date {end_date.isoformat()}.")
        return

    print(f"Fetching {start_date.isoformat()} through {end_date.isoformat()}.")
    file_exists = OUTPUT_CSV.exists()
    with OUTPUT_CSV.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()

        for day in daterange_weekdays_excluding_holidays(start_date, end_date, holidays):
            print(f"Fetching {day.isoformat()}...")
            try:
                trade_rows = fetch_day_trades(day)
            except Exception as exc:
                log_error(f"{day.isoformat()}: failed to fetch/parse - {exc}")
                time.sleep(REQUEST_DELAY_SECONDS)
                continue

            if not trade_rows:
                print(f"  {day.isoformat()}: no trades (non-trading day), skipping.")
                time.sleep(REQUEST_DELAY_SECONDS)
                continue

            try:
                day_rows = aggregate_day(trade_rows)
                for row in day_rows:
                    row["date"] = day.isoformat()
                    writer.writerow(row)
                csv_file.flush()
                print(f"  {day.isoformat()}: wrote {len(day_rows)} ticker rows.")
            except Exception as exc:
                log_error(f"{day.isoformat()}: failed to aggregate/write - {exc}")

            time.sleep(REQUEST_DELAY_SECONDS)

    print(f"Done. Output written to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
