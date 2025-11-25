#!/usr/bin/env python3
"""
Fix Yudor Fair Odds - Calculate odds at STORED AH line

This script:
1. Uses the STORED yudor_ah_fair (already correct, calculated by Claude)
2. Uses the STORED probabilities (pr_casa, pr_vis, pr_empate)
3. Calculates the correct odds at that specific AH line

METHODOLOGY (from user's correct understanding):
- Probabilities are normalized: pr_casa + pr_vis + pr_empate = 1.0
- Convert to percentages: 0.362 → 36.2%
- Favorite percentage determines moneyline odds: 100 / 36.2 = 2.76
- At line -0.5, odds = moneyline odds (2.76)
- Each +0.25 step UP in line: multiply odds by 0.85 (easier to cover)
- Each -0.25 step DOWN in line: multiply odds by 1.15 (harder to cover)

Example:
- Favorite: 36.2% → Moneyline = 2.76
- Line -0.5 → Odds 2.76
- Line -0.25 → Odds 2.76 × 0.85 = 2.35
- Line 0.0 → Odds 2.35 × 0.85 = 2.00
- Line +0.25 → Odds 2.00 × 0.85 = 1.70
"""
import os
import sys
import json
from pathlib import Path
from pyairtable import Api
from datetime import datetime

# Load env
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


def calculate_odds_at_line(pr_casa_pct: float, pr_vis_pct: float, ah_line: float) -> float:
    """
    Calculate odds at a specific AH line

    Args:
        pr_casa_pct: Home probability as PERCENTAGE (36.2, not 0.362)
        pr_vis_pct: Away probability as PERCENTAGE (33.5, not 0.335)
        ah_line: Asian Handicap line (-0.25, 0.0, +1.0, etc.)

    Returns:
        Odds at that line (e.g., 2.35)

    Logic:
        1. Determine favorite (higher percentage)
        2. Moneyline odds = 100 / favorite_percentage
        3. At line -0.5: odds = moneyline
        4. For each +0.25 step: multiply by 0.85
        5. For each -0.25 step: multiply by 1.15
    """
    # Determine favorite
    fav_prob_pct = max(pr_casa_pct, pr_vis_pct)

    # Moneyline odds (at line -0.5 for favorite)
    odd_ml = 100 / fav_prob_pct

    # Calculate steps from -0.5 to ah_line
    # ah_line = -0.5 + (steps × 0.25)
    # steps = (ah_line - (-0.5)) / 0.25 = (ah_line + 0.5) / 0.25
    steps = (ah_line + 0.5) / 0.25

    # Apply multipliers: 0.85 per +0.25 step, 1.15 per -0.25 step
    if steps > 0:
        # Positive steps: easier to cover → lower odds
        odds = odd_ml * (0.85 ** steps)
    elif steps < 0:
        # Negative steps: harder to cover → higher odds
        odds = odd_ml * (1.15 ** abs(steps))
    else:
        # Exactly at -0.5
        odds = odd_ml

    return round(odds, 2)


print("=" * 80)
print("🔧 FIX YUDOR FAIR ODDS - CALCULATE AT STORED AH LINE")
print("=" * 80)

# Get all Match Analyses records
table = base.table("Match Analyses")
all_records = table.all()

print(f"\n✅ Found {len(all_records)} records in Match Analyses table")
print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

updated_count = 0
skipped_count = 0
error_count = 0

for idx, record in enumerate(all_records, 1):
    record_id = record['id']
    fields = record['fields']
    match_id = fields.get('match_id', f'Record #{idx}')

    print(f"\n[{idx}/{len(all_records)}] Processing: {match_id}")

    try:
        # Get stored AH line
        ah_line_raw = fields.get('Yudor AH Fair', 0)
        try:
            ah_line = float(ah_line_raw) if ah_line_raw else 0
        except (ValueError, TypeError):
            ah_line = 0

        if ah_line == 0:
            # Special case: AH 0.0 is valid, but empty/None is not
            if ah_line_raw is None or ah_line_raw == '':
                print(f"   ⚠️  No AH line stored - skipping")
                skipped_count += 1
                continue

        # Extract probabilities from Full Analysis JSON
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

        pr_casa = analysis.get('pr_casa', 0)
        pr_vis = analysis.get('pr_vis', 0)
        pr_empate = analysis.get('pr_empate', 0)

        if not pr_casa or not pr_vis or not pr_empate:
            print(f"   ⚠️  Missing probability data - skipping")
            skipped_count += 1
            continue

        # Detect format: decimal (sum ≈ 1.0) or percentage (sum ≈ 100)
        prob_sum = pr_casa + pr_vis + pr_empate

        if prob_sum > 10:
            # Already percentages (23.9, 45.3, 30.8)
            pr_casa_pct = pr_casa
            pr_vis_pct = pr_vis
            pr_empate_pct = pr_empate
        else:
            # Decimals - need to convert (0.335, 0.362, 0.303)
            pr_casa_pct = pr_casa * 100
            pr_vis_pct = pr_vis * 100
            pr_empate_pct = pr_empate * 100

        # Calculate odds at the STORED AH line
        fair_odds = calculate_odds_at_line(pr_casa_pct, pr_vis_pct, ah_line)

        # Get current odds for comparison
        current_odds = fields.get('Yudor Fair Odds', 0)

        # Update if different
        if current_odds != fair_odds:
            table.update(record_id, {'Yudor Fair Odds': fair_odds})
            print(f"   ✅ AH Line: {ah_line:+.2f}")
            print(f"   ✅ Fair Odds: {current_odds} → {fair_odds}")
            print(f"   ℹ️  Probabilities: H={pr_casa_pct:.1f}%, A={pr_vis_pct:.1f}%, D={pr_empate_pct:.1f}%")
            updated_count += 1
        else:
            print(f"   ℹ️  Already correct: {fair_odds} (AH {ah_line:+.2f})")
            skipped_count += 1

    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        error_count += 1
        import traceback
        traceback.print_exc()
        continue

# Summary
print("\n" + "=" * 80)
print("📊 FIX SUMMARY")
print("=" * 80)
print(f"   Total records: {len(all_records)}")
print(f"   ✅ Updated: {updated_count}")
print(f"   ℹ️  Skipped (already correct): {skipped_count}")
print(f"   ❌ Errors: {error_count}")
print(f"\n🕐 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
print("\n💡 METHODOLOGY:")
print("   - Used STORED AH line (calculated by Claude)")
print("   - Used STORED probabilities from analysis")
print("   - Calculated odds at that specific line:")
print("     • Moneyline (at -0.5) = 100 / favorite%")
print("     • Each +0.25 step: ×0.85 (easier)")
print("     • Each -0.25 step: ×1.15 (harder)")
print("=" * 80)

sys.exit(0 if error_count == 0 else 1)
