import { NextResponse } from "next/server";
import { getDb, PriceRecord } from "@/lib/db";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const { id } = await params;
    const db = getDb();

    const product = db
      .prepare("SELECT * FROM products WHERE id = ?")
      .get(Number(id));

    if (!product) {
      return NextResponse.json(
        { error: "Produkt nie znaleziony" },
        { status: 404 },
      );
    }

    const history = db
      .prepare(
        `
      SELECT * FROM price_history
      WHERE product_id = ?
      ORDER BY scraped_at DESC
      LIMIT 50
    `,
      )
      .all(Number(id)) as PriceRecord[];

    db.close();
    return NextResponse.json({ product, history });
  } catch (error) {
    console.error("DB error:", error);
    return NextResponse.json({ error: "Błąd serwera" }, { status: 500 });
  }
}
