"""
PhilGEPS Scraper with Persistent Browser Profile
Scrapes bid opportunities from PhilGEPS with reCAPTCHA handling
"""

from scrapling import StealthyFetcher
import asyncpg
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import re


class PhilGEPSScraper:
    """
    Scraper for Philippine Government Electronic Procurement System (PhilGEPS)
    Uses persistent browser profile to maintain trust and avoid CAPTCHA challenges
    """

    def __init__(self, profile_dir: str = "./browser_profile"):
        """
        Initialize scraper with persistent browser profile

        Args:
            profile_dir: Directory to store browser profile data
        """
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(exist_ok=True)

        self.fetcher = StealthyFetcher(
            user_data_dir=str(self.profile_dir)  # Persistent profile
        )
        self.cookies = None
        self.logged_in = False

        print(f"🔧 Initialized scraper with profile: {self.profile_dir}")

    async def login_manual(self) -> bool:
        """
        Manual login - opens visible browser for human to solve CAPTCHA
        Use this for first 3-5 logins to build trust

        Returns:
            bool: True if login successful
        """
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
            headless=False,  # Show browser
            timeout=300  # 5 minutes for manual login
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
            print("Please enter them manually")

        # Wait for user to complete login
        input("\n👉 Press ENTER after you've successfully logged in...")

        # Save cookies from persistent profile
        self.cookies = page.cookies
        self.logged_in = True

        print("✅ Login session saved in persistent profile!")
        print("   Future automated logins will use this profile\n")

        return True

    async def login_automated(self) -> bool:
        """
        Automated login using persistent profile
        Works after trust is established through manual logins

        Returns:
            bool: True if login successful
        """
        print("🤖 Attempting automated login...")

        page = self.fetcher.get(
            "https://philgeps.gov.ph/Indexes/login",
            headless=True,  # Headless mode
            timeout=60
        )

        # Fill credentials
        try:
            page.css('input[name="username"], input#username').fill(
                os.getenv('PHILGEPS_USERNAME')
            )
            page.css('input[name="password"], input#password').fill(
                os.getenv('PHILGEPS_PASSWORD')
            )
        except Exception as e:
            print(f"❌ Could not fill credentials: {e}")
            return False

        # Handle reCAPTCHA (should be easy after trust established)
        try:
            # Check if reCAPTCHA checkbox exists
            recaptcha = page.css('.g-recaptcha, iframe[src*="recaptcha"]')
            if recaptcha.exists():
                print("🔄 Clicking reCAPTCHA checkbox...")
                recaptcha.click()
                page.wait(2)  # Wait for validation
        except Exception as e:
            print(f"⚠️ reCAPTCHA handling: {e}")
            # Might be invisible reCAPTCHA, continue anyway

        # Submit login form
        try:
            submit_btn = page.css('button[type="submit"], input[type="submit"]')
            submit_btn.click()
            page.wait(5)  # Wait for redirect

            # Check if login was successful
            current_url = page.url
            page_html = page.html.lower()

            if any(indicator in page_html for indicator in ['logout', 'dashboard', 'bulletin', 'merchant']):
                self.cookies = page.cookies
                self.logged_in = True
                print("✅ Automated login successful!")
                return True
            else:
                print("❌ Login may have failed - check page content")
                return False

        except Exception as e:
            print(f"❌ Submit failed: {e}")
            return False

    async def ensure_logged_in(self) -> bool:
        """
        Ensure we're logged in, try automated first, fall back to manual

        Returns:
            bool: True if logged in
        """
        if self.logged_in:
            return True

        # Try automated login first
        if await self.login_automated():
            return True

        # Fall back to manual login
        print("\n⚠️ Automated login failed - manual login required")
        return await self.login_manual()

    async def scrape_current_opportunities(self) -> List[Dict]:
        """
        Scrape bid opportunities from bulletin board

        Returns:
            List of bid opportunity dictionaries
        """
        await self.ensure_logged_in()

        print("\n📥 Scraping PhilGEPS current opportunities...")

        page = self.fetcher.get(
            "https://philgeps.gov.ph/BulletinBoard/current_oppourtunities",
            cookies=self.cookies,
            timeout=60
        )

        # Check if we're still logged in
        if 'login' in page.url.lower():
            print("❌ Session expired - need to login again")
            self.logged_in = False
            await self.ensure_logged_in()
            # Retry
            page = self.fetcher.get(
                "https://philgeps.gov.ph/BulletinBoard/current_oppourtunities",
                cookies=self.cookies
            )

        # Extract bid opportunities
        bids = []

        try:
            # NOTE: You'll need to adjust these selectors based on actual HTML
            # This is a template - inspect the page to get correct selectors

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
                        'scraped_at': datetime.now(),
                        'source_url': 'https://philgeps.gov.ph/BulletinBoard/current_oppourtunities'
                    }

                    # Only add if we have at least reference number
                    if bid['reference_number']:
                        bids.append(bid)

                except Exception as e:
                    print(f"⚠️ Error parsing row {idx}: {e}")
                    continue

            print(f"✅ Successfully parsed {len(bids)} bid opportunities")

        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            print("💡 You may need to adjust CSS selectors based on actual HTML")

        return bids

    def _extract_text(self, element, selector: str) -> Optional[str]:
        """Helper to extract text from element"""
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
            # Remove currency symbols, commas, spaces
            cleaned = re.sub(r'[^\d.]', '', budget_str)
            return float(cleaned) if cleaned else None
        except:
            return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None

        try:
            from dateutil import parser
            return parser.parse(date_str)
        except:
            return None

    async def save_to_database(self, bids: List[Dict]) -> int:
        """
        Save bids to PostgreSQL database

        Args:
            bids: List of bid dictionaries

        Returns:
            Number of bids saved
        """
        if not bids:
            print("⚠️ No bids to save")
            return 0

        print(f"\n💾 Saving {len(bids)} bids to database...")

        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))

        try:
            saved_count = 0

            for bid in bids:
                try:
                    await conn.execute('''
                        INSERT INTO bid_opportunities (
                            reference_number, title, budget, closing_date,
                            procuring_entity, area_of_delivery, category,
                            procurement_mode, scraped_at, source_url, created_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
                        ON CONFLICT (reference_number)
                        DO UPDATE SET
                            title = EXCLUDED.title,
                            budget = EXCLUDED.budget,
                            closing_date = EXCLUDED.closing_date,
                            procuring_entity = EXCLUDED.procuring_entity,
                            area_of_delivery = EXCLUDED.area_of_delivery,
                            category = EXCLUDED.category,
                            procurement_mode = EXCLUDED.procurement_mode,
                            updated_at = NOW()
                    ''',
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
                    )
                    saved_count += 1

                except Exception as e:
                    print(f"⚠️ Error saving bid {bid.get('reference_number')}: {e}")
                    continue

            print(f"✅ Saved {saved_count} bids to database")
            return saved_count

        finally:
            await conn.close()

    async def run_daily_scrape(self) -> Dict:
        """
        Main method for daily scraping job

        Returns:
            Dictionary with scraping results
        """
        print("\n" + "="*60)
        print(f"🚀 DAILY PHILGEPS SCRAPE - {datetime.now()}")
        print("="*60 + "\n")

        try:
            # Scrape bids
            bids = await self.scrape_current_opportunities()

            # Save to database
            saved_count = await self.save_to_database(bids)

            result = {
                'success': True,
                'scraped_count': len(bids),
                'saved_count': saved_count,
                'timestamp': datetime.now().isoformat()
            }

            print("\n" + "="*60)
            print("✅ DAILY SCRAPE COMPLETE")
            print(f"   Scraped: {len(bids)} bids")
            print(f"   Saved: {saved_count} bids")
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
        """Clean up resources"""
        if self.fetcher:
            self.fetcher.close()


# Test function
async def test_scraper():
    """Test the scraper"""
    scraper = PhilGEPSScraper()

    # Do manual login for testing
    await scraper.login_manual()

    # Try scraping
    result = await scraper.run_daily_scrape()

    print("\n📊 Test Results:")
    print(json.dumps(result, indent=2))

    scraper.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_scraper())
