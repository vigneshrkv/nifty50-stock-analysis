"""
dashboard.py
============
Phase 4 - Streamlit Dashboard

Run with:
    streamlit run dashboard.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import streamlit as st


# ─── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Nifty 50 Stock Analysis",
    page_icon="📈",
    layout="wide"
)


# ─── Sector & Company maps ─────────────────────────────────────────────────────

SECTOR_MAP = {
    'ADANIGREEN':'MISCELLANEOUS','ADANIPORTS':'MISCELLANEOUS','AIRTEL':'TELECOM',
    'APOLLOHOSP':'MISCELLANEOUS','ASIANPAINT':'PAINTS','AXISBANK':'BANKING',
    'BAJAJ-AUTO':'AUTOMOBILES','BAJAJFINSV':'FINANCE','BAJFINANCE':'FINANCE',
    'BEL':'DEFENCE','BPCL':'ENERGY','BRITANNIA':'FOOD & TOBACCO',
    'CIPLA':'PHARMACEUTICALS','COALINDIA':'MINING','DRREDDY':'PHARMACEUTICALS',
    'EICHERMOT':'AUTOMOBILES','GRASIM':'CEMENT','HCLTECH':'SOFTWARE',
    'HDFCBANK':'BANKING','HDFCLIFE':'INSURANCE','HEROMOTOCO':'AUTOMOBILES',
    'HINDALCO':'ALUMINIUM','HINDUNILVR':'FMCG','ICICIBANK':'BANKING',
    'INDUSINDBK':'BANKING','INFY':'SOFTWARE','IOC':'ENERGY','ITC':'FOOD & TOBACCO',
    'JSWSTEEL':'STEEL','KOTAKBANK':'BANKING','LT':'ENGINEERING',
    'M&M':'AUTOMOBILES','MARUTI':'AUTOMOBILES','NESTLEIND':'FMCG',
    'NTPC':'POWER','ONGC':'ENERGY','POWERGRID':'POWER','RELIANCE':'ENERGY',
    'SBILIFE':'INSURANCE','SBIN':'BANKING','SHRIRAMFIN':'FINANCE',
    'SUNPHARMA':'PHARMACEUTICALS','TATACONSUMER':'FMCG','TATAMOTORS':'AUTOMOBILES',
    'TATASTEEL':'STEEL','TCS':'SOFTWARE','TECHM':'SOFTWARE','TITAN':'RETAILING',
    'TRENT':'RETAILING','ULTRACEMCO':'CEMENT','WIPRO':'SOFTWARE'
}

COMPANY_MAP = {
    'ADANIGREEN':'ADANI ENTERPRISES','ADANIPORTS':'ADANI PORTS & SEZ',
    'AIRTEL':'BHARTI AIRTEL','APOLLOHOSP':'APOLLO HOSPITALS',
    'ASIANPAINT':'ASIAN PAINTS','AXISBANK':'AXIS BANK',
    'BAJAJ-AUTO':'BAJAJ AUTO','BAJAJFINSV':'BAJAJ FINSERV',
    'BAJFINANCE':'BAJAJ FINANCE','BEL':'BHARAT ELECTRONICS',
    'BPCL':'BPCL','BRITANNIA':'BRITANNIA','CIPLA':'CIPLA',
    'COALINDIA':'COAL INDIA','DRREDDY':'DR REDDYS','EICHERMOT':'EICHER MOTORS',
    'GRASIM':'GRASIM','HCLTECH':'HCL TECH','HDFCBANK':'HDFC BANK',
    'HDFCLIFE':'HDFC LIFE','HEROMOTOCO':'HERO MOTOCORP','HINDALCO':'HINDALCO',
    'HINDUNILVR':'HINDUSTAN UNILEVER','ICICIBANK':'ICICI BANK',
    'INDUSINDBK':'INDUSIND BANK','INFY':'INFOSYS','IOC':'IOC','ITC':'ITC',
    'JSWSTEEL':'JSW STEEL','KOTAKBANK':'KOTAK BANK','LT':'L&T',
    'M&M':'MAHINDRA & MAHINDRA','MARUTI':'MARUTI SUZUKI','NESTLEIND':'NESTLE',
    'NTPC':'NTPC','ONGC':'ONGC','POWERGRID':'POWER GRID','RELIANCE':'RELIANCE',
    'SBILIFE':'SBI LIFE','SBIN':'STATE BANK OF INDIA','SHRIRAMFIN':'SHRIRAM FINANCE',
    'SUNPHARMA':'SUN PHARMA','TATACONSUMER':'TATA CONSUMER','TATAMOTORS':'TATA MOTORS',
    'TATASTEEL':'TATA STEEL','TCS':'TCS','TECHM':'TECH MAHINDRA',
    'TITAN':'TITAN','TRENT':'TRENT','ULTRACEMCO':'ULTRATECH CEMENT','WIPRO':'WIPRO'
}


# ─── Load data ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    csv_dir = "stock_csvs"
    all_frames = []

    for fname in os.listdir(csv_dir):
        if not fname.endswith(".csv"):
            continue
        ticker = fname.replace(".csv", "")
        df = pd.read_csv(os.path.join(csv_dir, fname), parse_dates=["date"])
        df["ticker"]  = ticker
        df["sector"]  = SECTOR_MAP.get(ticker, "OTHER")
        df["company"] = COMPANY_MAP.get(ticker, ticker)
        all_frames.append(df)

    master = pd.concat(all_frames, ignore_index=True)
    master = master.sort_values(["ticker", "date"]).reset_index(drop=True)
    return master


# ─── Helper calculations ───────────────────────────────────────────────────────

def get_yearly_returns(master):
    returns = master.groupby(["ticker", "sector", "company"]).agg(
        first_close=("close", "first"),
        last_close=("close", "last")
    ).reset_index()
    returns["yearly_return_%"] = (
        (returns["last_close"] - returns["first_close"])
        / returns["first_close"] * 100
    ).round(2)
    return returns.sort_values("yearly_return_%", ascending=False).reset_index(drop=True)


def get_volatility(master):
    master = master.copy()
    master["daily_return"] = master.groupby("ticker")["close"].pct_change() * 100
    vol = master.groupby("ticker")["daily_return"].std().round(4).reset_index()
    vol.columns = ["ticker", "volatility_%"]
    return vol.sort_values("volatility_%", ascending=False).reset_index(drop=True)


def get_monthly_returns(master):
    monthly = master.groupby(["ticker", "month"]).agg(
        first_close=("close", "first"),
        last_close=("close", "last")
    ).reset_index()
    monthly["monthly_return_%"] = (
        (monthly["last_close"] - monthly["first_close"])
        / monthly["first_close"] * 100
    ).round(2)
    return monthly


# ─── Main app ──────────────────────────────────────────────────────────────────

def main():

    master = load_data()

    # Pre-compute all analysis
    returns  = get_yearly_returns(master)
    vol      = get_volatility(master)
    monthly  = get_monthly_returns(master)

    # ── Header ────────────────────────────────────────────────────────────────
    st.title("📈 Nifty 50 Stock Analysis Dashboard")
    st.caption("Data: Oct 2023 – Nov 2024  |  50 Nifty stocks  |  284 trading days")
    st.markdown("---")

    # ── Market Summary KPIs ────────────────────────────────────────────────────
    st.subheader("Market Summary")

    best   = returns.iloc[0]
    worst  = returns.iloc[-1]
    avg_r  = returns["yearly_return_%"].mean()
    greens = (returns["yearly_return_%"] > 0).sum()
    reds   = (returns["yearly_return_%"] < 0).sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Stocks",       "50")
    k2.metric("Avg Yearly Return",  f"{avg_r:.1f}%")
    k3.metric("Green Stocks",       f"{greens} stocks")
    k4.metric("Best Stock",         best["ticker"],  f"+{best['yearly_return_%']:.1f}%")
    k5.metric("Worst Stock",        worst["ticker"], f"{worst['yearly_return_%']:.1f}%")

    st.markdown("---")

    # ── Sidebar filters ───────────────────────────────────────────────────────
    st.sidebar.title("Filters")
    st.sidebar.markdown("Use these filters to explore specific stocks or sectors.")

    all_sectors = sorted(master["sector"].unique())
    sel_sector  = st.sidebar.selectbox("Filter by Sector", ["All Sectors"] + all_sectors)

    all_tickers = sorted(master["ticker"].unique())
    sel_ticker  = st.sidebar.selectbox("Select Stock (for price chart)", all_tickers, index=all_tickers.index("TCS"))

    st.sidebar.markdown("---")
    st.sidebar.markdown("**About this dashboard**")
    st.sidebar.markdown("Built as part of GUVI Data-Driven Stock Analysis project using pandas, matplotlib and streamlit.")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Green & Red Stocks",
        "⚡ Volatility",
        "📈 Cumulative Return",
        "🏭 Sector Performance",
        "🔥 Correlation Heatmap",
        "📅 Monthly Gainers & Losers",
        "🔍 Stock Explorer"
    ])

    # ════════════════════════════════════════════════════════════════
    # TAB 1 — Top 10 Green & Red
    # ════════════════════════════════════════════════════════════════
    with tab1:
        st.subheader("Top 10 Green & Red Stocks (Yearly Return)")
        st.caption("Yearly return = (last closing price - first closing price) / first closing price × 100")

        data = returns if sel_sector == "All Sectors" else returns[returns["sector"] == sel_sector]

        top_green = data.head(10)
        top_red   = data.tail(10).sort_values("yearly_return_%", ascending=True)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor="#f9f9f9")

        # Green
        bars1 = ax1.barh(top_green["ticker"], top_green["yearly_return_%"],
                          color="#2ecc71", edgecolor="white", height=0.6)
        ax1.set_title("Top 10 Best Performers", fontsize=11, fontweight="bold")
        ax1.set_xlabel("Yearly Return (%)")
        ax1.invert_yaxis()
        ax1.axvline(0, color="gray", linewidth=0.8, linestyle="--")
        ax1.spines[["top","right"]].set_visible(False)
        ax1.set_facecolor("#f9f9f9")
        for bar, val in zip(bars1, top_green["yearly_return_%"]):
            ax1.text(bar.get_width()+1, bar.get_y()+bar.get_height()/2,
                     f"+{val:.1f}%", va="center", ha="left", fontsize=8,
                     color="#27ae60", fontweight="bold")

        # Red
        bars2 = ax2.barh(top_red["ticker"], top_red["yearly_return_%"],
                          color="#e74c3c", edgecolor="white", height=0.6)
        ax2.set_title("Top 10 Worst Performers", fontsize=11, fontweight="bold")
        ax2.set_xlabel("Yearly Return (%)")
        ax2.invert_yaxis()
        ax2.axvline(0, color="gray", linewidth=0.8, linestyle="--")
        ax2.spines[["top","right"]].set_visible(False)
        ax2.set_facecolor("#f9f9f9")
        for bar, val in zip(bars2, top_red["yearly_return_%"]):
            ax2.text(bar.get_width()-1, bar.get_y()+bar.get_height()/2,
                     f"{val:.1f}%", va="center", ha="right", fontsize=8,
                     color="#c0392b", fontweight="bold")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        st.dataframe(
            returns[["ticker","company","sector","yearly_return_%"]].rename(
                columns={"yearly_return_%":"Yearly Return (%)"}),
            use_container_width=True, hide_index=True
        )

    # ════════════════════════════════════════════════════════════════
    # TAB 2 — Volatility
    # ════════════════════════════════════════════════════════════════
    with tab2:
        st.subheader("Volatility Analysis — Top 10 Most Volatile Stocks")
        st.caption("Volatility = standard deviation of daily returns. Higher = more risky.")

        top10_vol = vol.head(10).sort_values("volatility_%", ascending=True)
        colors    = plt.cm.Oranges([0.4 + 0.06*i for i in range(len(top10_vol))])

        fig, ax = plt.subplots(figsize=(10, 6), facecolor="#f9f9f9")
        bars = ax.barh(top10_vol["ticker"], top10_vol["volatility_%"],
                        color=colors, edgecolor="white", height=0.6)
        ax.set_title("Top 10 Most Volatile Nifty 50 Stocks", fontsize=12, fontweight="bold")
        ax.set_xlabel("Volatility (Std Dev of Daily Returns %)")
        ax.spines[["top","right"]].set_visible(False)
        ax.set_facecolor("#f9f9f9")
        for bar, val in zip(bars, top10_vol["volatility_%"]):
            ax.text(bar.get_width()+0.02, bar.get_y()+bar.get_height()/2,
                     f"{val:.4f}%", va="center", ha="left", fontsize=9,
                     fontweight="bold", color="#7f3b00")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        st.dataframe(
            vol.rename(columns={"volatility_%":"Volatility (%)"}),
            use_container_width=True, hide_index=True
        )

    # ════════════════════════════════════════════════════════════════
    # TAB 3 — Cumulative Return
    # ════════════════════════════════════════════════════════════════
    with tab3:
        st.subheader("Cumulative Return Over Time")
        st.caption("Shows how selected stocks grew from day 1 to the last trading day.")

        top5_default = returns.head(5)["ticker"].tolist()
        sel_stocks   = st.multiselect(
            "Select stocks to compare (up to 5):",
            options=all_tickers,
            default=top5_default,
            max_selections=5
        )

        if sel_stocks:
            colors_list = ["#e74c3c","#2ecc71","#3498db","#f39c12","#9b59b6"]
            fig, ax = plt.subplots(figsize=(13, 6), facecolor="#f9f9f9")

            for idx, ticker in enumerate(sel_stocks):
                stock = master[master["ticker"] == ticker].copy()
                stock["daily_return"]      = stock["close"].pct_change()
                stock["cumulative_return"] = (1 + stock["daily_return"]).cumprod() - 1
                stock["cumulative_return"] = stock["cumulative_return"] * 100
                stock = stock.dropna(subset=["cumulative_return"])
                final = stock["cumulative_return"].iloc[-1]
                color = colors_list[idx % len(colors_list)]
                ax.plot(stock["date"], stock["cumulative_return"],
                        label=f"{ticker} ({final:+.1f}%)", color=color, linewidth=2)
                ax.scatter(stock["date"].iloc[-1], final, color=color, s=50, zorder=5)

            ax.axhline(0, color="gray", linewidth=1, linestyle="--", alpha=0.6)
            ax.set_title("Cumulative Return Over Time", fontsize=12, fontweight="bold")
            ax.set_xlabel("Date")
            ax.set_ylabel("Cumulative Return (%)")
            ax.spines[["top","right"]].set_visible(False)
            ax.set_facecolor("#f9f9f9")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.xticks(rotation=45)
            ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
            ax.legend(title="Stock (Total Return)", fontsize=9)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    # ════════════════════════════════════════════════════════════════
    # TAB 4 — Sector Performance
    # ════════════════════════════════════════════════════════════════
    with tab4:
        st.subheader("Sector-wise Average Yearly Return")
        st.caption("Average yearly return of all stocks within each sector.")

        sector_perf = returns.groupby("sector")["yearly_return_%"].mean().round(2).reset_index()
        sector_perf.columns = ["sector", "avg_return_%"]
        sector_perf = sector_perf.sort_values("avg_return_%", ascending=True)

        colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in sector_perf["avg_return_%"]]

        fig, ax = plt.subplots(figsize=(11, 8), facecolor="#f9f9f9")
        bars = ax.barh(sector_perf["sector"], sector_perf["avg_return_%"],
                        color=colors, edgecolor="white", height=0.65)
        ax.axvline(0, color="gray", linewidth=1, linestyle="--", alpha=0.7)
        ax.set_title("Sector-wise Average Yearly Return", fontsize=12, fontweight="bold")
        ax.set_xlabel("Average Yearly Return (%)")
        ax.spines[["top","right"]].set_visible(False)
        ax.set_facecolor("#f9f9f9")
        ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
        for bar, val in zip(bars, sector_perf["avg_return_%"]):
            offset = 1 if val >= 0 else -1
            ha     = "left" if val >= 0 else "right"
            color  = "#27ae60" if val >= 0 else "#c0392b"
            ax.text(bar.get_width()+offset, bar.get_y()+bar.get_height()/2,
                     f"{val:+.1f}%", va="center", ha=ha, fontsize=9,
                     fontweight="bold", color=color)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        st.dataframe(
            sector_perf.sort_values("avg_return_%", ascending=False).rename(
                columns={"avg_return_%":"Avg Yearly Return (%)"}),
            use_container_width=True, hide_index=True
        )

    # ════════════════════════════════════════════════════════════════
    # TAB 5 — Correlation Heatmap
    # ════════════════════════════════════════════════════════════════
    with tab5:
        st.subheader("Stock Price Correlation Heatmap")
        st.caption("How closely do stocks move together? +1 = always together, -1 = always opposite.")

        price_matrix = master.pivot_table(index="date", columns="ticker", values="close")
        corr         = price_matrix.corr()

        fig, ax = plt.subplots(figsize=(20, 16), facecolor="white")
        im = ax.imshow(corr.values, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
        tickers_list = corr.columns.tolist()
        ax.set_xticks(range(len(tickers_list)))
        ax.set_yticks(range(len(tickers_list)))
        ax.set_xticklabels(tickers_list, rotation=90, fontsize=6.5)
        ax.set_yticklabels(tickers_list, fontsize=6.5)
        for i in range(len(tickers_list)):
            for j in range(len(tickers_list)):
                val = corr.values[i, j]
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=5, color="white" if abs(val) > 0.7 else "black")
        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label("Correlation Coefficient", fontsize=10)
        ax.set_title("Nifty 50 Stock Price Correlation Heatmap", fontsize=13, fontweight="bold", pad=15)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # ════════════════════════════════════════════════════════════════
    # TAB 6 — Monthly Gainers & Losers
    # ════════════════════════════════════════════════════════════════
    with tab6:
        st.subheader("Monthly Top 5 Gainers & Losers")

        all_months  = sorted(monthly["month"].unique())
        month_labels = [pd.to_datetime(m+"-01").strftime("%B %Y") for m in all_months]
        month_choice = st.selectbox("Select Month", month_labels)
        sel_month    = all_months[month_labels.index(month_choice)]

        month_data  = monthly[monthly["month"] == sel_month].sort_values("monthly_return_%", ascending=False)
        top5_gain   = month_data.head(5)
        top5_loss   = month_data.tail(5).sort_values("monthly_return_%", ascending=True)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), facecolor="#f9f9f9")
        fig.suptitle(f"Monthly Gainers & Losers — {month_choice}", fontsize=12, fontweight="bold")

        bars1 = ax1.barh(top5_gain["ticker"], top5_gain["monthly_return_%"],
                          color="#2ecc71", edgecolor="white", height=0.55)
        ax1.set_title("Top 5 Gainers", fontsize=10, fontweight="bold")
        ax1.set_xlabel("Monthly Return (%)")
        ax1.invert_yaxis()
        ax1.axvline(0, color="gray", linewidth=0.8, linestyle="--")
        ax1.spines[["top","right"]].set_visible(False)
        ax1.set_facecolor("#f9f9f9")
        for bar, val in zip(bars1, top5_gain["monthly_return_%"]):
            ax1.text(bar.get_width()+0.1, bar.get_y()+bar.get_height()/2,
                     f"+{val:.1f}%", va="center", ha="left", fontsize=8,
                     color="#27ae60", fontweight="bold")

        bars2 = ax2.barh(top5_loss["ticker"], top5_loss["monthly_return_%"],
                          color="#e74c3c", edgecolor="white", height=0.55)
        ax2.set_title("Top 5 Losers", fontsize=10, fontweight="bold")
        ax2.set_xlabel("Monthly Return (%)")
        ax2.invert_yaxis()
        ax2.axvline(0, color="gray", linewidth=0.8, linestyle="--")
        ax2.spines[["top","right"]].set_visible(False)
        ax2.set_facecolor("#f9f9f9")
        for bar, val in zip(bars2, top5_loss["monthly_return_%"]):
            ax2.text(bar.get_width()-0.1, bar.get_y()+bar.get_height()/2,
                     f"{val:.1f}%", va="center", ha="right", fontsize=8,
                     color="#c0392b", fontweight="bold")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # ════════════════════════════════════════════════════════════════
    # TAB 7 — Stock Explorer
    # ════════════════════════════════════════════════════════════════
    with tab7:
        st.subheader(f"Stock Explorer — {sel_ticker}")

        stock_data = master[master["ticker"] == sel_ticker].copy()
        stock_ret  = returns[returns["ticker"] == sel_ticker].iloc[0]
        stock_vol  = vol[vol["ticker"] == sel_ticker].iloc[0]

        # KPIs
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Company",       COMPANY_MAP.get(sel_ticker, sel_ticker))
        c2.metric("Sector",        SECTOR_MAP.get(sel_ticker, "N/A"))
        c3.metric("Yearly Return", f"{stock_ret['yearly_return_%']:+.2f}%")
        c4.metric("Volatility",    f"{stock_vol['volatility_%']:.4f}%")

        # Price chart
        fig, ax = plt.subplots(figsize=(13, 5), facecolor="#f9f9f9")
        ax.plot(stock_data["date"], stock_data["close"],
                color="#3498db", linewidth=1.8, label="Close Price")
        ax.fill_between(stock_data["date"], stock_data["close"],
                         stock_data["close"].min(), alpha=0.08, color="#3498db")
        ax.set_title(f"{sel_ticker} — Closing Price History", fontsize=12, fontweight="bold")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price (₹)")
        ax.spines[["top","right"]].set_visible(False)
        ax.set_facecolor("#f9f9f9")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        st.dataframe(
            stock_data[["date","open","high","low","close","volume"]].sort_values("date", ascending=False),
            use_container_width=True, hide_index=True
        )


if __name__ == "__main__":
    main()
