"""
LinkedIn Profile Scraper using Crawlee
Much better anti-detection and session management
"""
import asyncio
import json
import re
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Crawlee imports
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext
from crawlee import Request


class LinkedInCrawleeScraper:
    """LinkedIn scraper using Crawlee for better reliability"""

    def __init__(self, cookies_file: str = "cookies.json"):
        self.cookies_file = Path(cookies_file)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        self.results = []

    async def scrape_profiles(self, profile_urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple LinkedIn profiles"""

        print(f"\n{'='*70}")
        print(f"LinkedIn Profile Scraper - Crawlee Edition")
        print(f"{'='*70}\n")

        # Load cookies
        if not self.cookies_file.exists():
            raise FileNotFoundError(f"Cookies file not found: {self.cookies_file}")

        with open(self.cookies_file, 'r') as f:
            cookies = json.load(f)

        print(f"✓ Loaded {len(cookies)} cookies")
        print(f"✓ Profiles to scrape: {len(profile_urls)}\n")

        # Create crawler with better config
        crawler = PlaywrightCrawler(
            headless=False,  # Visible browser for debugging
            browser_type="chromium",
            max_requests_per_crawl=len(profile_urls),
            max_request_retries=2,
            request_handler=self._create_handler(),
        )

        # Configure browser launch options
        crawler.playwright_crawler_options.update({
            "launch_options": {
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ]
            }
        })

        # Add cookies to all requests
        async def add_cookies(context):
            await context.add_cookies(cookies)

        crawler.browser_pool.pre_navigation_hooks.append(add_cookies)

        # Create requests
        requests = [Request.from_url(url) for url in profile_urls]

        # Run crawler
        await crawler.run(requests)

        return self.results

    def _create_handler(self):
        """Create the request handler"""

        async def request_handler(context: PlaywrightCrawlingContext) -> None:
            """Handle each profile scraping request"""

            page = context.page
            url = context.request.url

            print(f"\n{'─'*70}")
            print(f"Scraping: {url}")
            print(f"{'─'*70}")

            try:
                # Wait for page to load
                await page.wait_for_load_state('domcontentloaded')
                await asyncio.sleep(2)

                # Check if we're logged in
                current_url = page.url
                if 'login' in current_url or 'authwall' in current_url:
                    print("❌ Hit login/auth wall - cookies may be invalid")
                    await page.screenshot(path=f"error_authwall_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                    return

                print(f"✓ Page loaded: {current_url}")

                # Scroll to load content
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)

                # Extract data
                profile_data = {
                    'linkedinUrl': url,
                    'scrapedAt': datetime.now().isoformat(),
                }

                # Extract name
                try:
                    name_selectors = [
                        'h1.text-heading-xlarge',
                        'h1[class*="text-heading"]',
                        '.pv-top-card--list h1',
                        'h1'
                    ]

                    for selector in name_selectors:
                        try:
                            name_elem = await page.query_selector(selector)
                            if name_elem:
                                full_name = await name_elem.inner_text()
                                full_name = full_name.strip()
                                if full_name and len(full_name) > 1:
                                    profile_data['fullName'] = full_name
                                    print(f"✓ Found name: {full_name}")
                                    break
                        except:
                            continue

                    if 'fullName' not in profile_data:
                        profile_data['fullName'] = ""
                        print("⚠ Could not find name")

                except Exception as e:
                    print(f"⚠ Error extracting name: {e}")
                    profile_data['fullName'] = ""

                # Extract headline
                try:
                    headline_selectors = [
                        'div.text-body-medium.break-words',
                        'div[class*="text-body-medium"]',
                        '.pv-top-card--list .text-body-medium',
                    ]

                    for selector in headline_selectors:
                        try:
                            headline_elem = await page.query_selector(selector)
                            if headline_elem:
                                headline = await headline_elem.inner_text()
                                headline = headline.strip()
                                # Make sure it's not the name
                                if headline and headline != profile_data.get('fullName', ''):
                                    profile_data['headline'] = headline
                                    print(f"✓ Found headline: {headline[:50]}...")
                                    break
                        except:
                            continue

                    if 'headline' not in profile_data:
                        profile_data['headline'] = ""
                        print("⚠ Could not find headline")

                except Exception as e:
                    print(f"⚠ Error extracting headline: {e}")
                    profile_data['headline'] = ""

                # Extract location
                try:
                    location_selectors = [
                        'span.text-body-small.inline.t-black--light.break-words',
                        'span[class*="text-body-small"]',
                    ]

                    for selector in location_selectors:
                        try:
                            location_elem = await page.query_selector(selector)
                            if location_elem:
                                location = await location_elem.inner_text()
                                location = location.strip()
                                if location and ',' in location:  # Locations usually have commas
                                    profile_data['location'] = location
                                    print(f"✓ Found location: {location}")
                                    break
                        except:
                            continue

                    if 'location' not in profile_data:
                        profile_data['location'] = ""
                        print("⚠ Could not find location")

                except Exception as e:
                    print(f"⚠ Error extracting location: {e}")
                    profile_data['location'] = ""

                # Extract connections count
                try:
                    connections_text = await page.inner_text('li:has-text("connection")', timeout=2000)
                    # Parse number from text like "500+ connections"
                    match = re.search(r'(\d+[\d,]*)', connections_text.replace(',', ''))
                    if match:
                        profile_data['connections'] = int(match.group(1))
                        print(f"✓ Found connections: {profile_data['connections']}")
                    else:
                        profile_data['connections'] = 0
                except:
                    profile_data['connections'] = 0
                    print("⚠ Could not find connections")

                # Extract about section
                try:
                    # Try to click "see more" button
                    try:
                        see_more = await page.query_selector('button:has-text("see more")')
                        if see_more:
                            await see_more.click()
                            await asyncio.sleep(0.5)
                    except:
                        pass

                    about_selectors = [
                        'section:has(#about) div.display-flex span[aria-hidden="true"]',
                        'section[data-section="summary"] span',
                        '#about-this-profile-entrypoint span',
                    ]

                    for selector in about_selectors:
                        try:
                            about_elem = await page.query_selector(selector)
                            if about_elem:
                                about = await about_elem.inner_text()
                                about = about.strip()
                                if about and len(about) > 20:
                                    profile_data['about'] = about
                                    print(f"✓ Found about: {about[:50]}...")
                                    break
                        except:
                            continue

                    if 'about' not in profile_data:
                        profile_data['about'] = ""
                        print("⚠ Could not find about section")

                except Exception as e:
                    print(f"⚠ Error extracting about: {e}")
                    profile_data['about'] = ""

                # Extract experience count
                try:
                    exp_section = await page.query_selector('section:has(#experience)')
                    if exp_section:
                        exp_items = await exp_section.query_selector_all('li')
                        profile_data['experienceCount'] = len(exp_items)
                        print(f"✓ Found {len(exp_items)} experience items")
                    else:
                        profile_data['experienceCount'] = 0
                except:
                    profile_data['experienceCount'] = 0

                # Extract education count
                try:
                    edu_section = await page.query_selector('section:has(#education)')
                    if edu_section:
                        edu_items = await edu_section.query_selector_all('li')
                        profile_data['educationCount'] = len(edu_items)
                        print(f"✓ Found {len(edu_items)} education items")
                    else:
                        profile_data['educationCount'] = 0
                except:
                    profile_data['educationCount'] = 0

                # Take screenshot for debugging
                screenshot_path = self.output_dir / f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"✓ Screenshot saved: {screenshot_path}")

                # Add to results
                self.results.append(profile_data)

                print(f"\n✅ Successfully scraped profile")
                print(f"   Name: {profile_data.get('fullName', 'N/A')}")
                print(f"   Headline: {profile_data.get('headline', 'N/A')[:50]}...")
                print(f"   Location: {profile_data.get('location', 'N/A')}")
                print(f"   Connections: {profile_data.get('connections', 0)}")

            except Exception as e:
                print(f"❌ Error scraping profile: {e}")
                import traceback
                traceback.print_exc()

        return request_handler


async def main():
    """Main entry point"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scraper_crawlee.py <profile_url> [profile_url2] [...]")
        print("\nExample:")
        print('  python scraper_crawlee.py "https://www.linkedin.com/in/johndoe/"')
        sys.exit(1)

    profile_urls = sys.argv[1:]

    scraper = LinkedInCrawleeScraper()
    results = await scraper.scrape_profiles(profile_urls)

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = scraper.output_dir / f'profiles_crawlee_{timestamp}.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"✅ Scraping complete!")
    print(f"📁 Results saved to: {output_file}")
    print(f"📊 Profiles scraped: {len(results)}/{len(profile_urls)}")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    asyncio.run(main())
