#!/usr/bin/env python3
"""
RECALCULATE ALL YUDOR AH FAIR & FAIR ODDS - USER'S CORRECT METHODOLOGY

Correct methodology:
1. Start with raw_casa, raw_vis from yudor_analysis
2. Get pr_empate (draw %) from consolidated_data
3. Normalize: raw_casa + raw_vis + empate = should be 100%
   - If not 100%, distribute the difference equally to casa/vis
4. Calculate moneyline: 100 / favorite%
5. Find AH line closest to odds 2.0
6. Calculate odds at that line using ±15% per 0.25 step

Example (Real Betis):
- raw_casa: 50, raw_vis: 17, pr_empate: 25
- Sum: 50 + 17 + 25 = 92% (missing 8%)
- Add 4% to each: 54%, 21%, 25% = 100%
- Moneyline: 100/54 = 1.85
- AH -0.75: 1.85 × 1.15 = 2.12 (closest to 2.0)
"""
import os
import sys
import json
from pathlib import Path
from pyairtable import Api

# Load env (navigate up to project root from scripts/production/)
env_file = Path(__file__).parent.parent.parent / '.env'
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
table = base.table("Match Analyses")

ARCHIVED_DIR = Path(__file__).parent.parent.parent / 'archived_analyses'


def calculate_correct_probabilities(raw_casa: float, raw_vis: float, pr_empate: float) -> dict:
    """
    Calculate CORRECT normalized probabilities

    Args:
        raw_casa: Raw home score (e.g., 50)
        raw_vis: Raw away score (e.g., 17)
        pr_empate: Draw probability as percentage or decimal (e.g., 25 or 0.25)

    Returns:
        {'pr_casa_pct': 54.0, 'pr_vis_pct': 21.0, 'pr_empate_pct': 25.0}
    """
    # Convert pr_empate to percentage if it's decimal
    if pr_empate < 1:
        empate_pct = pr_empate * 100
    else:
        empate_pct = pr_empate

    # Current sum
    current_sum = raw_casa + raw_vis + empate_pct

    # Calculate difference from 100
    diff = 100 - current_sum

    # Add difference equally to casa and vis
    pr_casa_pct = raw_casa + (diff / 2)
    pr_vis_pct = raw_vis + (diff / 2)

    return {
        'pr_casa_pct': round(pr_casa_pct, 2),
        'pr_vis_pct': round(pr_vis_pct, 2),
        'pr_empate_pct': round(empate_pct, 2)
    }


def calculate_odds_at_line(fav_prob_pct: float, ah_line: float) -> float:
    """
    Calculate odds at specific AH line

    Formula:
    - Moneyline (at -0.5): 100 / favorite%
    - Each +0.25 step: ×0.85 (easier for underdog)
    - Each -0.25 step: ×1.15 (harder for favorite)
    """
    odd_ml = 100 / fav_prob_pct
    steps = (ah_line + 0.5) / 0.25

    if steps > 0:
        odds = odd_ml * (0.85 ** steps)
    elif steps < 0:
        odds = odd_ml * (1.15 ** abs(steps))
    else:
        odds = odd_ml

    return round(odds, 2)


def find_ah_line_closest_to_2(fav_prob_pct: float) -> tuple:
    """
    Find AH line that gives odds closest to 2.0

    IMPORTANT: We always bet on FAVORITE in normal scenarios.
    - Negative AH: favorite gives goals (harder, higher odds)
    - Zero AH: push on draw (easier, lower odds)

    Returns:
        (ah_line, odds_at_line)

    Example:
        54% favorite → Moneyline 1.85
        - AH -0.5: 1.85 (baseline - favorite gives 0.5 goals)
        - AH -0.25: 1.85 * 0.85 = 1.57 (easier - smaller handicap)
        - AH 0.0: 1.85 * 0.85^2 = 1.34 (easiest - push on draw)
        - AH -0.75: 1.85 * 1.15 = 2.13 (harder - gives 0.75 goals)
    """
    odd_ml = 100 / fav_prob_pct

    best_line = None
    best_odds = None
    best_diff = float('inf')

    # Start from -0.5 (moneyline) and check in both directions
    # Direction 1: Harder handicaps (negative, favorite gives more goals)
    current_line = -0.5
    current_odds = odd_ml
    while current_line >= -3.0:
        diff = abs(current_odds - 2.0)
        if diff < best_diff:
            best_diff = diff
            best_line = current_line
            best_odds = current_odds
        current_line -= 0.25
        current_odds *= 1.15

    # Direction 2: Easier handicaps (AH -0.25 and 0.0)
    # AH -0.25 is 1 step from -0.5 (multiply by 0.85)
    # AH 0.0 is 2 steps from -0.5 (multiply by 0.85^2)
    for steps in [1, 2]:
        current_line = -0.5 + (0.25 * steps)
        current_odds = odd_ml * (0.85 ** steps)
        diff = abs(current_odds - 2.0)
        if diff < best_diff:
            best_diff = diff
            best_line = current_line
            best_odds = current_odds

    return (round(best_line, 2), round(best_odds, 2))


def determine_yudor_ah_team(home_team: str, away_team: str,
                            pr_casa_pct: float, pr_vis_pct: float,
                            ah_line: float) -> str:
    """
    Determine which team to bet on based on AH line

    Logic:
    - Negative AH: Bet on FAVORITE (gives handicap)
    - Positive AH: Bet on UNDERDOG (receives advantage) - FLIP SCENARIO
    - Zero AH: Bet on FAVORITE (even match)

    Returns:
        Team name to bet on
    """
    # Determine favorite
    is_home_favorite = pr_casa_pct > pr_vis_pct
    favorite_team = home_team if is_home_favorite else away_team
    underdog_team = away_team if is_home_favorite else home_team

    # Apply logic based on AH line
    if ah_line < 0:
        # Negative: bet on favorite (gives handicap)
        return favorite_team
    elif ah_line > 0:
        # Positive: bet on underdog (FLIP scenario detected)
        return underdog_team
    else:
        # Zero: bet on favorite (even match)
        return favorite_team


def extract_data_from_archived(match_id: str) -> dict:
    """Extract raw_casa, raw_vis, pr_empate, decision, yudor_ah_fair from archived file"""
    for date_dir in ARCHIVED_DIR.iterdir():
        if not date_dir.is_dir():
            continue

        analysis_file = date_dir / f"{match_id}_analysis.json"
        if analysis_file.exists():
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis = json.load(f)

            # Get raw scores and decision from yudor_analysis
            yudor = analysis.get('yudor_analysis', {})
            raw_casa = yudor.get('raw_casa')
            raw_vis = yudor.get('raw_vis')
            yudor_ah_fair_archived = yudor.get('yudor_ah_fair')  # May have flip logic!
            decision = yudor.get('decision')  # CORE, EXP, FLIP, VETO

            # Get pr_empate from consolidated_data
            cons = analysis.get('consolidated_data', {})
            pr_empate = cons.get('pr_empate') or cons.get('p_empate')

            # Get home/away team names
            match_info = analysis.get('match_info', {})
            home_team = match_info.get('home')
            away_team = match_info.get('away')

            if raw_casa and raw_vis and pr_empate:
                return {
                    'raw_casa': raw_casa,
                    'raw_vis': raw_vis,
                    'pr_empate': pr_empate,
                    'yudor_ah_fair_archived': yudor_ah_fair_archived,
                    'decision': decision,
                    'home_team': home_team,
                    'away_team': away_team
                }

    return None


print("=" * 80)
print("🔧 RECALCULATE ALL YUDOR AH FAIR & FAIR ODDS")
print("=" * 80)
print("\nUsing CORRECT methodology:")
print("  1. Normalize raw_casa + raw_vis + pr_empate = 100%")
print("  2. Find AH line closest to odds 2.0")
print("  3. Calculate fair odds at that line\n")

all_records = table.all()
print(f"✅ Found {len(all_records)} records\n")

updated_count = 0
skipped_count = 0
error_count = 0

for idx, record in enumerate(all_records, 1):
    record_id = record['id']
    fields = record['fields']
    match_id = fields.get('match_id', f'Record #{idx}')

    print(f"[{idx}/{len(all_records)}] {match_id}")

    try:
        # Extract data from archived file
        data = extract_data_from_archived(match_id)

        if not data:
            print(f"   ⚠️  Could not extract data from archived file")
            skipped_count += 1
            continue

        raw_casa = data['raw_casa']
        raw_vis = data['raw_vis']
        pr_empate = data['pr_empate']
        yudor_ah_fair_archived = data.get('yudor_ah_fair_archived')
        decision = data.get('decision')
        home_team = data['home_team']
        away_team = data['away_team']

        # Calculate CORRECT probabilities
        probs = calculate_correct_probabilities(raw_casa, raw_vis, pr_empate)
        pr_casa_pct = probs['pr_casa_pct']
        pr_vis_pct = probs['pr_vis_pct']
        pr_empate_pct = probs['pr_empate_pct']

        print(f"   Raw: {raw_casa} vs {raw_vis}, Draw: {pr_empate_pct}%")
        print(f"   Normalized: {pr_casa_pct}% vs {pr_vis_pct}%, Draw: {pr_empate_pct}%")

        # CRITICAL: For FLIP scenarios, preserve the archived AH line
        # The FLIP logic is complex (R-Score, injuries, etc.) and should not be recalculated here
        if decision == "FLIP" and yudor_ah_fair_archived is not None:
            # Use archived AH line for FLIP scenarios
            ah_fair = yudor_ah_fair_archived
            print(f"   🔄 FLIP scenario detected - using archived AH line: {ah_fair}")
        else:
            # For CORE, EXP, VETO: calculate AH line closest to 2.0 odds
            fav_prob_pct = max(pr_casa_pct, pr_vis_pct)
            ah_fair, _ = find_ah_line_closest_to_2(fav_prob_pct)
            print(f"   Moneyline: {100/fav_prob_pct:.2f} (at -0.5)")

        # Calculate fair odds at the AH line
        fav_prob_pct = max(pr_casa_pct, pr_vis_pct)
        fair_odds = calculate_odds_at_line(fav_prob_pct, ah_fair)

        # Determine which team to bet on based on AH line sign
        ah_team = determine_yudor_ah_team(home_team, away_team, pr_casa_pct, pr_vis_pct, ah_fair)

        print(f"   → AH {ah_fair} ({ah_team}) → Odds {fair_odds}")

        # Get current values
        current_ah = fields.get('Yudor AH Fair')
        current_odds = fields.get('Yudor Fair Odds')
        current_team = fields.get('Yudor AH Team')

        # Check if update needed
        needs_update = False
        if current_ah != ah_fair or current_odds != fair_odds or current_team != ah_team:
            needs_update = True

        if needs_update:
            # Update Airtable (convert to float to ensure proper type)
            try:
                table.update(record_id, {
                    'Yudor AH Fair': float(ah_fair),
                    'Yudor Fair Odds': float(fair_odds),
                    'Yudor AH Team': str(ah_team)
                })
                print(f"   ✅ UPDATED (was: AH {current_ah}, Odds {current_odds})")
                updated_count += 1
            except Exception as update_error:
                print(f"   ❌ Update failed: {str(update_error)[:150]}")
                print(f"      Attempted: AH={ah_fair}, Odds={fair_odds}, Team={ah_team}")
                error_count += 1
        else:
            print(f"   ℹ️  Already correct")
            skipped_count += 1

    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        error_count += 1

# Summary
print("\n" + "=" * 80)
print("📊 RECALCULATION SUMMARY")
print("=" * 80)
print(f"   Total records: {len(all_records)}")
print(f"   ✅ Updated: {updated_count}")
print(f"   ℹ️  Already correct: {skipped_count}")
print(f"   ❌ Errors: {error_count}")
print("=" * 80)

if updated_count > 0:
    print(f"\n✅ Successfully updated {updated_count} records with CORRECT calculations!")
else:
    print(f"\n✅ All records already have correct values!")

sys.exit(0 if error_count == 0 else 1)
