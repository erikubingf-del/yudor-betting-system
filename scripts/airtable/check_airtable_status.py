#!/usr/bin/env python3
"""Check current Airtable status"""

import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.getenv("AIRTABLE_API_KEY"))
base = api.base(os.getenv("AIRTABLE_BASE_ID"))
table = base.table("Match Analyses")

print("📊 Current Airtable Status:\n")

# Get all records
all_records = table.all()

print(f"Total records: {len(all_records)}\n")

# Group by decision
decisions = {}
for record in all_records:
    decision = record['fields'].get('Yudor Decision', 'UNKNOWN')
    if decision not in decisions:
        decisions[decision] = []
    decisions[decision].append(record['fields'].get('match_id', 'unknown'))

print("By Decision:")
for decision, matches in sorted(decisions.items()):
    print(f"  {decision}: {len(matches)}")
    if decision in ['CORE', 'EXP', 'FLIP']:
        for match_id in matches:
            print(f"    • {match_id}")

print()
