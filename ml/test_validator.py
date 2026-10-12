
from validate_invoice import validate_invoice


# Test 1: A mathematically consistent intra-state invoice
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

# Test 2: An invoice with an incorrect GST total
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
print(validate_invoice(normal_invoice))

print("\nSUSPICIOUS INVOICE")
print(validate_invoice(suspicious_invoice))
