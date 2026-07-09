# Data Quality Rules — Dubai E-Commerce Orders Dataset

## Purpose
Defines what "valid" and "trustworthy" means for each field in the orders
dataset, so cleansing decisions are traceable and repeatable rather than
ad hoc.

## Field-Level Rules

| Field | Rule | Action if violated |
|---|---|---|
| `order_id` | Must be unique. Format `ORDxxxxxx`. | Keep first occurrence, flag/drop later duplicates |
| `customer_id` | Must be non-null, format `CUSTxxxxx` | Flag for investigation if malformed |
| `customer_name` | Non-null. Trim leading/trailing/double whitespace. | Auto-trim |
| `email` | Must match standard email regex (`user@domain.tld`) or be null. | Flag as invalid; do not guess-correct. Null allowed but tracked. |
| `phone` | Must match `+971 5X XXXXXXX` pattern. | Standardize format where digits are recoverable |
| `city` | Must map to one of 6 valid Emirates: Dubai, Abu Dhabi, Sharjah, Ajman, Fujairah, Ras Al Khaimah | Normalize casing/whitespace/abbreviations to canonical list |
| `order_date` | Must be a valid date, stored as `YYYY-MM-DD`. | Parse mixed formats (`DD/MM/YYYY` too) and standardize |
| `ship_date` | Must be ≥ `order_date`. Null allowed (not yet shipped). | Flag rows where ship_date < order_date as invalid — do not silently fix, since it indicates an upstream process error |
| `category` | Must be one of the 8 approved categories. | Flag any unrecognized value |
| `unit_price_aed` | Must be > 0 and ≤ AED 5,000 (business-defined reasonable ceiling for this catalog). | Flag negative/zero/extreme values as outliers, do not delete |
| `quantity` | Must be a positive integer. | Flag zero/negative |
| `payment_method` | Must map to one of: Credit Card, Debit Card, Cash on Delivery, Apple Pay | Normalize aliases (CC → Credit Card, COD → Cash on Delivery, etc.) |

## Duplicate Handling Policy
- **Exact duplicate rows**: remove, keep first occurrence.
- **Duplicate `order_id` with differing values** (e.g. quantity changed):
  this indicates either a legitimate order amendment or a data pipeline
  error. Policy: keep the most recent record by `order_date`/load order,
  flag the rest in a separate "duplicates_for_review" file rather than
  silently discarding — this protects against deleting legitimate
  order-correction events.

## Ownership & Governance
- **Field owner**: Data Quality Analyst (this project) for initial
  profiling; in a real org this would map to the system-of-record team
  (e.g. Orders team owns `order_id`, `order_date`; CRM team owns
  `customer_name`, `email`).
- **Review cadence**: Quality checks should run on every data load, not
  just once — this is simulated here as a single before/after pass, but
  the profiling script is written to be rerunnable on any new file.

## Out of Scope
- This project does not attempt to *impute* missing prices or emails
  (i.e. guess a plausible value) — silently guessing values is itself a
  data quality risk. Missing values are documented and flagged instead.
