"""
Run PhilGEPS Scraper V2 (Playwright Version)
Uses saved session from first_time setup
"""
import asyncio
import os
from scraper.philgeps_scraper_playwright import PhilGEPSScraper

os.environ['PHILGEPS_USERNAME'] = 'jdeleon60'
os.environ['PHILGEPS_PASSWORD'] = 'Merritmed#01'
os.environ['DATABASE_URL'] = 'sqlite:///philgeps_local.db'

async def main():
    print("="*80)
    print("PhilGEPS Scraper V2 - Automated Run (Playwright)")
    print("="*80)

    scraper = PhilGEPSScraper()

    try:
        # Test with 1 page first
        print("\nStarting test scrape (1 page only)...")
        result = await scraper.run_daily_scrape(
            max_pages=1,  # Change to None for all pages
            fetch_details=True
        )

        print("\n" + "="*80)
        print("RESULTS")
        print("="*80)
        print(f"Success: {result['success']}")
        print(f"Total bids found: {result.get('total_bids', 0)}")
        print(f"Details fetched: {result.get('detailed_bids', 0)}")
        print(f"Saved to database: {result.get('saved_count', 0)}")

        if not result['success']:
            print(f"Error: {result.get('error', 'Unknown')}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await scraper.async_close()

if __name__ == "__main__":
    asyncio.run(main())
