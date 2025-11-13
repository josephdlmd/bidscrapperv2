"""
Working PhilGEPS Scraper using Playwright (SQLite)
"""
from playwright.sync_api import sync_playwright
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

        self.browser = None
        self.context = None
        self.page = None

        print(f"🔧 Initialized scraper")
        print(f"   Database: {os.path.abspath(db_path)}")
        print(f"   Profile: {self.profile_dir}")

        # Setup database
        self._setup_database()

    def _setup_database(self):
        """Create database and table if needed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if table exists and has correct schema
        try:
            cursor.execute("PRAGMA table_info(bid_opportunities)")
            columns = [row[1] for row in cursor.fetchall()]

            # If table exists but doesn't have 'category' column, drop it
            if columns and 'category' not in columns:
                print("⚠️ Old schema detected - dropping table to recreate with correct schema")
                cursor.execute('DROP TABLE IF EXISTS bid_opportunities')
        except:
            pass

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

        with sync_playwright() as p:
            # Launch browser with persistent context and anti-detection
            self.context = p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

            # Go to login page
            self.page.goto("https://philgeps.gov.ph/Indexes/login", timeout=60000)

            # Refresh page to clear any popups/errors
            self.page.reload(timeout=60000)
            print("✅ Page refreshed")

            # Pre-fill credentials
            try:
                # Select "Marchant" from dropdown (note: they spelled it "Marchant")
                self.page.select_option('select[name="type"], select#type', 'Marchant')
                print("✅ Selected Marchant")

                username = os.getenv('PHILGEPS_USERNAME', 'jdeleon60')
                password = os.getenv('PHILGEPS_PASSWORD', 'Merritmed#01')

                self.page.fill('input[name="username"], input#username', username)
                self.page.fill('input[name="password"], input#password', password)
                print("✅ Credentials pre-filled")

                # Click reCAPTCHA checkbox
                self.page.wait_for_timeout(2000)

                # Find and click reCAPTCHA checkbox in iframe
                frames = self.page.frames
                recaptcha_clicked = False

                for frame in frames:
                    try:
                        checkbox = frame.locator('.recaptcha-checkbox-border').first
                        if checkbox.is_visible():
                            checkbox.click()
                            recaptcha_clicked = True
                            print("✅ Clicked reCAPTCHA checkbox")
                            break
                    except:
                        continue

                if not recaptcha_clicked:
                    print("⚠️ Could not auto-click reCAPTCHA - please click it manually")

                # Wait for reCAPTCHA to auto-validate
                self.page.wait_for_timeout(4000)
                print("✅ reCAPTCHA validated")

                # Auto-click Login button
                self.page.click('input[type="submit"][value="Log In"]')
                print("✅ Clicked Login button")

                # Wait for navigation
                self.page.wait_for_timeout(5000)

                # Navigate directly to the bid opportunities page
                self.page.goto(
                    "https://philgeps.gov.ph/BulletinBoard/view_more_current_oppourtunities",
                    timeout=60000,
                    wait_until="networkidle"
                )
                print("✅ Navigated to bid opportunities page")

            except Exception as e:
                print(f"⚠️ Could not complete auto-login: {e}")
                print("   Please complete login manually and press ENTER")
                input("\n👉 Press ENTER after you've logged in...")

            print("✅ Login session saved in browser profile!")

            self.context.close()

        return True

    def scrape_opportunities(self, date_from=None, date_to=None) -> List[Dict]:
        """
        Scrape bid opportunities with optional date range

        Args:
            date_from: Start date (defaults to today)
            date_to: End date (defaults to tomorrow)
        """
        from datetime import datetime, timedelta

        # Default: today to tomorrow
        if date_from is None:
            date_from = datetime.now()
        if date_to is None:
            date_to = datetime.now() + timedelta(days=1)

        # Format dates as MM/DD/YYYY (PhilGEPS format)
        date_from_str = date_from.strftime('%m/%d/%Y')
        date_to_str = date_to.strftime('%m/%d/%Y')

        print(f"\n📥 Scraping PhilGEPS opportunities from {date_from_str} to {date_to_str}...")

        bids = []

        with sync_playwright() as p:
            # Launch with persistent context (has login session) and anti-detection
            self.context = p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

            try:
                # Go to the correct opportunities page
                self.page.goto(
                    "https://philgeps.gov.ph/BulletinBoard/view_more_current_oppourtunities",
                    timeout=60000,
                    wait_until="networkidle"
                )

                print("✅ Loaded opportunities page")

                # Fill in date range filters
                try:
                    # Wait for page to fully load
                    self.page.wait_for_timeout(2000)

                    # Fill "Publish Date From"
                    self.page.fill('input#searchPublishDateFrom', date_from_str)
                    print(f"✅ Set date from: {date_from_str}")

                    # Fill "Publish Date To"
                    self.page.fill('input#searchPublishDateTo', date_to_str)
                    print(f"✅ Set date to: {date_to_str}")

                    # Wait a moment for form to register
                    self.page.wait_for_timeout(1000)

                    # Click the search button
                    self.page.click('button#search[name="search"]')
                    print("✅ Clicked search button")

                    # Wait for results to load
                    self.page.wait_for_timeout(5000)

                except Exception as e:
                    print(f"⚠️ Could not set date filters: {e}")
                    print("   Continuing with default date range...")

                # Check if still logged in
                if 'login' in self.page.url.lower():
                    print("❌ Session expired - need to login again")
                    self.context.close()
                    return []

                # Wait for content to load
                self.page.wait_for_timeout(3000)

                # Get page HTML for debugging
                html_content = self.page.content()

                # Try to find table rows
                rows = self.page.query_selector_all('tr, tbody tr')
                print(f"Found {len(rows)} potential bid rows")

                for idx, row in enumerate(rows):
                    try:
                        cells = row.query_selector_all('td')

                        if len(cells) >= 3:  # At least 3 columns
                            bid = {
                                'reference_number': cells[0].inner_text().strip() if len(cells) > 0 else '',
                                'title': cells[1].inner_text().strip() if len(cells) > 1 else '',
                                'budget': self._parse_budget(cells[2].inner_text().strip() if len(cells) > 2 else ''),
                                'closing_date': cells[3].inner_text().strip() if len(cells) > 3 else '',
                                'procuring_entity': cells[4].inner_text().strip() if len(cells) > 4 else '',
                                'area_of_delivery': cells[5].inner_text().strip() if len(cells) > 5 else '',
                                'category': cells[6].inner_text().strip() if len(cells) > 6 else '',
                                'procurement_mode': cells[7].inner_text().strip() if len(cells) > 7 else '',
                                'scraped_at': datetime.now().isoformat(),
                                'source_url': 'https://philgeps.gov.ph/BulletinBoard/current_oppourtunities'
                            }

                            if bid['reference_number']:
                                bids.append(bid)

                    except Exception as e:
                        continue

                print(f"✅ Successfully parsed {len(bids)} bid opportunities")

            except Exception as e:
                print(f"❌ Error during scraping: {e}")
            finally:
                self.context.close()

        return bids

    def _parse_budget(self, budget_str: str) -> Optional[float]:
        """Parse budget string to float"""
        if not budget_str:
            return None
        try:
            cleaned = re.sub(r'[^\d.]', '', budget_str)
            return float(cleaned) if cleaned else None
        except:
            return None

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


# Quick test
if __name__ == "__main__":
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
    else:
        print("Invalid choice")
