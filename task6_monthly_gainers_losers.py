"""
task6_monthly_gainers_losers.py
================================
Phase 3 - Task 6: Monthly Top 5 Gainers & Losers
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_pdf import PdfPages

STOCK_CSV_DIR = "stock_csvs"
OUTPUT_PDF    = "task6_monthly_gainers_losers.pdf"
OUTPUT_FOLDER = "task6_charts"

def load_all_stocks(csv_dir):
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

def calculate_monthly_returns(master):
    monthly = master.groupby(["ticker", "month"]).agg(
        first_close=("close", "first"),
        last_close=("close", "last")
    ).reset_index()
    monthly["monthly_return_%"] = (
        (monthly["last_close"] - monthly["first_close"])
        / monthly["first_close"] * 100
    ).round(2)
    months = sorted(monthly["month"].unique())
    print(f"  Calculated monthly returns for {len(months)} months x {master['ticker'].nunique()} stocks")
    print(f"  Months covered: {months[0]}  to  {months[-1]}")
    return monthly

def plot_one_month(ax_gain, ax_loss, month, month_data):
    sorted_data = month_data.sort_values("monthly_return_%", ascending=False)
    top5_gain   = sorted_data.head(5)
    top5_loss   = sorted_data.tail(5).sort_values("monthly_return_%", ascending=True)
    month_label = pd.to_datetime(month + "-01").strftime("%b %Y")

    bars1 = ax_gain.barh(top5_gain["ticker"], top5_gain["monthly_return_%"],
                          color="#2ecc71", edgecolor="white", height=0.55)
    ax_gain.set_title(f"{month_label} - Top 5 Gainers", fontsize=10, fontweight="bold")
    ax_gain.set_xlabel("Monthly Return (%)", fontsize=8)
    ax_gain.invert_yaxis()
    ax_gain.axvline(0, color="gray", linewidth=0.8, linestyle="--")
    ax_gain.spines[["top", "right"]].set_visible(False)
    ax_gain.set_facecolor("#f9f9f9")
    ax_gain.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
    ax_gain.tick_params(labelsize=8)
    for bar, val in zip(bars1, top5_gain["monthly_return_%"]):
        ax_gain.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                     f"+{val:.1f}%", va="center", ha="left", fontsize=7.5,
                     color="#27ae60", fontweight="bold")

    bars2 = ax_loss.barh(top5_loss["ticker"], top5_loss["monthly_return_%"],
                          color="#e74c3c", edgecolor="white", height=0.55)
    ax_loss.set_title(f"{month_label} - Top 5 Losers", fontsize=10, fontweight="bold")
    ax_loss.set_xlabel("Monthly Return (%)", fontsize=8)
    ax_loss.invert_yaxis()
    ax_loss.axvline(0, color="gray", linewidth=0.8, linestyle="--")
    ax_loss.spines[["top", "right"]].set_visible(False)
    ax_loss.set_facecolor("#f9f9f9")
    ax_loss.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
    ax_loss.tick_params(labelsize=8)
    for bar, val in zip(bars2, top5_loss["monthly_return_%"]):
        ax_loss.text(bar.get_width() - 0.1, bar.get_y() + bar.get_height() / 2,
                     f"{val:.1f}%", va="center", ha="right", fontsize=7.5,
                     color="#c0392b", fontweight="bold")

def generate_all_charts(monthly, output_pdf, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    months = sorted(monthly["month"].unique())
    print(f"  Generating charts for {len(months)} months...")

    with PdfPages(output_pdf) as pdf:
        for i, month in enumerate(months, 1):
            month_data  = monthly[monthly["month"] == month].copy()
            month_label = pd.to_datetime(month + "-01").strftime("%B %Y")

            fig, (ax_gain, ax_loss) = plt.subplots(1, 2, figsize=(14, 5), facecolor="#f9f9f9")
            fig.suptitle(f"Nifty 50 - Monthly Gainers & Losers | {month_label}",
                         fontsize=12, fontweight="bold", y=1.02)

            plot_one_month(ax_gain, ax_loss, month, month_data)
            plt.tight_layout()

            pdf.savefig(fig, bbox_inches="tight")
            png_path = os.path.join(output_folder, f"{month}_gainers_losers.png")
            plt.savefig(png_path, dpi=130, bbox_inches="tight")
            plt.close(fig)
            print(f"  [{i:>2}/{len(months)}] {month_label} done")

    print(f"\n  All charts saved to PDF : '{output_pdf}'")
    print(f"  Individual PNGs saved in: '{output_folder}/'")

def print_summary(monthly):
    months = sorted(monthly["month"].unique())
    print("\n" + "=" * 62)
    print("MONTHLY SUMMARY - Top Gainer & Loser Each Month")
    print("=" * 62)
    print(f"  {'Month':<12} {'Top Gainer':<16} {'Return':>8}  {'Top Loser':<16} {'Return':>8}")
    print("-" * 62)
    for month in months:
        data   = monthly[monthly["month"] == month]
        gainer = data.loc[data["monthly_return_%"].idxmax()]
        loser  = data.loc[data["monthly_return_%"].idxmin()]
        label  = pd.to_datetime(month + "-01").strftime("%b %Y")
        print(f"  {label:<12} {gainer['ticker']:<16} {gainer['monthly_return_%']:>+7.2f}%"
              f"  {loser['ticker']:<16} {loser['monthly_return_%']:>+7.2f}%")
    print("=" * 62)

def main():
    print("=" * 55)
    print("Phase 3 - Task 6: Monthly Gainers & Losers")
    print("=" * 55 + "\n")

    print("[1/3] Loading stock data...")
    master = load_all_stocks(STOCK_CSV_DIR)

    print("\n[2/3] Calculating monthly returns...")
    monthly = calculate_monthly_returns(master)

    print("\n[3/3] Generating charts for all 14 months...")
    generate_all_charts(monthly, OUTPUT_PDF, OUTPUT_FOLDER)

    print_summary(monthly)

    print("\n" + "=" * 55)
    print("PHASE 3 COMPLETE - All 6 tasks done!")
    print("=" * 55)
    print("\nFiles saved:")
    print("  task1_top_green_red_stocks.png")
    print("  task2_volatility.png")
    print("  task3_cumulative_return.png")
    print("  task4_sector_performance.png")
    print("  task5_correlation_heatmap.png")
    print("  task6_monthly_gainers_losers.pdf")
    print("  task6_charts/  (14 individual PNGs)")

if __name__ == "__main__":
    main()
