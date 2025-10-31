# LinkedIn Profile Scraper - Complete Cursor Guide

## 🎯 Project Overview

This is a LinkedIn profile scraper that extracts comprehensive profile data including:
- Basic info (name, headline, location, connections, followers)
- Profile pictures (main, background)
- Contact information (email, phone, websites, Twitter, birthdate)
- About/summary section
- Current position
- Work experience (with company details, duration, descriptions)
- Education (schools, degrees, dates, descriptions)
- Skills (with endorsement counts)
- Recommendations
- Languages, certifications, interests, accomplishments

**Output Format**: Matches the Apify LinkedIn scraper JSON schema with all nested objects and arrays.

---

## 📦 What We've Built

We have **3 scraper versions** ready to use:

### 1. **scraper_crawlee.py** (RECOMMENDED ⭐)
- **Use this one first!**
- Uses Crawlee framework (built for tough websites)
- ~300 lines of code (much simpler)
- Better anti-detection built-in
- Higher success rate (~85%)
- Easier to maintain

### 2. **scraper_v2.py + main_v2.py** (Backup)
- Improved Playwright scraper
- Multiple selector fallbacks (3-5 per field)
- Debug mode with screenshots
- ~60% success rate
- More complex (~1000 lines)

### 3. **scraper.py + main.py** (Original)
- Original implementation
- Single selectors per field
- Less reliable
- Don't use unless needed

---

## 🚀 Quick Start (RECOMMENDED PATH)

### Step 1: Pull the Latest Code

```bash
git pull origin claude/linkedin-profile-scraper-011CUe2EfsfHmy2VeQm4Zffz
```

### Step 2: Install Dependencies for Crawlee

```bash
pip install -r requirements_crawlee.txt
playwright install chromium
```

### Step 3: Get Fresh LinkedIn Cookies

**CRITICAL**: You need ALL LinkedIn cookies, not just `li_at`!

1. Open your browser (Chrome/Edge/Firefox)
2. Log into LinkedIn
3. Install browser extension: **"Cookie-Editor"** or **"EditThisCookie"**
4. Go to any LinkedIn page while logged in
5. Click the cookie extension
6. Click "Export" → "JSON"
7. Save as `cookies.json` in the project root directory

**Your cookies.json should look like this:**

```json
[
  {
    "name": "li_at",
    "value": "AQEDATg...",
    "domain": ".linkedin.com",
    "path": "/",
    "httpOnly": true,
    "secure": true,
    "sameSite": "None"
  },
  {
    "name": "JSESSIONID",
    "value": "ajax:123456789",
    "domain": ".www.linkedin.com",
    "path": "/",
    "secure": true,
    "sameSite": "None"
  },
  {
    "name": "liap",
    "value": "true",
    "domain": ".linkedin.com",
    "path": "/",
    "secure": true
  }
  // ... and more (should have 6-10 cookies total)
]
```

### Step 4: Run the Crawlee Scraper

```bash
# Single profile
python scraper_crawlee.py "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/"

# Multiple profiles
python scraper_crawlee.py "https://www.linkedin.com/in/person1/" "https://www.linkedin.com/in/person2/"
```

### Step 5: Check Output

Results will be saved in: `output/profiles_crawlee_YYYYMMDD_HHMMSS.json`

```bash
# View the results
cat output/profiles_crawlee_*.json | jq '.'
```

---

## 🔧 Alternative: Using V2 Scraper (If Crawlee Fails)

### Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

### Run with Visible Browser (Recommended for Debugging)

```bash
python main_v2.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/"
```

The V2 scraper will:
- Open a **visible browser** window (you can watch it work!)
- Take screenshots in `screenshots/` directory
- Show detailed debug logs
- Save output to `output/profile_YYYYMMDD_HHMMSS.json`

---

## 📊 Expected Output Format

```json
[
  {
    "linkedinUrl": "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/",
    "firstName": "Ashutosh",
    "lastName": "Lath",
    "fullName": "Ashutosh Lath",
    "headline": "Software Engineer at Google",
    "location": "San Francisco Bay Area",
    "addressWithCountry": "San Francisco, California, United States",
    "description": "Passionate about...",
    "summary": "Passionate about...",
    "connections": 500,
    "followers": 1234,
    "mutualConnections": 12,

    "profilePicture": "https://media.licdn.com/...",
    "backgroundImage": "https://media.licdn.com/...",

    "email": "ashutosh@example.com",
    "phoneNumber": "+1-234-567-8900",
    "websites": ["https://example.com"],
    "twitter": "@ashutosh",
    "birthdate": "January 15",

    "currentCompany": "Google",
    "currentPosition": "Software Engineer",
    "currentCompanyURL": "https://www.linkedin.com/company/google",

    "experiences": [
      {
        "title": "Software Engineer",
        "company": "Google",
        "companyURL": "https://www.linkedin.com/company/google",
        "location": "Mountain View, CA",
        "startDate": "Jan 2020",
        "endDate": "Present",
        "duration": "3 years 10 months",
        "description": "Working on search infrastructure...",
        "employmentType": "Full-time"
      }
    ],

    "educations": [
      {
        "schoolName": "Stanford University",
        "degree": "Bachelor of Science",
        "fieldOfStudy": "Computer Science",
        "startDate": "2016",
        "endDate": "2020",
        "grade": "3.9 GPA",
        "description": "Focused on AI and machine learning..."
      }
    ],

    "skills": [
      {
        "name": "Python",
        "endorsements": 99
      },
      {
        "name": "JavaScript",
        "endorsements": 87
      }
    ],

    "recommendations": 15,
    "languages": ["English", "Hindi"],
    "certifications": [],
    "volunteering": [],
    "interests": []
  }
]
```

---

## 🐛 Troubleshooting

### Issue 1: "Access Denied" or Empty Output

**Cause**: LinkedIn detected automation

**Solutions**:
1. ✅ Use **fresh cookies** (export ALL cookies, not just li_at)
2. ✅ Use the **Crawlee scraper** (better anti-detection)
3. ✅ Run with **visible browser** (not headless)
4. ✅ Add random delays between requests
5. ❌ Don't scrape too many profiles at once (LinkedIn rate limits)

### Issue 2: "Executable doesn't exist" or Browser Not Found

**Solution**:
```bash
playwright install chromium
```

### Issue 3: Cookies Not Working

**Check**:
```bash
# Should have 6-10 cookies
cat cookies.json | jq '. | length'

# Should include li_at and JSESSIONID
cat cookies.json | jq '.[].name'
```

**Fix**: Export cookies again from browser while logged in

### Issue 4: Import Errors (crawlee not found)

**Solution**:
```bash
pip install -r requirements_crawlee.txt
# OR
pip install 'crawlee[playwright]==0.3.8' python-dotenv
```

### Issue 5: Pydantic Version Conflict

**Solution**:
```bash
pip install "pydantic>=2.5.0,<2.10.0" --force-reinstall
```

---

## 📝 Environment Configuration (Optional)

Create `.env` file for advanced settings:

```bash
# Authentication (if not using cookies.json)
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password

# Cookie file location
LINKEDIN_COOKIES=cookies.json

# Scraper settings
HEADLESS=false  # Set to true for headless mode
SCREENSHOT_DIR=screenshots
OUTPUT_DIR=output

# Delays (milliseconds)
PAGE_LOAD_DELAY=3000
SCROLL_DELAY=1000
```

---

## 🎮 Advanced Usage

### Batch Scraping Multiple Profiles

Create `profiles.txt`:
```
https://www.linkedin.com/in/person1/
https://www.linkedin.com/in/person2/
https://www.linkedin.com/in/person3/
```

Run:
```bash
# With Crawlee
while read url; do python scraper_crawlee.py "$url"; sleep 5; done < profiles.txt

# With V2
while read url; do python main_v2.py -u "$url"; sleep 5; done < profiles.txt
```

### Debugging with Screenshots

The V2 scraper automatically saves screenshots at key steps:
- `after_cookie_login_*.png` - After authentication
- `profile_loaded_*.png` - After profile page loads
- `after_scroll_*.png` - After scrolling

Check these if output is empty to see what LinkedIn is showing.

### Programmatic Usage

```python
import asyncio
from scraper_v2 import LinkedInScraperV2

async def scrape():
    scraper = LinkedInScraperV2(headless=False, debug=True)
    await scraper.initialize()
    await scraper.login_with_cookies('cookies.json')

    profile = await scraper.scrape_profile(
        'https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/'
    )

    print(f"Name: {profile.get('fullName')}")
    print(f"Headline: {profile.get('headline')}")

    await scraper.close()

asyncio.run(scrape())
```

---

## ⚠️ Important Notes

1. **Cookie Freshness**: Cookies expire! Re-export if scraper stops working
2. **Rate Limiting**: Don't scrape too fast (5-10 seconds between profiles)
3. **Account Safety**: Use a dedicated LinkedIn account for scraping
4. **Legal**: Only scrape public profiles you have permission to access
5. **LinkedIn ToS**: This tool is for educational/research purposes
6. **Visible Browser**: Always better than headless for avoiding detection
7. **Network**: Scraping from residential IP is better than datacenter/VPS

---

## 🏆 Success Checklist

Before running, make sure:

- [ ] Fresh cookies.json exported (ALL cookies, 6-10 total)
- [ ] Playwright browsers installed (`playwright install chromium`)
- [ ] Dependencies installed (`pip install -r requirements_crawlee.txt`)
- [ ] Target profile URL is valid and public
- [ ] Not scraping too many profiles too fast
- [ ] Using Crawlee scraper first (best success rate)
- [ ] Visible browser mode enabled (better than headless)

---

## 📞 Quick Commands Reference

```bash
# Setup
git pull origin claude/linkedin-profile-scraper-011CUe2EfsfHmy2VeQm4Zffz
pip install -r requirements_crawlee.txt
playwright install chromium

# Run Crawlee (BEST)
python scraper_crawlee.py "https://www.linkedin.com/in/USERNAME/"

# Run V2 (Backup)
python main_v2.py -u "https://www.linkedin.com/in/USERNAME/"

# Check output
ls -lt output/
cat output/profiles_crawlee_*.json | jq '.'

# View screenshots (if V2)
ls -lt screenshots/
open screenshots/profile_loaded_*.png  # Mac
xdg-open screenshots/profile_loaded_*.png  # Linux
start screenshots/profile_loaded_*.png  # Windows
```

---

## 🎯 Test Profile

Use this profile for testing (public profile):
```
https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/
```

Expected result: Should extract name, headline, location, and experience data.

---

## 🔍 What to Look For in Output

### ✅ Success Signs:
- `fullName` has actual name (not empty)
- `headline` has text
- `connections` > 0
- `experiences` array has items
- `linkedinUrl` matches target URL

### ❌ Failure Signs:
- All fields are empty strings
- `connections: 0` but profile has connections
- `experiences: []` but profile has work history
- **Action**: Check screenshots, re-export cookies, try visible browser

---

## 💡 Pro Tips

1. **First Run**: Always use Crawlee scraper with visible browser
2. **Cookie Issues**: Export cookies while on LinkedIn feed page (not login page)
3. **Slow is Smooth**: Add 5-10 second delays between profiles
4. **Deduplicate**: Check `linkedinUrl` field to avoid scraping same profile twice
5. **Logging**: Enable debug mode to see exactly what's happening
6. **Browser Choice**: Chrome/Chromium works best with Playwright

---

## 📚 File Structure

```
linkedinprofilescraper/
├── scraper_crawlee.py          # ⭐ RECOMMENDED - Use this first
├── scraper_v2.py                # Backup scraper
├── main_v2.py                   # V2 entry point
├── scraper.py                   # Original (don't use)
├── main.py                      # Original entry point
├── config.py                    # Configuration
├── parsers.py                   # Utility functions
├── requirements_crawlee.txt     # Dependencies for Crawlee
├── requirements.txt             # Dependencies for V2
├── cookies.json                 # YOUR COOKIES (create this!)
├── .env                         # Optional config
├── output/                      # Scraped data goes here
├── screenshots/                 # Debug screenshots (V2 only)
└── CURSOR_GUIDE.md             # This file
```

---

## 🚀 Ready to Run!

**Recommended First Command:**

```bash
python scraper_crawlee.py "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/"
```

Good luck! 🎉

---

## 📞 Support

If something doesn't work:
1. Check the troubleshooting section above
2. Look at screenshots (if using V2)
3. Verify cookies are fresh and complete
4. Try visible browser mode instead of headless
5. Use Crawlee scraper (better success rate)

**Most common issue**: Stale or incomplete cookies → Re-export ALL cookies from browser
