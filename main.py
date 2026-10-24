import argparse
from pathlib import Path

from src.config import RAW_DATA_PATH, SCRAPED_DATA_PATH
from src.data_loader import save_csv
from src.pipeline import run_pipeline
from src.web_scraper import BooksScraper, ScraperSettings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scrape", action="store_true")
    parser.add_argument("--max-pages", type=int, default=None)
    parser.add_argument("--delay", type=float, default=0.35)
    parser.add_argument("--association-engine", choices=["manual", "mlxtend"], default="manual")
    parser.add_argument("--input", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_path = args.input or RAW_DATA_PATH
    if args.scrape:
        scraper = BooksScraper(ScraperSettings(delay=args.delay, max_pages=args.max_pages))
        scraped = scraper.scrape()
        save_csv(scraped, SCRAPED_DATA_PATH)
        raw_path = SCRAPED_DATA_PATH
    summary = run_pipeline(raw_path, association_engine=args.association_engine)
    print("Pipeline completed")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
