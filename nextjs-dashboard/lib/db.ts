import Database from "better-sqlite3";
import path from "path";

const DB_PATH = path.join(process.cwd(), "..", "python", "data", "prices.db");

export function getDb() {
  return new Database(DB_PATH, { readonly: true });
}

export interface Product {
  id: number;
  name: string;
  url: string;
  category: string;
}

export interface PriceRecord {
  id: number;
  product_id: number;
  price: number;
  scraped_at: string;
}

export interface ProductWithPrice extends Product {
  current_price: number | null;
  previous_price: number | null;
  scraped_at: string | null;
}
