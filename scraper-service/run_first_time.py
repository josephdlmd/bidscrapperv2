"""
First time setup - Manual login to solve CAPTCHA
Run this ONCE to establish browser session
"""
import asyncio
import os
from scraper.philgeps_scraper import PhilGEPSScraper

os.environ['PHILGEPS_USERNAME'] = 'jdeleon60'
os.environ['PHILGEPS_PASSWORD'] = 'Merritmed#01'

async def first_run():
    print("="*80)
    print("FIRST TIME SETUP - Manual CAPTCHA Login")
    print("="*80)
    print("\nA browser window will open...")
    print("1. Solve the reCAPTCHA if it appears")
    print("2. Click the Login button")
    print("3. Wait until you see the dashboard")
    print("4. Come back here and press ENTER\n")

    scraper = PhilGEPSScraper()

    await scraper.login_manual()

    print("\n✅ Session saved!")
    print("Browser profile is now saved in ./browser_profile/")
    print("Future runs will be automated.\n")

    scraper.close()

if __name__ == "__main__":
    asyncio.run(first_run())
