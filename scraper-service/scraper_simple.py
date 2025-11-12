"""
Simplified PhilGEPS Scraper using SQLite for local testing
"""
from scrapling import StealthyFetcher
import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import re


class SimplePhilGEPSScraper:
    """Simplified scraper with SQLite support"""

    def __init__(self, db_path: str = "philgeps_local.db", profile_dir: str = "./browser_profile"):
        self.db_path = db_path
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(exist_ok=True)

        self.fetcher = StealthyFetcher(
            user_data_dir=str(self.profile_dir)
        )
        self.cookies = None
        self.logged_in = False

        print(f"🔧 Initialized scraper")
        print(f"   Database: {os.path.abspath(db_path)}")
        print(f"   Profile: {self.profile_dir}")

        # Setup database
        self._setup_database()

    def _setup_database(self):
        """Create database and table if needed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

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
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_closing_date ON bid_opportunities(closing_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON bid_opportunities(category)')

        conn.commit()
        conn.close()

    def login_manual(self) -> bool:
        """Manual login - opens browser for human"""
        print("\n" + "="*60)
        print("🔐 MANUAL LOGIN TO PhilGEPS")
        print("="*60)
        print("Opening browser window...")
        print("1. Solve the reCAPTCHA")
        print("2. Click the Login button")
        print("3. Wait until you see the dashboard")
        print("4. Come back here and press ENTER")
        print("="*60 + "\n")

        page = self.fetcher.get(
            "https://philgeps.gov.ph/Indexes/login",
            headless=False,
            timeout=300
        )

        # Pre-fill credentials
        try:
            username_field = page.css('input[name="username"], input#username')
            password_field = page.css('input[name="password"], input#password')

            if username_field.exists():
                username_field.fill(os.getenv('PHILGEPS_USERNAME'))
            if password_field.exists():
                password_field.fill(os.getenv('PHILGEPS_PASSWORD'))

            print("✅ Credentials pre-filled")
        except Exception as e:
            print(f"⚠️ Could not pre-fill credentials: {e}")

        input("\n👉 Press ENTER after you've successfully logged in...")

        self.cookies = page.cookies
        self.logged_in = True

        print("✅ Login session saved!")
        return True

    def scrape_opportunities(self) -> List[Dict]:
        """Scrape bid opportunities"""
        if not self.logged_in:
            print("⚠️ Not logged in. Running manual login...")
            self.login_manual()

        print("\n📥 Scraping PhilGEPS current opportunities...")

        page = self.fetcher.get(
            "https://philgeps.gov.ph/BulletinBoard/current_oppourtunities",
            cookies=self.cookies,
            timeout=60
        )

        # Check if still logged in
        if 'login' in page.url.lower():
            print("❌ Session expired - need to login again")
            self.logged_in = False
            self.login_manual()
            page = self.fetcher.get(
                "https://philgeps.gov.ph/BulletinBoard/current_oppourtunities",
                cookies=self.cookies
            )

        # Extract bids
        bids = []

        try:
            rows = page.css('tr.opportunity-row, tbody tr').get_all()
            print(f"Found {len(rows)} potential bid rows")

            for idx, row in enumerate(rows):
                try:
                    bid = {
                        'reference_number': self._extract_text(row, '.ref-number, td:nth-child(1)'),
                        'title': self._extract_text(row, '.title, td:nth-child(2)'),
                        'budget': self._parse_budget(
                            self._extract_text(row, '.budget, .abc, td:nth-child(3)')
                        ),
                        'closing_date': self._parse_date(
                            self._extract_text(row, '.closing-date, .deadline, td:nth-child(4)')
                        ),
                        'procuring_entity': self._extract_text(row, '.agency, .entity, td:nth-child(5)'),
                        'area_of_delivery': self._extract_text(row, '.location, .area, td:nth-child(6)'),
                        'category': self._extract_text(row, '.category, td:nth-child(7)'),
                        'procurement_mode': self._extract_text(row, '.procurement-mode, td:nth-child(8)'),
                        'scraped_at': datetime.now().isoformat(),
                        'source_url': 'https://philgeps.gov.ph/BulletinBoard/current_oppourtunities'
                    }

                    if bid['reference_number']:
                        bids.append(bid)

                except Exception as e:
                    print(f"⚠️ Error parsing row {idx}: {e}")
                    continue

            print(f"✅ Successfully parsed {len(bids)} bid opportunities")

        except Exception as e:
            print(f"❌ Error during scraping: {e}")

        return bids

    def _extract_text(self, element, selector: str) -> Optional[str]:
        """Extract text from element"""
        try:
            result = element.css(selector)
            if result.exists():
                return result.text.strip()
        except:
            pass
        return None

    def _parse_budget(self, budget_str: Optional[str]) -> Optional[float]:
        """Parse budget string to float"""
        if not budget_str:
            return None
        try:
            cleaned = re.sub(r'[^\d.]', '', budget_str)
            return float(cleaned) if cleaned else None
        except:
            return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse date string"""
        if not date_str:
            return None
        try:
            from dateutil import parser
            dt = parser.parse(date_str)
            return dt.isoformat()
        except:
            return date_str

    def save_to_database(self, bids: List[Dict]) -> int:
        """Save bids to SQLite"""
        if not bids:
            print("⚠️ No bids to save")
            return 0

        print(f"\n💾 Saving {len(bids)} bids to database...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        saved_count = 0

        for bid in bids:
            try:
                cursor.execute('''
                INSERT OR REPLACE INTO bid_opportunities
                (reference_number, title, budget, closing_date, procuring_entity,
                 area_of_delivery, category, procurement_mode, scraped_at, source_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bid['reference_number'],
                    bid['title'],
                    bid['budget'],
                    bid['closing_date'],
                    bid['procuring_entity'],
                    bid['area_of_delivery'],
                    bid['category'],
                    bid['procurement_mode'],
                    bid['scraped_at'],
                    bid['source_url']
                ))
                saved_count += 1
            except Exception as e:
                print(f"⚠️ Error saving bid {bid.get('reference_number')}: {e}")

        conn.commit()
        conn.close()

        print(f"✅ Saved {saved_count} bids to database")
        return saved_count

    def run_scrape(self) -> Dict:
        """Run full scrape"""
        print("\n" + "="*60)
        print(f"🚀 PHILGEPS SCRAPE - {datetime.now()}")
        print("="*60 + "\n")

        try:
            bids = self.scrape_opportunities()
            saved_count = self.save_to_database(bids)

            result = {
                'success': True,
                'scraped_count': len(bids),
                'saved_count': saved_count,
                'timestamp': datetime.now().isoformat()
            }

            print("\n" + "="*60)
            print("✅ SCRAPE COMPLETE")
            print(f"   Scraped: {len(bids)} bids")
            print(f"   Saved: {saved_count} bids")
            print(f"   Database: {os.path.abspath(self.db_path)}")
            print("="*60 + "\n")

            return result

        except Exception as e:
            print(f"\n❌ SCRAPE FAILED: {e}\n")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def close(self):
        """Cleanup"""
        if self.fetcher:
            self.fetcher.close()


# Quick test
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv('.env.local')

    scraper = SimplePhilGEPSScraper()

    print("="*60)
    print("SELECT TEST:")
    print("1. Manual login only")
    print("2. Full scrape test")
    print("="*60)

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        scraper.login_manual()
    elif choice == "2":
        scraper.run_scrape()

    scraper.close()
