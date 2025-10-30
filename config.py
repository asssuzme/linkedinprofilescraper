import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    """Configuration management for LinkedIn Profile Scraper"""

    # LinkedIn Authentication
    LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
    LINKEDIN_COOKIES = os.getenv('LINKEDIN_COOKIES')

    # Scraping Configuration
    MAX_PROFILES = int(os.getenv('MAX_PROFILES', 100))
    DELAY_BETWEEN_PROFILES = int(os.getenv('DELAY_BETWEEN_PROFILES', 5))
    HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'

    # Proxy Configuration
    PROXY_SERVER = os.getenv('PROXY_SERVER')
    PROXY_USERNAME = os.getenv('PROXY_USERNAME')
    PROXY_PASSWORD = os.getenv('PROXY_PASSWORD')

    # Output Configuration
    OUTPUT_DIR = Path('output')
    COOKIES_FILE = Path('cookies.json')

    @classmethod
    def get_proxy_config(cls):
        """Get proxy configuration if available"""
        if cls.PROXY_SERVER:
            config = {'server': cls.PROXY_SERVER}
            if cls.PROXY_USERNAME and cls.PROXY_PASSWORD:
                config['username'] = cls.PROXY_USERNAME
                config['password'] = cls.PROXY_PASSWORD
            return config
        return None

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.LINKEDIN_COOKIES and not (cls.LINKEDIN_EMAIL and cls.LINKEDIN_PASSWORD):
            raise ValueError("Either LINKEDIN_COOKIES or LINKEDIN_EMAIL/PASSWORD must be set")

        # Create output directory
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
