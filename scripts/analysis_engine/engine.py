"""
Main entry point for the Deterministic Analysis Engine.
"""
import pandas as pd
from . import q_scorers
from .odds_model import FairOddsModel

class DeterministicEngine:
    def __init__(self):
        """
        Initializes the engine, loading the ML model.
        """
        self.odds_model = FairOddsModel()
        self.odds_model.load_model() # Attempt to load a pre-trained model

    def analyze_match(self, match_data: dict) -> dict:
        """
        Runs the full deterministic analysis for a single match.

        Args:
            match_data (dict): A dictionary containing all the raw data for the match,
                               including stats, H2H, news, etc.

        Returns:
            dict: A dictionary containing the full analysis, including Q-scores
                  and the calculated fair odds.
        """
        print("Running analysis with the Deterministic Engine...")

        # 1. Calculate Q-Scores
        # The `get_all_q_scores` function will orchestrate calls to individual scorers.
        # This is a simplified call; the actual implementation will need to
        # pass the correct data slices to the scorer function.
        q_scores = q_scorers.get_all_q_scores(match_data)
        print(f"Calculated Q-Scores: {q_scores}")

        # 2. Predict Fair Odds
        # The ML model expects the Q-scores in a specific DataFrame format.
        # The order of columns here is critical and must match the training phase.
        q_scores_df = pd.DataFrame([q_scores])

        # Ensure all expected feature columns are present, even if not calculated yet
        # This should be defined in a config file in a real scenario
        expected_features = [f"Q{i}" for i in range(1, 20)] # Example
        for feature in q_scores_df.columns: # Use actual columns from the dataframe
            if feature not in expected_features:
                # Add a placeholder for any missing columns if necessary
                # For now, we assume get_all_q_scores returns all required features
                pass

        probabilities = self.odds_model.predict_probabilities(q_scores_df)
        print(f"Predicted Probabilities: {probabilities}")

        # 3. Format and return the complete analysis
        analysis_output = {
            "engine_version": "deterministic_v1.0",
            "q_scores": q_scores,
            "yudor_fair_odds": {
                "home_win_prob": probabilities["home_win"],
                "draw_prob": probabilities["draw"],
                "away_win_prob": probabilities["away_win"],
                "home_odds": 1 / probabilities["home_win"] if probabilities["home_win"] > 0 else None,
                "draw_odds": 1 / probabilities["draw"] if probabilities["draw"] > 0 else None,
                "away_odds": 1 / probabilities["away_win"] if probabilities["away_win"] > 0 else None,
            },
            "raw_data_summary": {
                # Include a summary of the input data for traceability
                "home_team": match_data.get('home_team_name'),
                "away_team": match_data.get('away_team_name'),
            }
        }

        return analysis_output
