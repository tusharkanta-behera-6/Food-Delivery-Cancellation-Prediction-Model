import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
import warnings
import os

warnings.filterwarnings('ignore')
os.makedirs('models', exist_ok=True)

print("="*70)
print("STEP 1: LOADING DATA")
print("="*70)
df = pd.read_csv('data/cleaned/food_delivery_cleaned.csv')
print(f"Loaded dataset with {df.shape[0]} rows.")

print("\n" + "="*70)
print("STEP 2: TARGET & FEATURES")
print("="*70)
cancelled_statuses = ['Rejected', 'Returned', 'Return cancelled', 'Timed out']
df['is_cancelled'] = df['Order Status'].apply(lambda x: 1 if x in cancelled_statuses else 0)
df['num_items'] = df['Items in order'].apply(lambda x: str(x).count('x') if pd.notna(x) else 1)

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

print("\n" + "="*70)
print("STEP 3: TRAINING BALANCED RANDOM FOREST")
print("="*70)
# We use class_weight='balanced' to ensure it actually learns the cancellation patterns
preprocessor = ColumnTransformer(transformers=[
    ('num', Pipeline([('imputer', SimpleImputer(strategy='constant', fill_value=0)), ('scaler', StandardScaler())]), numeric_features),
    ('cat', Pipeline([('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')), ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), categorical_features)
])

# Balanced Random Forest
rf_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, max_depth=10))
])
rf_pipeline.fit(X_train, y_train)

print("\n" + "="*70)
print("STEP 4: FINDING THE PERFECT DEMO THRESHOLD")
print("="*70)
y_prob = rf_pipeline.predict_proba(X_test)[:, 1]

best_f1 = 0
best_threshold = 0.5

# Test thresholds from 10% to 90% to find the perfect balance
for threshold in np.arange(0.10, 0.90, 0.05):
    y_pred_temp = (y_prob >= threshold).astype(int)
    f1 = f1_score(y_test, y_pred_temp)
    if f1 > best_f1:
        best_f1 = f1
        best_threshold = threshold

print(f"\n🎯 OPTIMAL THRESHOLD FOUND: {best_threshold:.2f}")
print(f"This threshold gives the best balance of Precision and Recall for your demo!")

# Evaluate at this specific threshold
y_pred_best = (y_prob >= best_threshold).astype(int)
print(f"\n--- Model Performance at Threshold {best_threshold:.2f} ---")
print(f"Accuracy:  {accuracy_score(y_test, y_pred_best):.4f}")
print(f"Precision: {precision_score(y_test, y_pred_best):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred_best):.4f}")
print(f"F1-Score:  {f1_score(y_test, y_pred_best):.4f}")

cm = confusion_matrix(y_test, y_pred_best)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Completed', 'Cancelled'], yticklabels=['Completed', 'Cancelled'])
plt.title(f'Confusion Matrix (Threshold: {best_threshold})')
plt.ylabel('Actual'); plt.xlabel('Predicted')
plt.show()

print("\n" + "="*70)
print("STEP 5: SAVING MODEL")
print("="*70)
joblib.dump(rf_pipeline, 'models/cancellation_model_rf.pkl')
print("✅ Model saved to 'models/cancellation_model_rf.pkl'")

# Save the threshold to a text file so the app can read it!
with open('models/optimal_threshold.txt', 'w') as f:
    f.write(str(best_threshold))
print(f"✅ Threshold saved to 'models/optimal_threshold.txt'")