from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
TABLES_DIR = REPORTS_DIR / "tables"
MODELS_DIR = ROOT_DIR / "models"
BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = f"{BASE_URL}catalogue/page-1.html"
RAW_DATA_PATH = RAW_DIR / "books_seed.csv"
SCRAPED_DATA_PATH = RAW_DIR / "books_scraped.csv"
CLEAN_DATA_PATH = INTERIM_DIR / "books_cleaned.csv"
FEATURE_DATA_PATH = PROCESSED_DIR / "books_features.csv"
RANDOM_STATE = 42
