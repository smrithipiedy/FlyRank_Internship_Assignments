import os
import requests
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "https://books.toscrape.com/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = "cache"
USER_AGENT = "FlyRankInternship A9/1.0 (+https://github.com/smrithipiedy/FlyRank_Internship_Assignments)"
TIMEOUT = 10
DELAY = 0.5  # seconds between real requests

def get_cache_filename(url):
    """Generates a cache filename based on the URL path."""
    # The user already has files named page-1.html, page-2.html, page-3.html
    # We need to match that specific pattern
    if "page-1.html" in url:
        return os.path.join(CACHE_DIR, "page-1.html")
    elif "page-2.html" in url:
        return os.path.join(CACHE_DIR, "page-2.html")
    elif "page-3.html" in url:
        return os.path.join(CACHE_DIR, "page-3.html")

    # Fallback for other pages
    filename = url.split("/")[-1]
    if not filename:
        filename = "index.html"
    return os.path.join(CACHE_DIR, filename)

def get_html(url):
    """
    Fetches HTML from the URL with caching and politeness.
    Returns the HTML content if successful, otherwise None.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = get_cache_filename(url)

    # 1. Check for cache first (No delay for cached pages)
    if os.path.exists(cache_file):
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
            # Save to cache
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(content)
            return content
        else:
            print(f"Failed to fetch {url}. Status: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    current_url = START_URL
    pages_visited = 0
    discovered_links = []

    while current_url and pages_visited < 3:
        html = get_html(current_url)
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")

        # Collect book links from the current page
        # Selector: h3 a (based on books.toscrape structure)
        books = soup.select("h3 a")
        for a in books:
            href = a.get("href")
            # Convert relative to absolute URL using urljoin
            absolute_url = urljoin(current_url, href)
            discovered_links.append(absolute_url)

        # Discover the 'next' page link
        next_link = soup.select_one(".next a")
        if next_link:
            next_href = next_link.get("href")
            current_url = urljoin(current_url, next_href)
        else:
            current_url = None

        pages_visited += 1

    # Remove duplicate links
    unique_urls = set(discovered_links)

    # Checkpoint Output
    print(f"catalogue_pages={pages_visited}, discovered={len(discovered_links)}, unique_urls={len(unique_urls)}")

if __name__ == "__main__":
    main()
