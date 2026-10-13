
from pathlib import Path

import joblib
import pandas as pd

from validate_invoice import validate_invoice


# Locate saved model files
BASE_DIR = Path(__file__).parent

MODEL_PATH = BASE_DIR / "isolation_forest_model.pkl"
SCALER_PATH = BASE_DIR / "scaler.pkl"

FEATURES = [
    "taxable_amount",
    "gst_rate_percent",
    "cgst",
    "sgst",
    "igst",
    "total_gst",
    "total_amount",
]


def detect_anomaly(invoice):
    """
    Combine rule-based invoice validation with Isolation Forest.
    """

    # 1. Validate invoice calculations
    validation_result = validate_invoice(invoice)

    # 2. Check required ML features
    missing_fields = [
        field for field in FEATURES
        if field not in invoice
    ]

    if missing_fields:
        return {
            "status": "Invalid Input",
            "is_valid": False,
            "ml_prediction": "Not evaluated",
            "issues": validation_result["issues"],
            "error": "Missing ML features: " + ", ".join(missing_fields),
        }

    try:
        # 3. Convert input into the same feature order used for training
        row = pd.DataFrame(
            [[float(invoice[field]) for field in FEATURES]],
            columns=FEATURES,
        )

        # 4. Load the trained model and scaler
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)

        # 5. Scale and predict
        scaled_row = scaler.transform(row)
        prediction = model.predict(scaled_row)[0]

        ml_prediction = (
            "Anomaly" if prediction == -1 else "Normal"
        )

        # 6. Combine ML prediction and validation results
        flagged = (
            not validation_result["is_valid"]
            or prediction == -1
        )

        reasons = list(validation_result["issues"])

        if prediction == -1:
            reasons.append(
                "Isolation Forest identified an unusual numerical pattern"
            )

        return {
            "status": "Flagged for Review" if flagged else "Normal",
            "is_valid": validation_result["is_valid"],
            "ml_prediction": ml_prediction,
            "issue_count": len(reasons),
            "issues": reasons,
        }

    except (ValueError, TypeError, KeyError) as error:
        return {
            "status": "Invalid Input",
            "is_valid": False,
            "ml_prediction": "Not evaluated",
            "issues": validation_result["issues"],
            "error": str(error),
        }
