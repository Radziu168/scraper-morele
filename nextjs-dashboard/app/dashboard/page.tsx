import { ProductWithPrice } from "@/lib/db";
import AddProductForm from "./add-product-form";
import ProductsList from "./products-list";

async function getProducts(): Promise<ProductWithPrice[]> {
  try {
    const res = await fetch("http://localhost:3000/api/products", {
      cache: "no-store",
    });
    const data = await res.json();
    return data.products;
  } catch {
    return [];
  }
}

export default async function DashboardPage() {
  const products = await getProducts();

  return (
    <main className="p-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-2">💰 Price Monitor — Dashboard</h1>
      <p className="text-gray-400 text-sm mb-6">
        {products.length} produktów · ostatnia aktualizacja:{" "}
        {new Date().toLocaleString("pl-PL")}
      </p>

      <AddProductForm />

      {products.length === 0 ? (
        <p className="text-red-500">
          ❌ Brak danych — uruchom <code>python scraper.py</code>
        </p>
      ) : (
        <ProductsList products={products} />
      )}
    </main>
  );
}
