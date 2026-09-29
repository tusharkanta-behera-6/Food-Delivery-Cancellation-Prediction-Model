import pandas as pd
import joblib

print("Loading data and model...")
# 1. Load your cleaned data and the trained model
df = pd.read_csv('data/cleaned/food_delivery_cleaned.csv')
model = joblib.load('models/cancellation_model_rf.pkl')

print("Calculating risk for all 21,321 orders...")

# 2. Feature Engineering (must match training script exactly)
df['num_items'] = df['Items in order'].apply(lambda x: str(x).count('x') if pd.notna(x) else 1)

# 3. Select the exact features the model was trained on
features = [
    'Restaurant name', 'Subzone', 'City', 'Delivery', 'Distance_km', 
    'Order_Hour', 'Order_Period', 'Day', 'Month', 'num_items', 
    'Bill subtotal', 'Packaging charges', 'Restaurant discount (Promo)', 
    'Restaurant discount (Flat offs, Freebies & others)', 'Gold discount', 
    'Brand pack discount', 'KPT duration (minutes)', 'Rider wait time (minutes)'
]

# Keep only columns that exist in the dataframe
existing_features = [f for f in features if f in df.columns]
X = df[existing_features]

# 4. Predict the probability of cancellation (Class 1)
probabilities = model.predict_proba(X)[:, 1] * 100
df['Cancellation_Risk_%'] = probabilities

# 5. Sort to find the absolute highest risk orders in your data
top_risky = df.sort_values(by='Cancellation_Risk_%', ascending=False).head(10)

print("\n" + "="*80)
print("🚨 TOP 10 HIGHEST RISK ORDERS IN YOUR DATASET 🚨")
print("="*80)

# Show the most important columns to understand WHY they are high risk
cols_to_show = [
    'Order ID', 'Restaurant name', 'Distance_km', 'KPT duration (minutes)', 
    'Rider wait time (minutes)', 'Order_Hour', 'Order Status', 'Cancellation_Risk_%'
]

print(top_risky[cols_to_show].to_string(index=False))
print("="*80)
print("\n💡 TIP: Plug these exact numbers into your Streamlit app to naturally trigger the HIGH RISK alert!")