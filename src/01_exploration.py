import pandas as pd

# Load the dataset
df = pd.read_csv("data/raw/food_delivery.csv")

print("=" * 50)
print("FOOD DELIVERY DATASET")
print("=" * 50)
print("Number of rows:", df.shape[0])
print("Number of columns:", df.shape[1])

print("\nColumn Names:")
print(df.columns.tolist())

print("\nFirst 5 Records:")
print(df.head())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Records:")
print(df.duplicated().sum())