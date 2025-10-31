#!/usr/bin/env python3
"""
LinkedIn Profile Scraper V2 - Improved with debugging
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

from config import Config
from scraper_v2 import LinkedInScraperV2


async def scrape_single_profile_debug(url: str, output_file: str = None):
    """Scrape a single profile with full debugging"""

    # Force visible mode and debugging for troubleshooting
    print("\n" + "="*80)
    print("LinkedIn Profile Scraper V2 - Debug Mode")
    print("="*80 + "\n")

    print("Configuration:")
    print(f"  - Headless: {Config.HEADLESS}")
    print(f"  - Cookies: {Config.LINKEDIN_COOKIES}")
    print(f"  - Target URL: {url}")
    print()

    # Initialize scraper with debugging enabled
    scraper = LinkedInScraperV2(headless=False, debug=True)  # Always visible for debugging

    try:
        await scraper.initialize()

        # Login with cookies
        if Config.LINKEDIN_COOKIES and Path(Config.LINKEDIN_COOKIES).exists():
            print(f"Authenticating with cookies from: {Config.LINKEDIN_COOKIES}")
            await scraper.login_with_cookies(Config.LINKEDIN_COOKIES)
        elif Config.LINKEDIN_EMAIL and Config.LINKEDIN_PASSWORD:
            print("Cookie file not found, but email/password auth not implemented in V2 yet")
            print("Please provide valid cookies")
            return None
        else:
            print("❌ No authentication method configured!")
            print("Please set LINKEDIN_COOKIES in .env file")
            return None

        print(f"\nScraping profile: {url}\n")

        # Scrape the profile
        profile_data = await scraper.scrape_profile(url)

        # Save to file
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'output/profile_{timestamp}.json'

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([profile_data], f, indent=2, ensure_ascii=False)

        print(f"\n✅ Success! Output saved to: {output_path}")
        print(f"\nQuick Summary:")
        print(f"  Name: {profile_data.get('fullName', 'N/A')}")
        print(f"  Headline: {profile_data.get('headline', 'N/A')}")
        print(f"  Location: {profile_data.get('addressWithCountry', 'N/A')}")
        print(f"  Connections: {profile_data.get('connections', 0)}")

        return profile_data

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await scraper.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='LinkedIn Profile Scraper V2 - Improved with debugging',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape single profile (debug mode)
  python main_v2.py -u "https://www.linkedin.com/in/johndoe"

  # Scrape with custom output
  python main_v2.py -u "https://www.linkedin.com/in/johndoe" -o results.json
        """
    )

    parser.add_argument(
        '-u', '--url',
        type=str,
        required=True,
        help='LinkedIn profile URL to scrape'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output JSON file path'
    )

    args = parser.parse_args()

    # Check if cookies exist
    if not Path('cookies.json').exists():
        print("\n❌ Error: cookies.json not found!")
        print("\nPlease create cookies.json with your LinkedIn session cookies.")
        print("\nExample cookies.json format:")
        print("""
[
  {
    "name": "li_at",
    "value": "YOUR_LI_AT_COOKIE_VALUE",
    "domain": ".linkedin.com",
    "path": "/",
    "httpOnly": true,
    "secure": true,
    "sameSite": "Lax"
  },
  {
    "name": "JSESSIONID",
    "value": "ajax:XXXXXXXXXX",
    "domain": ".www.linkedin.com",
    "path": "/",
    "secure": true
  }
]
        """)
        print("\nTo get cookies:")
        print("1. Login to LinkedIn in your browser")
        print("2. Use browser extension like 'EditThisCookie' or 'Cookie-Editor'")
        print("3. Export all linkedin.com cookies")
        print("4. Save as cookies.json in this directory\n")
        sys.exit(1)

    # Run scraper
    try:
        result = asyncio.run(scrape_single_profile_debug(args.url, args.output))
        if result:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
