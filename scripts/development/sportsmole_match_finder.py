#!/usr/bin/env python3
"""
SportsMole Match Preview Finder

SportsMole creates match-specific preview pages with URLs like:
https://www.sportsmole.co.uk/football/barcelona/preview/preview-espanyol-vs-sevilla-prediction-team-news-lineups_123456.html

This script searches for the specific match preview URL dynamically.
"""
import requests
import re
from typing import Optional
from urllib.parse import quote_plus


def find_sportsmole_preview(home_team: str, away_team: str, max_results: int = 5) -> Optional[str]:
    """
    Find SportsMole match preview URL via Google search

    Args:
        home_team: Home team name
        away_team: Away team name
        max_results: Maximum results to check

    Returns:
        Match preview URL or None
    """
    # Build search query
    query = f"site:sportsmole.co.uk {home_team} vs {away_team} preview prediction"
    search_url = f"https://www.google.com/search?q={quote_plus(query)}"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(search_url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None

        # Extract URLs from search results
        # Look for sportsmole.co.uk/football URLs containing "preview"
        pattern = r'https://www\.sportsmole\.co\.uk/football/[^"<>]+preview[^"<>]+'
        matches = re.findall(pattern, response.text)

        if matches:
            # Return first match (most relevant)
            # Clean up URL (remove tracking parameters)
            url = matches[0].split('&')[0]
            return url

        return None

    except Exception as e:
        print(f"  ⚠️  Error searching SportsMole: {e}")
        return None


def find_sportsmole_preview_direct(home_team: str, away_team: str) -> Optional[str]:
    """
    Scrape SportsMole main page to find specific match preview

    SportsMole lists upcoming match previews on their main football page.
    We scrape this page to extract the correct preview URL.
    """
    try:
        # Fetch main football page
        response = requests.get("https://www.sportsmole.co.uk/football/", timeout=15)

        if response.status_code != 200:
            return None

        html = response.text

        # Look for preview links containing both teams
        # Pattern: href="/football/{team}/preview/{home}-vs-{away}-prediction-team-news-lineups_{id}.html"
        pattern = r'href="(/football/[^"]+/preview/[^"]*' + re.escape(home_team.lower()) + r'[^"]*vs[^"]*' + re.escape(away_team.lower()) + r'[^"]*\.html)"'

        matches = re.findall(pattern, html, re.IGNORECASE)

        if matches:
            # Return first match (most recent)
            preview_path = matches[0]
            full_url = f"https://www.sportsmole.co.uk{preview_path}"
            return full_url

        # Try reverse order (away vs home)
        pattern_reverse = r'href="(/football/[^"]+/preview/[^"]*' + re.escape(away_team.lower()) + r'[^"]*vs[^"]*' + re.escape(home_team.lower()) + r'[^"]*\.html)"'
        matches_reverse = re.findall(pattern_reverse, html, re.IGNORECASE)

        if matches_reverse:
            preview_path = matches_reverse[0]
            full_url = f"https://www.sportsmole.co.uk{preview_path}"
            return full_url

        return None

    except Exception as e:
        print(f"  ⚠️  Error scraping SportsMole: {e}")
        return None


def get_sportsmole_match_url(home_team: str, away_team: str, method: str = 'search') -> Optional[str]:
    """
    Get SportsMole match preview URL

    Args:
        home_team: Home team name
        away_team: Away team name
        method: 'search' (Google search) or 'direct' (direct URL check)

    Returns:
        Match preview URL or None
    """
    if method == 'search':
        return find_sportsmole_preview(home_team, away_team)
    elif method == 'direct':
        return find_sportsmole_preview_direct(home_team, away_team)
    else:
        # Try both methods
        url = find_sportsmole_preview_direct(home_team, away_team)
        if not url:
            url = find_sportsmole_preview(home_team, away_team)
        return url


if __name__ == "__main__":
    # Test with Espanyol vs Sevilla
    print("\n" + "="*80)
    print("SPORTSMOLE MATCH PREVIEW FINDER - TEST")
    print("="*80 + "\n")

    test_matches = [
        ("Espanyol", "Sevilla"),
        ("Barcelona", "Real Madrid"),
        ("Liverpool", "Arsenal"),
    ]

    for home, away in test_matches:
        print(f"\n🔍 Searching: {home} vs {away}")
        print("-" * 80)

        # Try direct method first (faster)
        print("Method 1: Direct URL check...")
        url = find_sportsmole_preview_direct(home, away)
        if url:
            print(f"✅ Found: {url}")
        else:
            print("❌ Not found via direct method")

            # Try Google search as fallback
            print("\nMethod 2: Google search...")
            url = find_sportsmole_preview(home, away)
            if url:
                print(f"✅ Found: {url}")
            else:
                print("❌ Not found via search")

    print("\n" + "="*80 + "\n")
