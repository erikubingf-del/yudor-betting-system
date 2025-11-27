import requests
import json

API_KEY = "f9e8c54ea54bda893f34586680191036"
LEAGUE_ID = 71 # Brasileirão
DATE = "2025-11-26"

def check_fixtures():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': API_KEY
    }
    params = {
        "league": LEAGUE_ID,
        "season": "2025",
        "date": DATE
    }
    
    print(f"🔎 Searching fixtures for League {LEAGUE_ID} on {DATE}...")
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    fixtures = data.get("response", [])
    
    if not fixtures:
        print("❌ No fixtures found for this date.")
        # Try searching by round? Or just list next 10 fixtures
        print("   Trying to fetch next 10 fixtures for the league...")
        params = {"league": LEAGUE_ID, "season": "2025", "next": 10}
        response = requests.get(url, headers=headers, params=params)
        fixtures = response.json().get("response", [])
        
    print(f"\n✅ Found {len(fixtures)} fixtures:")
    for f in fixtures:
        home = f["teams"]["home"]["name"]
        away = f["teams"]["away"]["name"]
        date = f["fixture"]["date"]
        fid = f["fixture"]["id"]
        print(f"   - [{date}] {home} vs {away} (ID: {fid})")

if __name__ == "__main__":
    check_fixtures()
