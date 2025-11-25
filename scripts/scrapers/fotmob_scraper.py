#!/usr/bin/env python3
"""
FotMob Scraper - Formation and Lineup Data
Provides Q6 (formations) data for Yudor v5.3 system
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FotMobScraper:
    """Scraper for FotMob API to get formation and lineup data"""

    BASE_URL = "https://www.fotmob.com/api"

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FotMob/165 Mobile/15E148',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # League ID mapping (FotMob league IDs)
    LEAGUE_IDS = {
        'La Liga': 87,
        'Premier League': 47,
        'Serie A': 55,
        'Bundesliga': 54,
        'Ligue 1': 53,
        'Championship': 44,
        'Champions League': 42,
        'Europa League': 73,
        'Conference League': 10239,
        'Liga Portugal': 63,
        'Eredivisie': 57
    }

    def __init__(self, delay: float = 2.0):
        """
        Initialize FotMob scraper

        Args:
            delay: Delay between requests in seconds (default: 2.0)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def search_match(self, home_team: str, away_team: str, date: str, league: str = None) -> Optional[str]:
        """
        Search for a match on FotMob and return match ID

        Args:
            home_team: Home team name
            away_team: Away team name
            date: Match date in DD/MM/YYYY format
            league: League name (optional, helps narrow search)

        Returns:
            FotMob match ID or None if not found
        """
        try:
            # Convert date format
            match_date = datetime.strptime(date, '%d/%m/%Y')
            date_str = match_date.strftime('%Y%m%d')

            # Try searching by team name
            logger.info(f"Searching FotMob for: {home_team} vs {away_team} on {date}")

            # Search for home team
            search_url = f"{self.BASE_URL}/searchapi/suggest"
            params = {'term': home_team, 'lang': 'en'}

            response = self.session.get(search_url, params=params, timeout=10)

            if response.status_code != 200:
                logger.warning(f"FotMob search failed: {response.status_code}")
                return None

            data = response.json()

            # Look for team in results
            team_id = None
            if 'squad' in data:
                for team in data['squad']:
                    if self._team_name_match(team.get('name', ''), home_team):
                        team_id = team.get('id')
                        logger.info(f"Found team ID: {team_id} for {home_team}")
                        break

            if not team_id:
                logger.warning(f"Team not found: {home_team}")
                return None

            # Get team fixtures to find match
            time.sleep(self.delay)

            fixtures_url = f"{self.BASE_URL}/teams"
            params = {'id': team_id, 'tab': 'fixtures', 'timeZone': 'Europe/London'}

            response = self.session.get(fixtures_url, params=params, timeout=10)

            if response.status_code != 200:
                logger.warning(f"FotMob fixtures failed: {response.status_code}")
                return None

            fixtures_data = response.json()

            # Search through fixtures for matching game
            match_id = self._find_match_in_fixtures(
                fixtures_data,
                home_team,
                away_team,
                match_date
            )

            if match_id:
                logger.info(f"✅ Found match ID: {match_id}")
                return str(match_id)
            else:
                logger.warning(f"❌ Match not found in fixtures")
                return None

        except Exception as e:
            logger.error(f"Error searching FotMob: {e}")
            return None

    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """
        Get match details including formations and lineups

        Args:
            match_id: FotMob match ID

        Returns:
            Dict with formations and lineup data, or None if failed
        """
        try:
            logger.info(f"Fetching match details for ID: {match_id}")

            url = f"{self.BASE_URL}/matchDetails"
            params = {'matchId': match_id}

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code != 200:
                logger.warning(f"FotMob match details failed: {response.status_code}")
                return None

            data = response.json()

            # Extract formations and lineups
            result = self._extract_formations_and_lineups(data)

            if result:
                logger.info(f"✅ Formations: {result['home_formation']} vs {result['away_formation']}")

            return result

        except Exception as e:
            logger.error(f"Error getting match details: {e}")
            return None

    def get_formations(self, home_team: str, away_team: str, date: str, league: str = None) -> Dict:
        """
        Complete workflow: Search match and get formations

        Args:
            home_team: Home team name
            away_team: Away team name
            date: Match date in DD/MM/YYYY format
            league: League name (optional)

        Returns:
            Dict with home_formation, away_formation, and lineup data
        """
        # Default result
        default = {
            'home_formation': '0',
            'away_formation': '0',
            'home_lineup': [],
            'away_lineup': [],
            'source': 'default',
            'match_id': None
        }

        # Search for match
        match_id = self.search_match(home_team, away_team, date, league)

        if not match_id:
            logger.warning(f"Could not find match: {home_team} vs {away_team}")
            return default

        # Add delay before fetching details
        time.sleep(self.delay)

        # Get match details
        details = self.get_match_details(match_id)

        if not details:
            logger.warning(f"Could not get details for match ID: {match_id}")
            return default

        details['source'] = 'fotmob'
        details['match_id'] = match_id

        return details

    def _team_name_match(self, name1: str, name2: str) -> bool:
        """
        Check if two team names match (fuzzy matching)

        Args:
            name1: First team name
            name2: Second team name

        Returns:
            True if names match, False otherwise
        """
        # Normalize names
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()

        # Exact match
        if n1 == n2:
            return True

        # Remove common prefixes
        prefixes = ['fc ', 'cf ', 'real ', 'cd ', 'ud ', 'rcd ', 'athletic ', 'atletico ', 'club ']
        for prefix in prefixes:
            n1 = n1.replace(prefix, '')
            n2 = n2.replace(prefix, '')

        # Check if one is substring of other
        if n1 in n2 or n2 in n1:
            return True

        # Check first word match (e.g., "Barcelona" matches "FC Barcelona")
        if n1.split()[0] == n2.split()[0]:
            return True

        return False

    def _find_match_in_fixtures(self, fixtures_data: Dict, home_team: str, away_team: str, match_date: datetime) -> Optional[str]:
        """
        Find specific match in fixtures data

        Args:
            fixtures_data: FotMob fixtures response
            home_team: Home team name
            away_team: Away team name
            match_date: Match date

        Returns:
            Match ID or None
        """
        try:
            # FotMob structures fixtures in different ways
            all_fixtures = []

            # Try different data structures
            if 'fixtures' in fixtures_data:
                if 'allFixtures' in fixtures_data['fixtures']:
                    if 'fixtures' in fixtures_data['fixtures']['allFixtures']:
                        all_fixtures = fixtures_data['fixtures']['allFixtures']['fixtures']

            # Search through fixtures
            for fixture in all_fixtures:
                try:
                    # Get fixture date
                    fixture_date_str = fixture.get('status', {}).get('utcTime', '')
                    if fixture_date_str:
                        fixture_date = datetime.fromisoformat(fixture_date_str.replace('Z', '+00:00'))

                        # Check if same day
                        if fixture_date.date() != match_date.date():
                            continue

                    # Check teams
                    home = fixture.get('home', {}).get('name', '')
                    away = fixture.get('away', {}).get('name', '')

                    if (self._team_name_match(home, home_team) and
                        self._team_name_match(away, away_team)):
                        return fixture.get('id')

                except Exception as e:
                    logger.debug(f"Error parsing fixture: {e}")
                    continue

            return None

        except Exception as e:
            logger.error(f"Error finding match in fixtures: {e}")
            return None

    def _extract_formations_and_lineups(self, data: Dict) -> Optional[Dict]:
        """
        Extract formations and lineups from match details

        Args:
            data: FotMob match details response

        Returns:
            Dict with formations and lineups
        """
        try:
            result = {
                'home_formation': '0',
                'away_formation': '0',
                'home_lineup': [],
                'away_lineup': []
            }

            # Check if lineup data exists
            if 'content' not in data or 'lineup' not in data['content']:
                logger.warning("No lineup data available")
                return None

            lineup = data['content']['lineup']

            # Extract home formation
            if 'homeTeam' in lineup:
                home_formation = lineup['homeTeam'].get('formation', '0')
                result['home_formation'] = home_formation if home_formation else '0'

                # Extract home lineup
                if 'players' in lineup['homeTeam']:
                    result['home_lineup'] = self._parse_lineup(lineup['homeTeam']['players'])

            # Extract away formation
            if 'awayTeam' in lineup:
                away_formation = lineup['awayTeam'].get('formation', '0')
                result['away_formation'] = away_formation if away_formation else '0'

                # Extract away lineup
                if 'players' in lineup['awayTeam']:
                    result['away_lineup'] = self._parse_lineup(lineup['awayTeam']['players'])

            # Check if we got valid formations
            if result['home_formation'] == '0' or result['away_formation'] == '0':
                logger.warning("Formations not available yet (match may not have started)")
                return None

            return result

        except Exception as e:
            logger.error(f"Error extracting formations: {e}")
            return None

    def _parse_lineup(self, players_data: List) -> List[Dict]:
        """
        Parse lineup data

        Args:
            players_data: FotMob players array

        Returns:
            List of player dicts with name, position, rating
        """
        lineup = []

        try:
            for player in players_data:
                player_info = {
                    'name': player.get('name', {}).get('fullName', 'Unknown'),
                    'position': player.get('role', 'Unknown'),
                    'shirt_number': player.get('jerseyNumber', 0),
                    'is_captain': player.get('isCaptain', False)
                }
                lineup.append(player_info)

        except Exception as e:
            logger.error(f"Error parsing lineup: {e}")

        return lineup


def test_fotmob_scraper():
    """Test FotMob scraper with sample match"""
    scraper = FotMobScraper(delay=2.0)

    # Test with a known match
    print("\n" + "="*80)
    print("Testing FotMob Scraper")
    print("="*80)

    # Example: Barcelona vs Athletic Club on 22/11/2025
    result = scraper.get_formations(
        home_team="Barcelona",
        away_team="Athletic Club",
        date="22/11/2025",
        league="La Liga"
    )

    print(f"\n📊 Result:")
    print(f"Home Formation: {result['home_formation']}")
    print(f"Away Formation: {result['away_formation']}")
    print(f"Source: {result['source']}")
    print(f"Match ID: {result['match_id']}")

    if result['home_lineup']:
        print(f"\n👥 Home Lineup ({len(result['home_lineup'])} players):")
        for player in result['home_lineup'][:5]:  # First 5 players
            print(f"  - {player['name']} ({player['position']})")

    print("\n" + "="*80)


if __name__ == "__main__":
    test_fotmob_scraper()
