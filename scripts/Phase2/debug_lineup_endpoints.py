import requests
import json
import os
import time
from datetime import datetime, timedelta

# --- CONFIG ---
API_FOOTBALL_KEY = "f9e8c54ea54bda893f34586680191036"
FOOTYSTATS_KEY = "c715e230a56b394e01389862fd3bb752e3f9d5e174b2ec86de081c6740a2fcd2"

HOME_TEAM = "Bragantino"
AWAY_TEAM = "Fortaleza"
DATE_STR = "2025-11-26" # Likely date
LEAGUE_ID_API = 71 # Brasileirao Serie A
SEASON = 2025

OUTPUT_DIR = "data/debug_lineups"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_json(name, data):
    # Add match prefix
    filename = f"{name}_{HOME_TEAM}_vs_{AWAY_TEAM}.json"
    path = f"{OUTPUT_DIR}/{filename}"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"💾 Saved {name} to {path}")

# --- API-FOOTBALL ---
print(f"\n🚀 Testing API-Football Endpoints for {HOME_TEAM} vs {AWAY_TEAM}...")

headers = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': API_FOOTBALL_KEY
}

# 1. Search Fixture
print("   🔎 Searching Fixture...")
fixture_id = None
search_dates = [DATE_STR, "2025-11-25", "2025-11-27"] # Window

for d in search_dates:
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"league": LEAGUE_ID_API, "season": SEASON, "date": d}
    resp = requests.get(url, headers=headers, params=params)
    data = resp.json()
    # save_json(f"api_football_fixtures_{d}", data) # Skip saving search results to reduce clutter
    
    if data.get("response"):
        for f in data["response"]:
            h = f["teams"]["home"]["name"]
            a = f["teams"]["away"]["name"]
            # Simple check
            if (HOME_TEAM in h or "Red Bull" in h) and AWAY_TEAM in a:
                fixture_id = f["fixture"]["id"]
                print(f"   ✅ Found Fixture ID: {fixture_id} on {d}")
                break
    if fixture_id: break

if fixture_id:
    # 2. Lineups Endpoint
    print("   🔄 Fetching Lineups...")
    url = "https://v3.football.api-sports.io/fixtures/lineups"
    params = {"fixture": fixture_id}
    resp = requests.get(url, headers=headers, params=params)
    save_json("api_football_lineups", resp.json())

    # 3. Players Endpoint (Squad/Events)
    print("   🔄 Fetching Players (Fixture)...")
    url = "https://v3.football.api-sports.io/fixtures/players"
    params = {"fixture": fixture_id}
    resp = requests.get(url, headers=headers, params=params)
    save_json("api_football_players", resp.json())
    
    # 4. Predictions (Context)
    print("   🔄 Fetching Predictions...")
    url = "https://v3.football.api-sports.io/predictions"
    params = {"fixture": fixture_id}
    resp = requests.get(url, headers=headers, params=params)
    save_json("api_football_predictions", resp.json())

    # 5. Injuries (Context)
    print("   🔄 Fetching Injuries...")
    url = "https://v3.football.api-sports.io/injuries"
    params = {"fixture": fixture_id}
    resp = requests.get(url, headers=headers, params=params)
    save_json("api_football_injuries", resp.json())

else:
    print("   ❌ Fixture not found in API-Football.")


# --- FOOTYSTATS ---
print(f"\n🚀 Testing FootyStats Endpoints for {HOME_TEAM} vs {AWAY_TEAM}...")

# 1. Get Season ID (Hardcoded or Search)
# We know 2025 Brazil Serie A is likely 14231 from previous logs
SEASON_ID = 14231 
print(f"   ℹ️ Using Season ID: {SEASON_ID}")

# 2. List Matches to Find ID
print("   🔎 Searching Match ID...")
url = f"https://api.footystats.org/league-matches?key={FOOTYSTATS_KEY}&season_id={SEASON_ID}"
resp = requests.get(url)
data = resp.json()
# save_json("footystats_matches_list", data) # Too big, don't save entire list

fs_match_id = None
if data.get("data"):
    for m in data["data"]:
        h = m["home_name"]
        a = m["away_name"]
        # FootyStats names might differ
        if (HOME_TEAM in h or "Red Bull" in h) and AWAY_TEAM in a:
            fs_match_id = m["id"]
            print(f"   ✅ Found FootyStats Match ID: {fs_match_id}")
            break

if fs_match_id:
    # 3. Match Endpoint (includes lineups?)
    print("   🔄 Fetching Match Details (including lineups)...")
    # Try 'match_id' instead of 'id'
    url = f"https://api.footystats.org/match?key={FOOTYSTATS_KEY}&match_id={fs_match_id}"
    resp = requests.get(url)
    save_json("footystats_match_details", resp.json())
    
else:
    print("   ❌ Match not found in FootyStats.")

print("\n✅ Debug Complete. Check data/debug_lineups/ folder.")
