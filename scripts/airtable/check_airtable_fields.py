#!/usr/bin/env python3
"""
Check Airtable Fields - Show all fields in each table
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

print("📊 AIRTABLE FIELD AUDIT")
print("=" * 80)

tables = ["Match Analyses", "Bet Records", "Learning Ledger"]

for table_name in tables:
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name}")
    print('='*80)

    try:
        table = base.table(table_name)
        records = table.all(max_records=1)

        if records:
            fields = records[0]['fields']
            print(f"\n✅ Found {len(fields)} fields:\n")

            for idx, (field_name, value) in enumerate(fields.items(), 1):
                value_preview = str(value)[:50] if value else "(empty)"
                value_type = type(value).__name__

                print(f"  {idx:2}. {field_name:<35} | {value_type:<15} | {value_preview}")

        else:
            print("\n⚠️  Table is empty - cannot check fields")
            print("   Please add at least one record manually to see field structure")

    except Exception as e:
        print(f"\n❌ Error accessing {table_name}: {e}")

print("\n" + "="*80)
