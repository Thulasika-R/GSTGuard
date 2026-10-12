
import pandas as pd


def validate_invoice(invoice):
    """
    Validate invoice calculations and basic GST consistency.

    Parameters:
        invoice: Dictionary containing invoice details.

    Returns:
        Dictionary containing validation status and issues.
    """

    issues = []

    # Read numeric fields safely
    numeric_fields = [
        "taxable_amount",
        "gst_rate_percent",
        "cgst",
        "sgst",
        "igst",
        "total_gst",
        "total_amount",
    ]

    values = {}

    for field in numeric_fields:
        try:
            value = float(invoice[field])

            if not pd.notna(value):
                raise ValueError

            values[field] = value

        except (KeyError, TypeError, ValueError):
            issues.append(f"Missing or invalid value: {field}")

    # Continue calculation checks only if all values are valid
    if len(values) == len(numeric_fields):

        taxable = values["taxable_amount"]
        rate = values["gst_rate_percent"]
        cgst = values["cgst"]
        sgst = values["sgst"]
        igst = values["igst"]
        total_gst = values["total_gst"]
        total_amount = values["total_amount"]

        # 1. Check for negative amounts
        amount_fields = [
            "taxable_amount",
            "cgst",
            "sgst",
            "igst",
            "total_gst",
            "total_amount",
        ]

        for field in amount_fields:
            if values[field] < 0:
                issues.append(f"Negative amount detected: {field}")

        if not 0 <= rate <= 100:
            issues.append("GST rate must be between 0 and 100")

        # 2. Check total GST calculation
        calculated_gst = cgst + sgst + igst

        if abs(total_gst - calculated_gst) > 0.02:
            issues.append(
                "Total GST does not match CGST + SGST + IGST"
            )

        # 3. Check invoice total
        calculated_total = taxable + total_gst

        if abs(total_amount - calculated_total) > 0.02:
            issues.append(
                "Total amount does not match taxable amount + total GST"
            )

        # 4. Check whether GST is consistent with the declared rate
        expected_gst = taxable * rate / 100

        if abs(total_gst - expected_gst) > 0.05:
            issues.append(
                "Total GST differs from the amount expected using the declared GST rate"
            )

        # 5. Check transaction type and GST components
        transaction_type = str(
            invoice.get("transaction_type", "")
        ).strip().lower()

        if transaction_type == "intra-state":
            if igst > 0.02:
                issues.append(
                    "IGST is present for an intra-state transaction"
                )

            if abs(cgst - sgst) > 0.02:
                issues.append(
                    "CGST and SGST are not approximately equal"
                )

        elif transaction_type == "inter-state":
            if cgst > 0.02 or sgst > 0.02:
                issues.append(
                    "CGST or SGST is present for an inter-state transaction"
                )

    return {
        "is_valid": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues,
    }
