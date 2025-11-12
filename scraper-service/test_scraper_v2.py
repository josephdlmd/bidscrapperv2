"""
Test PhilGEPS Scraper V2
Quick test run with limited pages
"""
import asyncio
import os
import json
from scraper.philgeps_scraper import PhilGEPSScraper

# Set credentials from .env.example
os.environ['PHILGEPS_USERNAME'] = 'jdeleon60'
os.environ['PHILGEPS_PASSWORD'] = 'Merritmed#01'
os.environ['DATABASE_URL'] = 'sqlite:///philgeps_local.db'  # Use local SQLite

async def main():
    print("="*80)
    print("🧪 TESTING PhilGEPS Scraper V2")
    print("="*80)
    print()
    print("📋 Test Configuration:")
    print("   - Max pages: 1 (first page only)")
    print("   - Fetch details: Yes")
    print("   - Database: Local SQLite")
    print("   - Username:", os.environ['PHILGEPS_USERNAME'])
    print()

    scraper = PhilGEPSScraper()

    try:
        # Test with just 1 page for now
        print("🚀 Starting test scrape...")
        result = await scraper.run_daily_scrape(
            max_pages=1,  # Just test first page
            fetch_details=True  # Get full details including budget
        )

        print("\n" + "="*80)
        print("📊 TEST RESULTS")
        print("="*80)
        print(json.dumps(result, indent=2, default=str))

        if result['success']:
            print("\n✅ Test completed successfully!")
            print(f"   - Found {result.get('total_bids', 0)} bids")
            print(f"   - Fetched details for {result.get('detailed_bids', 0)} bids")
            print(f"   - Saved {result.get('saved_count', 0)} bids to database")
        else:
            print("\n❌ Test failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()
        print("\n🔒 Scraper closed")

if __name__ == "__main__":
    asyncio.run(main())
