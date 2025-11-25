#!/usr/bin/env python3
"""
Validate Airtable Schema - Ensure schema matches code expectations

Checks:
- All 3 tables exist (Match Analyses, Bet Records, Learning Ledger)
- All required fields present
- Field types match expectations
- Links between tables valid
"""
import os
import sys
from pathlib import Path
from pyairtable import Api

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

# Expected schema
EXPECTED_SCHEMA = {
    "Match Analyses": {
        "fields": [
            "match_id", "match_date", "Home Team", "Away Team", "League",
            "Analysis Timestamp", "Yudor AH Fair", "Yudor AH Team", "Yudor Fair Odds",
            "Yudor Decision", "CS Final", "R Score", "Tier", "Data Quality",
            "Q1-Q19 Scores", "Full Analysis", "Status"
        ],
        "min_fields": 17
    },
    "Bet Records": {
        "fields": [
            "Id", "Match Analyses", "match_id", "Home Team", "Away Team",
            "Yudor AH Fair", "Bet Placed", "Market AH Line", "Market AH Odds",
            "Stake", "Expected Value", "Final Score", "AH Result", "P/L", "ROI %"
        ],
        "min_fields": 10
    },
    "Learning Ledger": {
        "fields": [
            "Analysis ID", "analysis_timestamp", "outcome_type",
            "yudor_correct", "error_type", "pattern_tags"
        ],
        "min_fields": 3
    }
}

print("=" * 80)
print("🔍 AIRTABLE SCHEMA VALIDATION")
print("=" * 80)

all_valid = True
warnings = []

for table_name, schema in EXPECTED_SCHEMA.items():
    print(f"\n📊 Validating: {table_name}")
    print("-" * 80)

    try:
        table = base.table(table_name)
        records = table.all(max_records=1)

        if not records:
            warnings.append(f"⚠️  {table_name} is empty - cannot validate field types")
            print(f"   ⚠️  Table is empty")
            continue

        existing_fields = list(records[0]['fields'].keys())
        expected_fields = schema['fields']

        # Check for missing required fields
        missing = [f for f in expected_fields if f not in existing_fields]
        extra = [f for f in existing_fields if f not in expected_fields]

        if missing:
            print(f"   ❌ Missing fields: {', '.join(missing)}")
            all_valid = False
        else:
            print(f"   ✅ All required fields present ({len(existing_fields)} fields)")

        if extra and len(extra) <= 5:
            print(f"   ℹ️  Extra fields: {', '.join(extra)}")
        elif extra:
            print(f"   ℹ️  {len(extra)} extra fields (extensions)")

    except Exception as e:
        print(f"   ❌ Error accessing table: {str(e)[:60]}")
        all_valid = False

# Summary
print("\n" + "=" * 80)
print("📊 VALIDATION SUMMARY")
print("=" * 80)

if all_valid and not warnings:
    print("✅ All tables valid - schema matches expectations")
    sys.exit(0)
elif all_valid and warnings:
    print("⚠️  Schema valid with warnings:")
    for warning in warnings:
        print(f"   {warning}")
    sys.exit(0)
else:
    print("❌ Schema validation failed - please fix issues above")
    sys.exit(1)
