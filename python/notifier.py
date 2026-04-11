import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from logger import get_logger

load_dotenv()
logger = get_logger("notifier")

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")
SMTP_TO = os.getenv("SMTP_TO", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")


def send_discord(product_name: str, url: str, old_price: float, new_price: float):
    """Wyślij powiadomienie na Discord."""
    if not DISCORD_WEBHOOK_URL:
        logger.warning("Brak DISCORD_WEBHOOK_URL — pomijam Discord")
        return

    diff = old_price - new_price
    pct = (diff / old_price) * 100

    payload = {
        "embeds": [{
            "title": "📉 Spadek ceny!",
            "description": f"**{product_name}**",
            "color": 0x2ecc71,
            "fields": [
                {"name": "Stara cena", "value": f"{old_price:.2f} zł", "inline": True},
                {"name": "Nowa cena", "value": f"**{new_price:.2f} zł**", "inline": True},
                {"name": "Oszczędzasz", "value": f"{diff:.2f} zł ({pct:.1f}%)", "inline": True},
            ],
            "url": url,
            "footer": {"text": "Price Monitor"}
        }]
    }

    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if res.status_code == 204:
            logger.info(f"✅ Discord: wysłano alert dla {product_name}")
        else:
            logger.error(f"Discord błąd: {res.status_code} {res.text}")
    except Exception as e:
        logger.error(f"Discord wyjątek: {e}")


def send_email(product_name: str, url: str, old_price: float, new_price: float):
    """Wyślij powiadomienie email przez Gmail SMTP."""
    if not all([SMTP_FROM, SMTP_TO, SMTP_PASSWORD]):
        logger.warning("Brak danych SMTP — pomijam email")
        return

    diff = old_price - new_price
    pct = (diff / old_price) * 100

    subject = f"📉 Cena spadła: {product_name}"

    html = f"""
    <html><body>
    <h2>📉 Spadek ceny!</h2>
    <p><strong>{product_name}</strong></p>
    <table>
      <tr><td>Stara cena:</td><td>{old_price:.2f} zł</td></tr>
      <tr><td>Nowa cena:</td><td><strong>{new_price:.2f} zł</strong></td></tr>
      <tr><td>Oszczędzasz:</td><td>{diff:.2f} zł ({pct:.1f}%)</td></tr>
    </table>
    <p><a href="{url}">Zobacz produkt na Morele →</a></p>
    <hr><small>Price Monitor</small>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = SMTP_TO
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_FROM, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, SMTP_TO, msg.as_string())
        logger.info(f"✅ Email: wysłano alert dla {product_name}")
    except Exception as e:
        logger.error(f"Email wyjątek: {e}")


def notify(product_name: str, url: str, old_price: float, new_price: float):
    """Wyślij powiadomienia wszystkimi kanałami."""
    send_discord(product_name, url, old_price, new_price)
    send_email(product_name, url, old_price, new_price)