import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.Phase2.lineup_collector import FotMobScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_fotmob_flu_sp():
    print("🚀 Testing FotMob Full Flow for Fluminense vs Sao Paulo")
    
    collector = FotMobScraper()
    
    # Date: 27/11/2025
    # Teams: Fluminense vs Sao Paulo
    
    home_team = "Fluminense"
    away_team = "Sao Paulo"
    date = "27/11/2025"
    
    # 1. Search
    match_info = collector.search_match(home_team, away_team, date)
    
    if match_info:
        print(f"✅ Found match ID: {match_info['id']}")
        
        # 2. Get Details
        details = collector.get_match_details(match_info['id'], home_team, away_team, match_info['home_team_id'])
        
        print("\n📊 Result:")
        print(f"Match ID: {details.get('match_id')}")
        print(f"Home Formation: {details.get('home_formation')}")
        print(f"Away Formation: {details.get('away_formation')}")
        print(f"Source: {details.get('source')}")
        
        # H2H
        h2h = details.get('h2h', [])
        print(f"\n⚔️ Head-to-Head ({len(h2h)} matches):")
        for m in h2h[:3]:
            print(f"  - {m.get('time', {}).get('utcTime', 'Unknown')} | {m.get('home', {}).get('name')} {m.get('status', {}).get('scoreStr')} {m.get('away', {}).get('name')}")
            
        # Team Form
        home_form = details.get('home_form', [])
        print(f"\n📈 Home Form ({len(home_form)} matches):")
        for m in home_form:
            print(f"  - {m.get('resultString')} vs {m.get('home', {}).get('name') if m.get('home', {}).get('id') != str(match_info['home_team_id']) else m.get('away', {}).get('name')} ({m.get('score')})")

        away_form = details.get('away_form', [])
        print(f"\n📈 Away Form ({len(away_form)} matches):")
        for m in away_form:
            print(f"  - {m.get('resultString')} vs {m.get('home', {}).get('name') if m.get('home', {}).get('id') != str(match_info['away_team_id']) else m.get('away', {}).get('name')} ({m.get('score')})")

        if details.get('home_lineup'):
            print(f"\n👥 Home Lineup ({len(details['home_lineup'])} players):")
            for p in details['home_lineup'][:5]:
                print(f"  - {p['name']} ({p['position']})")
                
        if details.get('away_lineup'):
            print(f"\n👥 Away Lineup ({len(details['away_lineup'])} players):")
            for p in details['away_lineup'][:5]:
                print(f"  - {p['name']} ({p['position']})")
                
    else:
        print("❌ Match not found")

if __name__ == "__main__":
    test_fotmob_flu_sp()
