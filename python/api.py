from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import os
from turso import query

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*", "x-api-key"],
)

API_KEY = os.getenv("API_KEY", "dev-key")
api_key_header = APIKeyHeader(name="x-api-key")

def verify_key(key: str = Depends(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Nieautoryzowany")

@app.get("/produkty", dependencies=[Depends(verify_key)])
def pobierz_produkty():
    return query("""
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
    """)

@app.get("/produkty/{product_id}/historia", dependencies=[Depends(verify_key)])
def historia_cen(product_id: int):
    return query("""
        SELECT price, scraped_at
        FROM price_history
        WHERE product_id = ?
        ORDER BY scraped_at ASC
    """, [product_id])