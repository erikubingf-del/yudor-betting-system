import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from yudor_model.feature_engineering import calculate_rolling_averages, update_elo_ratings
from yudor_model.models import train_poisson_model, predict_match_outcome

def test_pipeline():
    print("Creating mock data...")
    # Create mock data
    dates = pd.date_range(start="2024-01-01", periods=20)
    data = []
    teams = ["Team A", "Team B", "Team C", "Team D"]
    
    for date in dates:
        home = np.random.choice(teams)
        away = np.random.choice([t for t in teams if t != home])
        
        data.append({
            "date": date,
            "home_team_name": home,
            "away_team_name": away,
            "home_goals": np.random.poisson(1.5),
            "away_goals": np.random.poisson(1.2),
            "home_xg": 1.5,
            "away_xg": 1.2,
            "home_goal_diff": 0, # Placeholder
            "away_goal_diff": 0, # Placeholder
            "home_xg_diff": 0,
            "away_xg_diff": 0
        })
        
    df = pd.DataFrame(data)
    
    print("Testing Feature Engineering...")
    df = calculate_rolling_averages(df, window=3)
    df = update_elo_ratings(df)
    
    # Check if columns were added
    expected_cols = ['home_rolling_goals_for', 'home_elo', 'away_elo']
    for col in expected_cols:
        if col not in df.columns:
            print(f"FAILED: Column {col} missing.")
            return

    print("Testing Model Training...")
    # Drop NaNs
    df_clean = df.dropna(subset=['home_rolling_goals_for'])
    model = train_poisson_model(df_clean)
    
    if model is None:
        print("FAILED: Model training returned None.")
        return
        
    print("Testing Prediction...")
    probs = predict_match_outcome(model, "Team A", "Team B")
    print(f"Prediction: {probs}")
    
    if probs['home_win'] + probs['draw'] + probs['away_win'] < 0.99:
         print("FAILED: Probabilities do not sum to ~1.")
         return

    print("SUCCESS: Pipeline test passed.")

if __name__ == "__main__":
    test_pipeline()
