import { NextResponse } from "next/server";
import { getDb, ProductWithPrice } from "@/lib/db";

export async function GET() {
  try {
    const db = getDb();
    const products = db
      .prepare(
        `
      SELECT
        p.id,
        p.name,
        p.url,
        p.category,
        h1.price   AS current_price,
        h1.scraped_at,
        h2.price   AS previous_price
      FROM products p
      LEFT JOIN price_history h1
        ON h1.product_id = p.id
        AND h1.id = (
          SELECT id FROM price_history
          WHERE product_id = p.id
          ORDER BY scraped_at DESC LIMIT 1
        )
      LEFT JOIN price_history h2
        ON h2.product_id = p.id
        AND h2.id = (
          SELECT id FROM price_history
          WHERE product_id = p.id
          ORDER BY scraped_at DESC LIMIT 1 OFFSET 1
        )
      ORDER BY p.id
    `,
      )
      .all() as ProductWithPrice[];

    db.close();
    return NextResponse.json({
      products,
      generated_at: new Date().toISOString(),
    });
  } catch (error) {
    console.error("DB error:", error);
    return NextResponse.json({ error: "Błąd bazy danych" }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const { url } = await request.json();

    // Walidacja — czy to URL Morele
    if (!url || !url.includes("morele.net")) {
      return NextResponse.json(
        { error: "Podaj prawidłowy URL produktu z morele.net" },
        { status: 422 },
      );
    }

    // Wywołaj Python scraper dla jednego URL
    const { execSync } = await import("child_process");
    const pythonPath = process.env.PYTHON_PATH || "python";
    const scriptPath = "../python/add_product.py";

    execSync(`${pythonPath} ${scriptPath} "${url}"`, {
      encoding: "utf-8",
      timeout: 30000,
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Add product error:", error);
    return NextResponse.json(
      { error: "Nie udało się dodać produktu" },
      { status: 500 },
    );
  }
}
