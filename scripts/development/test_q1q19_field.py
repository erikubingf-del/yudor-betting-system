#!/usr/bin/env python3
"""
Test if Q1-Q19 Scores field exists in Match Analyses table
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

api = Api(api_key)
base = api.base(base_id)
table = base.table("Match Analyses")

print("Testing Q1-Q19 Scores field...")

# Get first record
records = table.all(max_records=1)
if records:
    record_id = records[0]['id']
    fields = records[0]['fields']

    print(f"\n✅ Found record: {fields.get('match_id', 'Unknown')}")

    # Check if Q1-Q19 Scores exists
    if 'Q1-Q19 Scores' in fields:
        print(f"✅ Q1-Q19 Scores field EXISTS")
        print(f"   Current value: {fields['Q1-Q19 Scores'][:100] if fields['Q1-Q19 Scores'] else '(empty)'}...")
    else:
        print(f"❌ Q1-Q19 Scores field DOES NOT EXIST in record")
        print(f"\n📝 You need to manually add this field to Airtable:")
        print(f"   1. Open Airtable Match Analyses table")
        print(f"   2. Click '+' to add new field")
        print(f"   3. Name: Q1-Q19 Scores")
        print(f"   4. Type: Long text")
        print(f"   5. Enable rich text formatting: NO")

        # Try to update with test data
        print(f"\n🧪 Testing if we can write to Q1-Q19 Scores field...")
        try:
            test_data = "Q1: 5 vs 3\nQ2: 7 vs 4\nQ3: 2 vs 2"
            table.update(record_id, {"Q1-Q19 Scores": test_data})
            print(f"✅ Successfully wrote to Q1-Q19 Scores field!")
            print(f"   The field exists but was empty in this record.")
        except Exception as e:
            error_msg = str(e)
            if "UNKNOWN_FIELD_NAME" in error_msg or "Unknown field" in error_msg:
                print(f"❌ Field does NOT exist - you must create it manually in Airtable")
            else:
                print(f"❌ Error: {error_msg}")
else:
    print("❌ No records found in table")
