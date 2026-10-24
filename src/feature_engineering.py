import re

import numpy as np
import pandas as pd

THEMES = {
    "love": ["love", "heart", "romance", "kiss", "marriage"],
    "history": ["history", "war", "empire", "ancient", "america", "world"],
    "science": ["science", "physics", "brain", "technology", "nature", "human"],
    "life": ["life", "mind", "self", "happiness", "success", "freedom"],
    "art": ["art", "music", "poem", "poetry", "drawing", "design"],
    "food": ["cook", "food", "kitchen", "diet", "recipe", "wine"],
    "travel": ["travel", "journey", "places", "paris", "city", "road"],
    "crime": ["murder", "death", "killer", "crime", "dark", "secret"],
    "children": ["princess", "girl", "boy", "children", "fairy", "unicorn"],
}


def detect_theme(text: str) -> str:
    lowered = text.lower()
    scores = {theme: sum(keyword in lowered for keyword in keywords) for theme, keywords in THEMES.items()}
    theme, score = max(scores.items(), key=lambda item: item[1])
    return theme if score > 0 else "other"


def add_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    data = dataframe.copy()
    text = (data["title"].fillna("") + " " + data["description"].fillna("")).str.strip()
    data["text"] = text
    data["title_word_count"] = data["title"].str.findall(r"\b\w+\b").str.len().astype(int)
    data["title_char_count"] = data["title"].str.len().astype(int)
    data["description_word_count"] = data["description"].str.findall(r"\b\w+\b").str.len().astype(int)
    data["has_series_number"] = data["title"].str.contains(r"#\d+|\bvol\.?\s*\d+|\bvolume\s*\d+|\bbook\s*\d+", case=False, regex=True).map({True: "Yes", False: "No"})
    data["has_digit"] = data["title"].str.contains(r"\d", regex=True).map({True: "Yes", False: "No"})
    data["has_subtitle"] = data["title"].str.contains(":", regex=False).map({True: "Yes", False: "No"})
    data["has_parentheses"] = data["title"].str.contains(r"[()]", regex=True).map({True: "Yes", False: "No"})
    data["title_theme"] = data["text"].map(detect_theme)
    data["title_initial_group"] = data["title"].str[0].str.upper().map(lambda value: "A-F" if value and value <= "F" else "G-L" if value and value <= "L" else "M-R" if value and value <= "R" else "S-Z")
    data["price_band"] = pd.qcut(data["price"], q=3, labels=["Low", "Medium", "High"], duplicates="drop").astype(str)
    data["title_length_band"] = pd.cut(data["title_word_count"], bins=[-np.inf, 3, 7, np.inf], labels=["Short", "Medium", "Long"]).astype(str)
    data["description_length_band"] = pd.cut(data["description_word_count"], bins=[-np.inf, 8, 25, np.inf], labels=["Short", "Medium", "Long"]).astype(str)
    data["rating_group"] = pd.cut(data["rating_numeric"], bins=[-1, 2, 3, 5], labels=["Low", "Medium", "High"]).astype(str)
    data["price_above_median"] = np.where(data["price"] >= data["price"].median(), "Yes", "No")
    data["price_per_title_word"] = data["price"] / data["title_word_count"].clip(lower=1)
    data["average_word_length"] = data["title_char_count"] / data["title_word_count"].clip(lower=1)
    data["word_length_band"] = pd.cut(data["average_word_length"], bins=[-np.inf, 5.0, 7.0, np.inf], labels=["Short", "Medium", "Long"]).astype(str)
    data["text_unique_word_ratio"] = data["text"].map(lambda value: len(set(re.findall(r"\b\w+\b", value.lower()))) / max(len(re.findall(r"\b\w+\b", value.lower())), 1))
    return data
