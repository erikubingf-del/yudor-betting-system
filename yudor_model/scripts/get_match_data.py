
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import json

# Try to import soccerdata
try:
    import soccerdata as sd
    SOCCERDATA_AVAILABLE = True
except ImportError:
    SOCCERDATA_AVAILABLE = False

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ComprehensiveStatsScraper:
    """
    Fetch ALL available statistics from multiple sources.
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

    def __init__(self, league: str, season: str):
        if not SOCCERDATA_AVAILABLE:
            raise ImportError("soccerdata library not available")

        self.league = league
        fbref_league = self.LEAGUE_MAP.get(league, league)
        self.season = season

        try:
            self.fbref = sd.FBref(leagues=fbref_league, seasons=season)
        except Exception:
            self.fbref = None

        self.sofascore = None

        try:
            self.fotmob = sd.FotMob(leagues=fbref_league, seasons=season)
        except Exception:
            self.fotmob = None

        try:
            self.understat = sd.Understat(leagues=fbref_league, seasons=season)
        except Exception:
            self.understat = None
        
        try:
            self.clubelo = sd.ClubElo()
        except Exception:
            self.clubelo = None


    def get_all_team_stats(self, team_name: str) -> Dict:
        all_stats = {
            'fbref': {},
            'sofascore': {},
            'fotmob': {},
            'understat': {},
            'clubelo': {}
        }

        if self.fbref:
            all_stats['fbref'] = self._get_fbref_all_stats(team_name)
        if self.fotmob:
            all_stats['fotmob'] = self._get_fotmob_stats(team_name)
        if self.understat:
            all_stats['understat'] = self._get_understat_stats(team_name)
        if self.clubelo:
            all_stats['clubelo'] = self._get_clubelo_stats(team_name)

        return all_stats
    
    def _get_fbref_all_stats(self, team_name: str) -> Dict:
        fbref_stats = {}
        stat_types = ['standard', 'shooting', 'passing', 'defense', 'possession', 'misc']
        for stat_type in stat_types:
            try:
                stats = self.fbref.read_team_season_stats(stat_type=stat_type)
                team_data = stats[stats.index.get_level_values('team') == team_name]
                if not team_data.empty:
                    stat_dict = {}
                    for col in team_data.columns:
                        try:
                            value = team_data[col].values[0]
                            if pd.notna(value):
                                stat_dict[col] = float(value) if isinstance(value, (int, float)) else str(value)
                        except:
                            pass
                    fbref_stats[stat_type] = stat_dict
            except Exception:
                continue
        return fbref_stats

    def _get_fotmob_stats(self, team_name: str) -> Dict:
        fotmob_stats = {}
        try:
            table = self.fotmob.read_league_table()
            team_row = table[table.index.get_level_values('team') == team_name]
            if not team_row.empty:
                fotmob_stats['league_position'] = int(team_row['idx'].values[0])
        except Exception:
            pass
        return fotmob_stats

    def _get_understat_stats(self, team_name: str) -> Dict:
        understat_stats = {}
        try:
            match_stats = self.understat.read_team_match_stats()
            team_matches = match_stats[
                (match_stats['home_team'] == team_name) |
                (match_stats['away_team'] == team_name)
            ]
            if not team_matches.empty:
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
        except Exception:
            pass
        return understat_stats

    def _get_clubelo_stats(self, team_name: str) -> Dict:
        clubelo_stats = {}
        try:
            team_history = self.clubelo.read_team_history(team_name, max_age=90)
            if not team_history.empty:
                latest = team_history.iloc[-1]
                clubelo_stats['elo_rating'] = {'current_elo': float(latest['elo'])}
        except Exception:
            pass
        return clubelo_stats

def get_season_from_date(date_str):
    """Get season from date string like '22/11/2025' -> '2526'"""
    try:
        year = int(date_str.split('/')[-1])
        season_start = year % 100
        season_end = (season_start + 1) % 100
        return f"{season_start:02d}{season_end:02d}"
    except:
        return "2425" # default

def update_matches_data(matches_df):
    """
    Updates the matches dataframe with comprehensive stats.
    """
    if not SOCCERDATA_AVAILABLE:
        print("soccerdata not available. Skipping data fetching.")
        return matches_df

    # Group matches by league and season to initialize scraper once per group
    matches_df['season'] = matches_df['date'].apply(get_season_from_date)
    grouped = matches_df.groupby(['league', 'season'])

    all_matches = []

    for (league, season), group in grouped:
        print(f"Fetching data for {league} season {season}...")
        try:
            scraper = ComprehensiveStatsScraper(league=league, season=season)
        except Exception as e:
            print(f"Could not initialize scraper for {league} {season}: {e}")
            all_matches.append(group)
            continue
        
        for index, row in group.iterrows():
            try:
                home_stats = scraper.get_all_team_stats(row['home_team_name'])
                away_stats = scraper.get_all_team_stats(row['away_team_name'])

                # Update row with new data
                if home_stats.get('understat', {}).get('team_xg'):
                    row['home_xg'] = home_stats['understat']['team_xg'].get('xG_avg')
                if away_stats.get('understat', {}).get('team_xg'):
                    row['away_xg'] = away_stats['understat']['team_xg'].get('xG_avg')
                
                # Add more fields here as needed from other sources
                
            except Exception as e:
                print(f"Could not fetch data for match {row['match_id']}: {e}")
            
            all_matches.append(row.to_frame().T)

    if not all_matches:
        return matches_df

    # Concatenate all rows back into a single dataframe
    updated_df = pd.concat(all_matches, ignore_index=True)
    return updated_df


if __name__ == '__main__':
    matches_csv_path = 'yudor_model/data/matches.csv'
    
    try:
        df = pd.read_csv(matches_csv_path)
        
        # For demonstration, only process a subset of the data to avoid long run times
        # In a real scenario, you might process the whole file or new entries
        df_subset = df.head(5)

        updated_df = update_matches_data(df_subset)

        # In a real run, you would save the full updated dataframe
        # For this simulation, we just show the head
        print("\nUpdated DataFrame head:")
        print(updated_df.head())

        # Example of how you would save the file
        # updated_df.to_csv('yudor_model/data/matches_updated.csv', index=False)

    except FileNotFoundError:
        print(f"File not found: {matches_csv_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
