# Playwright Book Scraper (Python)

A small browser-automation demo built with Python and Playwright. It opens a
practice bookstore site, walks through the pages, extracts book data and saves
it to CSV.

## What it demonstrates

- Browser automation with Playwright (sync API, headless Chromium)
- Waiting for elements instead of fixed sleeps
- Pagination across multiple pages
- Retry logic and timeout handling
- Logging, CLI arguments and a clean CSV output
- Runs on Linux, macOS and Windows

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install playwright
playwright install chromium
```

## Run

```bash
python scrape_books.py                    # 3 pages -> books.csv
python scrape_books.py --pages 10         # more pages
python scrape_books.py --show-browser     # watch the browser work
```

## Output

`books.csv` with columns: `title, price, rating, in_stock`, plus a short
summary in the terminal (total books, average price, number of 5-star books).

## Notes

Target site: [books.toscrape.com](https://books.toscrape.com), a sandbox made
for scraping practice.

Author: Chit Lwin
