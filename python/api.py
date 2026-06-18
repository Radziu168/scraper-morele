from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import sqlite3
import os
from pathlib import Path

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dashboardv1-black.vercel.app"],  # zmień na swój URL
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
               ph1.price as aktualna_cena,
               ph1.scraped_at as ostatnia_aktualizacja,
               ph2.price as poprzednia_cena
        FROM products p
        LEFT JOIN price_history ph1 ON ph1.id = (
            SELECT id FROM price_history
            WHERE product_id = p.id
            ORDER BY scraped_at DESC LIMIT 1
        )
        LEFT JOIN price_history ph2 ON ph2.id = (
            SELECT id FROM price_history
            WHERE product_id = p.id
            ORDER BY scraped_at DESC LIMIT 1 OFFSET 1
        )
    """).fetchall()
    conn.close()
    return [dict(r) for r in produkty]