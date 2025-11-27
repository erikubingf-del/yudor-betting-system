from scripts.Phase2.lineup_collector import FotMobScraper
import logging

logging.basicConfig(level=logging.INFO)

def debug_search():
    scraper = FotMobScraper()
    
    teams = ["Fluminense", "Sao Paulo"]
    
    for team in teams:
        print(f"\n🔎 Searching for: {team}")
        url = f"{scraper.BASE_URL}/search/suggest"
        params = {'term': team, 'lang': 'en'}
        
        try:
            response = scraper.session.get(url, params=params)
            print(f"   Status: {response.status_code}")
            data = response.json()
            
            found = False
            results = []
            
            if isinstance(data, list):
                for section in data:
                    if 'suggestions' in section:
                        results.extend(section['suggestions'])
            
            for t in results:
                name = t.get('name', t.get('text', 'Unknown'))
                tid = t.get('id', t.get('value', 0))
                type_ = t.get('type', 'unknown')
                
                if type_ == 'team':
                    print(f"   - Found Team: {name} (ID: {tid})")
                    if scraper._team_name_match(name, team):
                        print(f"     ✅ MATCHED!")
                        found = True
                elif type_ == 'match':
                    print(f"   - Found Match: {t}")
            
            if not found:
                print("   ❌ No match found.")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_search()
