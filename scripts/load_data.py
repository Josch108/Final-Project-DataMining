"""
Load and clean raw transaction data for the Apriori pipeline using only standard libraries.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, List

RAW_PATH = Path("data/raw/transactions.csv")
CLEAN_PATH = Path("data/processed/cleaned_transactions.csv")


def _normalize_items(items: Iterable[str]) -> List[str]:
    normalized = []
    for item in items:
        item = item.strip()
        if item:
            normalized.append(item.title())
    return sorted(set(normalized))


def clean_transactions(raw_path: Path = RAW_PATH, output_path: Path = CLEAN_PATH) -> str:
    """
    Read the raw CSV file, normalize the items column, and save a cleaned dataset.

    The cleaned dataset includes:
    - transaction_id: integer identifier
    - items: JSON array containing the unique, title-cased items for the transaction
    """
    cleaned_rows = []
    with raw_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items = _normalize_items(row["Items"].split(","))
            if not items:
                continue
            cleaned_rows.append({
                "transaction_id": row.get("TransactionID") or row.get("transaction_id") or len(cleaned_rows) + 1,
                "items": json.dumps(items),
            })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["transaction_id", "items"])
        writer.writeheader()
        writer.writerows(cleaned_rows)

    # Return a JSON-serializable value for Airflow XCom
    return str(output_path)


if __name__ == "__main__":
    output_file = clean_transactions()
    print(f"Cleaned transactions saved to {output_file}")
