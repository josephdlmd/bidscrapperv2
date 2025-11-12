"""
Simple first time setup using Playwright directly
Run this ONCE to test login and setup
"""
import asyncio
import os
from playwright.async_api import async_playwright

os.environ['PHILGEPS_USERNAME'] = 'jdeleon60'
os.environ['PHILGEPS_PASSWORD'] = 'Merritmed#01'

async def first_run():
    print("="*80)
    print("FIRST TIME SETUP - Manual CAPTCHA Login")
    print("="*80)
    print("\nOpening browser to PhilGEPS login page...")
    print("1. The browser will open (visible)")
    print("2. Credentials will be pre-filled")
    print("3. Solve the reCAPTCHA")
    print("4. Click Login")
    print("5. Browser will stay open for 60 seconds to verify login")
    print("="*80 + "\n")

    async with async_playwright() as p:
        # Launch visible browser
        browser = await p.chromium.launch(
            headless=False,  # Visible browser for manual interaction
            args=['--start-maximized']
        )

        context = await browser.new_context(
            viewport=None,
            user_data_dir='./browser_profile'  # Save session
        )

        page = await context.new_page()

        try:
            # Go to login page
            print("📄 Navigating to PhilGEPS login...")
            await page.goto('https://philgeps.gov.ph/Indexes/login', timeout=60000)
            await page.wait_for_load_state('networkidle')

            print("✅ Login page loaded")
            print(f"   URL: {page.url}\n")

            # Pre-fill credentials
            try:
                print("📝 Pre-filling credentials...")
                await page.fill('input[name="username"]', os.environ['PHILGEPS_USERNAME'])
                await page.fill('input[name="password"]', os.environ['PHILGEPS_PASSWORD'])
                print("✅ Credentials filled\n")
            except Exception as e:
                print(f"⚠️ Could not auto-fill: {e}")
                print("Please fill credentials manually\n")

            print("="*80)
            print("👉 NOW:")
            print("   1. Solve the reCAPTCHA in the browser")
            print("   2. Click the Login button")
            print("   3. Wait for the dashboard to load")
            print("="*80)

            # Wait 60 seconds for user to complete login
            print("\n⏳ Waiting 60 seconds for you to complete login...")
            await asyncio.sleep(60)

            # Check final URL
            final_url = page.url
            print(f"\n📊 Final URL: {final_url}")

            if 'login' not in final_url.lower():
                print("\n✅ SUCCESS! You appear to be logged in.")
                print("   Browser profile saved to: ./browser_profile/")
                print("   Future runs can use this session.\n")
            else:
                print("\n⚠️ Still on login page - login may not have completed")
                print("   Try running again and make sure to:")
                print("   1. Solve CAPTCHA completely")
                print("   2. Click Login button")
                print("   3. Wait for redirect\n")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await context.close()
            await browser.close()
            print("🔒 Browser closed")

if __name__ == "__main__":
    asyncio.run(first_run())
