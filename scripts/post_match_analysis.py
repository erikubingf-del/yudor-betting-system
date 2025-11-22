#!/usr/bin/env python3
"""
Post-Match Analysis - Automated analysis after match results are entered in Airtable
Calculates win rates, edge accuracy, and Q-score performance
"""

import json
import os
from pathlib import Path
from datetime import datetime
from pyairtable import Api
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
ANALYSIS_DIR = BASE_DIR / "analysis_history"
RESULTS_FILE = BASE_DIR / "match_results.json"

def load_results():
    """Load existing match results"""
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"matches": [], "statistics": {}}

def save_results(results):
    """Save match results"""
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def fetch_results_from_airtable():
    """Fetch match results from Airtable"""
    api = Api(os.getenv("AIRTABLE_API_KEY"))
    base = api.base(os.getenv("AIRTABLE_BASE_ID"))
    table = base.table("Match Analyses")

    print("="*80)
    print("📥 FETCHING MATCH RESULTS FROM AIRTABLE")
    print("="*80)
    print()

    # Get all records with results
    all_records = table.all()

    results = []
    for record in all_records:
        fields = record['fields']

        # Skip if no result entered
        if 'Match Result' not in fields or not fields.get('Match Result'):
            continue

        match_id = fields.get('match_id')
        if not match_id:
            continue

        result_entry = {
            "match_id": match_id,
            "home_team": fields.get('Home Team'),
            "away_team": fields.get('Away Team'),
            "match_date": fields.get('match_date'),
            "match_result": fields.get('Match Result'),  # Format: "2-1" or "1-1"
            "bet_result": fields.get('Bet Result'),  # "WIN", "LOSS", "HALF_WIN", "HALF_LOSS", "PUSH"
            "units_won": float(fields.get('Units Won/Lost', 0)),
            "yudor_decision": fields.get('Yudor Decision'),
            "yudor_ah_fair": float(fields.get('Yudor AH Fair', 0)),
            "market_ah": float(fields.get('Market AH', 0)) if fields.get('Market AH') else None,
            "cs_final": int(fields.get('CS Final', 0)),
            "r_score": float(fields.get('R Score', 0)),
            "tier": int(fields.get('Tier', 0)),
            "bet_entered": fields.get('Bet Entered', False)  # True if actually bet
        }

        results.append(result_entry)

    print(f"✅ Fetched {len(results)} matches with results")
    print()

    return results

def calculate_statistics(results):
    """Calculate comprehensive statistics"""

    print("="*80)
    print("📊 CALCULATING STATISTICS")
    print("="*80)
    print()

    stats = {
        "total_matches": len(results),
        "by_decision": defaultdict(lambda: {
            "count": 0,
            "wins": 0,
            "losses": 0,
            "pushes": 0,
            "total_units": 0,
            "win_rate": 0,
            "roi": 0
        }),
        "by_tier": defaultdict(lambda: {
            "count": 0,
            "wins": 0,
            "losses": 0,
            "total_units": 0
        }),
        "edge_accuracy": [],
        "q_score_performance": defaultdict(list),
        "r_score_performance": defaultdict(list)
    }

    for result in results:
        decision = result['yudor_decision']
        tier = result['tier']
        bet_result = result['bet_result']
        units = result['units_won']

        # By decision stats
        stats["by_decision"][decision]["count"] += 1
        stats["by_decision"][decision]["total_units"] += units

        if bet_result in ["WIN", "HALF_WIN"]:
            stats["by_decision"][decision]["wins"] += 1
        elif bet_result in ["LOSS", "HALF_LOSS"]:
            stats["by_decision"][decision]["losses"] += 1
        elif bet_result == "PUSH":
            stats["by_decision"][decision]["pushes"] += 1

        # By tier stats
        stats["by_tier"][tier]["count"] += 1
        stats["by_tier"][tier]["total_units"] += units

        if bet_result in ["WIN", "HALF_WIN"]:
            stats["by_tier"][tier]["wins"] += 1
        elif bet_result in ["LOSS", "HALF_LOSS"]:
            stats["by_tier"][tier]["losses"] += 1

        # Edge accuracy (if market AH available)
        if result['market_ah'] is not None:
            yudor_ah = result['yudor_ah_fair']
            market_ah = result['market_ah']
            edge = abs(yudor_ah - market_ah)

            stats["edge_accuracy"].append({
                "match_id": result['match_id'],
                "yudor_ah": yudor_ah,
                "market_ah": market_ah,
                "edge": edge,
                "won": bet_result in ["WIN", "HALF_WIN"]
            })

        # R-Score performance
        r_score = result['r_score']
        won = bet_result in ["WIN", "HALF_WIN"]

        stats["r_score_performance"][decision].append({
            "r_score": r_score,
            "won": won
        })

    # Calculate win rates and ROI
    for decision, data in stats["by_decision"].items():
        total = data["wins"] + data["losses"]
        if total > 0:
            data["win_rate"] = (data["wins"] / total) * 100
            data["roi"] = (data["total_units"] / data["count"]) * 100

    # Convert defaultdicts to regular dicts for JSON serialization
    stats["by_decision"] = dict(stats["by_decision"])
    stats["by_tier"] = dict(stats["by_tier"])
    stats["r_score_performance"] = dict(stats["r_score_performance"])

    return stats

def print_statistics(stats):
    """Print statistics in readable format"""

    print("="*80)
    print("📈 MATCH RESULTS SUMMARY")
    print("="*80)
    print()

    print(f"Total Matches: {stats['total_matches']}")
    print()

    # By Decision
    print("-"*80)
    print("BY DECISION TYPE:")
    print("-"*80)
    for decision in ["CORE", "EXP", "FLIP", "VETO"]:
        if decision not in stats["by_decision"]:
            continue

        data = stats["by_decision"][decision]
        print(f"\n{decision}:")
        print(f"   Matches: {data['count']}")
        print(f"   Wins: {data['wins']}")
        print(f"   Losses: {data['losses']}")
        print(f"   Pushes: {data['pushes']}")
        print(f"   Win Rate: {data['win_rate']:.1f}%")
        print(f"   Total Units: {data['total_units']:+.2f}")
        print(f"   ROI: {data['roi']:+.1f}%")

    # By Tier
    print()
    print("-"*80)
    print("BY TIER:")
    print("-"*80)
    for tier in [1, 2, 3]:
        if tier not in stats["by_tier"]:
            continue

        data = stats["by_tier"][tier]
        total = data["wins"] + data["losses"]
        win_rate = (data["wins"] / total * 100) if total > 0 else 0

        print(f"\nTier {tier}:")
        print(f"   Matches: {data['count']}")
        print(f"   Wins: {data['wins']}")
        print(f"   Losses: {data['losses']}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Total Units: {data['total_units']:+.2f}")

    # Edge Accuracy
    if stats["edge_accuracy"]:
        print()
        print("-"*80)
        print("EDGE ACCURACY (Yudor vs Market):")
        print("-"*80)

        avg_edge = sum(e["edge"] for e in stats["edge_accuracy"]) / len(stats["edge_accuracy"])
        matches_with_edge = len(stats["edge_accuracy"])

        # Count wins when Yudor had edge vs Market
        yudor_edge_wins = sum(1 for e in stats["edge_accuracy"] if e["won"])
        yudor_edge_win_rate = (yudor_edge_wins / matches_with_edge * 100) if matches_with_edge > 0 else 0

        print(f"\n   Matches with Market AH: {matches_with_edge}")
        print(f"   Average Edge: {avg_edge:.2f} AH points")
        print(f"   Win Rate when edge exists: {yudor_edge_win_rate:.1f}%")

    # R-Score Performance
    print()
    print("-"*80)
    print("R-SCORE PERFORMANCE:")
    print("-"*80)

    for decision in ["CORE", "EXP"]:
        if decision not in stats["r_score_performance"]:
            continue

        performances = stats["r_score_performance"][decision]
        if not performances:
            continue

        avg_r = sum(p["r_score"] for p in performances) / len(performances)
        wins = sum(1 for p in performances if p["won"])
        win_rate = (wins / len(performances) * 100) if performances else 0

        print(f"\n{decision}:")
        print(f"   Average R-Score: {avg_r:.3f}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Sample Size: {len(performances)}")

    print()
    print("="*80)

def update_results():
    """Main function to update results from Airtable"""

    # Fetch from Airtable
    new_results = fetch_results_from_airtable()

    if not new_results:
        print("⚠️  No match results found in Airtable")
        return

    # Calculate statistics
    stats = calculate_statistics(new_results)

    # Print statistics
    print_statistics(stats)

    # Save to file
    output = {
        "last_updated": datetime.now().isoformat(),
        "matches": new_results,
        "statistics": stats
    }

    save_results(output)

    print(f"✅ Results saved to: {RESULTS_FILE}")
    print()

    # Check if ready for ML calibration
    total_losses = sum(
        d["losses"] for d in stats["by_decision"].values()
    )

    if total_losses >= 30:
        print("="*80)
        print("🎯 READY FOR ML CALIBRATION")
        print("="*80)
        print(f"You have {total_losses} losses - enough for machine learning analysis!")
        print()
        print("Run: python3 scripts/ml_calibration.py")
        print()

if __name__ == "__main__":
    update_results()
