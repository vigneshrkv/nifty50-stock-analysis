"""
task4_sector_performance.py
============================
Phase 3 - Task 4: Sector-wise Performance

What this script does:
  - Calculates yearly return for each of the 50 stocks
  - Groups stocks by their sector
  - Calculates the average yearly return per sector
  - Plots a bar chart showing best and worst performing sectors
  - Saves the chart as 'task4_sector_performance.png'

Key concept:
  Yearly Return per stock = (last close - first close) / first close * 100
  Sector Avg Return       = average of yearly returns of all stocks in that sector

  Example — BANKING sector has 4 stocks:
    HDFCBANK  : +12%
    ICICIBANK : +28%
    AXISBANK  : +15%
    KOTAKBANK : -8%
    Sector avg = (12 + 28 + 15 - 8) / 4 = +11.75%

Usage:
    python task4_sector_performance.py

Requirements:
    pip install pandas matplotlib
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# ─── Configuration ─────────────────────────────────────────────────────────────

STOCK_CSV_DIR   = "stock_csvs"
SECTOR_CSV_PATH = "Sector_data - Sheet1.csv"
OUTPUT_IMAGE    = "task4_sector_performance.png"


# ─── Step 1: Load all stocks ───────────────────────────────────────────────────

def load_all_stocks(csv_dir: str) -> pd.DataFrame:
    """Reads all 50 CSVs and combines into one DataFrame."""
    all_frames = []

    for fname in os.listdir(csv_dir):
        if not fname.endswith(".csv"):
            continue
        ticker = fname.replace(".csv", "")
        df = pd.read_csv(os.path.join(csv_dir, fname), parse_dates=["date"])
        df["ticker"] = ticker
        all_frames.append(df)

    master = pd.concat(all_frames, ignore_index=True)
    master = master.sort_values(["ticker", "date"]).reset_index(drop=True)

    print(f"  Loaded {master['ticker'].nunique()} stocks | {len(master):,} total rows")
    return master


# ─── Step 2: Load sector data ──────────────────────────────────────────────────

def load_sector_data(path: str) -> pd.DataFrame:
    """
    Reads the sector CSV and extracts ticker cleanly.
    Symbol column looks like 'TCS: TCS' — we take the part after colon.
    """
    df = pd.read_csv(path)
    df["ticker"]  = df["Symbol"].str.split(": ").str[-1].str.strip()
    df["company"] = df["COMPANY"].str.strip()
    df["sector"]  = df["sector"].str.strip()
    df = df[["ticker", "company", "sector"]]
    print(f"  Loaded sector info for {len(df)} stocks across {df['sector'].nunique()} sectors")
    return df


# ─── Step 3: Calculate yearly return per stock ─────────────────────────────────

def calculate_yearly_returns(master: pd.DataFrame) -> pd.DataFrame:
    """
    For each stock, gets first and last closing price
    and calculates percentage return over the full period.
    """
    returns = master.groupby("ticker").agg(
        first_close = ("close", "first"),
        last_close  = ("close", "last")
    ).reset_index()

    returns["yearly_return_%"] = (
        (returns["last_close"] - returns["first_close"])
        / returns["first_close"]
        * 100
    ).round(2)

    print(f"  Calculated yearly return for {len(returns)} stocks")
    return returns


# ─── Step 4: Calculate sector-wise average return ──────────────────────────────

def calculate_sector_performance(returns: pd.DataFrame, sector_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merges stock returns with sector info, then
    calculates average yearly return per sector.
    """

    # Merge returns with sector information
    merged = returns.merge(sector_df, on="ticker", how="left")

    # Check if any stocks are missing sector info
    missing = merged[merged["sector"].isnull()]["ticker"].tolist()
    if missing:
        print(f"  WARNING: No sector found for: {missing}")

    # Group by sector and calculate average return
    sector_perf = (
        merged
        .groupby("sector")["yearly_return_%"]
        .agg(
            avg_return    = "mean",
            num_stocks    = "count",
            best_stock    = lambda x: merged.loc[x.idxmax(), "ticker"],
            worst_stock   = lambda x: merged.loc[x.idxmin(), "ticker"]
        )
        .reset_index()
    )

    sector_perf["avg_return"] = sector_perf["avg_return"].round(2)

    # Sort from best to worst
    sector_perf = sector_perf.sort_values("avg_return", ascending=False).reset_index(drop=True)

    return sector_perf


# ─── Step 5: Plot bar chart ─────────────────────────────────────────────────────

def plot_chart(sector_perf: pd.DataFrame, output_path: str) -> None:
    """
    Plots a horizontal bar chart for all sectors.
    Green bars = positive return, Red bars = negative return.
    """

    # Sort ascending so highest is at top of horizontal chart
    df = sector_perf.sort_values("avg_return", ascending=True).copy()

    # Color: green for positive, red for negative
    colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in df["avg_return"]]

    fig, ax = plt.subplots(figsize=(12, 9), facecolor="#f9f9f9")

    bars = ax.barh(
        df["sector"],
        df["avg_return"],
        color=colors,
        edgecolor="white",
        height=0.65
    )

    # Vertical line at 0
    ax.axvline(0, color="gray", linewidth=1, linestyle="--", alpha=0.7)

    ax.set_title(
        "Nifty 50 — Sector-wise Average Yearly Return (Oct 2023 to Nov 2024)",
        fontsize=13, fontweight="bold", pad=15
    )
    ax.set_xlabel("Average Yearly Return (%)", fontsize=10)
    ax.set_facecolor("#f9f9f9")
    ax.spines[["top", "right"]].set_visible(False)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))

    # Value labels on each bar
    for bar, val in zip(bars, df["avg_return"]):
        offset = 1 if val >= 0 else -1
        ha     = "left" if val >= 0 else "right"
        color  = "#27ae60" if val >= 0 else "#c0392b"
        ax.text(
            bar.get_width() + offset,
            bar.get_y() + bar.get_height() / 2,
            f"{val:+.1f}%",
            va="center", ha=ha,
            fontsize=9, fontweight="bold", color=color
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  Chart saved as '{output_path}'")


# ─── Step 6: Print results table ───────────────────────────────────────────────

def print_results(sector_perf: pd.DataFrame) -> None:
    print("\n" + "=" * 68)
    print("SECTOR-WISE PERFORMANCE RANKING")
    print("=" * 68)
    print(f"  {'Rank':<5} {'Sector':<22} {'Avg Return':>10}  {'Stocks':>6}  {'Best Stock'}")
    print("-" * 68)

    for i, row in sector_perf.iterrows():
        rank = i + 1
        print(
            f"  {rank:<5} {row['sector']:<22} {row['avg_return']:>+9.2f}%"
            f"  {int(row['num_stocks']):>6}  {row['best_stock']}"
        )

    print("=" * 68)
    print(f"\n  Best sector  : {sector_perf.iloc[0]['sector']}  ({sector_perf.iloc[0]['avg_return']:+.2f}%)")
    print(f"  Worst sector : {sector_perf.iloc[-1]['sector']} ({sector_perf.iloc[-1]['avg_return']:+.2f}%)")


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("Phase 3 - Task 4: Sector-wise Performance")
    print("=" * 55 + "\n")

    print("[1/4] Loading stock data...")
    master = load_all_stocks(STOCK_CSV_DIR)

    print("\n[2/4] Loading sector data...")
    sector_df = load_sector_data(SECTOR_CSV_PATH)

    print("\n[3/4] Calculating yearly returns and sector averages...")
    returns     = calculate_yearly_returns(master)
    sector_perf = calculate_sector_performance(returns, sector_df)
    print(f"  Calculated performance for {len(sector_perf)} sectors")

    print("\n[4/4] Plotting chart...")
    plot_chart(sector_perf, OUTPUT_IMAGE)

    print_results(sector_perf)


if __name__ == "__main__":
    main()
