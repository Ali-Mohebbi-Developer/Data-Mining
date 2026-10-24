from pathlib import Path

import pandas as pd

from src.apriori_library import run_mlxtend_apriori
from src.apriori_manual import run_apriori
from src.transaction_builder import build_transactions


def analyze_association_rules(dataframe: pd.DataFrame, output_path: Path, engine: str = "manual") -> pd.DataFrame:
    transactions = build_transactions(dataframe)
    if engine == "mlxtend":
        rules = run_mlxtend_apriori(transactions)
    else:
        rules = run_apriori(transactions)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rules.head(100).to_csv(output_path, index=False)
    return rules
