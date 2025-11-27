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
import re
from bs4 import BeautifulSoup

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

    def search_match(self, home_team: str, away_team: str, date: str, league: str = None) -> Optional[Dict]:
        """
        Search for a match on FotMob and return match details including ID and team IDs.
        """
        try:
            # Convert date format
            try:
                match_date = datetime.strptime(date, '%d/%m/%Y')
            except ValueError:
                match_date = datetime.strptime(date, '%Y-%m-%d')
            
            # Try searching by team name
            logger.info(f"Searching FotMob for: {home_team} vs {away_team} on {date}")

            # Search for home team - UPDATED ENDPOINT
            search_url = f"{self.BASE_URL}/search/suggest"
            params = {'term': home_team, 'lang': 'en'}

            response = self.session.get(search_url, params=params, timeout=10)

            if response.status_code != 200:
                logger.warning(f"FotMob search failed: {response.status_code}")
                return None

            data = response.json()

            # Parse new search structure (List of sections)
            match_info = None
            
            if isinstance(data, list):
                for section in data:
                    if 'suggestions' in section:
                        for item in section['suggestions']:
                            # Check for direct match result
                            if item.get('type') == 'match':
                                h_name = item.get('homeTeamName', '')
                                a_name = item.get('awayTeamName', '')
                                m_date_str = item.get('matchDate', '') # e.g. 2025-11-26T00:30:00Z
                                
                                # Check teams
                                if (self._team_name_match(h_name, home_team) and 
                                    self._team_name_match(a_name, away_team)):
                                    
                                    # Check date (fuzzy check or exact)
                                    # API returns ISO format. We have DD/MM/YYYY
                                    if m_date_str:
                                        try:
                                            m_dt = datetime.fromisoformat(m_date_str.replace('Z', '+00:00'))
                                            if m_dt.date() == match_date.date():
                                                match_info = {
                                                    'id': str(item.get('id')),
                                                    'home_team_id': str(item.get('homeTeamId')),
                                                    'away_team_id': str(item.get('awayTeamId'))
                                                }
                                                logger.info(f"✅ Found match ID in search: {match_info['id']}")
                                                return match_info
                                        except:
                                            pass
            
            if match_info:
                return match_info

            logger.warning("Match not found in search suggestions.")
            return None

        except Exception as e:
            logger.error(f"Error searching FotMob: {e}")
            return None

    def _get_match_url_from_team_page(self, team_id: str, match_id: str) -> Optional[str]:
        """
        Scrape team page to find the correct match URL (with alphanumeric ID).
        """
        try:
            url = f"https://www.fotmob.com/teams/{team_id}/overview"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch team page {url}: {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            next_data = soup.find('script', {'id': '__NEXT_DATA__'})
            
            if not next_data:
                logger.warning(f"Could not find __NEXT_DATA__ on team page {url}")
                return None
                
            data = json.loads(next_data.string)
            
            match_id_str = str(match_id)
            
            # Let's try to parse the fallback data
            fallback = data.get('props', {}).get('pageProps', {}).get('fallback', {})
            logger.info(f"Fallback keys: {list(fallback.keys())}")
            
            for key, val in fallback.items():
                if key.startswith('team-'):
                    details = val.get('details', {})
                    next_match = details.get('nextMatch')
                    if next_match:
                        logger.info(f"Found nextMatch ID: {next_match.get('id')}")
                        if str(next_match.get('id')) == match_id_str:
                            return f"https://www.fotmob.com{next_match.get('pageUrl')}"
                    
                    # Check ongoing match
                    ongoing = details.get('ongoing')
                    if ongoing:
                        logger.info(f"Found ongoing ID: {ongoing.get('id')}")
                        if str(ongoing.get('id')) == match_id_str:
                             if ongoing.get('pageUrl'):
                                 return f"https://www.fotmob.com{ongoing.get('pageUrl')}"

                    # Check recent matches (fixtures)
                    recent_matches = details.get('recentMatches', [])
                    # Check upcoming matches (fixtures)
                    upcoming_matches = details.get('upcomingMatches', [])
                    
                    all_matches = recent_matches + upcoming_matches
                    for match in all_matches:
                        if str(match.get('id')) == match_id_str and match.get('pageUrl'):
                            return f"https://www.fotmob.com{match.get('pageUrl')}"

            # If not found in specific paths, regex search the string for the URL
            json_str = json.dumps(data)
            # Pattern: "pageUrl":"/matches/[^"]*match_id"
            # Allow spaces around colon
            pattern = r'"pageUrl"\s*:\s*"(/matches/[^"]+)"'
            matches = re.findall(pattern, json_str)
            for m in matches:
                if match_id_str in m:
                    return f"https://www.fotmob.com{m}"

            return None
            
        except Exception as e:
            logger.error(f"Error getting match URL from team page: {e}")
            return None

    def get_match_details(self, match_id: str, home_team: str = None, away_team: str = None, home_team_id: str = None) -> Optional[Dict]:
        """
        Get match details including formations and lineups
        Uses HTML scraping of __NEXT_DATA__ to bypass API auth issues.
        """
        try:
            logger.info(f"Fetching match details for ID: {match_id}")
            
            url = None
            
            # Try to get URL from team page if team ID is provided
            if home_team_id:
                url = self._get_match_url_from_team_page(home_team_id, match_id)
                if url:
                    logger.info(f"Found match URL: {url}")
            
            if not url:
                # Fallback to constructing URL (which might fail)
                # Try constructing slug if teams are known
                if home_team and away_team:
                    slug = f"{home_team.lower().replace(' ', '-')}-vs-{away_team.lower().replace(' ', '-')}"
                    url = f"https://www.fotmob.com/matches/{slug}/{match_id}" # This is likely wrong format (needs alphanumeric)
                    # But maybe numeric works with correct slug?
                    # Let's try the numeric ID URL as last resort
                else:
                    url = f"https://www.fotmob.com/matches/match/{match_id}"
                logger.warning(f"Using fallback URL (likely to fail): {url}")
            
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                logger.warning(f"FotMob match page failed: {response.status_code}")
                return None

            # Parse HTML to find __NEXT_DATA__
            soup = BeautifulSoup(response.text, 'html.parser')
            next_data_tag = soup.find('script', {'id': '__NEXT_DATA__'})
            
            if not next_data_tag:
                logger.warning("Could not find __NEXT_DATA__ in match page")
                return None
                
            data = json.loads(next_data_tag.string)
            
            # Extract content from props
            try:
                page_props = data.get('props', {}).get('pageProps', {})
                content = page_props.get('content', {})
                
                if not content:
                    content = page_props.get('matchDetails', {}).get('content', {})
                
                wrapped_data = {'content': content}
                
                # Extract match data (formations, lineups, h2h, form)
                result = self._extract_match_data(wrapped_data)

                if result:
                    logger.info(f"✅ Formations: {result['home_formation']} vs {result['away_formation']}")
                    logger.info(f"✅ H2H Matches: {len(result.get('h2h', []))}")
                    logger.info(f"✅ Team Form: Home({len(result.get('home_form', []))}), Away({len(result.get('away_form', []))})")

                return result
                
            except Exception as e:
                logger.error(f"Error parsing NEXT_DATA: {e}")
                return None

        except Exception as e:
            logger.error(f"Error getting match details: {e}")
            return None

    def get_formations(self, home_team: str, away_team: str, date: str, league: str = None) -> Dict:
        """
        Main method to get formations and lineups
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
        match_info = self.search_match(home_team, away_team, date, league)
        
        if not match_info:
            logger.warning(f"Could not find match: {home_team} vs {away_team}")
            return default

        match_id = match_info['id']
        home_team_id = match_info.get('home_team_id')

        # Add delay before fetching details
        time.sleep(self.delay)

        # Get match details
        details = self.get_match_details(match_id, home_team, away_team, home_team_id)

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

    def _extract_match_data(self, data: Dict) -> Optional[Dict]:
        """
        Extract formations, lineups, H2H, and team form from match data
        """
        try:
            if 'content' not in data:
                logger.warning("No content in match data")
                return None
                
            content = data['content']
            
            result = {
                'home_formation': '0',
                'away_formation': '0',
                'home_lineup': [],
                'away_lineup': [],
                'h2h': [],
                'home_form': [],
                'away_form': [],
                'source': 'fotmob'
            }
            
            # 1. Extract Lineups and Formations
            if 'lineup' in content:
                lineup = content['lineup']
                result['source'] = lineup.get('lineupType', 'fotmob')

                # Extract home formation
                if 'homeTeam' in lineup:
                    home_formation = lineup['homeTeam'].get('formation', '0')
                    result['home_formation'] = home_formation if home_formation else '0'
                    players = lineup['homeTeam'].get('players') or lineup['homeTeam'].get('starters')
                    if players:
                        result['home_lineup'] = self._parse_lineup(players)

                # Extract away formation
                if 'awayTeam' in lineup:
                    away_formation = lineup['awayTeam'].get('formation', '0')
                    result['away_formation'] = away_formation if away_formation else '0'
                    players = lineup['awayTeam'].get('players') or lineup['awayTeam'].get('starters')
                    if players:
                        result['away_lineup'] = self._parse_lineup(players)
            
            # 2. Extract Head-to-Head (H2H)
            if 'h2h' in content and 'matches' in content['h2h']:
                result['h2h'] = content['h2h']['matches']
            
            # 3. Extract Team Form
            # content.matchFacts.teamForm is a list of lists [HomeForm, AwayForm]
            if 'matchFacts' in content and 'teamForm' in content['matchFacts']:
                team_form = content['matchFacts']['teamForm']
                if isinstance(team_form, list) and len(team_form) >= 2:
                    result['home_form'] = team_form[0]
                    result['away_form'] = team_form[1]

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
        for p in players_data:
            try:
                if not isinstance(p, dict):
                    logger.warning(f"Skipping invalid player data: {p}")
                    continue
                    
                # Handle rating/performance
                rating = '0'
                if 'rating' in p and isinstance(p['rating'], dict):
                    rating = str(p['rating'].get('num', '0'))
                elif 'performance' in p and isinstance(p['performance'], dict):
                    rating = str(p['performance'].get('seasonRating', '0'))
                
                player = {
                    'id': str(p.get('id', '0')),
                    'name': p.get('name') or f"{p.get('firstName', '')} {p.get('lastName', '')}".strip(),
                    'number': str(p.get('shirtNumber', '')),
                    'position': p.get('position', 'Unknown'),
                    'rating': rating
                }
                lineup.append(player)
            except Exception as e:
                logger.error(f"Error parsing player: {e}, Data: {p}")
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
