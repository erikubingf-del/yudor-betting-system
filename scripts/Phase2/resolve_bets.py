import csv
import os
import sys
import time
from datetime import datetime
import pandas as pd

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.Phase2.api_football_collector import APIFootballCollector

class BetResolver:
    def __init__(self):
        self.ledger_path = "betting_ledger.csv"
        self.api = APIFootballCollector()
        
    def resolve_ah_bet(self, selection_str, home_score, away_score, odds):
        """
        Calculates the result of an Asian Handicap bet.
        Returns: Result String, Profit Unit (Multiplier of Stake)
        """
        try:
            line = float(selection_str.replace("AH ", ""))
        except:
            return "ERROR", 0.0

        # Calculate score difference from Home perspective
        diff = (home_score + line) - away_score
        
        # Profit Calculation based on Odds
        # Win: (Odds - 1)
        # Loss: -1
        # Half Win: (Odds - 1) / 2
        # Half Loss: -0.5
        
        profit_win = odds - 1.0
        
        # Simple Lines (.0, .5)
        if diff > 0: return "WIN", profit_win
        if diff < 0: return "LOSS", -1.0
        if diff == 0: return "PUSH", 0.0
        
        # Quarter Lines
        if abs(diff) == 0.25:
            if diff > 0: return "HALF WIN", profit_win / 2
            else: return "HALF LOSS", -0.5
            
        return "ERROR", 0.0

    def process_ledger(self):
        if not os.path.exists(self.ledger_path):
            print("❌ Ledger not found.")
            return

        # Read Ledger
        df = pd.read_csv(self.ledger_path)
        
        pending_mask = df['Status'] == 'PENDING'
        if not pending_mask.any():
            print("✅ No pending bets to resolve.")
            return

        print(f"🔄 Resolving {pending_mask.sum()} pending bets...")
        
        for index, row in df[pending_mask].iterrows():
            match_name = row['Match']
            date_str = row['Date']
            selection = row['Selection']
            
            print(f"  🔎 Checking {match_name} ({date_str})...")
            
            # Parse Teams
            try:
                home, away = match_name.split(" vs ")
            except:
                print("    ⚠️ Invalid match name format.")
                continue
                
            # Fetch Result from API
            # We need Fixture ID or search by names/date
            # APIFootballCollector has get_fixture_id
            
            # Note: Date in ledger might be YYYY-MM-DD
            fixture_id = self.api.get_fixture_id(home, away, date_str)
            
            if not fixture_id:
                print("    ❌ Fixture not found in API.")
                continue
                
            # Get Fixture Details (Score)
            # We need a method to get score. 
            # APIFootballCollector doesn't have a direct "get_score" but we can use "fixtures" endpoint with ID.
            
            url = f"https://v3.football.api-sports.io/fixtures?id={fixture_id}"
            resp = self.api._make_request(url) # Need to expose _make_request or use requests directly
            # Actually, let's just use requests here for simplicity or add method to collector.
            # I'll add get_match_result to collector later. For now, use requests.
            
            import requests
            headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': self.api.api_key}
            resp = requests.get(url, headers=headers).json()
            
            if not resp.get("response"):
                print("    ❌ No response for fixture.")
                continue
                
            fixture = resp["response"][0]
            status = fixture["fixture"]["status"]["short"]
            
            if status not in ["FT", "AET", "PEN"]:
                print(f"    ⏳ Match not finished (Status: {status})")
                continue
                
            score_home = fixture["goals"]["home"]
            score_away = fixture["goals"]["away"]
            
            print(f"    ⚽ Final Score: {home} {score_home} - {score_away} {away}")
            
            # --- NEW: Collect Post-Match Stats for Learning ---
            stats = {}
            try:
                stats_resp = fixture.get("statistics", [])
                # API-Football returns stats as a list of 2 dicts (one per team)
                for team_stat in stats_resp:
                    team_name = team_stat["team"]["name"]
                    is_home_team = (team_name == home) # Simple check
                    prefix = "home" if is_home_team else "away"
                    
                    for stat_item in team_stat["statistics"]:
                        type_name = stat_item["type"].lower().replace(" ", "_")
                        value = stat_item["value"]
                        stats[f"{prefix}_{type_name}"] = value
                        
                print(f"    📊 Stats Collected: {len(stats)} items")
            except Exception as e:
                print(f"    ⚠️ Could not collect stats: {e}")

            # Resolve Bet
            # Use Market Odds from CSV (User might have updated it)
            try:
                market_odds = float(row['Market_Odds'])
            except:
                market_odds = 1.90 # Default fallback
                
            result, profit_unit = self.resolve_ah_bet(selection, score_home, score_away, market_odds)
            
            # Update Row
            df.at[index, 'Result'] = result
            df.at[index, 'Profit_Loss'] = profit_unit * float(row['Stake'])
            df.at[index, 'Status'] = "RESOLVED"
            df.at[index, 'Notes'] = f"Score: {score_home}-{score_away}"
            
            # --- NEW: Update JSON Data File ---
            # Reconstruct filename: YYYY-MM-DD_Home_vs_Away.json
            try:
                # Convert date format if needed (Ledger has YYYY-MM-DD or DD/MM/YYYY)
                # Assuming YYYY-MM-DD from orchestrator
                safe_date = date_str.replace("/", "-")
                safe_home = home.replace(" ", "_")
                safe_away = away.replace(" ", "_")
                safe_league = row['League'].replace(" ", "_")
                # Season? Ledger doesn't have season. Assume current year or infer.
                # We'll search recursively in data/matches
                
                filename = f"{safe_date}_{safe_home}_vs_{safe_away}.json"
                found_path = None
                
                # Search for file
                import glob
                search_pattern = f"data/matches/**/{filename}"
                matches_found = glob.glob(search_pattern, recursive=True)
                
                if matches_found:
                    found_path = matches_found[0]
                    import json
                    with open(found_path, 'r') as f:
                        data = json.load(f)
                    
                    # Update with Result and Stats
                    data["result"] = {
                        "score_home": score_home,
                        "score_away": score_away,
                        "outcome": result,
                        "stats": stats
                    }
                    
                    with open(found_path, 'w') as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    print(f"    💾 Updated Training Data: {found_path}")
                else:
                    print(f"    ⚠️ Training Data File not found: {filename}")
                    
            except Exception as e:
                print(f"    ⚠️ Error updating JSON: {e}")

            print(f"    ✅ Bet Resolved: {result} (P/L: {df.at[index, 'Profit_Loss']})")
            
        # Save back to CSV
        df.to_csv(self.ledger_path, index=False)
        print("💾 Ledger updated.")

if __name__ == "__main__":
    resolver = BetResolver()
    resolver.process_ledger()
