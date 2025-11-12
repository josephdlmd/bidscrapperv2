"""
Quick test using Playwright directly to check the PhilGEPS page structure
This bypasses scrapling/camoufox issues
"""
import asyncio
from playwright.async_api import async_playwright
import os

os.environ['PHILGEPS_USERNAME'] = 'jdeleon60'
os.environ['PHILGEPS_PASSWORD'] = 'Merritmed#01'

async def test_philgeps():
    print("="*80)
    print("🧪 Quick PhilGEPS Test with Playwright")
    print("="*80)
    print()

    async with async_playwright() as p:
        print("🌐 Launching browser...")
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:
            # Go to login page
            print("📄 Navigating to PhilGEPS login...")
            await page.goto('https://philgeps.gov.ph/Indexes/login', timeout=60000)
            await page.wait_for_load_state('networkidle')

            print(f"   Current URL: {page.url}")
            print(f"   Title: {await page.title()}")

            # Fill credentials
            print("\n🔐 Filling credentials...")
            await page.fill('input[name="username"]', os.environ['PHILGEPS_USERNAME'])
            await page.fill('input[name="password"]', os.environ['PHILGEPS_PASSWORD'])

            print("   ✓ Credentials filled")
            print("   ⚠️ Note: reCAPTCHA needs to be solved manually")
            print("   For full automation, use the scraper with persistent profile")

            # Try to go to the opportunities page directly
            print("\n📄 Testing direct access to opportunities page...")
            await page.goto('https://philgeps.gov.ph/BulletinBoard/view_more_current_oppourtunities', timeout=60000)
            await page.wait_for_load_state('networkidle')

            print(f"   Current URL: {page.url}")

            # Check if we're redirected to login
            if 'login' in page.url.lower():
                print("   ❌ Redirected to login (need authentication)")
            else:
                print("   ✅ Page loaded!")

                # Try to find the table
                table = await page.query_selector('table.dataTable')
                if table:
                    print("   ✅ Found dataTable")

                    rows = await table.query_selector_all('tbody tr')
                    print(f"   Found {len(rows)} rows")

                    if len(rows) > 0:
                        print("\n   First bid:")
                        first_row = rows[0]

                        # Try to extract using data-label
                        ref_cell = await first_row.query_selector('td[data-label="Bid Notice Reference Number"]')
                        if ref_cell:
                            ref_text = await ref_cell.inner_text()
                            print(f"      Reference: {ref_text.strip()}")

                        title_cell = await first_row.query_selector('td[data-label="Notice Title"]')
                        if title_cell:
                            title_text = await title_cell.inner_text()
                            print(f"      Title: {title_text.strip()[:60]}...")

                        mode_cell = await first_row.query_selector('td[data-label="Mode of Procurement"]')
                        if mode_cell:
                            mode_text = await mode_cell.inner_text()
                            print(f"      Mode: {mode_text.strip()}")
                else:
                    print("   ❌ Table not found - might need login")

                    # Check pagination
                    paginator = await page.query_selector('.paginator p')
                    if paginator:
                        pag_text = await paginator.inner_text()
                        print(f"\n   Pagination: {pag_text}")

            print("\n" + "="*80)
            print("✅ Test Complete!")
            print("="*80)
            print("\n📝 Summary:")
            print("   - PhilGEPS is accessible")
            print("   - Login requires reCAPTCHA solving")
            print("   - For full automation:")
            print("     1. Use manual login first to build browser profile")
            print("     2. Then use automated login with persistent session")
            print("     3. The scraper will maintain cookies across runs")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_philgeps())
