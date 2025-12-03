# Market-Basket Mining Report

**Transactions processed:** 12

## Top Items in Transactions
- Bread: 6 occurrences
- Milk: 6 occurrences
- Butter: 5 occurrences
- Chips: 4 occurrences
- Eggs: 3 occurrences

## Frequent Itemsets
- Milk (k=1, support=0.5, count=6)
- Bread (k=1, support=0.5, count=6)
- Butter (k=1, support=0.417, count=5)
- Chips (k=1, support=0.333, count=4)
- Eggs (k=1, support=0.25, count=3)
- Bread, Milk (k=2, support=0.25, count=3)
- Eggs, Milk (k=2, support=0.25, count=3)
- Bread, Butter (k=2, support=0.25, count=3)
- Butter, Milk (k=2, support=0.25, count=3)

## Association Rules
- Eggs -> Milk (support=0.25, confidence=1.0, lift=2.0)
- Milk -> Eggs (support=0.25, confidence=0.5, lift=2.0)
- Butter -> Bread (support=0.25, confidence=0.6, lift=1.2)
- Butter -> Milk (support=0.25, confidence=0.6, lift=1.2)
- Bread -> Butter (support=0.25, confidence=0.5, lift=1.2)
- Milk -> Butter (support=0.25, confidence=0.5, lift=1.2)
- Milk -> Bread (support=0.25, confidence=0.5, lift=1.0)
- Bread -> Milk (support=0.25, confidence=0.5, lift=1.0)
