"""
This module contains the deterministic, code-first implementations for all Q-Score calculations.
Each function takes raw match and team data as input and returns a score.
The logic is based on the reasoning discovered in the project's consolidated data files.
"""
import pandas as pd
from typing import Dict, Any

# --- Scorer Classes ---

class Q2_OffensiveStrength:
    """
    Q2: Offensive Strength based on Expected Goals (xG) per game.
    - Score: Based on xG/game. Ranges from +0 to +8.
    """
    @staticmethod
    def calculate(team_data: Dict[str, Any]) -> int:
        xg_per_game = team_data.get("xg_per_game")
        if xg_per_game is None:
            return 2 # Default value if no data

        if xg_per_game >= 2.0:
            return 8
        if xg_per_game >= 1.8:
            return 7
        if xg_per_game >= 1.5:
            return 5
        if xg_per_game >= 1.3:
            return 3
        return 2

class Q4_DefensiveSolidity:
    """
    Q4: Defensive Solidity based on Expected Goals Against (xGA) per game.
    - Score: Based on xGA/game (lower is better). Ranges from +0 to +8.
    """
    @staticmethod
    def calculate(team_data: Dict[str, Any]) -> int:
        xga_per_game = team_data.get("xga_per_game")
        if xga_per_game is None:
            return 1 # Default value

        if xga_per_game <= 0.8:
            return 8
        if xga_per_game <= 1.0:
            return 5
        if xga_per_game <= 1.3:
            return 3
        if xga_per_game <= 1.6:
            return 1
        return 0

class Q17_H2HDominance:
    """
    Q17: Head-to-Head Dominance.
    - Score: Based on win percentage and recent H2H record.
    """
    @staticmethod
    def calculate(h2h_data: Dict[str, Any], team_name: str, opponent_name: str) -> int:
        if not h2h_data or h2h_data.get('matches') is None:
            return 0 # Default

        wins = 0
        total_games = 0
        for match in h2h_data['matches']:
            if match['home_team'] == team_name and match['winner'] == 'home':
                wins += 1
            if match['away_team'] == team_name and match['winner'] == 'away':
                wins += 1
            total_games +=1
        
        if total_games == 0:
            return 0

        win_pct = (wins / total_games) * 100
        
        if win_pct >= 75:
            return 10
        if win_pct >= 60:
            return 7
        if win_pct >= 50:
            return 5
        return 0


# --- Main Calculation Function ---

def get_all_q_scores(match_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Main function to calculate all Q-scores for a given match.
    This orchestrates calls to all individual q_score calculators.
    """
    home_team_name = match_data.get("match_info", {}).get("home")
    away_team_name = match_data.get("match_info", {}).get("away")

    # In a real scenario, this data would be populated from your scrapers
    # For now, we'll use the structure from the JSON file
    home_team_q_data = {
        "xg_per_game": 1.50,
        "xga_per_game": 1.60
    }
    away_team_q_data = {
        "xg_per_game": 1.23,
        "xga_per_game": 1.41
    }
    h2h_q_data = {
        "matches": [
            {'home_team': 'Manchester United', 'away_team': 'Everton', 'winner': 'home'},
            {'home_team': 'Manchester United', 'away_team': 'Everton', 'winner': 'home'},
            {'home_team': 'Manchester United', 'away_team': 'Everton', 'winner': 'home'},
            {'home_team': 'Manchester United', 'away_team': 'Everton', 'winner': 'home'},
            {'home_team': 'Manchester United', 'away_team': 'Everton', 'winner': 'draw'},
            {'home_team': 'Everton', 'away_team': 'Manchester United', 'winner': 'away'},
            {'home_team': 'Everton', 'away_team': 'Manchester United', 'winner': 'away'},
            {'home_team': 'Everton', 'away_team': 'Manchester United', 'winner': 'away'},
            {'home_team': 'Everton', 'away_team': 'Manchester United', 'winner': 'draw'},
            {'home_team': 'Everton', 'away_team': 'Manchester United', 'winner': 'home'},
        ]
    }


    q_scores = {
        "Q1_Home": 0, # Placeholder, needs player value data
        "Q1_Away": 0, # Placeholder
        "Q2_Home": Q2_OffensiveStrength.calculate(home_team_q_data),
        "Q2_Away": Q2_OffensiveStrength.calculate(away_team_q_data),
        "Q3_Home": 1, # Placeholder, needs bench data
        "Q3_Away": 1, # Placeholder
        "Q4_Home": Q4_DefensiveSolidity.calculate(home_team_q_data),
        "Q4_Away": Q4_DefensiveSolidity.calculate(away_team_q_data),
        "Q5_Home": 2, # Placeholder, needs manager data
        "Q5_Away": 2, # Placeholder
        "Q6_Home": 0, # Placeholder, needs formation data
        "Q6_Away": 0, # Placeholder
        "Q7_Home": 2, # Placeholder, needs pressing data
        "Q7_Away": 2, # Placeholder
        "Q8_Home": 2, # Placeholder, needs set-piece data
        "Q8_Away": 2, # Placeholder
        "Q9_Home": 0, # Placeholder, needs league position data
        "Q9_Away": 0, # Placeholder
        "Q10_Home": 0, # Placeholder, needs derby context
        "Q10_Away": 0, # Placeholder
        "Q11_Home": 0, # Placeholder, needs recent form data
        "Q11_Away": 0, # Placeholder
        "Q12_Home": 0, # Placeholder, needs opponent quality data
        "Q12_Away": 0, # Placeholder
        "Q13_Home": 1, # Placeholder, needs xG vs Goals data
        "Q13_Away": 1, # Placeholder
        "Q14_Home": 0, # Placeholder, needs SofaScore ratings
        "Q14_Away": 0, # Placeholder
        "Q15_Home": 0, # Placeholder, needs injury data
        "Q15_Away": 0, # Placeholder
        "Q16_Home": 0, # Placeholder, needs defensive injury cluster data
        "Q16_Away": 0, # Placeholder
        "Q17_Home": Q17_H2HDominance.calculate(h2h_q_data, home_team_name, away_team_name),
        "Q17_Away": Q17_H2HDominance.calculate(h2h_q_data, away_team_name, home_team_name),
        "Q18_Home": 5, # Placeholder, needs H2H at venue
        "Q18_Away": 0, # Placeholder
        "Q19_Home": 0, # Placeholder, needs H2H veto logic
        "Q19_Away": 0, # Placeholder
    }
    return q_scores
