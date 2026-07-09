"""
03_profile_after.py
Profiles clean_orders.csv the same way as before, for direct comparison.
"""
import pandas as pd
import numpy as np
import re
import json

df = pd.read_csv("clean_orders.csv")
report = {}

completeness = {}
for col in ["email", "ship_date", "unit_price_aed"]:
    missing = df[col].isna().sum()
    completeness[col] = {"missing_count": int(missing), "missing_pct": round(missing/len(df)*100, 2)}
report["completeness"] = completeness

report["uniqueness"] = {
    "exact_duplicate_rows": int(df.duplicated().sum()),
    "duplicate_order_ids": int(df["order_id"].duplicated().sum()),
    "total_rows": len(df)
}

report["validity"] = {
    "invalid_email_flagged": int(df["flag_invalid_email"].sum()),
    "ship_date_before_order_date_flagged": int(df["flag_ship_before_order"].sum()),
    "price_outlier_flagged": int(df["flag_price_outlier"].sum()),
}

report["consistency"] = {
    "city_distinct_values": int(df["city"].nunique()),
    "payment_method_distinct_values": int(df["payment_method"].nunique()),
}

with open("quality_report_after.json", "w") as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))

# ---- Build before/after comparison summary ----
with open("quality_report_before.json") as f:
    before = json.load(f)

comparison = {
    "duplicate_rows": {"before": before["uniqueness"]["exact_duplicate_rows"], "after": report["uniqueness"]["exact_duplicate_rows"]},
    "duplicate_order_ids": {"before": before["uniqueness"]["duplicate_order_ids"], "after": report["uniqueness"]["duplicate_order_ids"]},
    "invalid_emails": {"before": before["validity"]["invalid_email_format"], "after": report["validity"]["invalid_email_flagged"]},
    "ship_before_order": {"before": before["validity"]["ship_date_before_order_date"], "after": report["validity"]["ship_date_before_order_date_flagged"]},
    "price_outliers": {"before": before["validity"]["price_negative_or_extreme_outlier"], "after": report["validity"]["price_outlier_flagged"]},
    "city_distinct_values": {"before": before["consistency"]["city_distinct_raw_values"], "after": report["consistency"]["city_distinct_values"]},
    "payment_distinct_values": {"before": before["consistency"]["payment_method_distinct_raw_values"], "after": report["consistency"]["payment_method_distinct_values"]},
    "total_rows": {"before": before["uniqueness"]["total_rows"], "after": report["uniqueness"]["total_rows"]},
}
with open("comparison_summary.json", "w") as f:
    json.dump(comparison, f, indent=2)
print("\n--- BEFORE / AFTER COMPARISON ---")
print(json.dumps(comparison, indent=2))
