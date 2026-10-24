import pandas as pd


def run_mlxtend_apriori(transactions: list[set[str]], min_support: float = 0.045, min_confidence: float = 0.45, min_lift: float = 1.0) -> pd.DataFrame:
    from mlxtend.frequent_patterns import apriori, association_rules
    from mlxtend.preprocessing import TransactionEncoder

    encoder = TransactionEncoder()
    matrix = encoder.fit(transactions).transform(transactions)
    encoded = pd.DataFrame(matrix, columns=encoder.columns_)
    itemsets = apriori(encoded, min_support=min_support, use_colnames=True, max_len=3)
    rules = association_rules(itemsets, metric="confidence", min_threshold=min_confidence)
    rules = rules.loc[rules["lift"] >= min_lift].copy()
    rules["antecedents"] = rules["antecedents"].map(lambda value: " | ".join(sorted(value)))
    rules["consequents"] = rules["consequents"].map(lambda value: " | ".join(sorted(value)))
    return rules[["antecedents", "consequents", "support", "confidence", "lift"]].sort_values(["lift", "confidence", "support"], ascending=False).reset_index(drop=True)
