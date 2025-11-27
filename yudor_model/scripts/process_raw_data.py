
import json
import pandas as pd
import os

def create_team_id(team_name):
    """Creates a 3-letter team ID from the team name."""
    # Simple version: take the first 3 letters of the first word
    return team_name[:3].upper()

def process_raw_data(raw_data_path, output_path):
    """
    Processes the raw scraped data and transforms it into a structured CSV file.
    """
    with open(raw_data_path, 'r') as f:
        data = json.load(f)

    processed_matches = []

    for match_id, match_data in data.items():
        match_info = match_data.get('match_info', {})
        
        home_team_name = match_info.get('home')
        away_team_name = match_info.get('away')

        if not home_team_name or not away_team_name:
            continue

        processed_match = {
            'match_id': match_info.get('id'),
            'date': match_info.get('date'),
            'league': match_info.get('league'),
            'home_team_id': create_team_id(home_team_name),
            'away_team_id': create_team_id(away_team_name),
            'home_team_name': home_team_name,
            'away_team_name': away_team_name,
            'home_goals': None,
            'away_goals': None,
            'home_xg': None,
            'away_xg': None,
            'home_possession': None,
            'away_possession': None,
            'home_shots': None,
            'away_shots': None,
            'home_shots_on_target': None,
            'away_shots_on_target': None,
            'odds_home_win': None,
            'odds_draw': None,
            'odds_away_win': None,
            'odds_ah_line': None,
            'odds_ah_home': None,
            'odds_ah_away': None,
        }
        processed_matches.append(processed_match)

    df = pd.DataFrame(processed_matches)
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")

if __name__ == '__main__':
    # Using relative paths from the project root
    raw_data_path = 'data/raw_legacy/scraped_matches.json'
    output_path = 'yudor_model/data/matches.csv'
    process_raw_data(raw_data_path, output_path)
