import time
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.config import BASE_URL, CATALOGUE_URL
from src.utils import normalize_whitespace


@dataclass
class ScraperSettings:
    delay: float = 0.35
    timeout: int = 25
    max_pages: int | None = None


class BooksScraper:
    def __init__(self, settings: ScraperSettings | None = None) -> None:
        self.settings = settings or ScraperSettings()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "EducationalDataMiningProject/1.0"})

    def get_soup(self, url: str) -> BeautifulSoup:
        response = self.session.get(url, timeout=self.settings.timeout)
        response.raise_for_status()
        time.sleep(self.settings.delay)
        return BeautifulSoup(response.text, "html.parser")

    def catalogue_urls(self) -> Iterable[str]:
        current_url = CATALOGUE_URL
        page_count = 0
        while current_url:
            yield current_url
            page_count += 1
            if self.settings.max_pages and page_count >= self.settings.max_pages:
                break
            soup = self.get_soup(current_url)
            next_link = soup.select_one("li.next a")
            current_url = urljoin(current_url, next_link["href"]) if next_link else ""

    def product_urls(self, catalogue_url: str) -> list[str]:
        soup = self.get_soup(catalogue_url)
        return [urljoin(catalogue_url, anchor["href"]) for anchor in soup.select("article.product_pod h3 a")]

    def parse_product(self, url: str) -> dict[str, object]:
        soup = self.get_soup(url)
        title = normalize_whitespace(soup.select_one("div.product_main h1").get_text(" ", strip=True))
        price_text = normalize_whitespace(soup.select_one("p.price_color").get_text(" ", strip=True))
        availability = normalize_whitespace(soup.select_one("p.instock.availability").get_text(" ", strip=True))
        breadcrumb = [normalize_whitespace(item.get_text(" ", strip=True)) for item in soup.select("ul.breadcrumb li")]
        category = breadcrumb[-2] if len(breadcrumb) >= 2 else "Unknown"
        description_node = soup.select_one("#product_description + p")
        description = normalize_whitespace(description_node.get_text(" ", strip=True)) if description_node else ""
        rating_node = soup.select_one("p.star-rating")
        rating = next((item for item in rating_node.get("class", []) if item != "star-rating"), "Unknown") if rating_node else "Unknown"
        table = {}
        for row in soup.select("table.table.table-striped tr"):
            key = normalize_whitespace(row.select_one("th").get_text(" ", strip=True))
            value = normalize_whitespace(row.select_one("td").get_text(" ", strip=True))
            table[key] = value
        image_node = soup.select_one("div.item.active img")
        image_url = urljoin(url, image_node["src"]) if image_node else ""
        return {
            "detail_url": url,
            "image_url": image_url,
            "title": title,
            "category": category,
            "rating": rating,
            "price": price_text,
            "availability": availability,
            "description": description,
            "upc": table.get("UPC", ""),
            "product_type": table.get("Product Type", ""),
            "price_excluding_tax": table.get("Price (excl. tax)", ""),
            "price_including_tax": table.get("Price (incl. tax)", ""),
            "tax": table.get("Tax", ""),
            "number_of_reviews": table.get("Number of reviews", ""),
        }

    def scrape(self) -> pd.DataFrame:
        rows = []
        seen = set()
        for catalogue_url in self.catalogue_urls():
            for product_url in self.product_urls(catalogue_url):
                if product_url in seen:
                    continue
                rows.append(self.parse_product(product_url))
                seen.add(product_url)
        return pd.DataFrame(rows)
