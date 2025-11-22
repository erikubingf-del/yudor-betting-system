#!/usr/bin/env python3
"""
Sync ALL betting opportunities (CORE, EXP, FLIP) to Airtable
Includes match date and analysis timestamp
"""

import json
import os
from pathlib import Path
from datetime import datetime
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
ANALYSIS_DIR = BASE_DIR / "analysis_history"

def sync_all_to_airtable():
    """Sync all CORE, EXP, and FLIP matches to Airtable"""

    api = Api(os.getenv("AIRTABLE_API_KEY"))
    base = api.base(os.getenv("AIRTABLE_BASE_ID"))
    table = base.table("Match Analyses")

    synced = 0
    updated = 0
    created = 0
    skipped = 0
    errors = 0

    print("="*80)
    print("🎯 SYNCING ALL BETTING OPPORTUNITIES TO AIRTABLE")
    print("="*80)
    print()

    # Find all analysis files
    analysis_files = sorted(ANALYSIS_DIR.glob("*_analysis.json"))

    print(f"📋 Found {len(analysis_files)} analysis files")
    print()

    for analysis_file in analysis_files:
        match_id = analysis_file.stem.replace("_analysis", "")

        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            match_info = data.get("match_info", {})
            analysis = data.get("yudor_analysis", {})
            decision = analysis.get("decision", "")
            timestamp = data.get("timestamp", "")

            # Only sync CORE, EXP, and FLIP
            if decision not in ["CORE", "EXP", "FLIP"]:
                skipped += 1
                continue

            # Convert date format
            date_str = match_info.get("date", "")
            try:
                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                match_date_formatted = date_obj.strftime("%Y-%m-%d")
            except:
                match_date_formatted = date_str

            # Parse analysis timestamp
            analysis_timestamp = ""
            if timestamp:
                try:
                    ts_obj = datetime.fromisoformat(timestamp)
                    analysis_timestamp = ts_obj.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    analysis_timestamp = timestamp

            record_data = {
                "match_id": match_id,
                "match_date": match_date_formatted,
                "Home Team": match_info.get("home", ""),
                "Away Team": match_info.get("away", ""),
                "League": match_info.get("league", ""),
                "Yudor AH Fair": analysis.get("yudor_ah_fair", 0),
                "Yudor Decision": decision,
                "CS Final": analysis.get("cs_final", 0),
                "R Score": analysis.get("r_score", 0),
                "Tier": analysis.get("tier", 0),
                "Full Analysis": json.dumps(analysis, indent=2),
                "Data Quality": analysis.get("confidence", 0),
                "Status": "ANALYZED"
            }

            # Check if record exists
            existing = table.all(formula=f"{{match_id}}='{match_id}'")

            if existing:
                table.update(existing[0]['id'], record_data)
                print(f"   ✅ Updated: {match_info.get('home')} vs {match_info.get('away')} - {decision} ({match_date_formatted})")
                updated += 1
            else:
                table.create(record_data)
                print(f"   ✅ Created: {match_info.get('home')} vs {match_info.get('away')} - {decision} ({match_date_formatted})")
                created += 1

            synced += 1

        except Exception as e:
            print(f"   ❌ Error syncing {match_id}: {e}")
            errors += 1

    print()
    print("="*80)
    print("📊 SYNC SUMMARY")
    print("="*80)
    print(f"   ✅ Total Synced: {synced}")
    print(f"   🆕 Created: {created}")
    print(f"   🔄 Updated: {updated}")
    print(f"   ⏭️  Skipped (VETO/other): {skipped}")
    print(f"   ❌ Errors: {errors}")
    print()

    # Show breakdown by decision
    print("📋 BY DECISION TYPE:")
    for decision_type in ["CORE", "EXP", "FLIP"]:
        count = 0
        for analysis_file in ANALYSIS_DIR.glob("*_analysis.json"):
            try:
                with open(analysis_file, 'r') as f:
                    data = json.load(f)
                    if data.get("yudor_analysis", {}).get("decision") == decision_type:
                        count += 1
            except:
                pass
        print(f"   {decision_type}: {count}")
    print()

if __name__ == "__main__":
    sync_all_to_airtable()
