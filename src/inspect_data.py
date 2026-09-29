import pandas as pd
import os

# Path to your cleaned dataset
file_path = r"D:\Food_Delivery_BigData_Analytics\data\cleaned\food_delivery_cleaned.csv"

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    
    print("=== 1. EXACT COLUMN NAMES (35 columns) ===")
    print(df.columns.tolist())
    
    print("\n=== 2. DATA TYPES & NON-NULL COUNTS ===")
    print(df.dtypes)
    
    print("\n=== 3. TARGET VARIABLE CHECK (Looking for cancellation/status columns) ===")
    # Let's find any column with 'status', 'cancel', or 'order' in the name
    status_cols = [col for col in df.columns if 'status' in col.lower() or 'cancel' in col.lower()]
    for col in status_cols:
        print(f"\n--- {col} ---")
        print(df[col].value_counts(dropna=False))
        
    print("\n=== 4. SAMPLE DATA (First 2 rows) ===")
    # Transposed for easier reading in chat
    print(df.head(2).to_dict(orient='records'))
    
else:
    print(f"Error: File not found at {file_path}")