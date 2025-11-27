import os
import sys
import subprocess
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts", "Phase2")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_analysis():
    print("\n--- 🕵️‍♂️ Analyze Match ---")
    league = input("League (default: Brasileirão): ") or "Brasileirão"
    season = input("Season (default: 2025): ") or "2025"
    
    # We can create a temporary matches file or just run for default
    # For simplicity, let's ask for specific match or run batch
    mode = input("Run specific match? (y/n): ").lower()
    
    cmd = ["python3", os.path.join(SCRIPTS_DIR, "phase2_orchestrator.py"), "--league", league, "--season", season]
    
    if mode == 'y':
        home = input("Home Team: ")
        away = input("Away Team: ")
        date = input("Date (DD/MM/YYYY): ")
        # Create a temp file
        temp_file = os.path.join(SCRIPTS_DIR, "temp_single_match.txt")
        with open(temp_file, "w") as f:
            f.write(f"{home} vs {away}, {league}, {date}")
        cmd.extend(["--input", temp_file])
    else:
        # Run batch
        batch_file = os.path.join(SCRIPTS_DIR, "matches_batch.txt")
        if os.path.exists(batch_file):
            print(f"Using batch file: {batch_file}")
            cmd.extend(["--input", batch_file])
        else:
            print("No batch file found. Running default demo.")
            
    print("\n🚀 Running Analysis... (This may take a minute)")
    subprocess.run(cmd)
    input("\nPress Enter to continue...")

def log_bet():
    print("\n--- 📝 Log New Bet ---")
    match = input("Match (e.g. Arsenal vs Chelsea): ")
    league = input("League: ")
    selection = input("Selection (e.g. Home -0.5): ")
    market_odds = input("Market Odds: ")
    true_odds = input("True Odds (from System): ")
    stake = input("Stake (Units): ") or "1.0"
    confidence = input("Confidence (High/Medium/Low): ")
    edge = input("Edge (%): ")
    home_prob = input("Model Home Prob (%): ") or "0"
    away_prob = input("Model Away Prob (%): ") or "0"
    
    cmd = [
        "python3", os.path.join(SCRIPTS_DIR, "ledger_manager.py"),
        "--action", "add",
        "--match", match,
        "--league", league,
        "--selection", selection,
        "--odds", market_odds,
        "--true_odds", true_odds,
        "--stake", stake,
        "--confidence", confidence,
        "--edge", edge,
        "--home_prob", home_prob,
        "--away_prob", away_prob
    ]
    subprocess.run(cmd)
    input("\nPress Enter to continue...")

def update_results():
    print("\n--- ⚖️ Update Results ---")
    # First view the ledger to see indices
    subprocess.run(["python3", os.path.join(SCRIPTS_DIR, "ledger_manager.py"), "--action", "view"])
    
    index = input("\nEnter Bet Index to Update (Row Number): ")
    if not index.isdigit(): return
    
    print("Result Options: Win, Loss, Push, Half Win, Half Loss")
    result = input("Result: ")
    
    cmd = [
        "python3", os.path.join(SCRIPTS_DIR, "ledger_manager.py"),
        "--action", "update",
        "--index", index,
        "--result", result
    ]
    subprocess.run(cmd)
    input("\nPress Enter to continue...")

def view_stats():
    print("\n--- 📊 Statistics ---")
    subprocess.run(["python3", os.path.join(SCRIPTS_DIR, "ledger_manager.py"), "--action", "view"])
    input("\nPress Enter to continue...")

def run_post_mortem():
    print("\n--- 🧠 Post-Mortem Analysis ---")
    subprocess.run(["python3", os.path.join(SCRIPTS_DIR, "post_mortem_analyst.py")])
    input("\nPress Enter to continue...")

def main_menu():
    while True:
        clear_screen()
        print("==========================================")
        print("   🤖 YUDOR BETTING SYSTEM - DASHBOARD   ")
        print("==========================================")
        print("1. 🕵️‍♂️  Analyze Match (Orchestrator)")
        print("2. 📝  Log Bet (Ledger)")
        print("3. ⚖️   Update Results (Settle Bets)")
        print("4. 📊  View Ledger & Stats")
        print("5. 🧠  Run Post-Mortem (Learning)")
        print("6. 🚪  Exit")
        print("==========================================")
        
        choice = input("Select Option: ")
        
        if choice == "1":
            run_analysis()
        elif choice == "2":
            log_bet()
        elif choice == "3":
            update_results()
        elif choice == "4":
            view_stats()
        elif choice == "5":
            run_post_mortem()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            input("Invalid option. Press Enter...")

if __name__ == "__main__":
    main_menu()
