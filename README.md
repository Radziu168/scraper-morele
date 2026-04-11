# 💰 Price Monitor

Automatyczny system śledzenia cen produktów z Morele.net. Scraper pobiera ceny co 6 godzin, zapisuje historię do bazy SQLite i wysyła powiadomienia na Discord oraz email gdy cena spadnie.

## Funkcje

- Automatyczne pobieranie cen z Morele.net co X godzin (APScheduler)
- Historia cen w bazie SQLite
- Powiadomienia o spadku ceny — Discord webhook + Gmail
- Dashboard Next.js z filtrowaniem, sortowaniem i diff cenami
- Dodawanie produktów przez wklejenie URL w dashboardzie
- Retry z exponential backoff (tenacity) + pełne logowanie

## Struktura projektu

```
price-monitor/
├── python/
│   ├── scraper.py          # główny scraper (Playwright + SQLite)
│   ├── scheduler.py        # APScheduler — uruchamia scraper co X godzin
│   ├── add_product.py      # dodawanie produktu przez URL
│   ├── notifier.py         # powiadomienia Discord + email
│   ├── logger.py           # konfiguracja logowania
│   ├── config.json         # lista produktów do śledzenia
│   ├── .env                # zmienne środowiskowe
│   └── data/
│       ├── prices.db       # baza SQLite z historią cen
│       └── scraper.log     # logi scrapera
└── nextjs-dashboard/
    ├── app/
    │   ├── api/products/   # API Route — GET lista, POST dodaj produkt
    │   ├── dashboard/      # strona dashboardu
    │   └── ...
    ├── lib/
    │   ├── db.ts           # połączenie z SQLite + typy
    │   └── types.ts        # TypeScript interfaces
    └── .env.local          # ścieżka do Python
```

## Wymagania

**Python:**

- Python 3.11+
- pip

**Node.js:**

- Node.js 20 LTS+
- npm

## Instalacja

### 1. Klonuj repozytorium

```bash
git clone https://github.com/Radziu168/scraper-morele.git
cd price-monitor
```

### 2. Setup Python

```bash
cd python
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install playwright requests python-dotenv apscheduler tenacity beautifulsoup4
playwright install chromium
```

### 3. Konfiguracja zmiennych środowiskowych

Utwórz plik `python/.env`:

```env
# Discord (opcjonalne)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/TWÓJ_WEBHOOK

# Gmail SMTP (opcjonalne)
SMTP_FROM=twój@gmail.com
SMTP_TO=docelowy@gmail.com
SMTP_PASSWORD=haslo_aplikacji_gmail

# Próg alertu w % (domyślnie 3%)
ALERT_THRESHOLD_PCT=3

# Interwał scrapowania w godzinach (domyślnie 6)
SCRAPE_INTERVAL_HOURS=6
```

> **Discord webhook:** Ustawienia kanału → Integracje → Webhooki → Nowy webhook
>
> **Gmail hasło aplikacji:** myaccount.google.com/apppasswords (wymaga włączonej weryfikacji dwuetapowej)

### 4. Dodaj produkty do śledzenia

Edytuj `python/config.json`:

```json
{
  "products": [
    {
      "id": 1,
      "name": "Nazwa produktu",
      "url": "https://www.morele.net/nazwa-produktu-12345678/",
      "category": "Kategoria"
    }
  ]
}
```

### 5. Setup Next.js dashboard

```bash
cd ../nextjs-dashboard
npm install
```

Utwórz `nextjs-dashboard/.env.local`:

```env
# Windows
PYTHON_PATH=C:\ścieżka_do\price-monitor\python\.venv\Scripts\python.exe

# Linux/Mac
PYTHON_PATH=/home/user/price-monitor/python/.venv/bin/python
```

## Uruchomienie

### Scraper jednorazowy

```bash
cd python
.venv\Scripts\activate   # Windows
python scraper.py
```

### Scheduler (scraping automatyczny co X godzin)

```bash
cd python
.venv\Scripts\activate   # Windows
python scheduler.py
```

Zatrzymaj przez `Ctrl+C` (poczekaj aż bieżący job skończy, ~15 sekund).

Aby wymusić zatrzymanie w PowerShell:

```powershell
Get-Process python | Stop-Process
```

### Dashboard Next.js

```bash
cd nextjs-dashboard
npm run dev
```

Otwórz `http://localhost:3000/dashboard`

### Dodanie nowego produktu

**Opcja A — przez dashboard:**
Wklej URL produktu z Morele.net w formularzu na górze strony i kliknij "Dodaj produkt".

**Opcja B — przez terminal:**

```bash
cd python
python add_product.py "https://www.morele.net/nazwa-produktu-12345678/"
```

**Opcja C — przez `config.json`:**
Dodaj produkt do pliku i uruchom `python scraper.py`.

## Jak działają powiadomienia

Alert jest wysyłany gdy cena produktu **spadnie o więcej niż X%** (domyślnie 3%, konfigurowane przez `ALERT_THRESHOLD_PCT` w `.env`).

Powiadomienie zawiera:

- Nazwę produktu
- Starą i nową cenę
- Kwotę i % oszczędności
- Link do produktu na Morele.net

## Stack technologiczny

| Warstwa       | Technologia                            |
| ------------- | -------------------------------------- |
| Scraping      | Python + Playwright                    |
| Baza danych   | SQLite (better-sqlite3)                |
| Scheduler     | APScheduler                            |
| Retry         | tenacity                               |
| Powiadomienia | Discord Webhook + Gmail SMTP           |
| Frontend      | Next.js 16 + TypeScript + Tailwind CSS |
| API           | Next.js Route Handlers                 |

## Logi

Logi scrapera trafiają do:

- **Konsola** — poziom INFO (podsumowania)
- **`python/data/scraper.log`** — poziom DEBUG (szczegóły)

Format: `rrrr-mm-dd gg:mm:ss [INFO] scraper — komunikat`
