import pandas as pd
import numpy as np

# =========================
# CONFIG
# =========================
CSV_PATH = "D:\\chrome_downloads\\transactions_2023_2025.csv"   # <-- change this
DATE_COLUMN = "transaction_date"
AMOUNT_COLUMN = "amount"
TYPE_COLUMN = "type"  # expects 'income' or 'expense'

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(CSV_PATH)

# Convert date column
df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])

# Create month column
df["month"] = df[DATE_COLUMN].dt.to_period("M")

# =========================
# MONTHLY AGGREGATION
# =========================
monthly = (
    df.groupby(["month", TYPE_COLUMN])[AMOUNT_COLUMN]
    .sum()
    .unstack(fill_value=0)
    .reset_index()
)

monthly["month"] = monthly["month"].astype(str)

# Ensure both columns exist
if "income" not in monthly.columns:
    monthly["income"] = 0.0
if "expense" not in monthly.columns:
    monthly["expense"] = 0.0

monthly = monthly.sort_values("month")

# =========================
# BASIC INFO
# =========================
print("Total Months:", len(monthly))
print("Date Range:", monthly["month"].min(), "to", monthly["month"].max())
print("-" * 50)

# =========================
# SPIKE DETECTION FUNCTION
# =========================
def detect_spikes(series, label):
    mean = series.mean()
    std = series.std()
    threshold = mean + 1.5 * std  # spike threshold
    
    spikes = monthly[series > threshold]["month"].tolist()
    
    spike_month_numbers = [int(m.split("-")[1]) for m in spikes]
    
    print(f"{label} Mean:", round(mean, 2))
    print(f"{label} Std Dev:", round(std, 2))
    print(f"{label} Spike Months:", spikes)
    
    if len(spike_month_numbers) > 0:
        same_month_pattern = len(set(spike_month_numbers)) == 1
        print(f"{label} Spikes Same Calendar Month Each Year?:", same_month_pattern)
    else:
        print(f"{label} No significant spikes detected.")
    
    print("-" * 50)


# =========================
# RUN ANALYSIS
# =========================
detect_spikes(monthly["income"], "Income")
detect_spikes(monthly["expense"], "Expense")