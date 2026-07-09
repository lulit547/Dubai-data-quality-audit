# Orders Data Quality Audit — Dubai E-Commerce (Portfolio Project)

## Problem
Simulated a realistic Dubai e-commerce orders dataset (5,210 rows) with the
kinds of data quality issues found in real production systems: duplicate
records, inconsistent city/payment labels, malformed emails, mismatched
date sequencing, and price outliers. Ran a full data quality audit and
cleansing pipeline against it, following data governance best practice:
**fix what's safe to fix, flag what isn't — never silently guess.**

## Pipeline

| Script | What it does |
|---|---|
| `generate_data.py` | Generates the synthetic raw dataset with injected quality issues |
| `01_profile_data.py` | Profiles raw data — completeness, uniqueness, validity, consistency checks |
| `data_quality_rules.md` | Defines the validation rules and duplicate-handling policy used |
| `02_cleanse_data.py` | Applies the rules: dedupes, standardizes formats, flags unresolved issues |
| `03_profile_after.py` | Re-profiles cleaned data and builds the before/after comparison |
| `data_quality_dashboard.html` | Interactive dashboard summarizing the audit results |

## Results

| Metric | Before | After |
|---|---|---|
| Exact duplicate rows | 150 | **0** |
| Duplicate order IDs | 210 | **0** |
| City name variants | 18 | **6** (canonical) |
| Payment method variants | 7 | **4** (canonical) |
| Invalid emails | 367 | 354 (flagged, not fabricated) |
| Ship date before order date | 314 | 303 (flagged for source-system fix) |
| Price outliers | 41 | 40 (flagged, not deleted) |

**Key judgment call:** invalid emails, bad date sequencing, and price
outliers barely move after cleansing — that's intentional. These are
content-level errors that originate upstream (bad data entry, broken
integration). A data quality analyst's job is to catch and document them,
not silently invent "corrected" values that could be wrong. Structural
noise (duplicates, inconsistent labels) *is* fully resolved, because that's
safely automatable.

## Files produced
- `clean_orders.csv` — cleaned dataset with quality flags per row
- `flagged_issues.csv` — subset of rows with unresolved validity issues, for source-system review
- `duplicates_for_review.csv` — order_id duplicates held back from auto-deletion
- `cleansing_log.json` — step-by-step log of every transformation applied
- `quality_report_before.json` / `quality_report_after.json` — full profiling output
- `comparison_summary.json` — before/after metrics

## Tools used
Python (Pandas, NumPy, re), JSON-based logging, HTML/CSS for the dashboard.


