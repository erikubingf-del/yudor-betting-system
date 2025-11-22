#!/usr/bin/env python3
"""
Delete ALL records from Airtable and re-add only CORE and EXP
"""

import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.getenv("AIRTABLE_API_KEY"))
base = api.base(os.getenv("AIRTABLE_BASE_ID"))
table = base.table("Match Analyses")

print("🗑️  Deleting ALL records from Airtable...")

# Get all records
all_records = table.all()

print(f"Found {len(all_records)} records to delete")

deleted = 0
for record in all_records:
    try:
        table.delete(record['id'])
        print(f"✅ Deleted: {record['fields'].get('match_id', 'unknown')}")
        deleted += 1
    except Exception as e:
        print(f"❌ Error deleting {record['fields'].get('match_id')}: {e}")

print(f"\n✅ Deleted {deleted}/{len(all_records)} records")
print("Ready to re-add CORE and EXP records")
