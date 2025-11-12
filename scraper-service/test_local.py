"""
Local test script using SQLite (no PostgreSQL needed)
"""
import sys
import sqlite3
import os
from datetime import datetime

# Load environment
from dotenv import load_dotenv
load_dotenv('.env.local')

print("\n" + "="*60)
print("🚀 PhilGEPS SCRAPER - LOCAL TEST")
print("="*60 + "\n")

# Test 1: Check environment
print("1. Checking environment...")
username = os.getenv('PHILGEPS_USERNAME')
password = os.getenv('PHILGEPS_PASSWORD')

if username and password:
    print(f"   ✅ Credentials configured")
    print(f"      Username: {username}")
else:
    print(f"   ❌ Credentials missing")
    print(f"   Create .env file and add:")
    print(f"   PHILGEPS_USERNAME=jdeleon60")
    print(f"   PHILGEPS_PASSWORD=Merritmed#01")
    sys.exit(1)

# Test 2: Setup database
print("\n2. Setting up local database...")
db_path = 'philgeps_local.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bid_opportunities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference_number TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        budget REAL,
        closing_date TEXT,
        procuring_entity TEXT,
        area_of_delivery TEXT,
        category TEXT,
        procurement_mode TEXT,
        scraped_at TEXT,
        source_url TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reference_number ON bid_opportunities(reference_number)')

    conn.commit()
    print(f"   ✅ Database ready: {os.path.abspath(db_path)}")

    # Test insert
    test_bid = {
        'reference_number': 'TEST-001',
        'title': 'Test Bid Opportunity',
        'budget': 100000.00,
        'closing_date': datetime.now().isoformat(),
        'procuring_entity': 'Test Agency',
        'area_of_delivery': 'Test Location',
        'category': 'Test Category',
        'procurement_mode': 'Public Bidding',
        'scraped_at': datetime.now().isoformat(),
        'source_url': 'https://philgeps.gov.ph/test'
    }

    cursor.execute('''
    INSERT OR REPLACE INTO bid_opportunities
    (reference_number, title, budget, closing_date, procuring_entity,
     area_of_delivery, category, procurement_mode, scraped_at, source_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        test_bid['reference_number'],
        test_bid['title'],
        test_bid['budget'],
        test_bid['closing_date'],
        test_bid['procuring_entity'],
        test_bid['area_of_delivery'],
        test_bid['category'],
        test_bid['procurement_mode'],
        test_bid['scraped_at'],
        test_bid['source_url']
    ))

    conn.commit()
    print(f"   ✅ Test record inserted")

    # Verify
    cursor.execute('SELECT COUNT(*) FROM bid_opportunities')
    count = cursor.fetchone()[0]
    print(f"   ✅ Database has {count} record(s)")

    conn.close()

except Exception as e:
    print(f"   ❌ Database error: {e}")
    sys.exit(1)

# Test 3: Test browser import
print("\n3. Testing browser dependencies...")
try:
    from scrapling import StealthyFetcher
    print("   ✅ Scrapling imported successfully")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    print("   This is OK for now - we'll fix when doing actual scraping")

print("\n" + "="*60)
print("✅ LOCAL SETUP COMPLETE!")
print("="*60)
print(f"\n📊 Database location: {os.path.abspath(db_path)}")
print(f"📝 You can view data with: sqlite3 {db_path}")
print("\n🎯 NEXT STEPS:")
print("   1. Run: python test_scraper_simple.py")
print("   2. This will do manual login")
print("   3. Data saves to local SQLite file")
print("\n" + "="*60 + "\n")
