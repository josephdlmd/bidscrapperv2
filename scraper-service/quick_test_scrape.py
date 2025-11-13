"""
Quick test script to scrape 1 page of real PhilGEPS data
Uses simplified scraper with SQLite support
"""
import asyncio
import json
from scraper_simple import SimplePhilGEPSScraper

async def main():
    import os
    from pathlib import Path

    print("\n" + "="*80)
    print("🚀 QUICK TEST SCRAPE - 1 PAGE FROM PHILGEPS")
    print("="*80 + "\n")

    # Check if browser profile exists
    profile_exists = Path('browser_profile').exists()
    if profile_exists:
        print("✅ Browser profile found - Automated login should work!")
        print("   (No CAPTCHA expected)\n")
    else:
        print("📝 No browser profile found - First time login")
        print("   (CAPTCHA will be required to build trust)\n")

    # Create scraper
    scraper = SimplePhilGEPSScraper(db_path='philgeps_local.db')

    try:
        # Login (tries automated first, falls back to manual if needed)
        print("📝 Logging in to PhilGEPS...")
        print("   🤖 Attempting AUTOMATED login...")
        print("   📌 If you have an established browser profile, CAPTCHA should NOT appear!")
        print("   📌 If this is your first time, browser will open for manual login\n")

        await scraper.login()

        print("\n✅ Login successful!")

        # Scrape just 1 page
        print("\n📥 Scraping 1 page of bids...")
        bids = await scraper.scrape_opportunities(max_pages=1)

        print(f"\n✅ Found {len(bids)} bids on first page")

        # Save to database
        if bids:
            saved = scraper.save_to_database(bids)
            print(f"💾 Saved {saved} bids to database")

            # Show first bid as example
            print("\n" + "="*80)
            print("📊 EXAMPLE OF EXTRACTED DATA (First Bid)")
            print("="*80 + "\n")

            first_bid = bids[0]

            # Pretty print the data
            print(json.dumps({
                'reference_number': first_bid.get('reference_number'),
                'title': first_bid.get('title'),
                'classification': first_bid.get('classification'),
                'procurement_mode': first_bid.get('procurement_mode'),
                'agency_name': first_bid.get('agency_name'),
                'publish_date': first_bid.get('publish_date'),
                'closing_date': first_bid.get('closing_date'),
                'status': first_bid.get('status'),
                'detail_url': first_bid.get('detail_url')
            }, indent=2))

            print("\n" + "="*80)
            print(f"✅ SUCCESS! Scraped {len(bids)} real bids from PhilGEPS")
            print(f"   Database: philgeps_local.db")
            print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
