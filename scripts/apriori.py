"""
Pure Python Apriori algorithm implementation for market-basket analysis.
"""
from __future__ import annotations

import csv
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple

CLEAN_PATH = Path("data/processed/cleaned_transactions.csv")
FREQUENT_ITEMSETS_PATH = Path("results/frequent_itemsets.csv")
RULES_PATH = Path("results/rules.csv")
SUMMARY_REPORT_PATH = Path("results/summary_report.md")


@dataclass
class AprioriConfig:
    min_support: float = 0.2
    min_confidence: float = 0.4
    min_lift: float = 1.0
    max_items: int | None = None


Transaction = Set[str]
Itemset = frozenset[str]


def load_transactions(clean_path: Path = CLEAN_PATH) -> List[Transaction]:
    transactions: List[Transaction] = []
    with clean_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items = json.loads(row["items"])
            transactions.append(set(items))
    return transactions


def _generate_candidates(prev_frequents: List[Itemset], k: int) -> Set[Itemset]:
    candidates: Set[Itemset] = set()
    for itemset1 in prev_frequents:
        for itemset2 in prev_frequents:
            union_set = itemset1 | itemset2
            if len(union_set) == k:
                candidates.add(frozenset(union_set))
    return candidates


def _prune_candidates(candidates: Iterable[Itemset], prev_frequents: Set[Itemset]) -> Set[Itemset]:
    pruned: Set[Itemset] = set()
    for candidate in candidates:
        all_subsets_frequent = all(
            frozenset(subset) in prev_frequents
            for subset in itertools.combinations(candidate, len(candidate) - 1)
        )
        if all_subsets_frequent:
            pruned.add(candidate)
    return pruned


def _filter_with_support(
    transactions: Sequence[Transaction],
    candidates: Iterable[Itemset],
    min_support_count: int,
) -> Tuple[List[Itemset], Dict[Itemset, float], Dict[Itemset, int]]:
    support_counts: Dict[Itemset, int] = {}
    for transaction in transactions:
        for candidate in candidates:
            if candidate.issubset(transaction):
                support_counts[candidate] = support_counts.get(candidate, 0) + 1

    frequents: List[Itemset] = []
    support_data: Dict[Itemset, float] = {}
    count_data: Dict[Itemset, int] = {}
    total_transactions = len(transactions)
    for itemset, count in support_counts.items():
        support = count / total_transactions
        if count >= min_support_count:
            frequents.append(itemset)
        support_data[itemset] = support
        count_data[itemset] = count
    return frequents, support_data, count_data


def apriori(
    transactions: Sequence[Transaction], config: AprioriConfig
) -> Tuple[List[Itemset], Dict[Itemset, float], Dict[Itemset, int]]:
    min_support_count = math.ceil(config.min_support * len(transactions))
    item_counts: Dict[Itemset, int] = {}
    for transaction in transactions:
        for item in transaction:
            itemset = frozenset([item])
            item_counts[itemset] = item_counts.get(itemset, 0) + 1

    L1, support_data, count_data = _filter_with_support(
        transactions, item_counts.keys(), min_support_count
    )
    frequent_itemsets: List[Itemset] = L1.copy()
    current_frequents = L1
    k = 2

    while current_frequents:
        candidates = _generate_candidates(current_frequents, k)
        candidates = _prune_candidates(candidates, set(current_frequents))
        current_frequents, current_supports, current_counts = _filter_with_support(
            transactions, candidates, min_support_count
        )
        support_data.update(current_supports)
        count_data.update(current_counts)
        frequent_itemsets.extend(current_frequents)
        if config.max_items and k >= config.max_items:
            break
        k += 1

    return frequent_itemsets, support_data, count_data


def generate_association_rules(
    frequent_itemsets: Iterable[Itemset],
    support_data: Dict[Itemset, float],
    config: AprioriConfig,
) -> List[Dict[str, float | List[str]]]:
    rules: List[Dict[str, float | List[str]]] = []
    for itemset in frequent_itemsets:
        if len(itemset) < 2:
            continue
        for i in range(1, len(itemset)):
            for antecedent in itertools.combinations(itemset, i):
                antecedent_set = frozenset(antecedent)
                consequent_set = itemset - antecedent_set
                support_itemset = support_data[itemset]
                support_antecedent = support_data.get(antecedent_set, 0)
                support_consequent = support_data.get(consequent_set, 0)

                if support_antecedent == 0 or support_consequent == 0:
                    continue

                confidence = support_itemset / support_antecedent
                lift = confidence / support_consequent
                if confidence >= config.min_confidence and lift >= config.min_lift:
                    rules.append(
                        {
                            "antecedent": sorted(antecedent_set),
                            "consequent": sorted(consequent_set),
                            "support": round(support_itemset, 3),
                            "confidence": round(confidence, 3),
                            "lift": round(lift, 3),
                        }
                    )
    return rules


def save_frequent_itemsets(
    frequent_itemsets: Iterable[Itemset],
    support_data: Dict[Itemset, float],
    count_data: Dict[Itemset, int],
    total_transactions: int,
    output_path: Path = FREQUENT_ITEMSETS_PATH,
) -> Path:
    rows = []
    for itemset in frequent_itemsets:
        rows.append(
            {
                "itemset": ", ".join(sorted(itemset)),
                "k": len(itemset),
                "support": round(support_data[itemset], 3),
                "count": count_data.get(itemset, 0),
                "support_count_threshold": math.ceil(total_transactions * support_data[itemset]),
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["itemset", "k", "support", "count", "support_count_threshold"]
        )
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (r["k"], -r["support"])))
    return output_path


def save_rules(rules: Sequence[Dict[str, float | List[str]]], output_path: Path = RULES_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["antecedent", "consequent", "support", "confidence", "lift"]
        )
        writer.writeheader()
        for rule in sorted(rules, key=lambda r: (-r["lift"], -r["confidence"])):
            writer.writerow(
                {
                    "antecedent": ", ".join(rule["antecedent"]),
                    "consequent": ", ".join(rule["consequent"]),
                    "support": rule["support"],
                    "confidence": rule["confidence"],
                    "lift": rule["lift"],
                }
            )
    return output_path


def save_summary_report(
    frequent_itemsets: Sequence[Itemset],
    rules: Sequence[Dict[str, float | List[str]]],
    support_data: Dict[Itemset, float],
    output_path: Path = SUMMARY_REPORT_PATH,
) -> Path:
    lines = ["# Apriori Mining Summary", ""]
    lines.append(f"Total frequent itemsets: {len(frequent_itemsets)}")
    if frequent_itemsets:
        top_itemsets = sorted(
            frequent_itemsets, key=lambda i: support_data[i], reverse=True
        )[:5]
        lines.append("\n## Top Itemsets by Support")
        for itemset in top_itemsets:
            lines.append(f"- {', '.join(sorted(itemset))}: support={support_data[itemset]:.3f}")

    lines.append("\n## Association Rules")
    if rules:
        for rule in rules:
            antecedent = ", ".join(rule["antecedent"])
            consequent = ", ".join(rule["consequent"])
            lines.append(
                f"- {antecedent} -> {consequent} (support={rule['support']}, confidence={rule['confidence']}, lift={rule['lift']})"
            )
    else:
        lines.append("No rules met the configured thresholds.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))
    return output_path


def run_apriori_pipeline(
    clean_path: Path = CLEAN_PATH,
    frequent_itemsets_path: Path = FREQUENT_ITEMSETS_PATH,
    rules_path: Path = RULES_PATH,
    summary_report_path: Path = SUMMARY_REPORT_PATH,
    config: AprioriConfig | None = None,
) -> Tuple[Path, Path, Path]:
    config = config or AprioriConfig()
    transactions = load_transactions(clean_path)
    frequent_itemsets, support_data, count_data = apriori(transactions, config)
    rules = generate_association_rules(frequent_itemsets, support_data, config)

    fi_path = save_frequent_itemsets(
        frequent_itemsets,
        support_data,
        count_data,
        total_transactions=len(transactions),
        output_path=frequent_itemsets_path,
    )
    rules_path = save_rules(rules, rules_path)
    report_path = save_summary_report(frequent_itemsets, rules, support_data, summary_report_path)
    return fi_path, rules_path, report_path


if __name__ == "__main__":
    fi, rules, report = run_apriori_pipeline()
    print(f"Frequent itemsets saved to {fi}")
    print(f"Association rules saved to {rules}")
    print(f"Summary report saved to {report}")
