import os
import requests
import time
import json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, ValidationError
from typing import Optional

# Configuration
BASE_URL = "https://books.toscrape.com/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"

# Use paths relative to the script location to ensure they stay within the scraper folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CACHE_DIR = os.path.join(PROJECT_ROOT, "cache")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

USER_AGENT = "FlyRankInternship A9/1.0 (+https://github.com/smrithipiedy/FlyRank_Internship_Assignments)"
TIMEOUT = 10
DELAY = 0.5  # seconds between real requests

class Book(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: Optional[str] = None
    source_page: HttpUrl
    fetched_at: str

def clean_price(price_text):
    """Extracts the numeric value from a price string like '£51.77'."""
    if not price_text:
        return None
    # Remove currency symbol and any whitespace
    cleaned = price_text.replace('£', '').replace('Â', '').strip()
    try:
        return float(cleaned)
    except ValueError:
        return None

def get_cache_filename(url):
    """Generates a cache filename based on the URL path."""
    # Match the existing pattern: page-1.html, page-2.html, etc.
    if "page-1.html" in url:
        return os.path.join(CACHE_DIR, "page-1.html")
    elif "page-2.html" in url:
        return os.path.join(CACHE_DIR, "page-2.html")
    elif "page-3.html" in url:
        return os.path.join(CACHE_DIR, "page-3.html")

    # For detail pages: use the end of the URL
    # e.g., .../a-light-in-the-attic_1000/index.html -> a-light-in-the-attic_1000.html
    parts = url.split("/")
    if len(parts) >= 2:
        filename = parts[-2] if parts[-1] == "index.html" else parts[-1]
        return os.path.join(CACHE_DIR, f"{filename}.html")

    return os.path.join(CACHE_DIR, "index.html")

def get_html(url, cache=True):
    """
    Fetches HTML from the URL with caching and politeness.
    Returns the HTML content if successful, otherwise None.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = get_cache_filename(url)

    # 1. Check for cache first (No delay for cached pages)
    if cache and os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            content = f.read()
        return content

    # 2. Polite Fetch (Wait at least half a second)
    time.sleep(DELAY)

    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)

        # 3. Check status code
        if response.status_code == 200:
            content = response.text
            # Save to cache only if requested
            if cache:
                with open(cache_file, "w", encoding="utf-8") as f:
                    f.write(content)
            return content
        else:
            print(f"Failed to fetch {url}. Status: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_book_details(url, source_page):
    """
    Extracts raw records from a book detail page.
    """
    html = get_html(url, cache=False)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Target the product area specifically
    product_main = soup.select_one(".product_main")
    if not product_main:
        return None

    # Extract fields
    title = product_main.find("h1").get_text(strip=True) if product_main.find("h1") else None
    price = product_main.select_one(".price_color").get_text(strip=True) if product_main.select_one(".price_color") else None
    availability = product_main.select_one(".availability").get_text(strip=True) if product_main.select_one(".availability") else None

    # Rating: extract the second class of .star-rating (e.g. ['star-rating', 'Three'])
    rating_el = product_main.select_one(".star-rating")
    rating = None
    if rating_el and rating_el.has_attr("class"):
        classes = rating_el.get("class", [])
        # Filter out 'star-rating' class to find the value
        rating_classes = [c for c in classes if c != "star-rating"]
        if rating_classes:
            rating = rating_classes[0]

    # Description: find #product_description, then first following <p>
    description = None
    desc_div = soup.find("div", id="product_description")
    if desc_div:
        p_tag = desc_div.find_next_sibling("p")
        if p_tag:
            description = p_tag.get_text(strip=True)

    return {
        "title": title,
        "product_url": url,
        "price_text": price,
        "availability_text": availability,
        "rating_text": rating,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat() + "Z"
    }

def main():
    current_url = START_URL
    pages_visited = 0
    book_map = {}

    # --- Discovery Phase ---
    while current_url and pages_visited < 3:
        html = get_html(current_url)
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")
        books = soup.select("h3 a")
        for a in books:
            href = a.get("href")
            absolute_url = urljoin(current_url, href)
            # Map book URL to its source catalogue page
            book_map[absolute_url] = current_url

        next_link = soup.select_one(".next a")
        if next_link:
            next_href = next_link.get("href")
            current_url = urljoin(current_url, next_href)
        else:
            current_url = None

        pages_visited += 1

    # --- Extraction, Cleaning & Validation Phase ---
    valid_books = []
    errors = []

    for book_url, source_url in book_map.items():
        raw_record = extract_book_details(book_url, source_url)
        if not raw_record:
            continue

        # 1. Clean data
        price_gbp = clean_price(raw_record.get("price_text"))
        cleaned_record = {**raw_record, "price_gbp": price_gbp}

        # 2. Validate with Pydantic
        try:
            book = Book(**cleaned_record)
            valid_books.append(book.model_dump(mode='json'))
        except ValidationError as e:
            errors.append({
                "record": raw_record,
                "error": e.errors()
            })

    # --- Storage Phase ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(os.path.join(OUTPUT_DIR, "books.json"), "w", encoding="utf-8") as f:
        json.dump(valid_books, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "errors.json"), "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2)

    # Checkpoint Output
    if valid_books:
        print(valid_books[0])

    print(f"books.json has exactly {len(valid_books)} records")

if __name__ == "__main__":
    main()
