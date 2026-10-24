from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import RANDOM_STATE


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer([
        ("text", TfidfVectorizer(max_features=600, ngram_range=(1, 2), min_df=2), "text"),
        ("numeric", StandardScaler(), ["rating_numeric", "title_word_count", "title_char_count", "description_word_count", "text_unique_word_ratio"]),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), ["rating", "title_theme", "title_initial_group", "has_digit", "has_series_number"]),
    ])


def evaluate_model(name: str, pipeline: Pipeline, x_train: pd.DataFrame, x_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series, tables_dir: Path, models_dir: Path) -> dict[str, object]:
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)
    labels = sorted(y_test.unique())
    matrix = confusion_matrix(y_test, predictions, labels=labels)
    pd.DataFrame(matrix, index=labels, columns=labels).to_csv(tables_dir / f"confusion_matrix_{name}.csv")
    joblib.dump(pipeline, models_dir / f"{name}.joblib")
    return {
        "model": name,
        "accuracy": accuracy_score(y_test, predictions),
        "precision_macro": precision_score(y_test, predictions, average="macro", zero_division=0),
        "recall_macro": recall_score(y_test, predictions, average="macro", zero_division=0),
        "f1_macro": f1_score(y_test, predictions, average="macro", zero_division=0),
        "test_size": len(y_test),
    }


def run_classification(dataframe: pd.DataFrame, tables_dir: Path, models_dir: Path) -> pd.DataFrame:
    feature_columns = ["text", "rating_numeric", "title_word_count", "title_char_count", "description_word_count", "text_unique_word_ratio", "rating", "title_theme", "title_initial_group", "has_digit", "has_series_number"]
    x = dataframe[feature_columns]
    y = dataframe["price_band"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y)
    models = {
        "logistic_regression": LogisticRegression(max_iter=1500, class_weight="balanced", random_state=RANDOM_STATE),
        "random_forest": RandomForestClassifier(n_estimators=250, max_depth=12, min_samples_leaf=3, class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1),
    }
    rows = []
    for name, model in models.items():
        pipeline = Pipeline([("preprocessor", build_preprocessor()), ("model", model)])
        rows.append(evaluate_model(name, pipeline, x_train, x_test, y_train, y_test, tables_dir, models_dir))
    metrics = pd.DataFrame(rows).sort_values("f1_macro", ascending=False).reset_index(drop=True)
    metrics.to_csv(tables_dir / "classification_metrics.csv", index=False)
    return metrics
