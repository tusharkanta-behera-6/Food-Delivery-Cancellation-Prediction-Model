import pandas as pd
import os

INPUT_FILE = "data/raw/food_delivery.csv"
OUTPUT_FILE = "data/cleaned/food_delivery_cleaned.csv"

# Load data
df = pd.read_csv(INPUT_FILE)
print("Original shape:", df.shape)

# Remove duplicate rows
df = df.drop_duplicates()

# Convert order date/time
df["Order Placed At"] = pd.to_datetime(df["Order Placed At"], errors="coerce")

# Create date/time features (Fixed trailing spaces)
df["Order_Date"] = df["Order Placed At"].dt.date
df["Order_Hour"] = df["Order Placed At"].dt.hour
df["Day"] = df["Order Placed At"].dt.day_name()
df["Month"] = df["Order Placed At"].dt.month_name()

# Create order period
def get_order_period(hour):
    if 6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 22:
        return "Evening"
    else:
        return "Night"

df["Order_Period"] = df["Order_Hour"].apply(get_order_period)

# Convert Distance
df["Distance_km"] = (
    df["Distance"]
    .astype(str)
    .str.replace("km", "", regex=False)
    .str.replace("<1", "0.5", regex=False)
)
df["Distance_km"] = pd.to_numeric(df["Distance_km"], errors="coerce")

# Numeric columns
numeric_columns = [
    "Bill subtotal",
    "Packaging charges",
    "Total",
    "KPT duration (minutes)",
    "Rider wait time (minutes)"
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

# Create cleaned folder if required
os.makedirs("data/cleaned", exist_ok=True)

# Save
df.to_csv(OUTPUT_FILE, index=False)
print("Cleaned shape:", df.shape)
print("Cleaned dataset saved to:", OUTPUT_FILE)