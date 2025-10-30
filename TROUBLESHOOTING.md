# Troubleshooting Guide

This guide helps you resolve common issues with the LinkedIn Profile Scraper.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Authentication Problems](#authentication-problems)
3. [Scraping Errors](#scraping-errors)
4. [Data Quality Issues](#data-quality-issues)
5. [Performance Issues](#performance-issues)
6. [Rate Limiting](#rate-limiting)

---

## Installation Issues

### Issue: Playwright installation fails

**Symptoms:**
```
Error: playwright executable doesn't exist
```

**Solutions:**
```bash
# Make sure you run the install command
playwright install chromium

# If that fails, try with sudo (Linux/Mac)
sudo playwright install chromium

# On Windows, run as Administrator
playwright install chromium --with-deps
```

### Issue: Python version incompatibility

**Symptoms:**
```
SyntaxError: invalid syntax
```

**Solution:**
Make sure you're using Python 3.8 or higher:
```bash
python3 --version
# Should show 3.8.0 or higher
```

If needed, create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Missing dependencies

**Symptoms:**
```
ModuleNotFoundError: No module named 'playwright'
```

**Solution:**
```bash
pip install -r requirements.txt
```

---

## Authentication Problems

### Issue: Login fails with "Invalid credentials"

**Solutions:**

1. **Double-check your credentials** in `.env`:
   ```env
   LINKEDIN_EMAIL=your_actual_email@example.com
   LINKEDIN_PASSWORD=your_actual_password
   ```

2. **Try manual login first**:
   - Set `HEADLESS=false` in `.env`
   - Run the scraper
   - Watch the browser window
   - Check if LinkedIn requires verification

3. **Enable 2FA backup method**:
   - LinkedIn may require 2FA
   - Use SMS or authenticator app
   - Complete verification manually when prompted

### Issue: "Cookies are invalid or expired"

**Symptoms:**
```
Exception: Cookies are invalid or expired
```

**Solutions:**

1. **Delete old cookies and re-login**:
   ```bash
   rm cookies.json
   python main.py -u "https://linkedin.com/in/yourprofile"
   ```

2. **Login with credentials instead**:
   - Comment out `LINKEDIN_COOKIES` in `.env`
   - Use `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD` instead

### Issue: LinkedIn requires CAPTCHA

**Symptoms:**
- Browser shows CAPTCHA challenge
- Login stuck on verification page

**Solutions:**

1. **Complete CAPTCHA manually**:
   ```env
   HEADLESS=false  # Set in .env
   ```
   Run scraper and complete CAPTCHA in the browser window

2. **Use fresh cookies**:
   - Login to LinkedIn in your regular browser
   - Export cookies using a browser extension
   - Save to `cookies.json`
   - Set `LINKEDIN_COOKIES=cookies.json` in `.env`

3. **Wait and retry**:
   - LinkedIn may have flagged your account
   - Wait 24 hours before trying again
   - Use a different network/IP if possible

---

## Scraping Errors

### Issue: Profile not loading

**Symptoms:**
```
Error: Timeout waiting for page to load
```

**Solutions:**

1. **Increase timeout** - Modify in `scraper.py`:
   ```python
   await self.page.goto(profile_url, wait_until='networkidle', timeout=60000)
   ```

2. **Check internet connection**:
   ```bash
   ping linkedin.com
   ```

3. **Verify profile URL is correct**:
   ```
   ✓ https://www.linkedin.com/in/johndoe
   ✗ www.linkedin.com/in/johndoe (missing https://)
   ✗ linkedin.com/johndoe (wrong format)
   ```

### Issue: Missing data in output

**Symptoms:**
- Some fields are empty or null
- Expected data not present

**Reasons & Solutions:**

1. **Privacy settings** - User has restricted their profile
   - Solution: Can't be fixed, respect user privacy

2. **LinkedIn layout changed** - Selectors need updating
   - Solution: Check for updates to the scraper
   - Report issue on GitHub with profile URL

3. **Premium vs free profiles** - Different layouts
   - Solution: Code may need updates for premium profiles

4. **Not logged in properly** - Some data only visible when logged in
   - Solution: Verify authentication is working
   ```bash
   # Run in non-headless mode and check
   HEADLESS=false python main.py -u "https://linkedin.com/in/test"
   ```

### Issue: Scraper crashes mid-run

**Symptoms:**
```
Error: Target closed
Error: Connection closed
```

**Solutions:**

1. **Increase system resources**:
   - Close other applications
   - Increase RAM allocation if in Docker

2. **Reduce batch size**:
   - Scrape fewer profiles at once
   - Split input file into smaller batches

3. **Add error recovery**:
   The scraper should continue on errors. Check logs for which profile failed.

---

## Data Quality Issues

### Issue: Incorrect data extracted

**Symptoms:**
- Wrong name, company, or other fields
- Misaligned data

**Solutions:**

1. **Run in non-headless mode** to debug:
   ```env
   HEADLESS=false
   ```

2. **Check profile manually**:
   - Visit the LinkedIn profile
   - Compare with scraper output
   - Report discrepancies

3. **Update selectors**:
   - LinkedIn changes their HTML frequently
   - Check `scraper.py` for outdated selectors
   - Update CSS selectors as needed

### Issue: Special characters not displaying correctly

**Symptoms:**
- Garbled text with special characters
- Emoji not showing properly

**Solution:**

Output file should be UTF-8 encoded. This is handled automatically, but you can verify:
```python
# In main.py, encoding is already set:
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
```

---

## Performance Issues

### Issue: Scraping is very slow

**Symptoms:**
- Takes minutes per profile
- Browser seems frozen

**Solutions:**

1. **Reduce scrolling**:
   In `scraper.py`, reduce scroll iterations:
   ```python
   async def _scroll_page(self):
       for _ in range(3):  # Reduced from 5
           await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
           await asyncio.sleep(0.5)  # Reduced from 1
   ```

2. **Skip detailed sections**:
   Comment out sections you don't need in `scrape_profile()`:
   ```python
   # profile_data['recommendations'] = await self._extract_recommendations()
   ```

3. **Use faster network**:
   - Slow internet = slow scraping
   - Consider using a server with better bandwidth

### Issue: High memory usage

**Symptoms:**
- System runs out of memory
- Scraper crashes with memory errors

**Solutions:**

1. **Process in smaller batches**:
   ```bash
   # Instead of 100 profiles at once
   python main.py -i batch1.json  # 20 profiles
   python main.py -i batch2.json  # 20 profiles
   ```

2. **Clear results periodically**:
   Results are saved after each profile, so you can restart safely.

---

## Rate Limiting

### Issue: Getting rate limited by LinkedIn

**Symptoms:**
- Profiles stop loading
- LinkedIn shows "Too many requests"
- Account temporarily restricted

**Solutions:**

1. **Increase delays** in `.env`:
   ```env
   DELAY_BETWEEN_PROFILES=10  # Increased from 5
   ```

2. **Reduce daily quota**:
   ```env
   MAX_PROFILES=50  # Reduced from 100
   ```

3. **Use proxy rotation**:
   ```env
   PROXY_SERVER=http://proxy.example.com:8080
   ```

4. **Wait before retrying**:
   - Wait 24 hours if restricted
   - Don't scrape during peak hours (9am-5pm PST)

5. **Use multiple accounts** (carefully):
   - Rotate between different LinkedIn accounts
   - Each account should scrape different profiles
   - Be very careful not to violate ToS

### Issue: IP banned by LinkedIn

**Symptoms:**
- Can't access LinkedIn at all
- Login page doesn't load

**Solutions:**

1. **Use a different network**:
   - Switch from WiFi to mobile data
   - Use a VPN
   - Use residential proxies

2. **Wait it out**:
   - IP bans are often temporary (24-72 hours)
   - Don't try to bypass immediately

3. **Contact LinkedIn** (last resort):
   - If you believe it's a mistake
   - Explain legitimate use case

---

## Debug Mode

To enable detailed debugging:

1. **Run in non-headless mode**:
   ```env
   HEADLESS=false
   ```

2. **Add debug logging** in `scraper.py`:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Take screenshots**:
   ```python
   # Add after navigation
   await self.page.screenshot(path='debug.png')
   ```

4. **Print HTML** for debugging selectors:
   ```python
   html = await self.page.content()
   print(html)
   ```

---

## Getting Help

If you still have issues:

1. **Check existing issues**: https://github.com/yourrepo/issues
2. **Search the documentation**: README.md, OUTPUT_SCHEMA.md
3. **Open a new issue** with:
   - Error message (full traceback)
   - Steps to reproduce
   - Your environment (OS, Python version)
   - Profile URL (if not private)
   - Relevant configuration

## Prevention Tips

1. **Start small**: Test with 1-2 profiles first
2. **Monitor**: Watch the first few scrapes
3. **Backup**: Keep cookies and config backed up
4. **Update regularly**: Keep dependencies updated
5. **Respect limits**: Don't be too aggressive with scraping

---

**Remember**: LinkedIn's structure changes frequently. What works today might need adjustments tomorrow. Always test your scraper periodically and be ready to adapt.
