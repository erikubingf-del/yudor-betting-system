#!/usr/bin/env python3
"""
Test Airtable Access - Try different table names
"""
import os
import sys
from pathlib import Path
from pyairtable import Api

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

api = Api(api_key)
base = api.base(base_id)

print("🔍 TESTING AIRTABLE TABLE ACCESS")
print("=" * 80)

# Try different table names
table_names_to_try = [
    "Match Analyses",
    "Bet Records",
    "Learning Ledger",
    "Bets Entered",
    "Results",
    "Match Analysis",  # singular
    "Bet Record",  # singular
]

print("\nTrying to access tables...\n")

for table_name in table_names_to_try:
    try:
        table = base.table(table_name)
        records = table.all(max_records=1)

        if records:
            fields = list(records[0]['fields'].keys())
            print(f"✅ {table_name}")
            print(f"   Fields ({len(fields)}): {', '.join(fields[:5])}{'...' if len(fields) > 5 else ''}")
        else:
            print(f"✅ {table_name} (exists but empty)")

    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "NOT_FOUND" in error_msg:
            print(f"❌ {table_name} - Not found")
        elif "403" in error_msg or "FORBIDDEN" in error_msg:
            print(f"⚠️  {table_name} - No permission")
        else:
            print(f"❌ {table_name} - Error: {error_msg[:50]}")

    print()
