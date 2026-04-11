import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from logger import get_logger
import scraper

load_dotenv()
logger = get_logger("scheduler")

INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))


def job():
    logger.info("⏰ Scheduler uruchamia scraper...")
    try:
        scraper.run()
        logger.info("✅ Scraper zakończył pracę")
    except Exception as e:
        logger.error(f"❌ Błąd scrapera: {e}")


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    scheduler.add_job(
        job,
        trigger=IntervalTrigger(hours=INTERVAL_HOURS),
        id="price_scraper",
        name="Price Monitor Scraper",
        replace_existing=True
    )

    logger.info(f"🚀 Scheduler uruchomiony — scraping co {INTERVAL_HOURS}h")
    logger.info("   Ctrl+C aby zatrzymać")

    job()

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("⛔ Scheduler zatrzymany")
        scheduler.shutdown()