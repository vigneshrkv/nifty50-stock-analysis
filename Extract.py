"""
extract.py
==========
Phase 1 — Data Extraction & Transformation

Reads all YAML files from the raw_yaml folder,
organises them by stock symbol, and saves 50 individual
CSV files into the stock_csvs folder.

Folder structure expected:
    II Project/
    ├── extract.py           <- this file
    ├── raw_yaml/            <- all 284 YAML files here
    │   ├── 2023-10-03_05-30-00.yaml
    │   └── ...
    ├── Sector_data - Sheet1.xlsx
    └── stock_csvs/          <- created automatically by this script

Usage:
    Open terminal in II Project folder, then run:
    python extract.py

Requirements:
    pip install pyyaml pandas
"""

import os
import yaml
import pandas as pd
from collections import defaultdict


# ─── Configuration ────────────────────────────────────────────────────────────

# Folder where all YAML files are kept (no subfolders needed)
RAW_YAML_DIR = "raw_yaml"

# Folder where 50 CSVs will be saved (created automatically)
OUTPUT_DIR = "stock_csvs"

# Some ticker names inside the YAML files are slightly different
# from what the sector CSV uses. This mapping fixes those mismatches.
TICKER_CORRECTIONS = {
    "TATACONSUM": "TATACONSUMER",
    "ADANIENT":   "ADANIGREEN",
    "BHARTIARTL": "AIRTEL",
}


# ─── Step 1: Validate the raw_yaml folder ─────────────────────────────────────

def validate_input_folder(folder: str) -> list:
    """
    Checks that the raw_yaml folder exists and contains YAML files.
    Returns the sorted list of YAML filenames.
    """
    if not os.path.exists(folder):
        raise FileNotFoundError(
            f"\nERROR: Folder '{folder}' not found.\n"
            "Make sure 'raw_yaml' folder is in the same directory as extract.py.\n"
            f"Current directory: {os.getcwd()}"
        )

    yaml_files = sorted(
        f for f in os.listdir(folder) if f.endswith(".yaml")
    )

    if not yaml_files:
        raise FileNotFoundError(
            f"\nERROR: No .yaml files found inside '{folder}'.\n"
            "Make sure you extracted the RAR contents into the raw_yaml folder."
        )

    print(f"    Found {len(yaml_files)} YAML files in '{folder}/'")
    return yaml_files


# ─── Step 2: Parse all YAML files ─────────────────────────────────────────────

def parse_yaml_files(folder: str, yaml_files: list) -> dict:
    """
    Reads every YAML file. Each file has 50 entries (one per Nifty stock).
    Groups all entries by ticker symbol.

    Returns:
        { "TCS": [ {date, open, high, low, close, volume, month}, ... ], ... }
    """
    stock_records = defaultdict(list)
    skipped = []

    for i, fname in enumerate(yaml_files, 1):
        fpath = os.path.join(folder, fname)

        # Progress update every 50 files
        if i % 50 == 0 or i == len(yaml_files):
            print(f"    Parsed {i}/{len(yaml_files)} files...", end="\r")

        with open(fpath, "r", encoding="utf-8") as f:
            entries = yaml.safe_load(f)

        # Skip empty or malformed files
        if not entries or not isinstance(entries, list):
            skipped.append(fname)
            continue

        for entry in entries:
            ticker = entry.get("Ticker", "").strip()

            # Apply corrections for mismatched ticker names
            ticker = TICKER_CORRECTIONS.get(ticker, ticker)

            if not ticker:
                continue

            stock_records[ticker].append({
                "date":   entry["date"],
                "open":   entry["open"],
                "high":   entry["high"],
                "low":    entry["low"],
                "close":  entry["close"],
                "volume": entry["volume"],
                "month":  entry["month"],
            })

    print()  # newline after progress line

    if skipped:
        print(f"    WARNING: Skipped {len(skipped)} malformed files: {skipped}")

    return dict(stock_records)


# ─── Step 3: Save one CSV per stock ───────────────────────────────────────────

def save_stock_csvs(stock_records: dict, output_dir: str) -> None:
    """
    For each stock symbol, creates a sorted DataFrame and saves it as a CSV.
    Also checks for missing values and duplicate dates.
    """
    os.makedirs(output_dir, exist_ok=True)
    issues = []

    for ticker, records in sorted(stock_records.items()):
        df = pd.DataFrame(records)

        # Parse date and sort chronologically
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        # Reorder columns cleanly
        df = df[["date", "open", "high", "low", "close", "volume", "month"]]

        # Check for missing values
        if df.isnull().sum().sum() > 0:
            issues.append(f"  {ticker}: has missing values")

        # Check for and remove duplicate dates
        dupes = df.duplicated(subset="date").sum()
        if dupes > 0:
            issues.append(f"  {ticker}: {dupes} duplicate date(s) removed")
            df = df.drop_duplicates(subset="date")

        # Save
        out_path = os.path.join(output_dir, f"{ticker}.csv")
        df.to_csv(out_path, index=False)

    if issues:
        print("\n    Data quality warnings:")
        for issue in issues:
            print(issue)
    else:
        print("    No data quality issues found.")


# ─── Step 4: Print summary ────────────────────────────────────────────────────

def print_summary(output_dir: str) -> None:
    """Prints a table showing each stock, row count, and date range."""
    csv_files = sorted(f for f in os.listdir(output_dir) if f.endswith(".csv"))

    print("\n" + "=" * 58)
    print("EXTRACTION COMPLETE")
    print("=" * 58)
    print(f"{'Symbol':<18} {'Rows':>5}   {'Date range'}")
    print("-" * 58)

    for fname in csv_files:
        ticker = fname.replace(".csv", "")
        df = pd.read_csv(
            os.path.join(output_dir, fname),
            parse_dates=["date"]
        )
        start = df["date"].min().strftime("%Y-%m-%d")
        end   = df["date"].max().strftime("%Y-%m-%d")
        print(f"{ticker:<18} {len(df):>5}   {start}  to  {end}")

    print("=" * 58)
    print(f"\nAll CSV files saved to: {os.path.abspath(output_dir)}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 58)
    print("Phase 1 - Data Extraction")
    print(f"Working directory: {os.getcwd()}")
    print("=" * 58 + "\n")

    print("[1/3] Checking raw_yaml folder...")
    yaml_files = validate_input_folder(RAW_YAML_DIR)
    print()

    print("[2/3] Parsing YAML files and grouping by stock symbol...")
    stock_records = parse_yaml_files(RAW_YAML_DIR, yaml_files)
    print(f"    Found {len(stock_records)} unique stock symbols.")
    total_rows = sum(len(v) for v in stock_records.values())
    print(f"    Total rows collected: {total_rows}\n")

    print(f"[3/3] Saving {len(stock_records)} CSV files to '{OUTPUT_DIR}/'...")
    save_stock_csvs(stock_records, OUTPUT_DIR)
    print(f"    Saved {len(stock_records)} CSV files.\n")

    print_summary(OUTPUT_DIR)


if __name__ == "__main__":
    main()