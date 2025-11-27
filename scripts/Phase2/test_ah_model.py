import sys
import os
from pathlib import Path
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Mock statsmodels to avoid dependency error during testing
import sys
from unittest.mock import MagicMock
sys.modules["statsmodels"] = MagicMock()
sys.modules["statsmodels.api"] = MagicMock()
sys.modules["statsmodels.formula.api"] = MagicMock()
sys.modules["scipy"] = MagicMock()
sys.modules["scipy.stats"] = MagicMock()

from scripts.Phase2.ah_value_finder import AsianHandicapModel

def test_ah_model():
    print("--- Testing Phase 2 AH Model ---")
    
    # 1. Initialize
    # Use a dummy season ID. The data loader will fail to fetch real data, 
    # so we need to mock the data loading part or handle the empty case.
    model = AsianHandicapModel(season_id=99999)
    
    # Mock the internal model for testing purposes
    # We can't easily mock the full training without real data, 
    # so we'll manually inject a mock Poisson model if possible, 
    # OR we just test the logic that doesn't require a trained model (if any).
    # Actually, get_value_bets returns empty if model is not trained.
    
    # Let's mock the training data and train it
    print("Mocking training data...")
    mock_data = pd.DataFrame({
        "date": pd.date_range(start="2024-01-01", periods=10),
        "home_team_name": ["Team A"] * 10,
        "away_team_name": ["Team B"] * 10,
        "home_goals": [2, 1, 3, 2, 1, 0, 2, 1, 3, 2],
        "away_goals": [1, 1, 0, 1, 2, 1, 0, 1, 0, 1],
        "home_xg": [1.5] * 10,
        "away_xg": [1.0] * 10,
        "home_goal_diff": [1] * 10,
        "away_goal_diff": [-1] * 10,
        "home_xg_diff": [0.5] * 10,
        "away_xg_diff": [-0.5] * 10
    })
    
    # We need to monkeypatch load_and_process_season in the ah_value_finder module
    import scripts.Phase2.ah_value_finder as ah_module
    ah_module.load_and_process_season = lambda x: mock_data
    
    # Now train
    model.train()
    
    if not model.model:
        print("FAILED: Model did not train.")
        return

    # 2. Test Prediction & Value Finding
    print("Testing Value Finder...")
    
    # Mock the model prediction to match the User's Betis Example
    # Raw: Casa 50%, Vis 17%, Empate 25% (Total 92%)
    # Normalized: Casa 54%, Vis 21%, Empate 25%
    # Moneyline: 100/54 = 1.85
    # AH -0.5: 1.85
    # AH -0.75: 1.85 * 1.15 = 2.1275 (~2.13)
    
    # We need to mock predict_match_outcome to return these raw probs
    # 50% = 0.50, 17% = 0.17, 25% = 0.25
    
    import scripts.Phase2.ah_value_finder as ah_module
    ah_module.predict_match_outcome = lambda model, h, a: {"home_win": 0.50, "away_win": 0.17, "draw": 0.25}
    
    # Calculate Yudor Odds
    yudor_data = model.calculate_yudor_fair_odds("Betis", "Opponent")
    
    print("\n--- Yudor Math Verification (Betis Example) ---")
    print(f"Raw Probs: {yudor_data['raw_probs']}")
    print(f"Adjusted Probs: {yudor_data['adjusted_probs']}")
    print(f"Favorite: {yudor_data['favorite']}")
    
    print("\nCalculated Odds:")
    for line in ["AH -0.5", "AH -0.75", "AH -0.25"]:
        if line in yudor_data['fair_odds']:
            print(f"{line}: {yudor_data['fair_odds'][line]:.4f}")
            
    print(f"\nOptimal Line (Closest to 2.0): {yudor_data['optimal_line']}")
    print(f"Optimal Odds: {yudor_data['optimal_odds']:.4f}")
    
    # Verify against expected values
    expected_minus_075 = 2.1275
    calc_minus_075 = yudor_data['fair_odds'].get("AH -0.75", 0)
    
    if abs(calc_minus_075 - expected_minus_075) < 0.01:
        print("✅ SUCCESS: Calculation matches Betis example!")
    else:
        print(f"❌ FAILURE: Expected {expected_minus_075}, got {calc_minus_075}")

    return

if __name__ == "__main__":
    test_ah_model()
