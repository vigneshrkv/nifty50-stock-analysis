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

monthly = master.groupby(["ticker","month"]).agg(
    first_close=("close","first"),
    last_close=("close","last")
).reset_index()

monthly["monthly_return_%"] = (
    (monthly["last_close"] - monthly["first_close"])
    / monthly["first_close"] * 100
).round(2)

monthly.to_csv("monthly_returns.csv", index=False)
print("Saved monthly_returns.csv")
print(monthly.head(10).to_string(index=False))