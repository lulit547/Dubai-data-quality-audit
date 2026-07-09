"""
01_profile_data.py
Profiles raw_orders.csv and produces a data quality report:
completeness, uniqueness, validity, consistency checks.
"""
import pandas as pd
import numpy as np
import re
import json

df = pd.read_csv("raw_orders.csv")
report = {}

# ---- 1. COMPLETENESS ----
completeness = {}
for col in df.columns:
    missing = df[col].isna().sum()
    completeness[col] = {
        "missing_count": int(missing),
        "missing_pct": round(missing / len(df) * 100, 2)
    }
report["completeness"] = completeness

# ---- 2. UNIQUENESS ----
exact_dupes = df.duplicated().sum()
order_id_dupes = df["order_id"].duplicated().sum()
report["uniqueness"] = {
    "exact_duplicate_rows": int(exact_dupes),
    "duplicate_order_ids": int(order_id_dupes),
    "total_rows": len(df)
}

# ---- 3. VALIDITY ----
email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
invalid_emails = df["email"].apply(lambda x: pd.notna(x) and not bool(email_pattern.match(str(x)))).sum()

# dates
def try_parse(d, fmt):
    try:
        pd.to_datetime(d, format=fmt)
        return True
    except Exception:
        return False

order_date_fmt_mixed = df["order_date"].apply(
    lambda x: not (try_parse(x, "%Y-%m-%d"))
).sum()

order_dates_parsed = pd.to_datetime(df["order_date"], errors="coerce", format="mixed")
ship_dates_parsed = pd.to_datetime(df["ship_date"], errors="coerce", format="mixed")
ship_before_order = (ship_dates_parsed < order_dates_parsed).sum()

negative_or_extreme_price = ((df["unit_price_aed"] < 0) | (df["unit_price_aed"] > 5000)).sum()

report["validity"] = {
    "invalid_email_format": int(invalid_emails),
    "order_date_nonstandard_format_count": int(order_date_fmt_mixed),
    "ship_date_before_order_date": int(ship_before_order),
    "price_negative_or_extreme_outlier": int(negative_or_extreme_price)
}

# ---- 4. CONSISTENCY ----
city_variants = df["city"].str.strip().str.lower().nunique()
city_raw_variants = df["city"].nunique()
payment_variants = df["payment_method"].nunique()

report["consistency"] = {
    "city_distinct_raw_values": int(city_raw_variants),
    "city_distinct_after_normalizing_case_whitespace": int(city_variants),
    "payment_method_distinct_raw_values": int(payment_variants)
}

# ---- 5. OVERALL QUALITY SCORE (simple weighted composite) ----
total_cells = df.shape[0] * df.shape[1]
total_missing = df.isna().sum().sum()
completeness_score = 1 - (total_missing / total_cells)
uniqueness_score = 1 - (exact_dupes / len(df))
validity_issues = invalid_emails + ship_before_order + negative_or_extreme_price
validity_score = 1 - (validity_issues / len(df))

overall_score = round(np.mean([completeness_score, uniqueness_score, validity_score]) * 100, 2)
report["overall_quality_score_pct"] = overall_score

with open("quality_report_before.json", "w") as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
