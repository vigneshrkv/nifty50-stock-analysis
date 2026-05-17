"""
task3_cumulative_return.py
==========================
Phase 3 - Task 3: Cumulative Return Over Time

What this script does:
  - Takes the top 5 best performing stocks from Task 1
    (TRENT, BEL, M&M, BAJAJ-AUTO, AIRTEL)
  - Calculates how their cumulative return grew day by day
  - Plots a line chart showing all 5 stocks on the same graph
  - Saves the chart as 'task3_cumulative_return.png'

Key concept:
  Daily Return      = % change in closing price from previous day
  Cumulative Return = total % gain/loss from the very first day till now
                      It compounds — like interest on interest

  Formula:
    cumulative_return = ( (1+r1) * (1+r2) * (1+r3) * ... ) - 1

  Example:
    Day 1: +2%  → cumulative = +2%
    Day 2: +3%  → cumulative = (1.02 * 1.03) - 1 = +5.06%  (not just 5%!)
    Day 3: -1%  → cumulative = (1.02 * 1.03 * 0.99) - 1 = +4.01%

Usage:
    python task3_cumulative_return.py

Requirements:
    pip install pandas matplotlib
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker


# ─── Configuration ─────────────────────────────────────────────────────────────

STOCK_CSV_DIR = "stock_csvs"
OUTPUT_IMAGE  = "task3_cumulative_return.png"

# Top 5 stocks by yearly return (from Task 1 results)
TOP5_TICKERS = ["TRENT", "BEL", "M&M", "BAJAJ-AUTO", "AIRTEL"]

# Colors for each stock line
LINE_COLORS = {
    "TRENT":     "#e74c3c",   # red
    "BEL":       "#2ecc71",   # green
    "M&M":       "#3498db",   # blue
    "BAJAJ-AUTO": "#f39c12",  # orange
    "AIRTEL":    "#9b59b6",   # purple
}


# ─── Step 1: Load only the top 5 stocks ────────────────────────────────────────

def load_top5_stocks(csv_dir: str, tickers: list) -> pd.DataFrame:
    """
    Reads CSV files only for the top 5 tickers.
    Sorts by ticker and date for correct calculation.
    """
    all_frames = []

    for ticker in tickers:
        fpath = os.path.join(csv_dir, f"{ticker}.csv")

        if not os.path.exists(fpath):
            print(f"  WARNING: {ticker}.csv not found, skipping.")
            continue

        df = pd.read_csv(fpath, parse_dates=["date"])
        df["ticker"] = ticker
        all_frames.append(df)
        print(f"  Loaded {ticker} — {len(df)} trading days")

    master = pd.concat(all_frames, ignore_index=True)
    master = master.sort_values(["ticker", "date"]).reset_index(drop=True)

    return master


# ─── Step 2: Calculate cumulative return ───────────────────────────────────────

def calculate_cumulative_return(master: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates cumulative return for each stock day by day.

    Step 1: daily_return = pct_change of close price
    Step 2: cumulative   = (1 + r1)(1 + r2)... - 1

    We use transform(cumprod) so each stock's cumulative
    return is calculated independently within that group.
    """

    # Daily return for each stock
    master["daily_return"] = (
        master
        .groupby("ticker")["close"]
        .pct_change()
    )

    # Cumulative return — compounded day by day
    master["cumulative_return_%"] = (
        master
        .groupby("ticker")["daily_return"]
        .transform(lambda x: (1 + x).cumprod() - 1)
        * 100   # convert to percentage
    ).round(4)

    # Drop the first row for each ticker (NaN daily return)
    master = master.dropna(subset=["cumulative_return_%"])

    return master


# ─── Step 3: Plot the line chart ───────────────────────────────────────────────

def plot_chart(master: pd.DataFrame, tickers: list, output_path: str) -> None:
    """
    Plots one line per stock showing how cumulative return
    grew (or shrank) over the entire time period.

    Each line starts at 0% on day 1 and ends at the
    total yearly return on the last day.
    """

    fig, ax = plt.subplots(figsize=(14, 7), facecolor="#f9f9f9")

    for ticker in tickers:
        stock_data = master[master["ticker"] == ticker]

        if stock_data.empty:
            continue

        final_return = stock_data["cumulative_return_%"].iloc[-1]

        ax.plot(
            stock_data["date"],
            stock_data["cumulative_return_%"],
            label=f"{ticker}  ({final_return:+.1f}%)",
            color=LINE_COLORS.get(ticker, "gray"),
            linewidth=2.2,
            alpha=0.9
        )

        # Add a dot at the final point
        ax.scatter(
            stock_data["date"].iloc[-1],
            final_return,
            color=LINE_COLORS.get(ticker, "gray"),
            s=50, zorder=5
        )

    # Draw a horizontal line at 0% (breakeven)
    ax.axhline(0, color="gray", linewidth=1, linestyle="--", alpha=0.6)
    ax.text(
        master["date"].min(), 1.5,
        "0% (breakeven)",
        fontsize=8, color="gray", style="italic"
    )

    # Formatting
    ax.set_title(
        "Nifty 50 — Cumulative Return of Top 5 Stocks (Oct 2023 to Nov 2024)",
        fontsize=13, fontweight="bold", pad=15
    )
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Cumulative Return (%)", fontsize=10)
    ax.set_facecolor("#f9f9f9")
    ax.spines[["top", "right"]].set_visible(False)

    # Format x-axis to show month-year
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)

    # Format y-axis to show % sign
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))

    # Legend
    ax.legend(
        title="Stock (Total Return)",
        fontsize=10,
        title_fontsize=10,
        loc="upper left",
        framealpha=0.8
    )

    # Shaded area below 0 to highlight losses
    ax.fill_between(
        master["date"].unique(),
        0,
        master.groupby("date")["cumulative_return_%"].min().values,
        where=master.groupby("date")["cumulative_return_%"].min().values < 0,
        alpha=0.05, color="red"
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  Chart saved as '{output_path}'")


# ─── Step 4: Print final summary ───────────────────────────────────────────────

def print_results(master: pd.DataFrame, tickers: list) -> None:
    print("\n" + "=" * 52)
    print("CUMULATIVE RETURN — Final Values")
    print("=" * 52)
    print(f"  {'Ticker':<14} {'Start Date':<14} {'End Date':<14} {'Total Return'}")
    print("-" * 52)

    for ticker in tickers:
        stock = master[master["ticker"] == ticker]
        if stock.empty:
            continue
        start = stock["date"].min().strftime("%Y-%m-%d")
        end   = stock["date"].max().strftime("%Y-%m-%d")
        total = stock["cumulative_return_%"].iloc[-1]
        print(f"  {ticker:<14} {start:<14} {end:<14} {total:+.2f}%")

    print("=" * 52)


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 52)
    print("Phase 3 - Task 3: Cumulative Return Over Time")
    print("=" * 52 + "\n")

    print(f"[1/3] Loading top 5 stocks: {TOP5_TICKERS}")
    master = load_top5_stocks(STOCK_CSV_DIR, TOP5_TICKERS)
    print(f"\n  Total rows loaded: {len(master):,}")

    print("\n[2/3] Calculating cumulative returns...")
    master = calculate_cumulative_return(master)
    print("  Done.")

    print("\n[3/3] Plotting line chart...")
    plot_chart(master, TOP5_TICKERS, OUTPUT_IMAGE)

    print_results(master, TOP5_TICKERS)


if __name__ == "__main__":
    main()
