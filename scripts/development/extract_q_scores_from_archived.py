#!/usr/bin/env python3
"""
Extract Q1-Q19 Scores from Archived Analysis Files

This script:
1. Finds archived analysis JSON files for each match
2. Extracts Q1-Q19 scores from consolidated_data.q_scores
3. Formats them properly
4. Updates Airtable Q1-Q19 Scores field

This avoids re-analyzing matches since the data already exists in archived files!
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

# Archived analyses directory
ARCHIVED_DIR = Path(__file__).parent.parent / 'archived_analyses'


def find_archived_analysis(match_id: str) -> Path:
    """
    Find archived analysis file for a match_id

    Searches in archived_analyses/*/match_id_analysis.json
    """
    if not ARCHIVED_DIR.exists():
        return None

    # Search all subdirectories
    for date_dir in ARCHIVED_DIR.iterdir():
        if not date_dir.is_dir():
            continue

        # Try exact match
        analysis_file = date_dir / f"{match_id}_analysis.json"
        if analysis_file.exists():
            return analysis_file

    return None


def extract_q_scores_from_file(analysis_file: Path) -> str:
    """
    Extract Q1-Q19 scores from archived analysis file

    Returns formatted string like:
    Q1: 5 vs 4
    Q2: 4 vs 3
    ...
    Q19: 3 vs 2
    """
    try:
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis = json.load(f)

        # Try consolidated_data.q_scores
        if 'consolidated_data' in analysis and 'q_scores' in analysis['consolidated_data']:
            q_scores = analysis['consolidated_data']['q_scores']
            q_lines = []

            for q_id in sorted(q_scores.keys(), key=lambda x: int(x[1:])):  # Sort Q1, Q2, ..., Q19
                q_data = q_scores[q_id]
                if isinstance(q_data, dict):
                    home = q_data.get('home_score', 0)
                    away = q_data.get('away_score', 0)
                    q_lines.append(f"{q_id}: {home} vs {away}")

            if q_lines:
                return "\n".join(q_lines)

        # Try direct q_scores
        if 'q_scores' in analysis:
            q_scores = analysis['q_scores']
            q_lines = []

            for q_id in sorted(q_scores.keys(), key=lambda x: int(x[1:])):
                q_data = q_scores[q_id]
                if isinstance(q_data, dict):
                    home = q_data.get('home_score', 0)
                    away = q_data.get('away_score', 0)
                    q_lines.append(f"{q_id}: {home} vs {away}")

            if q_lines:
                return "\n".join(q_lines)

        return None

    except Exception as e:
        print(f"      ❌ Error reading file: {str(e)[:50]}")
        return None


print("=" * 80)
print("📂 EXTRACT Q1-Q19 SCORES FROM ARCHIVED FILES")
print("=" * 80)

# Get all Match Analyses records
table = base.table("Match Analyses")
all_records = table.all()

print(f"\n✅ Found {len(all_records)} records in Airtable")
print(f"📁 Searching archived analyses in: {ARCHIVED_DIR}")
print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

updated_count = 0
skipped_already_populated = 0
skipped_no_file = 0
skipped_no_q_scores = 0
error_count = 0

for idx, record in enumerate(all_records, 1):
    record_id = record['id']
    fields = record['fields']
    match_id = fields.get('match_id', f'Record #{idx}')

    print(f"\n[{idx}/{len(all_records)}] Processing: {match_id}")

    try:
        # Check if already populated
        existing_q_scores = fields.get('Q1-Q19 Scores', '')
        if existing_q_scores:
            print(f"   ℹ️  Already has Q1-Q19 scores - skipping")
            skipped_already_populated += 1
            continue

        # Find archived analysis file
        print(f"   🔍 Searching for archived analysis file...")
        analysis_file = find_archived_analysis(match_id)

        if not analysis_file:
            print(f"   ⚠️  No archived file found")
            skipped_no_file += 1
            continue

        print(f"   ✅ Found: {analysis_file.relative_to(ARCHIVED_DIR.parent)}")

        # Extract Q scores
        print(f"   📊 Extracting Q1-Q19 scores...")
        q_scores_text = extract_q_scores_from_file(analysis_file)

        if not q_scores_text:
            print(f"   ⚠️  No Q scores found in file")
            skipped_no_q_scores += 1
            continue

        # Count number of Q scores
        num_qs = len(q_scores_text.split('\n'))
        print(f"   ✅ Extracted {num_qs} Q scores")

        # Update Airtable
        table.update(record_id, {'Q1-Q19 Scores': q_scores_text})
        print(f"   ✅ Updated Airtable")
        updated_count += 1

    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        error_count += 1
        import traceback
        traceback.print_exc()
        continue

# Summary
print("\n" + "=" * 80)
print("📊 EXTRACTION SUMMARY")
print("=" * 80)
print(f"   Total records: {len(all_records)}")
print(f"   ✅ Updated with Q scores: {updated_count}")
print(f"   ℹ️  Already had Q scores: {skipped_already_populated}")
print(f"   ⚠️  No archived file: {skipped_no_file}")
print(f"   ⚠️  No Q scores in file: {skipped_no_q_scores}")
print(f"   ❌ Errors: {error_count}")
print(f"\n🕐 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

if updated_count > 0:
    print(f"\n🎉 Successfully populated Q1-Q19 scores for {updated_count} matches!")
    print("   All data extracted from existing archived analysis files.")
    print("   No re-analysis needed!")
else:
    print("\n⚠️  No matches were updated.")
    if skipped_no_file > 0:
        print(f"   {skipped_no_file} matches have no archived analysis files.")
        print("   These would need to be re-analyzed if you want Q1-Q19 scores.")

print("=" * 80)

sys.exit(0 if error_count == 0 else 1)
