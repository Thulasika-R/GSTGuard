
from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# Make the ml folder importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ML_DIR = PROJECT_ROOT / "ml"

sys.path.insert(0, str(ML_DIR))

from detect_anomaly import detect_anomaly


app = FastAPI(
    title="GSTGuard API",
    description="GST invoice anomaly detection for MSME compliance",
    version="1.0.0",
)

# Development configuration.
# Restrict origins to your actual frontend URL before deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class InvoiceRequest(BaseModel):
    taxable_amount: float = Field(ge=0)
    gst_rate_percent: float = Field(ge=0, le=100)
    transaction_type: str

    cgst: float = Field(ge=0)
    sgst: float = Field(ge=0)
    igst: float = Field(ge=0)
    total_gst: float = Field(ge=0)
    total_amount: float = Field(ge=0)


@app.get("/")
def home():
    return {
        "message": "Welcome to GSTGuard API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/predict")
def predict_invoice(invoice: InvoiceRequest):
    try:
        result = detect_anomaly(invoice.model_dump())
        return result
    except Exception as exc:
        # Log the detailed error locally; avoid exposing internals to clients.
        print(f"Invoice prediction failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Invoice analysis failed. Check the backend logs.",
        ) from exc
