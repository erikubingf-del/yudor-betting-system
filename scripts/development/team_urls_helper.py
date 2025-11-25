#!/usr/bin/env python3
"""
Team URLs Helper - Loads team URLs from pre-built database
Makes URL extraction instant and reliable
"""
import json
from pathlib import Path
from typing import Dict, Optional

# Path to team URLs databases
TEAM_NEWS_URLS = Path(__file__).parent.parent / 'team_news_urls_complete.json'
SOFASCORE_URLS = Path(__file__).parent.parent / 'sofascore_team_urls.json'
SPORTSMOLE_URLS = Path(__file__).parent.parent / 'sportsmole_team_urls.json'


class TeamURLsHelper:
    """Helper to get team URLs from pre-built databases"""

    def __init__(self):
        """Load all URL databases"""
        self.news_urls = self._load_json(TEAM_NEWS_URLS)
        self.sofascore_urls = self._load_json(SOFASCORE_URLS)
        self.sportsmole_urls = self._load_json(SPORTSMOLE_URLS)

    def _load_json(self, filepath: Path) -> Dict:
        """Load JSON file safely"""
        if not filepath.exists():
            print(f"⚠️  Database not found: {filepath}")
            return {}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
            return {}

    def get_news_url(self, team: str, league: str) -> Optional[str]:
        """
        Get news URL for a team

        Args:
            team: Team name (e.g., "Barcelona")
            league: League name (e.g., "La Liga")

        Returns:
            URL string or None if not found
        """
        if league not in self.news_urls:
            return None

        team_key = team.lower()
        url = self.news_urls[league].get(team_key)

        if url == "NOT_FOUND" or not url:
            return None

        return url

    def get_sofascore_url(self, team: str, league: str) -> Optional[Dict]:
        """
        Get SofaScore URL and team ID for a team

        Args:
            team: Team name (e.g., "Barcelona")
            league: League name (e.g., "La Liga")

        Returns:
            Dict with 'url' and 'team_id' or None if not found
        """
        if league not in self.sofascore_urls:
            return None

        team_key = team.lower()
        data = self.sofascore_urls[league].get(team_key)

        if not data or data.get('url') == "NOT_FOUND":
            return None

        return data

    def get_sportsmole_url(self, team: str, league: str) -> Optional[str]:
        """
        Get SportsMole URL for a team (news and form context)

        Args:
            team: Team name (e.g., "Barcelona")
            league: League name (e.g., "La Liga")

        Returns:
            URL string or None if not found
        """
        if league not in self.sportsmole_urls:
            return None

        team_key = team.lower()
        url = self.sportsmole_urls[league].get(team_key)

        if url == "NOT_FOUND" or not url:
            return None

        return url

    def get_all_teams_in_league(self, league: str) -> list:
        """Get list of all teams in a league"""
        if league not in self.news_urls:
            return []

        return list(self.news_urls[league].keys())

    def get_coverage_stats(self) -> Dict:
        """Get database coverage statistics"""
        stats = {
            'leagues': {},
            'total': {
                'teams': 0,
                'news_urls': 0,
                'sofascore_urls': 0
            }
        }

        # News URLs stats
        for league, teams in self.news_urls.items():
            found = sum(1 for url in teams.values() if url != "NOT_FOUND")
            stats['leagues'][league] = {
                'teams': len(teams),
                'news_urls': found,
                'news_coverage': f"{found/len(teams)*100:.1f}%" if teams else "0%"
            }
            stats['total']['teams'] += len(teams)
            stats['total']['news_urls'] += found

        # SofaScore URLs stats
        for league, teams in self.sofascore_urls.items():
            if league not in stats['leagues']:
                stats['leagues'][league] = {'teams': len(teams)}

            found = sum(1 for data in teams.values() if data.get('url') != "NOT_FOUND")
            stats['leagues'][league]['sofascore_urls'] = found
            stats['leagues'][league]['sofascore_coverage'] = f"{found/len(teams)*100:.1f}%" if teams else "0%"
            stats['total']['sofascore_urls'] += found

        return stats


def print_coverage_report():
    """Print comprehensive coverage report"""
    helper = TeamURLsHelper()
    stats = helper.get_coverage_stats()

    print("\n" + "="*80)
    print("TEAM URLs DATABASE COVERAGE REPORT")
    print("="*80)

    for league, data in sorted(stats['leagues'].items()):
        print(f"\n{league}:")
        print(f"  Teams: {data['teams']}")
        if 'news_urls' in data:
            print(f"  News URLs: {data['news_urls']} ({data['news_coverage']})")
        if 'sofascore_urls' in data:
            print(f"  SofaScore URLs: {data['sofascore_urls']} ({data['sofascore_coverage']})")

    print("\n" + "="*80)
    print("TOTAL SUMMARY")
    print("="*80)
    print(f"  Total teams: {stats['total']['teams']}")
    print(f"  News URLs: {stats['total']['news_urls']} ({stats['total']['news_urls']/stats['total']['teams']*100:.1f}%)")
    print(f"  SofaScore URLs: {stats['total']['sofascore_urls']} ({stats['total']['sofascore_urls']/stats['total']['teams']*100 if stats['total']['teams'] > 0 else 0:.1f}%)")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Test usage
    helper = TeamURLsHelper()

    # Test news URL
    print("Testing TeamURLsHelper...")
    print("\n1. Getting Barcelona news URL (La Liga):")
    url = helper.get_news_url("Barcelona", "La Liga")
    print(f"   {url}")

    print("\n2. Getting Santos news URL (Brasileirão):")
    url = helper.get_news_url("Santos", "Brasileirão")
    print(f"   {url}")

    print("\n3. Getting all teams in La Liga:")
    teams = helper.get_all_teams_in_league("La Liga")
    print(f"   Found {len(teams)} teams: {', '.join(teams[:5])}...")

    # Coverage report
    print_coverage_report()
