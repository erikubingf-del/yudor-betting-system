import requests
from bs4 import BeautifulSoup
import json

def check_team_page(team_id):
    url = f"https://www.fotmob.com/teams/{team_id}/overview"
    print(f"Checking Team Page: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    resp = requests.get(url, headers=headers)
    print(f"Status: {resp.status_code}")
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    next_data = soup.find('script', {'id': '__NEXT_DATA__'})
    if next_data:
        data = json.loads(next_data.string)
        # Save to file for inspection
        with open('debug_team_next_data.json', 'w') as f:
            json.dump(data, f, indent=4)
        print("✅ Saved debug_team_next_data.json")
        
        # Try to find fixtures
        # Structure might be props.pageProps.fallback or something
        props = data.get('props', {}).get('pageProps', {})
        print(f"PageProps keys: {list(props.keys())}")
        
    else:
        print("❌ NEXT_DATA not found.")

# Bragantino ID: 109705
check_team_page(109705)
