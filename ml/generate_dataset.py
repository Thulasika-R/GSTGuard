
from pathlib import Path

import numpy as np
import pandas as pd

# Reproducible synthetic data
rng = np.random.default_rng(42)

OUTPUT_PATH = Path(__file__).parent / "data" / "synthetic_invoices.csv"

num_shops = 12
invoices_per_shop = 100

gst_rates = [5, 12, 18, 28]
rows = []

for shop_num in range(1, num_shops + 1):
    shop_id = f"SHOP{shop_num:03d}"

    # Each shop has its own typical invoice amount.
    shop_average = rng.uniform(3000, 25000)

    for invoice_num in range(1, invoices_per_shop + 1):
        invoice_date = (
            pd.Timestamp("2026-01-01")
            + pd.Timedelta(days=int(rng.integers(0, 270)))
        )

        # Most invoices follow the shop's usual spending pattern.
        taxable_amount = float(
            rng.lognormal(
                mean=np.log(shop_average),
                sigma=0.35
            )
        )
        taxable_amount = round(taxable_amount, 2)

        gst_rate = int(rng.choice(gst_rates))
        transaction_type = str(
            rng.choice(["INTRA_STATE", "INTER_STATE"])
        )

        is_anomaly = False
        anomaly_reason = "Normal synthetic invoice"

        # Introduce occasional unusual examples for testing.
        if rng.random() < 0.08:
            is_anomaly = True
            anomaly_type = str(
                rng.choice([
                    "unusual_amount",
                    "tax_mismatch",
                    "amount_and_tax_mismatch"
                ])
            )

            if anomaly_type in [
                "unusual_amount",
                "amount_and_tax_mismatch"
            ]:
                taxable_amount = round(
                    taxable_amount * float(rng.uniform(5, 10)), 2
                )
                anomaly_reason = "Unusually high invoice amount"

            if anomaly_type in [
                "tax_mismatch",
                "amount_and_tax_mismatch"
            ]:
                anomaly_reason = (
                    "Unusually high invoice amount with tax mismatch"
                    if anomaly_type == "amount_and_tax_mismatch"
                    else "GST components do not match expected tax"
                )

        expected_tax = round(taxable_amount * gst_rate / 100, 2)

        if transaction_type == "INTRA_STATE":
            cgst = round(expected_tax / 2, 2)
            sgst = round(expected_tax - cgst, 2)
            igst = 0.0
        else:
            cgst = 0.0
            sgst = 0.0
            igst = expected_tax

        # Deliberately introduce an incorrect tax component in some records.
        if is_anomaly and anomaly_type in [
    "tax_mismatch",
    "amount_and_tax_mismatch"
]:
            if transaction_type == "INTRA_STATE":
                cgst = round(cgst * 1.8, 2)
            else:
                igst = round(igst * 1.8, 2)

        total_gst = round(cgst + sgst + igst, 2)
        total_amount = round(taxable_amount + total_gst, 2)

        rows.append({
            "shop_id": shop_id,
            "invoice_number": (
                f"{shop_id}-INV{invoice_num:04d}"
            ),
            "invoice_date": invoice_date.strftime("%Y-%m-%d"),
            "supplier_name": f"Supplier {shop_num:03d}",
            "supplier_gstin": (
                f"GSTTEST{shop_num:03d}"
            ),
            "buyer_gstin": f"BUYERTEST{shop_num:03d}",
            "taxable_amount": taxable_amount,
            "gst_rate_percent": gst_rate,
            "transaction_type": transaction_type,
            "cgst": cgst,
            "sgst": sgst,
            "igst": igst,
            "total_gst": total_gst,
            "total_amount": total_amount,
            "is_synthetic_anomaly": int(is_anomaly),
            "synthetic_anomaly_reason": anomaly_reason,
        })

df = pd.DataFrame(rows)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

print("Synthetic GST invoice dataset created!")
print(f"File location: {OUTPUT_PATH}")
print(f"Total invoices: {len(df)}")
print(f"Number of shops: {df['shop_id'].nunique()}")
print(
    "Synthetic anomaly examples:",
    int(df["is_synthetic_anomaly"].sum())
)
print("\nFirst five records:")
print(df.head().to_string(index=False))
