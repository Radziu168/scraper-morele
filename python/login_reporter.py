import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Ładuj zmienne środowiskowe z .env
load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SESSION_FILE = DATA_DIR / "session.json"
PRODUCTS_FILE = DATA_DIR / "products.json"
CONFIG_FILE = BASE_DIR / "config.json"

def load_config() -> dict:
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)

def login_and_save_session(page) -> bool:
    """Loguje się i zapisuje sesję. Zwraca True jeśli sukces."""
    print("🔐 Loguję się...")

    page.goto(os.getenv("LOGIN_URL"))
    page.fill("#username", os.getenv("SITE_USERNAME"))
    page.fill("#password", os.getenv("SITE_PASSWORD"))
    page.click("button[type='submit']")

    try:
        page.wait_for_selector(".flash.success", timeout=15000)
        print("✅ Zalogowano!")
        return True
    except Exception:
        print("❌ Błąd logowania!")
        return False

def scrape_protected_page(page, url: str) -> dict:
    """Pobiera dane z chronionej strony."""
    page.goto(url)

    # Pobierz tekst z głównej sekcji
    try:
        heading = page.locator("h2").inner_text()
        content = page.locator(".example").inner_text()
    except Exception:
        heading = "Brak danych"
        content = ""

    return {
        "heading": heading.strip(),
        "content": content.strip(),
        "scraped_at": datetime.now().isoformat()
    }

def run():
    config = load_config()
    DATA_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # --- FAZA 1: Logowanie ---
        success = login_and_save_session(page)
        if not success:
            browser.close()
            return

        # Zapisz sesję
        context.storage_state(path=str(SESSION_FILE))
        print(f"💾 Sesja zapisana → {SESSION_FILE}")

        results = []
        products = config["products"]
        print(f"\n📦 Pobieram dane dla {len(products)} produktów...")

        for product in products:
            print(f"  → {product['name']}...")
            scraped = scrape_protected_page(page, product["url"])
            results.append({
                "id": product["id"],
                "name": product["name"],
                "category": product["category"],
                "url": product["url"],
                **scraped
            })

        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "count": len(results),
                "products": results
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Zapisano {len(results)} produktów → {PRODUCTS_FILE}")
        browser.close()
if __name__ == "__main__":
    run()