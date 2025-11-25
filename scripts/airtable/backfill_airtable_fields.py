#!/usr/bin/env python3
"""
Backfill Airtable Fields - Update existing records with missing data

Updates:
- Yudor AH Team
- Yudor Fair Odds
- Q1-Q19 Scores
- Analysis Timestamp
- Data Quality
- Tier

Reads from "Full Analysis" JSON field to extract missing data.
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

print("=" * 80)
print("🔧 AIRTABLE BACKFILL - UPDATE MISSING FIELDS")
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
        # Check if update needed
        needs_update = False
        updates = {}

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

        # 1. Yudor AH Team
        if not fields.get('Yudor AH Team') and 'yudor_ah_team' not in fields:
            ah_fair_raw = fields.get('Yudor AH Fair', 0)
            # Convert to float if it's a string
            try:
                ah_fair = float(ah_fair_raw) if ah_fair_raw else 0
            except (ValueError, TypeError):
                ah_fair = 0

            home_team = fields.get('Home Team', '')
            away_team = fields.get('Away Team', '')
            favorite_side = analysis.get('favorite_side', '')

            yudor_ah_team = ""
            if favorite_side == "HOME":
                yudor_ah_team = home_team
            elif favorite_side == "AWAY":
                yudor_ah_team = away_team
            elif ah_fair < 0:
                yudor_ah_team = home_team
            else:
                yudor_ah_team = away_team

            if yudor_ah_team:
                updates['Yudor AH Team'] = yudor_ah_team
                needs_update = True
                print(f"   ✅ Adding Yudor AH Team: {yudor_ah_team}")

        # 2. Yudor Fair Odds
        if not fields.get('Yudor Fair Odds'):
            ah_fair_raw = fields.get('Yudor AH Fair', 0)
            try:
                ah_fair = float(ah_fair_raw) if ah_fair_raw else 0
            except (ValueError, TypeError):
                ah_fair = 0

            yudor_fair_odds = analysis.get('yudor_fair_odds', 0)

            if not yudor_fair_odds and ah_fair != 0:
                # Calculate from AH line
                yudor_fair_odds = 2.0 - (ah_fair * 0.4)
                yudor_fair_odds = round(max(1.01, min(yudor_fair_odds, 10.0)), 2)

            if yudor_fair_odds:
                updates['Yudor Fair Odds'] = yudor_fair_odds
                needs_update = True
                print(f"   ✅ Adding Yudor Fair Odds: {yudor_fair_odds}")

        # 3. Q1-Q19 Scores
        if not fields.get('Q1-Q19 Scores'):
            q1_q19_scores = ""

            # Try consolidated_data
            if "consolidated_data" in analysis:
                consolidated = analysis["consolidated_data"]
                if "q_scores" in consolidated:
                    q_scores = consolidated["q_scores"]
                    q_lines = []
                    for q_id, q_data in sorted(q_scores.items()):
                        home = q_data.get("home_score", 0)
                        away = q_data.get("away_score", 0)
                        q_lines.append(f"{q_id}: {home} vs {away}")
                    q1_q19_scores = "\n".join(q_lines)

            # Try direct q_scores
            if not q1_q19_scores and "q_scores" in analysis:
                q_scores = analysis["q_scores"]
                q_lines = []
                for q_id, q_data in sorted(q_scores.items()):
                    if isinstance(q_data, dict):
                        home = q_data.get("home_score", 0)
                        away = q_data.get("away_score", 0)
                        q_lines.append(f"{q_id}: {home} vs {away}")
                if q_lines:
                    q1_q19_scores = "\n".join(q_lines)

            if q1_q19_scores:
                updates['Q1-Q19 Scores'] = q1_q19_scores
                needs_update = True
                print(f"   ✅ Adding Q1-Q19 Scores ({len(q1_q19_scores)} chars)")
            else:
                print(f"   ⚠️  Q1-Q19 scores not found in analysis")

        # 4. Analysis Timestamp
        if not fields.get('Analysis Timestamp'):
            # Use match_date or current date
            match_date = fields.get('match_date', '')
            if match_date:
                updates['Analysis Timestamp'] = match_date
            else:
                updates['Analysis Timestamp'] = datetime.now().strftime("%Y-%m-%d")
            needs_update = True
            print(f"   ✅ Adding Analysis Timestamp: {updates['Analysis Timestamp']}")

        # 5. Data Quality
        if not fields.get('Data Quality'):
            confidence = analysis.get('confidence', 0)
            if confidence:
                updates['Data Quality'] = confidence
                needs_update = True
                print(f"   ✅ Adding Data Quality: {confidence}%")

        # 6. Tier
        if not fields.get('Tier'):
            tier = analysis.get('tier', 0)
            if tier:
                updates['Tier'] = tier
                needs_update = True
                print(f"   ✅ Adding Tier: {tier}")

        # Update record if needed
        if needs_update:
            table.update(record_id, updates)
            updated_count += 1
            print(f"   ✅ Updated {len(updates)} fields")
        else:
            print(f"   ℹ️  No updates needed")
            skipped_count += 1

    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        error_count += 1
        continue

# Summary
print("\n" + "=" * 80)
print("📊 BACKFILL SUMMARY")
print("=" * 80)
print(f"   Total records: {len(all_records)}")
print(f"   ✅ Updated: {updated_count}")
print(f"   ℹ️  Skipped: {skipped_count}")
print(f"   ❌ Errors: {error_count}")
print(f"\n🕐 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

sys.exit(0 if error_count == 0 else 1)
