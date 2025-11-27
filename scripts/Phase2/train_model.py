"""
This script trains the FairOddsModel using the historical dataset.

It loads the data from 'data/training_dataset.csv', selects the features and target,
and then trains and saves the machine learning model.
"""
import pandas as pd
from analysis_engine.odds_model import FairOddsModel
import os

# Define the path to the dataset
DATASET_PATH = "data/training_dataset.csv"

def train_model():
    """
    Main function to load data and train the model.
    """
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset not found at '{DATASET_PATH}'.")
        print("Please run 'scripts/build_training_dataset.py' first.")
        return

    print(f"Loading dataset from {DATASET_PATH}...")
    df = pd.read_csv(DATASET_PATH)

    # --- Feature Selection ---
    # We will use all the Q-score columns as our features.
    feature_columns = [col for col in df.columns if col.startswith('Q')]
    
    # --- Target Variable ---
    target_column = "outcome"

    # Drop rows where the outcome or features are missing
    df.dropna(subset=feature_columns + [target_column], inplace=True)

    if df.empty:
        print("Error: No valid data available for training after cleaning.")
        return
        
    print(f"Training model with {len(df)} records and {len(feature_columns)} features.")

    # Instantiate the model
    model = FairOddsModel()

    # Train the model
    model.train(
        training_data=df,
        features=feature_columns,
        target=target_column
    )

    print("\nModel training process complete.")
    print(f"The trained model has been saved to: {model.MODEL_PATH}")

if __name__ == "__main__":
    train_model()
