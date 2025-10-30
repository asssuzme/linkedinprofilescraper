# Setup in Cursor IDE

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/asssuzme/linkedinprofilescraper.git
cd linkedinprofilescraper

# Checkout the feature branch
git checkout claude/linkedin-profile-scraper-011CUe2EfsfHmy2VeQm4Zffz
```

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium
```

### 3. Configure Authentication

**Option A: Using Your Cookie (Quick & Secure)**

Create `cookies.json`:
```json
[
  {
    "name": "li_at",
    "value": "AQEDAV4NWSwCSzSOAAABmOFrM6AAAAGaWsVk1lYAggQUBtjXPkD7M0Sr_CHXhMaWziMUGlHvtmzek8FBjb8mkzL5mT82tR35PY28DFeLkFYsDGSpiYLl3NA3uMp0On_WPVg_0l9Wzbl8i9vz8VkmLVD5",
    "domain": ".linkedin.com",
    "path": "/",
    "expires": 1767225600,
    "httpOnly": true,
    "secure": true,
    "sameSite": "None"
  }
]
```

Create `.env`:
```bash
LINKEDIN_COOKIES=cookies.json
HEADLESS=true
DELAY_BETWEEN_PROFILES=5
MAX_PROFILES=100
```

**Option B: Using Email/Password**

Create `.env`:
```bash
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
HEADLESS=true
DELAY_BETWEEN_PROFILES=5
MAX_PROFILES=100
```

### 4. Run the Scraper

**Scrape Ashutosh Lath's Profile:**
```bash
python main.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/" -o ashutosh_lath.json
```

**Watch it run (visible browser):**
```bash
# Temporarily set headless to false
python main.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/" --headless=false
```

### 5. View Results

```bash
# Results saved in output directory
cat output/ashutosh_lath.json

# Or check the auto-generated file
ls -la output/
```

---

## 📊 What Gets Extracted

The scraper will extract comprehensive data including:

✅ **Profile Info**
- Full name, headline, location
- Connections, followers count
- Profile picture (multiple resolutions)
- Public identifier & URN

✅ **Contact Information**
- Email address (if visible)
- Phone number (if visible)

✅ **Current Job**
- Job title
- Company name & details
- Industry, website
- Job duration (e.g., "2 yrs 3 mos")

✅ **Work Experience**
- Complete job history
- Multiple roles per company
- Job descriptions
- Employment dates & durations

✅ **Education**
- Schools/Universities
- Degrees & fields of study
- Graduation dates
- Additional details (GPA, activities, etc.)

✅ **Skills & Expertise**
- All skills listed
- Endorsement counts
- Top 5 skills by endorsements
- Skills used at specific companies

✅ **Certifications & Licenses**
- Certificate names
- Issuing organizations
- Issue dates & expiration
- Credential URLs

✅ **Languages**
- Language names
- Proficiency levels

✅ **Recommendations**
- Received recommendations
- Recommendation text
- Recommender details
- Given recommendations

✅ **Interests**
- Companies followed
- Groups joined
- Schools followed
- Newsletters subscribed
- Top voices followed

---

## 🎯 Example Commands

```bash
# Single profile with default output location
python main.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/"

# Single profile with custom output
python main.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/" -o results/profile.json

# Multiple profiles from file
cat > profiles.json << 'EOF'
[
  {"url": "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/"},
  {"url": "https://www.linkedin.com/in/another-profile/"}
]
EOF

python main.py -i profiles.json -o results/batch.json

# Run in visible browser mode (for debugging)
HEADLESS=false python main.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/"

# Scrape with longer delays (avoid rate limiting)
echo "DELAY_BETWEEN_PROFILES=10" >> .env
python main.py -i profiles.json
```

---

## 📁 Project Structure

```
linkedinprofilescraper/
├── main.py                   # CLI entry point - START HERE
├── scraper.py                # Core scraping logic (43KB)
├── parsers.py                # Data parsing utilities
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── .env                      # Your configuration (create this)
├── cookies.json              # Authentication cookies (create this)
├── example_input.json        # Example input format
├── output/                   # Results saved here
│   └── profiles_*.json
│
├── README.md                 # Full documentation
├── RUN_INSTRUCTIONS.md       # Detailed setup guide
├── OUTPUT_SCHEMA.md          # Output format reference
├── TROUBLESHOOTING.md        # Common issues
├── CONTRIBUTING.md           # Contribution guidelines
└── setup.sh                  # Automated setup script
```

---

## ⚡ Quick Setup Script

Or just run the automated setup:

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh

# Edit .env with your credentials
nano .env

# Run scraper
python main.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/"
```

---

## 🔍 Debugging Tips

### If authentication fails:
```bash
# Run in non-headless mode to see what's happening
HEADLESS=false python main.py -u "https://www.linkedin.com/in/test/"

# Check if cookies are valid
cat cookies.json

# Try with email/password instead
rm cookies.json
# Edit .env with LINKEDIN_EMAIL and LINKEDIN_PASSWORD
```

### If scraping is slow:
```bash
# Reduce delays in config.py or .env
echo "DELAY_BETWEEN_PROFILES=2" >> .env

# Skip detailed sections (edit scraper.py)
# Comment out sections you don't need
```

### If data is missing:
- Some profiles have privacy settings
- LinkedIn layout may have changed
- Run in non-headless mode to inspect
- Check TROUBLESHOOTING.md

---

## 🚨 Important Notes

⚠️ **Security:**
- Never commit `cookies.json` or `.env` to git
- Keep your LinkedIn session secure
- Cookies expire - refresh periodically

⚠️ **Rate Limiting:**
- Don't scrape too aggressively
- Use 5-10 second delays between profiles
- Limit to 50-100 profiles per session
- Respect LinkedIn's Terms of Service

⚠️ **Legal & Ethical:**
- This is for educational/research purposes
- Only scrape public profile data
- Don't use for spam or harassment
- Consider using LinkedIn's official API for commercial use

---

## 🎓 Learn More

- **README.md** - Complete user guide
- **OUTPUT_SCHEMA.md** - Every field explained
- **TROUBLESHOOTING.md** - Solutions to common problems
- **scraper.py:520** - Where the magic happens

---

## 💡 Pro Tips

1. **Start Small**: Test with 1-2 profiles first
2. **Monitor First Run**: Use `HEADLESS=false` to watch it work
3. **Save Progress**: Results are saved after each profile
4. **Batch Wisely**: Process in small batches (20-50 profiles)
5. **Check Output**: Verify data quality before scaling up

---

**Ready to scrape!** 🚀

Just run:
```bash
python main.py -u "https://www.linkedin.com/in/ashutosh-lath-3a374b2b3/"
```
