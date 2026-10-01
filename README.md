# Data Validation MVP

A small, configuration-driven data validation project built with Python, pandas, and YAML. It checks fictional transaction data and produces a CSV summary suitable for reviewing data quality issues.

**YAML defines WHAT to validate; Python implements HOW.** Change the configured column names to reuse the same checks with another CSV.

## Architecture

```text
config/validation.yml (rules) ─┐
                              ├─> validate.py ─> output/validation_results.csv
data/transactions.csv (data) ──┘
```

- `data/transactions.csv`: five sample transactions with intentional errors.
- `config/validation.yml`: input file, primary key, required values, and positive numeric columns.
- `validate.py`: loads YAML safely, reads the CSV, applies checks, and writes the report.
- `requirements.txt`: Python dependencies.
- `output/validation_results.csv`: generated sample report, included for easy review.

## Run locally

Requires Python 3.10 or newer. From the project directory:

```bash
python -m venv .venv
```

Activate the environment on Windows with `.venv\Scripts\activate`, or on macOS/Linux with `source .venv/bin/activate`. Then run:

```bash
python -m pip install -r requirements.txt
python validate.py
```

The script prints the results and overwrites `output/validation_results.csv`. File paths are resolved relative to the project, so running the script from another directory also works.

## Sample validation results

| Check | Column | Status | Failed rows |
| --- | --- | --- | ---: |
| unique | transaction_id | FAIL | 2 |
| not_null | transaction_id | PASS | 0 |
| not_null | customer_id | FAIL | 1 |
| not_null | transaction_date | PASS | 0 |
| not_null | amount | PASS | 0 |
| positive | amount | FAIL | 1 |

Three checks fail as expected: transaction ID `1002` occurs in two rows, one customer ID is missing, and one amount is negative. The uniqueness check counts **both rows** sharing a duplicate key.

Required columns must exist and contain no null or blank values. Positive columns must contain numeric values greater than zero; missing or nonnumeric values fail that check. Missing configured columns produce `column_exists` failures, and their row checks are skipped. Dates are checked for missing values only, not date format.

This MVP reports data issues without changing the input. A successful script run exits normally even when validation checks fail; the report carries the PASS/FAIL results. It intentionally focuses on three basic rules without infrastructure or a user interface.
