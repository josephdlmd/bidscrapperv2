"""
Test script for PhilGEPS scraper
Run this to test the scraper before deploying
"""

import asyncio
import sys
from scraper.philgeps_scraper import PhilGEPSScraper
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


async def test_environment():
    """Test that environment is configured"""
    print("\n" + "="*60)
    print("🧪 TESTING ENVIRONMENT")
    print("="*60)

    required_vars = {
        'PHILGEPS_USERNAME': os.getenv('PHILGEPS_USERNAME'),
        'PHILGEPS_PASSWORD': os.getenv('PHILGEPS_PASSWORD'),
        'DATABASE_URL': os.getenv('DATABASE_URL')
    }

    all_set = True
    for var, value in required_vars.items():
        if value:
            # Show first 3 chars only for security
            display_value = value[:3] + "***" if len(value) > 3 else "***"
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
            all_set = False

    if not all_set:
        print("\n❌ Please set all required environment variables in .env file")
        return False

    print("\n✅ Environment configured correctly\n")
    return True


async def test_database_connection():
    """Test database connection"""
    print("="*60)
    print("🧪 TESTING DATABASE CONNECTION")
    print("="*60)

    try:
        import asyncpg
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))

        # Check if bid_opportunities table exists
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'bid_opportunities'
            )
        """)

        if result:
            print("✅ Connected to database")
            print("✅ bid_opportunities table exists")
        else:
            print("✅ Connected to database")
            print("⚠️ bid_opportunities table does NOT exist")
            print("   Run the database schema from DATABASE_SCHEMA.md")

        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_manual_login():
    """Test manual login"""
    print("\n" + "="*60)
    print("🧪 TESTING MANUAL LOGIN")
    print("="*60)

    scraper = PhilGEPSScraper()

    try:
        print("\nThis will open a browser window...")
        print("Please solve the CAPTCHA and complete login\n")

        await scraper.login_manual()

        print("\n✅ Manual login successful!")
        print("   Session saved for future automated logins\n")

        scraper.close()
        return True

    except Exception as e:
        print(f"\n❌ Manual login failed: {e}\n")
        scraper.close()
        return False


async def test_automated_login():
    """Test automated login"""
    print("="*60)
    print("🧪 TESTING AUTOMATED LOGIN")
    print("="*60)

    scraper = PhilGEPSScraper()

    try:
        success = await scraper.login_automated()

        if success:
            print("\n✅ Automated login successful!")
            print("   You can now run daily scraping automatically\n")
        else:
            print("\n⚠️ Automated login failed")
            print("   You may need to do a few more manual logins to build trust\n")

        scraper.close()
        return success

    except Exception as e:
        print(f"\n❌ Automated login error: {e}")
        print("   Run more manual logins to build trust\n")
        scraper.close()
        return False


async def test_scraping():
    """Test scraping"""
    print("="*60)
    print("🧪 TESTING SCRAPING")
    print("="*60)

    scraper = PhilGEPSScraper()

    try:
        print("\nAttempting to scrape bid opportunities...")

        bids = await scraper.scrape_current_opportunities()

        if bids:
            print(f"\n✅ Scraped {len(bids)} bid opportunities!")
            print("\nSample bid:")
            if len(bids) > 0:
                sample = bids[0]
                print(f"  Reference: {sample.get('reference_number')}")
                print(f"  Title: {sample.get('title')[:50]}...")
                print(f"  Budget: {sample.get('budget')}")
                print(f"  Agency: {sample.get('procuring_entity')}")
        else:
            print("\n⚠️ No bids scraped")
            print("   This might mean:")
            print("   - No opportunities currently posted")
            print("   - HTML structure changed (need to update selectors)")
            print("   - Login failed")

        scraper.close()
        return len(bids) > 0

    except Exception as e:
        print(f"\n❌ Scraping failed: {e}\n")
        scraper.close()
        return False


async def test_full_pipeline():
    """Test full scraping pipeline including database save"""
    print("="*60)
    print("🧪 TESTING FULL PIPELINE")
    print("="*60)

    scraper = PhilGEPSScraper()

    try:
        result = await scraper.run_daily_scrape()

        if result['success']:
            print("\n✅ FULL PIPELINE TEST SUCCESSFUL!")
            print(f"   Scraped: {result.get('scraped_count')} bids")
            print(f"   Saved: {result.get('saved_count')} bids to database")
        else:
            print("\n❌ Pipeline test failed")
            print(f"   Error: {result.get('error')}")

        scraper.close()
        return result['success']

    except Exception as e:
        print(f"\n❌ Pipeline test failed: {e}\n")
        scraper.close()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 PhilGEPS SCRAPER TEST SUITE")
    print("="*60 + "\n")

    # Test 1: Environment
    if not await test_environment():
        print("\n❌ Fix environment configuration before continuing\n")
        sys.exit(1)

    # Test 2: Database
    if not await test_database_connection():
        print("\n⚠️ Database connection issue - continuing anyway...\n")

    # Test 3: Ask user which tests to run
    print("="*60)
    print("SELECT TEST MODE")
    print("="*60)
    print("1. First time setup (manual login only)")
    print("2. Test automated login")
    print("3. Test scraping only")
    print("4. Full pipeline test (scrape + save to database)")
    print("="*60)

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        await test_manual_login()
    elif choice == "2":
        await test_automated_login()
    elif choice == "3":
        await test_scraping()
    elif choice == "4":
        await test_full_pipeline()
    else:
        print("Invalid choice")
        sys.exit(1)

    print("\n" + "="*60)
    print("✅ TESTING COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
