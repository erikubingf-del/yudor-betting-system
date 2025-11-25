#!/usr/bin/env python3
"""
Recalculate AH Fair Lines for all existing consolidated data
using the CORRECT Yudor v5.3 methodology.

This script:
1. Loads all consolidated_data/*.json files
2. Applies correct normalization (surplus/deficit split equally, P_Empate unchanged)
3. Calculates proper AH lines with 0.25 intervals and ±15% odds progression
4. Updates yudor_analysis in analysis_history/*.json files
5. Optionally syncs to Airtable

Usage:
    python3 scripts/recalculate_ah_lines.py
    python3 scripts/recalculate_ah_lines.py --sync-airtable
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

BASE_DIR = Path(__file__).parent.parent
CONSOLIDATED_DIR = BASE_DIR / "consolidated_data"
ANALYSIS_DIR = BASE_DIR / "analysis_history"


def normalize_probabilities(raw_casa: float, raw_vis: float, p_empate: float) -> Tuple[float, float]:
    """
    Normalize probabilities to sum to 100%

    CORRECT YUDOR METHODOLOGY:
    - If sum > 100: Remove surplus equally from both teams
    - If sum < 100: Add deficit equally to both teams
    - P(Empate) ALWAYS stays unchanged

    Args:
        raw_casa: Raw home score
        raw_vis: Raw away score
        p_empate: Draw probability (from odds, NOT modified)

    Returns:
        (adjusted_casa, adjusted_vis)
    """
    soma = raw_casa + raw_vis + p_empate

    if soma > 100:
        # Remove surplus equally from both teams
        surplus = (soma - 100) / 2
        adjusted_casa = raw_casa - surplus
        adjusted_vis = raw_vis - surplus
    elif soma < 100:
        # Add deficit equally to both teams
        deficit = (100 - soma) / 2
        adjusted_casa = raw_casa + deficit
        adjusted_vis = raw_vis + deficit
    else:
        adjusted_casa = raw_casa
        adjusted_vis = raw_vis

    return adjusted_casa, adjusted_vis


def calculate_ah_fair_line(adjusted_casa: float, adjusted_vis: float, p_empate: float) -> Dict:
    """
    Calculate Fair AH Line using 0.25 intervals with ±15% odds progression

    YUDOR METHODOLOGY:
    1. Favorite = max(adjusted_casa, adjusted_vis)
    2. Odd_ML = 100 / Favorite → This is -0.5 AH for favorite
    3. Reference: +0.5 AH = 100 / (Favorite + P_Empate)
    4. Iterate with 0.25 steps:
       - Each -0.25: odds *= 1.15
       - Each +0.25: odds *= 0.85
    5. Target: odds ~2.0 [1.97, 2.03]

    Returns:
        Dict with ah_line, ah_odds, iterations, favorite_side
    """
    favorite_pct = max(adjusted_casa, adjusted_vis)
    underdog_pct = min(adjusted_casa, adjusted_vis)

    # Determine which side is favorite
    home_is_favorite = adjusted_casa > adjusted_vis

    # Calculate Moneyline odds (anchor at -0.5 AH)
    odd_ml = 100 / favorite_pct

    # Start iteration from -0.5 AH
    current_line = -0.5
    current_odds = odd_ml

    target_min = 1.97
    target_max = 2.03

    iterations = []

    # Try going more negative (favorite needs bigger handicap)
    test_line = current_line
    test_odds = current_odds
    closest_line = current_line
    closest_odds = current_odds
    closest_distance = abs(test_odds - 2.0)

    # Go negative first (stronger favorite)
    for i in range(20):
        test_line -= 0.25
        test_odds *= 1.15
        distance = abs(test_odds - 2.0)

        iterations.append({
            "line": test_line,
            "odds": round(test_odds, 3),
            "distance": round(distance, 3)
        })

        if distance < closest_distance:
            closest_distance = distance
            closest_line = test_line
            closest_odds = test_odds

        if target_min <= test_odds <= target_max:
            break

    # If not found, try going positive (weaker favorite/stronger underdog)
    if not (target_min <= closest_odds <= target_max):
        test_line = current_line
        test_odds = current_odds

        for i in range(20):
            test_line += 0.25
            test_odds *= 0.85
            distance = abs(test_odds - 2.0)

            iterations.append({
                "line": test_line,
                "odds": round(test_odds, 3),
                "distance": round(distance, 3)
            })

            if distance < closest_distance:
                closest_distance = distance
                closest_line = test_line
                closest_odds = test_odds

            if target_min <= test_odds <= target_max:
                break

    # Convert line to home team perspective
    if not home_is_favorite:
        # If away is favorite, flip the sign for home team
        final_line = -closest_line
    else:
        final_line = closest_line

    return {
        "ah_line": round(final_line, 2),
        "ah_odds": round(closest_odds, 2),
        "favorite_side": "home" if home_is_favorite else "away",
        "favorite_pct": round(favorite_pct, 2),
        "underdog_pct": round(underdog_pct, 2),
        "iterations_count": len(iterations),
        "in_target_range": target_min <= closest_odds <= target_max,
        "debug_iterations": iterations[:5]  # Keep first 5 for debugging
    }


def recalculate_match(consolidated_file: Path) -> Dict:
    """
    Recalculate AH line for a single match

    Returns:
        Dict with old and new analysis
    """
    with open(consolidated_file, 'r', encoding='utf-8') as f:
        consolidated_data = json.load(f)

    # Extract values
    raw_casa = consolidated_data.get("raw_scores", {}).get("raw_casa", 0)
    raw_vis = consolidated_data.get("raw_scores", {}).get("raw_vis", 0)
    p_empate = consolidated_data.get("p_empate", 25.0)

    match_id = consolidated_data.get("game_id", "unknown")
    match_info = consolidated_data.get("match_info", {})

    # Step 1: Normalize probabilities
    adjusted_casa, adjusted_vis = normalize_probabilities(raw_casa, raw_vis, p_empate)

    # Step 2: Calculate AH line
    ah_result = calculate_ah_fair_line(adjusted_casa, adjusted_vis, p_empate)

    # Step 3: Load existing analysis to get CS_final, R-Score, Decision
    analysis_file = ANALYSIS_DIR / f"{match_id}_analysis.json"

    if analysis_file.exists():
        with open(analysis_file, 'r', encoding='utf-8') as f:
            existing_analysis = json.load(f)

        old_yudor = existing_analysis.get("yudor_analysis", {})

        # Create new yudor_analysis with corrected AH line
        new_yudor = {
            "match_id": match_id,
            "raw_casa": raw_casa,
            "raw_vis": raw_vis,
            "delta": raw_casa - raw_vis,
            "p_empate": p_empate,
            "adjusted_casa": round(adjusted_casa, 2),
            "adjusted_vis": round(adjusted_vis, 2),
            "yudor_ah_fair": ah_result["ah_line"],
            "yudor_ah_odds": ah_result["ah_odds"],
            "pr_casa": round(adjusted_casa / 100, 3),
            "pr_vis": round(adjusted_vis / 100, 3),
            "pr_empate": round(p_empate / 100, 3),
            "cs_final": old_yudor.get("cs_final", 0),
            "tier": old_yudor.get("tier", 0),
            "r_score": old_yudor.get("r_score", 0),
            "decision": old_yudor.get("decision", "VETO"),
            "reasoning": old_yudor.get("reasoning", ""),
            "calculation_method": "corrected_v5.3",
            "recalculated_at": datetime.now().isoformat()
        }

        # Update analysis file
        existing_analysis["yudor_analysis"] = new_yudor

        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(existing_analysis, f, indent=2, ensure_ascii=False)

        return {
            "match_id": match_id,
            "match": f"{match_info.get('home')} vs {match_info.get('away')}",
            "home_team": match_info.get('home'),
            "away_team": match_info.get('away'),
            "league": match_info.get('league'),
            "date": match_info.get('date'),
            "old_ah_line": old_yudor.get("yudor_ah_fair", "N/A"),
            "new_ah_line": new_yudor["yudor_ah_fair"],
            "new_ah_odds": new_yudor["yudor_ah_odds"],
            "decision": new_yudor["decision"],
            "cs_final": new_yudor["cs_final"],
            "r_score": new_yudor["r_score"],
            "tier": new_yudor["tier"],
            "changed": old_yudor.get("yudor_ah_fair") != new_yudor["yudor_ah_fair"],
            "calculation_details": ah_result
        }
    else:
        return {
            "match_id": match_id,
            "error": "Analysis file not found"
        }


def main():
    """Main execution"""
    print("="*80)
    print("🎯 RECALCULATING AH FAIR LINES (Corrected Yudor v5.3 Methodology)")
    print("="*80)
    print()

    # Find all consolidated data files
    consolidated_files = sorted(CONSOLIDATED_DIR.glob("*_consolidated.json"))

    if not consolidated_files:
        print("❌ No consolidated data files found!")
        print(f"   Looking in: {CONSOLIDATED_DIR}")
        sys.exit(1)

    print(f"📋 Found {len(consolidated_files)} matches to recalculate")
    print()

    results = []
    changed_count = 0

    for idx, consolidated_file in enumerate(consolidated_files, 1):
        print(f"[{idx}/{len(consolidated_files)}] {consolidated_file.stem}...", end=" ")

        try:
            result = recalculate_match(consolidated_file)
            results.append(result)

            if result.get("changed"):
                changed_count += 1
                old_line = result.get("old_ah_line", "N/A")
                new_line = result.get("new_ah_line", "N/A")
                print(f"✅ {old_line} → {new_line}")
            else:
                print(f"✓ {result.get('new_ah_line', 'N/A')} (unchanged)")

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "match_id": consolidated_file.stem,
                "error": str(e)
            })

    print()
    print("="*80)
    print("✅ RECALCULATION COMPLETE")
    print("="*80)
    print()
    print(f"📊 SUMMARY:")
    print(f"   Total matches: {len(consolidated_files)}")
    print(f"   Changed AH lines: {changed_count}")
    print(f"   Unchanged: {len(consolidated_files) - changed_count}")
    print()

    # Show matches by decision
    decisions = {}
    for r in results:
        if "error" not in r:
            decision = r.get("decision", "UNKNOWN")
            if decision not in decisions:
                decisions[decision] = []
            decisions[decision].append(r)

    print("📋 BY DECISION:")
    for decision, matches in sorted(decisions.items()):
        print(f"   {decision}: {len(matches)} matches")
        if decision in ["CORE", "EXP"]:
            for m in matches:
                print(f"      • {m['match']} ({m['league']}) - AH: {m['new_ah_line']}, CS: {m['cs_final']}")

    print()

    # Save summary
    summary_file = BASE_DIR / f"recalculation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_matches": len(consolidated_files),
            "changed_count": changed_count,
            "methodology": "corrected_yudor_v5.3",
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"💾 Summary saved to: {summary_file}")

    # Check if Airtable sync requested
    if "--sync-airtable" in sys.argv:
        print()
        print("="*80)
        print("💾 SYNCING TO AIRTABLE")
        print("="*80)
        sync_to_airtable(results)


def sync_to_airtable(results: list):
    """Sync recalculated results to Airtable"""
    try:
        from pyairtable import Api
        import os
        from dotenv import load_dotenv
        from datetime import datetime as dt

        load_dotenv()

        api = Api(os.getenv("AIRTABLE_API_KEY"))
        base = api.base(os.getenv("AIRTABLE_BASE_ID"))
        table = base.table("Match Analyses")

        synced = 0
        errors = 0

        for result in results:
            if "error" in result:
                continue

            # Skip VETO decisions - only sync CORE, EXP, and FLIP
            decision = result.get("decision", "")
            if decision == "VETO":
                continue

            try:
                match_id = result["match_id"]

                # Check if record exists
                existing = table.all(formula=f"{{match_id}}='{match_id}'")

                # Convert date format
                date_str = result.get("date", "")
                try:
                    date_obj = dt.strptime(date_str, "%d/%m/%Y")
                    match_date_formatted = date_obj.strftime("%Y-%m-%d")
                except:
                    match_date_formatted = date_str

                record_data = {
                    "match_id": match_id,
                    "match_date": match_date_formatted,
                    "Home Team": result.get("home_team", ""),
                    "Away Team": result.get("away_team", ""),
                    "League": result.get("league", ""),
                    "Yudor AH Fair": result["new_ah_line"],
                    "Yudor Decision": result["decision"],
                    "CS Final": result["cs_final"],
                    "R Score": result["r_score"],
                    "Tier": result["tier"],
                    "Status": "ANALYZED"
                }

                if existing:
                    table.update(existing[0]['id'], record_data)
                    print(f"   ✅ Updated: {result['match']}")
                    synced += 1
                else:
                    # Create new record
                    table.create(record_data)
                    print(f"   ✅ Created: {result['match']}")
                    synced += 1

            except Exception as e:
                print(f"   ❌ Error syncing {result.get('match')}: {e}")
                errors += 1

        print()
        print(f"✅ Synced {synced} records to Airtable")
        if errors > 0:
            print(f"⚠️  {errors} errors")

    except Exception as e:
        print(f"❌ Airtable sync failed: {e}")


if __name__ == "__main__":
    main()
