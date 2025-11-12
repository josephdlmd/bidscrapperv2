"""
FastAPI service for PhilGEPS scraper
Provides API endpoints for Next.js app to interact with scraper
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from scraper.philgeps_scraper import PhilGEPSScraper
import asyncio
import os

app = FastAPI(
    title="PhilGEPS Scraper API",
    description="API for scraping bid opportunities from PhilGEPS",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global scraper instance
scraper = PhilGEPSScraper()

# Store last scrape result
last_scrape_result: Optional[Dict] = None
scraping_in_progress = False


class ScrapeResponse(BaseModel):
    success: bool
    message: str
    scraped_count: Optional[int] = None
    saved_count: Optional[int] = None
    timestamp: str


class StatusResponse(BaseModel):
    scraping_in_progress: bool
    last_scrape: Optional[Dict] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "PhilGEPS Scraper API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database_url_configured": bool(os.getenv("DATABASE_URL")),
        "philgeps_credentials_configured": bool(
            os.getenv("PHILGEPS_USERNAME") and os.getenv("PHILGEPS_PASSWORD")
        )
    }


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get scraping status"""
    return {
        "scraping_in_progress": scraping_in_progress,
        "last_scrape": last_scrape_result
    }


async def run_scrape_job():
    """Background job to run scraping"""
    global last_scrape_result, scraping_in_progress

    try:
        scraping_in_progress = True
        result = await scraper.run_daily_scrape()
        last_scrape_result = result
    except Exception as e:
        last_scrape_result = {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    finally:
        scraping_in_progress = False


@app.post("/scrape/trigger", response_model=ScrapeResponse)
async def trigger_scrape(background_tasks: BackgroundTasks):
    """
    Manually trigger a scraping job
    Useful for testing or on-demand scraping
    """
    global scraping_in_progress

    if scraping_in_progress:
        raise HTTPException(
            status_code=409,
            detail="Scraping is already in progress"
        )

    # Run scraping in background
    background_tasks.add_task(run_scrape_job)

    return ScrapeResponse(
        success=True,
        message="Scraping job started in background",
        timestamp=datetime.now().isoformat()
    )


@app.post("/login/manual")
async def trigger_manual_login():
    """
    Trigger manual login
    Use this for first-time setup or when automated login fails
    """
    try:
        await scraper.login_manual()
        return {
            "success": True,
            "message": "Manual login completed successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Manual login failed: {str(e)}"
        )


@app.post("/login/automated")
async def trigger_automated_login():
    """
    Test automated login
    """
    try:
        success = await scraper.login_automated()
        if success:
            return {
                "success": True,
                "message": "Automated login successful"
            }
        else:
            raise HTTPException(
                status_code=401,
                detail="Automated login failed - may need manual login"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Login error: {str(e)}"
        )


@app.get("/scrape/last-result")
async def get_last_result():
    """Get results from last scraping job"""
    if last_scrape_result is None:
        raise HTTPException(
            status_code=404,
            detail="No scraping results available yet"
        )

    return last_scrape_result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
