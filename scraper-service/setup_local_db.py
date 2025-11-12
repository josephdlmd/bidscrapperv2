"""
Setup local SQLite database for testing
Run this once to create the database
"""
import sqlite3
import os

db_path = 'philgeps_local.db'

print("🗄️  Creating local SQLite database...")

# Create database
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

# Create indexes
cursor.execute('CREATE INDEX IF NOT EXISTS idx_reference_number ON bid_opportunities(reference_number)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_closing_date ON bid_opportunities(closing_date)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON bid_opportunities(category)')

conn.commit()
conn.close()

print(f"✅ Database created: {os.path.abspath(db_path)}")
print(f"✅ Table 'bid_opportunities' created")
print(f"✅ Indexes created")
print("\n🎉 Ready to use!")
