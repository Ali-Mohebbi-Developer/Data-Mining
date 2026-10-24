from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def save_price_histogram(dataframe: pd.DataFrame, path: Path) -> None:
    fig, axis = plt.subplots(figsize=(8, 5))
    axis.hist(dataframe["price"], bins=25)
    axis.set_title("Book Price Distribution")
    axis.set_xlabel("Price in GBP")
    axis.set_ylabel("Frequency")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def save_rating_counts(dataframe: pd.DataFrame, path: Path) -> None:
    counts = dataframe["rating"].value_counts().sort_index()
    fig, axis = plt.subplots(figsize=(8, 5))
    counts.plot(kind="bar", ax=axis)
    axis.set_title("Rating Counts")
    axis.set_xlabel("Rating")
    axis.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def save_price_by_rating(dataframe: pd.DataFrame, path: Path) -> None:
    groups = [group["price"].values for _, group in dataframe.groupby("rating", sort=True)]
    labels = sorted(dataframe["rating"].unique())
    fig, axis = plt.subplots(figsize=(8, 5))
    axis.boxplot(groups, tick_labels=labels)
    axis.set_title("Price by Rating")
    axis.set_xlabel("Rating")
    axis.set_ylabel("Price in GBP")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
