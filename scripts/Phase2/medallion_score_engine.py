import logging
from typing import Dict, Any, List

class MedallionScoreEngine:
    """
    Implements the 7-Category Medallion Scoring Methodology.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _get_stat(self, stats: Dict, key: str, default=0):
        return float(stats.get("footystats", {}).get(key, 0) or 0)

    def calculate_technique(self, team_stats: Dict, opp_stats: Dict) -> Dict[str, Any]:
        """
        Technique (Strength): 0-25%
        Based on PPG and League Rank comparison.
        """
        ppg = self._get_stat(team_stats, "points_per_game", 1.0)
        opp_ppg = self._get_stat(opp_stats, "points_per_game", 1.0)
        
        diff = ppg - opp_ppg
        
        if diff >= 0.8: return {"score": 22, "grade": "A", "reason": "Superior Quality (PPG Diff > 0.8)"}
        if diff >= 0.4: return {"score": 12, "grade": "B", "reason": "Strong Favorite (PPG Diff > 0.4)"}
        if diff >= 0.1: return {"score": 5, "grade": "C", "reason": "Slight Edge"}
        return {"score": 0, "grade": "D", "reason": "Equal or Inferior"}

    def calculate_must_win(self, team_stats: Dict) -> Dict[str, Any]:
        """
        Must Win (Motivation): 0-17%
        Based on Table Position.
        """
        rank = int(team_stats.get("footystats", {}).get("league_position", 10) or 10)
        
        if rank <= 4: return {"score": 15, "grade": "A", "reason": "Title/UCL Contender"}
        if rank >= 17: return {"score": 17, "grade": "A", "reason": "Relegation Fight"}
        if 5 <= rank <= 7: return {"score": 8, "grade": "B", "reason": "European Spot Chase"}
        return {"score": 2, "grade": "C", "reason": "Mid-table"}

    def calculate_absences_from_list(self, injuries: List, key_players: List, team_name: str) -> Dict[str, Any]:
        """
        Calculates Absences score based on injury list and key players.
        """
        score = 0
        missing_key_players = []
        missing_regular_players = []
        
        # Normalize key player names for matching
        key_names = [p["name"].lower() for p in key_players]
        key_lastnames = [p["lastname"].lower() for p in key_players]
        
        for inj in injuries:
            p_name = inj.get("player", {}).get("name", "").lower()
            reason = inj.get("player", {}).get("reason", "").lower()
            
            # Skip if "Questionable" or "Doubtful" (maybe apply half penalty? For now skip to be safe)
            if "questionable" in reason or "doubt" in reason:
                continue
                
            # Check if Key Player
            is_key = False
            for kn in key_names:
                if kn in p_name or p_name in kn:
                    is_key = True
                    break
            if not is_key:
                for kln in key_lastnames:
                    if kln in p_name or p_name in kln:
                        is_key = True
                        break
            
            if is_key:
                score -= 15
                missing_key_players.append(p_name)
            else:
                score -= 5
                missing_regular_players.append(p_name)
                
        # Cap at -50
        if score < -50: score = -50
        
        grade = "A"
        if score <= -30: grade = "D"
        elif score <= -15: grade = "C"
        elif score < 0: grade = "B"
        
        reason_str = "Full Strength"
        if missing_key_players:
            reason_str = f"Missing Key: {', '.join(missing_key_players)}"
        elif missing_regular_players:
            reason_str = f"Missing: {len(missing_regular_players)} players"
            
        return {"score": score, "grade": grade, "reason": reason_str}

    def calculate_home_advantage(self, team_stats: Dict, is_home: bool) -> Dict[str, Any]:
        """
        Home Advantage: -25% to 10%
        """
        if not is_home:
            # Playing Away
            # Grade E: -1% to -25%
            # If weak away team, penalty is higher
            ppg_away = self._get_stat(team_stats, "points_per_game_away", 1.0)
            if ppg_away < 0.8: return {"score": -15, "grade": "E", "reason": "Weak Away Form"}
            return {"score": -5, "grade": "E", "reason": "Playing Away"}
            
        # Playing Home
        ppg_home = self._get_stat(team_stats, "points_per_game_home", 1.5)
        if ppg_home >= 2.0: return {"score": 10, "grade": "A", "reason": "Fortress (PPG > 2.0)"}
        if ppg_home >= 1.5: return {"score": 6, "grade": "B", "reason": "Solid Home Advantage"}
        if ppg_home >= 1.2: return {"score": 3, "grade": "C", "reason": "Average Home Support"}
        return {"score": 0, "grade": "D", "reason": "No Home Advantage"}

    def calculate_tactics(self, team_fmt: str, opp_fmt: str) -> Dict[str, Any]:
        """
        Tactics: 0-25%
        """
        # Rock-Paper-Scissors Logic
        score = 10 # Default Grade B
        grade = "B"
        reason = "Neutral Matchup"
        
        if team_fmt == "4-3-3" and opp_fmt == "4-4-2": 
            score = 20; grade = "A"; reason = "Tactical Advantage (Midfield Control)"
        elif team_fmt == "3-5-2" and opp_fmt == "4-3-3":
            score = 20; grade = "A"; reason = "Tactical Advantage (Width Overload)"
        elif team_fmt == "4-4-2" and opp_fmt == "3-5-2":
            score = 20; grade = "A"; reason = "Tactical Advantage (Wing Exploitation)"
            
        # Disadvantage
        if opp_fmt == "4-3-3" and team_fmt == "4-4-2":
            score = 0; grade = "D"; reason = "Tactical Disadvantage"
            
        return {"score": score, "grade": grade, "reason": reason}

    def calculate_form(self, form_list: List) -> Dict[str, Any]:
        """
        Form: 0-8%
        """
        # form_list e.g. ["W", "D", "L", "W", "W"]
        points = 0
        for res in form_list:
            if res == "W": points += 3
            elif res == "D": points += 1
            
        if points >= 13: return {"score": 8, "grade": "A", "reason": "Excellent Form"}
        if points >= 10: return {"score": 6, "grade": "B", "reason": "Good Form"}
        if points >= 7: return {"score": 3, "grade": "C", "reason": "Average Form"}
        return {"score": 0, "grade": "D", "reason": "Poor Form"}

    def calculate_performance(self, team_stats: Dict) -> Dict[str, Any]:
        """
        Performance: 0-15%
        Based on xG vs Goals (Underlying Performance).
        """
        xg = self._get_stat(team_stats, "xg_for", 1.0)
        goals = self._get_stat(team_stats, "goals_for", 1.0)
        
        # If xG > Goals, they are underperforming (unlucky) -> Good underlying performance?
        # Or if xG is high in general?
        # Usually "Performance" means "Are they playing well?". High xG means yes.
        
        if xg >= 1.8: return {"score": 15, "grade": "A", "reason": "Dominant (xG > 1.8)"}
        if xg >= 1.4: return {"score": 10, "grade": "B", "reason": "Good Creation (xG > 1.4)"}
        if xg >= 1.0: return {"score": 5, "grade": "C", "reason": "Average"}
        return {"score": 0, "grade": "D", "reason": "Poor Creation"}

    def analyze_match(self, home_stats, away_stats, match_context, home_injuries, away_injuries, home_formation, away_formation, home_form, away_form, home_key_players=[], away_key_players=[]):
        """
        Wrapper to match the Orchestrator's call signature.
        """
        h_tech = self.calculate_technique(home_stats, away_stats)
        h_must = self.calculate_must_win(home_stats) # Should use match_context for cup/league logic
        h_abs = self.calculate_absences_from_list(home_injuries, home_key_players, "Home")
        h_adv = self.calculate_home_advantage(home_stats, True)
        h_tact = self.calculate_tactics(home_formation, away_formation)
        h_form_score = self.calculate_form(home_form or [])
        h_perf = self.calculate_performance(home_stats)
        
        h_total = (h_tech["score"] + h_must["score"] + h_abs["score"] + 
                   h_adv["score"] + h_tact["score"] + h_form_score["score"] + h_perf["score"])

        a_tech = self.calculate_technique(away_stats, home_stats)
        a_must = self.calculate_must_win(away_stats)
        a_abs = self.calculate_absences_from_list(away_injuries, away_key_players, "Away")
        a_adv = self.calculate_home_advantage(away_stats, False)
        a_tact = self.calculate_tactics(away_formation, home_formation)
        a_form_score = self.calculate_form(away_form or [])
        a_perf = self.calculate_performance(away_stats)
        
        a_total = (a_tech["score"] + a_must["score"] + a_abs["score"] + 
                   a_adv["score"] + a_tact["score"] + a_form_score["score"] + a_perf["score"])
                   
        # Determine Recommended AH Line based on Score Difference
        score_diff = h_total - a_total
        rec_line = 0.0
        if score_diff > 25: rec_line = -0.75
        elif score_diff > 15: rec_line = -0.5
        elif score_diff > 5: rec_line = -0.25
        elif score_diff < -25: rec_line = 0.75
        elif score_diff < -15: rec_line = 0.5
        elif score_diff < -5: rec_line = 0.25
        
        summary = (
            f"Medallion Score Results:\n"
            f"   Home Score: {h_total}% (Tech:{h_tech['score']} Must:{h_must['score']} Abs:{h_abs['score']} Adv:{h_adv['score']} Tact:{h_tact['score']} Form:{h_form_score['score']} Perf:{h_perf['score']})\n"
            f"   Away Score: {a_total}% (Tech:{a_tech['score']} Must:{a_must['score']} Abs:{a_abs['score']} Adv:{a_adv['score']} Tact:{a_tact['score']} Form:{a_form_score['score']} Perf:{a_perf['score']})\n"
            f"   Recommended Line: {rec_line}"
        )

        return {
            "home_score": h_total,
            "away_score": a_total,
            "details": {
                "home": {"technique": h_tech, "must_win": h_must, "absences": h_abs, "home_adv": h_adv, "tactics": h_tact, "form": h_form_score, "perf": h_perf},
                "away": {"technique": a_tech, "must_win": a_must, "absences": a_abs, "home_adv": a_adv, "tactics": a_tact, "form": a_form_score, "perf": a_perf}
            },
            "ah_line": {
                "recommended_line": rec_line
            },
            "summary": summary
        }
