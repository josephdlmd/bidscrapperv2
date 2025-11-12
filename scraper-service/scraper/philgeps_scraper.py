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

    async def scrape_current_opportunities_list(self, max_pages: Optional[int] = None) -> List[Dict]:
        """
        PHASE 1: Scrape list of bid opportunities from all pages

        This builds an index of all available bids with basic information.
        Does NOT include budget - that's only available in detail pages.

        Args:
            max_pages: Optional limit on number of pages to scrape (None = all pages)

        Returns:
            List of bid opportunity dictionaries with basic info
        """
        await self.ensure_logged_in()

        print("\n📥 PHASE 1: Building bid opportunities index...")

        all_bids = []
        current_page = 1
        total_bids = 0

        while True:
            if max_pages and current_page > max_pages:
                print(f"⚠️ Reached max pages limit ({max_pages})")
                break

            print(f"\n📄 Scraping page {current_page}...")

            # Construct URL with pagination
            if current_page == 1:
                url = "https://philgeps.gov.ph/BulletinBoard/view_more_current_oppourtunities"
            else:
                url = f"https://philgeps.gov.ph/bulletin-board/view-more-current-oppourtunities?page={current_page}&direction=Tenders.tender_start_datetime+desc"

            page = self.fetcher.get(url, cookies=self.cookies, timeout=60)

            # Check if we're still logged in
            if 'login' in page.url.lower():
                print("❌ Session expired - need to login again")
                self.logged_in = False
                await self.ensure_logged_in()
                page = self.fetcher.get(url, cookies=self.cookies)

            # Extract pagination info
            pagination_text = self._extract_text(page, '.paginator p')
            if pagination_text:
                print(f"   {pagination_text}")
                # Extract total from text like "Page 1 of 5, showing 20 record(s) out of 81 total"
                match = re.search(r'out of (\d+) total', pagination_text)
                if match:
                    total_bids = int(match.group(1))

            # Extract bid rows
            try:
                rows = page.css('table.dataTable tbody tr').get_all()

                if not rows or len(rows) == 0:
                    print("   No more bids found - end of pagination")
                    break

                print(f"   Found {len(rows)} bids on this page")

                for idx, row in enumerate(rows):
                    try:
                        # Extract reference number and detail URL
                        ref_link = row.css('td[data-label="Bid Notice Reference Number"] a')
                        reference_number = None
                        detail_url = None

                        if ref_link.exists():
                            reference_number = ref_link.text.strip()
                            detail_url = ref_link.attrib.get('href', '')
                            if detail_url and not detail_url.startswith('http'):
                                detail_url = f"https://philgeps.gov.ph{detail_url}"

                        if not reference_number:
                            continue

                        bid = {
                            'reference_number': reference_number,
                            'title': self._extract_text(row, 'td[data-label="Notice Title"] .wrapped-long-string'),
                            'procurement_mode': self._extract_text(row, 'td[data-label="Mode of Procurement"]'),
                            'classification': self._extract_text(row, 'td[data-label="Classification"]'),
                            'agency_name': self._extract_text(row, 'td[data-label="Agency Name"]'),
                            'publish_date': self._parse_date(
                                self._extract_text(row, 'td[data-label="Publish Date"]')
                            ),
                            'closing_date': self._parse_date(
                                self._extract_text(row, 'td[data-label="Due Date"]')
                            ),
                            'status': self._extract_text(row, 'td[data-label="Status"]'),
                            'detail_url': detail_url,
                            'scraped_at': datetime.now(),
                            'source_url': url
                        }

                        all_bids.append(bid)

                    except Exception as e:
                        print(f"   ⚠️ Error parsing row {idx + 1}: {e}")
                        continue

            except Exception as e:
                print(f"   ❌ Error extracting rows: {e}")
                break

            # Check if there's a next page
            next_button = page.css('.pagination li.next:not(.disabled)')
            if not next_button.exists():
                print("   ✅ Reached last page")
                break

            current_page += 1

        print(f"\n✅ PHASE 1 Complete: Collected {len(all_bids)} bids from {current_page} page(s)")
        if total_bids:
            print(f"   Total bids in system: {total_bids}")

        return all_bids

    async def scrape_bid_detail(self, reference_number: str, detail_url: str) -> Optional[Dict]:
        """
        PHASE 2: Scrape detailed information for a specific bid

        This fetches the full bid notice page which includes:
        - Approved Budget (NOT available in list view)
        - Delivery period, contact person, etc.
        - Line items with quantities

        Args:
            reference_number: The bid reference number
            detail_url: URL to the bid detail page

        Returns:
            Dictionary with detailed bid information
        """
        try:
            print(f"   📄 Fetching details for bid {reference_number}...")

            page = self.fetcher.get(detail_url, cookies=self.cookies, timeout=60)

            # Check login
            if 'login' in page.url.lower():
                print(f"   ⚠️ Session expired while fetching {reference_number}")
                return None

            # Extract all detail fields
            detail = {
                'reference_number': reference_number,

                # Left column fields
                'bid_validity_period': self._extract_label_value(page, 'Bid Validity Period:'),
                'control_number': self._extract_label_value(page, 'Control Number:'),
                'lot_type': self._extract_label_value(page, 'Lot Type:'),
                'approved_budget': self._parse_budget(
                    self._extract_label_value(page, 'Approved Budget of the Contract:')
                ),
                'procurement_mode': self._extract_label_value(page, 'Procurement Mode:'),
                'classification': self._extract_label_value(page, 'Classification:'),
                'applicable_rules': self._extract_label_value(page, 'Applicable Procurement Rules:'),
                'funding_source': self._extract_label_value(page, 'Funding Source:'),
                'delivery_location': self._extract_label_value(page, 'Delivery/Project Location:'),
                'business_category': self._extract_label_value(page, 'Business Category:'),
                'delivery_period': self._extract_label_value(page, 'Delivery Period:'),
                'client_agency': self._extract_label_value(page, 'Client Agency:'),
                'contact_person': self._extract_label_value(page, 'Contact Person:'),
                'created_by': self._extract_label_value(page, 'Created By:'),
                'date_created': self._parse_date(self._extract_label_value(page, 'Date created:')),

                # Right column fields
                'published_date': self._parse_date(self._extract_label_value(page, 'Published Date:')),
                'closing_date': self._parse_date(self._extract_label_value(page, 'Closing Date:')),
                'date_last_updated': self._parse_date(self._extract_label_value(page, 'Date Last updated:')),

                # Description
                'description': self._extract_text(page, '.wrapped-long-string1'),

                # URL
                'detail_url': detail_url,
                'scraped_at': datetime.now()
            }

            # Extract line items
            detail['line_items'] = self._extract_line_items(page)

            print(f"   ✅ Retrieved details for {reference_number} (Budget: {detail.get('approved_budget', 'N/A')})")

            return detail

        except Exception as e:
            print(f"   ❌ Error scraping detail for {reference_number}: {e}")
            return None

    def _extract_label_value(self, page_or_element, label_text: str) -> Optional[str]:
        """
        Extract value that comes after a label
        Example: <label>Control Number: </label><br>25011520108<br>
        """
        try:
            # Find all labels containing the text
            labels = page_or_element.css('label').get_all()

            for label in labels:
                if label_text in label.text:
                    # Get the parent and extract text after the label
                    parent = label.parent
                    if parent:
                        full_text = parent.text
                        # Split by the label and get what comes after
                        if label_text in full_text:
                            value = full_text.split(label_text, 1)[1].strip()
                            # Clean up (remove extra whitespace, newlines)
                            value = re.sub(r'\s+', ' ', value).strip()
                            # Take only the first line if multiple lines
                            value = value.split('\n')[0].strip()
                            return value if value else None
            return None
        except:
            return None

    def _extract_line_items(self, page) -> List[Dict]:
        """Extract line items table from bid detail page"""
        try:
            items = []

            # Find the line items table
            rows = page.css('table.table-bordered.table-striped tbody tr').get_all()

            for row in rows:
                cells = row.css('td').get_all()
                if len(cells) >= 6:
                    try:
                        item = {
                            'item_no': cells[0].text.strip(),
                            'unspsc': cells[1].text.strip(),
                            'lot_name': cells[2].text.strip(),
                            'lot_description': cells[3].text.strip(),
                            'quantity': cells[4].text.strip(),
                            'unit_of_measure': cells[5].text.strip()
                        }
                        items.append(item)
                    except:
                        continue

            return items
        except Exception as e:
            print(f"      ⚠️ Could not extract line items: {e}")
            return []

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
        Save bids to PostgreSQL database with all available fields

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
                    # Save main bid record
                    await conn.execute('''
                        INSERT INTO bid_opportunities (
                            reference_number, title, procurement_mode, classification,
                            agency_name, publish_date, closing_date, status,
                            approved_budget, delivery_period, delivery_location,
                            contact_person, control_number, lot_type, business_category,
                            funding_source, description, detail_url, source_url,
                            scraped_at, created_at
                        ) VALUES (
                            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                            $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, NOW()
                        )
                        ON CONFLICT (reference_number)
                        DO UPDATE SET
                            title = EXCLUDED.title,
                            procurement_mode = EXCLUDED.procurement_mode,
                            classification = EXCLUDED.classification,
                            agency_name = EXCLUDED.agency_name,
                            publish_date = EXCLUDED.publish_date,
                            closing_date = EXCLUDED.closing_date,
                            status = EXCLUDED.status,
                            approved_budget = EXCLUDED.approved_budget,
                            delivery_period = EXCLUDED.delivery_period,
                            delivery_location = EXCLUDED.delivery_location,
                            contact_person = EXCLUDED.contact_person,
                            control_number = EXCLUDED.control_number,
                            lot_type = EXCLUDED.lot_type,
                            business_category = EXCLUDED.business_category,
                            funding_source = EXCLUDED.funding_source,
                            description = EXCLUDED.description,
                            detail_url = EXCLUDED.detail_url,
                            updated_at = NOW()
                    ''',
                        bid.get('reference_number'),
                        bid.get('title'),
                        bid.get('procurement_mode'),
                        bid.get('classification'),
                        bid.get('agency_name'),
                        bid.get('publish_date'),
                        bid.get('closing_date'),
                        bid.get('status'),
                        bid.get('approved_budget'),
                        bid.get('delivery_period'),
                        bid.get('delivery_location'),
                        bid.get('contact_person'),
                        bid.get('control_number'),
                        bid.get('lot_type'),
                        bid.get('business_category'),
                        bid.get('funding_source'),
                        bid.get('description'),
                        bid.get('detail_url'),
                        bid.get('source_url'),
                        bid.get('scraped_at', datetime.now())
                    )

                    # Save line items if present
                    if bid.get('line_items'):
                        # First, delete existing line items for this bid
                        await conn.execute('''
                            DELETE FROM bid_line_items
                            WHERE reference_number = $1
                        ''', bid['reference_number'])

                        # Insert new line items
                        for item in bid['line_items']:
                            await conn.execute('''
                                INSERT INTO bid_line_items (
                                    reference_number, item_no, unspsc, lot_name,
                                    lot_description, quantity, unit_of_measure
                                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                            ''',
                                bid['reference_number'],
                                item.get('item_no'),
                                item.get('unspsc'),
                                item.get('lot_name'),
                                item.get('lot_description'),
                                item.get('quantity'),
                                item.get('unit_of_measure')
                            )

                    saved_count += 1

                except Exception as e:
                    print(f"⚠️ Error saving bid {bid.get('reference_number')}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

            print(f"✅ Saved {saved_count} bids to database")
            return saved_count

        finally:
            await conn.close()

    async def run_daily_scrape(self, max_pages: Optional[int] = None, fetch_details: bool = True) -> Dict:
        """
        Main method for daily scraping job using two-phase approach

        Args:
            max_pages: Optional limit on pages to scrape (None = all pages)
            fetch_details: Whether to fetch detail pages (slower but complete)

        Returns:
            Dictionary with scraping results
        """
        print("\n" + "="*80)
        print(f"🚀 DAILY PHILGEPS SCRAPE - {datetime.now()}")
        print("="*80 + "\n")

        try:
            # PHASE 1: Build index of all bids
            bid_list = await self.scrape_current_opportunities_list(max_pages=max_pages)

            if not bid_list:
                print("⚠️ No bids found in list view")
                return {
                    'success': False,
                    'error': 'No bids found',
                    'timestamp': datetime.now().isoformat()
                }

            # PHASE 2: Fetch details for each bid (if enabled)
            detailed_bids = []
            if fetch_details:
                print(f"\n📥 PHASE 2: Fetching details for {len(bid_list)} bids...")

                for idx, bid in enumerate(bid_list, 1):
                    print(f"\n[{idx}/{len(bid_list)}] Processing {bid['reference_number']}...")

                    detail = await self.scrape_bid_detail(
                        bid['reference_number'],
                        bid['detail_url']
                    )

                    if detail:
                        # Merge list data with detail data
                        merged = {**bid, **detail}
                        detailed_bids.append(merged)
                    else:
                        # If detail fetch failed, keep the list data
                        detailed_bids.append(bid)

                print(f"\n✅ PHASE 2 Complete: Retrieved details for {len(detailed_bids)} bids")
            else:
                detailed_bids = bid_list

            # Save to database
            saved_count = await self.save_to_database(detailed_bids)

            result = {
                'success': True,
                'total_bids': len(bid_list),
                'detailed_bids': len(detailed_bids),
                'saved_count': saved_count,
                'timestamp': datetime.now().isoformat()
            }

            print("\n" + "="*80)
            print("✅ DAILY SCRAPE COMPLETE")
            print(f"   Total bids found: {len(bid_list)}")
            print(f"   Details fetched: {len(detailed_bids)}")
            print(f"   Saved to database: {saved_count}")
            print("="*80 + "\n")

            return result

        except Exception as e:
            print(f"\n❌ SCRAPE FAILED: {e}\n")
            import traceback
            traceback.print_exc()
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
