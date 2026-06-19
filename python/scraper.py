import json
import os
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv
from logger import get_logger
from notifier import notify
from turso import query, execute

load_dotenv()

logger = get_logger("scraper")

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"

def init_db():
    execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            category TEXT
        )
    """)
    execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price REAL NOT NULL,
            scraped_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

def upsert_product(product: dict):
    execute("""
        INSERT INTO products (id, name, url, category)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            name = excluded.name,
            category = excluded.category
    """, [product["id"], product["name"], product["url"], product.get("category", "Inne")])

def save_price(product_id: int, price: float):
    execute("""
        INSERT INTO price_history (product_id, price, scraped_at)
        VALUES (?, ?, ?)
    """, [product_id, price, datetime.now().isoformat()])

def get_last_price(product_id: int) -> float | None:
    rows = query("""
        SELECT price FROM price_history
        WHERE product_id = ?
        ORDER BY scraped_at DESC LIMIT 1
    """, [product_id])
    return rows[0]["price"] if rows else None

@retry(
    retry=retry_if_exception_type((PWTimeout, Exception)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def scrape_product(page, url: str) -> dict | None:
    logger.debug(f"Scrapuję: {url}")

    page.route("**/*", lambda route: route.abort()
        if route.request.resource_type in {"image", "stylesheet", "font", "media"}
        else route.continue_()
    )

    page.goto(url, timeout=30000)
    page.wait_for_selector("#product_price", timeout=10000)

    price_str = page.get_attribute("#product_price", "data-price")
    price = float(price_str) if price_str else None
    name = page.get_attribute(".prod-name", "data-default")

    if not price or not name:
        logger.warning(f"Brak danych na stronie: {url}")
        return None

    logger.debug(f"Pobrano: {name} — {price} zł")
    return {"name": name, "price": price}

def run():
    logger.info("=== Start scrapowania ===")

    with open(CONFIG_FILE, encoding="utf-8") as f:
        config = json.load(f)

    init_db()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        logger.info(f"Scrapuję {len(config['products'])} produktów")

        for product in config["products"]:
            logger.info(f"→ {product['name']}")
            upsert_product(product)
            last_price = get_last_price(product["id"])

            try:
                result = scrape_product(page, product["url"])
            except Exception as e:
                logger.error(f"Nie udało się pobrać {product['name']}: {e}")
                continue

            if result:
                price = result["price"]
                save_price(product["id"], price)

                if last_price is None:
                    logger.info(f"  💰 {price:.2f} zł (pierwsze pobranie)")
                elif price < last_price:
                    diff = last_price - price
                    pct = (diff / last_price) * 100
                    threshold = float(os.getenv("ALERT_THRESHOLD_PCT", "3"))
                    logger.info(f"  📉 {price:.2f} zł (spadła o {diff:.2f} zł)")
                    if pct >= threshold:
                        logger.info(f"  🔔 Wysyłam powiadomienie ({pct:.1f}% >= {threshold}%)")
                        notify(product["name"], product["url"], last_price, price)
                elif price > last_price:
                    logger.info(f"  📈 {price:.2f} zł (wzrosła o {price - last_price:.2f} zł)")
                else:
                    logger.info(f"  ⚪ {price:.2f} zł (bez zmian)")

        browser.close()

    logger.info("=== Koniec scrapowania ===")

if __name__ == "__main__":
    run()