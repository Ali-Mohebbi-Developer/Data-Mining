from pathlib import Path

from src.association_rules_analysis import analyze_association_rules
from src.classification import run_classification
from src.clustering import run_clustering
from src.config import CLEAN_DATA_PATH, FEATURE_DATA_PATH, FIGURES_DIR, MODELS_DIR, TABLES_DIR
from src.data_loader import load_csv, save_csv
from src.exploratory_analysis import save_eda_tables
from src.feature_engineering import add_features
from src.preprocessing import clean_books
from src.report_builder import build_report
from src.utils import ensure_directories, save_json
from src.visualization import save_price_by_rating, save_price_histogram, save_rating_counts


def run_pipeline(raw_path: Path, association_engine: str = "manual") -> dict[str, object]:
    ensure_directories()
    raw = load_csv(raw_path)
    cleaned = clean_books(raw)
    save_csv(cleaned, CLEAN_DATA_PATH)
    featured = add_features(cleaned)
    save_csv(featured, FEATURE_DATA_PATH)
    save_eda_tables(featured, TABLES_DIR)
    save_price_histogram(featured, FIGURES_DIR / "price_distribution.png")
    save_rating_counts(featured, FIGURES_DIR / "rating_counts.png")
    save_price_by_rating(featured, FIGURES_DIR / "price_by_rating.png")
    rules = analyze_association_rules(featured, TABLES_DIR / "association_rules.csv", engine=association_engine)
    classification_metrics = run_classification(featured, TABLES_DIR, MODELS_DIR)
    clustering_metrics, clustered = run_clustering(featured, TABLES_DIR, MODELS_DIR)
    clustered.to_csv(FEATURE_DATA_PATH, index=False)
    build_report(clustered, rules, classification_metrics, clustering_metrics, Path("reports.md"))
    summary = {
        "raw_records": len(raw),
        "clean_records": len(cleaned),
        "processed_columns": int(clustered.shape[1]),
        "association_rules": int(len(rules)),
        "best_classification_model": classification_metrics.iloc[0]["model"],
        "best_classification_f1": classification_metrics.iloc[0]["f1_macro"],
        "best_clustering_algorithm": clustering_metrics.sort_values("silhouette", ascending=False).iloc[0]["algorithm"],
        "best_clustering_silhouette": clustering_metrics["silhouette"].max(),
    }
    save_json(summary, TABLES_DIR / "run_summary.json")
    return summary
