import pandas as pd
import os
from datetime import datetime
import argparse

LEDGER_FILE = "betting_ledger.csv"

class LedgerManager:
    def __init__(self, ledger_file=LEDGER_FILE):
        self.ledger_file = ledger_file
        self.columns = [
            "Date", "Match", "League", "Selection", "Market_Odds", "True_Odds", 
            "Stake", "Confidence", "System_Edge", "Model_Home_Prob", "Model_Away_Prob",
            "Result", "Profit_Loss", "Status", "Notes"
        ]
        self._load_ledger()

    def _load_ledger(self):
        if os.path.exists(self.ledger_file):
            self.df = pd.read_csv(self.ledger_file)
            # Ensure new columns exist if loading old file
            for col in self.columns:
                if col not in self.df.columns:
                    self.df[col] = 0.0 if "Prob" in col or "Odds" in col else ""
        else:
            self.df = pd.DataFrame(columns=self.columns)

    def add_bet(self, match, league, selection, market_odds, true_odds, stake, confidence, edge, home_prob, away_prob, notes=""):
        """Adds a new bet to the ledger."""
        new_row = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Match": match,
            "League": league,
            "Selection": selection,
            "Market_Odds": float(market_odds),
            "True_Odds": float(true_odds),
            "Stake": float(stake),
            "Confidence": confidence,
            "System_Edge": edge,
            "Model_Home_Prob": float(home_prob),
            "Model_Away_Prob": float(away_prob),
            "Result": "Pending",
            "Profit_Loss": 0.0,
            "Status": "Pending",
            "Notes": notes
        }
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        self.save()
        print(f"✅ Bet added: {match} - {selection} @ {market_odds} (True: {true_odds})")

    def update_result(self, match_index, result_status):
        """
        Updates the result of a bet.
        result_status: 'Win', 'Loss', 'Push', 'Half Win', 'Half Loss'
        """
        if match_index >= len(self.df):
            print("❌ Invalid Match Index")
            return

        row = self.df.iloc[match_index]
        stake = float(row["Stake"])
        odds = float(row["Odds"])
        
        pl = 0.0
        if result_status == "Win":
            pl = stake * (odds - 1)
        elif result_status == "Loss":
            pl = -stake
        elif result_status == "Push":
            pl = 0.0
        elif result_status == "Half Win":
            pl = (stake / 2) * (odds - 1)
        elif result_status == "Half Loss":
            pl = -(stake / 2)
            
        self.df.at[match_index, "Result"] = result_status
        self.df.at[match_index, "Profit_Loss"] = round(pl, 2)
        self.df.at[match_index, "Status"] = "Settled"
        
        self.save()
        print(f"✅ Bet updated: {row['Match']} -> {result_status} (P/L: {pl})")

    def show_ledger(self):
        print("\n--- Betting Ledger ---")
        if self.df.empty:
            print("No bets recorded.")
        else:
            print(self.df.to_string())
            
        # Stats
        settled = self.df[self.df["Status"] == "Settled"]
        if not settled.empty:
            total_pl = settled["Profit_Loss"].sum()
            total_stake = settled["Stake"].sum()
            roi = (total_pl / total_stake) * 100 if total_stake > 0 else 0
            print(f"\n💰 Total P/L: {total_pl:.2f}")
            print(f"📈 ROI: {roi:.2f}%")
            print(f"✅ Win Rate: {(len(settled[settled['Result'] == 'Win']) / len(settled)) * 100:.1f}%")

    def save(self):
        self.df.to_csv(self.ledger_file, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["add", "update", "view"], required=True)
    parser.add_argument("--match", help="Match Name (e.g. 'Arsenal vs Chelsea')")
    parser.add_argument("--league", help="League Name")
    parser.add_argument("--selection", help="Bet Selection (e.g. 'Home -0.5')")
    parser.add_argument("--odds", type=float, help="Market Odds")
    parser.add_argument("--true_odds", type=float, default=0.0, help="System True Odds")
    parser.add_argument("--stake", type=float, default=1.0, help="Stake Unit")
    parser.add_argument("--confidence", help="System Confidence")
    parser.add_argument("--edge", help="Calculated Edge")
    parser.add_argument("--home_prob", type=float, default=0.0, help="Model Home Probability")
    parser.add_argument("--away_prob", type=float, default=0.0, help="Model Away Probability")
    parser.add_argument("--index", type=int, help="Row Index for Update")
    parser.add_argument("--result", choices=["Win", "Loss", "Push", "Half Win", "Half Loss"], help="Result Status")
    
    args = parser.parse_args()
    
    manager = LedgerManager()
    
    if args.action == "add":
        manager.add_bet(
            args.match, args.league, args.selection, args.odds, args.true_odds, 
            args.stake, args.confidence, args.edge, args.home_prob, args.away_prob
        )
    elif args.action == "update":
        if args.index is not None and args.result:
            manager.update_result(args.index, args.result)
        else:
            print("❌ Provide --index and --result for update.")
    elif args.action == "view":
        manager.show_ledger()
