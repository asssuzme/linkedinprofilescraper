#!/usr/bin/env python3
"""
LinkedIn Profile Scraper
Main entry point for scraping LinkedIn profiles
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

from config import Config
from scraper import LinkedInScraper


async def scrape_profiles(profile_urls: list, output_file: str = None):
    """
    Scrape multiple LinkedIn profiles

    Args:
        profile_urls: List of LinkedIn profile URLs to scrape
        output_file: Optional output file path (default: output/profiles_TIMESTAMP.json)
    """
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please set up your .env file. See .env.example for reference.")
        return

    # Initialize scraper
    scraper = LinkedInScraper(headless=Config.HEADLESS)
    await scraper.initialize()

    try:
        # Login
        if Config.LINKEDIN_COOKIES and Path(Config.LINKEDIN_COOKIES).exists():
            await scraper.login_with_cookies(Config.LINKEDIN_COOKIES)
        elif Config.LINKEDIN_EMAIL and Config.LINKEDIN_PASSWORD:
            await scraper.login_with_credentials(Config.LINKEDIN_EMAIL, Config.LINKEDIN_PASSWORD)
        else:
            print("❌ No valid authentication method provided")
            return

        # Scrape profiles
        results = []
        total = min(len(profile_urls), Config.MAX_PROFILES)

        print(f"\n📊 Starting to scrape {total} profiles...")
        print("─" * 60)

        for i, url in enumerate(profile_urls[:total], 1):
            print(f"\n[{i}/{total}] Processing: {url}")

            try:
                profile_data = await scraper.scrape_profile(url)
                results.append(profile_data)

                # Save progress after each profile
                if output_file:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)

            except Exception as e:
                print(f"❌ Error scraping profile {url}: {e}")
                # Continue with next profile
                continue

            # Delay between profiles to avoid rate limiting
            if i < total:
                print(f"⏳ Waiting {Config.DELAY_BETWEEN_PROFILES} seconds before next profile...")
                await asyncio.sleep(Config.DELAY_BETWEEN_PROFILES)

        # Save final results
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Config.OUTPUT_DIR / f'profiles_{timestamp}.json'

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\n" + "─" * 60)
        print(f"✅ Successfully scraped {len(results)} profiles")
        print(f"📁 Output saved to: {output_file}")
        print(f"📊 Total profiles processed: {len(results)}/{total}")

    finally:
        await scraper.close()


async def scrape_single_profile(url: str):
    """Scrape a single profile and print to stdout"""
    Config.validate()

    scraper = LinkedInScraper(headless=Config.HEADLESS)
    await scraper.initialize()

    try:
        # Login
        if Config.LINKEDIN_COOKIES and Path(Config.LINKEDIN_COOKIES).exists():
            await scraper.login_with_cookies(Config.LINKEDIN_COOKIES)
        elif Config.LINKEDIN_EMAIL and Config.LINKEDIN_PASSWORD:
            await scraper.login_with_credentials(Config.LINKEDIN_EMAIL, Config.LINKEDIN_PASSWORD)

        # Scrape
        profile_data = await scraper.scrape_profile(url)

        # Print to stdout
        print(json.dumps([profile_data], indent=2, ensure_ascii=False))

    finally:
        await scraper.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='LinkedIn Profile Scraper - Extract comprehensive data from LinkedIn profiles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape profiles from input file
  python main.py -i input.json

  # Scrape a single profile
  python main.py -u "https://www.linkedin.com/in/johndoe"

  # Scrape with custom output file
  python main.py -i input.json -o output/results.json

  # Scrape multiple URLs from command line
  python main.py -u "https://linkedin.com/in/user1" "https://linkedin.com/in/user2"
        """
    )

    parser.add_argument(
        '-i', '--input',
        type=str,
        help='Input JSON file containing profile URLs (format: [{"url": "..."}, ...])'
    )
    parser.add_argument(
        '-u', '--urls',
        type=str,
        nargs='+',
        help='One or more LinkedIn profile URLs to scrape'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output JSON file path (default: output/profiles_TIMESTAMP.json)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (default: from .env)'
    )

    args = parser.parse_args()

    # Override headless mode if specified
    if args.headless:
        Config.HEADLESS = True

    # Determine profile URLs
    profile_urls = []

    if args.input:
        # Load from input file
        input_file = Path(args.input)
        if not input_file.exists():
            print(f"❌ Input file not found: {args.input}")
            sys.exit(1)

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Handle different input formats
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, str):
                        profile_urls.append(item)
                    elif isinstance(item, dict) and 'url' in item:
                        profile_urls.append(item['url'])
                    elif isinstance(item, dict) and 'linkedinUrl' in item:
                        profile_urls.append(item['linkedinUrl'])

    elif args.urls:
        profile_urls = args.urls

    else:
        parser.print_help()
        print("\n❌ Error: You must provide either -i/--input or -u/--urls")
        sys.exit(1)

    if not profile_urls:
        print("❌ No valid profile URLs found")
        sys.exit(1)

    # Run scraper
    try:
        asyncio.run(scrape_profiles(profile_urls, args.output))
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
