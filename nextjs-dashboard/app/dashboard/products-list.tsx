"use client";

import { useState, useMemo } from "react";
import { ProductWithPrice } from "@/lib/db";

function PriceDiff({
  current,
  previous,
}: {
  current: number;
  previous: number | null;
}) {
  if (!previous || current === previous) {
    return <span className="text-gray-400 text-sm">⚪ bez zmian</span>;
  }
  const diff = current - previous;
  const pct = ((diff / previous) * 100).toFixed(1);
  return diff < 0 ? (
    <span className="text-green-600 text-sm font-mono">
      📉 -{Math.abs(diff).toFixed(2)} zł ({pct}%)
    </span>
  ) : (
    <span className="text-red-500 text-sm font-mono">
      📈 +{diff.toFixed(2)} zł (+{pct}%)
    </span>
  );
}

type SortKey = "name" | "price_asc" | "price_desc" | "change";

interface Props {
  products: ProductWithPrice[];
}

export default function ProductsList({ products }: Props) {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("Wszystkie");
  const [sort, setSort] = useState<SortKey>("name");

  // Unikalne kategorie z danych
  const categories = useMemo(() => {
    const cats = new Set(products.map((p) => p.category).filter(Boolean));
    return ["Wszystkie", ...Array.from(cats)];
  }, [products]);

  // Filtrowanie + sortowanie
  const filtered = useMemo(() => {
    let list = [...products];

    // Filtr tekstowy
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter((p) => p.name.toLowerCase().includes(q));
    }

    // Filtr kategorii
    if (category !== "Wszystkie") {
      list = list.filter((p) => p.category === category);
    }

    // Sortowanie
    list.sort((a, b) => {
      switch (sort) {
        case "name":
          return a.name.localeCompare(b.name, "pl");
        case "price_asc":
          return (a.current_price ?? 0) - (b.current_price ?? 0);
        case "price_desc":
          return (b.current_price ?? 0) - (a.current_price ?? 0);
        case "change": {
          const diffA = a.previous_price
            ? a.current_price! - a.previous_price
            : 0;
          const diffB = b.previous_price
            ? b.current_price! - b.previous_price
            : 0;
          return diffA - diffB; // największy spadek na górze
        }
        default:
          return 0;
      }
    });

    return list;
  }, [products, search, category, sort]);

  return (
    <div>
      {/* Pasek filtrów */}
      <div className="flex flex-wrap gap-3 mb-6">
        {/* Wyszukiwarka */}
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Szukaj produktu..."
          className="border rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-blue-500 flex-1 min-w-48"
        />

        {/* Filtr kategorii */}
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="border rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-blue-500 bg-white"
        >
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>

        {/* Sortowanie */}
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as SortKey)}
          className="border rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-blue-500 bg-white"
        >
          <option value="name">Sortuj: A–Z</option>
          <option value="price_asc">Sortuj: cena rosnąco</option>
          <option value="price_desc">Sortuj: cena malejąco</option>
          <option value="change">Sortuj: największy spadek</option>
        </select>
      </div>

      {/* Licznik wyników */}
      <p className="text-xs text-gray-400 mb-4 font-mono">
        {filtered.length} z {products.length} produktów
      </p>

      {/* Lista produktów */}
      {filtered.length === 0 ? (
        <p className="text-gray-400 text-sm">
          Brak produktów spełniających kryteria.
        </p>
      ) : (
        <div className="grid gap-4">
          {filtered.map((product) => (
            <div
              key={product.id}
              className="border rounded-lg p-5 hover:border-blue-500 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <span className="text-xs text-gray-400 uppercase tracking-wide">
                    {product.category}
                  </span>
                  <h2 className="font-bold truncate">{product.name}</h2>
                  <a
                    href={product.url}
                    target="_blank"
                    className="text-xs text-blue-400 hover:underline"
                  >
                    morele.net →
                  </a>
                </div>

                <div className="text-right flex-shrink-0">
                  <p className="text-2xl font-mono font-bold">
                    {product.current_price?.toFixed(2)} zł
                  </p>
                  <PriceDiff
                    current={product.current_price!}
                    previous={product.previous_price}
                  />
                </div>
              </div>

              <p className="text-xs text-gray-400 mt-3 font-mono">
                ostatni scraping:{" "}
                {new Date(product.scraped_at!).toLocaleString("pl-PL")}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
