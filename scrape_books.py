"""
Playwright demo: scrape book data from a practice website and save it to CSV.

Shows: browser automation, waiting for elements, pagination, retries,
error handling, logging, CLI arguments and clean data output.

Target site: https://books.toscrape.com (built for scraping practice).
"""

import argparse
import csv
import logging
import re
import time

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

BASE_URL = "https://books.toscrape.com/"
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

log = logging.getLogger("scraper")


def with_retry(action, attempts=3, delay=2):
    """Run action(); retry on timeout so one slow page does not kill the run."""
    for attempt in range(1, attempts + 1):
        try:
            return action()
        except PlaywrightTimeout as exc:
            log.warning("Attempt %d/%d timed out: %s", attempt, attempts, exc)
            if attempt == attempts:
                raise
            time.sleep(delay)


def scrape_current_page(page):
    """Extract every book card on the page currently open."""
    books = []
    for card in page.locator("article.product_pod").all():
        title = card.locator("h3 a").get_attribute("title")
        price_text = card.locator(".price_color").inner_text()
        rating_word = card.locator("p.star-rating").get_attribute("class").split()[-1]
        availability = card.locator(".availability").inner_text()

        books.append(
            {
                "title": title,
                "price": float(re.sub(r"[^\d.]", "", price_text)),
                "rating": RATINGS.get(rating_word, 0),
                "in_stock": "In stock" in availability,
            }
        )
    return books


def run(max_pages, output_file, headless):
    all_books = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.set_default_timeout(10_000)  # 10 s max wait for any element

        with_retry(lambda: page.goto(BASE_URL))

        for page_number in range(1, max_pages + 1):
            page.wait_for_selector("article.product_pod")
            books = scrape_current_page(page)
            all_books.extend(books)
            log.info("Page %d: scraped %d books", page_number, len(books))

            next_link = page.locator("li.next a")
            if next_link.count() == 0:  # last page reached
                log.info("No more pages.")
                break
            next_link.click()
            page.wait_for_load_state("domcontentloaded")

        browser.close()

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "rating", "in_stock"])
        writer.writeheader()
        writer.writerows(all_books)

    return all_books


def print_summary(books):
    if not books:
        print("No books scraped.")
        return
    avg_price = sum(b["price"] for b in books) / len(books)
    five_star = sum(1 for b in books if b["rating"] == 5)
    print(f"\nScraped {len(books)} books")
    print(f"Average price: £{avg_price:.2f}")
    print(f"5-star books:  {five_star}")


def main():
    parser = argparse.ArgumentParser(description="Scrape books.toscrape.com to CSV")
    parser.add_argument("--pages", type=int, default=3, help="max pages to scrape")
    parser.add_argument("--output", default="books.csv", help="CSV output file")
    parser.add_argument("--show-browser", action="store_true", help="watch it run")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    try:
        books = run(args.pages, args.output, headless=not args.show_browser)
    except PlaywrightTimeout:
        log.error("Site did not respond in time. Try again later.")
        raise SystemExit(1)

    print_summary(books)
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
