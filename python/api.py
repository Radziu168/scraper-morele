from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
import sqlite3
import os
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://twój-url.vercel.app"],  # zmień na swój URL
    allow_methods=["GET"],
    allow_headers=["*", "x-api-key"],
)

DB_FILE = Path(__file__).parent / "data" / "prices.db"

API_KEY = os.getenv("API_KEY", "dev-key")
api_key_header = APIKeyHeader(name="x-api-key")

def verify_key(key: str = Depends(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Nieautoryzowany")

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/produkty", dependencies=[Depends(verify_key)])
def pobierz_produkty():
    conn = get_conn()
    produkty = conn.execute("""
        SELECT p.id, p.name, p.url, p.category,
               ph.price as aktualna_cena,
               ph.scraped_at as ostatnia_aktualizacja
        FROM products p
        LEFT JOIN price_history ph ON ph.id = (
            SELECT id FROM price_history
            WHERE product_id = p.id
            ORDER BY scraped_at DESC LIMIT 1
        )
    """).fetchall()
    conn.close()
    return [dict(r) for r in produkty]

@app.get("/produkty/{product_id}/historia", dependencies=[Depends(verify_key)])
def historia_cen(product_id: int):
    conn = get_conn()
    historia = conn.execute("""
        SELECT price, scraped_at
        FROM price_history
        WHERE product_id = ?
        ORDER BY scraped_at ASC
    """, (product_id,)).fetchall()
    conn.close()
    return [dict(r) for r in historia]