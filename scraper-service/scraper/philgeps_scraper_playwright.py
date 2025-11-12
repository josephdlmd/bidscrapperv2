"""
PhilGEPS Scraper with Playwright
Scrapes bid opportunities from PhilGEPS with reCAPTCHA handling
"""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import asyncpg
import asyncio
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

        self.playwright = None
        self.context = None
        self.page = None
        self.logged_in = False

        print(f"🔧 Initialized scraper with profile: {self.profile_dir}")

    async def _ensure_browser(self):
        """Ensure browser context is initialized"""
        if self.context is None:
            self.playwright = await async_playwright().start()
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.page = await self.context.new_page()

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

        # Use visible browser for manual login
        if self.playwright:
            await self.context.close()
            await self.playwright.stop()

        self.playwright = await async_playwright().start()
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir),
            headless=False,  # Visible for manual login
            args=['--start-maximized']
        )
        self.page = await self.context.new_page()

        await self.page.goto("https://philgeps.gov.ph/Indexes/login", timeout=60000)
        await self.page.wait_for_load_state('networkidle')

        # Pre-fill credentials
        try:
            await self.page.fill('input[name="username"]', os.getenv('PHILGEPS_USERNAME'))
            await self.page.fill('input[name="password"]', os.getenv('PHILGEPS_PASSWORD'))
            print("✅ Credentials pre-filled")
        except Exception as e:
            print(f"⚠️ Could not pre-fill credentials: {e}")
            print("Please enter them manually")

        # Wait for user to complete login
        input("\n👉 Press ENTER after you've successfully logged in...")

        self.logged_in = True
        print("✅ Login session saved in persistent profile!")
        print("   Future automated logins will use this profile\n")

        return True

    async def ensure_logged_in(self) -> bool:
        """
        Ensure we're logged in using persistent profile

        Returns:
            bool: True if logged in
        """
        await self._ensure_browser()

        if self.logged_in:
            return True

        # Check if already logged in from persistent profile
        try:
            await self.page.goto("https://philgeps.gov.ph/BulletinBoard/view_more_current_oppourtunities", timeout=60000)
            await self.page.wait_for_load_state('networkidle')

            # Check if we're redirected to login
            if 'login' in self.page.url.lower():
                print("❌ Not logged in - manual login required")
                return await self.login_manual()
            else:
                print("✅ Already logged in from persistent profile")
                self.logged_in = True
                return True

        except Exception as e:
            print(f"⚠️ Error checking login status: {e}")
            return False

    def _extract_text(self, element, selector: str) -> Optional[str]:
        """Extract text from element using selector"""
        try:
            el = element.query_selector(selector)
            if el:
                return el.inner_text().strip()
        except:
            pass
        return None

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

            await self.page.goto(url, timeout=60000)
            await self.page.wait_for_load_state('networkidle')

            # Check if we're still logged in
            if 'login' in self.page.url.lower():
                print("❌ Session expired - need to login again")
                self.logged_in = False
                await self.ensure_logged_in()
                await self.page.goto(url, timeout=60000)
                await self.page.wait_for_load_state('networkidle')

            # Extract pagination info
            try:
                pagination_elem = await self.page.query_selector('.paginator p')
                if pagination_elem:
                    pagination_text = await pagination_elem.inner_text()
                    print(f"   {pagination_text}")
                    # Extract total from text like "Page 1 of 5, showing 20 record(s) out of 81 total"
                    match = re.search(r'out of (\d+) total', pagination_text)
                    if match:
                        total_bids = int(match.group(1))
            except:
                pass

            # Extract bid rows
            try:
                rows = await self.page.query_selector_all('table.dataTable tbody tr')

                if not rows or len(rows) == 0:
                    print("   No more bids found - end of pagination")
                    break

                print(f"   Found {len(rows)} bids on this page")

                for idx, row in enumerate(rows):
                    try:
                        # Extract reference number and detail URL
                        ref_link = await row.query_selector('td[data-label="Bid Notice Reference Number"] a')
                        reference_number = None
                        detail_url = None

                        if ref_link:
                            reference_number = (await ref_link.inner_text()).strip()
                            detail_url = await ref_link.get_attribute('href')
                            if detail_url and not detail_url.startswith('http'):
                                detail_url = f"https://philgeps.gov.ph{detail_url}"

                        if not reference_number:
                            continue

                        # Extract all fields using data-label selectors
                        title_elem = await row.query_selector('td[data-label="Notice Title"] .wrapped-long-string')
                        title = await title_elem.inner_text() if title_elem else None

                        procurement_elem = await row.query_selector('td[data-label="Mode of Procurement"]')
                        procurement_mode = await procurement_elem.inner_text() if procurement_elem else None

                        classification_elem = await row.query_selector('td[data-label="Classification"]')
                        classification = await classification_elem.inner_text() if classification_elem else None

                        agency_elem = await row.query_selector('td[data-label="Procuring Entity Name"]')
                        agency_name = await agency_elem.inner_text() if agency_elem else None

                        publish_elem = await row.query_selector('td[data-label="Published Date"]')
                        publish_date = await publish_elem.inner_text() if publish_elem else None

                        closing_elem = await row.query_selector('td[data-label="Closing Date"]')
                        closing_date = await closing_elem.inner_text() if closing_elem else None

                        status_elem = await row.query_selector('td[data-label="Status"]')
                        status = await status_elem.inner_text() if status_elem else None

                        bid = {
                            'reference_number': reference_number,
                            'title': title.strip() if title else None,
                            'procurement_mode': procurement_mode.strip() if procurement_mode else None,
                            'classification': classification.strip() if classification else None,
                            'agency_name': agency_name.strip() if agency_name else None,
                            'publish_date': publish_date.strip() if publish_date else None,
                            'closing_date': closing_date.strip() if closing_date else None,
                            'status': status.strip() if status else None,
                            'detail_url': detail_url
                        }

                        all_bids.append(bid)

                    except Exception as e:
                        print(f"   ⚠️ Error extracting row {idx + 1}: {e}")
                        continue

            except Exception as e:
                print(f"   ❌ Error processing page: {e}")
                break

            current_page += 1
            await asyncio.sleep(1)  # Rate limiting

        print(f"\n✅ PHASE 1 Complete: Found {len(all_bids)} total bids")
        if total_bids:
            print(f"   Expected: {total_bids} bids")

        return all_bids

    def _parse_budget(self, budget_text: Optional[str]) -> Optional[float]:
        """Parse budget string to float"""
        if not budget_text:
            return None
        try:
            # Remove currency symbols, commas, and whitespace
            cleaned = re.sub(r'[₱$,\s]', '', budget_text)
            return float(cleaned)
        except:
            return None

    async def scrape_bid_detail(self, reference_number: str, detail_url: str) -> Optional[Dict]:
        """
        PHASE 2: Scrape detailed information for a specific bid

        Args:
            reference_number: Bid reference number
            detail_url: URL to bid detail page

        Returns:
            Dictionary with detailed bid information
        """
        try:
            await self.page.goto(detail_url, timeout=60000)
            await self.page.wait_for_load_state('networkidle')

            # Helper to extract label-value pairs
            async def extract_label_value(label_text: str) -> Optional[str]:
                try:
                    # Find label containing the text
                    labels = await self.page.query_selector_all('label')
                    for label in labels:
                        text = await label.inner_text()
                        if label_text.lower() in text.lower():
                            # Get the next text node after the label
                            parent = await label.evaluate_handle('el => el.parentElement')
                            value = await parent.evaluate('el => el.textContent')
                            # Remove the label text and clean up
                            value = value.replace(text, '').strip()
                            # Remove leading/trailing <br> tags
                            value = re.sub(r'^<br>|<br>$', '', value).strip()
                            if value:
                                return value
                except:
                    pass
                return None

            detail = {
                'reference_number': reference_number,
                'approved_budget': self._parse_budget(await extract_label_value('Approved Budget of the Contract:')),
                'delivery_period': await extract_label_value('Delivery Period:'),
                'contact_person': await extract_label_value('Contact Person:'),
                'contact_email': await extract_label_value('Email Address:'),
                'contact_phone': await extract_label_value('Contact Number:'),
                'delivery_location': await extract_label_value('Place of Delivery:'),
                'business_category': await extract_label_value('Business Category:'),
                'funding_source': await extract_label_value('Funding Source:'),
                'funding_instrument': await extract_label_value('Funding Instrument:'),
                'reason': await extract_label_value('Reason for Award:'),
                'solicitation_number': await extract_label_value('Solicitation Number:'),
                'trade_agreement': await extract_label_value('Trade Agreement:'),
                'control_number': await extract_label_value('Control Number:'),
                'area_of_delivery': await extract_label_value('Area of Delivery:')
            }

            # Extract line items if present
            detail['line_items'] = []
            try:
                line_item_rows = await self.page.query_selector_all('table.table-bordered tbody tr')
                for row in line_item_rows:
                    cells = await row.query_selector_all('td')
                    if len(cells) >= 6:
                        item = {
                            'lot_name': await cells[0].inner_text() if len(cells) > 0 else None,
                            'unspsc': await cells[1].inner_text() if len(cells) > 1 else None,
                            'item_name': await cells[2].inner_text() if len(cells) > 2 else None,
                            'description': await cells[3].inner_text() if len(cells) > 3 else None,
                            'quantity': await cells[4].inner_text() if len(cells) > 4 else None,
                            'unit_of_measure': await cells[5].inner_text() if len(cells) > 5 else None,
                        }
                        # Clean up values
                        for key in item:
                            if item[key]:
                                item[key] = item[key].strip()
                        detail['line_items'].append(item)
            except Exception as e:
                print(f"   ⚠️ Could not extract line items: {e}")

            return detail

        except Exception as e:
            print(f"   ❌ Error scraping detail for {reference_number}: {e}")
            return None

    async def run_daily_scrape(self, max_pages: Optional[int] = None, fetch_details: bool = True) -> Dict:
        """
        Main method to run daily scraping job

        Args:
            max_pages: Optional limit on pages to scrape
            fetch_details: Whether to fetch detailed information

        Returns:
            Dictionary with scraping results and statistics
        """
        start_time = datetime.now()

        try:
            # PHASE 1: Get list of all bids
            bid_list = await self.scrape_current_opportunities_list(max_pages=max_pages)

            if not bid_list:
                return {
                    'success': False,
                    'error': 'No bids found in list',
                    'total_bids': 0
                }

            result = {
                'success': True,
                'total_bids': len(bid_list),
                'detailed_bids': 0,
                'saved_count': 0,
                'start_time': start_time.isoformat(),
                'end_time': None
            }

            # PHASE 2: Fetch details if requested
            if fetch_details:
                print(f"\n📋 PHASE 2: Fetching details for {len(bid_list)} bids...")

                for idx, bid in enumerate(bid_list, 1):
                    print(f"\n[{idx}/{len(bid_list)}] Fetching details for bid #{bid['reference_number']}...")

                    detail = await self.scrape_bid_detail(
                        bid['reference_number'],
                        bid['detail_url']
                    )

                    if detail:
                        # Merge detail into bid
                        bid.update(detail)
                        result['detailed_bids'] += 1
                        print(f"   ✓ Budget: {detail.get('approved_budget', 'N/A')}")

                    await asyncio.sleep(1)  # Rate limiting

            result['end_time'] = datetime.now().isoformat()
            return result

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'total_bids': 0
            }

    def close(self):
        """Close browser and cleanup resources"""
        # Playwright cleanup happens async, we'll handle it in __del__ or explicit async close
        print("📌 Scraper session ended (browser profile saved)")

    async def async_close(self):
        """Async cleanup of browser resources"""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        print("🔒 Browser closed")
