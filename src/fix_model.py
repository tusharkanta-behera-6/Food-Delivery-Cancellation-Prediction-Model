import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import os

print("Loading data...")
df = pd.read_csv('data/cleaned/food_delivery_cleaned.csv')

# Target
cancelled_statuses = ['Rejected', 'Returned', 'Return cancelled', 'Timed out']
df['is_cancelled'] = df['Order Status'].apply(lambda x: 1 if x in cancelled_statuses else 0)
df['num_items'] = df['Items in order'].apply(lambda x: str(x).count('x') if pd.notna(x) else 1)

# Features
leakage_cols = ['Order Status', 'Cancellation / Rejection reason', 'Restaurant compensation (Cancellation)', 
                'Restaurant penalty (Rejection)', 'Rating', 'Review', 'Customer complaint tag', 
                'Order Ready Marked', 'Order ID', 'Customer ID', 'Order Placed At', 'Order_Date', 'Instructions']
df_model = df.drop(columns=[col for col in leakage_cols if col in df.columns], errors='ignore')

X = df_model.drop(columns=['is_cancelled'])
y = df_model['is_cancelled']

numeric_features = ['Distance_km', 'Bill subtotal', 'Packaging charges', 'Restaurant discount (Promo)', 
                    'Restaurant discount (Flat offs, Freebies & others)', 'Gold discount', 'Brand pack discount', 
                    'Order_Hour', 'KPT duration (minutes)', 'Rider wait time (minutes)', 'num_items']
categorical_features = ['Restaurant name', 'Subzone', 'City', 'Delivery', 'Day', 'Month', 'Order_Period']

numeric_features = [col for col in numeric_features if col in X.columns]
categorical_features = [col for col in categorical_features if col in X.columns]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("Training model...")
preprocessor = ColumnTransformer(transformers=[
    ('num', Pipeline([('imputer', SimpleImputer(strategy='constant', fill_value=0)), ('scaler', StandardScaler())]), numeric_features),
    ('cat', Pipeline([('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')), ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), categorical_features)
])

rf_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, max_depth=10))
])
rf_pipeline.fit(X_train, y_train)

print("Saving model...")
os.makedirs('models', exist_ok=True)
joblib.dump(rf_pipeline, 'models/cancellation_model_rf.pkl')
print("✅ DONE! Model saved to models/cancellation_model_rf.pkl")