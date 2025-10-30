# LinkedIn Profile Scraper

A comprehensive LinkedIn profile scraper built with Python and Playwright. Extract detailed profile information including work experience, education, skills, recommendations, and more.

## Features

- **Comprehensive Data Extraction**
  - Basic profile info (name, headline, location, connections, followers)
  - Profile pictures (multiple resolutions)
  - Contact information (email, phone)
  - Work experience with full job history
  - Education history
  - Skills with endorsements
  - Licenses and certifications
  - Languages
  - Recommendations (received and given)
  - Interests (companies, groups, schools, newsletters)
  - Projects, publications, patents, courses

- **Authentication**
  - Login with email/password
  - Cookie-based authentication
  - Automatic cookie persistence

- **Anti-Detection**
  - Realistic browser fingerprinting
  - Random delays between requests
  - User-agent rotation
  - Proxy support

- **Batch Processing**
  - Scrape multiple profiles from JSON input
  - Configurable rate limiting
  - Progress saving after each profile
  - Error handling and retry logic

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd linkedinprofilescraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

4. Set up configuration:
```bash
cp .env.example .env
```

5. Edit `.env` and add your LinkedIn credentials:
```env
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
HEADLESS=true
DELAY_BETWEEN_PROFILES=5
MAX_PROFILES=100
```

## Usage

### Basic Usage

Scrape a single profile:
```bash
python main.py -u "https://www.linkedin.com/in/johndoe"
```

Scrape multiple profiles from a JSON file:
```bash
python main.py -i input.json
```

Scrape with custom output file:
```bash
python main.py -i input.json -o output/results.json
```

### Input File Format

Create an `input.json` file with the following format:

```json
[
  {
    "url": "https://www.linkedin.com/in/profile1"
  },
  {
    "url": "https://www.linkedin.com/in/profile2"
  }
]
```

Or simply an array of URLs:
```json
[
  "https://www.linkedin.com/in/profile1",
  "https://www.linkedin.com/in/profile2"
]
```

### Command Line Options

```
usage: main.py [-h] [-i INPUT] [-u URLS [URLS ...]] [-o OUTPUT] [--headless]

LinkedIn Profile Scraper - Extract comprehensive data from LinkedIn profiles

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input JSON file containing profile URLs
  -u URLS [URLS ...], --urls URLS [URLS ...]
                        One or more LinkedIn profile URLs to scrape
  -o OUTPUT, --output OUTPUT
                        Output JSON file path (default: output/profiles_TIMESTAMP.json)
  --headless            Run in headless mode (default: from .env)
```

## Output Format

The scraper outputs comprehensive profile data in JSON format:

```json
[
  {
    "linkedinUrl": "https://www.linkedin.com/in/johndoe",
    "firstName": "John",
    "lastName": "Doe",
    "fullName": "John Doe",
    "headline": "Software Engineer at Tech Company",
    "connections": 500,
    "followers": 750,
    "email": "john@example.com",
    "mobileNumber": "+1-234-567-8900",
    "jobTitle": "Senior Software Engineer",
    "companyName": "Tech Company",
    "companyIndustry": "Information Technology",
    "companyWebsite": "techcompany.com",
    "currentJobDuration": "2 yrs 3 mos",
    "currentJobDurationInYrs": 2.25,
    "topSkillsByEndorsements": "Python, JavaScript, React, Node.js, AWS",
    "addressWithCountry": "San Francisco, California, United States",
    "profilePic": "https://media.licdn.com/...",
    "profilePicHighQuality": "https://media.licdn.com/...",
    "about": "Passionate software engineer...",
    "experiences": [...],
    "educations": [...],
    "skills": [...],
    "licenseAndCertificates": [...],
    "languages": [...],
    "recommendations": [...],
    "interests": [...]
  }
]
```

## Configuration

### Environment Variables

- `LINKEDIN_EMAIL` - Your LinkedIn email (required if not using cookies)
- `LINKEDIN_PASSWORD` - Your LinkedIn password (required if not using cookies)
- `LINKEDIN_COOKIES` - Path to cookies file (optional, alternative to email/password)
- `MAX_PROFILES` - Maximum number of profiles to scrape (default: 100)
- `DELAY_BETWEEN_PROFILES` - Seconds to wait between profiles (default: 5)
- `HEADLESS` - Run browser in headless mode (default: true)
- `PROXY_SERVER` - Proxy server URL (optional)
- `PROXY_USERNAME` - Proxy username (optional)
- `PROXY_PASSWORD` - Proxy password (optional)

### Rate Limiting

To avoid detection and rate limiting:

1. Use reasonable delays between requests (5-10 seconds)
2. Don't scrape too many profiles in a short time
3. Use proxies for large-scale scraping
4. Rotate accounts if scraping many profiles

## Best Practices

1. **Authentication**
   - Use cookie-based authentication for better reliability
   - Keep your cookies file secure
   - Refresh cookies periodically

2. **Rate Limiting**
   - Set `DELAY_BETWEEN_PROFILES` to at least 5 seconds
   - Scrape during off-peak hours
   - Limit to 50-100 profiles per session

3. **Error Handling**
   - The scraper continues on errors
   - Check output for missing data
   - Retry failed profiles manually

4. **Privacy & Ethics**
   - Only scrape public profile data
   - Respect LinkedIn's Terms of Service
   - Don't use for spam or harassment
   - Consider rate limits and privacy

## Troubleshooting

### Login Issues

If you encounter login issues:

1. Check your credentials in `.env`
2. LinkedIn may require CAPTCHA verification
3. Try running in non-headless mode: `HEADLESS=false`
4. Use cookie-based authentication instead

### Extraction Issues

If some data is missing:

1. LinkedIn's layout may have changed
2. Some profiles have privacy settings that hide information
3. Check the console output for errors
4. Run in non-headless mode to debug visually

### Rate Limiting

If you're getting rate limited:

1. Increase `DELAY_BETWEEN_PROFILES`
2. Use proxies
3. Scrape fewer profiles per session
4. Wait a few hours before retrying

## Architecture

```
linkedinprofilescraper/
├── config.py              # Configuration management
├── parsers.py            # Utility functions for parsing
├── scraper.py            # Main scraper class
├── main.py               # Entry point
├── requirements.txt      # Python dependencies
├── .env                  # Configuration (not in git)
├── .env.example          # Example configuration
├── example_input.json    # Example input file
└── output/              # Output directory (auto-created)
```

## Development

### Adding New Fields

To extract additional fields:

1. Add extraction method in `scraper.py`
2. Add parsing utilities in `parsers.py` if needed
3. Update the output format in `README.md`

### Testing

Test with a single profile first:
```bash
python main.py -u "https://www.linkedin.com/in/yourprofile" --headless=false
```

## Legal & Ethical Considerations

⚠️ **Important**: This tool is for educational and research purposes only.

- LinkedIn's Terms of Service prohibit automated scraping
- Use responsibly and ethically
- Respect privacy and data protection laws (GDPR, CCPA, etc.)
- Only scrape public information
- Don't use scraped data for spam or harassment
- Consider using LinkedIn's official API for commercial use

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Changelog

### v1.0.0 (2025)
- Initial release
- Comprehensive profile data extraction
- Cookie and credential-based authentication
- Batch processing support
- Anti-detection features
- Proxy support

## Acknowledgments

Built with:
- [Playwright](https://playwright.dev/) - Browser automation
- [Python](https://www.python.org/) - Programming language
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing

## Disclaimer

This tool is provided as-is without any guarantees. The authors are not responsible for any misuse or violation of LinkedIn's Terms of Service. Use at your own risk.
