
import pandas as pd
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from yudor_model.models import train_poisson_model, predict_match_outcome

def run_model_training(input_path):
    """
    Trains the Poisson model and runs a sample prediction.
    """
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"File not found: {input_path}")
        return

    # Train the model
    poisson_model = train_poisson_model(df)
    
    if poisson_model:
        print("\nModel training complete.")
        
        # Run a sample prediction
        home_team = 'Valencia'
        away_team = 'Levante'
        
        print(f"\nPredicting match: {home_team} vs {away_team}")
        
        prediction = predict_match_outcome(poisson_model, home_team, away_team)
        
        if prediction:
            print("\nPrediction Results:")
            print(f"  Home win probability: {prediction['home_win']:.2%}")
            print(f"  Draw probability: {prediction['draw']:.2%}")
            print(f"  Away win probability: {prediction['away_win']:.2%}")
            print(f"  Predicted score: {prediction['predicted_home_goals']:.2f} - {prediction['predicted_away_goals']:.2f}")

if __name__ == '__main__':
    input_path = 'yudor_model/data/matches_with_features.csv'
    run_model_training(input_path)
