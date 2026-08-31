# Polite Web Scraper

A professional web scraping project designed to practice ethical data extraction techniques, respecting site rules and implementing responsible fetching.

## Target Classification

- **Target Site**: [books.toscrape.com](https://books.toscrape.com/)
- **Classification**: Sandbox. The site explicitly states: "This is a demo website for web scraping purposes."
- **Scope**: First 3 catalogue pages only.
- **Data to Collect**: Book titles, prices, and star ratings.
- **Appropriateness**: Scraping this site is appropriate because it is a dedicated sandbox created specifically for developers to practice and test their scraping tools without impacting a real business.
- **Robots.txt Result**: No robots.txt file found.

I will not reuse this code on another site without checking its rules and terms first.

## Installation & Running

**Lane**: Engineering Intern

### Installation
Install the required dependencies via pip:
```bash
pip install requests beautifulsoup4 pydantic
```

### Running the Scraper
Run the script from the `scraper` directory:
```bash
python src/main.py
```

## Data Schema

Each book record follows this schema:

| Field | Type | Description |
| :--- | :--- | :--- |
| `title` | string | The full title of the book |
| `product_url` | URL | The canonical URL of the book detail page |
| `price_text` | string | The raw price string (e.g., "£51.77") |
| `price_gbp` | float | The numeric price in GBP |
| `availability_text` | string | Raw availability text from the page |
| `rating_text` | string | Star rating (e.g., "Three") |
| `description` | string (opt) | The book description text |
| `source_page` | URL | The catalogue page where the book was found |
| `fetched_at` | timestamp | ISO 8601 UTC timestamp of extraction |

## Politeness Rules

To ensure responsible scraping, the following rules are implemented:
- **User-Agent**: `FlyRankInternship A9/1.0 (+https://github.com/smrithipiedy/FlyRank_Internship_Assignments)`
- **Delay**: A minimum delay of 0.5 seconds between real network requests.
- **Timeout**: All requests have a strict 10-second timeout.
- **Caching**: Implements local file-based caching for HTML pages to prevent redundant requests to the server.
- **Retries**: Only retries on server errors (5xx) or network timeouts. Does not retry 403 or 404 errors.

## Limitations
The scraper is currently limited to the first 3 pages of the catalogue as per the project scope.

## Proof of Run

### Run Report
```json
{
  "start_time": "2026-08-29T13:16:08.839734+00:00Z",
  "duration_seconds": 98.149441,
  "pages_fetched": 61,
  "cache_hits": 3,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}
```

**Why no browser?**
This assignment needed no browser because the data is already in the HTML the server sends, so a browser would only add unnecessary cost and complexity.

## Ethics Note
I adhere to the following ethical guidelines:
- **API First**: I will always use an official API if one is provided by the service.
- **Respect Barriers**: I will never attempt to bypass logins, paywalls, or site-implemented blocks.
- **Minimalism**: I collect only the specific data needed for the task to minimize server load.
