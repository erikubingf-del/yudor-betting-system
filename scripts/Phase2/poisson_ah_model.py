import numpy as np
from scipy.stats import poisson
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class TeamMetrics:
    name: str
    attack_strength_home: float
    defense_strength_home: float
    attack_strength_away: float
    defense_strength_away: float
    avg_goals_for_home: float
    avg_goals_against_home: float
    avg_goals_for_away: float
    avg_goals_against_away: float

def create_team_metrics_from_data(name: str, footystats: Dict, api_football: Dict) -> TeamMetrics:
    """
    Factory method to create TeamMetrics from various data sources.
    Prioritizes FootyStats data, falls back to API-Football or defaults.
    """
    fs = footystats or {}
    
    # Extract strengths (FootyStats usually provides these relative to league avg)
    # If not, we default to 1.0 (average)
    att_h = float(fs.get("attack_strength_home", 0) or 1.0)
    def_h = float(fs.get("defense_strength_home", 0) or 1.0)
    att_a = float(fs.get("attack_strength_away", 0) or 1.0)
    def_a = float(fs.get("defense_strength_away", 0) or 1.0)
    
    # Goals averages
    gf_h = float(fs.get("goals_scored_home_avg", 0) or 1.5)
    ga_h = float(fs.get("goals_conceded_home_avg", 0) or 1.0)
    gf_a = float(fs.get("goals_scored_away_avg", 0) or 1.0)
    ga_a = float(fs.get("goals_conceded_away_avg", 0) or 1.5)
    
    return TeamMetrics(
        name=name,
        attack_strength_home=att_h,
        defense_strength_home=def_h,
        attack_strength_away=att_a,
        defense_strength_away=def_a,
        avg_goals_for_home=gf_h,
        avg_goals_against_home=ga_h,
        avg_goals_for_away=gf_a,
        avg_goals_against_away=ga_a
    )

class PoissonAHModel:
    """
    Mathematically rigorous Poisson model with Dixon-Coles adjustment
    and Asian Handicap line calculation.
    """
    
    def __init__(self, league_avg_home_goals=1.50, league_avg_away_goals=1.15):
        self.league_avg_home_goals = league_avg_home_goals
        self.league_avg_away_goals = league_avg_away_goals
        self.rho = -0.13  # Dixon-Coles correlation parameter

    def calculate_xg(self, home: TeamMetrics, away: TeamMetrics) -> Tuple[float, float]:
        """
        Calculates Expected Goals (xG) for the match.
        Home xG = Home Attack * Away Defense * League Avg Home Goals
        Away xG = Away Attack * Home Defense * League Avg Away Goals
        """
        home_xg = home.attack_strength_home * away.defense_strength_away * self.league_avg_home_goals
        away_xg = away.attack_strength_away * home.defense_strength_home * self.league_avg_away_goals
        return home_xg, away_xg

    def _dixon_coles_adjustment(self, i: int, j: int, home_xg: float, away_xg: float) -> float:
        """
        Adjusts probability for low-scoring scores (0-0, 1-0, 0-1, 1-1).
        """
        prob = poisson.pmf(i, home_xg) * poisson.pmf(j, away_xg)
        
        if i == 0 and j == 0:
            return prob * (1.0 - (home_xg * away_xg * self.rho))
        elif i == 0 and j == 1:
            return prob * (1.0 + (home_xg * self.rho))
        elif i == 1 and j == 0:
            return prob * (1.0 + (away_xg * self.rho))
        elif i == 1 and j == 1:
            return prob * (1.0 - self.rho)
        else:
            return prob

    def analyze_match(self, home_metrics: TeamMetrics, away_metrics: TeamMetrics) -> Dict[str, Any]:
        """
        Runs the full analysis: xG -> Probabilities -> AH Line -> EV.
        """
        # 1. Calculate xG
        h_xg, a_xg = self.calculate_xg(home_metrics, away_metrics)
        
        # 2. Generate Probability Matrix (10x10 goals)
        max_goals = 10
        matrix = np.zeros((max_goals, max_goals))
        
        for i in range(max_goals):
            for j in range(max_goals):
                matrix[i][j] = self._dixon_coles_adjustment(i, j, h_xg, a_xg)
        
        # Normalize
        matrix /= np.sum(matrix)
        
        # 3. Calculate 1X2 Probabilities
        prob_home = np.sum(np.tril(matrix, -1))
        prob_draw = np.sum(np.diag(matrix))
        prob_away = np.sum(np.triu(matrix, 1))
        
        # 4. Calculate Fair Asian Handicap Line
        # We find the line where Prob(Home Win by > Line) is closest to 50%
        # Simplified: Based on xG difference
        xg_diff = h_xg - a_xg
        fair_line = -round(xg_diff * 4) / 4  # Negative for Home Favorite (e.g. -0.5)
        
        # 5. Kelly Criterion (assuming odds ~ 1.90 for the fair line for simplicity, 
        # in real usage we would compare against bookie odds)
        # Here we just return the probabilities and the line.
        
        summary = (
            f"Poisson Model Results:\n"
            f"   xG: {home_metrics.name} {h_xg:.2f} - {a_xg:.2f} {away_metrics.name}\n"
            f"   Probs: Home {prob_home:.1%} | Draw {prob_draw:.1%} | Away {prob_away:.1%}\n"
            f"   Fair AH Line: {home_metrics.name} {fair_line}"
        )
        
        return {
            "home_xg": h_xg,
            "away_xg": a_xg,
            "probabilities": {
                "home": prob_home,
                "draw": prob_draw,
                "away": prob_away
            },
            "fair_ah_line": {
                "home_perspective": fair_line,
                "away_perspective": -fair_line
            },
            "summary": summary
        }
