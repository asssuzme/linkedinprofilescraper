#!/usr/bin/env python3
"""
Simple LinkedIn scraper test - Minimal version to verify cookies work
"""
import asyncio
import json
from playwright.async_api import async_playwright

async def test_cookies():
    """Test if cookies actually work"""

    print("="*60)
    print("LinkedIn Cookie Test")
    print("="*60)

    # Load cookies
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)

    print(f"\n✓ Loaded {len(cookies)} cookies")

    # Start browser
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)  # VISIBLE!

    context = await browser.new_context()
    await context.add_cookies(cookies)

    page = await context.new_page()

    # Test 1: Can we access LinkedIn feed?
    print("\n[1/3] Testing LinkedIn feed access...")
    await page.goto('https://www.linkedin.com/feed/')
    await asyncio.sleep(3)

    current_url = page.url
    print(f"    Current URL: {current_url}")

    if 'login' in current_url or 'authwall' in current_url:
        print("    ❌ FAILED - Cookies are invalid/expired")
        print("    → You need to export fresh cookies")
    else:
        print("    ✓ SUCCESS - Logged in!")

    # Test 2: Can we access a profile?
    print("\n[2/3] Testing profile access...")
    await page.goto('https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/')
    await asyncio.sleep(3)

    current_url = page.url
    print(f"    Current URL: {current_url}")

    if 'authwall' in current_url:
        print("    ❌ FAILED - Hit auth wall")
    else:
        print("    ✓ SUCCESS - Profile loaded")

    # Test 3: Can we find the name?
    print("\n[3/3] Testing if we can find profile elements...")

    # Try to find name
    try:
        name = await page.inner_text('h1', timeout=5000)
        print(f"    ✓ Found name: {name}")
    except:
        print("    ❌ Can't find name element")

    # Try to find headline
    try:
        headline = await page.inner_text('div.text-body-medium', timeout=5000)
        print(f"    ✓ Found headline: {headline}")
    except:
        print("    ❌ Can't find headline element")

    print("\n" + "="*60)
    print("Test complete! Browser will stay open.")
    print("MANUALLY CHECK:")
    print("  1. Are you seeing the actual profile or a login page?")
    print("  2. Can you see name, headline, experience?")
    print("  3. Any consent banners or popups?")
    print("="*60)

    # Keep browser open for manual inspection
    input("\nPress Enter to close browser...")

    await browser.close()

if __name__ == '__main__':
    asyncio.run(test_cookies())
