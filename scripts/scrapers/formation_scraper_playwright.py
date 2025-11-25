#!/usr/bin/env python3
"""
Formation Scraper using Playwright
Scrapes formations and lineups from FlashScore (most reliable free source)
Provides Q6 (formations) data for Yudor v5.3 system
"""

import time
import json
import re
import logging
from typing import Dict, Optional, List
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not installed. Install with: pip install playwright && playwright install chromium")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FormationScraperPlaywright:
    """Scraper using Playwright to get formations from FlashScore"""

    FLASHSCORE_URL = "https://www.flashscore.com"

    def __init__(self, headless: bool = True, delay: float = 2.0):
        """
        Initialize Playwright scraper

        Args:
            headless: Run browser in headless mode (default: True)
            delay: Delay between actions in seconds (default: 2.0)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not installed. Run: pip install playwright && playwright install chromium")

        self.headless = headless
        self.delay = delay

    def search_flashscore_match(self, home_team: str, away_team: str, date: str) -> Optional[str]:
        """
        Search for match on FlashScore and return match URL

        Args:
            home_team: Home team name
            away_team: Away team name
            date: Match date in DD/MM/YYYY format

        Returns:
            FlashScore match URL or None
        """
        try:
            with sync_playwright() as p:
                logger.info(f"Launching browser to search for: {home_team} vs {away_team}")

                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()

                # Convert date
                match_date = datetime.strptime(date, '%d/%m/%Y')
                date_str = match_date.strftime('%d.%m.%Y')  # FlashScore format

                # Go to FlashScore
                page.goto(self.FLASHSCORE_URL, wait_until='networkidle')
                time.sleep(self.delay)

                # Search for match
                search_query = f"{home_team} {away_team}"
                logger.info(f"Searching FlashScore: {search_query}")

                # Type in search box
                try:
                    search_input = page.wait_for_selector('input[placeholder*="Search"]', timeout=5000)
                    search_input.fill(search_query)
                    time.sleep(1)

                    # Look for match in results
                    match_url = self._find_match_in_results(page, home_team, away_team, date_str)

                    browser.close()
                    return match_url

                except Exception as e:
                    logger.error(f"Error during search: {e}")
                    browser.close()
                    return None

        except Exception as e:
            logger.error(f"Error searching FlashScore: {e}")
            return None

    def get_formations_from_url(self, match_url: str) -> Dict:
        """
        Get formations from FlashScore match URL

        Args:
            match_url: FlashScore match URL

        Returns:
            Dict with formations and lineup data
        """
        default_result = {
            'home_formation': '0',
            'away_formation': '0',
            'home_lineup': [],
            'away_lineup': [],
            'source': 'default'
        }

        try:
            with sync_playwright() as p:
                logger.info(f"Fetching formations from: {match_url}")

                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()

                # Go to match page
                page.goto(match_url, wait_until='networkidle')
                time.sleep(self.delay)

                # Click on Lineups tab
                try:
                    lineups_tab = page.wait_for_selector('text=Lineups', timeout=5000)
                    lineups_tab.click()
                    time.sleep(self.delay)
                except:
                    logger.warning("Lineups tab not found")

                # Extract formations
                formations = self._extract_formations_flashscore(page)

                browser.close()

                if formations:
                    formations['source'] = 'flashscore'
                    return formations
                else:
                    return default_result

        except Exception as e:
            logger.error(f"Error getting formations: {e}")
            return default_result

    def get_formations(self, home_team: str, away_team: str, date: str) -> Dict:
        """
        Complete workflow: Search match and get formations

        Args:
            home_team: Home team name
            away_team: Away team name
            date: Match date in DD/MM/YYYY format

        Returns:
            Dict with formations and lineup data
        """
        # Search for match
        match_url = self.search_flashscore_match(home_team, away_team, date)

        if not match_url:
            logger.warning(f"Could not find match URL")
            return {
                'home_formation': '0',
                'away_formation': '0',
                'home_lineup': [],
                'away_lineup': [],
                'source': 'default'
            }

        # Get formations from match page
        return self.get_formations_from_url(match_url)

    def _find_match_in_results(self, page: Page, home_team: str, away_team: str, date_str: str) -> Optional[str]:
        """Find match in search results"""
        try:
            # Wait for search results
            time.sleep(2)

            # Get all match links
            matches = page.query_selector_all('a[href*="/match/"]')

            for match in matches:
                try:
                    # Get match text
                    text = match.inner_text().lower()

                    # Check if both teams are mentioned
                    if (home_team.lower() in text and away_team.lower() in text) or \
                       (away_team.lower() in text and home_team.lower() in text):

                        # Get match URL
                        href = match.get_attribute('href')
                        if href:
                            full_url = f"{self.FLASHSCORE_URL}{href}" if href.startswith('/') else href
                            logger.info(f"✅ Found match URL: {full_url}")
                            return full_url

                except Exception as e:
                    logger.debug(f"Error checking match: {e}")
                    continue

            return None

        except Exception as e:
            logger.error(f"Error finding match in results: {e}")
            return None

    def _extract_formations_flashscore(self, page: Page) -> Optional[Dict]:
        """Extract formations from FlashScore page"""
        try:
            result = {
                'home_formation': '0',
                'away_formation': '0',
                'home_lineup': [],
                'away_lineup': []
            }

            # Look for formation elements (FlashScore uses specific class names)
            # These may need to be updated based on actual HTML structure

            # Try to find formation text
            formations = page.query_selector_all('text=/\\d-\\d-\\d/')

            if len(formations) >= 2:
                result['home_formation'] = formations[0].inner_text().strip()
                result['away_formation'] = formations[1].inner_text().strip()

                logger.info(f"✅ Found formations: {result['home_formation']} vs {result['away_formation']}")
                return result
            else:
                logger.warning("Formations not found on page")
                return None

        except Exception as e:
            logger.error(f"Error extracting formations: {e}")
            return None


# Simple fallback scraper without Playwright (manual formation input)
class ManualFormationInput:
    """Manual formation input as fallback when scraping fails"""

    def get_formations(self, home_team: str, away_team: str, date: str) -> Dict:
        """
        Prompt user to manually enter formations

        Args:
            home_team: Home team name
            away_team: Away team name
            date: Match date

        Returns:
            Dict with manually entered formations
        """
        print(f"\n{'='*80}")
        print(f"Manual Formation Input Required")
        print(f"Match: {home_team} vs {away_team} ({date})")
        print(f"{'='*80}\n")

        print("Please check lineups on FlashScore/SofaScore and enter formations:")
        print("Examples: 4-3-3, 3-5-2, 4-4-2, 4-2-3-1, etc.")
        print("Enter '0' if formations not available yet\n")

        home_formation = input(f"{home_team} formation: ").strip()
        away_formation = input(f"{away_team} formation: ").strip()

        if not home_formation:
            home_formation = '0'
        if not away_formation:
            away_formation = '0'

        return {
            'home_formation': home_formation,
            'away_formation': away_formation,
            'home_lineup': [],
            'away_lineup': [],
            'source': 'manual'
        }


def get_formations_with_fallback(home_team: str, away_team: str, date: str, manual_fallback: bool = False) -> Dict:
    """
    Get formations with automatic fallback to manual input

    Args:
        home_team: Home team name
        away_team: Away team name
        date: Match date in DD/MM/YYYY
        manual_fallback: Allow manual input if scraping fails (default: False)

    Returns:
        Dict with formations
    """
    # Try Playwright scraper first
    if PLAYWRIGHT_AVAILABLE:
        try:
            scraper = FormationScraperPlaywright(headless=True, delay=2.0)
            result = scraper.get_formations(home_team, away_team, date)

            if result['home_formation'] != '0' and result['away_formation'] != '0':
                return result
            else:
                logger.warning("Playwright scraper returned no formations")

        except Exception as e:
            logger.error(f"Playwright scraper failed: {e}")

    # Fallback to manual input if enabled
    if manual_fallback:
        logger.info("Falling back to manual formation input")
        manual_scraper = ManualFormationInput()
        return manual_scraper.get_formations(home_team, away_team, date)

    # Return default
    return {
        'home_formation': '0',
        'away_formation': '0',
        'home_lineup': [],
        'away_lineup': [],
        'source': 'default'
    }


def test_playwright_scraper():
    """Test Playwright scraper"""
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not installed!")
        print("Install with: pip install playwright && playwright install chromium")
        return

    print("\n" + "="*80)
    print("Testing Playwright Formation Scraper")
    print("="*80)

    # Test with manual fallback
    result = get_formations_with_fallback(
        home_team="Barcelona",
        away_team="Athletic Club",
        date="22/11/2025",
        manual_fallback=True  # Allow manual input for testing
    )

    print(f"\n📊 Result:")
    print(f"Home Formation: {result['home_formation']}")
    print(f"Away Formation: {result['away_formation']}")
    print(f"Source: {result['source']}")
    print("\n" + "="*80)


if __name__ == "__main__":
    test_playwright_scraper()
