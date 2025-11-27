import sys
import os
import re
import json
import requests
from bs4 import BeautifulSoup

# Add project root to path to import scripts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.scrapers.fotmob_scraper import FotMobScraper

def test_quixada():
    scraper = FotMobScraper()
    
    # 1. Try ID from URL directly
    url_id = "9qv4d5h"
    print(f"🚀 Testing FotMob with ID: {url_id}")
    
    details = scraper.get_match_details(url_id)
    if details:
        print("✅ Success with URL ID!")
        print(json.dumps(details, indent=4))
        return

    print("⚠️ URL ID failed (expected if it's a slug). Scraping page for numeric ID...")
    
    # 2. Scrape page to find numeric ID
    url = f"https://www.fotmob.com/matches/fortaleza-vs-quixada/{url_id}"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            # Look for numeric ID in the HTML
            # Often in <script id="__NEXT_DATA__"> or links
            # Pattern: "id":1234567 or matchId:1234567
            
            # Simple regex for matchId
            match = re.search(r'"matchId":(\d+)', resp.text)
            if not match:
                match = re.search(r'"id":(\d+),"matchTime', resp.text) # Contextual
            
            if match:
                numeric_id = match.group(1)
                print(f"✅ Found Numeric ID: {numeric_id}")
                
                # Dump NEXT_DATA for inspection
                soup = BeautifulSoup(resp.text, 'html.parser')
                next_data = soup.find('script', {'id': '__NEXT_DATA__'})
                if next_data:
                    data = json.loads(next_data.string)
                    with open("debug_fotmob_next_data.json", "w") as f:
                        json.dump(data, f, indent=4)
                    print("💾 Saved __NEXT_DATA__ to debug_fotmob_next_data.json")
                else:
                    print("❌ Could not find __NEXT_DATA__ script tag.")

                # details = scraper.get_match_details(numeric_id)
                # if details:
                #     print("✅ Success with Numeric ID!")
                #     print(json.dumps(details, indent=4))
                # else:
                #     print("❌ Failed to get details with Numeric ID.")
            else:
                print("❌ Could not find numeric ID in page HTML.")
                # Save HTML for debugging if needed
                # with open("debug_fotmob_page.html", "w") as f: f.write(resp.text)
        else:
            print(f"❌ Failed to fetch page: {resp.status_code}")
            
    except Exception as e:
        print(f"❌ Error scraping page: {e}")

if __name__ == "__main__":
    test_quixada()
