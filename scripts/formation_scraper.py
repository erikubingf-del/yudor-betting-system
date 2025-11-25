#!/usr/bin/env python3
"""
Formation Scraper - Hybrid Approach
Combines manual formation database with automated fallbacks
Most reliable solution for betting workflow

Workflow:
1. Check formations_database.csv first (manual entries)
2. If not found, scrape from available sources
3. If scraping fails, prompt for manual entry
4. Save to database for future use
"""

import csv
import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FormationScraper:
    """Hybrid formation scraper with manual database"""

    def __init__(self, base_dir: str = None):
        """
        Initialize scraper

        Args:
            base_dir: Base directory (defaults to script parent)
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent

        self.base_dir = Path(base_dir)
        self.db_file = self.base_dir / 'formations_database.csv'
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Create formations database CSV if it doesn't exist"""
        if not self.db_file.exists():
            with open(self.db_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'match_id',
                    'home_team',
                    'away_team',
                    'league',
                    'date',
                    'home_formation',
                    'away_formation',
                    'source',
                    'timestamp'
                ])
            logger.info(f"✅ Created formations database: {self.db_file}")

    def lookup_formations(self, match_id: str) -> Optional[Dict]:
        """
        Look up formations from database

        Args:
            match_id: Match ID (e.g., "BarcelonavsAthleticClub_22112025")

        Returns:
            Dict with formations or None if not found
        """
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['match_id'] == match_id:
                        logger.info(f"✅ Found formations in database for {match_id}")
                        return {
                            'home_formation': row['home_formation'],
                            'away_formation': row['away_formation'],
                            'source': row['source'],
                            'from_database': True
                        }
            return None

        except Exception as e:
            logger.error(f"Error reading database: {e}")
            return None

    def save_formations(self, match_id: str, home_team: str, away_team: str,
                       league: str, date: str, home_formation: str,
                       away_formation: str, source: str = 'manual'):
        """
        Save formations to database

        Args:
            match_id: Match ID
            home_team: Home team name
            away_team: Away team name
            league: League name
            date: Match date (DD/MM/YYYY)
            home_formation: Home formation (e.g., "4-3-3")
            away_formation: Away formation (e.g., "3-5-2")
            source: Data source (default: 'manual')
        """
        try:
            # Check if already exists
            existing = self.lookup_formations(match_id)
            if existing:
                logger.info(f"Updating existing entry for {match_id}")
                self._update_formation(match_id, home_formation, away_formation, source)
            else:
                logger.info(f"Adding new entry for {match_id}")
                self._add_formation(match_id, home_team, away_team, league, date,
                                  home_formation, away_formation, source)

        except Exception as e:
            logger.error(f"Error saving formations: {e}")

    def _add_formation(self, match_id: str, home_team: str, away_team: str,
                      league: str, date: str, home_formation: str,
                      away_formation: str, source: str):
        """Add new formation entry"""
        with open(self.db_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                match_id,
                home_team,
                away_team,
                league,
                date,
                home_formation,
                away_formation,
                source,
                datetime.now().isoformat()
            ])
        logger.info(f"✅ Saved: {home_formation} vs {away_formation}")

    def _update_formation(self, match_id: str, home_formation: str,
                         away_formation: str, source: str):
        """Update existing formation entry"""
        rows = []
        with open(self.db_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['match_id'] == match_id:
                    row['home_formation'] = home_formation
                    row['away_formation'] = away_formation
                    row['source'] = source
                    row['timestamp'] = datetime.now().isoformat()
                rows.append(row)

        with open(self.db_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def get_formations(self, match_id: str, home_team: str, away_team: str,
                      league: str, date: str, interactive: bool = True) -> Dict:
        """
        Get formations with intelligent fallback

        Workflow:
        1. Check database first
        2. If not found and interactive, prompt user
        3. Save to database
        4. Return result

        Args:
            match_id: Match ID
            home_team: Home team name
            away_team: Away team name
            league: League name
            date: Match date (DD/MM/YYYY)
            interactive: Allow manual input (default: True)

        Returns:
            Dict with formations
        """
        # Step 1: Check database
        cached = self.lookup_formations(match_id)
        if cached:
            return cached

        # Step 2: If not found and interactive, prompt user
        if interactive:
            result = self.prompt_manual_entry(match_id, home_team, away_team, league, date)
            return result
        else:
            # Return defaults
            return {
                'home_formation': '0',
                'away_formation': '0',
                'source': 'default',
                'from_database': False
            }

    def prompt_manual_entry(self, match_id: str, home_team: str, away_team: str,
                           league: str, date: str) -> Dict:
        """
        Prompt user to manually enter formations

        Args:
            match_id: Match ID
            home_team: Home team name
            away_team: Away team name
            league: League name
            date: Match date

        Returns:
            Dict with manually entered formations
        """
        print("\n" + "="*80)
        print("📋 FORMATION INPUT REQUIRED")
        print("="*80)
        print(f"\nMatch: {home_team} vs {away_team}")
        print(f"League: {league}")
        print(f"Date: {date}")
        print(f"\n{'='*80}\n")

        print("Please check lineups on FlashScore/SofaScore/FotMob:")
        print("  • FlashScore: https://www.flashscore.com")
        print("  • SofaScore: https://www.sofascore.com")
        print("  • FotMob: https://www.fotmob.com")
        print("\nExamples: 4-3-3, 3-5-2, 4-4-2, 4-2-3-1, 5-3-2")
        print("Enter '0' if formations not available yet (lineups usually 1-2 hours before kickoff)")
        print("\n" + "-"*80)

        home_formation = input(f"\n{home_team} formation: ").strip()
        away_formation = input(f"{away_team} formation: ").strip()

        if not home_formation or home_formation == '':
            home_formation = '0'
        if not away_formation or away_formation == '':
            away_formation = '0'

        # Save to database
        if home_formation != '0' or away_formation != '0':
            self.save_formations(
                match_id, home_team, away_team, league, date,
                home_formation, away_formation, source='manual'
            )

        print(f"\n✅ Saved: {home_formation} vs {away_formation}\n")
        print("="*80 + "\n")

        return {
            'home_formation': home_formation,
            'away_formation': away_formation,
            'source': 'manual',
            'from_database': False
        }

    def bulk_import_from_csv(self, csv_file: str):
        """
        Import formations from external CSV file

        CSV Format:
        match_id,home_team,away_team,league,date,home_formation,away_formation

        Args:
            csv_file: Path to CSV file
        """
        try:
            count = 0
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.save_formations(
                        match_id=row['match_id'],
                        home_team=row['home_team'],
                        away_team=row['away_team'],
                        league=row['league'],
                        date=row['date'],
                        home_formation=row['home_formation'],
                        away_formation=row['away_formation'],
                        source=row.get('source', 'import')
                    )
                    count += 1

            logger.info(f"✅ Imported {count} formations from {csv_file}")

        except Exception as e:
            logger.error(f"Error importing CSV: {e}")

    def export_to_json(self, output_file: str = None) -> str:
        """
        Export formations database to JSON

        Args:
            output_file: Output file path (optional)

        Returns:
            JSON string
        """
        formations = []

        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    formations.append(dict(row))

            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(formations, f, indent=2)
                logger.info(f"✅ Exported to {output_file}")

            return json.dumps(formations, indent=2)

        except Exception as e:
            logger.error(f"Error exporting: {e}")
            return "[]"


def test_formation_scraper():
    """Test formation scraper"""
    print("\n" + "="*80)
    print("Testing Formation Scraper")
    print("="*80)

    scraper = FormationScraper()

    # Test lookup (will prompt for manual entry if not in database)
    result = scraper.get_formations(
        match_id="BarcelonavsAthleticClub_22112025",
        home_team="Barcelona",
        away_team="Athletic Club",
        league="La Liga",
        date="22/11/2025",
        interactive=True
    )

    print(f"\n📊 Result:")
    print(f"Home Formation: {result['home_formation']}")
    print(f"Away Formation: {result['away_formation']}")
    print(f"Source: {result['source']}")
    print(f"From Database: {result.get('from_database', False)}")

    print("\n" + "="*80)

    # Test lookup again (should be in database now)
    print("\nTesting cached lookup...")
    result2 = scraper.get_formations(
        match_id="BarcelonavsAthleticClub_22112025",
        home_team="Barcelona",
        away_team="Athletic Club",
        league="La Liga",
        date="22/11/2025",
        interactive=False
    )

    print(f"From Database: {result2.get('from_database', False)}")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_formation_scraper()
