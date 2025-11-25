#!/usr/bin/env python3
"""
Complete Match Analyzer - Automated System
Performs ALL data collection and analysis for a match in one command

Usage:
    python3 scripts/complete_match_analyzer.py "Barcelona" "Sevilla" "La Liga"
"""
import sys
sys.path.insert(0, '/tmp/soccerdata')

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from comprehensive_stats_scraper import ComprehensiveStatsScraper
from team_urls_helper import TeamURLsHelper
from sportsmole_match_finder import get_sportsmole_match_url


class TeamNameMatcher:
    """
    Automatic team name matching for different data sources

    Different data sources use different team name formats:
    - FBref: "Espanyol", "Athletic Bilbao", "Real Sociedad"
    - MatchHistory: "Espanol", "Ath Bilbao", "Sociedad"

    This class automatically finds the best match using fuzzy matching.
    """

    def __init__(self):
        self._cache = {}  # Cache matches to avoid recomputation

    def find_best_match(self, team_name: str, available_teams: list) -> str:
        """
        Find the best matching team name from a list of available teams

        Uses multiple strategies:
        1. Exact match (case-insensitive)
        2. Contains match (e.g., "Espanyol" contains in "Espanol")
        3. Similarity score (Levenshtein distance)

        Args:
            team_name: Team name to match (e.g., "Espanyol")
            available_teams: List of available team names in the database

        Returns:
            Best matching team name from the database
        """
        # Check cache first
        cache_key = (team_name.lower(), tuple(sorted(available_teams)))
        if cache_key in self._cache:
            return self._cache[cache_key]

        team_lower = team_name.lower()

        # Strategy 1: Exact match (case-insensitive)
        for available in available_teams:
            if available.lower() == team_lower:
                self._cache[cache_key] = available
                return available

        # Strategy 2: Character-level similarity (handles "Espanyol" -> "Espanol")
        best_match = None
        best_score = 0

        for available in available_teams:
            available_lower = available.lower()

            # Calculate character-level similarity
            # Count matching characters in order
            matches = 0
            j = 0
            for i, char in enumerate(team_lower):
                while j < len(available_lower) and available_lower[j] != char:
                    j += 1
                if j < len(available_lower):
                    matches += 1
                    j += 1

            # Calculate similarity score
            score = matches / max(len(team_lower), len(available_lower))

            if score > best_score:
                best_score = score
                best_match = available

        # Don't return yet - continue to word-based matching for better results

        # Strategy 3: Word-based matching (handles "Athletic Club Bilbao" -> "Ath Bilbao")
        # Remove common stopwords that don't help with matching
        stopwords = {'fc', 'cf', 'club', 'de', 'rcd', 'real', 'cd', 'ud', 'sd', 'balompie', 'futbol'}

        team_words = set(word for word in team_lower.split() if word not in stopwords)

        for available in available_teams:
            available_words = set(word for word in available.lower().split() if word not in stopwords)

            # Check if significant words overlap
            common_words = team_words & available_words
            if len(common_words) >= 1:  # At least one word in common
                # Calculate Jaccard similarity
                score = len(common_words) / len(team_words | available_words) if (team_words | available_words) else 0

                # Boost score if most important words match
                if len(team_words) > 0 and len(common_words) / len(team_words) > 0.5:
                    score += 0.2  # Boost for matching majority of non-stopwords

                if score > best_score:
                    best_score = score
                    best_match = available

        # Strategy 4: Abbreviation matching (handles "Ath" in "Athletic")
        if best_score < 0.5:
            for available in available_teams:
                # Check if available is an abbreviation of team_name or vice versa
                if self._is_abbreviation(team_lower, available.lower()):
                    best_match = available
                    best_score = 0.9
                    break

        # Return best match if score is reasonable (>0.4), otherwise return original
        # Lower threshold allows matching with stopwords removed
        result = best_match if best_match and best_score > 0.4 else team_name
        self._cache[cache_key] = result
        return result

    def _is_abbreviation(self, full_name: str, abbrev: str) -> bool:
        """Check if abbrev is an abbreviation of full_name"""
        # "Athletic Bilbao" -> "Ath Bilbao"
        words = full_name.split()
        abbrev_words = abbrev.split()

        if len(words) != len(abbrev_words):
            return False

        for word, abbrev_word in zip(words, abbrev_words):
            if not (word.startswith(abbrev_word) or abbrev_word.startswith(word)):
                return False

        return True


# Global team name matcher instance
_team_matcher = TeamNameMatcher()


class CompleteMatchAnalyzer:
    """
    Complete automated match analysis system

    Features:
    - Fetches ALL soccerdata sources (FBref, Understat, ClubElo, match_history, FotMob)
    - Gets team news URLs from database
    - Calculates H2H from match_history
    - Provides complete data package ready for Claude AI
    """

    def __init__(self, league: str, season: str = '2425'):
        """Initialize analyzer with league and season"""
        self.league = league
        self.season = season

        # Initialize scrapers
        print(f"\n{'='*80}")
        print(f"INITIALIZING COMPLETE MATCH ANALYZER")
        print(f"League: {league} | Season: {season}")
        print('='*80 + "\n")

        self.stats_scraper = ComprehensiveStatsScraper(league=league, season=season)
        self.url_helper = TeamURLsHelper()

        # Cache available team names from MatchHistory for automatic matching
        self._available_teams_cache = None

        print(f"✅ All systems initialized\n")

    def _get_available_teams(self) -> list:
        """Get list of all available team names in MatchHistory database (cached)"""
        if self._available_teams_cache is not None:
            return self._available_teams_cache

        try:
            if self.stats_scraper.match_history:
                games = self.stats_scraper.match_history.read_games()
                home_teams = set(games['home_team'].unique())
                away_teams = set(games['away_team'].unique())
                self._available_teams_cache = list(home_teams | away_teams)
            else:
                self._available_teams_cache = []
        except Exception:
            self._available_teams_cache = []

        return self._available_teams_cache

    def analyze_match(self, home_team: str, away_team: str) -> Dict:
        """
        Complete match analysis - ONE command does everything!

        Returns:
            Complete data package with:
            - All stats from 5 sources (FBref, Understat, ClubElo, match_history, FotMob)
            - Team news URLs
            - H2H analysis
            - Data quality scores
        """
        print(f"\n{'='*80}")
        print(f"COMPLETE MATCH ANALYSIS")
        print(f"{home_team} vs {away_team}")
        print('='*80 + "\n")

        match_data = {
            'match_info': {
                'home_team': home_team,
                'away_team': away_team,
                'league': self.league,
                'season': self.season,
                'analysis_date': datetime.now().isoformat()
            },
            'home_team_data': {},
            'away_team_data': {},
            'head_to_head': {},
            'team_news_urls': {},
            'summary': {}
        }

        # 1. Get comprehensive stats for both teams
        print("📊 STEP 1: Fetching comprehensive statistics...")
        print("-" * 80)

        print(f"\n🏠 {home_team} (Home):")
        match_data['home_team_data'] = self.stats_scraper.get_all_team_stats(home_team)

        print(f"\n✈️  {away_team} (Away):")
        match_data['away_team_data'] = self.stats_scraper.get_all_team_stats(away_team)

        # 2. Get team news URLs
        print(f"\n📰 STEP 2: Getting team news URLs...")
        print("-" * 80)

        home_news_url = self.url_helper.get_news_url(home_team, self.league)
        away_news_url = self.url_helper.get_news_url(away_team, self.league)

        match_data['team_news_urls'] = {
            'home': home_news_url if home_news_url else "NOT_FOUND",
            'away': away_news_url if away_news_url else "NOT_FOUND"
        }

        if home_news_url:
            print(f"✅ {home_team} (Marca): {home_news_url}")
        else:
            print(f"❌ {home_team} (Marca): No URL found")

        if away_news_url:
            print(f"✅ {away_team} (Marca): {away_news_url}")
        else:
            print(f"❌ {away_team} (Marca): No URL found")

        # 2b. Get SportsMole match preview URL (crucial for news and form context)
        print(f"\n🏆 Getting SportsMole match preview URL...")
        print("-" * 80)

        sportsmole_url = get_sportsmole_match_url(home_team, away_team, method='both')

        match_data['sportsmole_preview_url'] = sportsmole_url if sportsmole_url else "NOT_FOUND"

        if sportsmole_url:
            print(f"✅ Match preview: {sportsmole_url}")
        else:
            print(f"❌ Match preview: Not found (may not be available yet)")

        # 3. Calculate head-to-head from match_history
        print(f"\n⚔️  STEP 3: Calculating head-to-head...")
        print("-" * 80)

        h2h = self._calculate_h2h(home_team, away_team)
        match_data['head_to_head'] = h2h

        if h2h['total_matches'] > 0:
            print(f"✅ Found {h2h['total_matches']} H2H matches")
            print(f"   {home_team}: {h2h['home_wins']}W {h2h['draws']}D {h2h['away_wins']}L")
            print(f"   Goals: {h2h['home_goals']}-{h2h['away_goals']}")
        else:
            print(f"⚠️  No H2H matches found in current season")

        # 4. Calculate summary
        print(f"\n📈 STEP 4: Generating summary...")
        print("-" * 80)

        match_data['summary'] = self._generate_summary(match_data)

        # Print summary
        summary = match_data['summary']
        print(f"\n✅ ANALYSIS COMPLETE!")
        print(f"   Total sources: {summary['total_sources']}")
        print(f"   Data quality: {summary['overall_quality']}/5.0")
        print(f"   Coverage: {summary['coverage_score']}")
        print(f"   Ready for Claude AI: {'✅ YES' if summary['ready_for_analysis'] else '❌ NO'}")

        return match_data

    def _calculate_h2h(self, home_team: str, away_team: str) -> Dict:
        """Calculate head-to-head record from match_history with automatic team name matching"""
        import pandas as pd

        h2h = {
            'home_wins': 0,
            'draws': 0,
            'away_wins': 0,
            'home_goals': 0,
            'away_goals': 0,
            'total_matches': 0,
            'last_5_results': [],
            'recent_meetings': []
        }

        try:
            # Get all games from match_history
            games = self.stats_scraper.match_history.read_games()

            # Get available team names from database
            available_teams = self._get_available_teams()

            # Automatically find best matching team names using fuzzy matching
            # This handles variations like "Espanyol" -> "Espanol", "Athletic Bilbao" -> "Ath Bilbao"
            home_team_normalized = _team_matcher.find_best_match(home_team, available_teams)
            away_team_normalized = _team_matcher.find_best_match(away_team, available_teams)

            # Filter for matches between these two teams (using normalized names)
            h2h_matches = games[
                ((games['home_team'] == home_team_normalized) & (games['away_team'] == away_team_normalized)) |
                ((games['home_team'] == away_team_normalized) & (games['away_team'] == home_team_normalized))
            ]

            if not h2h_matches.empty:
                h2h['total_matches'] = len(h2h_matches)

                # Calculate H2H record
                for idx, match in h2h_matches.iterrows():
                    home_score = match['FTHG']  # Full Time Home Goals
                    away_score = match['FTAG']  # Full Time Away Goals

                    if pd.notna(home_score) and pd.notna(away_score):
                        # Determine result from home_team's perspective (using normalized names for comparison)
                        if match['home_team'] == home_team_normalized:
                            # home_team was playing at home
                            h2h['home_goals'] += int(home_score)
                            h2h['away_goals'] += int(away_score)
                            if home_score > away_score:
                                h2h['home_wins'] += 1
                                result = 'W'
                            elif home_score < away_score:
                                h2h['away_wins'] += 1
                                result = 'L'
                            else:
                                h2h['draws'] += 1
                                result = 'D'
                        else:
                            # home_team was playing away
                            h2h['home_goals'] += int(away_score)
                            h2h['away_goals'] += int(home_score)
                            if away_score > home_score:
                                h2h['home_wins'] += 1
                                result = 'W'
                            elif away_score < home_score:
                                h2h['away_wins'] += 1
                                result = 'L'
                            else:
                                h2h['draws'] += 1
                                result = 'D'

                        # Add to recent meetings
                        h2h['recent_meetings'].append({
                            'date': str(match.get('date', 'Unknown')),
                            'home': match['home_team'],
                            'away': match['away_team'],
                            'score': f"{int(home_score)}-{int(away_score)}",
                            'result_for_home_team': result
                        })

                # Get last 5 results
                h2h['last_5_results'] = [m['result_for_home_team'] for m in h2h['recent_meetings'][-5:]]

        except Exception as e:
            print(f"⚠️  H2H calculation error: {e}")

        return h2h

    def _generate_summary(self, match_data: Dict) -> Dict:
        """Generate analysis summary"""
        home_sources = len(match_data['home_team_data']['sources_available'])
        away_sources = len(match_data['away_team_data']['sources_available'])

        home_quality = match_data['home_team_data']['overall_data_quality']
        away_quality = match_data['away_team_data']['overall_data_quality']

        summary = {
            'total_sources': home_sources + away_sources,
            'home_sources': home_sources,
            'away_sources': away_sources,
            'overall_quality': round((home_quality + away_quality) / 2, 1),
            'home_quality': home_quality,
            'away_quality': away_quality,
            'coverage_score': 'EXCELLENT' if (home_sources >= 4 and away_sources >= 4) else
                            'GOOD' if (home_sources >= 3 and away_sources >= 3) else
                            'FAIR' if (home_sources >= 2 and away_sources >= 2) else 'POOR',
            'ready_for_analysis': (home_sources >= 3 and away_sources >= 3),
            'sources_breakdown': {
                'fbref': ('fbref' in match_data['home_team_data']['sources_available'] and
                         'fbref' in match_data['away_team_data']['sources_available']),
                'understat': ('understat' in match_data['home_team_data']['sources_available'] and
                            'understat' in match_data['away_team_data']['sources_available']),
                'clubelo': ('clubelo' in match_data['home_team_data']['sources_available'] and
                           'clubelo' in match_data['away_team_data']['sources_available']),
                'match_history': ('match_history' in match_data['home_team_data']['sources_available'] and
                                'match_history' in match_data['away_team_data']['sources_available'])
            }
        }

        return summary

    def _convert_to_json_serializable(self, obj):
        """Convert objects to JSON-serializable format (handle tuple keys)"""
        if isinstance(obj, dict):
            # Convert tuple keys to strings
            return {
                (str(k) if isinstance(k, tuple) else k): self._convert_to_json_serializable(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        else:
            return obj

    def save_analysis(self, match_data: Dict, output_file: Optional[str] = None) -> str:
        """Save analysis to JSON file in appropriate quality folder"""
        if not output_file:
            home = match_data['match_info']['home_team'].replace(' ', '_')
            away = match_data['match_info']['away_team'].replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Determine quality level and target folder
            summary = match_data.get('summary', {})
            total_sources = summary.get('total_sources', 0)

            scraped_folder = Path(__file__).parent.parent / 'scraped_data'

            if total_sources >= 5:
                # High quality: 5+ sources
                target_folder = scraped_folder / 'high_quality'
            else:
                # Low/Medium quality: for learning purposes
                target_folder = scraped_folder / 'low_quality'

            target_folder.mkdir(parents=True, exist_ok=True)
            output_file = target_folder / f"match_analysis_{home}_vs_{away}_{timestamp}.json"

        output_path = Path(output_file)

        # Convert to JSON-serializable format
        serializable_data = self._convert_to_json_serializable(match_data)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Analysis saved to: {output_path}")
        return str(output_path)


def main():
    """CLI interface"""
    if len(sys.argv) < 4:
        print("Usage: python3 complete_match_analyzer.py HOME_TEAM AWAY_TEAM LEAGUE [SEASON]")
        print("\nExamples:")
        print('  python3 complete_match_analyzer.py "Barcelona" "Sevilla" "La Liga"')
        print('  python3 complete_match_analyzer.py "Liverpool" "Arsenal" "Premier League"')
        print('  python3 complete_match_analyzer.py "Inter" "Juventus" "Serie A" "2425"')
        sys.exit(1)

    home_team = sys.argv[1]
    away_team = sys.argv[2]
    league = sys.argv[3]
    season = sys.argv[4] if len(sys.argv) > 4 else '2425'

    # Initialize analyzer
    analyzer = CompleteMatchAnalyzer(league=league, season=season)

    # Run complete analysis
    match_data = analyzer.analyze_match(home_team, away_team)

    # Save results
    output_file = analyzer.save_analysis(match_data)

    # Print final summary
    print(f"\n{'='*80}")
    print("🎯 ANALYSIS READY FOR CLAUDE AI!")
    print('='*80)
    print(f"\n✅ Complete data package created")
    print(f"✅ All sources fetched: {match_data['summary']['total_sources']} sources")
    print(f"✅ Data quality: {match_data['summary']['overall_quality']}/5.0")
    print(f"✅ Saved to: {output_file}")
    print(f"\nYou can now use this data for Q1-Q19 analysis with Claude AI!")
    print('='*80 + "\n")


if __name__ == "__main__":
    main()
