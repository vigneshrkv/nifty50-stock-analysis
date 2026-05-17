"""
task2_volatility.py
===================
Phase 3 - Task 2: Volatility Analysis

What this script does:
  - Calculates the daily return for each stock each day
  - Measures volatility as the standard deviation of daily returns
  - Higher std deviation = more price swings = more risky stock
  - Plots a bar chart of the top 10 most volatile stocks
  - Saves the chart as 'task2_volatility.png'

Key concept:
  Daily Return   = (today's close - yesterday's close) / yesterday's close * 100
  Volatility     = standard deviation of all daily returns for that stock
  High volatility = stock price jumps a lot (risky)
  Low volatility  = stock price is stable (safe)

Usage:
    python task2_volatility.py

Requirements:
    pip install pandas matplotlib
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# ─── Configuration ─────────────────────────────────────────────────────────────

STOCK_CSV_DIR = "stock_csvs"
OUTPUT_IMAGE  = "task2_volatility.png"


# ─── Step 1: Load all stock CSVs ───────────────────────────────────────────────

def load_all_stocks(csv_dir: str) -> pd.DataFrame:
    """
    Reads all 50 CSVs and combines into one DataFrame.
    Sorts by ticker and date so daily return calculation is correct.
    """
    all_frames = []

    for fname in os.listdir(csv_dir):
        if not fname.endswith(".csv"):
            continue
        ticker = fname.replace(".csv", "")
        df = pd.read_csv(
            os.path.join(csv_dir, fname),
            parse_dates=["date"]
        )
        df["ticker"] = ticker
        all_frames.append(df)

    master = pd.concat(all_frames, ignore_index=True)

    # IMPORTANT: sort by ticker first, then date
    # This ensures daily return is calculated within each stock separately
    master = master.sort_values(["ticker", "date"]).reset_index(drop=True)

    print(f"  Loaded {master['ticker'].nunique()} stocks | {len(master):,} total rows")
    return master


# ─── Step 2: Calculate daily returns ───────────────────────────────────────────

def calculate_daily_returns(master: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a 'daily_return' column to the DataFrame.

    Formula:
      daily_return = (today_close - yesterday_close) / yesterday_close * 100

    pct_change() does this automatically.
    We use groupby('ticker') so the first day of each stock
    doesn't accidentally compare with the last day of another stock.
    """
    master["daily_return"] = (
        master
        .groupby("ticker")["close"]
        .pct_change() * 100     # multiply by 100 to get percentage
    )

    # The very first row for each stock will be NaN (no previous day)
    # That is expected and correct — we leave it as NaN
    total_nulls = master["daily_return"].isnull().sum()
    print(f"  Calculated daily returns. ({total_nulls} NaN values expected — one per stock)")

    return master


# ─── Step 3: Calculate volatility per stock ────────────────────────────────────

def calculate_volatility(master: pd.DataFrame) -> pd.DataFrame:
    """
    Groups by ticker and calculates the standard deviation
    of daily returns for each stock.

    std() automatically ignores NaN values.

    Higher std = bigger price swings = more volatile = more risky.
    """
    volatility = (
        master
        .groupby("ticker")["daily_return"]
        .std()
        .round(4)
        .reset_index()
    )

    volatility.columns = ["ticker", "volatility_%"]

    # Sort from most volatile to least volatile
    volatility = volatility.sort_values("volatility_%", ascending=False).reset_index(drop=True)

    return volatility


# ─── Step 4: Plot bar chart ─────────────────────────────────────────────────────

def plot_chart(volatility: pd.DataFrame, output_path: str) -> None:
    """
    Plots a horizontal bar chart of the top 10 most volatile stocks.
    Color intensity increases with volatility for visual impact.
    """
    top10 = volatility.head(10).copy()

    # Reverse so highest is at the top
    top10 = top10.sort_values("volatility_%", ascending=True)

    # Color: darker orange = more volatile
    colors = plt.cm.Oranges(
        [0.4 + 0.06 * i for i in range(len(top10))]
    )

    fig, ax = plt.subplots(figsize=(11, 7), facecolor="#f9f9f9")

    bars = ax.barh(
        top10["ticker"],
        top10["volatility_%"],
        color=colors,
        edgecolor="white",
        height=0.6
    )

    ax.set_title(
        "Nifty 50 — Top 10 Most Volatile Stocks (Oct 2023 to Nov 2024)",
        fontsize=13, fontweight="bold", pad=15
    )
    ax.set_xlabel("Volatility (Std Dev of Daily Returns %)", fontsize=10)
    ax.set_facecolor("#f9f9f9")
    ax.spines[["top", "right"]].set_visible(False)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f%%"))

    # Add value labels on each bar
    for bar, val in zip(bars, top10["volatility_%"]):
        ax.text(
            bar.get_width() + 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.4f}%",
            va="center", ha="left",
            fontsize=9, fontweight="bold", color="#7f3b00"
        )

    # Add a note explaining what volatility means
    fig.text(
        0.99, 0.01,
        "Higher value = more price swings = higher risk",
        ha="right", va="bottom",
        fontsize=8, color="gray", style="italic"
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  Chart saved as '{output_path}'")


# ─── Step 5: Print results table ───────────────────────────────────────────────

def print_results(volatility: pd.DataFrame) -> None:
    print("\n" + "=" * 48)
    print("VOLATILITY RANKING — All 50 Stocks")
    print("=" * 48)
    print(f"  {'Rank':<6} {'Ticker':<16} {'Volatility %'}")
    print("-" * 48)

    for i, row in volatility.iterrows():
        rank  = i + 1
        label = " ← most volatile"  if rank == 1  else ""
        label = " ← least volatile" if rank == 50 else label
        print(f"  {rank:<6} {row['ticker']:<16} {row['volatility_%']:.4f}%{label}")

    print("=" * 48)
    print(f"\n  Most volatile : {volatility.iloc[0]['ticker']}  ({volatility.iloc[0]['volatility_%']:.4f}%)")
    print(f"  Least volatile: {volatility.iloc[-1]['ticker']} ({volatility.iloc[-1]['volatility_%']:.4f}%)")


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("Phase 3 - Task 2: Volatility Analysis")
    print("=" * 50 + "\n")

    print("[1/4] Loading stock data...")
    master = load_all_stocks(STOCK_CSV_DIR)

    print("\n[2/4] Calculating daily returns...")
    master = calculate_daily_returns(master)

    print("\n[3/4] Calculating volatility per stock...")
    volatility = calculate_volatility(master)
    print(f"  Volatility calculated for {len(volatility)} stocks.")

    print("\n[4/4] Plotting chart...")
    plot_chart(volatility, OUTPUT_IMAGE)

    print_results(volatility)


if __name__ == "__main__":
    main()
