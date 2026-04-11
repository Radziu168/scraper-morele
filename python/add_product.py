import sys
import sqlite3
from pathlib import Path
from playwright.sync_api import sync_playwright
from logger import get_logger
from scraper import init_db, upsert_product_by_url, save_price, scrape_product

logger = get_logger("add_product")

DB_FILE = Path(__file__).parent / "data" / "prices.db"

def add_product(url: str):
    logger.info(f"Dodaję produkt: {url}")

    conn = sqlite3.connect(DB_FILE)
    init_db(conn)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        try:
            result = scrape_product(page, url)
        except Exception as e:
            logger.error(f"Błąd scrapowania: {e}")
            browser.close()
            conn.close()
            sys.exit(1)

        if not result:
            logger.error("Nie znaleziono danych produktu")
            browser.close()
            conn.close()
            sys.exit(1)

        product_id = upsert_product_by_url(
            conn,
            name=result["name"],
            url=url,
            category="Inne"
        )
        save_price(conn, product_id, result["price"])

        logger.info(f"✅ Dodano: {result['name']} — {result['price']} zł")

        browser.close()
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie: python add_product.py <url>")
        sys.exit(1)
    add_product(sys.argv[1])