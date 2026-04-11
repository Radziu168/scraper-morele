"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function AddProductForm() {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");
  const [error, setError] = useState("");
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("loading");
    setError("");

    try {
      const res = await fetch("/api/products", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Błąd serwera");
        setStatus("error");
        return;
      }

      setUrl("");
      setStatus("idle");
      router.refresh(); // odśwież dashboard
    } catch {
      setError("Błąd połączenia z serwerem");
      setStatus("error");
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 mb-8">
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Wklej URL produktu z morele.net..."
        required
        disabled={status === "loading"}
        className="flex-1 border rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={status === "loading" || !url}
        className="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-bold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
      >
        {status === "loading" ? "⏳ Dodaję..." : "+ Dodaj produkt"}
      </button>
      {error && <p className="text-red-500 text-sm self-center">{error}</p>}
    </form>
  );
}
