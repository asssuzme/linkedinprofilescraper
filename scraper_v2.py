"""
Improved LinkedIn Profile Scraper with Debugging
"""
import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from datetime import datetime

from config import Config
from parsers import (
    extract_text, extract_attribute, parse_duration_to_years,
    parse_connections_count, extract_company_id, clean_url,
    normalize_linkedin_url, extract_email_from_text, extract_phone_from_text,
    split_name
)


class LinkedInScraperV2:
    """Improved scraper with better debugging and multiple selector fallbacks"""

    def __init__(self, headless: bool = True, debug: bool = False):
        self.headless = headless
        self.debug = debug
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.screenshot_dir = Path('screenshots')
        self.screenshot_dir.mkdir(exist_ok=True)

    def log(self, message: str):
        """Debug logging"""
        if self.debug or not self.headless:
            print(f"[DEBUG] {message}")

    async def screenshot(self, name: str):
        """Take a screenshot for debugging"""
        if self.page and (self.debug or not self.headless):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            path = self.screenshot_dir / f"{name}_{timestamp}.png"
            await self.page.screenshot(path=str(path))
            self.log(f"Screenshot saved: {path}")

    async def initialize(self):
        """Initialize browser with better anti-detection"""
        self.log("Initializing browser...")
        playwright = await async_playwright().start()

        launch_options = {
            'headless': self.headless,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        }

        # Resolve Chromium path on macOS if provided via env or default cache
        import os, platform
        browsers_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH')
        if not browsers_path and platform.system() == 'Darwin':
            browsers_path = os.path.expanduser('~/Library/Caches/ms-playwright')
        if browsers_path and platform.system() == 'Darwin':
            # Try common installed folder name pattern
            try:
                from glob import glob
                candidates = glob(os.path.join(browsers_path, 'chromium-*', 'Chromium.app', 'Contents', 'MacOS', 'Chromium'))
                if candidates:
                    launch_options['executable_path'] = candidates[0]
                    self.log(f"Using Chromium binary: {launch_options['executable_path']}")
            except Exception as _:
                pass

        proxy_config = Config.get_proxy_config()
        if proxy_config:
            launch_options['proxy'] = proxy_config

        self.browser = await playwright.chromium.launch(**launch_options)

        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            ignore_https_errors=True,
        )

        await self.context.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })

        self.page = await self.context.new_page()

        # Enhanced anti-detection
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            window.chrome = { runtime: {} };
        """)

        self.log("Browser initialized")

    async def login_with_cookies(self, cookies_path: str):
        """Login using saved cookies with better error handling"""
        self.log(f"Loading cookies from {cookies_path}...")

        cookies_file = Path(cookies_path)
        if not cookies_file.exists():
            raise FileNotFoundError(f"Cookies file not found: {cookies_path}")

        with open(cookies_file, 'r') as f:
            cookies = json.load(f)

        self.log(f"Loaded {len(cookies)} cookies")

        # Add cookies
        await self.context.add_cookies(cookies)

        # Test authentication by visiting feed
        self.log("Testing authentication...")
        await self.page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(3)

        await self.screenshot("after_cookie_login")

        # Check if we're logged in
        current_url = self.page.url
        self.log(f"Current URL after cookie load: {current_url}")

        if 'login' in current_url or 'authwall' in current_url:
            raise Exception("Cookies are invalid or expired - LinkedIn is showing login page")

        self.log("✓ Successfully authenticated with cookies")

    async def scrape_profile(self, profile_url: str) -> Dict[str, Any]:
        """Scrape profile with better error handling and multiple selector fallbacks"""
        print(f"\n{'='*60}")
        print(f"Scraping: {profile_url}")
        print(f"{'='*60}\n")

        profile_url = normalize_linkedin_url(profile_url)

        # Navigate to profile
        self.log("Navigating to profile...")
        try:
            await self.page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)
        except Exception as e:
            self.log(f"Navigation error: {e}")
            await self.screenshot("navigation_error")
            raise

        await self.screenshot("profile_loaded")

        # Check if we hit an auth wall
        if 'authwall' in self.page.url or 'login' in self.page.url:
            self.log("⚠️  Hit authentication wall - cookies may be expired")
            await self.screenshot("authwall")
            raise Exception("Authentication required - please refresh cookies")

        # Scroll to load dynamic content
        self.log("Scrolling to load content...")
        await self._scroll_page()
        await self.screenshot("after_scroll")

        # Debug: Save HTML to inspect structure
        try:
            html_content = await self.page.content()
            debug_html_path = self.screenshot_dir / f"page_html_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(debug_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.log(f"Saved page HTML for debugging: {debug_html_path}")
        except Exception as e:
            self.log(f"Could not save HTML: {e}")

        # Extract data with multiple fallbacks
        profile_data = {'linkedinUrl': profile_url}

        self.log("Extracting basic info...")
        profile_data.update(await self._extract_basic_info_v2())

        self.log("Extracting profile pictures...")
        profile_data.update(await self._extract_profile_pictures_v2())

        self.log("Extracting about section...")
        profile_data['about'] = await self._extract_about_v2()

        self.log("Extracting current job...")
        profile_data.update(await self._extract_current_job_v2())

        self.log("Extracting experiences...")
        profile_data['experiences'] = await self._extract_experiences_v2()

        self.log("Extracting education...")
        profile_data['educations'] = await self._extract_education_v2()

        self.log("Extracting skills...")
        profile_data.update(await self._extract_skills_v2())

        # Contact info
        profile_data['email'] = None
        profile_data['mobileNumber'] = None

        # Placeholders for other sections
        profile_data['licenseAndCertificates'] = []
        profile_data['languages'] = []
        profile_data['honorsAndAwards'] = []
        profile_data['volunteerAndAwards'] = []
        profile_data['projects'] = []
        profile_data['publications'] = []
        profile_data['patents'] = []
        profile_data['courses'] = []
        profile_data['testScores'] = []
        profile_data['organizations'] = []
        profile_data['volunteerCauses'] = []
        profile_data['verifications'] = []
        profile_data['promos'] = []
        profile_data['highlights'] = []
        profile_data['interests'] = []
        profile_data['recommendations'] = []
        profile_data['updates'] = []

        print(f"\n✓ Successfully scraped: {profile_data.get('fullName', 'Unknown')}")
        print(f"  - Name: {profile_data.get('fullName')}")
        print(f"  - Headline: {profile_data.get('headline')}")
        print(f"  - Location: {profile_data.get('addressWithCountry')}")
        print(f"  - Connections: {profile_data.get('connections')}")
        print(f"  - Experiences: {len(profile_data.get('experiences', []))}")
        print(f"  - Education: {len(profile_data.get('educations', []))}")
        print(f"  - Skills: {len(profile_data.get('skills', []))}")

        return profile_data

    async def _scroll_page(self):
        """Scroll page to load dynamic content"""
        for i in range(3):
            await self.page.evaluate(f'window.scrollTo(0, {(i + 1) * 800})')
            await asyncio.sleep(0.5)
        await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(1)
        await self.page.evaluate('window.scrollTo(0, 0)')
        await asyncio.sleep(0.5)

    async def _extract_basic_info_v2(self) -> Dict[str, Any]:
        """Extract basic info with multiple selector fallbacks"""
        data = {}

        try:
            # Full name - try multiple selectors
            # First wait for any h1 to appear
            try:
                await self.page.wait_for_selector('h1', timeout=10000, state='visible')
            except:
                pass

            name_selectors = [
                'h1.text-heading-xlarge',
                'h1[class*="text-heading-xlarge"]',
                'h1[class*="text-heading"]',
                '.pv-text-details__left-panel h1',
                'section.top-card h1',
                'div[data-section="profile-top-card"] h1',
                'main h1',
                'h1.inline.t-24.t-black.t-normal.break-words',
                'h1',
            ]

            full_name = ""
            for selector in name_selectors:
                try:
                    elem = await self.page.query_selector(selector)
                    if elem:
                        # Try inner_text first (more reliable)
                        try:
                            full_name = await elem.inner_text()
                            full_name = full_name.strip()
                        except:
                            full_name = await extract_text(elem)
                        
                        if full_name and len(full_name) > 1:
                            self.log(f"Found name with selector: {selector} -> {full_name}")
                            break
                except:
                    continue

            data['fullName'] = full_name
            first_name, last_name = split_name(full_name)
            data['firstName'] = first_name
            data['lastName'] = last_name

            # Headline - multiple selectors
            headline_selectors = [
                'div.text-body-medium.break-words',
                'div[class*="text-body-medium"]',
                '.pv-text-details__left-panel .text-body-medium',
                'section.top-card div[class*="text-body"]',
            ]

            headline = ""
            for selector in headline_selectors:
                try:
                    elem = await self.page.query_selector(selector)
                    if elem:
                        headline = await extract_text(elem)
                        if headline and headline != full_name:  # Make sure it's not the name
                            self.log(f"Found headline with selector: {selector}")
                            break
                except:
                    continue

            data['headline'] = headline

            # Location - multiple selectors
            location_selectors = [
                'span.text-body-small.inline.t-black--light.break-words',
                'span[class*="text-body-small"]',
                '.pv-text-details__left-panel span.text-body-small',
                'section.top-card span[class*="text-body-small"]',
            ]

            location = ""
            for selector in location_selectors:
                try:
                    elem = await self.page.query_selector(selector)
                    if elem:
                        location = await extract_text(elem)
                        if location and ',' in location:  # Locations usually have commas
                            self.log(f"Found location with selector: {selector}")
                            break
                except:
                    continue

            data['addressWithCountry'] = location

            if location:
                parts = [p.strip() for p in location.split(',')]
                if len(parts) >= 2:
                    data['addressCountryOnly'] = parts[-1]
                    data['addressWithoutCountry'] = ', '.join(parts[:-1])
                else:
                    data['addressCountryOnly'] = location
                    data['addressWithoutCountry'] = ""
            else:
                data['addressCountryOnly'] = ""
                data['addressWithoutCountry'] = ""

            # Connections/Followers
            data['connections'] = 0
            data['followers'] = 0

            try:
                # Try to find connection count
                conn_text = await self.page.inner_text('li:has-text("connection")', timeout=2000)
                data['connections'] = parse_connections_count(conn_text)
                self.log(f"Found connections: {data['connections']}")
            except:
                pass

            try:
                # Try to find follower count
                follower_text = await self.page.inner_text('li:has-text("follower")', timeout=2000)
                data['followers'] = parse_connections_count(follower_text)
                self.log(f"Found followers: {data['followers']}")
            except:
                pass

            # Public identifier
            url_match = re.search(r'/in/([^/?]+)', self.page.url)
            data['publicIdentifier'] = url_match.group(1) if url_match else ""

            data['urn'] = ""
            data['openConnection'] = False

        except Exception as e:
            self.log(f"Error in _extract_basic_info_v2: {e}")
            import traceback
            traceback.print_exc()

        return data

    async def _extract_profile_pictures_v2(self) -> Dict[str, Any]:
        """Extract profile pictures with fallbacks"""
        data = {
            'profilePic': "",
            'profilePicHighQuality': "",
            'profilePicAllDimensions': []
        }

        try:
            img_selectors = [
                'img.pv-top-card-profile-picture__image',
                'img[class*="profile-picture"]',
                'button[aria-label*="View"] img',
                'img.pv-top-card--photo',
            ]

            for selector in img_selectors:
                try:
                    img_elem = await self.page.query_selector(selector)
                    if img_elem:
                        src = await extract_attribute(img_elem, 'src')
                        if src and 'profile' in src.lower():
                            self.log(f"Found profile pic with selector: {selector}")
                            data['profilePic'] = src
                            data['profilePicHighQuality'] = src
                            data['profilePicAllDimensions'] = [
                                {'width': 200, 'height': 200, 'url': src}
                            ]
                            break
                except:
                    continue
        except Exception as e:
            self.log(f"Error extracting profile pictures: {e}")

        return data

    async def _extract_about_v2(self) -> str:
        """Extract about section with fallbacks"""
        try:
            # Try to expand "see more"
            try:
                show_more = await self.page.query_selector('button:has-text("see more")', timeout=1000)
                if show_more:
                    await show_more.click()
                    await asyncio.sleep(0.5)
            except:
                pass

            about_selectors = [
                'section:has(div#about) div.display-flex span[aria-hidden="true"]',
                'section[data-section="summary"] span[aria-hidden="true"]',
                '#about-this-profile-entrypoint span',
                'section:has-text("About") span[aria-hidden="true"]',
            ]

            for selector in about_selectors:
                try:
                    elem = await self.page.query_selector(selector)
                    if elem:
                        text = await extract_text(elem)
                        if text and len(text) > 20:  # About sections are usually longer
                            self.log(f"Found about with selector: {selector}")
                            return text
                except:
                    continue
        except Exception as e:
            self.log(f"Error extracting about: {e}")

        return ""

    async def _extract_current_job_v2(self) -> Dict[str, Any]:
        """Extract current job info"""
        data = {
            'jobTitle': "",
            'companyName': "",
            'companyIndustry': "",
            'companyWebsite': "",
            'companyLinkedin': "",
            'companyFoundedIn': None,
            'companySize': "",
            'currentJobDuration': "",
            'currentJobDurationInYrs': 0.0
        }

        try:
            # Find experience section
            exp_section = await self.page.query_selector('section:has(div#experience)')
            if exp_section:
                # Get first experience item
                first_exp = await exp_section.query_selector('li')
                if first_exp:
                    # Job title
                    title_elem = await first_exp.query_selector('div[class*="display-flex"] span[aria-hidden="true"]')
                    if title_elem:
                        data['jobTitle'] = await extract_text(title_elem)

                    # Company name
                    company_elem = await first_exp.query_selector('span.t-14 span[aria-hidden="true"]')
                    if company_elem:
                        company_text = await extract_text(company_elem)
                        data['companyName'] = company_text.split(' · ')[0].strip() if ' · ' in company_text else company_text

                    self.log(f"Found current job: {data['jobTitle']} at {data['companyName']}")
        except Exception as e:
            self.log(f"Error extracting current job: {e}")

        return data

    async def _extract_experiences_v2(self) -> List[Dict[str, Any]]:
        """Extract work experiences"""
        experiences = []

        try:
            # Try multiple selectors for experience section
            exp_selectors = [
                'section:has(div#experience)',
                'section[data-section="experience"]',
                'section#experience',
                'section.artdeco-card:has-text("Experience")',
                'section:has-text("Experience")',
            ]
            
            exp_section = None
            for selector in exp_selectors:
                try:
                    exp_section = await self.page.query_selector(selector)
                    if exp_section:
                        self.log(f"Found experience section with selector: {selector}")
                        break
                except:
                    continue
            
            if exp_section:
                exp_items = await exp_section.query_selector_all('li')
                self.log(f"Found {len(exp_items)} experience items")
                
                # If no items with li, try other patterns
                if len(exp_items) == 0:
                    exp_items = await exp_section.query_selector_all('div[class*="experience"]')
                    self.log(f"Trying alternative selector, found {len(exp_items)} items")

                for item in exp_items[:5]:  # Limit to first 5
                    try:
                        title_elem = await item.query_selector('div span[aria-hidden="true"]')
                        company_elem = await item.query_selector('span.t-14 span[aria-hidden="true"]')

                        if title_elem:
                            title = await extract_text(title_elem)
                            company = await extract_text(company_elem) if company_elem else ""

                            experiences.append({
                                'title': title,
                                'company': company,
                                'companyId': "",
                                'companyUrn': "",
                                'companyLink1': "",
                                'logo': "",
                                'subtitle': "",
                                'caption': "",
                                'breakdown': False,
                                'subComponents': []
                            })
                    except:
                        continue
        except Exception as e:
            self.log(f"Error extracting experiences: {e}")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}")

        if len(experiences) == 0:
            self.log("⚠️ No experiences found - section might not be visible or selectors need updating")
        
        return experiences

    async def _extract_education_v2(self) -> List[Dict[str, Any]]:
        """Extract education"""
        educations = []

        try:
            # Try multiple selectors for education section
            edu_selectors = [
                'section:has(div#education)',
                'section[data-section="education"]',
                'section#education',
                'section.artdeco-card:has-text("Education")',
                'section:has-text("Education")',
            ]
            
            edu_section = None
            for selector in edu_selectors:
                try:
                    edu_section = await self.page.query_selector(selector)
                    if edu_section:
                        self.log(f"Found education section with selector: {selector}")
                        break
                except:
                    continue
            
            if edu_section:
                edu_items = await edu_section.query_selector_all('li')
                self.log(f"Found {len(edu_items)} education items")
                
                if len(edu_items) == 0:
                    edu_items = await edu_section.query_selector_all('div[class*="education"]')
                    self.log(f"Trying alternative selector, found {len(edu_items)} items")

                for item in edu_items:
                    try:
                        title_elem = await item.query_selector('div span[aria-hidden="true"]')
                        subtitle_elem = await item.query_selector('span.t-14 span[aria-hidden="true"]')

                        if title_elem:
                            title = await extract_text(title_elem)
                            subtitle = await extract_text(subtitle_elem) if subtitle_elem else ""

                            educations.append({
                                'title': title,
                                'subtitle': subtitle,
                                'companyId': "",
                                'companyUrn': "",
                                'companyLink1': "",
                                'logo': "",
                                'caption': "",
                                'breakdown': False,
                                'subComponents': []
                            })
                    except:
                        continue
        except Exception as e:
            self.log(f"Error extracting education: {e}")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}")

        if len(educations) == 0:
            self.log("⚠️ No education found - section might not be visible or selectors need updating")
        
        return educations

    async def _extract_skills_v2(self) -> Dict[str, Any]:
        """Extract skills"""
        skills_data = {
            'skills': [],
            'topSkillsByEndorsements': ""
        }

        try:
            # Try multiple selectors for skills section
            skills_selectors = [
                'section:has-text("Skills")',
                'section[data-section="skills"]',
                'section#skills',
                'section.artdeco-card:has-text("Skills")',
                'section:has(div#skills)',
            ]
            
            skills_section = None
            for selector in skills_selectors:
                try:
                    skills_section = await self.page.query_selector(selector)
                    if skills_section:
                        self.log(f"Found skills section with selector: {selector}")
                        break
                except:
                    continue
            
            if skills_section:
                skill_items = await skills_section.query_selector_all('li')
                self.log(f"Found {len(skill_items)} skill items")
                
                if len(skill_items) == 0:
                    skill_items = await skills_section.query_selector_all('span[class*="skill"]')
                    self.log(f"Trying alternative selector, found {len(skill_items)} items")

                skill_names = []
                for item in skill_items[:10]:  # Limit to top 10
                    try:
                        skill_elem = await item.query_selector('span[aria-hidden="true"]')
                        if skill_elem:
                            skill_name = await extract_text(skill_elem)
                            if skill_name:
                                skill_names.append(skill_name)
                                skills_data['skills'].append({
                                    'title': skill_name,
                                    'subComponents': [{'description': []}]
                                })
                    except:
                        continue

                skills_data['topSkillsByEndorsements'] = ', '.join(skill_names[:5])
        except Exception as e:
            self.log(f"Error extracting skills: {e}")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}")

        if len(skills_data['skills']) == 0:
            self.log("⚠️ No skills found - section might not be visible or selectors need updating")
        
        return skills_data

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            self.log("Browser closed")
