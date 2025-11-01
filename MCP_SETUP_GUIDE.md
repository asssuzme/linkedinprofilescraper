# LinkedIn Profile Scraper - MCP Server Setup Guide

## Overview

After extensive testing, we've determined that **LinkedIn has very sophisticated anti-bot detection** that blocks traditional web scraping approaches (Playwright, Selenium, etc.). The recommended solution is to use the **LinkedIn MCP Server** within Claude Desktop.

## Problem Identified

LinkedIn blocks automated scraping by:
- ✅ Detecting Playwright/Selenium automation
- ✅ Showing only skeleton loaders (gray placeholders) on profile pages
- ✅ Returning empty pages for detail URLs (`/details/experience/`, etc.)
- ✅ Blocking even with stealth mode and realistic behavior

**Evidence:** Our tests showed that even with:
- playwright-stealth integration
- Valid authentication cookies
- Human-like scrolling and delays
- Proper User-Agent and headers

LinkedIn still blocks content from rendering.

## Solution: LinkedIn MCP Server

The MCP (Model Context Protocol) server works within Claude Desktop and provides reliable LinkedIn scraping.

### Setup Instructions

#### 1. Get Your LinkedIn Cookie

Run the cookie generator:

```bash
python3 generate_cookies.py
```

This will:
- Open a browser
- Log you into LinkedIn
- Save authentication cookies to `cookies.json`

#### 2. Extract the `li_at` Cookie

Run the MCP setup helper:

```bash
python3 mcp_scraper.py -u "your-linkedin-username" -o mcp_config.json
```

This will display your `li_at` cookie value and setup instructions.

#### 3. Configure Claude Desktop

Add to `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/stickerdaniel/linkedin-mcp-server",
        "linkedin-mcp-server"
      ],
      "env": {
        "LINKEDIN_COOKIE": "YOUR_LI_AT_COOKIE_VALUE_HERE"
      }
    }
  }
}
```

**Replace `YOUR_LI_AT_COOKIE_VALUE_HERE`** with the cookie value from step 2.

#### 4. Restart Claude Desktop

Close and reopen Claude Desktop to load the MCP server.

#### 5. Use in Claude

Ask Claude:

```
Get the LinkedIn profile for ashutosh-lath-3a374b2b3
```

Or:

```
Research this candidate's background: https://www.linkedin.com/in/johndoe/
```

## What the MCP Server Provides

The MCP server gives you access to:

- ✅ **Profile scraping** - Work history, education, skills, connections
- ✅ **Company data** - Organization information
- ✅ **Job postings** - Retrieve specific job details
- ✅ **Job search** - Query positions by keyword and location
- ✅ **Recommendations** - Get personalized job suggestions

## Why MCP Works Better

1. **Runs in Claude Desktop context** - Not detected as standalone bot
2. **Uses proven libraries** - Built on `linkedin-scraper` library
3. **Proper session management** - Handles authentication securely
4. **Active maintenance** - Regularly updated for LinkedIn changes

## Improvements Made to This Repo

Even though the MCP approach is recommended, we made these improvements:

1. ✅ **Added playwright-stealth** - Anti-detection for Playwright
2. ✅ **Fixed scroll methods** - Corrected `_scroll_page` implementation
3. ✅ **Improved navigation** - Better detail page handling
4. ✅ **Cookie generator** - Easy authentication setup ([generate_cookies.py](generate_cookies.py))
5. ✅ **MCP helper** - Setup assistant ([mcp_scraper.py](mcp_scraper.py))

## Files in This Repo

- `generate_cookies.py` - Generate LinkedIn cookies
- `mcp_scraper.py` - MCP setup helper
- `scraper_v2.py` - Enhanced Playwright scraper (blocked by LinkedIn)
- `main_v2.py` - Main entry point for v2 scraper
- `requirements.txt` - Python dependencies

## Alternative: Standalone Scraping

If you must use standalone scraping (not recommended), check:

- [joeyism/linkedin_scraper](https://github.com/joeyism/linkedin_scraper) - Most popular library
- [stickerdaniel/fast-linkedin-scraper](https://github.com/stickerdaniel/fast-linkedin-scraper) - Modern alternative

**Warning:** These will likely also be blocked by LinkedIn's anti-bot systems.

## Troubleshooting

### Cookie expired

Re-run: `python3 generate_cookies.py`

### MCP server not showing

1. Check Claude Desktop config path
2. Restart Claude Desktop
3. Check logs in Claude Desktop settings

### Profile data empty

LinkedIn may have updated their HTML structure. The MCP server is usually updated faster than this repo.

## Security Note

⚠️ **Never commit `cookies.json` or your `li_at` cookie to git!**

These files are in `.gitignore` for your protection.

## Credits

- LinkedIn MCP Server: https://github.com/stickerdaniel/linkedin-mcp-server
- LinkedIn Scraper Library: https://github.com/joeyism/linkedin_scraper

## License

See [LICENSE](LICENSE) file.
