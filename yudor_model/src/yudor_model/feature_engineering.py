
import pandas as pd

def calculate_goal_difference(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the goal difference for each match.
    """
    df['home_goal_diff'] = df['home_goals'] - df['away_goals']
    df['away_goal_diff'] = df['away_goals'] - df['home_goals']
    return df

def calculate_xg_difference(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the expected goal difference for each match.
    """
    df['home_xg_diff'] = df['home_xg'] - df['away_xg']
    df['away_xg_diff'] = df['away_xg'] - df['home_xg']
    return df

def calculate_rolling_averages(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """
    Calculates rolling averages for key stats (goals, xG) for each team.
    Assumes df is sorted by date.
    """
    # Create a copy to avoid SettingWithCopy warnings
    df = df.copy()
    
    # Ensure date column is datetime
    if 'date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
        
    df = df.sort_values('date')

    # We need to calculate rolling stats for each team independently
    # This requires reshaping the data to a "team-match" level
    
    # 1. Create a long-form dataframe where each row is a team-match
    home_df = df[['date', 'home_team_name', 'home_goals', 'home_xg', 'home_goal_diff', 'home_xg_diff']].rename(
        columns={'home_team_name': 'team', 'home_goals': 'goals_for', 'home_xg': 'xg_for', 
                 'home_goal_diff': 'goal_diff', 'home_xg_diff': 'xg_diff'}
    )
    home_df['is_home'] = 1
    # For home team, goals against is away goals (which we need to grab from original df if not in subset)
    # Let's grab away_goals too
    home_df['goals_against'] = df['away_goals']
    home_df['xg_against'] = df['away_xg']

    away_df = df[['date', 'away_team_name', 'away_goals', 'away_xg', 'away_goal_diff', 'away_xg_diff']].rename(
        columns={'away_team_name': 'team', 'away_goals': 'goals_for', 'away_xg': 'xg_for',
                 'away_goal_diff': 'goal_diff', 'away_xg_diff': 'xg_diff'}
    )
    away_df['is_home'] = 0
    away_df['goals_against'] = df['home_goals']
    away_df['xg_against'] = df['home_xg']
    
    # Invert diffs for away team (since they were calculated as home - away)
    away_df['goal_diff'] = -away_df['goal_diff']
    away_df['xg_diff'] = -away_df['xg_diff']

    team_stats = pd.concat([home_df, away_df]).sort_values(['team', 'date'])

    # 2. Calculate rolling averages per team
    cols_to_roll = ['goals_for', 'goals_against', 'xg_for', 'xg_against', 'goal_diff', 'xg_diff']
    
    for col in cols_to_roll:
        # shift(1) ensures we only use PAST data for the current match prediction
        team_stats[f'rolling_{col}'] = team_stats.groupby('team')[col].transform(
            lambda x: x.shift(1).rolling(window=window, min_periods=1).mean()
        )

    # 3. Merge back to the original match dataframe
    # We need to merge twice: once for home team stats, once for away team stats
    
    # Prepare home stats to merge
    home_stats_to_merge = team_stats[team_stats['is_home'] == 1][['date', 'team'] + [f'rolling_{c}' for c in cols_to_roll]]
    home_stats_to_merge = home_stats_to_merge.rename(columns={
        'team': 'home_team_name',
        **{f'rolling_{c}': f'home_rolling_{c}' for c in cols_to_roll}
    })
    
    # Prepare away stats to merge
    away_stats_to_merge = team_stats[team_stats['is_home'] == 0][['date', 'team'] + [f'rolling_{c}' for c in cols_to_roll]]
    away_stats_to_merge = away_stats_to_merge.rename(columns={
        'team': 'away_team_name',
        **{f'rolling_{c}': f'away_rolling_{c}' for c in cols_to_roll}
    })

    # Merge
    df = pd.merge(df, home_stats_to_merge, on=['date', 'home_team_name'], how='left')
    df = pd.merge(df, away_stats_to_merge, on=['date', 'away_team_name'], how='left')

    return df

def update_elo_ratings(df: pd.DataFrame, k_factor: int = 20, initial_rating: int = 1500) -> pd.DataFrame:
    """
    Calculates and updates Elo ratings for teams based on match results.
    Adds 'home_elo' and 'away_elo' (ratings BEFORE the match) to the dataframe.
    """
    df = df.copy()
    
    if 'date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
        
    df = df.sort_values('date')
    
    ratings = {} # Dictionary to store current ratings for each team

    def get_rating(team):
        return ratings.get(team, initial_rating)

    def expected_score(rating_a, rating_b):
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    home_elos = []
    away_elos = []

    for index, row in df.iterrows():
        home_team = row['home_team_name']
        away_team = row['away_team_name']
        
        home_rating = get_rating(home_team)
        away_rating = get_rating(away_team)
        
        # Store ratings *before* the match update
        home_elos.append(home_rating)
        away_elos.append(away_rating)
        
        # Calculate actual score (1 for win, 0.5 for draw, 0 for loss)
        if row['home_goals'] > row['away_goals']:
            home_actual = 1
            away_actual = 0
        elif row['home_goals'] == row['away_goals']:
            home_actual = 0.5
            away_actual = 0.5
        else:
            home_actual = 0
            away_actual = 1
            
        # Calculate expected score
        home_expected = expected_score(home_rating, away_rating)
        away_expected = expected_score(away_rating, home_rating)
        
        # Update ratings
        new_home_rating = home_rating + k_factor * (home_actual - home_expected)
        new_away_rating = away_rating + k_factor * (away_actual - away_expected)
        
        ratings[home_team] = new_home_rating
        ratings[away_team] = new_away_rating

    df['home_elo'] = home_elos
    df['away_elo'] = away_elos
    
    return df
