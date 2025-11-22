#!/usr/bin/env python3
"""
Sync only CORE and EXP matches from re-analysis to Airtable
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

# Match IDs from the 20 re-analyzed games
REANALYZED_MATCHES = [
    "ArsenalvsTottenhamHotspur_23112025",
    "BarcelonavsAthleticClub_22112025",
    "BayernMunichvsFreiburg_22112025",
    "VillarrealvsMallorca_22112025",
    "RBLeipzigvsWerderBremen_23112025",
    "LiverpoolvsNottinghamForest_22112025",
    "NewcastleUnitedvsManchesterCity_22112025",
    "ManchesterUnitedvsEverton_24112025",
    "PalmeirasvsFluminense_22112025",
    "AugsburgvsHamburgerSV_22112025",
    "InterMilanvsACMilan_23112025",
    "BorussiaDortmundvsStuttgart_22112025",
    "FiorentinavsJuventus_22112025",
    "RealBetisvsGirona_23112025",
    "FlamengovsRedBullBragantino_22112025",
    "CruzeirovsCorinthians_23112025",
    "NapolivsAtalanta_22112025",
    "OsasunavsRealSociedad_22112025",
    "CagliarivsGenoa_22112025",
    "Mainz05vsHoffenheim_21112025"
]

def sync_to_airtable():
    """Sync CORE and EXP matches to Airtable"""

    api = Api(os.getenv("AIRTABLE_API_KEY"))
    base = api.base(os.getenv("AIRTABLE_BASE_ID"))
    table = base.table("Match Analyses")

    synced = 0
    skipped = 0
    errors = 0

    print("="*80)
    print("🎯 SYNCING RE-ANALYZED MATCHES TO AIRTABLE")
    print("="*80)
    print()

    for match_id in REANALYZED_MATCHES:
        analysis_file = ANALYSIS_DIR / f"{match_id}_analysis.json"

        if not analysis_file.exists():
            print(f"⚠️  File not found: {match_id}")
            errors += 1
            continue

        with open(analysis_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        match_info = data.get("match_info", {})
        analysis = data.get("yudor_analysis", {})
        decision = analysis.get("decision", "")

        # Only sync CORE and EXP
        if decision not in ["CORE", "EXP"]:
            print(f"⏭️  Skipping {match_id}: {decision}")
            skipped += 1
            continue

        try:
            # Convert date format
            date_str = match_info.get("date", "")
            try:
                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                match_date_formatted = date_obj.strftime("%Y-%m-%d")
            except:
                match_date_formatted = date_str

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
                print(f"   ✅ Updated: {match_info.get('home')} vs {match_info.get('away')} - {decision}")
            else:
                table.create(record_data)
                print(f"   ✅ Created: {match_info.get('home')} vs {match_info.get('away')} - {decision}")

            synced += 1

        except Exception as e:
            print(f"   ❌ Error syncing {match_id}: {e}")
            errors += 1

    print()
    print("="*80)
    print("📊 SYNC SUMMARY")
    print("="*80)
    print(f"   ✅ Synced: {synced}")
    print(f"   ⏭️  Skipped (VETO): {skipped}")
    print(f"   ❌ Errors: {errors}")
    print()

if __name__ == "__main__":
    sync_to_airtable()
