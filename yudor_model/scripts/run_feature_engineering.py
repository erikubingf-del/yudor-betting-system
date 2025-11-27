
import pandas as pd
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from yudor_model.feature_engineering import (
    calculate_goal_difference,
    calculate_xg_difference
)

def run_feature_engineering(input_path, output_path):
    """
    Runs the feature engineering pipeline.
    """
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"File not found: {input_path}")
        return

    # Apply feature engineering functions
    df = calculate_goal_difference(df)
    df = calculate_xg_difference(df)

    # Save the dataframe with features
    df.to_csv(output_path, index=False)
    print(f"Feature-engineered data saved to {output_path}")

if __name__ == '__main__':
    input_path = 'yudor_model/data/matches.csv'
    output_path = 'yudor_model/data/matches_with_features.csv'
    run_feature_engineering(input_path, output_path)
