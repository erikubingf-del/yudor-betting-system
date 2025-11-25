#!/usr/bin/env python3
"""
Organize analysis files by date into archived_analyses/YYYY-MM-DD/
Only archives analysis files (not consolidated data)
Consolidated data is temporary and can be regenerated
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
CONSOLIDATED_DIR = BASE_DIR / "consolidated_data"
ANALYSIS_DIR = BASE_DIR / "analysis_history"
ARCHIVE_BASE = BASE_DIR / "archived_analyses"

def organize_by_date():
    """Move analysis files to date-organized folders based on file creation date"""

    moved_count = 0
    deleted_count = 0
    files_by_date = {}

    # Delete consolidated_data files (can be regenerated)
    if CONSOLIDATED_DIR.exists():
        for file in CONSOLIDATED_DIR.glob("*.json"):
            file.unlink()
            deleted_count += 1
            print(f"   🗑️  Deleted: {file.name}")

    # Group analysis files by their creation date
    if ANALYSIS_DIR.exists():
        for file in ANALYSIS_DIR.glob("*.json"):
            # Get file creation timestamp and convert to date
            creation_time = datetime.fromtimestamp(file.stat().st_mtime)
            file_date = creation_time.strftime("%Y-%m-%d")

            if file_date not in files_by_date:
                files_by_date[file_date] = []
            files_by_date[file_date].append(file)

    # Move files to their respective date folders
    for file_date, files in files_by_date.items():
        archive_dir = ARCHIVE_BASE / file_date
        archive_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            dest = archive_dir / file.name
            shutil.move(str(file), str(dest))
            moved_count += 1
            print(f"   📊 Archived to {file_date}/: {file.name}")

    print()
    print(f"✅ Archived {moved_count} analysis files to date-organized folders")
    print(f"🗑️  Deleted {deleted_count} consolidated files (regenerable)")
    print()

if __name__ == "__main__":
    print("="*80)
    print("📂 ORGANIZING ANALYSIS FILES BY DATE")
    print("="*80)
    print()
    organize_by_date()
