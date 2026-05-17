"""
task1_top_stocks.py
===================
Phase 3 - Task 1: Top 10 Green & Red Stocks

What this script does:
  - Reads all 50 stock CSVs
  - Calculates yearly return for each stock
    Formula: (last closing price - first closing price) / first closing price * 100
  - Finds top 10 best performing (green) and top 10 worst performing (red) stocks
  - Saves a bar chart as 'task1_top_green_red_stocks.png'

Usage:
    python task1_top_stocks.py

Requirements:
    pip install pandas matplotlib
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# ─── Configuration ─────────────────────────────────────────────────────────────

STOCK_CSV_DIR = "stock_csvs"       # folder with 50 CSVs from Phase 1
OUTPUT_IMAGE  = "task1_top_green_red_stocks.png"


# ─── Step 1: Load all stock CSVs ───────────────────────────────────────────────

def load_all_stocks(csv_dir: str) -> pd.DataFrame:
    """
    Reads all 50 CSVs and combines them into one big DataFrame.
    Adds a 'ticker' column using the filename.
    """
    all_frames = []

    csv_files = [f for f in os.listdir(csv_dir) if f.endswith(".csv")]

    for fname in csv_files:
        ticker = fname.replace(".csv", "")
        df = pd.read_csv(
            os.path.join(csv_dir, fname),
            parse_dates=["date"]
        )
        df["ticker"] = ticker
        all_frames.append(df)

    # Combine all into one DataFrame and sort by date
    master = pd.concat(all_frames, ignore_index=True)
    master = master.sort_values("date").reset_index(drop=True)

    print(f"  Loaded {master['ticker'].nunique()} stocks | {len(master):,} total rows")
    print(f"  Date range: {master['date'].min().date()} to {master['date'].max().date()}")

    return master


# ─── Step 2: Calculate yearly return per stock ─────────────────────────────────

def calculate_yearly_returns(master: pd.DataFrame) -> pd.DataFrame:
    """
    For each stock, calculates:
      - first_close : closing price on the very first trading day
      - last_close  : closing price on the very last trading day
      - yearly_return_%  : percentage change from first to last

    Formula:
      yearly_return = (last_close - first_close) / first_close * 100
    """

    # Group by ticker and get first and last closing price
    returns = master.groupby("ticker").agg(
        first_close = ("close", "first"),
        last_close  = ("close", "last")
    ).reset_index()

    # Calculate percentage return
    returns["yearly_return_%"] = (
        (returns["last_close"] - returns["first_close"])
        / returns["first_close"]
        * 100
    ).round(2)

    # Sort from highest to lowest return
    returns = returns.sort_values("yearly_return_%", ascending=False).reset_index(drop=True)

    return returns


# ─── Step 3: Extract top 10 green and red stocks ───────────────────────────────

def get_top_green_red(returns: pd.DataFrame):
    """
    Splits the sorted returns DataFrame into:
      - top_green : top 10 highest returns (best performers)
      - top_red   : top 10 lowest returns  (worst performers)
    """
    top_green = returns.head(10).copy()   # first 10 rows = highest return
    top_red   = returns.tail(10).copy()   # last 10 rows  = lowest return

    # Sort red stocks so worst is at bottom of chart
    top_red = top_red.sort_values("yearly_return_%", ascending=True)

    return top_green, top_red


# ─── Step 4: Plot the chart ────────────────────────────────────────────────────

def plot_chart(top_green: pd.DataFrame, top_red: pd.DataFrame, output_path: str) -> None:
    """
    Creates a side-by-side bar chart:
      Left  : Top 10 Green stocks (positive returns) in green
      Right : Top 10 Red stocks   (negative returns) in red
    """

    fig, (ax1, ax2) = plt.subplots(
        1, 2,
        figsize=(16, 7),
        facecolor="#f9f9f9"
    )

    fig.suptitle(
        "Nifty 50 — Top 10 Green & Red Stocks (Oct 2023 to Nov 2024)",
        fontsize=15,
        fontweight="bold",
        y=1.01
    )

    # ── Left chart: Green stocks ───────────────────────────────────────────────
    bars1 = ax1.barh(
        top_green["ticker"],
        top_green["yearly_return_%"],
        color="#2ecc71",
        edgecolor="white",
        height=0.6
    )

    ax1.set_title("Top 10 Best Performers 📈", fontsize=12, fontweight="bold", pad=12)
    ax1.set_xlabel("Yearly Return (%)", fontsize=10)
    ax1.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax1.invert_yaxis()   # highest at top
    ax1.set_facecolor("#f9f9f9")
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.axvline(0, color="gray", linewidth=0.8, linestyle="--")

    # Add value labels on bars
    for bar, val in zip(bars1, top_green["yearly_return_%"]):
        ax1.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            f"+{val:.1f}%",
            va="center", ha="left",
            fontsize=9, color="#27ae60", fontweight="bold"
        )

    # ── Right chart: Red stocks ────────────────────────────────────────────────
    bars2 = ax2.barh(
        top_red["ticker"],
        top_red["yearly_return_%"],
        color="#e74c3c",
        edgecolor="white",
        height=0.6
    )

    ax2.set_title("Top 10 Worst Performers 📉", fontsize=12, fontweight="bold", pad=12)
    ax2.set_xlabel("Yearly Return (%)", fontsize=10)
    ax2.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax2.invert_yaxis()
    ax2.set_facecolor("#f9f9f9")
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.axvline(0, color="gray", linewidth=0.8, linestyle="--")

    # Add value labels on bars
    for bar, val in zip(bars2, top_red["yearly_return_%"]):
        offset = -1 if val < 0 else 1
        ha     = "right" if val < 0 else "left"
        label  = f"{val:.1f}%"
        ax2.text(
            bar.get_width() + offset,
            bar.get_y() + bar.get_height() / 2,
            label,
            va="center", ha=ha,
            fontsize=9, color="#c0392b", fontweight="bold"
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  Chart saved as '{output_path}'")


# ─── Step 5: Print results table ───────────────────────────────────────────────

def print_results(top_green: pd.DataFrame, top_red: pd.DataFrame) -> None:
    print("\n" + "=" * 50)
    print("TOP 10 GREEN STOCKS (Best Performers)")
    print("=" * 50)
    print(f"  {'Rank':<6} {'Ticker':<15} {'Return'}")
    print("-" * 50)
    for i, row in top_green.iterrows():
        rank = i + 1
        print(f"  {rank:<6} {row['ticker']:<15} +{row['yearly_return_%']:.2f}%")

    print("\n" + "=" * 50)
    print("TOP 10 RED STOCKS (Worst Performers)")
    print("=" * 50)
    print(f"  {'Rank':<6} {'Ticker':<15} {'Return'}")
    print("-" * 50)
    for i, (_, row) in enumerate(top_red.iterrows(), 1):
        print(f"  {i:<6} {row['ticker']:<15} {row['yearly_return_%']:.2f}%")
    print("=" * 50)


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("Phase 3 - Task 1: Top 10 Green & Red Stocks")
    print("=" * 50 + "\n")

    print("[1/4] Loading stock data...")
    master = load_all_stocks(STOCK_CSV_DIR)

    print("\n[2/4] Calculating yearly returns...")
    returns = calculate_yearly_returns(master)
    print(f"  Calculated returns for {len(returns)} stocks.")

    print("\n[3/4] Extracting top 10 green and red stocks...")
    top_green, top_red = get_top_green_red(returns)

    print("\n[4/4] Plotting chart...")
    plot_chart(top_green, top_red, OUTPUT_IMAGE)

    print_results(top_green, top_red)


if __name__ == "__main__":
    main()
