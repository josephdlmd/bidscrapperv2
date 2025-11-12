"""
Run PhilGEPS Scraper V2 (Playwright Version)
Uses saved session from first_time setup

Usage:
    python run_scraper_playwright.py                    # Scrape all pages
    python run_scraper_playwright.py --test             # Test with 1 page only
    python run_scraper_playwright.py --pages 5          # Scrape first 5 pages
    python run_scraper_playwright.py --no-details       # Skip detail scraping
"""
import asyncio
import os
import subprocess
import sys
import argparse
from pathlib import Path
from scraper.philgeps_scraper_playwright import PhilGEPSScraper

os.environ['PHILGEPS_USERNAME'] = 'jdeleon60'
os.environ['PHILGEPS_PASSWORD'] = 'Merritmed#01'
os.environ['DATABASE_URL'] = 'sqlite:///philgeps_local.db'

async def main(max_pages=None, fetch_details=True):
    print("="*80)
    print("PhilGEPS Scraper V2 - Automated Run (Playwright)")
    print("="*80)

    # Check if database exists, if not create it
    db_path = Path('philgeps_local.db')
    if not db_path.exists():
        print("\n⚠️  Database not found. Creating database...")
        try:
            result = subprocess.run([sys.executable, 'setup_local_db_v2.py'],
                                  capture_output=True, text=True, check=True)
            print(result.stdout)
            print("✅ Database created successfully!\n")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create database: {e.stderr}")
            return
        except FileNotFoundError:
            print("❌ setup_local_db_v2.py not found. Please create database manually.")
            return

    scraper = PhilGEPSScraper()

    try:
        # Configuration
        print("\n📋 Scraper Configuration:")
        print(f"   Max Pages: {'All pages' if max_pages is None else max_pages}")
        print(f"   Fetch Details: {'Yes' if fetch_details else 'No (list only)'}")
        print("   Database: philgeps_local.db")
        print()

        # Run scraper
        print("Starting scrape...")
        result = await scraper.run_daily_scrape(
            max_pages=max_pages,
            fetch_details=fetch_details
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
    parser = argparse.ArgumentParser(
        description='PhilGEPS Scraper V2 - Automated Bid Scraping',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scraper_playwright.py              # Scrape all pages with details
  python run_scraper_playwright.py --test       # Test with 1 page only
  python run_scraper_playwright.py --pages 5    # Scrape first 5 pages
  python run_scraper_playwright.py --no-details # Scrape list only (faster)
        """
    )
    parser.add_argument('--test', action='store_true',
                       help='Test mode: scrape only 1 page')
    parser.add_argument('--pages', type=int, metavar='N',
                       help='Scrape first N pages (default: all pages)')
    parser.add_argument('--no-details', action='store_true',
                       help='Skip detail scraping (faster, no budgets)')

    args = parser.parse_args()

    # Determine max_pages
    if args.test:
        max_pages = 1
    elif args.pages:
        max_pages = args.pages
    else:
        max_pages = None  # All pages

    # Run scraper
    asyncio.run(main(
        max_pages=max_pages,
        fetch_details=not args.no_details
    ))
