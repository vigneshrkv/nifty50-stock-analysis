# Nifty 50 — Data Driven Stock Analysis

> **GUVI Capstone Project**
> Domain: Data Analysis / Python / SQL / Dashboard
> Skills: Python · Pandas · Matplotlib · MySQL · Streamlit · Power BI

---

## Project Overview

The Nifty 50 is India's benchmark stock market index representing the top 50 companies listed on the National Stock Exchange (NSE). Understanding how these stocks perform over time is critical for investors, analysts, and financial institutions.

This project performs an **end-to-end data analysis** on all 50 Nifty stocks covering **14 months of daily trading data (Oct 2023 – Nov 2024)**. It extracts raw YAML data, cleans and loads it into MySQL, performs 6 analytical tasks with visualizations, and presents everything in both a **Streamlit web dashboard** and a **Power BI dashboard**.

---

## Project Structure

```
II Project/
│
├── extract.py                      # Phase 1: Extract YAML → 50 CSVs
├── load_to_mysql.py                # Phase 2: Clean & load into MySQL
│
├── task1_top_stocks.py             # Top 10 Green & Red Stocks
├── task2_volatility.py             # Volatility Analysis
├── task3_cumulative_return.py      # Cumulative Return Over Time
├── task4_sector_performance.py     # Sector-wise Performance
├── task5_correlation_heatmap.py    # Correlation Heatmap
├── task6_monthly_gainers_losers.py # Monthly Gainers & Losers
│
├── dashboard.py                    # Streamlit Dashboard
├── Nifty50_Dashboard.pbix          # Power BI Dashboard
│
├── raw_yaml/                       # 284 raw YAML files
├── stock_csvs/                     # 50 individual stock CSVs
├── sector_performance.csv          # Sector summary (for Power BI)
├── monthly_returns.csv             # Monthly returns (for Power BI)
│
└── README.md                       # Project documentation
```

---

## Dataset

| Dataset | Format | Records | Description |
|---|---|---|---|
| `data.rar` | YAML (284 files) | 14,200 rows | Daily OHLCV data for 50 Nifty stocks |
| `Sector_data - Sheet1.csv` | CSV | 50 rows | Sector mapping for all 50 stocks |

### Key Columns

| Column | Description |
|---|---|
| `date` | Trading date |
| `ticker` | Stock symbol (e.g. TCS, SBIN) |
| `company` | Full company name |
| `sector` | Industry sector (Banking, IT, FMCG etc.) |
| `open` | Opening price of the day (₹) |
| `high` | Highest price of the day (₹) |
| `low` | Lowest price of the day (₹) |
| `close` | Closing price of the day (₹) |
| `volume` | Number of shares traded |
| `month` | Month identifier (e.g. 2024-01) |

---

## Data Pipeline

### Phase 1 — Data Extraction (`extract.py`)
- Reads 284 YAML files from `raw_yaml/` folder
- Each file contains 50 stock entries for one trading day
- Groups records by ticker symbol
- Applies ticker name corrections for 3 mismatched symbols
- Saves 50 individual CSVs to `stock_csvs/` folder

### Phase 2 — Data Cleaning & MySQL (`load_to_mysql.py`)
- Reads all 50 CSVs
- Cleans data types, handles nulls, removes duplicates
- Merges sector information from `Sector_data - Sheet1.csv`
- Loads all 14,200 rows into MySQL (`stock_analysis` database)

---

## Analysis Tasks

### Task 1 — Top 10 Green & Red Stocks
Calculates yearly return for each stock using:
```
Yearly Return = (last close - first close) / first close × 100
```
Identifies the top 10 best and worst performing stocks over the full period.

### Task 2 — Volatility Analysis
Measures risk using standard deviation of daily returns:
```
Daily Return = (today close - yesterday close) / yesterday close × 100
Volatility   = std deviation of all daily returns
```
Higher volatility = more price swings = higher risk.

### Task 3 — Cumulative Return Over Time
Tracks how the top 5 stocks grew day by day using compounded returns:
```
Cumulative Return = (1+r1)(1+r2)(1+r3)... - 1
```
Plotted as a line chart showing growth from Day 1 to last trading day.

### Task 4 — Sector-wise Performance
Groups 50 stocks into 21 sectors and calculates average yearly return per sector. Identifies which industries performed best and worst overall.

### Task 5 — Correlation Heatmap
Builds a 50×50 correlation matrix of closing prices:
- **+1.0** = stocks always move together
- **0.0** = no relationship
- **-1.0** = stocks move in opposite directions

Useful for portfolio diversification analysis.

### Task 6 — Monthly Gainers & Losers
For each of the 14 months, identifies the top 5 gainers and top 5 losers based on monthly return. Generates 14 individual charts saved as PNG and PDF.

---

## Key Findings

| Insight | Finding |
|---|---|
| Best performing stock | TRENT (+223% yearly return) |
| Worst performing stock | INDUSINDBK (-30.46%) |
| Best performing sector | RETAILING (+113% avg return) |
| Worst performing sector | PAINTS (-21.94%) |
| Most volatile stock | ADANIGREEN (2.86% daily std dev) |
| Most stable stock | SUNPHARMA (1.17% daily std dev) |
| Most correlated pair | TRENT & AIRTEL (0.976) |
| Total trading days | 284 days (Oct 2023 – Nov 2024) |
| Green stocks | 47 out of 50 |
| Red stocks | 3 out of 50 |

---

## Dashboards

### Streamlit Dashboard (`dashboard.py`)
An interactive Python web app with 7 tabs:

| Tab | Content |
|---|---|
| 📊 Green & Red Stocks | Top 10 best and worst performers |
| ⚡ Volatility | Top 10 most volatile stocks |
| 📈 Cumulative Return | Multi-stock line chart with selector |
| 🏭 Sector Performance | All 21 sectors ranked by avg return |
| 🔥 Correlation Heatmap | Full 50×50 heatmap |
| 📅 Monthly Gainers & Losers | Month dropdown — top 5 each month |
| 🔍 Stock Explorer | Pick any stock — price history + KPIs |

### Power BI Dashboard (`Nifty50_Dashboard.pbix`)
Interactive dashboard with:
- Top 10 Green & Red Stocks bar chart
- Volatility top 10 bar chart
- Cumulative Return line chart
- Sector Performance bar chart
- Correlation Heatmap (image)
- Monthly Gainers & Losers with month slicer
- Sector slicer and ticker slicer

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3 |
| Data Manipulation | Pandas |
| Visualization | Matplotlib |
| Data Format | YAML → CSV |
| Database | MySQL + SQLAlchemy + PyMySQL |
| Web Dashboard | Streamlit |
| BI Dashboard | Microsoft Power BI |

---

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/vigneshrkv/nifty50-stock-analysis.git
cd nifty50-stock-analysis
```

### 2. Install dependencies
```bash
pip install pandas matplotlib pyyaml sqlalchemy pymysql streamlit
```

### 3. Extract data (Phase 1)
Place `data.rar` contents into `raw_yaml/` folder, then:
```bash
python extract.py
```

### 4. Load to MySQL (Phase 2)
Make sure MySQL is running, then:
```bash
python load_to_mysql.py
```

### 5. Run individual analysis tasks
```bash
python task1_top_stocks.py
python task2_volatility.py
python task3_cumulative_return.py
python task4_sector_performance.py
python task5_correlation_heatmap.py
python task6_monthly_gainers_losers.py
```

### 6. Launch Streamlit dashboard
```bash
streamlit run dashboard.py
```
Open browser at `http://localhost:8501`

---

## Database Schema

```
Database : stock_analysis
Table    : stock_analysis

Columns:
  date      DATETIME
  ticker    VARCHAR
  company   VARCHAR
  sector    VARCHAR
  open      FLOAT
  high      FLOAT
  low       FLOAT
  close     FLOAT
  volume    BIGINT
  month     VARCHAR
```

---

## Author

**Vignesh R K**
GUVI
