
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. Define file paths
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "synthetic_invoices.csv"
MODEL_PATH = BASE_DIR / "isolation_forest_model.pkl"
SCALER_PATH = BASE_DIR / "scaler.pkl"

# 2. Load the dataset
df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)

# 3. Select numerical features
# Do not use synthetic labels or anomaly reasons for training.
features = [
    "taxable_amount",
    "gst_rate_percent",
    "cgst",
    "sgst",
    "igst",
    "total_gst",
    "total_amount",
]

X = df[features].copy()
y = df["is_synthetic_anomaly"].astype(int)

# 4. Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y,
)

# 5. Scale numerical features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 6. Train Isolation Forest
model = IsolationForest(
    n_estimators=200,
    contamination=0.075,
    random_state=42,
)

model.fit(X_train_scaled)

# 7. Predict anomalies in the test set
# Isolation Forest: -1 = anomaly, 1 = normal
predictions = model.predict(X_test_scaled)
y_pred = (predictions == -1).astype(int)

# 8. Evaluate the model against synthetic labels
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred, labels=[0, 1]))

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        labels=[0, 1],
        target_names=["Normal", "Anomaly"],
        zero_division=0,
    )
)

# 9. Save the trained model and scaler
joblib.dump(model, MODEL_PATH)
joblib.dump(scaler, SCALER_PATH)

print("\nModel saved to:", MODEL_PATH)
print("Scaler saved to:", SCALER_PATH)
print("\nTraining completed successfully!")
