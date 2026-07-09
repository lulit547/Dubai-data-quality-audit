"""
02_cleanse_data.py
Applies the rules in data_quality_rules.md to raw_orders.csv.
Produces:
  - clean_orders.csv          (cleansed dataset)
  - duplicates_for_review.csv (flagged, not deleted)
  - flagged_issues.csv        (rows with unresolved validity issues)
  - cleansing_log.json        (summary of every change made)
"""
import pandas as pd
import numpy as np
import re
import json

df = pd.read_csv("raw_orders.csv")
log = {"steps": []}

def log_step(name, detail):
    log["steps"].append({"step": name, "detail": detail})
    print(f"[{name}] {detail}")

start_rows = len(df)

# ---- 1. Trim whitespace on text fields ----
text_cols = ["customer_name", "city", "payment_method"]
for c in text_cols:
    df[c] = df[c].astype(str).str.strip()
log_step("trim_whitespace", f"Trimmed whitespace on {text_cols}")

# ---- 2. Remove exact duplicate rows ----
before = len(df)
df = df.drop_duplicates(keep="first").reset_index(drop=True)
log_step("remove_exact_duplicates", f"Removed {before - len(df)} exact duplicate rows")

# ---- 3. Handle duplicate order_ids (keep first, flag rest for review) ----
dupe_mask = df.duplicated(subset=["order_id"], keep="first")
duplicates_for_review = df[dupe_mask].copy()
df = df[~dupe_mask].reset_index(drop=True)
duplicates_for_review.to_csv("duplicates_for_review.csv", index=False)
log_step("flag_duplicate_order_ids",
          f"Moved {len(duplicates_for_review)} rows with duplicate order_id to duplicates_for_review.csv")

# ---- 4. Standardize city names ----
city_map = {
    "dubai": "Dubai", "dubai ": "Dubai",
    "abu dhabi": "Abu Dhabi", "abudhabi": "Abu Dhabi",
    "sharjah": "Sharjah", "sharjah ": "Sharjah",
    "ajman": "Ajman",
    "ras al khaimah": "Ras Al Khaimah", "rak": "Ras Al Khaimah",
    "fujeirah": "Fujairah", "fujairah": "Fujairah",
}
df["city_clean"] = df["city"].str.strip().str.lower().map(city_map).fillna(df["city"].str.strip())
mismatches = (df["city_clean"] != df["city"]).sum()
df["city"] = df["city_clean"]
df = df.drop(columns=["city_clean"])
log_step("standardize_city", f"Normalized {mismatches} city values to canonical list")

# ---- 5. Standardize payment_method ----
payment_map = {
    "credit card": "Credit Card", "cc": "Credit Card",
    "debit card": "Debit Card",
    "cash on delivery": "Cash on Delivery", "cod": "Cash on Delivery",
    "apple pay": "Apple Pay",
}
df["payment_clean"] = df["payment_method"].str.strip().str.lower().map(payment_map).fillna(df["payment_method"])
mismatches_pay = (df["payment_clean"] != df["payment_method"]).sum()
df["payment_method"] = df["payment_clean"]
df = df.drop(columns=["payment_clean"])
log_step("standardize_payment_method", f"Normalized {mismatches_pay} payment_method values")

# ---- 6. Standardize date formats ----
df["order_date_parsed"] = pd.to_datetime(df["order_date"], errors="coerce", format="mixed")
unparsed_orders = df["order_date_parsed"].isna().sum()
df["ship_date_parsed"] = pd.to_datetime(df["ship_date"], errors="coerce", format="mixed")
log_step("standardize_dates",
          f"Parsed order_date/ship_date to ISO format. {unparsed_orders} order_date values could not be parsed.")

# ---- 7. Flag (do not silently fix) ship_date < order_date ----
invalid_ship = df["ship_date_parsed"] < df["order_date_parsed"]
df["flag_ship_before_order"] = invalid_ship.fillna(False)
log_step("flag_ship_before_order", f"Flagged {int(invalid_ship.sum())} rows where ship_date < order_date")

# ---- 8. Standardize phone format ----
def clean_phone(p):
    digits = re.sub(r"\D", "", str(p))
    if digits.startswith("971"):
        digits = digits[3:]
    if digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 9 and digits.startswith("5"):
        return f"+971 {digits[:2]} {digits[2:]}"
    return p  # leave as-is if unrecognized pattern, don't guess
df["phone"] = df["phone"].apply(clean_phone)
log_step("standardize_phone", "Normalized phone numbers to +971 5X XXXXXXX where possible")

# ---- 9. Validate email, flag invalid (do not delete or guess-fix) ----
email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
df["flag_invalid_email"] = df["email"].apply(
    lambda x: pd.notna(x) and not bool(email_pattern.match(str(x)))
)
log_step("flag_invalid_email", f"Flagged {int(df['flag_invalid_email'].sum())} rows with malformed email")

# ---- 10. Flag price outliers (do not delete) ----
df["flag_price_outlier"] = (df["unit_price_aed"] < 0) | (df["unit_price_aed"] > 5000)
df["flag_price_outlier"] = df["flag_price_outlier"].fillna(False)
log_step("flag_price_outliers", f"Flagged {int(df['flag_price_outlier'].sum())} rows with negative/extreme price")

# ---- Finalize columns ----
df["order_date"] = df["order_date_parsed"].dt.strftime("%Y-%m-%d")
df["ship_date"] = df["ship_date_parsed"].dt.strftime("%Y-%m-%d")
df = df.drop(columns=["order_date_parsed", "ship_date_parsed"])

# Split into clean vs flagged-for-review
any_flag = df["flag_ship_before_order"] | df["flag_invalid_email"] | df["flag_price_outlier"]
flagged_issues = df[any_flag].copy()
clean_orders = df.copy()  # keep all rows, but flags make issues visible/filterable

flagged_issues.to_csv("flagged_issues.csv", index=False)
clean_orders.to_csv("clean_orders.csv", index=False)

log["summary"] = {
    "starting_rows": start_rows,
    "final_rows": len(clean_orders),
    "duplicate_order_ids_moved_to_review": len(duplicates_for_review),
    "rows_with_unresolved_flags": int(any_flag.sum()),
}
with open("cleansing_log.json", "w") as f:
    json.dump(log, f, indent=2, default=str)

print("\nDone. Files written: clean_orders.csv, duplicates_for_review.csv, flagged_issues.csv, cleansing_log.json")
