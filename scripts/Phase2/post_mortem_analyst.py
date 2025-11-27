import pandas as pd
import json
import os
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
LEDGER_FILE = "betting_ledger.csv"

class PostMortemAnalyst:
    def __init__(self, ledger_file=LEDGER_FILE):
        self.ledger_file = ledger_file
        
    def load_ledger(self):
        if not os.path.exists(self.ledger_file):
            print("❌ Ledger file not found.")
            return None
        return pd.read_csv(self.ledger_file)

    def analyze(self):
        df = self.load_ledger()
        if df is None or df.empty:
            return

        print("\n🔍 Running Post-Mortem Analysis on Settled Bets...")
        
        settled = df[df["Status"] == "Settled"]
        if settled.empty:
            print("   No settled bets to analyze.")
            return

        # 1. General Stats
        total_bets = len(settled)
        wins = len(settled[settled["Result"] == "Win"])
        losses = len(settled[settled["Result"] == "Loss"])
        win_rate = (wins / total_bets) * 100
        total_pl = settled["Profit_Loss"].sum()
        
        print(f"\n📊 Performance Summary:")
        print(f"   Total Bets: {total_bets}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Total P/L: {total_pl:.2f} units")
        
        # 2. Deep Dive: Why did we lose?
        print(f"\n🧐 Loss Analysis (Learning Opportunity):")
        losses_df = settled[settled["Result"] == "Loss"]
        
        for index, row in losses_df.iterrows():
            match_name = row["Match"]
            selection = row["Selection"]
            confidence = row["Confidence"]
            
            print(f"   ❌ {match_name} ({selection})")
            print(f"      Confidence: {confidence} | Edge: {row['System_Edge']}")
            
            # Try to find the match data file to see what the system "thought"
            # We need to reconstruct the path or find it. 
            # Since the ledger doesn't store the file path (yet), we might need to search.
            # For now, we just highlight the discrepancy.
            
            if confidence == "High":
                print("      ⚠️ CRITICAL: High Confidence Loss. Needs Review.")
                print("      Possible Causes: Red Card? Injury? Model Overconfidence?")
            else:
                print("      ℹ️ Standard Loss (Medium/Low Confidence). Variance likely.")

        # 3. Win Analysis
        print(f"\n✅ Win Analysis (Validation):")
        wins_df = settled[settled["Result"] == "Win"]
        high_conf_wins = wins_df[wins_df["Confidence"] == "High"]
        print(f"   High Confidence Wins: {len(high_conf_wins)}/{len(wins_df)}")
        
        if len(high_conf_wins) > 0:
            print("   🌟 The model is correctly identifying high-probability events.")

if __name__ == "__main__":
    analyst = PostMortemAnalyst()
    analyst.analyze()
