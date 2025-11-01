# macOS Run Guide - LinkedIn Scraper V2 (FIXED)

## 🎉 What Was Fixed

### Critical Fixes Applied:
1. ✅ **Async/await bugs** - Added `extract_text_async()` and `extract_attribute_async()` helpers
2. ✅ **Hardcoded paths removed** - No more `/root/.cache/` paths, works on macOS
3. ✅ **Better selectors** - Simplified fallbacks for name, headline, location
4. ✅ **Explicit waits** - Wait for top-card elements before extraction
5. ✅ **Auth wall handling** - Detect and retry with consent button clicks
6. ✅ **Timeout fixes** - Increased to 45s for slow LinkedIn pages
7. ✅ **Connection parsing** - No hard timeouts, query elements instead
8. ✅ **Better error messages** - Actionable guidance with screenshot paths

## 🚀 How to Run (macOS)

### Prerequisites
```bash
# Ensure you're in the venv
cd ~/linkedin\ scraper/linkedinprofilescraper
source .venv/bin/activate

# Verify Playwright is installed
playwright --version

# If not, install it
pip install playwright
playwright install chromium
```

### Option 1: Seed cookies first (if needed)

If you don't have `cookies.json` or it's expired:

```bash
# Add credentials to .env
echo "LINKEDIN_EMAIL=your-email@example.com" >> .env
echo "LINKEDIN_PASSWORD=your-password" >> .env
echo "HEADLESS=false" >> .env

# Run v1 to create cookies.json
python main.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/" -o output/seed.json
```

This will:
- Open a visible browser
- Log in with your credentials
- Save cookies to `cookies.json`
- Scrape the profile

### Option 2: Export cookies manually

1. Open Chrome/Safari/Firefox
2. Log into LinkedIn
3. Install "Cookie-Editor" extension
4. Click extension → Export → JSON
5. Save as `cookies.json` in project root

### Run V2 Scraper

**Visible mode (recommended for first run):**
```bash
HEADLESS=false python main_v2.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/" -o output/ashutosh_profile.json
```

**Headless mode (after confirming it works):**
```bash
python main_v2.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/" -o output/ashutosh_profile.json
```

### Check Output

```bash
# View the JSON
cat output/ashutosh_profile.json | python -m json.tool | head -50

# Check screenshots
ls -lt screenshots/

# View screenshot (macOS)
open screenshots/profile_loaded_*.png
```

## 📊 Expected Output

The scraper should now extract:
```json
{
  "linkedinUrl": "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/",
  "fullName": "Ashutosh Lath",
  "firstName": "Ashutosh",
  "lastName": "Lath",
  "headline": "Your headline here",
  "addressWithCountry": "Location, State, Country",
  "connections": 500,
  "followers": 100,
  "experiences": [...],
  "educations": [...],
  "skills": [...]
}
```

## 🐛 Troubleshooting

### Issue: "Cookies are invalid or expired"
**Fix:**
1. Delete old `cookies.json`
2. Run v1 with credentials OR export fresh cookies from browser
3. Check screenshot: `screenshots/after_cookie_login_*.png`

### Issue: "Profile gated or authentication required"
**Fix:**
1. Run with `HEADLESS=false` to manually click consent buttons
2. Check screenshot: `screenshots/authwall_*.png`
3. The scraper will try clicking Accept/Continue automatically in visible mode

### Issue: Empty fields (name, headline, etc.)
**Fix:**
- The new selectors should handle this
- Check screenshots to see what LinkedIn is showing
- Check debug logs for which selectors matched

### Issue: Playwright browser not found
**Fix:**
```bash
playwright install chromium
```

## 📝 What Changed in Code

### `parsers.py`
- Added `async def extract_text_async(element)`
- Added `async def extract_attribute_async(element, attr)`
- Original sync versions kept for backwards compatibility

### `scraper_v2.py`
- Changed imports to use `extract_text_async`, `extract_attribute_async`
- Removed hardcoded `executable_path`
- Simplified name selectors: `h1.text-heading-xlarge`, `h1`, `.pv-text-details__left-panel h1`
- Simplified headline selectors: `div.text-body-medium`, variants
- Simplified location selectors: `span.text-body-small`, variants
- Added explicit wait for top-card before extraction
- Added `_try_click_consent_button()` method
- Auth wall retry logic with consent button clicking
- Connection/follower parsing uses `query_selector_all` instead of `inner_text` with timeouts
- Increased timeouts from 30s to 45s
- Expand "See more" buttons before extraction

### `main_v2.py`
- Use `Config.HEADLESS` instead of hardcoded `True`
- Better error messages with command examples
- Guide user to run v1 if cookies missing but credentials present

## ✅ Verification Steps

After running, verify:
1. ✅ Output file exists in `output/ashutosh_profile.json`
2. ✅ `fullName` field is not empty
3. ✅ `headline` field has text
4. ✅ `connections` > 0 (if profile has connections visible)
5. ✅ `experiences` array has items
6. ✅ Screenshots show loaded profile (not "Access denied")

## 🎯 Next Steps

If v2 works:
- Run on more profiles to test reliability
- Batch scrape with delays between profiles

If v2 still has issues:
- Try Crawlee version: `python scraper_crawlee.py "<url>"`
- Crawlee has even better anti-detection built-in

## 📞 Quick Commands Reference

```bash
# Activate venv
source .venv/bin/activate

# Seed cookies (first time)
python main.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/" -o output/seed.json

# Run v2 (visible)
HEADLESS=false python main_v2.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/" -o output/result.json

# Run v2 (headless)
python main_v2.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/" -o output/result.json

# Check output
cat output/result.json | python -m json.tool

# View screenshots
open screenshots/profile_loaded_*.png
```

---

## 🎉 Ready to Test!

All fixes are applied and pushed. Pull the latest code and run v2 - it should work much better now on macOS!

The key improvements:
- ✅ No more async warnings
- ✅ Works on macOS (no hardcoded paths)
- ✅ Better selector matching
- ✅ Handles auth walls gracefully
- ✅ Actionable error messages
- ✅ No timeout issues on connections/followers
