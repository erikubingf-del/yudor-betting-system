"""
This module contains the deterministic, code-first implementations for all Q-Score calculations.
Each function takes raw match and team data as input and returns a score.
The logic is based on the reasoning discovered in the project's consolidated data files.
"""
import pandas as pd
from typing import Dict, Any

# --- Scorer Classes ---

# --- Real Implementation of Q-Scorers ---

class Q2_OffensiveStrength:
    """Q2: Offensive Strength based on Goals/xG per game."""
    @staticmethod
    def calculate(stats: Dict[str, Any]) -> int:
        # Try FootyStats xG first
        if "footystats" in stats:
            xg = float(stats["footystats"].get("xg_for", 0) or 0)
            if xg > 2.0: return 9
            if xg > 1.7: return 8
            if xg > 1.4: return 6
            if xg > 1.1: return 4
            return 2
            
        # Fallback to API-Football Goals For
        if "api_football" in stats:
            # API structure varies, assuming we extracted 'goals_for_avg' or similar
            # For now, use a default if specific key missing
            return 5 
        return 5 # Average

class Q4_DefensiveSolidity:
    """Q4: Defensive Solidity based on Goals Against/xGA per game."""
    @staticmethod
    def calculate(stats: Dict[str, Any]) -> int:
        # Try FootyStats xGA (using xg_against)
        if "footystats" in stats:
            xga = float(stats["footystats"].get("xg_against", 0) or 0)
            if xga < 0.8: return 9
            if xga < 1.0: return 8
            if xga < 1.3: return 6
            if xga < 1.6: return 4
            return 2
        return 5

class Q6_TacticalMatchup:
    """Q6: Formation Analysis."""
    @staticmethod
    def calculate(home_fmt: str, away_fmt: str) -> Dict[str, int]:
        # Simple Rock-Paper-Scissors logic for common formations
        # 4-3-3 beats 4-4-2 (midfield control)
        # 3-5-2 beats 4-3-3 (width + overload)
        # 4-4-2 beats 3-5-2 (wing exploitation)
        
        h_score = 5
        a_score = 5
        
        if home_fmt == "4-3-3" and away_fmt == "4-4-2": h_score += 2
        elif home_fmt == "3-5-2" and away_fmt == "4-3-3": h_score += 2
        elif home_fmt == "4-4-2" and away_fmt == "3-5-2": h_score += 2
        
        if away_fmt == "4-3-3" and home_fmt == "4-4-2": a_score += 2
        elif away_fmt == "3-5-2" and home_fmt == "4-3-3": a_score += 2
        elif away_fmt == "4-4-2" and home_fmt == "3-5-2": a_score += 2
        
        return {"home": h_score, "away": a_score}

class Q9_LeaguePosition:
    """Q9: League Position / Motivation."""
    @staticmethod
    def calculate(stats: Dict[str, Any]) -> int:
        # Assuming we have 'rank' in stats
        rank = stats.get("rank", 10)
        if rank <= 4: return 9 # Title/UCL contender
        if rank >= 17: return 8 # Relegation fighter (high motivation)
        return 5 # Mid-table

class Q17_H2HDominance:
    """Q17: Head-to-Head Dominance."""
    @staticmethod
    def calculate(h2h_list: list, team_name: str) -> int:
        if not h2h_list: return 5
        
        wins = 0
        total = 0
        for m in h2h_list:
            # Check if team won
            # Check if team won
            try:
                # FotMob Structure
                if "status" in m and "scoreStr" in m["status"]:
                    score = m["status"]["scoreStr"].split(" - ")
                    h_score = int(score[0])
                    a_score = int(score[1])
                    h_name = m["home"]["name"]
                    a_name = m["away"]["name"]
                    
                    if h_name == team_name:
                        if h_score > a_score: wins += 1
                    elif a_name == team_name:
                        if a_score > h_score: wins += 1
                    total += 1
                    
                # API-Football Structure
                elif "teams" in m:
                    if m["teams"]["home"]["name"] == team_name and m["teams"]["home"]["winner"]: wins += 1
                    elif m["teams"]["away"]["name"] == team_name and m["teams"]["away"]["winner"]: wins += 1
                    total += 1
            except: pass
            
        if total == 0: return 5
        win_pct = wins / total
        
        if win_pct > 0.7: return 9
        if win_pct > 0.5: return 7
        if win_pct > 0.3: return 5
        return 3

def get_all_q_scores(match_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates Q-Scores using REAL data from the orchestrator.
    Returns a dict with breakdown AND total scores.
    """
    data = match_data.get("data", {})
    home_stats = data.get("home_stats", {})
    away_stats = data.get("away_stats", {})
    lineups = data.get("lineups", {})
    # H2H might be in lineups (FotMob) or top level
    h2h = data.get("h2h", [])
    if not h2h and "h2h" in lineups:
        h2h = lineups["h2h"]
    
    # Calculate Components
    q2_h = Q2_OffensiveStrength.calculate(home_stats)
    q2_a = Q2_OffensiveStrength.calculate(away_stats)
    
    q4_h = Q4_DefensiveSolidity.calculate(home_stats)
    q4_a = Q4_DefensiveSolidity.calculate(away_stats)
    
    # Formations
    h_fmt = lineups.get("home_formation", "0")
    a_fmt = lineups.get("away_formation", "0")
    q6 = Q6_TacticalMatchup.calculate(h_fmt, a_fmt)
    
    # H2H (Need team names)
    home_name = match_data.get("match_info", {}).get("home", "")
    away_name = match_data.get("match_info", {}).get("away", "")
    q17_h = Q17_H2HDominance.calculate(h2h, home_name)
    q17_a = Q17_H2HDominance.calculate(h2h, away_name)
    
    # Aggregate (Weighted Average)
    # Weights: Attack (1.5), Defense (1.5), H2H (1.0), Tactics (0.5)
    
    h_total = (q2_h * 1.5 + q4_h * 1.5 + q17_h * 1.0 + q6["home"] * 0.5) / 4.5
    a_total = (q2_a * 1.5 + q4_a * 1.5 + q17_a * 1.0 + q6["away"] * 0.5) / 4.5
    
    # Normalize to 0-100 scale (Score 0-10 -> 0-100)
    h_final = min(100, h_total * 10)
    a_final = min(100, a_total * 10)
    
    return {
        "home": h_final,
        "away": a_final,
        "details": {
            "Q2_Attack": {"home": q2_h, "away": q2_a},
            "Q4_Defense": {"home": q4_h, "away": q4_a},
            "Q6_Tactics": q6,
            "Q17_H2H": {"home": q17_h, "away": q17_a}
        }
    }
