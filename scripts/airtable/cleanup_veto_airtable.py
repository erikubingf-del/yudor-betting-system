#!/usr/bin/env python3
"""
Remove VETO records from Airtable - only keep CORE and EXP
"""

import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.getenv("AIRTABLE_API_KEY"))
base = api.base(os.getenv("AIRTABLE_BASE_ID"))
table = base.table("Match Analyses")

print("🗑️  Finding VETO records in Airtable...")

# Get all VETO records
veto_records = table.all(formula="{Yudor Decision}='VETO'")

print(f"Found {len(veto_records)} VETO records to delete")

if len(veto_records) > 0:
    confirm = input(f"Delete {len(veto_records)} VETO records? (yes/no): ")
    if confirm.lower() == "yes":
        deleted = 0
        for record in veto_records:
            try:
                table.delete(record['id'])
                print(f"✅ Deleted: {record['fields'].get('match_id', 'unknown')}")
                deleted += 1
            except Exception as e:
                print(f"❌ Error deleting {record['fields'].get('match_id')}: {e}")
        
        print(f"\n✅ Deleted {deleted}/{len(veto_records)} VETO records")
    else:
        print("Cancelled")
else:
    print("✅ No VETO records found")
