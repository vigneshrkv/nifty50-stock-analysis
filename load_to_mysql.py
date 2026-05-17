"""
load_to_mysql.py
================
Phase 2 — Data Cleaning & Loading into MySQL

What this script does:
  1. Reads all 50 CSVs from the stock_csvs folder
  2. Cleans the data (fixes data types, handles nulls, removes duplicates)
  3. Merges sector information from Sector_data - Sheet1.csv
  4. Creates the MySQL database and table automatically
  5. Loads all cleaned data into MySQL

Folder structure expected:
    II Project/
    ├── load_to_mysql.py        <- this file
    ├── stock_csvs/             <- 50 CSVs from Phase 1
    └── Sector_data - Sheet1.csv

Usage:
    python load_to_mysql.py

Requirements:
    pip install pandas sqlalchemy pymysql
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text


# ─── Configuration ─────────────────────────────────────────────────────────────

STOCK_CSV_DIR   = "stock_csvs"               # folder with 50 CSVs
SECTOR_CSV_PATH = "Sector_data - Sheet1.csv" # sector mapping file

# MySQL connection details
DB_HOST     = "localhost"
DB_USER     = "root"
DB_PASSWORD = "1234"
DB_NAME     = "stock_analysis"
TABLE_NAME  = "nifty50_stocks"


# ─── Step 1: Load and clean sector data ────────────────────────────────────────

def load_sector_data(path: str) -> pd.DataFrame:
    """
    Reads the sector CSV and extracts the ticker symbol cleanly.

    The Symbol column looks like: 'TCS: TCS' or 'HDFC BANK: HDFCBANK'
    We extract the part after the colon as the ticker.
    """
    print("  Loading sector data...")

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"\nERROR: '{path}' not found.\n"
            "Make sure Sector_data - Sheet1.csv is in the same folder as this script."
        )

    df = pd.read_csv(path)

    # Extract ticker from Symbol column (e.g. "TCS: TCS" → "TCS")
    df["ticker"]  = df["Symbol"].str.split(": ").str[-1].str.strip()
    df["company"] = df["COMPANY"].str.strip()
    df["sector"]  = df["sector"].str.strip()

    # Keep only what we need
    df = df[["ticker", "company", "sector"]]

    print(f"  Loaded {len(df)} sector entries.")
    return df


# ─── Step 2: Load, clean and merge all stock CSVs ──────────────────────────────

def load_and_clean_stocks(csv_dir: str, sector_df: pd.DataFrame) -> pd.DataFrame:
    """
    Reads all 50 stock CSVs, cleans each one, adds the ticker column,
    merges with sector data, and combines into one master DataFrame.
    """
    print(f"\n  Reading CSVs from '{csv_dir}/'...")

    csv_files = sorted(f for f in os.listdir(csv_dir) if f.endswith(".csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"\nERROR: No CSV files found in '{csv_dir}/'.\n"
            "Make sure you ran extract.py first (Phase 1)."
        )

    all_frames = []

    for i, fname in enumerate(csv_files, 1):
        ticker = fname.replace(".csv", "")
        fpath  = os.path.join(csv_dir, fname)

        df = pd.read_csv(fpath)

        # ── Cleaning steps ────────────────────────────────────────────────────

        # 1. Parse date column to proper datetime
        df["date"] = pd.to_datetime(df["date"])

        # 2. Add ticker column
        df["ticker"] = ticker

        # 3. Ensure numeric columns are correct type
        for col in ["open", "high", "low", "close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df["volume"] = pd.to_numeric(df["volume"], errors="coerce").astype("Int64")

        # 4. Drop rows where critical columns are missing
        before = len(df)
        df = df.dropna(subset=["date", "open", "high", "low", "close", "volume"])
        dropped = before - len(df)
        if dropped > 0:
            print(f"    WARNING: {ticker} — dropped {dropped} rows with missing values")

        # 5. Remove duplicate dates
        dupes = df.duplicated(subset=["date"]).sum()
        if dupes > 0:
            print(f"    WARNING: {ticker} — removed {dupes} duplicate date(s)")
            df = df.drop_duplicates(subset=["date"])

        # 6. Sort chronologically
        df = df.sort_values("date").reset_index(drop=True)

        all_frames.append(df)

        if i % 10 == 0 or i == len(csv_files):
            print(f"  Cleaned {i}/{len(csv_files)} stocks...", end="\r")

    print()

    # ── Combine all stocks into one DataFrame ─────────────────────────────────
    master_df = pd.concat(all_frames, ignore_index=True)
    print(f"\n  Combined shape before merge: {master_df.shape}")

    # ── Merge sector information ───────────────────────────────────────────────
    master_df = master_df.merge(sector_df, on="ticker", how="left")

    # Check if any tickers didn't get sector info
    missing_sector = master_df[master_df["sector"].isnull()]["ticker"].unique()
    if len(missing_sector) > 0:
        print(f"  WARNING: No sector info for: {missing_sector}")

    # ── Final column order ────────────────────────────────────────────────────
    master_df = master_df[[
        "date", "ticker", "company", "sector",
        "open", "high", "low", "close", "volume", "month"
    ]]

    print(f"  Final shape after merge:  {master_df.shape}")
    print(f"  Total stocks:  {master_df['ticker'].nunique()}")
    print(f"  Date range:    {master_df['date'].min().date()} to {master_df['date'].max().date()}")
    print(f"  Missing values:\n{master_df.isnull().sum()}")

    return master_df


# ─── Step 3: Create database and load data into MySQL ──────────────────────────

def load_to_mysql(df: pd.DataFrame) -> None:
    """
    Connects to MySQL, creates the database if it doesn't exist,
    and loads the full cleaned DataFrame into the nifty50_stocks table.
    """

    # First connect without specifying the database to create it
    print(f"\n  Connecting to MySQL...")
    engine_root = create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/",
        echo=False
    )

    with engine_root.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
        conn.execute(text(f"USE {DB_NAME}"))
        print(f"  Database '{DB_NAME}' ready.")

    engine_root.dispose()

    # Now connect directly to stock_analysis database
    engine = create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}",
        echo=False
    )

    print(f"  Loading {len(df):,} rows into '{TABLE_NAME}' table...")
    print("  (This may take 30-60 seconds, please wait...)")

    # if_exists='replace' drops and recreates the table each run
    df.to_sql(
        name=TABLE_NAME,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=1000     # load 1000 rows at a time
    )

    # Verify the load
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
        count = result.fetchone()[0]

    engine.dispose()

    print(f"  Successfully loaded {count:,} rows into MySQL.")


# ─── Step 4: Print final summary ───────────────────────────────────────────────

def print_summary(df: pd.DataFrame) -> None:
    print("\n" + "=" * 58)
    print("PHASE 2 COMPLETE — Summary")
    print("=" * 58)
    print(f"  Database  :  {DB_NAME}")
    print(f"  Table     :  {TABLE_NAME}")
    print(f"  Total rows:  {len(df):,}")
    print(f"  Stocks    :  {df['ticker'].nunique()}")
    print(f"  Sectors   :  {df['sector'].nunique()}")
    print()
    print("  Sector breakdown:")
    sector_counts = df.groupby("sector")["ticker"].nunique().sort_values(ascending=False)
    for sector, count in sector_counts.items():
        print(f"    {sector:<25} {count} stock(s)")
    print("=" * 58)
    print("\nYou can now open MySQL Workbench and run:")
    print(f"  USE {DB_NAME};")
    print(f"  SELECT * FROM {TABLE_NAME} LIMIT 10;")
    print("to verify your data is loaded correctly.")


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 58)
    print("Phase 2 - Data Cleaning & MySQL Loading")
    print(f"Working directory: {os.getcwd()}")
    print("=" * 58)

    print("\n[1/3] Loading sector data...")
    sector_df = load_sector_data(SECTOR_CSV_PATH)

    print("\n[2/3] Loading and cleaning stock CSVs...")
    master_df = load_and_clean_stocks(STOCK_CSV_DIR, sector_df)

    print("\n[3/3] Loading into MySQL...")
    load_to_mysql(master_df)

    print_summary(master_df)


if __name__ == "__main__":
    main()  