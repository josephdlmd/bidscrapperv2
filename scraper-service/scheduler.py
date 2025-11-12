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
from pathlib import Path

# Import custom logging configuration
try:
    from logging_config import get_scheduler_logger, log_exception
    logger = get_scheduler_logger()
except ImportError:
    # Fallback to basic logging
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
        # Run scraper with report generation enabled
        result = await scraper.run_daily_scrape(
            max_pages=None,  # Scrape all pages
            fetch_details=True,  # Fetch full details
            filters={},  # No filters for daily run
            generate_report=True  # Generate summary reports
        )

        if result['success']:
            logger.info(f"✅ Scrape successful!")
            logger.info(f"   Total bids: {result.get('total_bids', 0)}")
            logger.info(f"   New bids: {result.get('new_bids', 0)}")
            logger.info(f"   Updated bids: {result.get('updated_bids', 0)}")
            logger.info(f"   Duration: {result.get('duration_seconds', 0):.1f}s")
            logger.info(f"   Success rate: {result.get('success_rate', 0):.1f}%")

            # Log report files if generated
            if result.get('report_files'):
                logger.info("📊 Reports generated:")
                for format_type, file_path in result['report_files'].items():
                    logger.info(f"   {format_type.upper()}: {file_path}")
        else:
            logger.error(f"❌ Scrape failed: {result.get('error')}")

        return result

    except Exception as e:
        logger.error(f"❌ Unexpected error during scrape: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}

    finally:
        scraper.close()
        logger.info("="*60)
        logger.info("Daily scrape job completed")
        logger.info("="*60)


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
