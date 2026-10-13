
from detect_anomaly import detect_anomaly


normal_invoice = {
    "taxable_amount": 10000,
    "gst_rate_percent": 18,
    "transaction_type": "intra-state",
    "cgst": 900,
    "sgst": 900,
    "igst": 0,
    "total_gst": 1800,
    "total_amount": 11800,
}

suspicious_invoice = {
    "taxable_amount": 10000,
    "gst_rate_percent": 18,
    "transaction_type": "intra-state",
    "cgst": 900,
    "sgst": 900,
    "igst": 0,
    "total_gst": 1500,
    "total_amount": 11500,
}

print("NORMAL INVOICE")
print(detect_anomaly(normal_invoice))

print("\nSUSPICIOUS INVOICE")
print(detect_anomaly(suspicious_invoice))
