import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List

class APIFootballCollector:
    """
    Collector for API-Football (v3.football.api-sports.io).
    Fetches Fixtures, Lineups, Odds, and Predictions.
    """
    
    BASE_URL = "https://v3.football.api-sports.io"
    
    # Mapping common league names to API-Football League IDs
    LEAGUE_IDS = {
        "Brasileirão": 71,
        "Serie A": 71, # Brazil Serie A
        "Premier League": 39,
        "La Liga": 140,
        "Bundesliga": 78,
        "Serie A Italy": 135,
        "Ligue 1": 61
    }

    def __init__(self, api_key: str = "f9e8c54ea54bda893f34586680191036"):
        self.api_key = api_key
        self.headers = {
            'x-rapidapi-host': "v3.football.api-sports.io",
            'x-rapidapi-key': self.api_key
        }

    # Common Team Name Mappings (User Input -> API Name)
    TEAM_ALIASES = {
        "atletico mineiro": ["atletico-mg", "atletico mg", "atletico mineiro"],
        "athletico paranaense": ["athletico-pr", "athletico pr", "paranaense"],
        "atletico goianiense": ["atletico-go", "atletico go"],
        "bragantino": ["red bull bragantino", "rb bragantino"],
        "vasco": ["vasco da gama"],
        "botafogo": ["botafogo rj", "botafogo fr"],
        "sport": ["sport recife"],
        "america mineiro": ["america-mg", "america mg"],
    }

    def _match_teams(self, input_name: str, api_name: str) -> bool:
        """
        Fuzzy match team names, handling common aliases.
        """
        in_norm = input_name.lower().strip()
        api_norm = api_name.lower().strip()
        
        # 1. Direct Match
        if in_norm == api_norm:
            return True
            
        # 2. Check Aliases
        if in_norm in self.TEAM_ALIASES:
            if api_norm in self.TEAM_ALIASES[in_norm]:
                return True
                
        # 3. Substring Match (with safety)
        # Avoid matching "Manchester" to "Manchester City" AND "Manchester United" blindly
        # But for "Flamengo" -> "Flamengo RJ" it's okay.
        if len(in_norm) > 3 and in_norm in api_norm:
            return True
        if len(api_norm) > 3 and api_norm in in_norm:
            return True
            
        return False

    def get_fixture_id(self, home_team: str, away_team: str, date: str, league_id: int = None, season: int = 2025) -> Optional[int]:
        """
        Search for a fixture ID by team names and date.
        """
        try:
            # If league_id is not provided, try to infer or search broadly (but API requires parameters)
            # For now, default to Brasileirão (71) if not found or passed
            if not league_id:
                league_id = 71 
                
            # Format date to YYYY-MM-DD
            # Input might be DD/MM/YYYY or YYYY-MM-DD
            if "/" in date:
                dt = datetime.strptime(date, "%d/%m/%Y")
                date_str = dt.strftime("%Y-%m-%d")
            else:
                date_str = date
                
            url = f"{self.BASE_URL}/fixtures"
            
            # Helper to search a specific date
            def search_date(search_dt_str):
                print(f"   🔎 Searching API-Football for {home_team} vs {away_team} on {search_dt_str}...")
                params = {"league": league_id, "season": season, "date": search_dt_str}
                resp = requests.get(url, headers=self.headers, params=params)
                d = resp.json()
                
                # Fallback to date-only if needed
                if resp.status_code != 200 or d.get("errors"):
                    params = {"date": search_dt_str}
                    resp = requests.get(url, headers=self.headers, params=params)
                    d = resp.json()
                    
                if not d.get("response"):
                    return None
                    
                for fixture in d["response"]:
                    f_home = fixture["teams"]["home"]["name"]
                    f_away = fixture["teams"]["away"]["name"]
                    fid = fixture["fixture"]["id"]
                    
                    if self._match_teams(home_team, f_home) and self._match_teams(away_team, f_away):
                        print(f"    -> Found Fixture ID: {fid}")
                        return {"id": fid, "home_id": fixture["teams"]["home"]["id"], "away_id": fixture["teams"]["away"]["id"]}
                    
                    if self._match_teams(home_team, f_away) and self._match_teams(away_team, f_home):
                        print(f"    -> Found Fixture ID: {fid} (Teams Swapped)")
                        return {"id": fid, "home_id": fixture["teams"]["home"]["id"], "away_id": fixture["teams"]["away"]["id"]}
                return None

            # 1. Try Requested Date
            res = search_date(date_str)
            if res: return res
            
            # 2. Try Next Day (Timezone +)
            dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
            next_day = (dt_obj + timedelta(days=1)).strftime("%Y-%m-%d")
            print(f"   🔄 Checking next day ({next_day}) for timezone diff...")
            res = search_date(next_day)
            if res: return res
            
            # 3. Try Prev Day (Timezone -)
            prev_day = (dt_obj - timedelta(days=1)).strftime("%Y-%m-%d")
            print(f"   🔄 Checking prev day ({prev_day}) for timezone diff...")
            res = search_date(prev_day)
            if res: return res
            
            print("   ⚠️ Match not found in +/- 1 day window.")
            return None
            
        except Exception as e:
            print(f"   ❌ Error searching fixture: {e}")
            return None

    def get_team_stats(self, team_id: int, league_id: int, season: int) -> Dict:
        """
        Get team statistics for the season (Form, Goals, etc.)
        """
        url = f"{self.BASE_URL}/teams/statistics"
        params = {
            "team": team_id,
            "league": league_id,
            "season": season
        }
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json().get("response", {})
            return {}
        except Exception as e:
            print(f"   ❌ Error fetching team stats: {e}")
            return {}

    def get_fixture_details(self, fixture_id: int) -> Dict:
        """
        Get comprehensive details for a fixture:
        - Lineups
        - Injuries (if available in lineups/events)
        - Predictions (API-Football specific)
        - Odds (Pre-match)
        """
        details = {}
        
        try:
            # 1. Lineups
            url = f"{self.BASE_URL}/fixtures/lineups"
            response = requests.get(url, headers=self.headers, params={"fixture": fixture_id})
            if response.status_code == 200:
                details["lineups"] = response.json().get("response", [])
                
            # 2. Predictions (Stats/Advice)
            url = f"{self.BASE_URL}/predictions"
            response = requests.get(url, headers=self.headers, params={"fixture": fixture_id})
            if response.status_code == 200:
                details["predictions"] = response.json().get("response", [])
                
            # 3. Injuries
            url = f"{self.BASE_URL}/injuries"
            response = requests.get(url, headers=self.headers, params={"fixture": fixture_id})
            if response.status_code == 200:
                details["injuries"] = response.json().get("response", [])
                
            return details
            
        except Exception as e:
            print(f"   ❌ Error fetching details: {e}")
            return {}

if __name__ == "__main__":
    # Test
    collector = APIFootballCollector()
    fid = collector.get_fixture_id("Atletico Mineiro", "Flamengo", "2025-11-25", league_id=71, season=2025)
    if fid:
        print(f"Found Fixture ID: {fid}")
        details = collector.get_fixture_details(fid)
        print(f"Details keys: {details.keys()}")
        if details.get("predictions"):
            print(f"Prediction: {details['predictions'][0]['predictions']}")
    else:
        print("Fixture not found (expected for future/mock dates if not in API).")
    def get_key_players(self, team_id: int, season: int = 2025) -> List[Dict]:
        """
        Fetches top players for a team based on rating/goals.
        """
        url = f"{self.BASE_URL}/players"
        params = {
            "team": team_id,
            "season": season
        }
        
        try:
            resp = requests.get(url, headers=self.headers, params=params)
            data = resp.json()
            
            if not data.get("response"):
                return []
                
            players = []
            for item in data["response"]:
                p = item["player"]
                stats = item["statistics"][0] # League stats usually 0
                
                # Calculate a simple "Importance Score"
                # Rating (if available) or Goals + Assists
                rating = stats.get("games", {}).get("rating")
                try:
                    rating_val = float(rating) if rating else 0.0
                except:
                    rating_val = 0.0
                    
                goals = stats.get("goals", {}).get("total") or 0
                assists = stats.get("goals", {}).get("assists") or 0
                minutes = stats.get("games", {}).get("minutes") or 0
                
                players.append({
                    "name": p["name"],
                    "lastname": p["lastname"],
                    "rating": rating_val,
                    "goals": goals,
                    "assists": assists,
                    "minutes": minutes,
                    "position": stats.get("games", {}).get("position")
                })
                
            # Sort by Rating (desc) then Minutes (desc)
            players.sort(key=lambda x: (x["rating"], x["minutes"]), reverse=True)
            
            # Return top 5
            return players[:5]
            
        except Exception as e:
            print(f"    ⚠️ Error fetching key players: {e}")
            return []
