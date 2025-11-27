import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional

# Add project root to path to import yudor_model
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))
# print(f"DEBUG: sys.path: {sys.path}")

# Import the Poisson model components
# Import the Poisson model components
try:
    from yudor_model.src.yudor_model.models import predict_match_outcome, train_poisson_model
    from yudor_model.src.yudor_model.data_loader import load_and_process_season
    from yudor_model.src.yudor_model.feature_engineering import calculate_rolling_averages, update_elo_ratings
except ImportError:
    print("⚠️  Statsmodels/Scipy not found. Using Mock Model for demonstration.")
    # Mock functions to allow flow to continue
    def predict_match_outcome(model, home, away):
        return {'home_win': 0.45, 'draw': 0.25, 'away_win': 0.30}
    def train_poisson_model(df):
        return "MOCK_MODEL"
    def load_and_process_season(season_id):
        return pd.DataFrame()
    def calculate_rolling_averages(df):
        return df
    def update_elo_ratings(df):
        return df

from scripts.Phase2.context_analyzer import ContextAnalyzer
from scripts.Phase2.context_analyzer import ContextAnalyzer

class AsianHandicapModel:
    """
    Advanced Asian Handicap Model.
    
    Combines:
    1. Poisson Distribution (Mathematical Base)
    2. Contextual Adjustments (News/Sentiment - Placeholder)
    """
    
    def __init__(self, season_id: int):
        self.season_id = season_id
        self.model = None
        self.data = None
        
    def train(self):
        """Trains the base Poisson model on the season data."""
        print(f"Loading and training model for season {self.season_id}...")
        df = load_and_process_season(self.season_id)
        if df.empty:
            print("No data found.")
            return
            
        # Feature Engineering
        df = calculate_rolling_averages(df)
        df = update_elo_ratings(df)
        df = df.dropna(subset=['home_rolling_goals_for'])
        
        self.data = df
        self.model = train_poisson_model(df)
        print("Model trained successfully.")

    def calculate_yudor_fair_odds(self, home_team: str, away_team: str, home_stats: Dict = None, away_stats: Dict = None, sentiment_score: float = 0.0, q_scores: Dict = None) -> Dict[str, float]:
        """
        Calculates Fair Odds using the specific 'Yudor Math Process'.
        Now incorporates Q-Scores and Sentiment directly into probability estimation.
        """
        # 1. Get Base Probabilities (Mock or Poisson)
        if self.model:
            probs = predict_match_outcome(self.model, home_team, away_team)
            raw_home = probs['home_win'] * 100
            raw_away = probs['away_win'] * 100
            raw_draw = probs['draw'] * 100
        else:
            # Fallback if model not trained: Use Q-Scores as base if available
            # Base assumption: Home 45%, Draw 25%, Away 30%
            raw_home = 45.0
            raw_draw = 25.0
            raw_away = 30.0
            
        # 2. Apply Q-Score Adjustments
        # Q-Score is roughly 0-100. Higher is better.
        if q_scores:
            h_q = q_scores.get("home", 50)
            a_q = q_scores.get("away", 50)
            
            # Simple heuristic: Difference in Q-Score shifts probability
            # e.g. Home Q=80, Away Q=60 -> Diff +20 -> Shift 5% to Home
            diff = h_q - a_q
            shift = diff * 0.25 # Weight factor
            
            raw_home += shift
            raw_away -= shift
            
        # 3. Apply Sentiment/Context Adjustment
        # Sentiment -1.0 to 1.0. 
        # Positive sentiment for Home -> Increase Home Prob
        if sentiment_score:
            # e.g. Score 0.5 -> Shift 2.5%
            sent_shift = sentiment_score * 5.0 
            raw_home += sent_shift
            raw_away -= sent_shift
            
        # Ensure bounds
        raw_home = max(5.0, min(90.0, raw_home))
        raw_away = max(5.0, min(90.0, raw_away))
        
        # Recalculate Draw (simplified, usually draw prob decreases as one team dominates)
        # For now, keep draw relatively stable or normalize
        
        # 4. Normalize to 100%
        total_prob = raw_home + raw_away + raw_draw
        scale = 100.0 / total_prob
        
        norm_home = raw_home * scale
        norm_away = raw_away * scale
        norm_draw = raw_draw * scale
        
        # Determine Favorite
        if norm_home > norm_away:
            favorite = "home"
            fav_prob = norm_home
        else:
            favorite = "away"
            fav_prob = norm_away
            
        # 5. Moneyline Odds
        moneyline = 100 / fav_prob if fav_prob > 0 else 999
        
        # 6. Scale by AH Line & Find Closest to 2.0
        base_line = -0.5
        lines_to_test = np.arange(-3.0, 3.25, 0.25)
        
        best_line = None
        best_odds = None
        min_diff = float('inf')
        
        all_lines = {}

        for line in lines_to_test:
            # Steps calculation (same as before)
            step_diff = (base_line - line) / 0.25 
            
            if step_diff > 0:
                odds = moneyline * (1.15 ** step_diff)
            else:
                odds = moneyline * (0.85 ** abs(step_diff))
            
            line_key = f"AH {line}" if favorite == "home" else f"AH {line} (Away)"
            all_lines[line_key] = odds
            
            diff = abs(odds - 2.0)
            if diff < min_diff:
                min_diff = diff
                best_line = line
                best_odds = odds
                
        return {
            "fair_odds": all_lines,
            "optimal_line": f"AH {best_line}" if favorite == "home" else f"AH {best_line} (Away)",
            "optimal_odds": best_odds,
            "favorite": favorite,
            "probabilities": {"home": norm_home, "draw": norm_draw, "away": norm_away}, # Standardized key
            "raw_probs": {"home": raw_home, "draw": raw_draw, "away": raw_away}
        }

    def get_value_bets(self, home_team: str, away_team: str, market_odds: Dict[str, float], context_score: float = None, true_probs: Dict = None):
        """
        Identifies value bets by comparing Model Probability vs Market Odds.
        
        Args:
            true_probs: Pre-calculated result from calculate_yudor_fair_odds.
        """
        if not self.model and not true_probs:
            return []

        # Auto-fetch context if not provided
        if context_score is None:
            analyzer = ContextAnalyzer()
            context_score = analyzer.get_context_score(home_team, away_team)
            print(f"   [Context] Auto-calculated score for {home_team} vs {away_team}: {context_score:.2f}")

        # Use Yudor Math Process
        if true_probs:
            yudor_data = true_probs
        else:
            # If we don't have pre-calculated probs, we can't easily calculate them without stats
            # So we return empty or rely on defaults (which might be inaccurate)
            print("   ⚠️ No true_probs provided to get_value_bets. Recalculating with defaults.")
            yudor_data = self.calculate_yudor_fair_odds(home_team, away_team)
            
        if not yudor_data:
            return []
            
        fair_odds_map = yudor_data["fair_odds"]
        favorite = yudor_data["favorite"]
        
        value_bets = []
        
        # Iterate through market odds and compare with our fair odds
        for market_line, market_odd in market_odds.items():
            # Market line format expected: "AH -0.5", "AH +0.25", etc.
            # We need to match this with our keys.
            # Note: Our keys are relative to the favorite. 
            # If Home is favorite, "AH -0.5" matches "AH -0.5".
            # If Away is favorite, "AH -0.5" (Home) corresponds to "AH +0.5" (Away)? 
            # This mapping is complex. For now, let's assume market odds are given for the Favorite.
            
            # Simple matching for now (assuming market odds keys match our generated keys)
            if market_line in fair_odds_map:
                fair_odd = fair_odds_map[market_line]
                
                # Apply Context Adjustment to Fair Odds?
                # User prompt didn't specify HOW context affects the math formula.
                # Let's apply it as a final discount/markup on the edge.
                
                # Calculate Edge
                # Edge = (Market Odds / Fair Odds) - 1
                # (Standard formula when both are decimal odds)
                
                edge = (market_odd / fair_odd) - 1
                
                # Context Boost: If context score supports the bet, increase edge/confidence
                # Context Score: +1 (Home), -1 (Away)
                
                is_home_bet = "Home" in market_line or (favorite == "home" and "-" in market_line)
                
                context_factor = 0
                if is_home_bet and context_score > 0:
                    context_factor = context_score * 0.05 # Up to 5% boost
                elif not is_home_bet and context_score < 0:
                    context_factor = abs(context_score) * 0.05
                
                final_edge = edge + context_factor
                
                if final_edge > 0.05: # 5% threshold
                    value_bets.append({
                        "selection": f"{home_team} {market_line}" if favorite == "home" else f"{away_team} {market_line}",
                        "fair_odds": round(fair_odd, 2),
                        "market_odds": market_odd,
                        "edge": round(final_edge * 100, 1),
                        "confidence": "High" if abs(context_score) > 0.5 else "Medium",
                        "yudor_optimal": yudor_data["optimal_line"] == market_line
                    })

        return value_bets

if __name__ == "__main__":
    # Example Usage
    # 1. Initialize with a season ID (e.g. Premier League)
    ah_model = AsianHandicapModel(season_id=12345)
    
    # 2. Train (fetches data and builds Poisson model)
    # ah_model.train()
    
    # 3. Analyze a match (Mock data for example)
    # market_odds = {"AH -0.5": 2.10, "AH 0.0": 1.55}
    # bets = ah_model.get_value_bets("Arsenal", "Chelsea", market_odds, context_score=0.2)
    # print(bets)
    print("Import AsianHandicapModel to use.")
