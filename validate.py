"""Validate a CSV using rules defined in YAML and write a summary report."""

from pathlib import Path

import pandas as pd
import yaml


def main():
    root = Path(__file__).resolve().parent
    with (root / "config/validation.yml").open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    data = pd.read_csv(root / config["dataset"]["file"])
    rules = config["validation"]
    results = []

    def record(check, column, count):
        results.append({
            "check": check,
            "column": column,
            "status": "PASS" if count == 0 else "FAIL",
            "failed_rows": int(count),
        })

    # Check column presence before applying row-level rules.
    columns = dict.fromkeys([
        rules["primary_key"],
        *rules["required_columns"],
        *rules["positive_columns"],
    ])
    for column in columns:
        if column not in data.columns:
            record("column_exists", column, len(data))
            results[-1]["status"] = "FAIL"

    primary_key = rules["primary_key"]
    if primary_key in data.columns:
        record("unique", primary_key, data.duplicated(primary_key, keep=False).sum())

    for column in rules["required_columns"]:
        if column in data.columns:
            missing = data[column].isna() | data[column].astype(str).str.strip().eq("")
            record("not_null", column, missing.sum())

    for column in rules["positive_columns"]:
        if column in data.columns:
            values = pd.to_numeric(data[column], errors="coerce")
            record("positive", column, (values.isna() | values.le(0)).sum())

    report = pd.DataFrame(results, columns=["check", "column", "status", "failed_rows"])
    output = root / "output/validation_results.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(output, index=False)
    print(report.to_string(index=False))
    print(f"\nValidated {len(data)} rows; {(report['status'] == 'FAIL').sum()} checks failed.")
    print("Report saved to output/validation_results.csv")


if __name__ == "__main__":
    main()
