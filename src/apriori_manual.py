from collections import Counter
from itertools import combinations

import pandas as pd


def mine_frequent_itemsets(transactions: list[set[str]], min_support: float = 0.045, max_length: int = 3) -> dict[frozenset[str], float]:
    total = len(transactions)
    frequent: dict[frozenset[str], float] = {}
    candidates = {frozenset([item]) for transaction in transactions for item in transaction}
    size = 1
    while candidates and size <= max_length:
        counts = Counter()
        for transaction in transactions:
            for candidate in candidates:
                if candidate.issubset(transaction):
                    counts[candidate] += 1
        current = {itemset: count / total for itemset, count in counts.items() if count / total >= min_support}
        frequent.update(current)
        size += 1
        previous = list(current)
        joined = set()
        for left, right in combinations(previous, 2):
            candidate = left | right
            if len(candidate) == size and all(frozenset(part) in current for part in combinations(candidate, size - 1)):
                joined.add(candidate)
        candidates = joined
    return frequent


def generate_rules(frequent: dict[frozenset[str], float], min_confidence: float = 0.45, min_lift: float = 1.0) -> pd.DataFrame:
    rows = []
    for itemset, support in frequent.items():
        if len(itemset) < 2:
            continue
        items = list(itemset)
        for size in range(1, len(items)):
            for antecedent_tuple in combinations(items, size):
                antecedent = frozenset(antecedent_tuple)
                consequent = itemset - antecedent
                antecedent_support = frequent.get(antecedent)
                consequent_support = frequent.get(consequent)
                if not antecedent_support or not consequent_support:
                    continue
                confidence = support / antecedent_support
                lift = confidence / consequent_support
                if confidence >= min_confidence and lift >= min_lift:
                    rows.append({
                        "antecedents": " | ".join(sorted(antecedent)),
                        "consequents": " | ".join(sorted(consequent)),
                        "support": support,
                        "confidence": confidence,
                        "lift": lift,
                    })
    if not rows:
        return pd.DataFrame(columns=["antecedents", "consequents", "support", "confidence", "lift"])
    return pd.DataFrame(rows).drop_duplicates().sort_values(["lift", "confidence", "support"], ascending=False).reset_index(drop=True)


def run_apriori(transactions: list[set[str]], min_support: float = 0.045, min_confidence: float = 0.45, min_lift: float = 1.0, max_length: int = 3) -> pd.DataFrame:
    frequent = mine_frequent_itemsets(transactions, min_support=min_support, max_length=max_length)
    return generate_rules(frequent, min_confidence=min_confidence, min_lift=min_lift)
