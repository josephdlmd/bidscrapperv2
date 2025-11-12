"""
Main entry point for PhilGEPS Scraper Service
Runs both FastAPI server and scheduler together
"""

import asyncio
import uvicorn
from scheduler import start_scheduler
from dotenv import load_dotenv
import logging
import os

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Start both the FastAPI server and the scheduler
    """
    logger.info("="*60)
    logger.info("🚀 Starting PhilGEPS Scraper Service")
    logger.info("="*60)

    # Validate environment variables
    required_vars = ['PHILGEPS_USERNAME', 'PHILGEPS_PASSWORD', 'DATABASE_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("   Please check your .env file")
        return

    logger.info("✅ Environment variables configured")

    # Start scheduler in background
    scheduler = start_scheduler()
    logger.info("✅ Scheduler started")

    # Start FastAPI server
    port = int(os.getenv("PORT", 8000))
    logger.info(f"✅ Starting API server on port {port}")
    logger.info("="*60 + "\n")

    try:
        uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down...")
        scheduler.shutdown()
        logger.info("✅ Shutdown complete")


if __name__ == "__main__":
    main()
