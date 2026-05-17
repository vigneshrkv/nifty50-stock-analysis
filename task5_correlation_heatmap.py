"""
task5_correlation_heatmap.py
=============================
Phase 3 - Task 5: Correlation Heatmap

What this script does:
  - Builds a price matrix: rows = dates, columns = stock tickers
  - Calculates correlation between every pair of stocks
  - Plots a heatmap showing which stocks move together
  - Saves the chart as 'task5_correlation_heatmap.png'

Key concept:
  Correlation tells us how two stocks move relative to each other.

  +1.0  = perfect positive  → when Stock A goes up, Stock B always goes up too
   0.0  = no relation       → Stock A and B move independently
  -1.0  = perfect negative  → when Stock A goes up, Stock B goes down

  This is useful for:
    - Portfolio diversification (pick low-correlated stocks to reduce risk)
    - Understanding which sectors move together

Usage:
    python task5_correlation_heatmap.py

Requirements:
    pip install pandas matplotlib
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np


# ─── Configuration ─────────────────────────────────────────────────────────────

STOCK_CSV_DIR = "stock_csvs"
OUTPUT_IMAGE  = "task5_correlation_heatmap.png"


# ─── Step 1: Build the price matrix ────────────────────────────────────────────

def build_price_matrix(csv_dir: str) -> pd.DataFrame:
    """
    Reads all 50 CSVs and builds a wide-format DataFrame:
      - Each row   = one trading date
      - Each column = one stock's closing price

    This is called a 'pivot' — instead of one long column,
    we lay each stock side by side.

    Example:
      date        TCS     SBIN    INFY   ...
      2023-10-03  3811    641     1423   ...
      2023-10-04  3790    638     1418   ...
    """
    all_frames = []

    for fname in sorted(os.listdir(csv_dir)):
        if not fname.endswith(".csv"):
            continue
        ticker = fname.replace(".csv", "")
        df = pd.read_csv(os.path.join(csv_dir, fname), parse_dates=["date"])

        # Keep only date and close, rename close to ticker name
        df = df[["date", "close"]].rename(columns={"close": ticker})
        all_frames.append(df)

    # Merge all stocks on date
    price_matrix = all_frames[0]
    for df in all_frames[1:]:
        price_matrix = price_matrix.merge(df, on="date", how="inner")

    price_matrix = price_matrix.sort_values("date").set_index("date")

    print(f"  Price matrix shape: {price_matrix.shape[0]} dates × {price_matrix.shape[1]} stocks")
    print(f"  Date range: {price_matrix.index.min().date()} to {price_matrix.index.max().date()}")

    return price_matrix


# ─── Step 2: Calculate correlation matrix ──────────────────────────────────────

def calculate_correlation(price_matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the Pearson correlation between every pair of stocks.

    pandas .corr() does this in one line — it computes correlation
    between every column pair automatically.

    Result is a 50x50 matrix where:
      - Diagonal is always 1.0 (a stock is perfectly correlated with itself)
      - Upper and lower triangles are mirror images
    """
    corr_matrix = price_matrix.corr()

    print(f"  Correlation matrix shape: {corr_matrix.shape}")
    print(f"  Value range: {corr_matrix.values.min():.4f} to {corr_matrix.values.max():.4f}")

    # Find most and least correlated pairs (excluding diagonal)
    np.fill_diagonal(corr_matrix.values, np.nan)  # temporarily remove diagonal

    mask = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    pairs = corr_matrix.where(mask).stack().dropna().sort_values(ascending=False)

    print(f"\n  Most correlated pair  : {pairs.index[0]}  →  {pairs.iloc[0]:.4f}")
    print(f"  Least correlated pair : {pairs.index[-1]}  →  {pairs.iloc[-1]:.4f}")

    # Restore diagonal
    np.fill_diagonal(corr_matrix.values, 1.0)

    return corr_matrix


# ─── Step 3: Plot the heatmap ──────────────────────────────────────────────────

def plot_heatmap(corr_matrix: pd.DataFrame, output_path: str) -> None:
    """
    Plots a 50x50 heatmap of the correlation matrix.

    Color scale:
      Dark green  = +1.0 (highly correlated)
      White       =  0.0 (no correlation)
      Dark red    = -1.0 (negatively correlated)

    We also add the correlation value as text inside each cell
    for the clearest readability.
    """

    fig, ax = plt.subplots(figsize=(22, 18), facecolor="white")

    # Draw the heatmap manually using imshow
    im = ax.imshow(
        corr_matrix.values,
        cmap="RdYlGn",      # Red → Yellow → Green
        vmin=-1, vmax=1,
        aspect="auto"
    )

    # Tick labels
    tickers = corr_matrix.columns.tolist()
    ax.set_xticks(range(len(tickers)))
    ax.set_yticks(range(len(tickers)))
    ax.set_xticklabels(tickers, rotation=90, fontsize=7)
    ax.set_yticklabels(tickers, fontsize=7)

    # Add correlation values as text in each cell
    for i in range(len(tickers)):
        for j in range(len(tickers)):
            val = corr_matrix.values[i, j]
            # Use white text on dark cells, black text on light cells
            text_color = "white" if abs(val) > 0.7 else "black"
            ax.text(
                j, i,
                f"{val:.2f}",
                ha="center", va="center",
                fontsize=5.5,
                color=text_color
            )

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label("Correlation Coefficient", fontsize=11)
    cbar.set_ticks([-1, -0.5, 0, 0.5, 1])
    cbar.set_ticklabels(["-1.0\n(opposite)", "-0.5", "0.0\n(no link)", "0.5", "+1.0\n(together)"])

    ax.set_title(
        "Nifty 50 — Stock Price Correlation Heatmap (Oct 2023 to Nov 2024)",
        fontsize=14, fontweight="bold", pad=20
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  Chart saved as '{output_path}'")


# ─── Step 4: Print top correlated pairs ────────────────────────────────────────

def print_results(corr_matrix: pd.DataFrame) -> None:
    """Prints the top 10 most and least correlated stock pairs."""

    # Get upper triangle pairs only (avoid duplicates)
    np.fill_diagonal(corr_matrix.values, np.nan)
    mask  = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    pairs = corr_matrix.where(mask).stack().dropna().sort_values(ascending=False)
    np.fill_diagonal(corr_matrix.values, 1.0)

    print("\n" + "=" * 52)
    print("TOP 10 MOST CORRELATED PAIRS (move together)")
    print("=" * 52)
    print(f"  {'Stock A':<16} {'Stock B':<16} {'Correlation'}")
    print("-" * 52)
    for (a, b), val in pairs.head(10).items():
        print(f"  {a:<16} {b:<16} {val:+.4f}")

    print("\n" + "=" * 52)
    print("TOP 10 LEAST CORRELATED PAIRS (move independently)")
    print("=" * 52)
    print(f"  {'Stock A':<16} {'Stock B':<16} {'Correlation'}")
    print("-" * 52)
    for (a, b), val in pairs.tail(10).items():
        print(f"  {a:<16} {b:<16} {val:+.4f}")
    print("=" * 52)


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("Phase 3 - Task 5: Correlation Heatmap")
    print("=" * 55 + "\n")

    print("[1/3] Building price matrix...")
    price_matrix = build_price_matrix(STOCK_CSV_DIR)

    print("\n[2/3] Calculating correlation matrix...")
    corr_matrix = calculate_correlation(price_matrix)

    print("\n[3/3] Plotting heatmap...")
    plot_heatmap(corr_matrix, OUTPUT_IMAGE)

    print_results(corr_matrix)


if __name__ == "__main__":
    main()
