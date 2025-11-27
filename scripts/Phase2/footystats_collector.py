import requests
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class FootyStatsCollector:
    """
    Collector for FootyStats API.
    Focuses on advanced stats: xG, Form, BTTS, Over/Under, etc.
    """
    BASE_URL = "https://api.footystats.org"
    
    # Mapping common league names to FootyStats names or IDs if needed
    # But dynamic search is better.
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def get_season_id(self, league_name: str, season_year: int) -> Optional[int]:
        """
        Find the Season ID for a given league and year.
        Example: "Brazil Serie A", 2025 -> 14231
        """
        url = f"{self.BASE_URL}/league-list?key={self.api_key}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Fuzzy match league name
                    # e.g. "Brasileirão" -> "Brazil Serie A"
                    target_name = league_name
                    if "Brasileirão" in league_name:
                        target_name = "Brazil Serie A"
                        
                    for league in data['data']:
                        if target_name.lower() in league['name'].lower():
                            # Find season
                            for season in league['season']:
                                if season['year'] == season_year:
                                    return season['id']
            return None
        except Exception as e:
            logger.error(f"Error fetching season ID: {e}")
            return None

    def get_team_stats(self, season_id: int) -> Dict[str, Dict]:
        """
        Fetch stats for ALL teams in a season.
        Returns a dictionary mapping Team Name -> Stats.
        This is more efficient than fetching per team if the API supports it.
        FootyStats has 'league-teams?key=X&season_id=Y&include=stats'
        """
        url = f"{self.BASE_URL}/league-teams?key={self.api_key}&season_id={season_id}&include=stats"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    teams_map = {}
                    for team in data['data']:
                        name = team['name']
                        # Store relevant stats
                        teams_map[name] = {
                            "id": team['id'],
                            "stats": team.get('stats', {}),
                            "form": team.get('stats', {}).get('form'),
                            "xg_for": team.get('stats', {}).get('xg_for_avg_overall'),
                            "xg_against": team.get('stats', {}).get('xg_against_avg_overall'),
                            "clean_sheets": team.get('stats', {}).get('clean_sheets_percentage_overall'),
                            "failed_to_score": team.get('stats', {}).get('failed_to_score_percentage_overall'),
                            "btts": team.get('stats', {}).get('btts_percentage_overall')
                        }
                    return teams_map
            return {}
        except Exception as e:
            logger.error(f"Error fetching team stats: {e}")
            return {}

    def get_league_tables(self, season_id: int) -> Dict:
        """
        Fetch league table/standings.
        """
        url = f"{self.BASE_URL}/league-tables?key={self.api_key}&season_id={season_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json().get("data", {})
            return {}
        except Exception as e:
            logger.error(f"Error fetching league tables: {e}")
            return {}
    def get_match_id(self, home_team: str, away_team: str, date: str) -> Optional[int]:
        """
        Find match ID by teams and date.
        FootyStats doesn't have a direct search by date/team easily accessible without listing matches.
        We can list matches for the league/season and filter.
        """
        # This is expensive if we don't know the season ID. 
        # Assuming we can pass season_id or find it.
        # For now, let's try to list matches for the specific day if possible, or just return None 
        # as implementing full match search might be complex without a known season ID.
        # However, we can use the 'todays-matches' endpoint if the date is today/tomorrow.
        
        # Better approach: The orchestrator already finds the season_id. 
        # We should update this method to accept season_id.
        return None

    def get_matches_for_season(self, season_id: int) -> List[Dict]:
        """Get all matches for a season."""
        url = f"{self.BASE_URL}/league-matches?key={self.api_key}&season_id={season_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json().get("data", [])
        except Exception:
            pass
        return []

    def get_match_lineups(self, match_id: int) -> Dict:
        """
        Fetch lineups for a specific match.
        Endpoint: /match?key=...&match_id=...
        """
        url = f"{self.BASE_URL}/match?key={self.api_key}&match_id={match_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Parse lineups
                    # FootyStats structure varies, need to be careful
                    # Usually data['data']['lineups']
                    return data['data'].get('lineups', {})
            return {}
        except Exception as e:
            logger.error(f"Error fetching match lineups: {e}")
            return {}
