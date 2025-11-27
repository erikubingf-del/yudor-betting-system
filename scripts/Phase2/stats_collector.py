#!/usr/bin/env python3
"""
Comprehensive Stats Scraper for Yudor v5.3
Fetches ALL available statistics from soccerdata (FBref, FotMob, SofaScore, etc.)

Purpose: Maximize information for Claude AI to analyze Q1-Q19 without hallucinating
Strategy: Use multiple sources, provide fallbacks, document data quality
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

# Try to import soccerdata
try:
    import soccerdata as sd
    from soccerdata._config import LEAGUE_DICT
    SOCCERDATA_AVAILABLE = True
except ImportError:
    sys.path.insert(0, '/tmp/soccerdata')
    try:
        import soccerdata as sd
        from soccerdata._config import LEAGUE_DICT
        SOCCERDATA_AVAILABLE = True
    except ImportError:
        SOCCERDATA_AVAILABLE = False
        print("⚠️  soccerdata not available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveStatsScraper:
    """
    Fetch ALL available statistics from multiple sources
    to ensure Claude AI has maximum information
    """

    LEAGUE_MAP = {
        'La Liga': 'ESP-La Liga',
        'Premier League': 'ENG-Premier League',
        'Serie A': 'ITA-Serie A',
        'Bundesliga': 'GER-Bundesliga',
        'Ligue 1': 'FRA-Ligue 1',
        'Championship': 'ENG-Championship',
        'Eredivisie': 'NED-Eredivisie',
        'Liga Portugal': 'POR-Liga Portugal',
        'Brasileirão': 'BRA-Serie A',
    }

    def __init__(self, league: str = 'La Liga', season: str = '2425'):
        """Initialize all available data sources"""
        if not SOCCERDATA_AVAILABLE:
            raise ImportError("soccerdata library not available")

        self.league = league
        fbref_league = self.LEAGUE_MAP.get(league, league)
        self.season = season

        # Initialize all sources
        logger.info(f"Initializing comprehensive scraper for {league} {season}")

        # Manually add Brazil to soccerdata config if missing
        if "BRA-Serie A" not in LEAGUE_DICT:
            LEAGUE_DICT["BRA-Serie A"] = {
                "ClubElo": "BRA_1",
                "MatchHistory": "BRA1",
                "FBref": "Campeonato Brasileiro Série A",
                "FotMob": "BRA-Serie A",
                "season_start": "Apr",
                "season_end": "Dec"
            }
            logger.info("🇧🇷 Added Brazil Serie A to soccerdata config")

        try:
            self.fbref = sd.FBref(leagues=fbref_league, seasons=season)
            logger.info("✅ FBref initialized")
        except Exception as e:
            logger.warning(f"⚠️  FBref failed: {e}")
            self.fbref = None

        # TEMPORARILY DISABLED: SofaScore has 404 errors due to league mapping bug in soccerdata
        # TODO: Re-enable when soccerdata fixes hardcoded "EN" in sofascore.py line 80
        # try:
        #     self.sofascore = sd.Sofascore(leagues=fbref_league, seasons=season)
        #     logger.info("✅ SofaScore initialized")
        # except Exception as e:
        #     logger.warning(f"⚠️  SofaScore failed: {e}")
        #     self.sofascore = None
        logger.info("⏸️  SofaScore DISABLED (league mapping bug - non-critical)")
        self.sofascore = None

        try:
            self.fotmob = sd.FotMob(leagues=fbref_league, seasons=season)
            logger.info("✅ FotMob initialized")
        except Exception as e:
            logger.warning(f"⚠️  FotMob failed: {e}")
            self.fotmob = None

        # Understat - Best xG data source (Priority: VERY HIGH)
        try:
            self.understat = sd.Understat(leagues=fbref_league, seasons=season)
            logger.info("✅ Understat initialized (xG data)")
        except Exception as e:
            logger.warning(f"⚠️  Understat failed: {e}")
            self.understat = None

        # ClubElo - Elo ratings for strength comparison (Priority: HIGH)
        try:
            self.clubelo = sd.ClubElo()
            logger.info("✅ ClubElo initialized (Elo ratings)")
        except Exception as e:
            logger.warning(f"⚠️  ClubElo failed: {e}")
            self.clubelo = None

        # match_history - Historical H2H data (Priority: HIGH)
        # Fetch last 5 seasons for comprehensive H2H analysis
        try:
            # Calculate last 5 seasons
            current_year = int(season[:2])
            last_5_seasons = [f"{current_year-i:02d}{current_year-i+1:02d}" for i in range(5)]

            self.match_history = sd.MatchHistory(leagues=fbref_league, seasons=last_5_seasons)
            logger.info(f"✅ match_history initialized (H2H data for {len(last_5_seasons)} seasons)")
        except Exception as e:
            logger.warning(f"⚠️  match_history failed: {e}")
            self.match_history = None

    def get_all_team_stats(self, team_name: str) -> Dict:
        """
        Get ALL available statistics for a team from all sources

        Returns comprehensive dict with:
        - FBref: defense, possession, passing, shooting, misc, goalkeeper
        - SofaScore: league table position, recent form
        - FotMob: team ratings, momentum
        - Data quality score per source
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"FETCHING COMPREHENSIVE STATS: {team_name}")
        logger.info(f"{'='*80}\n")

        all_stats = {
            'team_name': team_name,
            'sources_available': [],
            'fbref': {},
            'sofascore': {},
            'fotmob': {},
            'understat': {},
            'clubelo': {},
            'match_history': {},
            'data_quality': {}
        }

        # FBref - Most comprehensive source
        if self.fbref:
            all_stats['fbref'] = self._get_fbref_all_stats(team_name)
            if all_stats['fbref']:
                all_stats['sources_available'].append('fbref')
                all_stats['data_quality']['fbref'] = 5

        # SofaScore - League table, form
        if self.sofascore:
            all_stats['sofascore'] = self._get_sofascore_stats(team_name)
            if all_stats['sofascore']:
                all_stats['sources_available'].append('sofascore')
                all_stats['data_quality']['sofascore'] = 4

        # FotMob - Ratings, momentum
        if self.fotmob:
            all_stats['fotmob'] = self._get_fotmob_stats(team_name)
            if all_stats['fotmob']:
                all_stats['sources_available'].append('fotmob')
                all_stats['data_quality']['fotmob'] = 4

        # Understat - xG data (best quality)
        if self.understat:
            all_stats['understat'] = self._get_understat_stats(team_name)
            if all_stats['understat']:
                all_stats['sources_available'].append('understat')
                all_stats['data_quality']['understat'] = 5

        # ClubElo - Elo ratings
        if self.clubelo:
            all_stats['clubelo'] = self._get_clubelo_stats(team_name)
            if all_stats['clubelo']:
                all_stats['sources_available'].append('clubelo')
                all_stats['data_quality']['clubelo'] = 4

        # match_history - Historical data
        if self.match_history:
            all_stats['match_history'] = self._get_match_history_stats(team_name)
            if all_stats['match_history']:
                all_stats['sources_available'].append('match_history')
                all_stats['data_quality']['match_history'] = 4

        # Calculate overall data quality
        quality_scores = list(all_stats['data_quality'].values())
        all_stats['overall_data_quality'] = round(sum(quality_scores) / len(quality_scores), 1) if quality_scores else 0

        logger.info(f"\n✅ Fetched stats from {len(all_stats['sources_available'])} sources")
        logger.info(f"📊 Overall data quality: {all_stats['overall_data_quality']}/5.0\n")

        return all_stats

    def _get_fbref_all_stats(self, team_name: str) -> Dict:
        """Get ALL stat types from FBref"""
        logger.info("Fetching FBref statistics...")

        fbref_stats = {}

        # Available stat types in FBref
        stat_types = [
            'standard',      # Goals, assists, xG, xAG
            'shooting',      # Shots, SoT, conversion rate
            'passing',       # Pass completion, key passes
            'passing_types', # Through balls, crosses
            'gca',          # Goal/shot creating actions
            'defense',      # Tackles, interceptions, blocks
            'possession',   # Touches, dribbles, carries
            'playing_time', # Minutes, starts, subs
            'misc',         # Cards, aerials, fouls
            'keeper',       # Saves, clean sheets (if GK stats available)
        ]

        for stat_type in stat_types:
            try:
                stats = self.fbref.read_team_season_stats(stat_type=stat_type)
                team_data = stats[stats.index.get_level_values('team') == team_name]

                if not team_data.empty:
                    # Convert to dict, keeping only numeric values
                    stat_dict = {}
                    for col in team_data.columns:
                        try:
                            value = team_data[col].values[0]
                            if pd.notna(value):  # Skip NaN values
                                stat_dict[col] = float(value) if isinstance(value, (int, float)) else str(value)
                        except:
                            pass

                    fbref_stats[stat_type] = stat_dict
                    logger.info(f"  ✅ {stat_type}: {len(stat_dict)} metrics")

            except Exception as e:
                logger.debug(f"  ⚠️  {stat_type} not available: {e}")
                continue

        # Get player stats for Q14 (player form)
        try:
            player_stats = self.fbref.read_player_season_stats(stat_type='standard')
            team_players = player_stats[player_stats.index.get_level_values('team') == team_name]

            if not team_players.empty:
                # Get top 5 players by minutes
                top_players = team_players.nlargest(5, 'minutes')
                fbref_stats['top_players'] = []

                for idx, player in top_players.iterrows():
                    player_name = idx[0] if isinstance(idx, tuple) else str(idx)
                    fbref_stats['top_players'].append({
                        'name': player_name,
                        'minutes': float(player['minutes']),
                        'goals': float(player.get('goals', 0)),
                        'assists': float(player.get('assists', 0)),
                        'xG': float(player.get('xG', 0)),
                        'xAG': float(player.get('xAG', 0))
                    })

                logger.info(f"  ✅ top_players: {len(fbref_stats['top_players'])} players")

        except Exception as e:
            logger.debug(f"  ⚠️  Player stats not available: {e}")

        return fbref_stats

    def _get_sofascore_stats(self, team_name: str) -> Dict:
        """Get league table and form from SofaScore"""
        logger.info("Fetching SofaScore statistics...")

        sofascore_stats = {}

        try:
            # League table
            table = self.sofascore.read_league_table()
            team_row = table[table.index.get_level_values('team') == team_name]

            if not team_row.empty:
                sofascore_stats['league_table'] = {
                    'position': int(team_row['rank'].values[0]),
                    'points': int(team_row['pts'].values[0]),
                    'wins': int(team_row['w'].values[0]),
                    'draws': int(team_row['d'].values[0]),
                    'losses': int(team_row['l'].values[0]),
                    'goals_for': int(team_row['gf'].values[0]),
                    'goals_against': int(team_row['ga'].values[0]),
                }
                logger.info(f"  ✅ league_table: Position {sofascore_stats['league_table']['position']}")

        except Exception as e:
            logger.debug(f"  ⚠️  League table not available: {e}")

        try:
            # Schedule/results for recent form
            schedule = self.sofascore.read_schedule()
            # Filter team matches and get last 5
            team_matches = schedule[
                (schedule['home_team'] == team_name) |
                (schedule['away_team'] == team_name)
            ].tail(5)

            if not team_matches.empty:
                form = []
                for idx, match in team_matches.iterrows():
                    is_home = match['home_team'] == team_name
                    team_score = match['home_score'] if is_home else match['away_score']
                    opp_score = match['away_score'] if is_home else match['home_score']

                    if team_score > opp_score:
                        result = 'W'
                    elif team_score < opp_score:
                        result = 'L'
                    else:
                        result = 'D'

                    form.append(result)

                sofascore_stats['recent_form'] = ''.join(form)
                logger.info(f"  ✅ recent_form: {sofascore_stats['recent_form']}")

        except Exception as e:
            logger.debug(f"  ⚠️  Recent form not available: {e}")

        return sofascore_stats

    def _get_fotmob_stats(self, team_name: str) -> Dict:
        """Get team ratings from FotMob"""
        logger.info("Fetching FotMob statistics...")

        fotmob_stats = {}

        try:
            # League table (FotMob also has this)
            table = self.fotmob.read_league_table()
            team_row = table[table.index.get_level_values('team') == team_name]

            if not team_row.empty:
                fotmob_stats['league_position'] = int(team_row['idx'].values[0])
                logger.info(f"  ✅ league_position: {fotmob_stats['league_position']}")

        except Exception as e:
            logger.debug(f"  ⚠️  FotMob table not available: {e}")

        return fotmob_stats

    def _get_understat_stats(self, team_name: str) -> Dict:
        """Get xG data from Understat (highest quality xG source)"""
        logger.info("Fetching Understat statistics (xG)...")

        understat_stats = {}

        try:
            # Team match stats (xG per match)
            match_stats = self.understat.read_team_match_stats()

            # Filter for this team (can be home or away)
            team_matches = match_stats[
                (match_stats['home_team'] == team_name) |
                (match_stats['away_team'] == team_name)
            ]

            if not team_matches.empty:
                # Calculate team's xG (home_xg when home, away_xg when away)
                xg_values = []
                xga_values = []

                for idx, match in team_matches.iterrows():
                    if match['home_team'] == team_name:
                        xg_values.append(match['home_xg'])
                        xga_values.append(match['away_xg'])
                    else:
                        xg_values.append(match['away_xg'])
                        xga_values.append(match['home_xg'])

                understat_stats['team_xg'] = {
                    'xG_total': float(sum(xg_values)),
                    'xG_avg': float(sum(xg_values) / len(xg_values)),
                    'xGA_total': float(sum(xga_values)),
                    'xGA_avg': float(sum(xga_values) / len(xga_values)),
                    'matches': len(team_matches)
                }
                logger.info(f"  ✅ team_xg: xG avg {understat_stats['team_xg']['xG_avg']:.2f}")

        except Exception as e:
            logger.debug(f"  ⚠️  Understat team stats not available: {e}")

        try:
            # Player stats (individual xG/xAG for Q14 player form)
            player_stats = self.understat.read_player_season_stats()

            # Filter for this team's players
            team_players = player_stats[player_stats['team'] == team_name]

            if not team_players.empty:
                # Get top 5 players by xG
                top_players = team_players.nlargest(5, 'xG')
                understat_stats['top_players_xg'] = []

                for idx, player in top_players.iterrows():
                    # Player name is in the index
                    player_name = idx[0] if isinstance(idx, tuple) else str(idx)
                    understat_stats['top_players_xg'].append({
                        'name': player_name,
                        'xG': float(player.get('xG', 0)),
                        'xAG': float(player.get('xA', 0)),
                        'goals': int(player.get('goals', 0)),
                        'assists': int(player.get('assists', 0)),
                        'shots': int(player.get('shots', 0)),
                        'minutes': int(player.get('time', 0))
                    })

                logger.info(f"  ✅ top_players_xg: {len(understat_stats['top_players_xg'])} players")

        except Exception as e:
            logger.debug(f"  ⚠️  Understat player stats not available: {e}")

        return understat_stats

    def _get_clubelo_stats(self, team_name: str) -> Dict:
        """Get Elo ratings from ClubElo (objective strength measure)"""
        logger.info("Fetching ClubElo statistics (Elo ratings)...")

        clubelo_stats = {}

        try:
            # Get team history (last 90 days)
            team_history = self.clubelo.read_team_history(team_name, max_age=90)

            if not team_history.empty:
                # Get most recent rating
                latest = team_history.iloc[-1]

                # Calculate 30d change (if available)
                if len(team_history) > 1:
                    # Find row from 30 days ago
                    thirty_days_ago = team_history.iloc[max(0, len(team_history) - 30)]
                    elo_change = float(latest['elo'] - thirty_days_ago['elo'])
                else:
                    elo_change = 0.0

                clubelo_stats['elo_rating'] = {
                    'current_elo': float(latest['elo']),
                    'elo_change_30d': elo_change,
                    'rank': int(latest['rank']) if pd.notna(latest.get('rank')) else None,
                    'level': int(latest['level']) if pd.notna(latest.get('level')) else None
                }
                logger.info(f"  ✅ elo_rating: {clubelo_stats['elo_rating']['current_elo']:.1f}")

        except Exception as e:
            logger.debug(f"  ⚠️  ClubElo ratings not available: {e}")

        return clubelo_stats

    def _get_match_history_stats(self, team_name: str) -> Dict:
        """Get historical match data (H2H, form)"""
        logger.info("Fetching match_history statistics (H2H)...")

        history_stats = {}

        try:
            # Get full schedule (all games in season)
            games = self.match_history.read_games()

            # Filter for this team's matches
            team_matches = games[
                (games['home_team'] == team_name) |
                (games['away_team'] == team_name)
            ]

            if not team_matches.empty:
                # Calculate overall record
                wins = 0
                draws = 0
                losses = 0
                goals_for = 0
                goals_against = 0

                for idx, match in team_matches.iterrows():
                    is_home = match['home_team'] == team_name
                    # FTHG = Full Time Home Goals, FTAG = Full Time Away Goals
                    team_score = match['FTHG'] if is_home else match['FTAG']
                    opp_score = match['FTAG'] if is_home else match['FTHG']

                    if pd.notna(team_score) and pd.notna(opp_score):
                        goals_for += int(team_score)
                        goals_against += int(opp_score)

                        if team_score > opp_score:
                            wins += 1
                        elif team_score < opp_score:
                            losses += 1
                        else:
                            draws += 1

                history_stats['season_record'] = {
                    'wins': wins,
                    'draws': draws,
                    'losses': losses,
                    'goals_for': goals_for,
                    'goals_against': goals_against,
                    'matches': len(team_matches),
                    'points': wins * 3 + draws
                }
                logger.info(f"  ✅ season_record: {wins}W {draws}D {losses}L")

        except Exception as e:
            logger.debug(f"  ⚠️  match_history not available: {e}")

        return history_stats

    def get_comprehensive_match_data(self, home_team: str, away_team: str) -> Dict:
        """
        Get comprehensive data for both teams in a match

        Returns:
            Complete data dict ready for Claude AI analysis
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"COMPREHENSIVE MATCH DATA COLLECTION")
        logger.info(f"{home_team} vs {away_team}")
        logger.info(f"{'='*80}\n")

        match_data = {
            'home_team': home_team,
            'away_team': away_team,
            'home_stats': self.get_all_team_stats(home_team),
            'away_stats': self.get_all_team_stats(away_team),
            'data_completeness': {}
        }

        # Assess data completeness
        home_sources = len(match_data['home_stats']['sources_available'])
        away_sources = len(match_data['away_stats']['sources_available'])

        match_data['data_completeness'] = {
            'home_sources': home_sources,
            'away_sources': away_sources,
            'total_sources': home_sources + away_sources,
            'quality_score': round(
                (match_data['home_stats']['overall_data_quality'] +
                 match_data['away_stats']['overall_data_quality']) / 2,
                1
            ),
            'ready_for_analysis': (home_sources >= 1 and away_sources >= 1)
        }

        logger.info(f"\n{'='*80}")
        logger.info(f"DATA COLLECTION COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Home sources: {home_sources}")
        logger.info(f"Away sources: {away_sources}")
        logger.info(f"Quality score: {match_data['data_completeness']['quality_score']}/5.0")
        logger.info(f"Ready: {match_data['data_completeness']['ready_for_analysis']}\n")

        return match_data


def test_comprehensive_scraper():
    """Test the comprehensive scraper"""
    print("\n" + "="*80)
    print("TESTING COMPREHENSIVE STATS SCRAPER")
    print("="*80 + "\n")

    scraper = ComprehensiveStatsScraper(league='La Liga', season='2425')

    # Test single team
    team_stats = scraper.get_all_team_stats('Barcelona')

    print("\n" + "="*80)
    print("BARCELONA STATS SUMMARY")
    print("="*80)
    print(f"Sources available: {team_stats['sources_available']}")
    print(f"Data quality: {team_stats['overall_data_quality']}/5.0")

    if team_stats['fbref']:
        print(f"\nFBref stat types: {list(team_stats['fbref'].keys())}")
        if 'standard' in team_stats['fbref']:
            print(f"  Goals: {team_stats['fbref']['standard'].get('goals', 'N/A')}")
            print(f"  xG: {team_stats['fbref']['standard'].get('xG', 'N/A')}")

    if team_stats['sofascore']:
        if 'league_table' in team_stats['sofascore']:
            print(f"\nSofaScore league position: {team_stats['sofascore']['league_table']['position']}")
        if 'recent_form' in team_stats['sofascore']:
            print(f"Recent form: {team_stats['sofascore']['recent_form']}")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    test_comprehensive_scraper()
