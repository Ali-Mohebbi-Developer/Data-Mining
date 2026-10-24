from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from src.config import RANDOM_STATE


def prepare_matrix(dataframe: pd.DataFrame):
    vectorizer = TfidfVectorizer(max_features=400, ngram_range=(1, 2), min_df=2)
    text_matrix = vectorizer.fit_transform(dataframe["text"])
    numeric = dataframe[["price", "rating_numeric", "title_word_count", "description_word_count", "text_unique_word_ratio"]].astype(float)
    numeric_matrix = StandardScaler().fit_transform(numeric)
    combined = hstack([text_matrix, numeric_matrix])
    component_count = min(40, combined.shape[1] - 1)
    reduced = TruncatedSVD(n_components=component_count, random_state=RANDOM_STATE).fit_transform(combined)
    return reduced, vectorizer


def choose_k(matrix: np.ndarray) -> tuple[int, pd.DataFrame]:
    rows = []
    for k in range(2, 7):
        labels = KMeans(n_clusters=k, n_init=20, random_state=RANDOM_STATE).fit_predict(matrix)
        rows.append({"k": k, "silhouette": silhouette_score(matrix, labels)})
    scores = pd.DataFrame(rows)
    best_k = int(scores.sort_values("silhouette", ascending=False).iloc[0]["k"])
    return best_k, scores


def profile_clusters(dataframe: pd.DataFrame, label_column: str) -> pd.DataFrame:
    numeric_profile = dataframe.groupby(label_column).agg(
        size=("title", "size"),
        mean_price=("price", "mean"),
        mean_rating=("rating_numeric", "mean"),
        mean_title_words=("title_word_count", "mean"),
        mean_description_words=("description_word_count", "mean"),
    ).reset_index()
    theme = dataframe.groupby(label_column)["title_theme"].agg(lambda values: values.value_counts().index[0]).reset_index(name="dominant_theme")
    price_band = dataframe.groupby(label_column)["price_band"].agg(lambda values: values.value_counts().index[0]).reset_index(name="dominant_price_band")
    return numeric_profile.merge(theme, on=label_column).merge(price_band, on=label_column)


def run_clustering(dataframe: pd.DataFrame, tables_dir: Path, models_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    matrix, vectorizer = prepare_matrix(dataframe)
    best_k, scores = choose_k(matrix)
    kmeans = KMeans(n_clusters=best_k, n_init=30, random_state=RANDOM_STATE)
    kmeans_labels = kmeans.fit_predict(matrix)
    agglomerative = AgglomerativeClustering(n_clusters=best_k, linkage="ward")
    agglomerative_labels = agglomerative.fit_predict(matrix)
    result = dataframe.copy()
    result["cluster_kmeans"] = kmeans_labels
    result["cluster_agglomerative"] = agglomerative_labels
    metrics = pd.DataFrame([
        {"algorithm": "KMeans", "clusters": best_k, "silhouette": silhouette_score(matrix, kmeans_labels)},
        {"algorithm": "Agglomerative", "clusters": best_k, "silhouette": silhouette_score(matrix, agglomerative_labels)},
    ])
    scores.to_csv(tables_dir / "k_selection_scores.csv", index=False)
    metrics.to_csv(tables_dir / "clustering_metrics.csv", index=False)
    profile_clusters(result, "cluster_kmeans").to_csv(tables_dir / "cluster_profiles_kmeans.csv", index=False)
    profile_clusters(result, "cluster_agglomerative").to_csv(tables_dir / "cluster_profiles_agglomerative.csv", index=False)
    result[["detail_url", "title", "cluster_kmeans", "cluster_agglomerative"]].to_csv(tables_dir / "cluster_assignments.csv", index=False)
    joblib.dump(kmeans, models_dir / "kmeans.joblib")
    joblib.dump(vectorizer, models_dir / "clustering_vectorizer.joblib")
    return metrics, result
