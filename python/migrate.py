import sqlite3
import requests
from pathlib import Path
from dotenv import load_dotenv
import os
import json

load_dotenv()

DB_FILE = Path(__file__).parent / "data" / "prices.db"
TURSO_URL = os.getenv("TURSO_URL").replace("libsql://", "https://")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

def execute_turso(sql: str, params: list = []):
    res = requests.post(
        f"{TURSO_URL}/v2/pipeline",
        headers={
            "Authorization": f"Bearer {TURSO_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "requests": [
                {
                    "type": "execute",
                    "stmt": {
                        "sql": sql,
                        "args": [{"type": "text", "value": str(p)} for p in params]
                    }
                },
                {"type": "close"}
            ]
        }
    )
    return res.json()

def migrate():
    local = sqlite3.connect(DB_FILE)
    local.row_factory = sqlite3.Row

    produkty = local.execute("SELECT * FROM products").fetchall()
    historia = local.execute("SELECT * FROM price_history").fetchall()

    print(f"Produkty: {len(produkty)}, Historia: {len(historia)}")

    # Stwórz tabele
    execute_turso("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            category TEXT
        )
    """)
    execute_turso("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price REAL NOT NULL,
            scraped_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    for p in produkty:
        execute_turso(
            "INSERT OR IGNORE INTO products (id, name, url, category) VALUES (?, ?, ?, ?)",
            [p["id"], p["name"], p["url"], p["category"]]
        )
        print(f"  ✓ {p['name']}")

    for h in historia:
        execute_turso(
            "INSERT OR IGNORE INTO price_history (id, product_id, price, scraped_at) VALUES (?, ?, ?, ?)",
            [h["id"], h["product_id"], h["price"], h["scraped_at"]]
        )

    print("Migracja zakończona!")

migrate()