"""
Setup local SQLite database for testing - Version 2
Updated schema to match PhilGEPS scraper v2 with all fields
"""
import sqlite3
import os

db_path = 'philgeps_local.db'

print("🗄️  Creating/Updating local SQLite database...")
print("   Schema Version: 2.0")
print("   Based on PhilGEPS reference pages analysis")

# Create or connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop old tables if they exist (for clean migration)
print("\n📝 Dropping old tables (if any)...")
cursor.execute('DROP TABLE IF EXISTS bid_line_items')
cursor.execute('DROP TABLE IF EXISTS bid_opportunities')

# Create main bid_opportunities table with all fields
print("📝 Creating bid_opportunities table...")
cursor.execute('''
CREATE TABLE bid_opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Core identification
    reference_number TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    status TEXT,

    -- URLs
    detail_url TEXT,
    source_url TEXT,

    -- Procurement details
    procurement_mode TEXT,
    classification TEXT,  -- Goods, Civil Works, Consulting Services, etc.
    lot_type TEXT,
    control_number TEXT,

    -- Financial
    approved_budget REAL,  -- From detail page only!

    -- Dates
    publish_date TEXT,
    closing_date TEXT,
    date_created TEXT,
    date_last_updated TEXT,

    -- Agency/Organization
    agency_name TEXT,
    client_agency TEXT,
    contact_person TEXT,

    -- Location and delivery
    delivery_location TEXT,
    delivery_period TEXT,

    -- Categorization
    business_category TEXT,
    funding_source TEXT,
    applicable_rules TEXT,

    -- Additional info
    bid_validity_period TEXT,
    description TEXT,  -- Full HTML description

    -- Metadata
    scraped_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
''')

# Create line items table
print("📝 Creating bid_line_items table...")
cursor.execute('''
CREATE TABLE bid_line_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_number TEXT NOT NULL,
    item_no TEXT,
    unspsc TEXT,  -- United Nations Standard Products and Services Code
    lot_name TEXT,
    lot_description TEXT,
    quantity TEXT,
    unit_of_measure TEXT,

    FOREIGN KEY (reference_number) REFERENCES bid_opportunities(reference_number)
        ON DELETE CASCADE
)
''')

# Create indexes for performance
print("📝 Creating indexes...")
cursor.execute('CREATE INDEX idx_reference_number ON bid_opportunities(reference_number)')
cursor.execute('CREATE INDEX idx_closing_date ON bid_opportunities(closing_date)')
cursor.execute('CREATE INDEX idx_classification ON bid_opportunities(classification)')
cursor.execute('CREATE INDEX idx_agency_name ON bid_opportunities(agency_name)')
cursor.execute('CREATE INDEX idx_status ON bid_opportunities(status)')
cursor.execute('CREATE INDEX idx_line_items_ref ON bid_line_items(reference_number)')

conn.commit()
conn.close()

print(f"\n✅ Database created: {os.path.abspath(db_path)}")
print("✅ Tables created:")
print("   - bid_opportunities (main table with all bid details)")
print("   - bid_line_items (line items for each bid)")
print("✅ Indexes created for optimal query performance")
print("\n🎉 Database ready for PhilGEPS scraper v2!")
print("\n📊 Schema supports:")
print("   ✓ List view fields (classification, publish_date, status)")
print("   ✓ Detail view fields (approved_budget, delivery_period, contact_person)")
print("   ✓ Line items with UNSPSC codes")
print("   ✓ Full pagination data from view_more_current_oppourtunities")
