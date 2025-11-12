"""
Scheduler for daily PhilGEPS scraping
Runs at 2 AM Manila time every day
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from scraper.philgeps_scraper import PhilGEPSScraper
import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def daily_scrape_job():
    """Daily scraping job"""
    logger.info("="*60)
    logger.info(f"Starting daily scrape job at {datetime.now()}")
    logger.info("="*60)

    scraper = PhilGEPSScraper()

    try:
        result = await scraper.run_daily_scrape()

        if result['success']:
            logger.info(f"✅ Scrape successful: {result['saved_count']} bids saved")
        else:
            logger.error(f"❌ Scrape failed: {result.get('error')}")

    except Exception as e:
        logger.error(f"❌ Unexpected error during scrape: {e}", exc_info=True)

    finally:
        scraper.close()


def start_scheduler():
    """Start the APScheduler"""
    scheduler = AsyncIOScheduler(timezone='Asia/Manila')

    # Schedule daily at 2 AM Manila time
    scheduler.add_job(
        daily_scrape_job,
        CronTrigger(hour=2, minute=0, timezone='Asia/Manila'),
        id='daily_philgeps_scrape',
        name='Daily PhilGEPS Scrape',
        replace_existing=True
    )

    # Optional: Run immediately on startup for testing
    # scheduler.add_job(daily_scrape_job, 'date', run_date=datetime.now())

    scheduler.start()

    logger.info("⏰ Scheduler started")
    logger.info("📅 Daily scraping scheduled for 2:00 AM Manila time")
    logger.info("   Next run: " + str(scheduler.get_jobs()[0].next_run_time))

    return scheduler


if __name__ == "__main__":
    # Start scheduler
    scheduler = start_scheduler()

    # Keep the script running
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
