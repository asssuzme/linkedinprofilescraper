# Quick Start Guide - Running the LinkedIn Scraper

## Prerequisites Installed ✓
- ✓ Python dependencies installed
- ✓ Configuration files created
- ✓ Cookie authentication configured

## To Run on Your Local Machine

### 1. Install Playwright Browsers

```bash
python -m playwright install chromium
```

### 2. Your Cookie is Already Configured

The `cookies.json` file has been created with your LinkedIn session token.

### 3. Run the Scraper

**Single Profile:**
```bash
python main.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/"
```

**Multiple Profiles:**
```bash
# Create input file
cat > input.json << 'EOF'
[
  {"url": "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/"},
  {"url": "https://www.linkedin.com/in/another-profile/"}
]
EOF

# Run scraper
python main.py -i input.json -o output/results.json
```

### 4. Output Location

Results will be saved to:
- Default: `output/profiles_TIMESTAMP.json`
- Custom: Whatever you specify with `-o` flag

## What Gets Extracted

✅ **Basic Info**: Name, headline, location, connections, followers
✅ **Contact**: Email, phone (if visible)
✅ **Profile Pictures**: Multiple resolutions (100x100 to 800x800)
✅ **Current Job**: Title, company, industry, duration
✅ **Work Experience**: Full job history with descriptions
✅ **Education**: Schools, degrees, dates
✅ **Skills**: All skills with endorsement counts
✅ **Certifications**: Licenses and certificates
✅ **Languages**: Language proficiencies
✅ **Recommendations**: Both received and given
✅ **Interests**: Companies, groups, schools followed

## Example Commands

```bash
# Run with visible browser (for debugging)
echo "HEADLESS=false" >> .env
python main.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/"

# Run with custom delay between profiles
echo "DELAY_BETWEEN_PROFILES=10" >> .env
python main.py -i input.json

# Scrape and save to specific file
python main.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/" -o ashutosh_profile.json
```

## Troubleshooting

**If cookies expire:**
```bash
# Delete old cookies
rm cookies.json

# Login with email/password instead
cat > .env << 'EOF'
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
HEADLESS=true
EOF
```

**If rate limited:**
- Increase `DELAY_BETWEEN_PROFILES` in `.env`
- Reduce number of profiles scraped per session
- Wait 24 hours before retrying

**If data is missing:**
- Some profiles have privacy settings
- Try running in non-headless mode to debug
- Check if you're properly authenticated

## Network Restriction Note

The current environment has network restrictions preventing Playwright browser downloads.

**To run successfully, you need to:**
1. Download this repository to your local machine
2. Run `python -m playwright install chromium` locally
3. Execute the scraper commands above

## Security Notes

⚠️ **Important:**
- Keep your `cookies.json` file secure
- Don't commit it to version control (already in `.gitignore`)
- Cookies expire - you may need to refresh them periodically
- Use responsibly and respect LinkedIn's Terms of Service

## Support

For issues, check:
- `TROUBLESHOOTING.md` - Common problems and solutions
- `README.md` - Full documentation
- `OUTPUT_SCHEMA.md` - Detailed output format

---

**Ready to scrape!** Just run the commands above on your local machine where Playwright browsers can be installed.
