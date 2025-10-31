"""
LinkedIn Profile Scraper
Extracts comprehensive profile data from LinkedIn profiles
"""
import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import time

from config import Config
from parsers import (
    extract_text, extract_attribute, parse_duration_to_years,
    clean_company_size, parse_connections_count, extract_linkedin_urn,
    extract_company_id, parse_year_from_text, clean_url,
    normalize_linkedin_url, extract_email_from_text, extract_phone_from_text,
    split_name
)


class LinkedInScraper:
    """Main scraper class for LinkedIn profiles"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def initialize(self):
        """Initialize the browser and context"""
        playwright = await async_playwright().start()

        launch_options = {
            'headless': self.headless,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        }

        # Add proxy if configured
        proxy_config = Config.get_proxy_config()
        if proxy_config:
            launch_options['proxy'] = proxy_config

        self.browser = await playwright.chromium.launch(**launch_options)

        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )

        # Set extra headers
        await self.context.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
        })

        self.page = await self.context.new_page()

        # Anti-detection: remove webdriver property
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    async def login_with_credentials(self, email: str, password: str):
        """Login to LinkedIn using email and password"""
        print("Logging in to LinkedIn...")

        await self.page.goto('https://www.linkedin.com/login', wait_until='networkidle')
        await asyncio.sleep(2)

        # Fill in credentials
        await self.page.fill('input[id="username"]', email)
        await asyncio.sleep(0.5)
        await self.page.fill('input[id="password"]', password)
        await asyncio.sleep(0.5)

        # Click sign in
        await self.page.click('button[type="submit"]')
        await asyncio.sleep(3)

        # Wait for navigation
        try:
            await self.page.wait_for_url('https://www.linkedin.com/feed/*', timeout=10000)
            print("✓ Successfully logged in")
        except:
            # Check if we're already on the feed or another LinkedIn page
            if 'linkedin.com' in self.page.url and 'login' not in self.page.url:
                print("✓ Successfully logged in")
            else:
                print("⚠ Login may have failed or requires verification")

        # Save cookies for future use
        await self.save_cookies()

    async def login_with_cookies(self, cookies_path: str):
        """Login using saved cookies"""
        print("Loading cookies for authentication...")

        cookies_file = Path(cookies_path)
        if not cookies_file.exists():
            raise FileNotFoundError(f"Cookies file not found: {cookies_path}")

        with open(cookies_file, 'r') as f:
            raw_cookies = json.load(f)

        # Normalize cookies for both domains to reduce redirect loops
        cookies = []
        for c in raw_cookies:
            cookies.append(c)
            domain = (c.get('domain') or '').lower()
            if domain == '.linkedin.com':
                dup = dict(c)
                dup['domain'] = '.www.linkedin.com'
                cookies.append(dup)
            elif domain == '.www.linkedin.com':
                dup = dict(c)
                dup['domain'] = '.linkedin.com'
                cookies.append(dup)

        await self.context.add_cookies(cookies)

        # Do not navigate to /feed here (can cause redirect loops). We'll verify lazily.
        print("✓ Cookies loaded")

    async def save_cookies(self):
        """Save current cookies to file"""
        cookies = await self.context.cookies()
        with open(Config.COOKIES_FILE, 'w') as f:
            json.dump(cookies, f, indent=2)
        print(f"✓ Cookies saved to {Config.COOKIES_FILE}")

    async def scrape_profile(self, profile_url: str) -> Dict[str, Any]:
        """Scrape a single LinkedIn profile"""
        print(f"\nScraping profile: {profile_url}")

        profile_url = normalize_linkedin_url(profile_url)

        # Navigate to profile
        await self.page.goto(profile_url, wait_until='networkidle')
        await asyncio.sleep(3)

        # Scroll to load all content
        await self._scroll_page()

        # Extract all profile data
        profile_data = {
            'linkedinUrl': profile_url,
        }

        # Basic info
        profile_data.update(await self._extract_basic_info())

        # Profile pictures
        profile_data.update(await self._extract_profile_pictures())

        # Current job info
        profile_data.update(await self._extract_current_job_info())

        # About section
        profile_data['about'] = await self._extract_about()

        # Contact info
        contact_info = await self._extract_contact_info()
        profile_data.update(contact_info)

        # Experiences
        profile_data['experiences'] = await self._extract_experiences()

        # Skills
        profile_data.update(await self._extract_skills())

        # Education
        profile_data['educations'] = await self._extract_education()

        # Licenses and Certificates
        profile_data['licenseAndCertificates'] = await self._extract_licenses_certificates()

        # Languages
        profile_data['languages'] = await self._extract_languages()

        # Honors and Awards
        profile_data['honorsAndAwards'] = await self._extract_honors_awards()

        # Volunteer and Awards
        profile_data['volunteerAndAwards'] = await self._extract_volunteer()

        # Projects, Publications, Patents, Courses, etc.
        profile_data['projects'] = await self._extract_projects()
        profile_data['publications'] = await self._extract_publications()
        profile_data['patents'] = await self._extract_patents()
        profile_data['courses'] = await self._extract_courses()
        profile_data['testScores'] = []
        profile_data['organizations'] = []
        profile_data['volunteerCauses'] = []
        profile_data['verifications'] = []
        profile_data['promos'] = []
        profile_data['highlights'] = []

        # Interests
        profile_data['interests'] = await self._extract_interests()

        # Recommendations
        profile_data['recommendations'] = await self._extract_recommendations()

        # Updates (activity)
        profile_data['updates'] = []

        print(f"✓ Successfully scraped profile: {profile_data.get('fullName', 'Unknown')}")

        return profile_data

    async def _scroll_page(self):
        """Scroll the page to load all dynamic content"""
        for _ in range(5):
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1)
        await self.page.evaluate('window.scrollTo(0, 0)')
        await asyncio.sleep(1)

    async def _extract_basic_info(self) -> Dict[str, Any]:
        """Extract basic profile information"""
        data = {}

        try:
            # Full name
            name_elem = await self.page.query_selector('h1.text-heading-xlarge')
            full_name = extract_text(name_elem)
            data['fullName'] = full_name

            first_name, last_name = split_name(full_name)
            data['firstName'] = first_name
            data['lastName'] = last_name

            # Headline
            headline_elem = await self.page.query_selector('div.text-body-medium.break-words')
            data['headline'] = extract_text(headline_elem)

            # Location
            location_elem = await self.page.query_selector('span.text-body-small.inline.t-black--light.break-words')
            location = extract_text(location_elem)
            data['addressWithCountry'] = location

            # Parse location
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

            # Connections and Followers (avoid hard timeouts on inner_text)
            try:
                connections_elem = await self.page.query_selector('li.text-body-small:has-text("connection")')
                connections_text = extract_text(connections_elem)
                data['connections'] = parse_connections_count(connections_text) if connections_text else 0
            except:
                data['connections'] = 0

            try:
                followers_elem = await self.page.query_selector('li.text-body-small:has-text("follower")')
                followers_text = extract_text(followers_elem)
                data['followers'] = parse_connections_count(followers_text) if followers_text else 0
            except:
                data['followers'] = 0

            # Public identifier and URN
            url_match = re.search(r'/in/([^/]+)', self.page.url)
            data['publicIdentifier'] = url_match.group(1) if url_match else ""

            # Try to extract URN
            try:
                profile_card = await self.page.query_selector('[data-member-id]')
                if profile_card:
                    member_id = extract_attribute(profile_card, 'data-member-id')
                    if member_id:
                        data['urn'] = f"ACoAAA{member_id}"
                    else:
                        data['urn'] = ""
                else:
                    data['urn'] = ""
            except:
                data['urn'] = ""

            # Connection status
            data['openConnection'] = False
            try:
                connect_button = await self.page.query_selector('button:has-text("Connect")')
                data['openConnection'] = connect_button is not None
            except:
                pass

        except Exception as e:
            print(f"Error extracting basic info: {e}")

        return data

    async def _extract_profile_pictures(self) -> Dict[str, Any]:
        """Extract profile picture URLs"""
        data = {
            'profilePic': "",
            'profilePicHighQuality': "",
            'profilePicAllDimensions': []
        }

        try:
            # Find profile image
            img_elem = await self.page.query_selector('img.pv-top-card-profile-picture__image')
            if img_elem:
                src = extract_attribute(img_elem, 'src')

                if src and 'profile-displayphoto' in src:
                    # Generate different sizes
                    base_url = re.sub(r'shrink_\d+_\d+', 'shrink_{}_{}', src)

                    sizes = [(200, 200), (800, 800), (400, 400), (100, 100)]
                    dimensions = []

                    for width, height in sizes:
                        url = base_url.format(width, height)
                        dimensions.append({
                            'width': width,
                            'height': height,
                            'url': url
                        })

                    data['profilePic'] = dimensions[0]['url'] if dimensions else src
                    data['profilePicHighQuality'] = dimensions[1]['url'] if len(dimensions) > 1 else src
                    data['profilePicAllDimensions'] = dimensions

        except Exception as e:
            print(f"Error extracting profile pictures: {e}")

        return data

    async def _extract_about(self) -> str:
        """Extract the About section"""
        try:
            # Click "Show more" if present
            try:
                show_more = await self.page.query_selector('button#line-clamp-show-more-button')
                if show_more:
                    await show_more.click()
                    await asyncio.sleep(0.5)
            except:
                pass

            about_section = await self.page.query_selector('section.artdeco-card:has(div#about)')
            if about_section:
                about_text_elem = await about_section.query_selector('div.display-flex.ph5.pv3 span[aria-hidden="true"]')
                return extract_text(about_text_elem)
        except Exception as e:
            print(f"Error extracting about: {e}")

        return ""

    async def _extract_contact_info(self) -> Dict[str, Optional[str]]:
        """Extract contact information"""
        data = {
            'email': None,
            'mobileNumber': None
        }

        try:
            # Click on "Contact info" button
            contact_button = await self.page.query_selector('a[href*="overlay/contact-info"]')
            if contact_button:
                await contact_button.click()
                await asyncio.sleep(2)

                # Extract email
                email_section = await self.page.query_selector('section.pv-contact-info__contact-type.ci-email')
                if email_section:
                    email_text = extract_text(email_section)
                    data['email'] = extract_email_from_text(email_text)

                # Extract phone
                phone_section = await self.page.query_selector('section.pv-contact-info__contact-type.ci-phone')
                if phone_section:
                    phone_text = extract_text(phone_section)
                    data['mobileNumber'] = extract_phone_from_text(phone_text)

                # Close modal
                close_button = await self.page.query_selector('button[data-test-modal-close-btn]')
                if close_button:
                    await close_button.click()
                    await asyncio.sleep(0.5)

        except Exception as e:
            print(f"Error extracting contact info: {e}")

        return data

    async def _extract_current_job_info(self) -> Dict[str, Any]:
        """Extract current job information"""
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
            # Find the first experience (current job)
            experience_section = await self.page.query_selector('section.artdeco-card:has(div#experience)')
            if experience_section:
                first_experience = await experience_section.query_selector('li.artdeco-list__item')
                if first_experience:
                    # Job title
                    title_elem = await first_experience.query_selector('div.display-flex.flex-column.full-width span[aria-hidden="true"]')
                    data['jobTitle'] = extract_text(title_elem)

                    # Company name
                    company_elem = await first_experience.query_selector('span.t-14.t-normal span[aria-hidden="true"]')
                    company_text = extract_text(company_elem)
                    if ' · ' in company_text:
                        data['companyName'] = company_text.split(' · ')[0].strip()
                    else:
                        data['companyName'] = company_text

                    # Duration
                    duration_elem = await first_experience.query_selector('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')
                    duration = extract_text(duration_elem)
                    if duration:
                        # Extract just the duration part
                        duration_parts = duration.split(' · ')
                        if len(duration_parts) > 0:
                            data['currentJobDuration'] = duration_parts[0].strip()
                            data['currentJobDurationInYrs'] = parse_duration_to_years(data['currentJobDuration'])

                    # Try to get company details by clicking on company link
                    company_link = await first_experience.query_selector('a[href*="/company/"]')
                    if company_link:
                        company_url = extract_attribute(company_link, 'href')
                        data['companyLinkedin'] = clean_url(company_url).replace('https://www.linkedin.com/', '').replace('/company/', 'linkedin.com/company/')

        except Exception as e:
            print(f"Error extracting current job info: {e}")

        return data

    async def _extract_skills(self) -> Dict[str, Any]:
        """Extract skills section"""
        skills_data = {
            'skills': [],
            'topSkillsByEndorsements': ""
        }

        try:
            # Navigate to skills page
            public_id = re.search(r'/in/([^/]+)', self.page.url)
            if public_id:
                skills_url = f"https://www.linkedin.com/in/{public_id.group(1)}/details/skills/"
                await self.page.goto(skills_url, wait_until='networkidle')
                await asyncio.sleep(2)

                # Extract skills
                skill_items = await self.page.query_selector_all('li.artdeco-list__item')

                top_skills = []
                all_skills = []

                for item in skill_items:
                    try:
                        # Skill title
                        title_elem = await item.query_selector('div.display-flex.align-items-center span[aria-hidden="true"]')
                        title = extract_text(title_elem)

                        if not title:
                            continue

                        # Get endorsements and insights
                        insights = await item.query_selector_all('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')

                        description = []
                        endorsement_count = 0

                        for insight in insights:
                            text = extract_text(insight)
                            if text:
                                # Check for endorsement count
                                endorsement_match = re.search(r'(\d+)\s+endorsement', text)
                                if endorsement_match:
                                    endorsement_count = int(endorsement_match.group(1))

                                description.append({
                                    'type': 'insightComponent',
                                    'text': text
                                })

                        skill_obj = {
                            'title': title,
                            'subComponents': [{
                                'description': description
                            }]
                        }

                        all_skills.append(skill_obj)

                        if endorsement_count > 0:
                            top_skills.append((title, endorsement_count))

                    except Exception as e:
                        print(f"Error parsing skill item: {e}")
                        continue

                skills_data['skills'] = all_skills

                # Sort top skills by endorsements and take top 5
                top_skills.sort(key=lambda x: x[1], reverse=True)
                top_skill_names = [skill[0] for skill in top_skills[:5]]
                skills_data['topSkillsByEndorsements'] = ', '.join(top_skill_names)

                # Navigate back to main profile
                await self.page.go_back()
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Error extracting skills: {e}")

        return skills_data

    async def _extract_experiences(self) -> List[Dict[str, Any]]:
        """Extract work experience"""
        experiences = []

        try:
            # Navigate to experience details page
            public_id = re.search(r'/in/([^/]+)', self.page.url)
            if public_id:
                experience_url = f"https://www.linkedin.com/in/{public_id.group(1)}/details/experience/"
                await self.page.goto(experience_url, wait_until='networkidle')
                await asyncio.sleep(2)

                # Find all experience items
                exp_items = await self.page.query_selector_all('li.artdeco-list__item')

                current_company = None

                for item in exp_items:
                    try:
                        # Check if this is a company header or a role
                        is_company_header = await item.query_selector('div.display-flex.flex-column.full-width.align-items-start')

                        if is_company_header:
                            # This is a company with multiple roles
                            company_name_elem = await item.query_selector('span.mr1.t-bold span[aria-hidden="true"]')
                            company_name = extract_text(company_name_elem)

                            # Company logo
                            logo_elem = await item.query_selector('img')
                            logo = extract_attribute(logo_elem, 'src') if logo_elem else ""

                            # Company link
                            company_link_elem = await item.query_selector('a[href*="/company/"]')
                            company_link = extract_attribute(company_link_elem, 'href') if company_link_elem else ""
                            company_id = extract_company_id(company_link)

                            # Duration and location
                            subtitle_elem = await item.query_selector('span.t-14.t-normal span[aria-hidden="true"]')
                            subtitle = extract_text(subtitle_elem)

                            caption_elem = await item.query_selector('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')
                            caption = extract_text(caption_elem)

                            current_company = {
                                'companyId': company_id,
                                'companyUrn': f"urn:li:fsd_company:{company_id}" if company_id else "",
                                'companyLink1': clean_url(company_link),
                                'logo': logo,
                                'title': company_name,
                                'subtitle': subtitle,
                                'caption': caption,
                                'breakdown': True,
                                'subComponents': []
                            }

                        else:
                            # This is either a sub-role or a standalone role
                            title_elem = await item.query_selector('div.display-flex.flex-column.full-width span[aria-hidden="true"]')
                            title = extract_text(title_elem)

                            # Get caption (duration)
                            caption_elem = await item.query_selector('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')
                            caption = extract_text(caption_elem)

                            # Get metadata (location/type)
                            metadata_elems = await item.query_selector_all('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')
                            metadata = extract_text(metadata_elems[1]) if len(metadata_elems) > 1 else ""

                            # Description
                            desc_elem = await item.query_selector('div.display-flex.full-width span[aria-hidden="true"]')
                            description_text = extract_text(desc_elem)
                            description = [{
                                'type': 'textComponent',
                                'text': description_text
                            }] if description_text else []

                            role_data = {
                                'title': title,
                                'caption': caption,
                                'metadata': metadata,
                                'description': description
                            }

                            if current_company:
                                # Add as sub-component to current company
                                current_company['subComponents'].append(role_data)
                            else:
                                # Standalone experience
                                company_name_elem = await item.query_selector('span.t-14.t-normal span[aria-hidden="true"]')
                                company_name = extract_text(company_name_elem)

                                logo_elem = await item.query_selector('img')
                                logo = extract_attribute(logo_elem, 'src') if logo_elem else ""

                                company_link_elem = await item.query_selector('a[href*="/company/"]')
                                company_link = extract_attribute(company_link_elem, 'href') if company_link_elem else ""
                                company_id = extract_company_id(company_link)

                                experiences.append({
                                    'companyId': company_id,
                                    'companyUrn': f"urn:li:fsd_company:{company_id}" if company_id else "",
                                    'companyLink1': clean_url(company_link),
                                    'logo': logo,
                                    'title': company_name,
                                    'subtitle': "",
                                    'caption': caption,
                                    'breakdown': False,
                                    'subComponents': [{
                                        'title': title,
                                        'caption': caption,
                                        'metadata': metadata,
                                        'description': description
                                    }]
                                })

                    except Exception as e:
                        print(f"Error parsing experience item: {e}")
                        continue

                    # Check if we should add the current company
                    # (we do this when we encounter a new company or at the end)
                    next_item_index = exp_items.index(item) + 1
                    if next_item_index >= len(exp_items) or await exp_items[next_item_index].query_selector('div.display-flex.flex-column.full-width.align-items-start'):
                        if current_company:
                            experiences.append(current_company)
                            current_company = None

                # Add last company if exists
                if current_company:
                    experiences.append(current_company)

                # Navigate back
                await self.page.go_back()
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Error extracting experiences: {e}")

        return experiences

    async def _extract_education(self) -> List[Dict[str, Any]]:
        """Extract education information"""
        educations = []

        try:
            education_section = await self.page.query_selector('section.artdeco-card:has(div#education)')
            if education_section:
                edu_items = await education_section.query_selector_all('li.artdeco-list__item')

                for item in edu_items:
                    try:
                        # School name
                        title_elem = await item.query_selector('div.display-flex.align-items-center span[aria-hidden="true"]')
                        title = extract_text(title_elem)

                        # Degree
                        subtitle_elem = await item.query_selector('span.t-14.t-normal span[aria-hidden="true"]')
                        subtitle = extract_text(subtitle_elem)

                        # Duration
                        caption_elem = await item.query_selector('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')
                        caption = extract_text(caption_elem)

                        # Logo
                        logo_elem = await item.query_selector('img')
                        logo = extract_attribute(logo_elem, 'src') if logo_elem else ""

                        # School link
                        link_elem = await item.query_selector('a[href*="/school/"]')
                        if link_elem:
                            link = extract_attribute(link_elem, 'href')
                            company_link = clean_url(link)
                            school_id = extract_company_id(link)
                        else:
                            # Try to construct search link
                            company_link = f"https://www.linkedin.com/search/results/all/?keywords={title.replace(' ', '+')}"
                            school_id = ""

                        # Additional details (e.g., grade)
                        details = []
                        detail_elems = await item.query_selector_all('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')
                        for i, detail_elem in enumerate(detail_elems):
                            if i > 0:  # Skip the first one (duration)
                                detail_text = extract_text(detail_elem)
                                if detail_text:
                                    details.append({
                                        'type': 'insightComponent',
                                        'text': detail_text
                                    })

                        educations.append({
                            'companyId': school_id,
                            'companyUrn': f"urn:li:fsd_company:{school_id}" if school_id else "",
                            'companyLink1': company_link,
                            'logo': logo,
                            'title': title,
                            'subtitle': subtitle,
                            'caption': caption,
                            'breakdown': False,
                            'subComponents': [{
                                'description': details
                            }]
                        })

                    except Exception as e:
                        print(f"Error parsing education item: {e}")
                        continue

        except Exception as e:
            print(f"Error extracting education: {e}")

        return educations

    async def _extract_licenses_certificates(self) -> List[Dict[str, Any]]:
        """Extract licenses and certifications"""
        licenses = []

        try:
            # Navigate to licenses page
            public_id = re.search(r'/in/([^/]+)', self.page.url)
            if public_id:
                licenses_url = f"https://www.linkedin.com/in/{public_id.group(1)}/details/certifications/"
                await self.page.goto(licenses_url, wait_until='networkidle')
                await asyncio.sleep(2)

                license_items = await self.page.query_selector_all('li.artdeco-list__item')

                for item in license_items:
                    try:
                        # Certificate name
                        title_elem = await item.query_selector('div.display-flex.align-items-center span[aria-hidden="true"]')
                        title = extract_text(title_elem)

                        # Issuing organization
                        subtitle_elem = await item.query_selector('span.t-14.t-normal span[aria-hidden="true"]')
                        subtitle = extract_text(subtitle_elem)

                        # Issue date
                        caption_elem = await item.query_selector('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')
                        caption = extract_text(caption_elem)

                        # Logo
                        logo_elem = await item.query_selector('img')
                        logo = extract_attribute(logo_elem, 'src') if logo_elem else ""

                        # Organization link
                        link_elem = await item.query_selector('a[href*="/company/"]')
                        if link_elem:
                            link = extract_attribute(link_elem, 'href')
                            company_link = clean_url(link)
                            org_id = extract_company_id(link)
                        else:
                            company_link = ""
                            org_id = ""

                        licenses.append({
                            'companyId': org_id,
                            'companyUrn': f"urn:li:fsd_company:{org_id}" if org_id else "",
                            'companyLink1': company_link,
                            'logo': logo,
                            'title': title,
                            'subtitle': subtitle,
                            'caption': caption,
                            'breakdown': False,
                            'subComponents': [{
                                'description': []
                            }]
                        })

                    except Exception as e:
                        print(f"Error parsing license item: {e}")
                        continue

                # Navigate back
                await self.page.go_back()
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Error extracting licenses: {e}")

        return licenses

    async def _extract_languages(self) -> List[Dict[str, Any]]:
        """Extract languages"""
        languages = []

        try:
            language_section = await self.page.query_selector('section.artdeco-card:has-text("Languages")')
            if language_section:
                lang_items = await language_section.query_selector_all('li.artdeco-list__item')

                for item in lang_items:
                    try:
                        title_elem = await item.query_selector('div.display-flex.align-items-center span[aria-hidden="true"]')
                        title = extract_text(title_elem)

                        caption_elem = await item.query_selector('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')
                        caption = extract_text(caption_elem)

                        languages.append({
                            'title': title,
                            'caption': caption,
                            'breakdown': False,
                            'subComponents': [{
                                'description': []
                            }]
                        })

                    except Exception as e:
                        print(f"Error parsing language item: {e}")
                        continue

        except Exception as e:
            print(f"Error extracting languages: {e}")

        return languages

    async def _extract_honors_awards(self) -> List[Dict[str, Any]]:
        """Extract honors and awards"""
        # Placeholder - implement if needed
        return []

    async def _extract_volunteer(self) -> List[Dict[str, Any]]:
        """Extract volunteer experience"""
        # Placeholder - implement if needed
        return []

    async def _extract_projects(self) -> List[Dict[str, Any]]:
        """Extract projects"""
        # Placeholder - implement if needed
        return []

    async def _extract_publications(self) -> List[Dict[str, Any]]:
        """Extract publications"""
        # Placeholder - implement if needed
        return []

    async def _extract_patents(self) -> List[Dict[str, Any]]:
        """Extract patents"""
        # Placeholder - implement if needed
        return []

    async def _extract_courses(self) -> List[Dict[str, Any]]:
        """Extract courses"""
        # Placeholder - implement if needed
        return []

    async def _extract_interests(self) -> List[Dict[str, Any]]:
        """Extract interests (companies, groups, schools, etc.)"""
        interests = []

        try:
            # Navigate to interests page
            public_id = re.search(r'/in/([^/]+)', self.page.url)
            if public_id:
                # Try different interest sections
                sections = [
                    ('Companies', f"https://www.linkedin.com/in/{public_id.group(1)}/details/interests/companies/"),
                    ('Groups', f"https://www.linkedin.com/in/{public_id.group(1)}/details/interests/groups/"),
                    ('Schools', f"https://www.linkedin.com/in/{public_id.group(1)}/details/interests/schools/"),
                ]

                for section_name, url in sections:
                    try:
                        await self.page.goto(url, wait_until='networkidle')
                        await asyncio.sleep(2)

                        items = await self.page.query_selector_all('li.artdeco-list__item')

                        if items:
                            section_components = []

                            for item in items:
                                try:
                                    title_elem = await item.query_selector('span.mr1.hoverable-link-text.t-bold span[aria-hidden="true"]')
                                    title = extract_text(title_elem)

                                    caption_elem = await item.query_selector('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')
                                    caption = extract_text(caption_elem)

                                    subtitle_elem = await item.query_selector('span.t-14.t-normal span[aria-hidden="true"]')
                                    subtitle = extract_text(subtitle_elem) if subtitle_elem else ""

                                    link_elem = await item.query_selector('a')
                                    link = extract_attribute(link_elem, 'href') if link_elem else ""

                                    section_components.append({
                                        'titleV2': title,
                                        'caption': caption,
                                        'subtitle': subtitle,
                                        'size': 'LARGE',
                                        'textActionTarget': clean_url(link),
                                        'subComponents': []
                                    })

                                except Exception as e:
                                    print(f"Error parsing interest item: {e}")
                                    continue

                            if section_components:
                                interests.append({
                                    'section_name': section_name,
                                    'section_components': section_components
                                })

                    except Exception as e:
                        print(f"Error extracting {section_name}: {e}")
                        continue

                # Navigate back to main profile
                await self.page.goto(f"https://www.linkedin.com/in/{public_id.group(1)}/", wait_until='networkidle')
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Error extracting interests: {e}")

        return interests

    async def _extract_recommendations(self) -> List[Dict[str, Any]]:
        """Extract recommendations"""
        recommendations = []

        try:
            # Navigate to recommendations page
            public_id = re.search(r'/in/([^/]+)', self.page.url)
            if public_id:
                # Received recommendations
                received_url = f"https://www.linkedin.com/in/{public_id.group(1)}/details/recommendations/"
                await self.page.goto(received_url, wait_until='networkidle')
                await asyncio.sleep(2)

                received_items = await self.page.query_selector_all('li.artdeco-list__item')
                received_components = []

                for item in received_items:
                    try:
                        # Recommender name
                        name_elem = await item.query_selector('span.mr1.hoverable-link-text.t-bold span[aria-hidden="true"]')
                        name = extract_text(name_elem)

                        # Relationship and date
                        caption_elem = await item.query_selector('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')
                        caption = extract_text(caption_elem)

                        # Title
                        subtitle_elem = await item.query_selector('span.t-14.t-normal span[aria-hidden="true"]')
                        subtitle = extract_text(subtitle_elem)

                        # Profile link
                        link_elem = await item.query_selector('a[href*="/in/"]')
                        link = extract_attribute(link_elem, 'href') if link_elem else ""

                        # Profile picture
                        img_elem = await item.query_selector('img')
                        image = extract_attribute(img_elem, 'src') if img_elem else ""

                        # Recommendation text
                        text_elem = await item.query_selector('div.display-flex.full-width span[aria-hidden="true"]')
                        text = extract_text(text_elem)

                        received_components.append({
                            'titleV2': name,
                            'caption': caption,
                            'subtitle': subtitle,
                            'size': 'LARGE',
                            'textActionTarget': clean_url(link),
                            'image': image,
                            'subComponents': [{
                                'fixedListComponent': [{
                                    'type': 'textComponent',
                                    'text': text
                                }]
                            }]
                        })

                    except Exception as e:
                        print(f"Error parsing recommendation item: {e}")
                        continue

                if received_components:
                    recommendations.append({
                        'section_name': 'Received',
                        'section_components': received_components
                    })

                # Given recommendations (navigate to given page if exists)
                # This would require navigating to a different URL
                # For now, we'll skip this as it may not always be accessible

                # Navigate back
                await self.page.go_back()
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Error extracting recommendations: {e}")

        return recommendations

    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
            print("✓ Browser closed")
