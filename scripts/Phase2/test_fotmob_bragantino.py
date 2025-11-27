import sys
import os
import json
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.Phase2.lineup_collector import FotMobScraper

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_bragantino():
    scraper = FotMobScraper()
    
    home = "Red Bull Bragantino"
    away = "Fortaleza"
    date = "26/11/2025"
    
    print(f"🚀 Testing FotMob Full Flow for {home} vs {away} on {date}")
    
    result = scraper.get_formations(home, away, date)
    
    print("\n📊 Result:")
    print(f"Match ID: {result.get('match_id')}")
    print(f"Home Formation: {result.get('home_formation')}")
    print(f"Away Formation: {result.get('away_formation')}")
    print(f"Source: {result.get('source')}")
    
    if result.get('home_lineup'):
        print(f"\n👥 Home Lineup ({len(result['home_lineup'])} players):")
        for p in result['home_lineup'][:5]:
            print(f"  - {p['name']} ({p['position']})")
            
    if result.get('away_lineup'):
        print(f"\n👥 Away Lineup ({len(result['away_lineup'])} players):")
        for p in result['away_lineup'][:5]:
            print(f"  - {p['name']} ({p['position']})")

if __name__ == "__main__":
    test_bragantino()
