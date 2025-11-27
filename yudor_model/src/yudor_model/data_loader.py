import os
import sys
import requests
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path to import from scripts
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

try:
    from scripts.production.master_orchestrator import Config
except ImportError:
    # Fallback if import fails (e.g. different directory structure)
    class Config:
        FOOTYSTATS_API_KEY = os.getenv("FOOTYSTATS_API_KEY", "")

def fetch_season_matches(season_id: int) -> List[Dict]:
    """
    Fetches all matches for a given season ID from FootyStats.
    """
    if not Config.FOOTYSTATS_API_KEY:
        raise ValueError("FOOTYSTATS_API_KEY not found in environment or Config.")

    url = f"https://api.football-data-api.com/league-matches?key={Config.FOOTYSTATS_API_KEY}&season_id={season_id}"
    
    print(f"Fetching matches for season {season_id}...")
    response = requests.get(url, timeout=30)
    
    if response.status_code != 200:
        print(f"Error fetching data: HTTP {response.status_code}")
        return []
        
    data = response.json()
    if not data.get("data"):
        print(f"No data found for season {season_id}")
        return []
        
    return data["data"]

def process_matches_to_df(matches: List[Dict]) -> pd.DataFrame:
    """
    Converts raw FootyStats match list to a clean DataFrame for the model.
    """
    processed_data = []
    
    for match in matches:
        # Skip if match is not completed (no scores)
        if match.get("status") != "complete":
            continue
            
        # Parse date (unix timestamp or string)
        date_unix = match.get("date_unix")
        if date_unix:
            match_date = datetime.fromtimestamp(date_unix)
        else:
            continue # Skip if no date

        processed_data.append({
            "date": match_date,
            "home_team_name": match.get("home_name"),
            "away_team_name": match.get("away_name"),
            "home_goals": int(match.get("homeGoalCount", 0)),
            "away_goals": int(match.get("awayGoalCount", 0)),
            "home_xg": float(match.get("team_a_xg", 0) or 0),
            "away_xg": float(match.get("team_b_xg", 0) or 0),
            "status": match.get("status")
        })
        
    df = pd.DataFrame(processed_data)
    if not df.empty:
        df = df.sort_values("date")
        
    return df

def load_and_process_season(season_id: int) -> pd.DataFrame:
    """
    Orchestrates fetching and processing for a season.
    """
    matches = fetch_season_matches(season_id)
    df = process_matches_to_df(matches)
    return df

if __name__ == "__main__":
    # Example usage: Premier League 2024/2025 (check ID)
    # For now, we can test with a known ID or just print help
    print("Import this module to use load_and_process_season(season_id)")
