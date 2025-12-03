"""
Generate a markdown report combining frequent itemsets and association rules results.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

CLEAN_PATH = Path("data/processed/cleaned_transactions.csv")
ITEMSETS_PATH = Path("results/frequent_itemsets.csv")
RULES_PATH = Path("results/rules.csv")
REPORT_PATH = Path("results/report.md")


def summarize_transactions(clean_path: Path = CLEAN_PATH) -> dict:
    num_transactions = 0
    item_counts = {}
    with clean_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            num_transactions += 1
            for item in json.loads(row["items"]):
                item_counts[item] = item_counts.get(item, 0) + 1
    top_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    return {"transactions": num_transactions, "top_items": top_items}


def read_csv_rows(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def generate_report(
    clean_path: Path = CLEAN_PATH,
    itemsets_path: Path = ITEMSETS_PATH,
    rules_path: Path = RULES_PATH,
    output_path: Path = REPORT_PATH,
) -> Path:
    summary = summarize_transactions(clean_path)
    itemsets_rows = read_csv_rows(itemsets_path)
    rules_rows = read_csv_rows(rules_path)

    lines = ["# Market-Basket Mining Report", ""]
    lines.append(f"**Transactions processed:** {summary['transactions']}")
    lines.append("\n## Top Items in Transactions")
    for item, count in summary["top_items"]:
        lines.append(f"- {item}: {count} occurrences")

    lines.append("\n## Frequent Itemsets")
    if not itemsets_rows:
        lines.append("No frequent itemsets generated.")
    else:
        sorted_rows = sorted(itemsets_rows, key=lambda r: float(r["support"]), reverse=True)[:10]
        for row in sorted_rows:
            lines.append(
                f"- {row['itemset']} (k={row['k']}, support={row['support']}, count={row['count']})"
            )

    lines.append("\n## Association Rules")
    if not rules_rows:
        lines.append("No rules met the configured thresholds.")
    else:
        for row in rules_rows[:10]:
            lines.append(
                f"- {row['antecedent']} -> {row['consequent']} (support={row['support']}, confidence={row['confidence']}, lift={row['lift']})"
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))
    return output_path


if __name__ == "__main__":
    report = generate_report()
    print(f"Report saved to {report}")
