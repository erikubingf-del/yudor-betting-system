"""
This module contains the machine learning model for calculating fair odds
from a given set of Q-Scores.
"""
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression

# Define the path where the trained model will be saved.
MODEL_PATH = "scripts/analysis_engine/fair_odds_model.joblib"

class FairOddsModel:
    def __init__(self):
        self.model = LogisticRegression()
        self.is_trained = False

    def train(self, training_data: pd.DataFrame, features: list, target: str):
        """
        Trains the logistic regression model.

        Args:
            training_data (pd.DataFrame): DataFrame containing historical match data,
                                          including Q-scores and the actual outcome.
            features (list): A list of column names to be used as features (the Q-scores).
            target (str): The name of the column representing the outcome (e.g., 'result').
        """
        print("Training the fair odds model...")
        X = training_data[features]
        y = training_data[target]

        # TODO: Add more sophisticated data preprocessing and feature engineering.
        self.model.fit(X, y)
        self.is_trained = True
        print("Model training complete.")
        self.save_model()

    def predict_probabilities(self, q_scores_df: pd.DataFrame) -> dict:
        """
        Predicts the probability of home win, draw, and away win.

        Args:
            q_scores_df (pd.DataFrame): A DataFrame with a single row containing the
                                        Q-scores for the match to be analyzed.

        Returns:
            dict: A dictionary with probabilities for 'home_win', 'draw', 'away_win'.
        """
        if not self.is_trained:
            # Return neutral placeholder odds if the model isn't trained
            return {"home_win": 0.33, "draw": 0.33, "away_win": 0.33}

        # The model will return probabilities for each class (e.g., [H, D, A])
        probabilities = self.model.predict_proba(q_scores_df)[0]

        # It's crucial to map these probabilities to the correct outcomes
        # based on the order the model learned from the target variable.
        # e.g., self.model.classes_ might be ['Away', 'Draw', 'Home']
        class_mapping = {label: prob for label, prob in zip(self.model.classes_, probabilities)}

        return {
            "home_win": class_mapping.get("Home", 0.0),
            "draw": class_mapping.get("Draw", 0.0),
            "away_win": class_mapping.get("Away", 0.0),
        }

    def save_model(self, path: str = MODEL_PATH):
        """Saves the trained model to a file."""
        print(f"Saving model to {path}...")
        joblib.dump(self.model, path)
        print("Model saved.")

    def load_model(self, path: str = MODEL_PATH):
        """Loads a trained model from a file."""
        try:
            self.model = joblib.load(path)
            self.is_trained = True
            print(f"Model loaded successfully from {path}.")
        except FileNotFoundError:
            print(f"No model file found at {path}. The model is not trained.")
            self.is_trained = False
        except Exception as e:
            print(f"An error occurred while loading the model: {e}")
            self.is_trained = False
