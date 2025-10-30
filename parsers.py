"""
Utility functions for parsing LinkedIn profile data
"""
import re
from typing import Any, Dict, List, Optional


def extract_text(element) -> str:
    """Safely extract text from an element"""
    if element is None:
        return ""
    try:
        return element.text_content().strip()
    except:
        return ""


def extract_attribute(element, attr: str) -> str:
    """Safely extract attribute from an element"""
    if element is None:
        return ""
    try:
        return element.get_attribute(attr) or ""
    except:
        return ""


def parse_duration_to_years(duration: str) -> float:
    """Convert duration string like '1 yr 2 mos' to years"""
    if not duration:
        return 0.0

    years = 0.0
    months = 0.0

    year_match = re.search(r'(\d+)\s*yr', duration)
    if year_match:
        years = float(year_match.group(1))

    month_match = re.search(r'(\d+)\s*mo', duration)
    if month_match:
        months = float(month_match.group(1))

    return round(years + (months / 12), 2)


def clean_company_size(size_text: str) -> str:
    """Extract and clean company size"""
    if not size_text:
        return ""

    # Match patterns like "501-1000 employees"
    match = re.search(r'([\d,]+-[\d,]+|\d+\+?)', size_text)
    if match:
        return match.group(1).replace(',', '')
    return size_text.strip()


def parse_connections_count(text: str) -> int:
    """Parse connection count from text like '10,219 connections'"""
    if not text:
        return 0

    # Remove commas and extract number
    match = re.search(r'([\d,]+)', text.replace(',', ''))
    if match:
        try:
            return int(match.group(1))
        except:
            return 0
    return 0


def extract_linkedin_urn(element) -> str:
    """Extract LinkedIn URN from element data attributes"""
    if element is None:
        return ""

    try:
        # Try different data attributes that might contain URN
        for attr in ['data-entity-urn', 'data-control-name', 'href']:
            value = element.get_attribute(attr)
            if value and 'urn:li:' in value:
                urn_match = re.search(r'(urn:li:[^&\s"]+)', value)
                if urn_match:
                    return urn_match.group(1)
    except:
        pass
    return ""


def extract_company_id(link: str) -> str:
    """Extract company ID from LinkedIn company URL"""
    if not link:
        return ""

    match = re.search(r'/company/(\d+)', link)
    if match:
        return match.group(1)
    return ""


def parse_year_from_text(text: str) -> Optional[int]:
    """Extract year from text"""
    if not text:
        return None

    match = re.search(r'\b(19|20)\d{2}\b', text)
    if match:
        try:
            return int(match.group(0))
        except:
            return None
    return None


def clean_url(url: str) -> str:
    """Clean and standardize URL"""
    if not url:
        return ""

    # Remove tracking parameters
    url = re.sub(r'[?&].*$', '', url)
    return url.strip()


def extract_image_urls(element, selector: str) -> List[Dict[str, Any]]:
    """Extract image URLs with dimensions"""
    images = []
    if element is None:
        return images

    try:
        img_elements = element.query_selector_all(selector)
        for img in img_elements:
            src = extract_attribute(img, 'src')
            if src:
                images.append({
                    'url': src,
                    'width': extract_attribute(img, 'width') or 'auto',
                    'height': extract_attribute(img, 'height') or 'auto'
                })
    except:
        pass

    return images


def normalize_linkedin_url(url: str) -> str:
    """Normalize LinkedIn profile URL"""
    if not url:
        return ""

    # Remove locale and tracking parameters
    url = re.sub(r'/[a-z]{2}_[A-Z]{2}/', '/', url)
    url = re.sub(r'[?&].*$', '', url)

    # Ensure https
    if url.startswith('http://'):
        url = url.replace('http://', 'https://')
    elif not url.startswith('https://'):
        url = 'https://' + url

    return url.rstrip('/')


def extract_email_from_text(text: str) -> Optional[str]:
    """Extract email address from text"""
    if not text:
        return None

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    if match:
        return match.group(0)
    return None


def extract_phone_from_text(text: str) -> Optional[str]:
    """Extract phone number from text"""
    if not text:
        return None

    # Match various phone formats
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    match = re.search(phone_pattern, text)
    if match:
        return match.group(0)
    return None


def split_name(full_name: str) -> tuple:
    """Split full name into first and last name"""
    if not full_name:
        return "", ""

    parts = full_name.strip().split()
    if len(parts) == 0:
        return "", ""
    elif len(parts) == 1:
        return parts[0], ""
    else:
        return parts[0], ' '.join(parts[1:])
