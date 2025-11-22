#!/usr/bin/env python3
"""
Yudor v5.3 - Unified Command Line Interface
Interactive menu for all betting system operations
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent

def print_header():
    """Print system header"""
    print("\n" + "="*80)
    print("⚽ YUDOR v5.3 - BETTING SYSTEM")
    print("="*80)
    print()

def print_menu():
    """Print main menu"""
    print("📋 MAIN MENU")
    print("-" * 80)
    print()
    print("🔄 DAILY WORKFLOW:")
    print("  1. Scrape Match Data")
    print("  2. Run Analysis (Batch)")
    print("  3. Sync to Airtable")
    print("  4. Archive Files")
    print("  5. ⚡ RUN ALL (Scrape → Analyze → Sync → Archive)")
    print()
    print("🤖 MACHINE LEARNING:")
    print("  6. Post-Match Analysis (Update Statistics)")
    print("  7. ML Calibration (After 30+ Losses)")
    print()
    print("🔍 UTILITIES:")
    print("  8. View Results Summary")
    print("  9. Recalculate AH Lines")
    print("  10. Clean Up Temp Files")
    print()
    print("📊 QUICK STATS:")
    print("  11. Count Decisions")
    print("  12. View Match Analysis")
    print()
    print("  0. Exit")
    print()
    print("-" * 80)

def run_scraper():
    """Run scraper"""
    print("\n" + "="*80)
    print("🌐 SCRAPING MATCH DATA")
    print("="*80)
    print()

    matches_file = input("Match list file [matches_all.txt]: ").strip() or "matches_all.txt"

    if not (BASE_DIR / matches_file).exists():
        print(f"❌ Error: {matches_file} not found")
        return

    date_str = datetime.now().strftime("%Y%m%d")
    output_file = f"match_data_v{date_str}.json"

    print(f"\n📂 Input: {matches_file}")
    print(f"💾 Output: {output_file}")
    print()

    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled")
        return

    cmd = f"python3 scripts/scraper.py --input {matches_file} --output {output_file}"
    subprocess.run(cmd, shell=True, cwd=BASE_DIR)

def run_analysis():
    """Run analysis"""
    print("\n" + "="*80)
    print("🎯 RUNNING YUDOR v5.3 ANALYSIS")
    print("="*80)
    print()

    matches_file = input("Match list file [matches_all.txt]: ").strip() or "matches_all.txt"

    if not (BASE_DIR / matches_file).exists():
        print(f"❌ Error: {matches_file} not found")
        return

    print(f"\n📂 Input: {matches_file}")
    print("⏱️  Duration: ~1-2 min per match")
    print()

    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled")
        return

    cmd = f"python3 scripts/master_orchestrator.py analyze-batch --input {matches_file}"
    subprocess.run(cmd, shell=True, cwd=BASE_DIR)

def run_sync():
    """Sync to Airtable"""
    print("\n" + "="*80)
    print("📤 SYNCING TO AIRTABLE")
    print("="*80)
    print()
    print("Syncing: CORE, EXP, FLIP (skipping VETO)")
    print()

    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled")
        return

    cmd = "python3 scripts/sync_all_betting_opportunities.py"
    subprocess.run(cmd, shell=True, cwd=BASE_DIR)

def run_archive():
    """Archive files"""
    print("\n" + "="*80)
    print("📦 ARCHIVING FILES")
    print("="*80)
    print()
    print("Moving files to: archived_analyses/YYYY-MM-DD/")
    print()

    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled")
        return

    cmd = "python3 scripts/organize_analyses.py"
    subprocess.run(cmd, shell=True, cwd=BASE_DIR)

def run_all():
    """Run complete workflow"""
    print("\n" + "="*80)
    print("⚡ RUNNING COMPLETE WORKFLOW")
    print("="*80)
    print()
    print("Steps: Scrape → Analyze → Sync → Archive")
    print()

    matches_file = input("Match list file [matches_all.txt]: ").strip() or "matches_all.txt"

    if not (BASE_DIR / matches_file).exists():
        print(f"❌ Error: {matches_file} not found")
        return

    print()
    confirm = input("⚠️  This will run the complete workflow. Continue? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled")
        return

    date_str = datetime.now().strftime("%Y%m%d")
    output_file = f"match_data_v{date_str}.json"

    # Step 1: Scrape
    print("\n" + "="*80)
    print("STEP 1/4: SCRAPING")
    print("="*80)
    cmd = f"python3 scripts/scraper.py --input {matches_file} --output {output_file}"
    subprocess.run(cmd, shell=True, cwd=BASE_DIR)

    # Step 2: Analyze
    print("\n" + "="*80)
    print("STEP 2/4: ANALYZING")
    print("="*80)
    cmd = f"python3 scripts/master_orchestrator.py analyze-batch --input {matches_file}"
    subprocess.run(cmd, shell=True, cwd=BASE_DIR)

    # Step 3: Sync
    print("\n" + "="*80)
    print("STEP 3/4: SYNCING")
    print("="*80)
    cmd = "python3 scripts/sync_all_betting_opportunities.py"
    subprocess.run(cmd, shell=True, cwd=BASE_DIR)

    # Step 4: Archive
    print("\n" + "="*80)
    print("STEP 4/4: ARCHIVING")
    print("="*80)
    cmd = "python3 scripts/organize_analyses.py"
    subprocess.run(cmd, shell=True, cwd=BASE_DIR)

    print("\n" + "="*80)
    print("✅ COMPLETE WORKFLOW FINISHED")
    print("="*80)

def run_post_match():
    """Run post-match analysis"""
    print("\n" + "="*80)
    print("📊 POST-MATCH ANALYSIS")
    print("="*80)
    print()
    print("Fetching results from Airtable and calculating statistics...")
    print()

    cmd = "python3 scripts/post_match_analysis.py"
    subprocess.run(cmd, shell=True, cwd=BASE_DIR)

def run_ml_calibration():
    """Run ML calibration"""
    print("\n" + "="*80)
    print("🤖 ML CALIBRATION")
    print("="*80)
    print()
    print("⚠️  Requirements:")
    print("   - Minimum 100 total matches")
    print("   - Minimum 30 losses")
    print()

    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled")
        return

    cmd = "python3 scripts/ml_calibration.py"
    subprocess.run(cmd, shell=True, cwd=BASE_DIR)

def view_results():
    """View results summary"""
    print("\n" + "="*80)
    print("📊 RESULTS SUMMARY")
    print("="*80)
    print()

    results_file = BASE_DIR / "match_results.json"
    ledger_file = BASE_DIR / "loss_ledger.json"

    if results_file.exists():
        import json
        with open(results_file, 'r') as f:
            data = json.load(f)
            stats = data.get("statistics", {})

            print("MATCH RESULTS:")
            print(f"   Total Matches: {stats.get('total_matches', 0)}")
            print()

            by_decision = stats.get("by_decision", {})
            for decision in ["CORE", "EXP", "FLIP"]:
                if decision in by_decision:
                    d = by_decision[decision]
                    print(f"   {decision}:")
                    print(f"      Matches: {d.get('count', 0)}")
                    print(f"      Win Rate: {d.get('win_rate', 0):.1f}%")
                    print(f"      ROI: {d.get('roi', 0):+.1f}%")
                    print()
    else:
        print("⚠️  No results file found. Run post-match analysis first.")
        print()

    if ledger_file.exists():
        import json
        with open(ledger_file, 'r') as f:
            data = json.load(f)
            summary = data.get("summary", {})

            print("LOSS LEDGER:")
            print(f"   Total Losses: {summary.get('total_losses', 0)}")
            print(f"   Total Units Lost: {summary.get('total_units_lost', 0):.2f}")
            print()

            categories = summary.get("by_category", {})
            if categories:
                print("   By Category:")
                for cat, count in categories.items():
                    print(f"      {cat}: {count}")
                print()
    else:
        print("⚠️  No loss ledger found.")
        print()

def recalculate_ah():
    """Recalculate AH lines"""
    print("\n" + "="*80)
    print("🔄 RECALCULATE AH LINES")
    print("="*80)
    print()

    sync = input("Sync to Airtable after recalculation? (yes/no): ").strip().lower()

    if sync == "yes":
        cmd = "python3 scripts/recalculate_ah_lines.py --sync-airtable"
    else:
        cmd = "python3 scripts/recalculate_ah_lines.py"

    subprocess.run(cmd, shell=True, cwd=BASE_DIR)

def cleanup_temp():
    """Clean up temp files"""
    print("\n" + "="*80)
    print("🧹 CLEANING UP TEMP FILES")
    print("="*80)
    print()

    temp_files = list(BASE_DIR.glob("matches_priority.txt")) + \
                 list(BASE_DIR.glob("matches_test*.txt")) + \
                 list(BASE_DIR.glob("matches_remaining_*.txt")) + \
                 list(BASE_DIR.glob("matches_failed_*.txt")) + \
                 list(BASE_DIR.glob("*.log"))

    if not temp_files:
        print("✅ No temp files found")
        return

    print("Files to delete:")
    for f in temp_files:
        print(f"   - {f.name}")
    print()

    confirm = input("Delete these files? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled")
        return

    for f in temp_files:
        f.unlink()
        print(f"   ✅ Deleted: {f.name}")

    print()
    print(f"✅ Cleaned up {len(temp_files)} files")

def count_decisions():
    """Count decisions"""
    print("\n" + "="*80)
    print("📊 DECISION COUNT")
    print("="*80)
    print()

    analysis_dir = BASE_DIR / "analysis_history"

    if not analysis_dir.exists():
        print("❌ No analysis_history folder found")
        return

    cmd = 'grep -r "\"decision\":" analysis_history/*.json 2>/dev/null | grep -o "CORE\\|EXP\\|FLIP\\|VETO" | sort | uniq -c'
    subprocess.run(cmd, shell=True, cwd=BASE_DIR)
    print()

def view_match():
    """View specific match analysis"""
    print("\n" + "="*80)
    print("🔍 VIEW MATCH ANALYSIS")
    print("="*80)
    print()

    match_id = input("Match ID (e.g., BarcelonavsAthleticClub_22112025): ").strip()

    if not match_id:
        print("Cancelled")
        return

    analysis_file = BASE_DIR / "analysis_history" / f"{match_id}_analysis.json"

    if not analysis_file.exists():
        print(f"❌ Analysis file not found: {analysis_file.name}")
        return

    print()
    cmd = f"cat analysis_history/{match_id}_analysis.json | jq '.yudor_analysis'"
    subprocess.run(cmd, shell=True, cwd=BASE_DIR)
    print()

def main():
    """Main menu loop"""
    while True:
        print_header()
        print_menu()

        try:
            choice = input("Select option: ").strip()

            if choice == "0":
                print("\n👋 Goodbye!")
                break
            elif choice == "1":
                run_scraper()
            elif choice == "2":
                run_analysis()
            elif choice == "3":
                run_sync()
            elif choice == "4":
                run_archive()
            elif choice == "5":
                run_all()
            elif choice == "6":
                run_post_match()
            elif choice == "7":
                run_ml_calibration()
            elif choice == "8":
                view_results()
            elif choice == "9":
                recalculate_ah()
            elif choice == "10":
                cleanup_temp()
            elif choice == "11":
                count_decisions()
            elif choice == "12":
                view_match()
            else:
                print("\n❌ Invalid option. Please try again.")

            input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
