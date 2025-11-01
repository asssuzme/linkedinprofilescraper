#!/usr/bin/env python3
"""
LinkedIn Profile Scraper using MCP Server
Uses the linkedin-mcp-server to scrape LinkedIn profiles
"""
import json
import sys
import subprocess
from pathlib import Path

def get_li_at_cookie():
    """Extract li_at cookie from cookies.json"""
    cookies_file = Path('cookies.json')
    if not cookies_file.exists():
        print("❌ Error: cookies.json not found!")
        print("Please run: python3 generate_cookies.py first")
        sys.exit(1)

    with open(cookies_file, 'r') as f:
        cookies = json.load(f)

    li_at = next((c['value'] for c in cookies if c['name'] == 'li_at'), None)

    if not li_at:
        print("❌ Error: li_at cookie not found in cookies.json!")
        print("Please ensure you're logged into LinkedIn and regenerate cookies")
        sys.exit(1)

    return li_at

def scrape_profile(username: str, output_file: str = None):
    """
    Scrape a LinkedIn profile using the MCP server

    Args:
        username: LinkedIn username (e.g., "ashutosh-lath-3a374b2b3")
        output_file: Path to save the JSON output
    """
    print(f"\n{'='*60}")
    print("LinkedIn Profile Scraper via MCP Server")
    print(f"{'='*60}\n")

    # Get cookie
    print("Extracting authentication cookie...")
    li_at_cookie = get_li_at_cookie()
    print(f"✓ Found li_at cookie")

    # Extract username from URL if needed
    if username.startswith('http'):
        # Parse username from URL
        username = username.rstrip('/').split('/')[-1]

    print(f"✓ Target profile: {username}")

    # Prepare MCP server command
    # The MCP server provides get_person_profile tool
    mcp_request = {
        "linkedin_username": username
    }

    print(f"\nℹ️  The LinkedIn MCP server is a Model Context Protocol server")
    print(f"   designed to work with Claude Desktop, not as a standalone tool.")
    print(f"\n📋 To use it properly:")
    print(f"\n1. Install in Claude Desktop:")
    print(f"   Add to Claude Desktop config (~/.config/Claude/claude_desktop_config.json):")
    print(f'''
   {{
     "mcpServers": {{
       "linkedin": {{
         "command": "uvx",
         "args": ["--from", "git+https://github.com/stickerdaniel/linkedin-mcp-server", "linkedin-mcp-server"],
         "env": {{
           "LINKEDIN_COOKIE": "{li_at_cookie[:30]}..."
         }}
       }}
     }}
   }}
''')
    print(f"\n2. Restart Claude Desktop")
    print(f"\n3. In Claude, ask:")
    print(f'   "Get the LinkedIn profile for {username}"')
    print(f"\n" + "="*60)
    print(f"\n💡 Alternative: Use the linkedin-scraper library directly")
    print(f"   See: https://github.com/joeyism/linkedin_scraper")

    return {
        "note": "MCP server requires Claude Desktop",
        "username": username,
        "li_at_cookie": li_at_cookie[:30] + "...",
        "setup_instructions": "See output above"
    }

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='LinkedIn Profile Scraper using MCP Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 mcp_scraper.py -u "ashutosh-lath-3a374b2b3"
  python3 mcp_scraper.py -u "https://www.linkedin.com/in/johndoe/" -o output.json
        """
    )

    parser.add_argument(
        '-u', '--url',
        type=str,
        required=True,
        help='LinkedIn profile URL or username'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output JSON file path (optional)'
    )

    args = parser.parse_args()

    result = scrape_profile(args.url, args.output)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n✅ Config info saved to: {output_path}")

if __name__ == '__main__':
    main()
