#!/usr/bin/env python3
"""
Generate cookies.json by logging into LinkedIn with email/password
"""
import asyncio
import json
from playwright.async_api import async_playwright
from config import Config

async def generate_cookies():
    """Login to LinkedIn and save cookies"""
    print("Logging into LinkedIn to generate cookies...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()

        try:
            # Go to LinkedIn login page
            print("Navigating to LinkedIn login page...")
            await page.goto('https://www.linkedin.com/login', wait_until='networkidle')
            await page.wait_for_timeout(2000)

            # Fill in credentials
            print("Entering credentials...")
            await page.fill('input[name="session_key"]', Config.LINKEDIN_EMAIL)
            await page.wait_for_timeout(500)
            await page.fill('input[name="session_password"]', Config.LINKEDIN_PASSWORD)
            await page.wait_for_timeout(500)

            # Click login button
            print("Clicking login button...")
            await page.click('button[type="submit"]')

            # Wait for navigation to complete
            print("Waiting for login to complete...")
            await page.wait_for_timeout(5000)

            # Check if we need to handle verification
            current_url = page.url
            print(f"Current URL after login: {current_url}")

            if 'checkpoint' in current_url or 'challenge' in current_url or 'uas/authenticate' in current_url:
                print("\n⚠️  LinkedIn is asking for verification!")
                print("Please complete the verification in the browser window.")
                print("Press Enter here after you've completed verification...")
                input()
                await page.wait_for_timeout(2000)
                current_url = page.url

            # Check if we're logged in (not on login page)
            if '/feed' in current_url or '/mynetwork' in current_url:
                print("Already on a logged-in page!")
            else:
                # Try to navigate to feed with a longer timeout
                print("Navigating to feed...")
                try:
                    await page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=60000)
                    await page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"Warning: Could not navigate to feed (continuing anyway): {e}")
                    # Check if we're on a verification page
                    if 'checkpoint' in page.url or 'challenge' in page.url:
                        print("\n⚠️  LinkedIn is asking for verification!")
                        print("Please complete the verification in the browser window.")
                        print("Press Enter here after you've completed verification...")
                        input()
                        await page.wait_for_timeout(2000)

            # Get cookies
            print("Extracting cookies...")
            cookies = await context.cookies()

            # Save cookies to file
            with open('cookies.json', 'w') as f:
                json.dump(cookies, f, indent=2)

            print(f"\n✅ Success! Cookies saved to cookies.json")
            print(f"Found {len(cookies)} cookies")

            # Verify we have the important cookies
            cookie_names = [c['name'] for c in cookies]
            if 'li_at' in cookie_names:
                print("✅ Found li_at cookie (main session cookie)")
            else:
                print("⚠️  Warning: li_at cookie not found")

        except Exception as e:
            print(f"\n❌ Error during login: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(generate_cookies())
