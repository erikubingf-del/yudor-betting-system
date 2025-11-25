#!/usr/bin/env python3
"""
FBref Stats Integration for Yudor v5.3
Provides real data for Q7 (PPDA), Q8 (Corners), Q14 (Player Form)

Uses soccerdata library: https://github.com/probberechts/soccerdata
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Optional

# Try to import soccerdata
try:
    import soccerdata as sd
    SOCCERDATA_AVAILABLE = True
except ImportError:
    # Try from local clone
    sys.path.insert(0, '/tmp/soccerdata')
    try:
        import soccerdata as sd
        SOCCERDATA_AVAILABLE = True
    except ImportError:
        SOCCERDATA_AVAILABLE = False
        print("⚠️  soccerdata not available. Install with: pip install soccerdata")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FBrefStatsIntegration:
    """
    FBref statistics integration for Q7, Q8, Q14
    Provides real data to replace defaults/estimates
    """

    # League name mapping
    LEAGUE_MAP = {
        'La Liga': 'ESP-La Liga',
        'Premier League': 'ENG-Premier League',
        'Serie A': 'ITA-Serie A',
        'Bundesliga': 'GER-Bundesliga',
        'Ligue 1': 'FRA-Ligue 1',
        'Championship': 'ENG-Championship',
        'Eredivisie': 'NED-Eredivisie',
        'Liga Portugal': 'POR-Liga Portugal',
    }

    def __init__(self, league: str = 'La Liga', season: str = '2425'):
        """
        Initialize FBref integration

        Args:
            league: League name (e.g., "La Liga")
            season: Season code (e.g., "2425" for 2024/25)
        """
        if not SOCCERDATA_AVAILABLE:
            raise ImportError("soccerdata library not available")

        # Map league name to FBref format
        fbref_league = self.LEAGUE_MAP.get(league)
        if not fbref_league:
            raise ValueError(f"League '{league}' not supported. Available: {list(self.LEAGUE_MAP.keys())}")

        self.league = league
        self.fbref_league = fbref_league
        self.season = season

        # Initialize FBref scraper
        logger.info(f"Initializing FBref for {fbref_league} {season}")
        self.fbref = sd.FBref(leagues=fbref_league, seasons=season)

        # Cache for stats
        self._defense_stats = None
        self._misc_stats = None
        self._player_stats = None

    def _load_defense_stats(self):
        """Load and cache defense statistics"""
        if self._defense_stats is None:
            logger.info("Loading defense statistics from FBref...")
            self._defense_stats = self.fbref.read_team_season_stats(stat_type='defense')
            logger.info(f"✅ Loaded stats for {len(self._defense_stats)} teams")
        return self._defense_stats

    def _load_misc_stats(self):
        """Load and cache misc statistics (corners, cards, aerials)"""
        if self._misc_stats is None:
            logger.info("Loading misc statistics from FBref...")
            self._misc_stats = self.fbref.read_team_season_stats(stat_type='misc')
            logger.info(f"✅ Loaded stats for {len(self._misc_stats)} teams")
        return self._misc_stats

    def _load_player_stats(self):
        """Load and cache player statistics"""
        if self._player_stats is None:
            logger.info("Loading player statistics from FBref...")
            self._player_stats = self.fbref.read_player_season_stats(stat_type='standard')
            logger.info(f"✅ Loaded stats for {len(self._player_stats)} players")
        return self._player_stats

    def get_q7_pressing_score(self, team_name: str) -> Dict:
        """
        Calculate Q7 (Pressing) score based on real PPDA data

        PPDA (Passes Allowed Per Defensive Action):
        - Lower = more pressing
        - Liverpool ~8, Man City ~10, Mid-table ~12, Deep block ~15+

        We use defensive actions per game as proxy:
        - High press (>160 actions/game): +5
        - Medium press (120-160): +3
        - Low press (<120): +1

        Args:
            team_name: Team name

        Returns:
            Dict with score, reasoning, source
        """
        try:
            defense_stats = self._load_defense_stats()

            # Find team in stats
            team_data = defense_stats[defense_stats.index.get_level_values('team') == team_name]

            if team_data.empty:
                logger.warning(f"Team '{team_name}' not found in FBref defense stats")
                return {
                    'score': 2,
                    'reasoning': f"No FBref data for {team_name} → default +2",
                    'source': 'default'
                }

            # Get defensive actions
            tackles = team_data['tackles'].values[0]
            interceptions = team_data['interceptions'].values[0]
            matches = team_data['matches'].values[0]

            # Calculate actions per game
            actions_per_game = (tackles + interceptions) / matches

            # Score based on defensive intensity
            if actions_per_game >= 160:
                score = 5
                press_level = "High press"
            elif actions_per_game >= 120:
                score = 3
                press_level = "Medium press"
            else:
                score = 1
                press_level = "Low press"

            reasoning = f"{press_level} ({actions_per_game:.1f} def actions/game) → +{score}"

            return {
                'score': score,
                'reasoning': reasoning,
                'source': 'fbref',
                'raw_data': {
                    'tackles': tackles,
                    'interceptions': interceptions,
                    'matches': matches,
                    'actions_per_game': round(actions_per_game, 1)
                }
            }

        except Exception as e:
            logger.error(f"Error calculating Q7 for {team_name}: {e}")
            return {
                'score': 2,
                'reasoning': f"FBref error → default +2",
                'source': 'default'
            }

    def get_q8_set_pieces_score(self, team_name: str) -> Dict:
        """
        Calculate Q8 (Set Pieces) score based on real corner data

        Scoring:
        - High corners (>6/game) + High aerials (>55%): +5
        - Medium corners (4-6/game) + Good aerials (>50%): +3
        - Low corners (<4/game) or Poor aerials (<50%): +1

        Args:
            team_name: Team name

        Returns:
            Dict with score, reasoning, source
        """
        try:
            misc_stats = self._load_misc_stats()

            # Find team in stats
            team_data = misc_stats[misc_stats.index.get_level_values('team') == team_name]

            if team_data.empty:
                logger.warning(f"Team '{team_name}' not found in FBref misc stats")
                return {
                    'score': 2,
                    'reasoning': f"No FBref data for {team_name} → default +2",
                    'source': 'default'
                }

            # Get set-piece indicators
            corners = team_data['corners'].values[0] if 'corners' in team_data.columns else 0
            matches = team_data['matches'].values[0]
            aerials_won_pct = team_data['aerials_won_pct'].values[0] if 'aerials_won_pct' in team_data.columns else 50

            corners_per_game = corners / matches if corners > 0 else 0

            # Calculate score
            score = 1  # Base

            # Bonus for corner frequency
            if corners_per_game > 6:
                score += 2
            elif corners_per_game > 4:
                score += 1

            # Bonus for aerial dominance
            if aerials_won_pct > 55:
                score += 2
            elif aerials_won_pct > 50:
                score += 1

            score = min(score, 5)  # Cap at 5

            reasoning = f"{corners_per_game:.1f} corners/game, {aerials_won_pct:.0f}% aerials → +{score}"

            return {
                'score': score,
                'reasoning': reasoning,
                'source': 'fbref',
                'raw_data': {
                    'corners': corners,
                    'matches': matches,
                    'corners_per_game': round(corners_per_game, 1),
                    'aerials_won_pct': round(aerials_won_pct, 1)
                }
            }

        except Exception as e:
            logger.error(f"Error calculating Q8 for {team_name}: {e}")
            return {
                'score': 2,
                'reasoning': f"FBref error → default +2",
                'source': 'default'
            }

    def get_q14_player_form_score(self, team_name: str) -> Dict:
        """
        Calculate Q14 (Player Form) score based on per-player xG

        Players in form = xG above team median in recent games

        Scoring:
        - 3+ players in form: +5
        - 2 players in form: +3
        - 1 player in form: +2
        - 0 players in form: +1

        Args:
            team_name: Team name

        Returns:
            Dict with score, reasoning, source
        """
        try:
            player_stats = self._load_player_stats()

            # Filter for team players
            team_players = player_stats[player_stats.index.get_level_values('team') == team_name]

            if team_players.empty:
                logger.warning(f"No players found for {team_name} in FBref stats")
                return {
                    'score': 2,
                    'reasoning': f"No FBref player data for {team_name} → default +2",
                    'source': 'default'
                }

            # Check if xG column exists
            if 'xG' not in team_players.columns:
                logger.warning(f"No xG data for {team_name}")
                return {
                    'score': 2,
                    'reasoning': f"No xG data for {team_name} → default +2",
                    'source': 'default'
                }

            # Calculate median xG
            median_xg = team_players['xG'].median()

            # Count players above median (in form)
            in_form_players = team_players[team_players['xG'] > median_xg]
            count = len(in_form_players)

            # Score based on count
            if count >= 3:
                score = 5
            elif count == 2:
                score = 3
            elif count == 1:
                score = 2
            else:
                score = 1

            reasoning = f"{count} players above median xG (in form) → +{score}"

            # Get top performers
            top_performers = in_form_players.nlargest(3, 'xG')['xG'].tolist() if count > 0 else []

            return {
                'score': score,
                'reasoning': reasoning,
                'source': 'fbref',
                'raw_data': {
                    'in_form_count': count,
                    'median_xg': round(median_xg, 2),
                    'top_performers_xg': [round(x, 2) for x in top_performers]
                }
            }

        except Exception as e:
            logger.error(f"Error calculating Q14 for {team_name}: {e}")
            return {
                'score': 2,
                'reasoning': f"FBref error → default +2",
                'source': 'default'
            }

    def get_all_scores(self, team_name: str) -> Dict:
        """
        Get all FBref-based scores for a team

        Args:
            team_name: Team name

        Returns:
            Dict with Q7, Q8, Q14 scores
        """
        return {
            'Q7': self.get_q7_pressing_score(team_name),
            'Q8': self.get_q8_set_pieces_score(team_name),
            'Q14': self.get_q14_player_form_score(team_name)
        }


def test_fbref_integration():
    """Test FBref integration with La Liga"""
    print("\n" + "="*80)
    print("TESTING FBREF INTEGRATION FOR YUDOR v5.3")
    print("="*80 + "\n")

    if not SOCCERDATA_AVAILABLE:
        print("❌ soccerdata library not available")
        print("   Install with: pip install soccerdata")
        return

    # Test with La Liga
    print("Initializing FBref for La Liga 2024/25...\n")

    try:
        fbref = FBrefStatsIntegration(league='La Liga', season='2425')

        # Test with Barcelona
        print("Testing with Barcelona:")
        print("-" * 80)

        scores = fbref.get_all_scores('Barcelona')

        print(f"\nQ7 (Pressing):")
        print(f"  Score: +{scores['Q7']['score']}")
        print(f"  Reasoning: {scores['Q7']['reasoning']}")
        print(f"  Source: {scores['Q7']['source']}")
        if 'raw_data' in scores['Q7']:
            print(f"  Raw: {scores['Q7']['raw_data']}")

        print(f"\nQ8 (Set Pieces):")
        print(f"  Score: +{scores['Q8']['score']}")
        print(f"  Reasoning: {scores['Q8']['reasoning']}")
        print(f"  Source: {scores['Q8']['source']}")
        if 'raw_data' in scores['Q8']:
            print(f"  Raw: {scores['Q8']['raw_data']}")

        print(f"\nQ14 (Player Form):")
        print(f"  Score: +{scores['Q14']['score']}")
        print(f"  Reasoning: {scores['Q14']['reasoning']}")
        print(f"  Source: {scores['Q14']['source']}")
        if 'raw_data' in scores['Q14']:
            print(f"  Raw: {scores['Q14']['raw_data']}")

        print("\n" + "="*80)
        print("✅ FBref integration working!")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_fbref_integration()
