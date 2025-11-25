#!/usr/bin/env python3
"""
Recalculate Yudor Fair Odds - Using CORRECT methodology

This script:
1. Reads probability data from Full Analysis JSON
2. Applies the CORRECT Yudor Fair Odds calculation
3. Populates Q1-Q19 Scores where available
4. Updates all existing Airtable records

CORRECT METHODOLOGY:
- Calculate favorite probability
- odd_ml = 100 / fav_prob
- Generate AH lines with ±15% per 0.25 step
- Find line closest to odds 2.0
- Return THAT line and THOSE odds (varies: 1.95, 2.05, 2.15, etc.)
"""
import os
import sys
import json
from pathlib import Path
from pyairtable import Api
from datetime import datetime

# Load env manually
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

api_key = os.getenv('AIRTABLE_API_KEY')
base_id = os.getenv('AIRTABLE_BASE_ID')

if not api_key or not base_id:
    print("❌ Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID")
    sys.exit(1)

api = Api(api_key)
base = api.base(base_id)


def calculate_ah_fair_odds_correct(pr_casa: float, pr_vis: float, pr_empate: float) -> dict:
    """
    Calculate AH Fair Odds using CORRECT YUDOR methodology

    Steps:
    1. Convert decimal probabilities to percentages (0.362 → 36.2%)
    2. Determine favorite (higher probability)
    3. odd_ml = 100 / favorite_percentage
    4. Generate AH lines from -3.0 to +3.0 with ±15% per 0.25 step
    5. Find line closest to odds 2.0
    6. Return that line AND those odds

    Args:
        pr_casa: Home probability as DECIMAL (0.362)
        pr_vis: Away probability as DECIMAL (0.455)
        pr_empate: Draw probability as DECIMAL (0.303)

    Returns:
        {
            'favorite_side': 'HOME' or 'AWAY',
            'fair_line': -0.25,
            'fair_odd': 2.05,  # Actual odds at that line
            'odd_ml': 2.76
        }
    """
    # Convert to percentages (CRITICAL: pr_casa is 0.362, we need 36.2)
    pr_casa_pct = pr_casa * 100
    pr_vis_pct = pr_vis * 100
    pr_empate_pct = pr_empate * 100

    # Determine favorite
    fav_prob_pct = max(pr_casa_pct, pr_vis_pct)
    fav_side = "HOME" if pr_casa_pct > pr_vis_pct else "AWAY"

    # Moneyline odds (using percentage, not decimal)
    odd_ml = 100 / fav_prob_pct

    # Generate all AH lines
    ah_lines = []

    # Negative lines (favorite gives handicap)
    current_line = -0.5
    current_odd = odd_ml
    while current_line >= -3.0:
        ah_lines.append({
            'line': current_line,
            'odd': round(current_odd, 2),
            'side': fav_side
        })
        current_line -= 0.25
        current_odd *= 1.15  # Each 0.25 step adds 15%

    # Positive lines (favorite receives handicap)
    current_line = -0.25
    current_odd = odd_ml * 0.85  # Each 0.25 step subtracts 15%
    while current_line <= 3.0:
        ah_lines.append({
            'line': current_line,
            'odd': round(current_odd, 2),
            'side': fav_side
        })
        current_line += 0.25
        current_odd *= 0.85

    # Sort by line
    ah_lines.sort(key=lambda x: x['line'])

    # Find line closest to odds 2.0
    fair_line = min(ah_lines, key=lambda x: abs(x['odd'] - 2.0))

    return {
        'favorite_side': fav_side,
        'fair_line': fair_line['line'],
        'fair_odd': fair_line['odd'],
        'odd_ml': round(odd_ml, 2)
    }


def extract_q_scores(analysis: dict) -> str:
    """
    Extract Q1-Q19 scores from analysis JSON

    Tries multiple locations:
    1. consolidated_data.q_scores
    2. q_scores (direct)
    3. Returns empty if not found
    """
    q1_q19_scores = ""

    # Try consolidated_data
    if "consolidated_data" in analysis:
        consolidated = analysis["consolidated_data"]
        if "q_scores" in consolidated:
            q_scores = consolidated["q_scores"]
            q_lines = []
            for q_id in sorted(q_scores.keys()):
                q_data = q_scores[q_id]
                if isinstance(q_data, dict):
                    home = q_data.get("home_score", 0)
                    away = q_data.get("away_score", 0)
                    q_lines.append(f"{q_id}: {home} vs {away}")
            if q_lines:
                q1_q19_scores = "\n".join(q_lines)

    # Try direct q_scores
    if not q1_q19_scores and "q_scores" in analysis:
        q_scores = analysis["q_scores"]
        q_lines = []
        for q_id in sorted(q_scores.keys()):
            q_data = q_scores[q_id]
            if isinstance(q_data, dict):
                home = q_data.get("home_score", 0)
                away = q_data.get("away_score", 0)
                q_lines.append(f"{q_id}: {home} vs {away}")
        if q_lines:
            q1_q19_scores = "\n".join(q_lines)

    return q1_q19_scores


print("=" * 80)
print("🔧 RECALCULATE YUDOR FAIR ODDS - CORRECT METHODOLOGY")
print("=" * 80)

# Get all Match Analyses records
table = base.table("Match Analyses")
all_records = table.all()

print(f"\n✅ Found {len(all_records)} records in Match Analyses table")
print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

updated_count = 0
skipped_count = 0
error_count = 0
q_scores_added = 0
q_scores_missing = 0

for idx, record in enumerate(all_records, 1):
    record_id = record['id']
    fields = record['fields']
    match_id = fields.get('match_id', f'Record #{idx}')

    print(f"\n[{idx}/{len(all_records)}] Processing: {match_id}")

    try:
        # Extract Full Analysis JSON
        full_analysis_json = fields.get('Full Analysis', '')
        if not full_analysis_json:
            print(f"   ⚠️  No Full Analysis data - skipping")
            skipped_count += 1
            continue

        try:
            analysis = json.loads(full_analysis_json)
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON in Full Analysis - skipping")
            error_count += 1
            continue

        updates = {}

        # 1. RECALCULATE YUDOR FAIR ODDS (CORRECT METHOD)
        pr_casa = analysis.get('pr_casa', 0)
        pr_vis = analysis.get('pr_vis', 0)
        pr_empate = analysis.get('pr_empate', 0)

        if pr_casa and pr_vis and pr_empate:
            # Calculate using CORRECT methodology
            ah_result = calculate_ah_fair_odds_correct(pr_casa, pr_vis, pr_empate)

            # Get current values for comparison
            current_odds = fields.get('Yudor Fair Odds', 0)
            current_line = fields.get('Yudor AH Fair', 0)

            # Update Yudor Fair Odds with CORRECT value
            new_odds = ah_result['fair_odd']
            if current_odds != new_odds:
                updates['Yudor Fair Odds'] = new_odds
                print(f"   ✅ Yudor Fair Odds: {current_odds} → {new_odds} (CORRECTED)")
            else:
                print(f"   ℹ️  Yudor Fair Odds: {new_odds} (already correct)")

            # Verify AH line matches (should already be correct)
            stored_line = float(current_line) if current_line else 0
            calculated_line = ah_result['fair_line']
            if abs(stored_line - calculated_line) > 0.01:
                print(f"   ⚠️  AH Line mismatch: stored={stored_line}, calculated={calculated_line}")

            # Update Yudor AH Team if missing
            if not fields.get('Yudor AH Team'):
                home_team = fields.get('Home Team', '')
                away_team = fields.get('Away Team', '')
                yudor_ah_team = home_team if ah_result['favorite_side'] == 'HOME' else away_team
                updates['Yudor AH Team'] = yudor_ah_team
                print(f"   ✅ Yudor AH Team: {yudor_ah_team}")

        else:
            print(f"   ⚠️  Missing probability data (pr_casa, pr_vis, pr_empate)")

        # 2. POPULATE Q1-Q19 SCORES
        if not fields.get('Q1-Q19 Scores'):
            q1_q19_scores = extract_q_scores(analysis)

            if q1_q19_scores:
                updates['Q1-Q19 Scores'] = q1_q19_scores
                num_qs = len(q1_q19_scores.split('\n'))
                print(f"   ✅ Q1-Q19 Scores: Added {num_qs} questions")
                q_scores_added += 1
            else:
                print(f"   ⚠️  Q1-Q19 Scores: Not found in analysis JSON")
                q_scores_missing += 1
        else:
            print(f"   ℹ️  Q1-Q19 Scores: Already populated")

        # Update record if needed
        if updates:
            table.update(record_id, updates)
            updated_count += 1
            print(f"   ✅ Updated {len(updates)} fields")
        else:
            print(f"   ℹ️  No updates needed")
            skipped_count += 1

    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        error_count += 1
        import traceback
        traceback.print_exc()
        continue

# Summary
print("\n" + "=" * 80)
print("📊 RECALCULATION SUMMARY")
print("=" * 80)
print(f"   Total records: {len(all_records)}")
print(f"   ✅ Updated: {updated_count}")
print(f"   ℹ️  Skipped (no changes): {skipped_count}")
print(f"   ❌ Errors: {error_count}")
print(f"\n   Q1-Q19 Scores:")
print(f"      ✅ Added: {q_scores_added}")
print(f"      ⚠️  Missing: {q_scores_missing}")
print(f"\n🕐 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
print("\n💡 NOTE: Yudor Fair Odds variety (1.95, 2.05, 2.15, etc.) is EXPECTED")
print("   Each match has different probabilities, so the line closest to 2.0 varies.")
print("   This is the CORRECT methodology!")
print("=" * 80)

sys.exit(0 if error_count == 0 else 1)
