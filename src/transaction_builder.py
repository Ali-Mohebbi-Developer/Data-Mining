import pandas as pd


def build_transactions(dataframe: pd.DataFrame) -> list[set[str]]:
    transactions = []
    for row in dataframe.itertuples(index=False):
        items = {
            f"rating={row.rating}",
            f"price_band={row.price_band}",
            f"title_length={row.title_length_band}",
            f"theme={row.title_theme}",
            f"series_number={row.has_series_number}",
            f"subtitle={row.has_subtitle}",
            f"parentheses={row.has_parentheses}",
            f"word_length={row.word_length_band}",
            f"initial_group={row.title_initial_group}",
        }
        transactions.append(items)
    return transactions
