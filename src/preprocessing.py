import re

import numpy as np
import pandas as pd

from src.utils import normalize_whitespace

RATING_MAP = {"Zero": 0, "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_number(value: object) -> float:
    text = normalize_whitespace(value).replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group()) if match else np.nan


def normalize_boolean(value: object) -> str:
    text = normalize_whitespace(value).lower()
    return "In stock" if text in {"true", "1", "yes", "in stock"} or "in stock" in text else "Out of stock"


def clean_books(dataframe: pd.DataFrame) -> pd.DataFrame:
    data = dataframe.copy()
    data.columns = [normalize_whitespace(column).lower() for column in data.columns]
    if "availability" not in data.columns and "in_stock_availability" in data.columns:
        data["availability"] = data["in_stock_availability"]
    required_defaults = {
        "detail_url": "",
        "image_url": "",
        "title": "",
        "category": "Unknown",
        "rating": "Unknown",
        "price": np.nan,
        "availability": "Unknown",
        "description": "",
        "upc": "",
        "product_type": "Book",
        "price_excluding_tax": np.nan,
        "price_including_tax": np.nan,
        "tax": np.nan,
        "number_of_reviews": 0,
    }
    for column, default in required_defaults.items():
        if column not in data.columns:
            data[column] = default
    text_columns = ["detail_url", "image_url", "title", "category", "rating", "availability", "description", "upc", "product_type"]
    for column in text_columns:
        data[column] = data[column].fillna("").map(normalize_whitespace)
    for column in ["price", "price_excluding_tax", "price_including_tax", "tax", "number_of_reviews"]:
        data[column] = data[column].map(parse_number)
    data["price"] = data["price"].fillna(data["price"].median())
    data["price_excluding_tax"] = data["price_excluding_tax"].fillna(data["price"])
    data["price_including_tax"] = data["price_including_tax"].fillna(data["price"])
    data["tax"] = data["tax"].fillna(0.0)
    data["number_of_reviews"] = data["number_of_reviews"].fillna(0).astype(int)
    data["rating"] = data["rating"].replace("", "Unknown")
    mode_rating = data.loc[data["rating"].isin(RATING_MAP), "rating"].mode()
    replacement_rating = mode_rating.iloc[0] if not mode_rating.empty else "Three"
    data.loc[~data["rating"].isin(RATING_MAP), "rating"] = replacement_rating
    data["rating_numeric"] = data["rating"].map(RATING_MAP).astype(int)
    data["availability"] = data["availability"].map(normalize_boolean)
    data["category"] = data["category"].replace("", "Unknown")
    data["product_type"] = data["product_type"].replace("", "Book")
    data["description"] = data["description"].where(data["description"].str.len() > 0, data["title"])
    data = data.drop_duplicates(subset=["detail_url", "title"], keep="first")
    data = data.loc[data["title"].str.len() > 0].reset_index(drop=True)
    return data
