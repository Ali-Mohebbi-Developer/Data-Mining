from pathlib import Path

import pandas as pd


def build_eda_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = dataframe.select_dtypes(include="number").columns
    summary = dataframe[numeric_columns].describe().T.reset_index().rename(columns={"index": "feature"})
    summary["missing"] = [int(dataframe[column].isna().sum()) for column in numeric_columns]
    return summary


def build_data_quality_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "column": dataframe.columns,
        "dtype": [str(dataframe[column].dtype) for column in dataframe.columns],
        "missing": [int(dataframe[column].isna().sum()) for column in dataframe.columns],
        "unique": [int(dataframe[column].nunique(dropna=False)) for column in dataframe.columns],
    })


def save_eda_tables(dataframe: pd.DataFrame, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    build_eda_summary(dataframe).to_csv(directory / "eda_numeric_summary.csv", index=False)
    build_data_quality_summary(dataframe).to_csv(directory / "data_quality_summary.csv", index=False)
    dataframe["price_band"].value_counts().rename_axis("price_band").reset_index(name="count").to_csv(directory / "price_band_counts.csv", index=False)
    dataframe["rating"].value_counts().rename_axis("rating").reset_index(name="count").to_csv(directory / "rating_counts.csv", index=False)
