#!/usr/bin/env python3
"""
Discover Airtable Schema - Shows all tables and fields
"""
import os
import sys
from pathlib import Path
from pyairtable import Api

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

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

if not api_key or not base_id:
    print("❌ Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID in .env")
    sys.exit(1)

api = Api(api_key)
base = api.base(base_id)

print("🔍 AIRTABLE SCHEMA DISCOVERY")
print("=" * 80)

try:
    schema = base.schema()
    print(f"\n✅ Found {len(schema.tables)} tables:\n")

    for idx, table in enumerate(schema.tables, 1):
        print(f"\n{idx}. TABLE: {table.name}")
        print(f"   ID: {table.id}")
        print(f"   Fields: {len(table.fields)}")
        print(f"   {'─' * 76}")

        for field in table.fields:
            field_type = field.type
            options = ""

            # Show options for select fields
            if hasattr(field, 'options') and field.options:
                if hasattr(field.options, 'choices') and field.options.choices:
                    choices = [c.name for c in field.options.choices]
                    options = f" (Options: {', '.join(choices[:3])}{'...' if len(choices) > 3 else ''})"

            print(f"      • {field.name:<30} {field_type:<20} {options}")

        print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
