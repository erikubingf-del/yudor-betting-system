import sys
import os
import json
import time
import argparse
from typing import List, Dict
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import Phase 2 Components
# Import Phase 2 Components
from scripts.Phase2.data_collector import DataCollector
from scripts.Phase2.stats_collector import ComprehensiveStatsScraper
from scripts.Phase2.lineup_collector import FotMobScraper as LineupCollector
from scripts.Phase2.api_football_collector import APIFootballCollector
from scripts.Phase2.footystats_collector import FootyStatsCollector
from scripts.Phase2.context_analyzer import ContextAnalyzer
from scripts.Phase2.ah_value_finder import AsianHandicapModel
from scripts.Phase2.q_scorers import get_all_q_scores
from scripts.Phase2.medallion_score_engine import MedallionScoreEngine
from scripts.Phase2.poisson_ah_model import PoissonAHModel, create_team_metrics_from_data

class Phase2Orchestrator:
    """
    Master Orchestrator for Phase 2.
    Runs the full pipeline for a list of matches:
    1. Qualitative Data (News/Previews) -> DataCollector
    2. Quantitative Data (Stats/xG/Elo) -> StatsCollector
    3. Lineups/Formations -> LineupCollector
    4. API-Football Data (Predictions/Injuries) -> APIFootballCollector
    5. FootyStats Data (Advanced Stats) -> FootyStatsCollector
    6. Feature Engineering -> Q-Scores (Q7, Q8, Q14)
    7. Context Analysis -> Sentiment Score
    8. Modeling -> AH Value Finder (Poisson + Adjustments)
    """
    
    def __init__(self, league: str = "Brasileirão", season: str = "2025"):
        print(f"🚀 Initializing Phase 2 Orchestrator ({league} {season})...")
        self.league = league
        self.season = season
        
        # Initialize Components
        self.data_collector = DataCollector()
        self.context_analyzer = ContextAnalyzer() 
        self.footystats = FootyStatsCollector(api_key="c715e230a56b394e01389862fd3bb752e3f9d5e174b2ec86de081c6740a2fcd2")
        self.api_football = APIFootballCollector()
        
        # Models
        self.medallion_engine = MedallionScoreEngine()  # Ultra-advanced scoring engine
        self.poisson_ah_model = PoissonAHModel()  # Mathematically rigorous Poisson model

        # Models
        self.context_analyzer = ContextAnalyzer()
        
        # Try initializing Hard Stats collectors
        try:
            self.stats_collector = ComprehensiveStatsScraper(league=league, season=season)
            self.lineup_collector = FotMobScraper()
            self.has_hard_stats = True
            print("   ✅ Hard Stats Collectors (FBref/FotMob) ready.")
        except Exception as e:
            print(f"   ⚠️  Hard Stats Collectors unavailable: {e}")
            self.has_hard_stats = False
            
        # Initialize Model
        self.ah_model = AsianHandicapModel(season_id=12345) 
        
    def calculate_confidence(self, match_data: Dict) -> Dict:
        """
        Calculates a Confidence Score (0-100%) and determines if match should be VETOED.
        """
        score = 0
        reasons = []
        veto = False
        
        # 1. News Quantity (20%)
        news = match_data.get("data", {}).get("news", {}).get("news", {})
        home_news = len(news.get("home", []))
        away_news = len(news.get("away", []))
        total_news = home_news + away_news
        
        if total_news >= 10:
            score += 20
            reasons.append(f"✅ Good News Coverage ({total_news} items)")
        elif total_news >= 4:
            score += 10
            reasons.append(f"⚠️ Low News Coverage ({total_news} items)")
        else:
            reasons.append(f"❌ Insufficient News ({total_news} items)")
            
        # 2. Hard Stats (30%)
        if "home_stats" in match_data["data"] and (match_data["data"]["home_stats"].get("fbref") or match_data["data"]["home_stats"].get("api_football") or match_data["data"]["home_stats"].get("footystats")):
            score += 30
            reasons.append("✅ Hard Stats Available")
        else:
            reasons.append("❌ Missing Hard Stats")
            
        # 3. Lineups (20%)
        if "lineups" in match_data["data"] and match_data["data"]["lineups"].get("home_formation") != "0":
            score += 20
            reasons.append("✅ Lineups Found (FotMob)")
        elif "api_football" in match_data["data"] and match_data["data"]["api_football"].get("lineups"):
            score += 20
            reasons.append("✅ Lineups Found (API-Football)")
        else:
            reasons.append("⚠️ Missing Lineups")
            
        # 4. API-Football Extra Data (20%)
        if "api_football" in match_data["data"] and match_data["data"]["api_football"]:
            details = match_data["data"]["api_football"]
            if details.get("predictions"):
                score += 10
                reasons.append("✅ API Predictions Available")
            if details.get("injuries"):
                score += 10
                reasons.append("✅ API Injury Reports Available")
            
        # 5. Sentiment Clarity (10%)
        sentiment = abs(match_data["analysis"].get("sentiment_score", 0))
        if sentiment > 0.2:
            score += 10
            reasons.append("✅ Clear Sentiment Signal")
        else:
            reasons.append("ℹ️ Neutral Sentiment")

        # VETO Logic
        if score < 40: # Lowered threshold slightly as we have more sources
            veto = True
            reasons.append("⛔ VETO: Confidence Score too low (<40%)")
        elif total_news < 2 and not match_data.get("data", {}).get("api_football"):
            veto = True
            reasons.append("⛔ VETO: Critical Data Missing (News & API)")
            
        return {
            "score": score,
            "veto": veto,
            "reasons": reasons
        }

    def process_matches(self, matches: List[Dict]):
        results = []
        print(f"DEBUG: Received matches: {matches}")
        print(f"\n📋 Processing {len(matches)} matches...")
        
        for i, m in enumerate(matches):
            home = m["home"]
            away = m["away"]
            date = m["date"]
            
            print(f"\n{'='*60}")
            print(f"⚽ Match {i+1}/{len(matches)}: {home} vs {away}")
            print(f"{'='*60}")
            
            match_result = {
                "match_info": m,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "data": {},
                "analysis": {},
                "value_bets": []
            }
            
            # --- STEP 1: Qualitative Data (News) ---
            print("\n[1] Collecting News & Context...")
            news_data = self.data_collector.collect_data(home, away, date)
            match_result["data"]["news"] = news_data
            
            # Analyze Sentiment
            full_text = ""
            for team in ["home", "away"]:
                for item in news_data["news"].get(team, []):
                    full_text += item.get("title", "") + ". "
            for item in news_data["news"].get("match", []):
                full_text += item.get("title", "") + ". " + item.get("content", "") + ". "
                
            sentiment_score = self.context_analyzer.analyze_text(full_text)
            match_result["analysis"]["sentiment_score"] = sentiment_score
            print(f"    -> Sentiment Score: {sentiment_score:.2f}")
            
            # --- STEP 2: Quantitative Data (Hard Stats) ---
            if self.has_hard_stats:
                print("\n[2] Collecting Hard Stats (FBref/FotMob)...")
                try:
                    home_stats = self.stats_collector.get_all_team_stats(home)
                    away_stats = self.stats_collector.get_all_team_stats(away)
                    match_result["data"]["home_stats"] = home_stats
                    match_result["data"]["away_stats"] = away_stats
                except Exception as e:
                    print(f"    ⚠️ Error fetching team stats: {e}")
                
                try:
                    formations = self.lineup_collector.get_formations(home, away, date, self.league)
                    match_result["data"]["lineups"] = formations
                    print(f"    -> Formations: {formations.get('home_formation')} vs {formations.get('away_formation')}")
                except Exception as e:
                    print(f"    ⚠️ Error fetching lineups: {e}")
            
            # --- STEP 3: API-Football Data ---
            print("\n[3] Fetching API-Football Data...")
            # Default to Brasileirão (71) and 2025 (or 2024 if 2025 fails in API logic)
            league_id = 71 
            season_year = int(self.season) if self.season.isdigit() else 2025
            api_details = {}
            
            fixture_info = self.api_football.get_fixture_id(home, away, date, league_id=league_id, season=season_year)
            
            if fixture_info:
                fid = fixture_info["id"]
                home_id = fixture_info["home_id"]
                away_id = fixture_info["away_id"]
                
                print(f"    -> Found Fixture ID: {fid}")
                api_details = self.api_football.get_fixture_details(fid)
                match_result["data"]["api_football"] = api_details
                
                # Fetch Team Stats from API (Replacement for missing FBref)
                print("    -> Fetching Team Stats from API...")
                api_home_stats = self.api_football.get_team_stats(home_id, league_id, season_year)
                api_away_stats = self.api_football.get_team_stats(away_id, league_id, season_year)
                
                if api_home_stats:
                    match_result["data"]["home_stats"] = match_result["data"].get("home_stats") or {}
                    match_result["data"]["home_stats"]["api_football"] = api_home_stats
                    print("       ✅ Home Stats Fetched")
                if api_away_stats:
                    match_result["data"]["away_stats"] = match_result["data"].get("away_stats") or {}
                    match_result["data"]["away_stats"]["api_football"] = api_away_stats
                    print("       ✅ Away Stats Fetched")
                
                if api_details.get("predictions"):
                    pred = api_details["predictions"][0].get("predictions", {})
                    print(f"    -> API Prediction: {pred.get('winner', {}).get('name')} (Advice: {pred.get('advice')})")
                
                # --- LINEUP FALLBACK LOGIC (Projected/Confirmed) ---
            # If FotMob failed (formations 0 vs 0) but API has lineups, use API.
            # API-Football often provides "Projected" lineups 24-48h before match in the same endpoint.
            current_lineups = match_result["data"].get("lineups", {})
            if current_lineups.get("home_formation") == "0" and api_details.get("lineups"):
                print("    🔄 Using API-Football Lineups (Projected/Confirmed)...")
                try:
                    # API Lineups format is a list of 2 dicts (one for each team)
                    api_lineups = api_details["lineups"]
                    new_lineups = {
                        "home_formation": "0",
                        "away_formation": "0",
                        "home_lineup": [],
                        "away_lineup": [],
                        "source": "api_football (Projected/Confirmed)"
                    }
                    
                    for team_data in api_lineups:
                        # Check if this is a confirmed lineup or projected
                        # API-Football doesn't always explicitly say, but if it's early, it's projected.
                        
                        formation = team_data.get("formation")
                        start_xi = team_data.get("startXI", [])
                        
                        # Identify Home/Away
                        if team_data["team"]["id"] == home_id:
                            new_lineups["home_formation"] = formation or "Projected"
                            new_lineups["home_lineup"] = [{"name": p["player"]["name"], "number": p["player"]["number"], "pos": p["player"]["pos"]} for p in start_xi]
                        elif team_data["team"]["id"] == away_id:
                            new_lineups["away_formation"] = formation or "Projected"
                            new_lineups["away_lineup"] = [{"name": p["player"]["name"], "number": p["player"]["number"], "pos": p["player"]["pos"]} for p in start_xi]
                            
                    match_result["data"]["lineups"] = new_lineups
                    print(f"    -> API Formations: {new_lineups['home_formation']} vs {new_lineups['away_formation']}")
                    
                except Exception as e:
                    print(f"    ⚠️ Error parsing API lineups: {e}")

            elif current_lineups.get("home_formation") == "0":
                print("    ℹ️ Lineups not found in API-Football (yet).")
                match_result["data"]["api_football"] = {}

            # --- STEP 3.5: FootyStats Data (New Layer) ---
            print("\n[3.5] Fetching FootyStats Data...")
            fs_season_id = self.footystats.get_season_id(self.league, season_year)
            if fs_season_id:
                print(f"    -> Found Season ID: {fs_season_id}")
                # Fetch all teams stats for the season (efficient)
                fs_teams_data = self.footystats.get_team_stats(fs_season_id)
                
                # Find Home/Away in FootyStats data
                fs_home = next((stats for name, stats in fs_teams_data.items() if home.lower() in name.lower() or name.lower() in home.lower()), None)
                fs_away = next((stats for name, stats in fs_teams_data.items() if away.lower() in name.lower() or name.lower() in away.lower()), None)
                
                if fs_home:
                    match_result["data"]["home_stats"] = match_result["data"].get("home_stats") or {}
                    match_result["data"]["home_stats"]["footystats"] = fs_home
                    print(f"       ✅ FootyStats: {home} (xG: {fs_home.get('xg_for', 'N/A')})")
                if fs_away:
                    match_result["data"]["away_stats"] = match_result["data"].get("away_stats") or {}
                    match_result["data"]["away_stats"]["footystats"] = fs_away
                    print(f"       ✅ FootyStats: {away} (xG: {fs_away.get('xg_for', 'N/A')})")
                    
                # --- FOOTYSTATS LINEUP FALLBACK ---
                # If still no lineups, try FootyStats
                current_lineups = match_result["data"].get("lineups", {})
                if current_lineups.get("home_formation") == "0":
                    print("    🔄 Checking FootyStats for Lineups...")
                    # We need to find the specific match ID in FootyStats
                    # This requires fetching all matches for the season
                    fs_matches = self.footystats.get_matches_for_season(fs_season_id)
                    
                    # Filter for our match
                    # FootyStats match objects usually have 'homeTeam' and 'awayTeam' names
                    # and 'date_unix' or 'date_iso'
                    target_fs_match = None
                    for m in fs_matches:
                        # Simple name check
                        m_home = m.get("home_name", "")
                        m_away = m.get("away_name", "")
                        if (home in m_home or m_home in home) and (away in m_away or m_away in away):
                            target_fs_match = m
                            break
                    
                    if target_fs_match:
                        fs_match_id = target_fs_match.get("id")
                        print(f"       -> Found FootyStats Match ID: {fs_match_id}")
                        fs_lineups = self.footystats.get_match_lineups(fs_match_id)
                        
                        if fs_lineups:
                            print("       ✅ Found FootyStats Lineups!")
                            # Parse and use them (Simplified mapping)
                            # FootyStats format needs inspection, but assuming standard dict
                            match_result["data"]["lineups"]["source"] = "footystats"
                            match_result["data"]["lineups"]["raw_footystats"] = fs_lineups
                            # We might not parse fully to formation string yet, but we save the data
                            match_result["data"]["lineups"]["home_formation"] = "Available (FS)"
                            match_result["data"]["lineups"]["away_formation"] = "Available (FS)"
                    else:
                        print("       ⚠️ Match not found in FootyStats list.")

            else:
                print("    ⚠️ Season not found in FootyStats.")
                
            # Fallback for Form Analysis if FootyStats missing
            if "footystats" not in match_result["data"].get("home_stats", {}):
                print("    -> Using API Stats for Form Analysis")

            # --- STEP 4: Feature Engineering (Q-Scores) ---
            print("\n[4] Calculating Q-Scores (Advanced Metrics)...")
            try:
                q_scores = get_all_q_scores(match_result)
                
                print(f"    -> Home Q-Score: {q_scores['home']:.1f}")
                print(f"    -> Away Q-Score: {q_scores['away']:.1f}")
                
                # Print Breakdown
                details = q_scores.get("details", {})
                print(f"       Attack (Q2): H {details['Q2_Attack']['home']} vs A {details['Q2_Attack']['away']}")
                print(f"       Defense (Q4): H {details['Q4_Defense']['home']} vs A {details['Q4_Defense']['away']}")
                print(f"       Tactics (Q6): H {details['Q6_Tactics']['home']} vs A {details['Q6_Tactics']['away']}")
                print(f"       H2H (Q17): H {details['Q17_H2H']['home']} vs A {details['Q17_H2H']['away']}")
                
            except Exception as e:
                print(f"    ⚠️ Error calculating Q-Scores: {e}")
                q_scores = {"home": 50.0, "away": 50.0} # Fallback
                
            match_result["analysis"]["q_scores"] = q_scores
            


            # --- MEDALLION ENGINE (Ultra-Advanced AH Analysis) ---
            print("\n[4.6] Running Medallion Score Engine (Quantitative AH Analysis)...")
            try:
                # Extract injuries by team from API-Football
                all_injuries = match_result["data"].get("api_football", {}).get("injuries", [])
                home_injuries = [inj for inj in all_injuries if inj.get("team", {}).get("name", "").lower() in home.lower() or home.lower() in inj.get("team", {}).get("name", "").lower()]
                away_injuries = [inj for inj in all_injuries if inj.get("team", {}).get("name", "").lower() in away.lower() or away.lower() in inj.get("team", {}).get("name", "").lower()]

                # Fetch Key Players (Refinement)
                home_id = match_result["data"].get("api_football", {}).get("fixture", {}).get("teams", {}).get("home", {}).get("id")
                away_id = match_result["data"].get("api_football", {}).get("fixture", {}).get("teams", {}).get("away", {}).get("id")
                
                home_key_players = []
                away_key_players = []
                
                if home_id:
                    print(f"    🔎 Fetching Key Players for Home Team (ID: {home_id})...")
                    home_key_players = self.api_football.get_key_players(home_id, season=2025)
                if away_id:
                    print(f"    🔎 Fetching Key Players for Away Team (ID: {away_id})...")
                    away_key_players = self.api_football.get_key_players(away_id, season=2025)

                # Extract form strings from API-Football predictions data
                home_form_str = ""
                away_form_str = ""
                api_predictions = match_result["data"].get("api_football", {}).get("predictions", [])
                if api_predictions:
                    pred_data = api_predictions[0] if isinstance(api_predictions, list) else api_predictions
                    home_form_str = pred_data.get("teams", {}).get("home", {}).get("league", {}).get("form", "")
                    away_form_str = pred_data.get("teams", {}).get("away", {}).get("league", {}).get("form", "")

                # Extract formations
                lineups = match_result["data"].get("lineups", {})
                home_formation = lineups.get("home_formation", "4-3-3")
                away_formation = lineups.get("away_formation", "4-3-3")

                # Build match context
                match_context = {
                    "home_team": home,
                    "away_team": away,
                    "date": date,
                    "total_teams": 20,  # Brasileirão
                    "match_type": "league"
                }

                # Run Medallion analysis
                medallion_result = self.medallion_engine.analyze_match(
                    home_stats=match_result["data"].get("home_stats", {}),
                    away_stats=match_result["data"].get("away_stats", {}),
                    match_context=match_context,
                    home_injuries=home_injuries,
                    away_injuries=away_injuries,
                    home_formation=home_formation,
                    away_formation=away_formation,
                    home_form=home_form_str[-6:] if home_form_str else None,
                    away_form=away_form_str[-6:] if away_form_str else None,
                    home_key_players=home_key_players,
                    away_key_players=away_key_players
                )

                match_result["analysis"]["medallion"] = medallion_result

                # Print Summary
                print(f"\n{medallion_result['summary']}")

            except Exception as e:
                print(f"    ⚠️ Error in Medallion Engine: {e}")
                import traceback
                traceback.print_exc()

            # --- POISSON MODEL (Mathematically Rigorous AH Analysis) ---
            print("\n[4.7] Running Poisson AH Model (Mathematical Foundation)...")
            try:
                # Create TeamMetrics from our data sources
                home_metrics = create_team_metrics_from_data(
                    name=home,
                    footystats=match_result["data"].get("home_stats", {}).get("footystats"),
                    api_football=match_result["data"].get("home_stats", {}).get("api_football")
                )
                away_metrics = create_team_metrics_from_data(
                    name=away,
                    footystats=match_result["data"].get("away_stats", {}).get("footystats"),
                    api_football=match_result["data"].get("away_stats", {}).get("api_football")
                )

                # Run Poisson analysis
                poisson_result = self.poisson_ah_model.analyze_match(
                    home_metrics=home_metrics,
                    away_metrics=away_metrics
                )

                match_result["analysis"]["poisson"] = poisson_result

                # Print Summary
                print(f"\n{poisson_result['summary']}")

                # Compare with Medallion for consensus check
                medallion_line = match_result["analysis"].get("medallion", {}).get("ah_line", {}).get("recommended_line", 0)
                poisson_line = poisson_result.get("fair_ah_line", {}).get("home_perspective", 0)
                
                consensus_status = "UNCERTAIN"
                veto_status = False
                veto_reason = ""

                if medallion_line is not None and poisson_line is not None:
                    line_diff = abs(medallion_line - poisson_line)
                    
                    if line_diff <= 0.25:
                        consensus_status = "✅ MODEL CONSENSUS"
                        print(f"    {consensus_status}: Both models agree on line ~{medallion_line}")
                    elif line_diff <= 0.5:
                        consensus_status = "⚠️ MINOR DIVERGENCE"
                        print(f"    {consensus_status}: Models differ by 0.5 (Med: {medallion_line}, Poi: {poisson_line})")
                    else:
                        consensus_status = "❌ MAJOR DIVERGENCE"
                        veto_status = True
                        veto_reason = f"Models disagree significantly (Med: {medallion_line}, Poi: {poisson_line})"
                        print(f"    {consensus_status}: {veto_reason} -> VETOED")
                        
                # Check for Insignificant Matches (Low Score)
                med_home_score = match_result["analysis"].get("medallion", {}).get("home_score", 0)
                med_away_score = match_result["analysis"].get("medallion", {}).get("away_score", 0)
                
                if abs(med_home_score) < 10 and abs(med_away_score) < 10:
                    veto_status = True
                    veto_reason = "Insignificant Match (Scores < 10%)"
                    print(f"    ❌ VETOED: {veto_reason}")

                match_result["analysis"]["consensus"] = {
                    "status": consensus_status,
                    "medallion_line": medallion_line,
                    "poisson_line": poisson_line,
                    "veto": veto_status,
                    "veto_reason": veto_reason
                }
                
                # --- WORKFLOW: Save to Ledger ---
                print(f"    [DEBUG] Veto: {veto_status}, Status: {consensus_status}")
                if not veto_status and consensus_status != "UNCERTAIN":
                    self.save_to_ledger(match_result, medallion_line, poisson_line, consensus_status)

            except Exception as e:
                print(f"    ⚠️ Error in Poisson Model: {e}")
                import traceback
                traceback.print_exc()

            # --- STEP 5: Confidence Check & Veto ---
            print("\n[4] Running Confidence Check...")
            confidence = self.calculate_confidence(match_result)
            match_result["analysis"]["confidence"] = confidence
            
            print(f"    -> Confidence Score: {confidence['score']}%")
            for reason in confidence['reasons']:
                print(f"       {reason}")
                
            if confidence['veto']:
                print(f"    ⛔ MATCH VETOED: Skipping Model Analysis.")
                match_result["veto_status"] = "VETOED"
                self.save_match_data_json(match_result) # Save data even if vetoed
                results.append(match_result)
                continue 
            
            # --- STEP 6: Model & Value Calculation ---
            print("\n[5] Running Yudor Model...")
            
            # 1. Get True Probabilities & Optimal Line
            yudor_data = self.ah_model.calculate_yudor_fair_odds(home, away)
            # Calculate True Odds & Line regardless of "Value"
            probs = self.ah_model.calculate_yudor_fair_odds(
                home_team=home,
                away_team=away,
                home_stats=match_result["data"].get("home_stats", {}),
                away_stats=match_result["data"].get("away_stats", {}),
                sentiment_score=sentiment_score,
                q_scores=q_scores
            )
            
            # Store the math in the result
            match_result["analysis"]["true_probabilities"] = probs["probabilities"]
            match_result["analysis"]["fair_odds"] = probs["fair_odds"]
            match_result["analysis"]["optimal_line"] = probs["optimal_line"]
            
            print(f"    -> True Prob: Home {probs['probabilities']['home']:.2%} | Draw {probs['probabilities']['draw']:.2%} | Away {probs['probabilities']['away']:.2%}")
            print(f"    -> Optimal Line: {probs['optimal_line']}")
            print(f"    -> Fair Odds: {probs['fair_odds']}")

            # Check for Value
            value_bets = self.ah_model.get_value_bets(
                home_team=home,
                away_team=away,
                true_probs=probs,
                market_odds={} # We don't have live market odds in this flow yet, user inputs them in Dashboard
            )
            
            if value_bets:
                print(f"    💰 VALUE FOUND: {len(value_bets)} bets")
                match_result["analysis"]["value_bets"] = value_bets
            else:
                print("    ❌ No Value Found (Model might need training or odds don't match)")
                
            # --- STEP 7: Save Granular Data for ML ---
            self.save_match_data_json(match_result)

            results.append(match_result)
            
        return results

    def save_match_data_json(self, match_result):
        """
        Saves the FULL match_result to a structured file for future training.
        Structure: data/matches/{league}/{season}/{YYYY-MM-DD}_{home}_{away}.json
        """
        import os
        import json
        from datetime import datetime
        
        try:
            # Handle nested match_info structure
            if "match_info" in match_result:
                home = match_result["match_info"].get("home")
                away = match_result["match_info"].get("away")
                date = match_result["match_info"].get("date")
            else:
                home = match_result.get("home")
                away = match_result.get("away")
                date = match_result.get("date")
            
            home = home or "UnknownHome"
            away = away or "UnknownAway"
            date = date or "UnknownDate"
            
            safe_league = self.league.replace(" ", "_")
            safe_season = self.season
            safe_home = home.replace(" ", "_")
            safe_away = away.replace(" ", "_")
            
            # Convert date to ISO format (YYYY-MM-DD) for sorting
            try:
                if "/" in date:
                    dt = datetime.strptime(date, "%d/%m/%Y")
                    safe_date = dt.strftime("%Y-%m-%d")
                else:
                    safe_date = date
            except:
                safe_date = date.replace("/", "-")
            
            # Create dir
            save_dir = os.path.join(PROJECT_ROOT, "data", "matches", safe_league, safe_season)
            os.makedirs(save_dir, exist_ok=True)
            
            filename = f"{safe_date}_{safe_home}_vs_{safe_away}.json"
            filepath = os.path.join(save_dir, filename)
            
            # Sanitize before saving
            def sanitize(obj):
                if isinstance(obj, dict):
                    return {str(k): sanitize(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [sanitize(v) for v in obj]
                elif isinstance(obj, tuple):
                    return str(obj)
                else:
                    return obj
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(sanitize(match_result), f, indent=4, ensure_ascii=False)
            
            print(f"    💾 Match Data Saved: {filepath}")
            match_result["data_file"] = str(filepath) # Link result to data file
            
        except Exception as e:
            print(f"    ⚠️ Error saving match data: {e}")
            # Do not append to results here, it's done in the main loop

    def save_to_ledger(self, match_result, medallion_line, poisson_line, consensus_status):
        """
        Appends a high-confidence bet to the betting ledger.
        """
        import csv
        import os
        from datetime import datetime
        
        ledger_path = "betting_ledger.csv"
        
        # Prepare Data
        if "match_info" in match_result:
            date = match_result["match_info"].get("date")
            home = match_result["match_info"].get("home")
            away = match_result["match_info"].get("away")
            match_name = f"{home} vs {away}"
        else:
            date = match_result.get("date")
            match_name = f"{match_result.get('home')} vs {match_result.get('away')}"
            
        league = self.league # Use self.league as it's cleaner
        
        # Selection: Use Medallion Line as the primary recommendation
        selection = f"AH {medallion_line}"
        if medallion_line > 0: selection = f"AH +{medallion_line}"
        
        # Market Odds (Placeholder - usually from API, but we might not have exact AH odds)
        # We'll use 1.90 as a standard placeholder for AH lines
        market_odds = 1.90 
        
        # True Odds (from Poisson)
        # Poisson gives probabilities, but converting to AH odds is complex.
        # We'll store the Poisson Line as "True Line" reference
        true_odds = f"Line {poisson_line}"
        
        # Stake (Kelly - Placeholder for now, or 1 unit)
        stake = 1.0
        if consensus_status == "✅ MODEL CONSENSUS":
            stake = 2.0
            
        # Probabilities
        probs = match_result["analysis"].get("poisson", {}).get("probabilities", {})
        h_prob = probs.get("home", 0)
        a_prob = probs.get("away", 0)
        
        row = [
            date,
            match_name,
            league,
            selection,
            market_odds,
            true_odds,
            stake,
            consensus_status, # Confidence
            f"Med:{medallion_line}|Poi:{poisson_line}", # System Edge / Notes
            f"{h_prob:.2f}",
            f"{a_prob:.2f}",
            "PENDING", # Result
            0.0, # Profit/Loss
            "PENDING", # Status
            "" # Notes
        ]
        
        # Write to CSV
        file_exists = os.path.isfile(ledger_path)
        
        try:
            with open(ledger_path, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    # Header
                    writer.writerow(["Date","Match","League","Selection","Market_Odds","True_Odds","Stake","Confidence","System_Edge","Model_Home_Prob","Model_Away_Prob","Result","Profit_Loss","Status","Notes"])
                writer.writerow(row)
            print(f"    💾 Saved to Ledger: {selection} ({consensus_status})")
        except Exception as e:
            print(f"    ⚠️ Error saving to ledger: {e}")

    def save_results(self, results: List[Dict], filename: str = "phase2_results.json"):
        def sanitize(obj):
            if isinstance(obj, dict):
                return {str(k): sanitize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize(v) for v in obj]
            elif isinstance(obj, tuple):
                return str(obj)
            else:
                return obj
                
        sanitized_results = sanitize(results)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(sanitized_results, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Results saved to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to matches file (csv or txt)")
    parser.add_argument("--league", default="Brasileirão", help="League name")
    parser.add_argument("--season", default="2025", help="Season (e.g. 2425 or 2025)")
    args = parser.parse_args()
    
    matches = []
    if args.input:
        with open(args.input, "r") as f:
            for line in f:
                if "," in line and not line.startswith("#"):
                    parts = [p.strip() for p in line.split(",")]
                    matches.append({"home": parts[0].split(" vs ")[0], "away": parts[0].split(" vs ")[1], "league": parts[1], "date": parts[2]})
    else:
        matches = [{"home": "Internacional", "away": "Santos", "league": "Brasileirão", "date": "25/11/2025"}]
        
    orchestrator = Phase2Orchestrator(league=args.league, season=args.season)
    results = orchestrator.process_matches(matches)
    orchestrator.save_results(results)
