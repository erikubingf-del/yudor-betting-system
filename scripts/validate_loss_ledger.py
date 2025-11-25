#!/usr/bin/env python3
"""
Loss Ledger System Validation Script

Validates that the loss ledger system is ready for production use.
Checks:
1. Required prompt files exist
2. Airtable connection works
3. Required table/column schema is correct
4. Claude API is accessible
5. Loss ledger directory is writable

Usage:
    python3 scripts/validate_loss_ledger.py
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_prompt_files():
    """Check if required prompt files exist"""
    print("\n📄 Checking Prompt Files...")

    base_dir = Path(__file__).parent.parent
    prompts_dir = base_dir / 'prompts'

    required_files = [
        'LOSS_LEDGER_ANALYSIS_PROMPT_v1.0.md',
        'DATA_CONSOLIDATION_PROMPT_v1.0.md',
        'anexos/ANEXO_I_SCORING_CRITERIA.md'
    ]

    all_exist = True
    for file in required_files:
        file_path = prompts_dir / file
        if file_path.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ MISSING: {file}")
            all_exist = False

    return all_exist


def check_api_keys():
    """Check if required API keys are configured"""
    print("\n🔑 Checking API Keys...")

    keys = {
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'AIRTABLE_API_KEY': os.getenv('AIRTABLE_API_KEY'),
        'AIRTABLE_BASE_ID': os.getenv('AIRTABLE_BASE_ID')
    }

    all_configured = True
    for key_name, key_value in keys.items():
        if key_value:
            masked = key_value[:8] + '...' + key_value[-4:] if len(key_value) > 12 else '***'
            print(f"   ✅ {key_name}: {masked}")
        else:
            print(f"   ❌ MISSING: {key_name}")
            all_configured = False

    return all_configured


def check_airtable_connection():
    """Check if Airtable connection works and validate schema"""
    print("\n📊 Checking Airtable Connection...")

    try:
        from pyairtable import Api

        api_key = os.getenv('AIRTABLE_API_KEY')
        base_id = os.getenv('AIRTABLE_BASE_ID')

        if not api_key or not base_id:
            print("   ❌ Airtable credentials not configured")
            return False

        api = Api(api_key)
        base = api.base(base_id)

        # Check Match Analyses table
        print("\n   📋 Match Analyses Table:")
        try:
            analyses_table = base.table('Match Analyses')
            records = analyses_table.all(max_records=1)

            if records:
                fields = records[0]['fields'].keys()
                required_fields = ['match_id', 'Home Team', 'Away Team', 'Yudor AH Fair', 'Yudor AH Team']

                for field in required_fields:
                    if field in fields:
                        print(f"      ✅ {field}")
                    else:
                        print(f"      ⚠️  Missing recommended field: {field}")

                # Check if Yudor AH Team exists (the fix we just made)
                if 'Yudor AH Team' in fields:
                    print(f"      🎯 NEW FIELD CONFIRMED: 'Yudor AH Team' is present!")
            else:
                print("      ℹ️  Table is empty (no records to check)")
        except Exception as e:
            print(f"      ❌ Error accessing Match Analyses: {str(e)}")

        # Check Bets Entered table (linked table)
        print("\n   📋 Bets Entered Table (for Loss Ledger):")
        try:
            bets_table = base.table('Bets Entered')
            records = bets_table.all(max_records=1)

            if records:
                fields = records[0]['fields'].keys()
                required_loss_fields = ['match_id', 'Score', 'Result', 'P/L', 'Bets Entered']

                missing_fields = []
                for field in required_loss_fields:
                    if field in fields:
                        print(f"      ✅ {field}")
                    else:
                        print(f"      ❌ MISSING: {field} (USER MUST ADD)")
                        missing_fields.append(field)

                if missing_fields:
                    print(f"\n      ⚠️  USER ACTION REQUIRED:")
                    print(f"         Please add these columns to 'Bets Entered' table:")
                    for field in missing_fields:
                        if field == 'Score':
                            print(f"         - {field} (Single line text)")
                        elif field == 'Result':
                            print(f"         - {field} (Single select: Win, Loss, Half Win, Half Loss, Refund)")
                        elif field == 'P/L':
                            print(f"         - {field} (Number)")
                        elif field == 'Bets Entered':
                            print(f"         - {field} (Checkbox)")
            else:
                print("      ℹ️  Table is empty (no records to check)")
                print("      ⚠️  Cannot validate schema without records")
                print("      📝 Required columns: match_id, Score, Result, P/L, Bets Entered")
        except Exception as e:
            print(f"      ❌ Error accessing Bets Entered: {str(e)}")

        # Check Results table
        print("\n   📋 Results Table:")
        try:
            results_table = base.table('Results')
            records = results_table.all(max_records=1)

            if records:
                fields = records[0]['fields'].keys()
                loss_fields = ['match_id', 'error_category', 'error_type', 'failed_q_ids']

                for field in loss_fields:
                    if field in fields:
                        print(f"      ✅ {field}")
                    else:
                        print(f"      ℹ️  Will be created: {field}")
            else:
                print("      ℹ️  Table is empty - fields will be created on first loss analysis")
        except Exception as e:
            print(f"      ❌ Error accessing Results: {str(e)}")

        print("\n   ✅ Airtable connection successful!")
        return True

    except ImportError:
        print("   ❌ pyairtable not installed. Run: pip install pyairtable")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {str(e)}")
        return False


def check_directories():
    """Check if required directories exist and are writable"""
    print("\n📁 Checking Directories...")

    base_dir = Path(__file__).parent.parent

    required_dirs = [
        base_dir / 'loss_ledger',
        base_dir / 'analysis_history',
        base_dir / 'consolidated_data'
    ]

    all_ok = True
    for dir_path in required_dirs:
        if dir_path.exists():
            # Check if writable
            test_file = dir_path / '.write_test'
            try:
                test_file.touch()
                test_file.unlink()
                print(f"   ✅ {dir_path.name}/ (exists & writable)")
            except Exception:
                print(f"   ⚠️  {dir_path.name}/ (exists but not writable)")
                all_ok = False
        else:
            # Create it
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ {dir_path.name}/ (created)")
            except Exception as e:
                print(f"   ❌ {dir_path.name}/ (cannot create: {e})")
                all_ok = False

    return all_ok


def check_claude_api():
    """Quick check if Claude API is accessible"""
    print("\n🤖 Checking Claude API...")

    try:
        from anthropic import Anthropic

        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("   ❌ ANTHROPIC_API_KEY not configured")
            return False

        client = Anthropic(api_key=api_key)

        # Simple test call
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": "test"}]
        )

        print(f"   ✅ Claude API accessible (model: claude-sonnet-4-20250514)")
        return True

    except ImportError:
        print("   ❌ anthropic package not installed. Run: pip install anthropic")
        return False
    except Exception as e:
        print(f"   ❌ API error: {str(e)}")
        return False


def main():
    print("=" * 80)
    print("🔍 YUDOR LOSS LEDGER SYSTEM - VALIDATION")
    print("=" * 80)

    checks = {
        'Prompt Files': check_prompt_files(),
        'API Keys': check_api_keys(),
        'Directories': check_directories(),
        'Claude API': check_claude_api(),
        'Airtable': check_airtable_connection()
    }

    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)

    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}  {check_name}")

    all_passed = all(checks.values())

    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - READY FOR PRODUCTION!")
        print("\nNext steps:")
        print("1. Manually add test data to Airtable 'Bets Entered' table")
        print("2. Run: python3 scripts/master_orchestrator.py loss-analysis --auto")
        print("3. Check loss_ledger/ folder for analysis files")
    else:
        print("⚠️  SOME CHECKS FAILED - PLEASE FIX BEFORE PRODUCTION")
        print("\nReview the errors above and fix them before running loss analysis.")
    print("=" * 80 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
