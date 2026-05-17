import os
import pandas as pd

csv_dir = "stock_csvs"
all_frames = []

for fname in os.listdir(csv_dir):
    if fname.endswith(".csv"):
        ticker = fname.replace(".csv", "")
        df = pd.read_csv(os.path.join(csv_dir, fname), parse_dates=["date"])
        df["ticker"] = ticker
        all_frames.append(df)

master = pd.concat(all_frames, ignore_index=True).sort_values(["ticker","date"])

sector_map = {
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

master["sector"] = master["ticker"].map(sector_map)

returns = master.groupby(["ticker","sector"]).agg(
    first_close=("close","first"),
    last_close=("close","last")
).reset_index()

returns["yearly_return_%"] = (
    (returns["last_close"] - returns["first_close"]) 
    / returns["first_close"] * 100
).round(2)

sector_perf = returns.groupby("sector")["yearly_return_%"].mean().round(2).reset_index()
sector_perf.columns = ["sector", "avg_yearly_return_%"]
sector_perf = sector_perf.sort_values("avg_yearly_return_%", ascending=False)

sector_perf.to_csv("sector_performance.csv", index=False)
print(sector_perf.to_string(index=False))
print("\nSaved to sector_performance.csv")