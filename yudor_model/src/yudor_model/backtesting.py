import pandas as pd
import numpy as np
from .data_loader import load_and_process_season
from .feature_engineering import calculate_rolling_averages, update_elo_ratings
from .models import train_poisson_model, predict_match_outcome

def run_backtest(season_id: int, train_ratio: float = 0.7):
    """
    Runs a backtest for a specific season.
    
    1. Loads data.
    2. Applies feature engineering (rolling averages, Elo).
    3. Splits into train/test based on date.
    4. Trains model on training set.
    5. Evaluates on test set.
    """
    print(f"--- Starting Backtest for Season {season_id} ---")
    
    # 1. Load Data
    df = load_and_process_season(season_id)
    if df.empty:
        print("No data found.")
        return

    print(f"Loaded {len(df)} matches.")

    # 2. Feature Engineering
    print("Applying feature engineering...")
    df = calculate_rolling_averages(df)
    df = update_elo_ratings(df)
    
    # Drop initial rows with NaNs from rolling averages
    df = df.dropna(subset=['home_rolling_goals_for', 'away_rolling_goals_for'])
    print(f"Data after cleaning: {len(df)} matches.")

    # 3. Split Train/Test
    # We split by time, not random shuffle, to avoid lookahead bias
    split_idx = int(len(df) * train_ratio)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    print(f"Training set: {len(train_df)} matches")
    print(f"Test set: {len(test_df)} matches")

    # 4. Train Model
    print("Training Poisson model...")
    model = train_poisson_model(train_df)
    
    if model is None:
        print("Model training failed.")
        return

    # 5. Evaluate
    print("Evaluating on test set...")
    correct_predictions = 0
    total_predictions = 0
    
    results = []

    for idx, row in test_df.iterrows():
        home_team = row['home_team_name']
        away_team = row['away_team_name']
        
        # Predict
        probs = predict_match_outcome(model, home_team, away_team)
        
        # Determine predicted outcome (highest probability)
        if probs['home_win'] > probs['draw'] and probs['home_win'] > probs['away_win']:
            pred = "HOME_WIN"
        elif probs['away_win'] > probs['home_win'] and probs['away_win'] > probs['draw']:
            pred = "AWAY_WIN"
        else:
            pred = "DRAW"
            
        # Determine actual outcome
        if row['home_goals'] > row['away_goals']:
            actual = "HOME_WIN"
        elif row['home_goals'] < row['away_goals']:
            actual = "AWAY_WIN"
        else:
            actual = "DRAW"
            
        if pred == actual:
            correct_predictions += 1
            
        total_predictions += 1
        
        results.append({
            "date": row['date'],
            "home": home_team,
            "away": away_team,
            "actual": actual,
            "predicted": pred,
            "prob_home": probs['home_win'],
            "prob_draw": probs['draw'],
            "prob_away": probs['away_win']
        })

    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
    print(f"--- Backtest Complete ---")
    print(f"Accuracy: {accuracy:.2%}")
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    # Example: Premier League 2023/2024 (ID might need adjustment)
    # run_backtest(12345) 
    print("Import run_backtest to use.")
