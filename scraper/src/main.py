import os
import requests

# Configuration
TARGET_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "catalogue-page-1.html")
USER_AGENT = "FlyRankInternship A9/1.0 (+https://github.com/smrithipiedy/FlyRank_Internship_Assignments)"
TIMEOUT = 10  # seconds

def fetch_page():
    """
    Fetches the target page with caching logic.
    Returns the HTML content if successful, otherwise None.
    """
    # Ensure cache directory exists relative to the project root (scraper/)
    # The script is run from scraper/ so we use relative paths
    os.makedirs(CACHE_DIR, exist_ok=True)

    # 1. Check for cache first
    if os.path.exists(CACHE_FILE):
        print("CACHE HIT")
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"Response size: {len(content)} bytes")
            return content
        except Exception as e:
            print(f"Error reading cache: {e}")

    # 2. Fetch from the web
    print("FETCH")
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=TIMEOUT)

        # 3. Check status code
        if response.status_code == 200:
            content = response.text

            # 4. Save to cache
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Response size: {len(content)} bytes")
            return content
        else:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during fetch: {e}")
        return None

if __name__ == "__main__":
    # Run the fetcher
    html = fetch_page()
    if html:
        # HTML is successfully retrieved (either via FETCH or CACHE HIT)
        # We do NOT dump the HTML to the terminal as per requirements
        pass
