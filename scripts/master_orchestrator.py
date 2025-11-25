#!/usr/bin/env python3
"""
🎯 YUDOR MASTER ORCHESTRATOR
Complete betting analysis system with blind pricing and persistent memory

Usage:
    python master_orchestrator.py analyze "Flamengo vs Bragantino, Brasileirão, 25/11/2025, 19:00"
    python master_orchestrator.py batch  # Analyze all matches in matches.txt
    python master_orchestrator.py review MATCH_ID  # Review past analysis
    python master_orchestrator.py track MATCH_ID --entered --edge 12.5  # Track bet
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic, APIError, RateLimitError
from pyairtable import Api
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =========================
# CONFIGURATION
# =========================

class Config:
    """System configuration - Edit these values"""

    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "")
    AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
    FOOTYSTATS_API_KEY = os.getenv("FOOTYSTATS_API_KEY", "c715e230a56b394e01389862fd3bb752e3f9d5e174b2ec86de081c6740a2fcd2")
    
    # Directories
    BASE_DIR = Path(__file__).parent.parent  # Project root (parent of scripts/)
    PROMPTS_DIR = BASE_DIR / "prompts"
    ANEXOS_DIR = PROMPTS_DIR / "anexos"
    ANALYSIS_DIR = BASE_DIR / "analysis_history"
    CONSOLIDATED_DIR = BASE_DIR / "consolidated_data"
    PRE_FILTER_DIR = BASE_DIR / "pre_filter_history"
    LOSS_LEDGER_DIR = BASE_DIR / "loss_ledger"
    SCRAPED_DIR = BASE_DIR / "scraped_data"

    # Files
    MATCHES_ALL_FILE = BASE_DIR / "matches_all.txt"
    MATCHES_PRIORITY_FILE = BASE_DIR / "matches_priority.txt"
    SCRAPER_SCRIPT = BASE_DIR / "scripts" / "scraper.py"

    # Settings
    CLAUDE_MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 8000
    DATA_QUALITY_THRESHOLD = 70  # Minimum quality score to analyze

    # Ensure directories exist
    for directory in [ANALYSIS_DIR, PROMPTS_DIR, ANEXOS_DIR, CONSOLIDATED_DIR,
                      PRE_FILTER_DIR, LOSS_LEDGER_DIR, SCRAPED_DIR]:
        directory.mkdir(exist_ok=True)


# =========================
# AIRTABLE SCHEMA
# =========================

class AirtableSchema:
    """
    Airtable Base Structure:
    
    Table 1: MATCH_ANALYSES
    - match_id (text, primary)
    - date (date)
    - home_team (text)
    - away_team (text)
    - league (text)
    - analysis_timestamp (datetime)
    - yudor_ah_fair (number) - Claude's fair line
    - yudor_decision (select: CORE/EXP/VETO/FLIP/IGNORAR)
    - cs_final (number)
    - r_score (number)
    - tier (number)
    - full_analysis (long text)
    - data_quality (number)
    - status (select: ANALYZED/BET_ENTERED/RESULT_RECORDED)
    
    Table 2: BETS_ENTERED
    - match_id (link to MATCH_ANALYSES)
    - entry_timestamp (datetime)
    - market_ah_line (number) - What market offered
    - market_ah_odds (number) - Odds you got
    - edge_pct (number) - Calculated edge
    - stake (number) - Amount bet
    - notes (long text)
    
    Table 3: RESULTS
    - match_id (link to MATCH_ANALYSES)
    - result_timestamp (datetime)
    - final_score (text)
    - ah_result (select: WIN/PUSH/LOSS)
    - profit_loss (number)
    - yudor_correct (checkbox) - Was Yudor's prediction right?
    - notes (long text)
    """
    
    TABLES = {
        "analyses": "Match Analyses",
        "bets": "Bets_Entered",
        "results": "Results"
    }


# =========================
# CORE SYSTEM CLASS
# =========================

class YudorOrchestrator:
    """Master orchestrator for the entire Yudor system"""

    def __init__(self):
        self.config = Config()
        self.claude = Anthropic(api_key=self.config.ANTHROPIC_API_KEY)

        # Initialize Airtable if configured
        if self.config.AIRTABLE_API_KEY and self.config.AIRTABLE_BASE_ID:
            self.airtable = Api(self.config.AIRTABLE_API_KEY)
            self.base = self.airtable.base(self.config.AIRTABLE_BASE_ID)
        else:
            self.airtable = None
            print("⚠️  Airtable not configured - using local storage only")

    # =========================
    # HELPER METHODS
    # =========================

    def call_claude_with_retry(self, prompt: str, model: str = "claude-3-5-sonnet-20241022",
                               max_tokens: int = 16000, max_retries: int = 3) -> str:
        """
        Call Claude API with retry logic and exponential backoff

        Handles:
        - Rate limiting (429 errors)
        - API errors (500+ errors)
        - Network timeouts

        Args:
            prompt: The prompt to send
            model: Claude model to use
            max_tokens: Maximum tokens in response
            max_retries: Maximum retry attempts

        Returns:
            Response text from Claude
        """
        retry_delay = 5  # Initial delay in seconds

        for attempt in range(max_retries):
            try:
                response = self.claude.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text

            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"⚠️  Rate limited. Waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Rate limit exceeded after {max_retries} attempts")
                    raise

            except APIError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay
                    print(f"⚠️  API Error: {str(e)[:60]}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ API Error after {max_retries} attempts: {e}")
                    raise

            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                raise

        raise Exception(f"Failed after {max_retries} attempts")

    def load_prompt(self, prompt_name: str) -> str:
        """Load a prompt file from prompts/ directory"""
        prompt_path = self.config.PROMPTS_DIR / prompt_name
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt not found: {prompt_path}")
        with open(prompt_path, encoding="utf-8") as f:
            return f.read()

    def call_claude(self, system_prompt: str, user_message: str, max_tokens: Optional[int] = None) -> str:
        """Helper to call Claude API"""
        if max_tokens is None:
            max_tokens = self.config.MAX_TOKENS

        try:
            message = self.claude.messages.create(
                model=self.config.CLAUDE_MODEL,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_message
                }]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Claude API call failed: {e}")

    def extract_json_from_response(self, response_text: str) -> Dict:
        """Extract JSON from Claude's response (handles markdown code blocks)"""
        # Try to extract JSON from markdown code blocks
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()

        return json.loads(response_text)

    def fetch_url_content(self, url: str, max_chars: int = 15000) -> str:
        """Fetch content from a URL using requests + BeautifulSoup"""
        if not url or url == "NOT_FOUND":
            return ""

        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
            }

            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                return f"[Error: HTTP {response.status_code}]"

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text content
            text = soup.get_text(separator="\n", strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = "\n".join(lines)

            # Truncate if too long
            if len(text) > max_chars:
                text = text[:max_chars] + "\n...[truncated]"

            return text

        except Exception as e:
            return f"[Error fetching: {str(e)[:100]}]"

    def fetch_all_match_content(self, match_data: Dict) -> Dict:
        """Fetch content from all URLs for a match"""
        urls = match_data.get("urls", {})
        fetched_content = {}

        # Priority URLs to fetch
        url_priorities = [
            ("sofascore", "SofaScore - Stats, Form, H2H"),
            ("whoscored", "WhoScored - Tactics, Formations"),
            ("sportsmole", "SportsMole - Preview, Team News"),
            ("flashscore", "FlashScore - Form, Results"),
            ("tm_home", "Transfermarkt Home - Squad Values"),
            ("tm_away", "Transfermarkt Away - Squad Values"),
            ("news_home", "Local News Home - Derby Context, Injuries, Motivation"),
            ("news_away", "Local News Away - Derby Context, Injuries, Motivation"),
        ]

        print("   📡 Fetching URL content...")

        for url_key, description in url_priorities:
            url = urls.get(url_key, "")
            if url and url != "NOT_FOUND":
                print(f"      • {url_key}: fetching...")
                content = self.fetch_url_content(url, max_chars=12000)
                if content and not content.startswith("[Error"):
                    fetched_content[url_key] = {
                        "url": url,
                        "description": description,
                        "content": content
                    }
                    print(f"        ✓ Got {len(content)} chars")
                else:
                    print(f"        ✗ Failed: {content[:50] if content else 'empty'}")
            else:
                print(f"      • {url_key}: NOT_FOUND")

        return fetched_content

    # =========================
    # FOOTYSTATS API INTEGRATION
    # =========================

    def fetch_footystats_seasons(self) -> Dict:
        """Fetch available seasons/leagues from FootyStats API"""
        import requests

        url = f"https://api.football-data-api.com/league-list?key={self.config.FOOTYSTATS_API_KEY}&chosen_leagues_only=true"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                return response.json()
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def get_footystats_season_id(self, league_name: str) -> Optional[int]:
        """Map league name to FootyStats season_id"""
        # Common league mappings (season IDs for 2025/2026 - CURRENT SEASON)
        league_map = {
            "premier league": 15050,   # England Premier League 2025/26
            "la liga": 14956,          # Spain La Liga 2025/26
            "bundesliga": 14968,       # Germany Bundesliga 2025/26
            "serie a": 15068,          # Italy Serie A 2025/26
            "ligue 1": 14932,          # France Ligue 1 2025/26
            "eredivisie": 14936,       # Netherlands Eredivisie 2025/26
            "liga portugal": 15115,    # Portugal Liga NOS 2025/26
            # Note: Some leagues may not have 2025/26 data yet
            # Fallback to 2024/25 for these:
            "brasileirão": 11321,      # Brazil Serie A 2024 (calendar year)
            "serie a brazil": 11321,   # Brazil Serie A 2024
            "championship": 12496,     # England Championship 2024/25 (update when available)
            "segunda división": 12467, # Spain Segunda 2024/25 (update when available)
            "2. bundesliga": 12528,    # Germany 2. Bundesliga 2024/25 (update when available)
        }

        league_lower = league_name.lower()
        for key, season_id in league_map.items():
            if key in league_lower or league_lower in key:
                return season_id
        return None

    def fetch_footystats_match(self, home_team: str, away_team: str, league: str, date: str) -> Dict:
        """
        Fetch match data from FootyStats API

        Args:
            home_team: Home team name
            away_team: Away team name
            league: League name
            date: Match date (DD/MM/YYYY)

        Returns:
            Dict with match stats, xG, form, H2H
        """
        import requests
        from datetime import datetime as dt

        season_id = self.get_footystats_season_id(league)
        if not season_id:
            return {"error": f"League not mapped: {league}"}

        # Fetch league matches
        url = f"https://api.football-data-api.com/league-matches?key={self.config.FOOTYSTATS_API_KEY}&season_id={season_id}"

        try:
            print(f"      • FootyStats: fetching matches for season {season_id}...")
            response = requests.get(url, timeout=30)

            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}"}

            data = response.json()
            matches = data.get("data", [])

            # Parse target date
            try:
                target_date = dt.strptime(date, "%d/%m/%Y")
            except ValueError:
                target_date = None

            # Find matching match
            home_lower = home_team.lower()
            away_lower = away_team.lower()

            best_match = None
            for match in matches:
                match_home = match.get("home_name", "").lower()
                match_away = match.get("away_name", "").lower()

                # Check team names (partial match)
                home_match = any(h in match_home or match_home in h for h in [home_lower, home_lower.replace(" ", "")])
                away_match = any(a in match_away or match_away in a for a in [away_lower, away_lower.replace(" ", "")])

                if home_match and away_match:
                    best_match = match
                    break

            if not best_match:
                return {"error": f"Match not found: {home_team} vs {away_team}"}

            # Extract relevant stats
            return self._extract_footystats_data(best_match)

        except Exception as e:
            return {"error": str(e)}

    def _extract_footystats_data(self, match: Dict) -> Dict:
        """Extract relevant data from FootyStats match object"""
        return {
            "source": "FootyStats",
            "match_id": match.get("id"),
            "home_team": match.get("home_name"),
            "away_team": match.get("away_name"),
            "status": match.get("status"),
            "game_week": match.get("game_week"),

            # xG Data
            "home_xg": match.get("team_a_xg"),
            "away_xg": match.get("team_b_xg"),
            "home_xg_avg": match.get("pre_match_teamA_overall_xg_for"),
            "away_xg_avg": match.get("pre_match_teamB_overall_xg_for"),

            # Match Stats (from completed matches)
            "home_goals": match.get("homeGoalCount"),
            "away_goals": match.get("awayGoalCount"),
            "home_shots": match.get("team_a_shots"),
            "away_shots": match.get("team_b_shots"),
            "home_shots_on_target": match.get("team_a_shotsOnTarget"),
            "away_shots_on_target": match.get("team_b_shotsOnTarget"),
            "home_possession": match.get("team_a_possession"),
            "away_possession": match.get("team_b_possession"),
            "home_corners": match.get("team_a_corners"),
            "away_corners": match.get("team_b_corners"),

            # Form Data (PPG = Points Per Game)
            "home_ppg": match.get("pre_match_teamA_overall_ppg"),
            "away_ppg": match.get("pre_match_teamB_overall_ppg"),
            "home_home_ppg": match.get("pre_match_teamA_home_ppg"),
            "away_away_ppg": match.get("pre_match_teamB_away_ppg"),

            # Goals Data
            "home_goals_scored_avg": match.get("pre_match_teamA_overall_goals_for"),
            "home_goals_conceded_avg": match.get("pre_match_teamA_overall_goals_against"),
            "away_goals_scored_avg": match.get("pre_match_teamB_overall_goals_for"),
            "away_goals_conceded_avg": match.get("pre_match_teamB_overall_goals_against"),

            # Over/Under Stats
            "home_over25_pct": match.get("pre_match_teamA_overall_over25_percentage"),
            "away_over25_pct": match.get("pre_match_teamB_overall_over25_percentage"),
            "home_btts_pct": match.get("pre_match_teamA_overall_btts_percentage"),
            "away_btts_pct": match.get("pre_match_teamB_overall_btts_percentage"),

            # Clean Sheets & Defense
            "home_cs_pct": match.get("pre_match_teamA_overall_clean_sheet_percentage"),
            "away_cs_pct": match.get("pre_match_teamB_overall_clean_sheet_percentage"),
            "home_fts_pct": match.get("pre_match_teamA_overall_fts_percentage"),
            "away_fts_pct": match.get("pre_match_teamB_overall_fts_percentage"),

            # Recent Form (Wins/Draws/Losses)
            "home_wins": match.get("pre_match_teamA_overall_wins"),
            "home_draws": match.get("pre_match_teamA_overall_draws"),
            "home_losses": match.get("pre_match_teamA_overall_losses"),
            "away_wins": match.get("pre_match_teamB_overall_wins"),
            "away_draws": match.get("pre_match_teamB_overall_draws"),
            "away_losses": match.get("pre_match_teamB_overall_losses"),

            # Corner Stats
            "home_corners_avg": match.get("pre_match_teamA_overall_corners_for"),
            "away_corners_avg": match.get("pre_match_teamB_overall_corners_for"),

            # Table Position
            "home_position": match.get("pre_match_teamA_overall_table_position"),
            "away_position": match.get("pre_match_teamB_overall_table_position"),

            # Odds (for reference - NOT used in blind pricing)
            "odds_ft_home": match.get("odds_ft_1"),
            "odds_ft_draw": match.get("odds_ft_x"),
            "odds_ft_away": match.get("odds_ft_2"),
            "odds_over25": match.get("odds_ft_over25"),
            "odds_btts_yes": match.get("odds_btts_yes"),
        }

    def fetch_footystats_team(self, team_name: str, league: str) -> Dict:
        """
        Fetch comprehensive team statistics from FootyStats API
        Uses league-tables endpoint for PPG, goals, and position data.
        Calculates xG averages from match history.

        Error-proof implementation with:
        - Retry logic for transient failures
        - Data validation
        - Graceful degradation
        """
        import requests
        import time

        season_id = self.get_footystats_season_id(league)
        if not season_id:
            return {"error": f"League not mapped: {league}", "partial": False}

        # Fetch from league-tables with retry logic
        url = f"https://api.football-data-api.com/league-tables?key={self.config.FOOTYSTATS_API_KEY}&season_id={season_id}"

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=20)

                if response.status_code == 429:  # Rate limited
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue

                if response.status_code != 200:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return {"error": f"HTTP {response.status_code}", "partial": False}

                data = response.json()

                # Validate API response structure
                if not data.get("success", True) == True:
                    return {"error": f"API error: {data.get('message', 'Unknown')}", "partial": False}

                teams = data.get("data", {}).get("league_table", [])

                if not teams:
                    return {"error": "No teams in league table", "partial": False}

                # Find team with flexible matching
                team_data = self._find_team_in_list(team_name, teams)

                if not team_data:
                    return {"error": f"Team not found: {team_name}", "partial": False}

                # Extract and validate data with safe defaults
                result = self._extract_team_stats(team_data)

                # Validate critical data points
                result["data_quality"] = self._validate_team_data(result)

                # Fetch xG data from matches (separate try/catch for graceful degradation)
                try:
                    xg_data = self._calculate_team_xg(team_data.get("id"), season_id)
                    if xg_data and "error_xg" not in xg_data:
                        result.update(xg_data)
                    else:
                        result["xg_note"] = "xG data unavailable"
                except Exception as xg_error:
                    result["xg_note"] = f"xG fetch failed: {str(xg_error)[:50]}"

                return result

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return {"error": "Request timeout after retries", "partial": False}

            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return {"error": "Connection error", "partial": False}

            except json.JSONDecodeError:
                return {"error": "Invalid JSON response", "partial": False}

            except Exception as e:
                return {"error": f"Unexpected error: {str(e)[:100]}", "partial": False}

        return {"error": "Max retries exceeded", "partial": False}

    def _find_team_in_list(self, team_name: str, teams: List[Dict]) -> Optional[Dict]:
        """Find team with flexible name matching"""
        import re
        import unicodedata

        def normalize(s: str) -> str:
            """Remove accents and normalize string"""
            if not s:
                return ""
            # Normalize unicode and remove accents
            s = unicodedata.normalize('NFD', s)
            s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
            return s.lower().strip()

        team_lower = team_name.lower().strip()
        team_norm = normalize(team_name)

        # Remove common suffixes for matching
        team_clean = re.sub(r'\s*(fc|cf|sc|ac|afc|united|city)$', '', team_lower, flags=re.IGNORECASE).strip()
        team_clean_norm = normalize(team_clean)

        # Common name variations mapping
        name_aliases = {
            "atletico madrid": ["atletico de madrid", "atlético madrid", "atlético de madrid", "atletico"],
            "atletico": ["atletico de madrid", "atlético madrid", "atlético de madrid"],
            "real madrid": ["real madrid cf"],
            "barcelona": ["fc barcelona"],
            "bayern munich": ["bayern münchen", "fc bayern münchen", "bayern munchen"],
            "bayern": ["bayern münchen", "fc bayern münchen"],
            "dortmund": ["borussia dortmund", "bvb"],
            "inter milan": ["internazionale", "inter"],
            "ac milan": ["milan"],
            "psg": ["paris saint-germain", "paris saint germain", "paris sg"],
        }

        # Priority 0: Check aliases
        aliases = name_aliases.get(team_lower, []) + name_aliases.get(team_clean, [])
        for alias in aliases:
            alias_norm = normalize(alias)
            for team in teams:
                clean_name = normalize(team.get("cleanName", ""))
                full_name = normalize(team.get("name", ""))
                if alias_norm in clean_name or alias_norm in full_name or clean_name in alias_norm:
                    return team

        # Priority 1: Exact match on cleanName (normalized)
        for team in teams:
            clean_name = normalize(team.get("cleanName", ""))
            if clean_name == team_norm or clean_name == team_clean_norm:
                return team

        # Priority 2: Partial match on cleanName or name (normalized)
        for team in teams:
            clean_name = normalize(team.get("cleanName", ""))
            full_name = normalize(team.get("name", ""))

            if (team_norm in clean_name or clean_name in team_norm or
                team_clean_norm in clean_name or clean_name in team_clean_norm or
                team_norm in full_name or team_clean_norm in full_name):
                return team

        # Priority 3: Word-based matching (e.g., "Mainz" matches "1. FSV Mainz 05")
        for team in teams:
            clean_name = normalize(team.get("cleanName", ""))
            full_name = normalize(team.get("name", ""))
            combined = f"{clean_name} {full_name}"

            # Check if main word is present
            main_word = team_clean_norm.split()[0] if team_clean_norm else team_norm.split()[0]
            if len(main_word) >= 3 and main_word in combined:
                return team

        return None

    def _extract_team_stats(self, team_data: Dict) -> Dict:
        """Extract team stats with safe defaults and validation"""

        def safe_int(val, default=0):
            try:
                return int(val) if val is not None else default
            except (ValueError, TypeError):
                return default

        def safe_float(val, default=0.0):
            try:
                return float(val) if val is not None else default
            except (ValueError, TypeError):
                return default

        # Calculate matches from W/D/L if matchesPlayed is missing
        wins_home = safe_int(team_data.get("seasonWins_home"))
        draws_home = safe_int(team_data.get("seasonDraws_home"))
        losses_home = safe_int(team_data.get("seasonLosses_home"))
        wins_away = safe_int(team_data.get("seasonWins_away"))
        draws_away = safe_int(team_data.get("seasonDraws_away"))
        losses_away = safe_int(team_data.get("seasonLosses_away"))

        home_matches = wins_home + draws_home + losses_home
        away_matches = wins_away + draws_away + losses_away
        matches_played = safe_int(team_data.get("matchesPlayed")) or (home_matches + away_matches)

        # Avoid division by zero
        matches_played = max(matches_played, 1)
        home_matches = max(home_matches, 1)
        away_matches = max(away_matches, 1)

        goals_scored = safe_int(team_data.get("seasonGoals"))
        goals_conceded = safe_int(team_data.get("seasonConceded"))
        goals_home = safe_int(team_data.get("seasonGoals_home"))
        goals_away = safe_int(team_data.get("seasonGoals_away"))
        conceded_home = safe_int(team_data.get("seasonConceded_home"))
        conceded_away = safe_int(team_data.get("seasonConceded_away"))

        # PPG calculation
        ppg_overall = safe_float(team_data.get("ppg_overall"))
        ppg_home = round((wins_home * 3 + draws_home) / home_matches, 2)
        ppg_away = round((wins_away * 3 + draws_away) / away_matches, 2)

        return {
            "source": "FootyStats",
            "team_id": team_data.get("id"),
            "team_name": team_data.get("name"),

            # === LEAGUE POSITION ===
            "position": safe_int(team_data.get("position")),
            "points": safe_int(team_data.get("points")),

            # === MATCHES PLAYED ===
            "matches_played_overall": matches_played,
            "matches_played_home": home_matches,
            "matches_played_away": away_matches,

            # === WIN/DRAW/LOSS RECORD ===
            "wins_overall": safe_int(team_data.get("seasonWins_overall")),
            "draws_overall": safe_int(team_data.get("seasonDraws_overall")),
            "losses_overall": safe_int(team_data.get("seasonLosses_overall")),
            "wins_home": wins_home,
            "draws_home": draws_home,
            "losses_home": losses_home,
            "wins_away": wins_away,
            "draws_away": draws_away,
            "losses_away": losses_away,

            # === POINTS PER GAME (PPG) - KEY FOR Q11 ===
            "ppg_overall": ppg_overall if ppg_overall else round((safe_int(team_data.get("points")) / matches_played), 2),
            "ppg_home": ppg_home,
            "ppg_away": ppg_away,

            # === GOALS SCORED - KEY FOR Q2 ===
            "goals_scored_overall": goals_scored,
            "goals_scored_home": goals_home,
            "goals_scored_away": goals_away,
            "goals_scored_avg_overall": round(goals_scored / matches_played, 2),
            "goals_scored_avg_home": round(goals_home / home_matches, 2),
            "goals_scored_avg_away": round(goals_away / away_matches, 2),

            # === GOALS CONCEDED - KEY FOR Q4 ===
            "goals_conceded_overall": goals_conceded,
            "goals_conceded_home": conceded_home,
            "goals_conceded_away": conceded_away,
            "goals_conceded_avg_overall": round(goals_conceded / matches_played, 2),
            "goals_conceded_avg_home": round(conceded_home / home_matches, 2),
            "goals_conceded_avg_away": round(conceded_away / away_matches, 2),

            # === GOAL DIFFERENCE ===
            "goal_difference": safe_int(team_data.get("seasonGoalDifference")) or (goals_scored - goals_conceded),
        }

    def _validate_team_data(self, result: Dict) -> Dict:
        """Validate team data and return quality assessment"""
        issues = []
        score = 100

        # Check critical fields
        if not result.get("position") or result.get("position") == 0:
            issues.append("Missing position")
            score -= 20

        if not result.get("matches_played_overall") or result.get("matches_played_overall") < 3:
            issues.append("Insufficient matches (<3)")
            score -= 30

        if result.get("goals_scored_overall") == 0 and result.get("goals_conceded_overall") == 0:
            issues.append("No goal data")
            score -= 25

        if not result.get("ppg_overall"):
            issues.append("Missing PPG")
            score -= 15

        # Sanity checks
        if result.get("position", 0) > 30:
            issues.append(f"Suspicious position: {result.get('position')}")
            score -= 10

        matches = result.get("matches_played_overall", 0)
        goals = result.get("goals_scored_overall", 0)
        if matches > 0 and goals / matches > 5:
            issues.append(f"Suspicious goals avg: {goals/matches:.1f}")
            score -= 10

        return {
            "score": max(0, score),
            "valid": score >= 50,
            "issues": issues if issues else ["All checks passed"]
        }

    def _calculate_team_xg(self, team_id: int, season_id: int) -> Dict:
        """Calculate team's xG averages from completed matches"""
        import requests

        if not team_id:
            return {}

        url = f"https://api.football-data-api.com/league-matches?key={self.config.FOOTYSTATS_API_KEY}&season_id={season_id}"

        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                return {}

            data = response.json()
            matches = data.get("data", [])

            xg_for_home = []
            xg_for_away = []
            xg_against_home = []
            xg_against_away = []

            for match in matches:
                if match.get("status") != "complete":
                    continue

                home_id = match.get("homeID")
                away_id = match.get("awayID")
                home_xg = match.get("team_a_xg")
                away_xg = match.get("team_b_xg")

                if home_xg is None or away_xg is None:
                    continue

                if home_id == team_id:
                    xg_for_home.append(float(home_xg))
                    xg_against_home.append(float(away_xg))
                elif away_id == team_id:
                    xg_for_away.append(float(away_xg))
                    xg_against_away.append(float(home_xg))

            result = {}

            if xg_for_home or xg_for_away:
                all_xg_for = xg_for_home + xg_for_away
                all_xg_against = xg_against_home + xg_against_away

                result["xg_for_avg_overall"] = round(sum(all_xg_for) / len(all_xg_for), 2) if all_xg_for else None
                result["xg_against_avg_overall"] = round(sum(all_xg_against) / len(all_xg_against), 2) if all_xg_against else None
                result["xg_for_avg_home"] = round(sum(xg_for_home) / len(xg_for_home), 2) if xg_for_home else None
                result["xg_for_avg_away"] = round(sum(xg_for_away) / len(xg_for_away), 2) if xg_for_away else None
                result["xg_against_avg_home"] = round(sum(xg_against_home) / len(xg_against_home), 2) if xg_against_home else None
                result["xg_against_avg_away"] = round(sum(xg_against_away) / len(xg_against_away), 2) if xg_against_away else None

                # xG difference (positive = creates more than concedes)
                if result.get("xg_for_avg_overall") and result.get("xg_against_avg_overall"):
                    result["xg_diff_overall"] = round(result["xg_for_avg_overall"] - result["xg_against_avg_overall"], 2)

            return result

        except Exception as e:
            return {"error_xg": str(e)}

    def fetch_all_footystats_data(self, match_info: Dict) -> Dict:
        """
        Fetch all available FootyStats data for a match

        Args:
            match_info: Dict with home, away, league, date

        Returns:
            Dict with match and team data
        """
        home = match_info.get("home", "")
        away = match_info.get("away", "")
        league = match_info.get("league", "")
        date = match_info.get("date", "")

        print(f"   📊 Fetching FootyStats data for {home} vs {away}...")

        result = {
            "match_data": None,
            "home_team_data": None,
            "away_team_data": None
        }

        # Fetch match data
        match_data = self.fetch_footystats_match(home, away, league, date)
        if "error" not in match_data:
            result["match_data"] = match_data
            print(f"      ✓ Match data found")
        else:
            print(f"      ✗ Match: {match_data.get('error', 'Unknown error')}")

        # Fetch team data
        home_data = self.fetch_footystats_team(home, league)
        if "error" not in home_data:
            result["home_team_data"] = home_data
            print(f"      ✓ Home team data found")
        else:
            print(f"      ✗ Home team: {home_data.get('error', 'Unknown error')}")

        away_data = self.fetch_footystats_team(away, league)
        if "error" not in away_data:
            result["away_team_data"] = away_data
            print(f"      ✓ Away team data found")
        else:
            print(f"      ✗ Away team: {away_data.get('error', 'Unknown error')}")

        return result

    # =========================
    # COMMAND 1: PRE-FILTER
    # =========================

    def pre_filter(self, input_file: Optional[str] = None):
        """
        Pre-filter strategy: Analyze all games for data quality

        Process:
        1. Read matches_all.txt (30-40 games)
        2. Run scraper for all games
        3. Run DATA_CONSOLIDATION_PROMPT (light mode) for each
        4. Calculate data quality scores
        5. Filter by threshold (default ≥70)
        6. Create matches_priority.txt with top 15-20 games
        7. Save pre-filter history

        Args:
            input_file: Path to input file (default: matches_all.txt)
        """
        print("\n" + "="*80)
        print("🎯 COMMAND: PRE-FILTER")
        print("="*80)

        # Load input file
        if input_file is None:
            input_file = self.config.MATCHES_ALL_FILE

        if not Path(input_file).exists():
            print(f"❌ Input file not found: {input_file}")
            print(f"💡 Create {input_file} with format:")
            print("   Mainz 05 vs Hoffenheim, Bundesliga, 21/11/2025, 20:30")
            print("   Valencia vs Levante, La Liga, 21/11/2025, 21:00")
            sys.exit(1)

        # Read all matches
        with open(input_file, encoding="utf-8") as f:
            matches = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        print(f"📋 Loaded {len(matches)} matches from {input_file}")

        # Step 1: Run scraper for all matches
        print("\n" + "-"*80)
        print("🔍 STEP 1: SCRAPING URLs for all matches")
        print("-"*80)

        # Create temporary matches file for scraper
        temp_matches_file = self.config.BASE_DIR / "temp_matches_for_scraper.txt"
        with open(temp_matches_file, "w", encoding="utf-8") as f:
            f.write("\n".join(matches))

        # Run scraper with explicit input file
        result = subprocess.run(
            [sys.executable, str(self.config.SCRAPER_SCRIPT), "--input", str(temp_matches_file)],
            capture_output=True,
            text=True,
            cwd=str(self.config.BASE_DIR)
        )

        if result.returncode != 0:
            print(f"❌ Scraper failed: {result.stderr}")
            sys.exit(1)

        # Load scraped data
        scraped_data_file = self.config.BASE_DIR / "match_data_v29.json"
        if not scraped_data_file.exists():
            print(f"❌ Scraper output not found: {scraped_data_file}")
            sys.exit(1)

        with open(scraped_data_file, encoding="utf-8") as f:
            scraped_data = json.load(f)

        print(f"✅ Scraped {len(scraped_data)} games successfully")

        # Step 2: Calculate data quality for each game
        print("\n" + "-"*80)
        print("📊 STEP 2: CALCULATING DATA QUALITY SCORES")
        print("-"*80)

        # Load DATA_CONSOLIDATION_PROMPT
        data_consolidation_prompt = self.load_prompt("DATA_CONSOLIDATION_PROMPT_v1.0.md")

        quality_results = []

        for idx, (match_id, match_data) in enumerate(scraped_data.items(), 1):
            print(f"\n[{idx}/{len(scraped_data)}] Analyzing: {match_id}")

            try:
                # Call Claude for data quality calculation
                user_message = f"""
Calculate data quality score for this match.

MATCH DATA:
{json.dumps(match_data, indent=2)}

INSTRUCTIONS:
1. Check which data sources are available (URLs found vs NOT_FOUND)
2. Calculate data quality score (0-100) based on:
   - Q1-Q19 data availability
   - Critical missing data (tactical preview, squad values, xG stats)
3. Output JSON with:
   - data_quality.score (0-100)
   - data_quality.assessment (Excellent/Good/Fair/Poor)
   - data_quality.missing_critical (list)
   - data_quality.proceed (true/false)

Focus ONLY on data quality calculation. Do NOT run full analysis.
"""

                response = self.call_claude(data_consolidation_prompt, user_message, max_tokens=2000)
                data_quality_json = self.extract_json_from_response(response)

                quality_score = data_quality_json.get("data_quality", {}).get("score", 0)
                assessment = data_quality_json.get("data_quality", {}).get("assessment", "Unknown")
                proceed = data_quality_json.get("data_quality", {}).get("proceed", False)

                quality_results.append({
                    "match_id": match_id,
                    "match_info": match_data.get("match_info", {}),
                    "quality_score": quality_score,
                    "assessment": assessment,
                    "proceed": proceed,
                    "urls": match_data.get("urls", {})
                })

                print(f"   Quality Score: {quality_score}/100 ({assessment}) {'✅' if proceed else '❌'}")

            except Exception as e:
                print(f"   ⚠️  Failed to calculate quality: {e}")
                quality_results.append({
                    "match_id": match_id,
                    "match_info": match_data.get("match_info", {}),
                    "quality_score": 0,
                    "assessment": "Error",
                    "proceed": False,
                    "error": str(e)
                })

        # Step 3: Filter by threshold
        print("\n" + "-"*80)
        print(f"📈 STEP 3: FILTERING BY THRESHOLD (≥{self.config.DATA_QUALITY_THRESHOLD})")
        print("-"*80)

        # Sort by quality score (descending)
        quality_results.sort(key=lambda x: x["quality_score"], reverse=True)

        # Filter by threshold
        priority_games = [g for g in quality_results if g["quality_score"] >= self.config.DATA_QUALITY_THRESHOLD]

        print(f"\n✅ {len(priority_games)} games pass quality threshold")
        print(f"❌ {len(quality_results) - len(priority_games)} games filtered out")

        # Step 4: Create matches_priority.txt
        print("\n" + "-"*80)
        print("📝 STEP 4: CREATING matches_priority.txt")
        print("-"*80)

        priority_file = self.config.MATCHES_PRIORITY_FILE

        with open(priority_file, "w", encoding="utf-8") as f:
            f.write("# PRIORITY GAMES (Pre-filtered by data quality)\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Threshold: ≥{self.config.DATA_QUALITY_THRESHOLD}/100\n\n")

            for game in priority_games:
                match_info = game["match_info"]
                f.write(f"{match_info.get('home', 'Unknown')} vs {match_info.get('away', 'Unknown')}, "
                       f"{match_info.get('league', 'Unknown')}, {match_info.get('date', 'Unknown')}  "
                       f"# Quality: {game['quality_score']}/100\n")

        print(f"✅ Saved to: {priority_file}")

        # Step 5: Save pre-filter history
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = self.config.PRE_FILTER_DIR / f"pre_filter_{timestamp}.json"

        with open(history_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "input_file": str(input_file),
                "total_games": len(matches),
                "scraped_games": len(scraped_data),
                "threshold": self.config.DATA_QUALITY_THRESHOLD,
                "priority_games": len(priority_games),
                "filtered_out": len(quality_results) - len(priority_games),
                "results": quality_results
            }, f, indent=2, ensure_ascii=False)

        print(f"💾 History saved to: {history_file}")

        # Summary
        print("\n" + "="*80)
        print("✅ PRE-FILTER COMPLETE")
        print("="*80)
        print(f"\n📊 SUMMARY:")
        print(f"   Total games analyzed: {len(quality_results)}")
        print(f"   Games passing threshold: {len(priority_games)}")
        avg_quality = (sum(g['quality_score'] for g in quality_results) / len(quality_results)) if quality_results else 0
        print(f"   Average quality score: {avg_quality:.1f}/100")
        print(f"\n📝 Next step: Run analyze-batch with {priority_file}")
        print(f"   python scripts/master_orchestrator.py analyze-batch --input {priority_file}")

    # =========================
    # STAGE 1: SCRAPING (OLD CODE)
    # =========================
    
    def run_scraper(self, match_string: Optional[str] = None) -> str:
        """
        Run scraper.py to get URLs

        Args:
            match_string: Single match like "Flamengo vs Bragantino, Brasileirão, 25/11/2025, 19:00"
                         If None, uses matches.txt

        Returns:
            Path to generated JSON file
        """
        print("\n" + "="*80)
        print("🔍 STAGE 1: SCRAPING URLs")
        print("="*80)

        # If single match, create temp matches.txt
        input_path = self.config.MATCHES_ALL_FILE
        if match_string:
            temp_file = self.config.BASE_DIR / "temp_matches.txt"
            with open(temp_file, "w") as f:
                f.write(match_string)
            input_path = temp_file

        # Run scraper
        result = subprocess.run(
            [sys.executable, str(self.config.SCRAPER_SCRIPT), "--input", str(input_path)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Scraper failed: {result.stderr}")
            sys.exit(1)

        print("✅ URLs scraped successfully")

        # Return path to generated JSON
        return str(self.config.BASE_DIR / "match_data_v29.json")

    def run_integrated_scraper(self, match_string: str) -> Dict:
        """
        Run integrated scraper combining FootyStats + FBref + Formations

        This is the NEW workflow using:
        - FootyStats URL scraping (existing)
        - FBref statistics (Q7, Q8, Q14)
        - Formation database (Q6)

        Args:
            match_string: Match like "Flamengo vs Bragantino, Brasileirão, 25/11/2025, 19:00"

        Returns:
            Complete structured match data
        """
        print("\n" + "="*80)
        print("🔍 STAGE 1: INTEGRATED DATA SCRAPING")
        print("="*80)

        # Parse match string
        parts = match_string.split(",")
        teams = parts[0].strip().split(" vs ")
        home_team = teams[0].strip()
        away_team = teams[1].strip()
        league = parts[1].strip()
        date = parts[2].strip()  # DD/MM/YYYY

        # Generate match ID
        teams_id = f"{home_team}{away_team}".replace(" ", "")
        date_id = date.replace("/", "")
        match_id = f"{teams_id}_{date_id}"

        print(f"Match: {home_team} vs {away_team}")
        print(f"League: {league}")
        print(f"Date: {date}")
        print(f"Match ID: {match_id}\n")

        # First, run URL scraper to get FootyStats URL
        urls_json_path = self.run_scraper(match_string)
        with open(urls_json_path) as f:
            urls_data = json.load(f)

        # Get the match data (there should be one match)
        match_data = next(iter(urls_data.values()))
        footystats_url = match_data.get("footystats_url", "")

        if not footystats_url:
            print("❌ No FootyStats URL found from scraper")
            sys.exit(1)

        print(f"FootyStats URL: {footystats_url}\n")

        # Now run integrated scraper
        print("🔄 Running integrated scraper...")

        try:
            from scripts.integrated_scraper import IntegratedDataScraper

            # Initialize integrated scraper
            scraper = IntegratedDataScraper(league=league, season='2425')

            # Scrape complete match data
            complete_data = scraper.scrape_complete_match_data(
                match_id=match_id,
                home_team=home_team,
                away_team=away_team,
                league=league,
                date=date,
                footystats_url=footystats_url
            )

            # Save to file
            output_path = self.config.BASE_DIR / f"match_data_INTEGRATED_{match_id}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(complete_data, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Saved integrated data to: {output_path}")

            return complete_data

        except ImportError as e:
            print(f"❌ Integrated scraper not available: {e}")
            print("   Falling back to old workflow")
            return None
        except Exception as e:
            print(f"❌ Integrated scraper failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # =========================
    # STAGE 2: DATA EXTRACTION
    # =========================
    
    def extract_data(self, urls_json_path: str) -> Dict:
        """
        Use Claude + web_fetch to extract data from URLs
        
        Args:
            urls_json_path: Path to match_data_v29.json
            
        Returns:
            Extracted data dictionary
        """
        print("\n" + "="*80)
        print("🔍 STAGE 2: EXTRACTING DATA (Claude + web_fetch)")
        print("="*80)
        
        # Load URLs JSON
        with open(urls_json_path) as f:
            urls_data = json.load(f)
        
        # Load extraction prompt
        extraction_prompt_path = self.config.PROMPTS_DIR / "EXTRACTION_PROMPT.md"
        if not extraction_prompt_path.exists():
            print("⚠️  EXTRACTION_PROMPT.md not found - using default")
            extraction_prompt = "Extract all data from these URLs for betting analysis."
        else:
            with open(extraction_prompt_path) as f:
                extraction_prompt = f.read()
        
        # Call Claude with web_fetch enabled
        print("🤖 Calling Claude API...")
        
        try:
            message = self.claude.messages.create(
                model=self.config.CLAUDE_MODEL,
                max_tokens=self.config.MAX_TOKENS,
                system=extraction_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Extract data from these match URLs:\n\n{json.dumps(urls_data, indent=2)}"
                }]
            )
            
            # Parse Claude's response (should be JSON)
            response_text = message.content[0].text
            
            # Try to extract JSON from response
            # Claude might wrap it in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            extracted_data = json.loads(response_text)
            
            print("✅ Data extracted successfully")
            
            # Save extracted data
            output_path = self.config.BASE_DIR / "match_data_PROCESSED.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved to: {output_path}")
            
            return extracted_data
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            sys.exit(1)
    
    # =========================
    # STAGE 3: YUDOR ANALYSIS (BLIND PRICING)
    # =========================
    
    def analyze_match(self, extracted_data: Dict, match_id: str, use_integrated: bool = False) -> Dict:
        """
        Run Yudor analysis with BLIND PRICING (no market odds)

        Args:
            extracted_data: Data from extraction stage (or integrated scraper)
            match_id: Match identifier
            use_integrated: If True, uses .claude/analysis_prompt.md with pre-calculated FBref scores

        Returns:
            Analysis results
        """
        print("\n" + "="*80)
        print("🎯 STAGE 3: YUDOR ANALYSIS (BLIND PRICING)")
        print("="*80)

        # Check if we should use new integrated workflow
        claude_analysis_prompt = self.config.BASE_DIR / ".claude" / "analysis_prompt.md"

        if use_integrated and claude_analysis_prompt.exists():
            # NEW WORKFLOW: Use .claude/analysis_prompt.md with FBref integration
            print("📋 Using NEW workflow (.claude/analysis_prompt.md + FBref)")

            with open(claude_analysis_prompt) as f:
                analysis_prompt = f.read()

            # Prepare prompt with match data
            full_prompt = f"""
{analysis_prompt}

## MATCH DATA TO ANALYZE:

{json.dumps(extracted_data, indent=2)}

## YOUR TASK:

Analyze this match using the structured data provided. Use the pre-calculated FBref scores for Q7, Q8, Q14. Calculate Q1-Q6, Q9-Q13, Q15-Q19 from FootyStats data. Output analysis in exact JSON format specified above.

🚨 CRITICAL: BLIND PRICING MODE 🚨
- DO NOT use or reference market odds
- Calculate YOUR fair Asian Handicap line
- User will calculate edge manually later
"""

            print("🤖 Running Yudor analysis with FBref integration...")

        else:
            # OLD WORKFLOW: Use existing YUDOR_ANALYSIS_PROMPT.md
            print("📋 Using OLD workflow (YUDOR_ANALYSIS_PROMPT.md)")

            yudor_prompt_path = self.config.PROMPTS_DIR / "YUDOR_ANALYSIS_PROMPT.md"
            if not yudor_prompt_path.exists():
                print("❌ YUDOR_ANALYSIS_PROMPT.md not found!")
                sys.exit(1)

            with open(yudor_prompt_path) as f:
                yudor_prompt = f.read()

            # CRITICAL: Add blind pricing instruction
            blind_pricing_instruction = """

🚨 CRITICAL: BLIND PRICING MODE 🚨

You MUST NOT see or use market odds in your analysis. Your job is to:

1. Analyze the match data objectively
2. Calculate YOUR fair Asian Handicap line based on:
   - Team strength difference
   - Form analysis
   - Home advantage
   - Injuries impact
   - All Q1-Q19 factors

3. Provide YOUR fair line (e.g., "Flamengo -1.25")
4. DO NOT calculate edge - user will do this manually
5. DO NOT reference market odds - stay blind

Your fair line should represent TRUE probability, not market opinion.

Example output:
{
  "yudor_fair_ah": -1.25,
  "yudor_fair_ah_odds": 2.05,
  "confidence": 82,
  "decision": "CORE",
  "reasoning": "Flamengo significantly stronger in all metrics..."
}

The user will compare YOUR line to market and calculate edge themselves.
            """

            yudor_prompt += blind_pricing_instruction
            full_prompt = f"Analyze this match (BLIND PRICING - no market odds):\n\n{json.dumps(extracted_data, indent=2)}"

        # Call Claude for analysis
        print("🤖 Running Yudor analysis...")

        try:
            message = self.claude.messages.create(
                model=self.config.CLAUDE_MODEL,
                max_tokens=self.config.MAX_TOKENS,
                system=yudor_prompt if not use_integrated or not claude_analysis_prompt.exists() else "",
                messages=[{
                    "role": "user",
                    "content": full_prompt
                }]
            )
            
            response_text = message.content[0].text
            
            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            analysis = json.loads(response_text)
            
            print("✅ Analysis complete")
            print(f"\n📊 RESULTS:")
            print(f"   Fair AH Line: {analysis.get('yudor_fair_ah', 'N/A')}")
            print(f"   Decision: {analysis.get('decision', 'N/A')}")
            print(f"   Confidence: {analysis.get('confidence', 0)}%")
            print(f"   CS Final: {analysis.get('cs_final', 0)}")
            print(f"   R-Score: {analysis.get('r_score', 0)}")
            
            # Save analysis
            timestamp = datetime.now().isoformat()
            analysis_file = self.config.ANALYSIS_DIR / f"{match_id}_{timestamp}.json"
            
            full_record = {
                "match_id": match_id,
                "timestamp": timestamp,
                "extracted_data": extracted_data,
                "yudor_analysis": analysis
            }
            
            with open(analysis_file, "w", encoding="utf-8") as f:
                json.dump(full_record, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Analysis saved to: {analysis_file}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            sys.exit(1)
    
    # =========================
    # HELPER: CORRECT FAIR ODDS CALCULATION
    # =========================

    def calculate_fair_odds_at_line(self, pr_casa_pct: float, pr_vis_pct: float, ah_line: float) -> float:
        """
        Calculate Fair Odds at a specific AH line using CORRECT YUDOR methodology

        Args:
            pr_casa_pct: Home probability as PERCENTAGE (36.2, not 0.362)
            pr_vis_pct: Away probability as PERCENTAGE (33.5, not 0.335)
            ah_line: Asian Handicap line (-0.25, 0.0, +1.0, etc.)

        Returns:
            Fair odds at that line (e.g., 2.35)

        Methodology:
            1. Moneyline (at -0.5) = 100 / favorite_percentage
            2. For each +0.25 step: multiply by 0.85 (easier to cover)
            3. For each -0.25 step: multiply by 1.15 (harder to cover)

        Example:
            pr_casa_pct=36.2, pr_vis_pct=33.5, ah_line=-0.25
            → Favorite: 36.2%
            → Moneyline: 100/36.2 = 2.76 (at line -0.5)
            → Steps from -0.5 to -0.25: +1 step
            → Odds: 2.76 × 0.85 = 2.35
        """
        # Determine favorite
        fav_prob_pct = max(pr_casa_pct, pr_vis_pct)

        # Moneyline odds (at line -0.5 for favorite)
        odd_ml = 100 / fav_prob_pct

        # Calculate steps from -0.5 to ah_line
        steps = (ah_line + 0.5) / 0.25

        # Apply multipliers
        if steps > 0:
            # Positive steps: easier to cover → lower odds
            odds = odd_ml * (0.85 ** steps)
        elif steps < 0:
            # Negative steps: harder to cover → higher odds
            odds = odd_ml * (1.15 ** abs(steps))
        else:
            # Exactly at -0.5
            odds = odd_ml

        return round(odds, 2)

    # =========================
    # STAGE 4: AIRTABLE SYNC
    # =========================

    def save_to_airtable(self, match_id: str, match_info: Dict, analysis: Dict):
        """
        Save analysis to Airtable
        
        Args:
            match_id: Match identifier
            match_info: Basic match information
            analysis: Yudor analysis results
        """
        if not self.airtable:
            print("⚠️  Airtable not configured - skipping sync")
            return
        
        print("\n" + "="*80)
        print("💾 STAGE 4: SAVING TO AIRTABLE")
        print("="*80)
        
        try:
            table = self.base.table(AirtableSchema.TABLES["analyses"])
            
            # Check if record exists
            existing = table.all(formula=f"{{match_id}}='{match_id}'")
            
            # Convert date from DD/MM/YYYY to YYYY-MM-DD for Airtable
            match_date_str = match_info.get("date", "")
            try:
                from datetime import datetime as dt
                date_obj = dt.strptime(match_date_str, "%d/%m/%Y")
                match_date_formatted = date_obj.strftime("%Y-%m-%d")
            except:
                match_date_formatted = match_date_str  # Fallback to original if parsing fails

            # Determine which team to bet on based on AH line
            ah_fair = analysis.get("yudor_ah_fair", analysis.get("yudor_fair_ah", 0))
            home_team = match_info.get("home", "")
            away_team = match_info.get("away", "")

            # Determine yudor_ah_team based on line and favorite_side
            yudor_ah_team = analysis.get("yudor_ah_team", "")
            if not yudor_ah_team:
                # Fallback logic if not explicitly provided
                favorite_side = analysis.get("favorite_side", "")
                if favorite_side == "HOME":
                    yudor_ah_team = home_team
                elif favorite_side == "AWAY":
                    yudor_ah_team = away_team
                elif ah_fair < 0:
                    # Negative line typically means home is favorite
                    yudor_ah_team = home_team
                else:
                    # Positive line typically means away is favorite
                    yudor_ah_team = away_team

            # Calculate Yudor Fair Odds using CORRECT methodology
            yudor_fair_odds = analysis.get("yudor_fair_odds", 0)
            if not yudor_fair_odds and ah_fair != 0:
                # Get probabilities from analysis
                pr_casa = analysis.get("pr_casa", 0)
                pr_vis = analysis.get("pr_vis", 0)
                pr_empate = analysis.get("pr_empate", 0)

                if pr_casa and pr_vis and pr_empate:
                    # Detect format: decimal (sum ≈ 1.0) or percentage (sum ≈ 100)
                    prob_sum = pr_casa + pr_vis + pr_empate

                    if prob_sum > 10:
                        # Already percentages
                        pr_casa_pct = pr_casa
                        pr_vis_pct = pr_vis
                    else:
                        # Convert decimals to percentages
                        pr_casa_pct = pr_casa * 100
                        pr_vis_pct = pr_vis * 100

                    # Use CORRECT calculation
                    yudor_fair_odds = self.calculate_fair_odds_at_line(pr_casa_pct, pr_vis_pct, ah_fair)
                else:
                    # Fallback to approximation if probabilities missing
                    yudor_fair_odds = 2.0 - (ah_fair * 0.4)
                    yudor_fair_odds = round(max(1.01, min(yudor_fair_odds, 10.0)), 2)

            # Extract Q1-Q19 scores from consolidated_data
            q1_q19_scores = ""
            if "consolidated_data" in analysis:
                consolidated = analysis["consolidated_data"]
                if "q_scores" in consolidated:
                    q_scores = consolidated["q_scores"]
                    # Create readable summary
                    q_lines = []
                    for q_id, q_data in sorted(q_scores.items()):
                        home = q_data.get("home_score", 0)
                        away = q_data.get("away_score", 0)
                        q_lines.append(f"{q_id}: {home} vs {away}")
                    q1_q19_scores = "\n".join(q_lines)
                elif isinstance(consolidated, dict):
                    # Try alternative structure
                    q_lines = []
                    for i in range(1, 20):
                        q_key = f"Q{i}"
                        if q_key in consolidated:
                            q_data = consolidated[q_key]
                            if isinstance(q_data, dict):
                                home = q_data.get("home_score", 0)
                                away = q_data.get("away_score", 0)
                                q_lines.append(f"{q_key}: {home} vs {away}")
                    if q_lines:
                        q1_q19_scores = "\n".join(q_lines)

            # If still empty, try to extract from Full Analysis JSON
            if not q1_q19_scores and "q_scores" in analysis:
                q_scores = analysis["q_scores"]
                q_lines = []
                for q_id, q_data in sorted(q_scores.items()):
                    if isinstance(q_data, dict):
                        home = q_data.get("home_score", 0)
                        away = q_data.get("away_score", 0)
                        q_lines.append(f"{q_id}: {home} vs {away}")
                q1_q19_scores = "\n".join(q_lines) if q_lines else "Q scores not available"

            if not q1_q19_scores:
                q1_q19_scores = "Q1-Q19 scores not found in analysis"

            record_data = {
                "match_id": match_id,
                "match_date": match_date_formatted,  # YYYY-MM-DD format
                "Home Team": home_team,  # Title Case with spaces
                "Away Team": away_team,
                "League": match_info.get("league", ""),
                "Analysis Timestamp": datetime.now().strftime("%Y-%m-%d"),  # NEW: When analysis was done
                "Yudor AH Fair": ah_fair,
                "Yudor AH Team": yudor_ah_team,  # NEW: Which team to bet on
                "Yudor Fair Odds": yudor_fair_odds,  # NEW: Fair odds calculation
                "Yudor Decision": analysis.get("decision", ""),
                "CS Final": analysis.get("cs_final", 0),
                "R Score": analysis.get("r_score", 0),
                "Tier": analysis.get("tier", 0),
                "Data Quality": analysis.get("confidence", 0),
                "Q1-Q19 Scores": q1_q19_scores,  # NEW: Q1-Q19 summary
                "Full Analysis": json.dumps(analysis, indent=2),
                "Status": "ANALYZED"
            }
            
            if existing:
                # Update existing record
                table.update(existing[0]['id'], record_data)
                print("✅ Updated existing Airtable record")
            else:
                # Create new record
                table.create(record_data)
                print("✅ Created new Airtable record")
                
        except Exception as e:
            print(f"⚠️  Airtable sync failed: {e}")

    # =========================
    # COMMAND 2: ANALYZE-BATCH
    # =========================

    def analyze_batch(self, input_file: Optional[str] = None):
        """
        Batch analysis with v5.3 prompts

        Process:
        1. Read matches_priority.txt (15-20 games)
        2. For each game:
           a. Load scraped data from match_data_v29.json
           b. Run DATA_CONSOLIDATION_PROMPT (full mode with Q1-Q19)
           c. Run YUDOR_MASTER_PROMPT_v5.3 (3-layer analysis)
           d. Save consolidated data to consolidated_data/
           e. Save analysis to analysis_history/
           f. Save to Airtable

        Args:
            input_file: Path to priority matches file (default: matches_priority.txt)
        """
        print("\n" + "="*80)
        print("🎯 COMMAND: ANALYZE-BATCH (v5.3)")
        print("="*80)

        # Load input file
        if input_file is None:
            input_file = self.config.MATCHES_PRIORITY_FILE

        if not Path(input_file).exists():
            print(f"❌ Input file not found: {input_file}")
            print(f"💡 Run pre-filter first:")
            print(f"   python scripts/master_orchestrator.py pre-filter")
            sys.exit(1)

        # Read priority matches
        with open(input_file, encoding="utf-8") as f:
            matches = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        print(f"📋 Loaded {len(matches)} priority matches")

        # Load scraped data
        scraped_data_file = self.config.BASE_DIR / "match_data_v29.json"
        if not scraped_data_file.exists():
            print(f"❌ Scraped data not found: {scraped_data_file}")
            print(f"💡 Run pre-filter first to generate scraped data")
            sys.exit(1)

        with open(scraped_data_file, encoding="utf-8") as f:
            scraped_data = json.load(f)

        # Load prompts
        print("\n📚 Loading v5.3 prompts...")
        data_consolidation_prompt = self.load_prompt("DATA_CONSOLIDATION_PROMPT_v1.0.md")
        yudor_master_prompt = self.load_prompt("YUDOR_MASTER_PROMPT_v5.3.md")

        # Process each match
        results_summary = []

        for idx, match in enumerate(matches, 1):
            print("\n" + "="*80)
            print(f"[{idx}/{len(matches)}] ANALYZING: {match}")
            print("="*80)

            # Parse match string
            parts = match.split("#")[0].strip().split(",")
            if len(parts) < 3:
                print(f"⚠️  Invalid format, skipping: {match}")
                continue

            teams = parts[0].strip()
            league = parts[1].strip()
            date_str = parts[2].strip()

            # Generate match_id
            home_away = teams.replace(" vs ", "vs").replace(" ", "")
            date_clean = date_str.replace("/", "")
            match_id = f"{home_away}_{date_clean}"

            # Find match in scraped data
            match_data = None
            for scraped_id, scraped_match in scraped_data.items():
                if scraped_id.lower().startswith(home_away.lower()[:10]):
                    match_data = scraped_match
                    match_id = scraped_id
                    break

            if not match_data:
                print(f"⚠️  Match not found in scraped data: {match_id}")
                continue

            match_info = match_data.get("match_info", {})

            try:
                # STAGE 0: Fetch URL Content + FootyStats Data
                print("\n" + "-"*80)
                print("🌐 STAGE 0: FETCHING DATA (URLs + FootyStats API)")
                print("-"*80)

                # Fetch URL content (SportsMole, Transfermarkt, etc.)
                fetched_content = self.fetch_all_match_content(match_data)

                # Build content summary for prompt
                content_sections = []
                for source_key, source_data in fetched_content.items():
                    content_sections.append(f"""
=== {source_data['description']} ===
URL: {source_data['url']}
CONTENT:
{source_data['content']}
""")

                fetched_text = "\n".join(content_sections) if content_sections else "[No content fetched from URLs]"

                print(f"   ✅ Fetched content from {len(fetched_content)} URL sources")

                # Fetch FootyStats API data
                footystats_data = self.fetch_all_footystats_data(match_info)

                # Format FootyStats data for prompt
                footystats_text = ""
                if footystats_data.get("match_data"):
                    footystats_text += f"""
=== FootyStats Match Data ===
{json.dumps(footystats_data['match_data'], indent=2)}
"""
                if footystats_data.get("home_team_data"):
                    footystats_text += f"""
=== FootyStats Home Team ({match_info.get('home')}) ===
{json.dumps(footystats_data['home_team_data'], indent=2)}
"""
                if footystats_data.get("away_team_data"):
                    footystats_text += f"""
=== FootyStats Away Team ({match_info.get('away')}) ===
{json.dumps(footystats_data['away_team_data'], indent=2)}
"""

                if not footystats_text:
                    footystats_text = "[FootyStats data not available for this match]"
                else:
                    print(f"   ✅ FootyStats API data fetched")

                # STAGE 1: Data Consolidation
                print("\n" + "-"*80)
                print("📊 STAGE 1: DATA CONSOLIDATION")
                print("-"*80)

                user_message_consolidation = f"""
Extract and consolidate data for this match using the full v5.3 rubric.

MATCH INFO:
{json.dumps(match_info, indent=2)}

NEWS HEADLINES:
{json.dumps(match_data.get('news', {}), indent=2)}

FETCHED PAGE CONTENT (SportsMole, Transfermarkt, etc.):
{fetched_text}

FOOTYSTATS API DATA (xG, form, goals, positions):
{footystats_text}

INSTRUCTIONS:
1. EXTRACT REAL DATA from the sources above:
   - xG data from FootyStats (home_xg_avg, away_xg_avg, home_goals_scored_avg, etc.)
   - Form from FootyStats (home_ppg, away_ppg, wins/draws/losses, position)
   - Team news/injuries from SportsMole
   - Squad values from Transfermarkt
   - Tactical info from news headlines
2. Fill Q1-Q19 scores deterministically using ANEXO I criteria
3. Calculate data quality score based on ACTUAL data found
4. Document sources for each Q-score
5. Output complete JSON with:
   - q_scores (Q1-Q19 with home_score, away_score, reasoning, sources)
   - category_totals (Technique, Tactics, Motivation, Form, Performance, Injuries, Home/Away)
   - raw_scores (raw_casa, raw_vis)
   - data_quality
   - notes

DATA PRIORITY:
1. FootyStats API → xG, goals/game, form, table position (MOST RELIABLE)
2. SportsMole → Team news, injuries, preview context
3. Transfermarkt → Squad values
4. News Headlines → Derby context, motivation

IMPORTANT:
- Use ACTUAL DATA from the fetched content and FootyStats API
- Do NOT include Betfair odds - we use BLIND PRICING
- Be deterministic and reference ANEXO I for scoring rules
"""

                print("🤖 Calling Claude for data consolidation...")
                consolidation_response = self.call_claude(
                    data_consolidation_prompt,
                    user_message_consolidation,
                    max_tokens=8000
                )

                consolidated_data = self.extract_json_from_response(consolidation_response)

                # Save consolidated data
                consolidated_file = self.config.CONSOLIDATED_DIR / f"{match_id}_consolidated.json"
                with open(consolidated_file, "w", encoding="utf-8") as f:
                    json.dump(consolidated_data, f, indent=2, ensure_ascii=False)

                print(f"✅ Data consolidated and saved to: {consolidated_file}")

                # STAGE 2: Yudor v5.3 Analysis
                print("\n" + "-"*80)
                print("🎯 STAGE 2: YUDOR v5.3 ANALYSIS (3 Layers)")
                print("-"*80)

                user_message_yudor = f"""
Run complete Yudor v5.3 analysis on this consolidated data.

CONSOLIDATED DATA:
{json.dumps(consolidated_data, indent=2)}

EXECUTE THESE LAYERS IN ORDER:

LAYER 1: BLIND PRICING (CORRECT YUDOR METHODOLOGY)
- Sum Raw_Casa from all home Q-scores
- Sum Raw_Vis from all away Q-scores
- Get P(Empate) from consolidated data (derived from odds, NOT modified)

STEP 1: Normalize if sum > 100
  * Soma = Raw_Casa + Raw_Vis + P(Empate)
  * IF Soma > 100:
    - Surplus = (Soma - 100) / 2
    - Adjusted_Casa = Raw_Casa - Surplus
    - Adjusted_Vis = Raw_Vis - Surplus
    - P(Empate) STAYS UNCHANGED
  * ELSE:
    - Adjusted_Casa = Raw_Casa
    - Adjusted_Vis = Raw_Vis

STEP 2: Identify favorite and calculate Moneyline odds
  * Favorite_Pct = max(Adjusted_Casa, Adjusted_Vis)
  * Underdog_Pct = min(Adjusted_Casa, Adjusted_Vis)
  * Odd_ML = 100 / Favorite_Pct
  * This Odd_ML = -0.5 AH for the favorite

STEP 3: Calculate +0.5 AH reference point
  * Odds_Plus05 = 100 / (Favorite_Pct + P_Empate)

STEP 4: Iterate to find AH line with odds ~2.0 [1.97, 2.03]
  * Start at -0.5 AH with Odd_ML
  * For each -0.25 step (more negative): odds *= 1.15
  * For each +0.25 step (more positive): odds *= 0.85
  * Stop when odds reach [1.97, 2.03] range
  * Max 20 iterations

STEP 5: Return Fair AH Line
  * If home is favorite: line is negative (e.g., -1.25)
  * If away is favorite: line is positive for home (e.g., +0.75)
  * Include Delta = Raw_Casa - Raw_Vis for reference

LAYER 2: CONFIDENCE (CS_final)
- BSD = |Delta| / max(Raw_Casa, Raw_Vis) * 100
- CCS = consistency of category scores
- CS_final = (BSD * 0.6 + CCS * 0.4)
- Tier: 1 if CS≥70, 2 if CS≥50, 3 otherwise

LAYER 3: RG GUARD
- Calculate R-Score from risk signals
- Decision: VETO/FLIP/EXP/CORE based on R-Score and Tier

OUTPUT ONLY VALID JSON (no markdown, no explanation text):
```json
{{
  "match_id": "{consolidated_data.get('game_id', 'unknown')}",
  "raw_casa": <number>,
  "raw_vis": <number>,
  "delta": <number>,
  "yudor_ah_fair": <number like -0.5 or +1.0>,
  "pr_casa": <decimal>,
  "pr_vis": <decimal>,
  "pr_empate": 0.25,
  "cs_final": <0-100>,
  "tier": <1, 2, or 3>,
  "r_home": <0.0-1.0>,
  "r_away": <0.0-1.0>,
  "r_fav": <0.0-1.0>,
  "r_dog": <0.0-1.0>,
  "rbr": <-1.0 to +1.0>,
  "r_score": <0.0-1.0>,
  "edge_synthetic": <calculated as (|AH_Line| / 0.25) × 8, used for FLIP evaluation>,
  "decision": "CORE" or "EXP" or "FLIP" or "VETO",
  "reasoning": "<brief explanation>"
}}
```

CRITICAL: Return ONLY the JSON object, no other text.
"""

                print("🤖 Calling Claude for v5.3 analysis...")
                yudor_response = self.call_claude(
                    yudor_master_prompt,
                    user_message_yudor,
                    max_tokens=8000
                )

                # Debug: save raw response if parsing fails
                try:
                    yudor_analysis = self.extract_json_from_response(yudor_response)
                except json.JSONDecodeError as e:
                    # Save raw response for debugging
                    debug_file = self.config.ANALYSIS_DIR / f"{match_id}_yudor_raw.txt"
                    with open(debug_file, "w", encoding="utf-8") as f:
                        f.write(yudor_response)
                    print(f"⚠️  JSON parse error. Raw response saved to: {debug_file}")
                    print(f"   Response length: {len(yudor_response)} chars")
                    print(f"   Response preview: {yudor_response[:500]}...")
                    raise e

                # Combine results
                full_analysis = {
                    "match_id": match_id,
                    "match_info": match_info,
                    "timestamp": datetime.now().isoformat(),
                    "consolidated_data": consolidated_data,
                    "yudor_analysis": yudor_analysis
                }

                # Save analysis
                analysis_file = self.config.ANALYSIS_DIR / f"{match_id}_analysis.json"
                with open(analysis_file, "w", encoding="utf-8") as f:
                    json.dump(full_analysis, f, indent=2, ensure_ascii=False)

                print(f"✅ Analysis complete and saved to: {analysis_file}")

                # Display results
                print(f"\n📊 RESULTS:")
                print(f"   Fair AH Line: {yudor_analysis.get('yudor_ah_fair', 'N/A')}")
                print(f"   Fair Odds: {yudor_analysis.get('yudor_ah_odds', 'N/A')}")
                print(f"   Decision: {yudor_analysis.get('decision', 'N/A')}")
                print(f"   CS_final: {yudor_analysis.get('cs_final', 0)}")
                print(f"   R-Score: {yudor_analysis.get('r_score', 0)}")
                print(f"   Tier: {yudor_analysis.get('tier', 0)}")

                # STAGE 3: Save to Airtable
                print("\n" + "-"*80)
                print("💾 STAGE 3: SAVING TO AIRTABLE")
                print("-"*80)

                self.save_to_airtable(match_id, match_info, yudor_analysis)

                results_summary.append({
                    "match": match,
                    "match_id": match_id,
                    "status": "SUCCESS",
                    "decision": yudor_analysis.get('decision', 'N/A'),
                    "fair_line": yudor_analysis.get('yudor_ah_fair', 'N/A'),
                    "cs_final": yudor_analysis.get('cs_final', 0),
                    "r_score": yudor_analysis.get('r_score', 0)
                })

            except Exception as e:
                print(f"\n❌ Analysis failed: {e}")
                results_summary.append({
                    "match": match,
                    "match_id": match_id,
                    "status": "FAILED",
                    "error": str(e)
                })

        # Final Summary
        print("\n" + "="*80)
        print("✅ BATCH ANALYSIS COMPLETE")
        print("="*80)

        successful = [r for r in results_summary if r["status"] == "SUCCESS"]
        failed = [r for r in results_summary if r["status"] == "FAILED"]

        print(f"\n📊 SUMMARY:")
        print(f"   Total matches: {len(matches)}")
        print(f"   Successful: {len(successful)}")
        print(f"   Failed: {len(failed)}")

        if successful:
            print(f"\n✅ SUCCESSFUL ANALYSES:")
            for result in successful:
                print(f"   - {result['match']}")
                print(f"     Decision: {result['decision']}, Fair Line: {result['fair_line']}, "
                      f"CS: {result['cs_final']}, R: {result['r_score']:.2f}")

        if failed:
            print(f"\n❌ FAILED ANALYSES:")
            for result in failed:
                print(f"   - {result['match']}: {result.get('error', 'Unknown error')}")

        print(f"\n📁 All analyses saved in:")
        print(f"   - Consolidated data: {self.config.CONSOLIDATED_DIR}")
        print(f"   - Analyses: {self.config.ANALYSIS_DIR}")
        print(f"   - Airtable: Match Analyses table")

        print(f"\n📝 Next steps:")
        print(f"   1. Check Betfair for market odds")
        print(f"   2. Calculate edge% for each match")
        print(f"   3. Enter bets with ≥8% edge")

    # =========================
    # INTERACTIVE EDGE CALCULATION (OLD CODE)
    # =========================
    
    def calculate_edge_interactive(self, analysis: Dict):
        """
        Interactive session to calculate edge vs market
        
        Args:
            analysis: Yudor analysis with fair line
        """
        print("\n" + "="*80)
        print("📊 EDGE CALCULATION (Manual)")
        print("="*80)
        
        fair_line = analysis.get("yudor_fair_ah", 0)
        fair_odds = analysis.get("yudor_fair_ah_odds", 2.0)
        
        print(f"\n🎯 Yudor's Fair Line: {fair_line}")
        print(f"💰 Fair Odds: {fair_odds}")
        print(f"📈 Decision: {analysis.get('decision', 'N/A')}")
        print(f"✅ Confidence: {analysis.get('confidence', 0)}%")
        
        print("\n" + "-"*80)
        print("Now check Betfair/market for actual lines:")
        print("-"*80)
        
        # Get market line from user
        market_line = input("\nWhat's the market AH line? (e.g., -1.0): ").strip()
        market_odds = input("What are the odds? (e.g., 1.95): ").strip()
        
        try:
            market_line = float(market_line)
            market_odds = float(market_odds)
            
            # Calculate edge
            # If market line is MORE favorable than fair line = POSITIVE edge
            line_difference = fair_line - market_line
            
            # Simple edge calculation (can be more sophisticated)
            if abs(line_difference) >= 0.25:
                edge_pct = abs(line_difference) * 10  # Rough estimate
            else:
                edge_pct = 0
            
            print(f"\n📊 EDGE ANALYSIS:")
            print(f"   Fair Line: {fair_line}")
            print(f"   Market Line: {market_line}")
            print(f"   Difference: {line_difference:+.2f}")
            print(f"   Estimated Edge: {edge_pct:.1f}%")
            
            if edge_pct >= 8:
                print(f"\n✅ POSITIVE EDGE (≥8%) - Consider betting!")
            elif edge_pct >= 5:
                print(f"\n⚠️  MARGINAL EDGE (5-8%) - Be cautious")
            else:
                print(f"\n❌ NO EDGE (<5%) - Skip this bet")
            
            # Ask if entering bet
            enter = input("\nEnter this bet? (y/n): ").strip().lower()
            
            if enter == 'y':
                stake = input("Stake amount: ").strip()
                return {
                    "entered": True,
                    "market_line": market_line,
                    "market_odds": market_odds,
                    "edge_pct": edge_pct,
                    "stake": float(stake) if stake else 0
                }
            else:
                reason = input("Why not entering? (optional): ").strip()
                return {
                    "entered": False,
                    "reason": reason,
                    "edge_pct": edge_pct
                }
                
        except ValueError:
            print("❌ Invalid input")
            return None
    
    # =========================
    # COMPLETE WORKFLOW
    # =========================

    def analyze_complete_integrated(self, match_string: str):
        """
        NEW Complete workflow with FBref integration:
        - Integrated scraper (FootyStats + FBref + Formations)
        - Claude analysis with .claude/analysis_prompt.md
        - Save to Airtable

        Args:
            match_string: Match like "Barcelona vs Athletic Club, La Liga, 22/11/2025"
        """
        print("\n" + "="*80)
        print("🎯 YUDOR COMPLETE ANALYSIS WORKFLOW (FBref Integrated)")
        print("="*80)
        print(f"\nMatch: {match_string}\n")

        # Stage 1: Integrated scraping
        integrated_data = self.run_integrated_scraper(match_string)

        if not integrated_data:
            print("⚠️  Integrated scraper failed, falling back to old workflow")
            return self.analyze_complete(match_string)

        # Check data quality
        data_quality = integrated_data.get("data_quality", {}).get("overall_score", 0)
        print(f"\n📊 Data Quality: {data_quality}/5.0")

        if data_quality < 3.0:
            print("⚠️  Data quality too low, consider skipping this match")
            proceed = input("Continue anyway? (y/n): ").strip().lower()
            if proceed != 'y':
                print("❌ Skipping match due to low data quality")
                return

        # Get match info for Airtable
        match_id = integrated_data["match_id"]
        match_info = {
            "home_team": integrated_data["home_team"],
            "away_team": integrated_data["away_team"],
            "league": integrated_data["league"],
            "date": integrated_data["date"]
        }

        # Stage 2: Analysis with FBref data (no separate extraction needed)
        analysis = self.analyze_match(integrated_data, match_id, use_integrated=True)

        # Stage 3: Save to Airtable
        self.save_to_airtable(match_id, match_info, analysis)

        # Stage 4: Interactive edge calculation
        bet_decision = self.calculate_edge_interactive(analysis)

        # Save bet decision if entered
        if bet_decision and bet_decision.get("entered") and self.airtable:
            try:
                bets_table = self.base.table(AirtableSchema.TABLES["bets"])
                bets_table.create({
                    "match_id": match_id,
                    "entry_timestamp": datetime.now().isoformat(),
                    "market_ah_line": bet_decision["market_line"],
                    "market_ah_odds": bet_decision["market_odds"],
                    "edge_pct": bet_decision["edge_pct"],
                    "stake": bet_decision.get("stake", 0),
                    "notes": bet_decision.get("notes", "")
                })
                print("\n✅ Bet tracked in Airtable")
            except Exception as e:
                print(f"\n⚠️  Could not save bet to Airtable: {e}")

        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETE (FBref Integrated)")
        print("="*80)

    def analyze_complete(self, match_string: str):
        """
        OLD Complete workflow: scrape → extract → analyze → save

        Args:
            match_string: Match like "Flamengo vs Bragantino, Brasileirão, 25/11/2025, 19:00"
        """
        print("\n" + "="*80)
        print("🎯 YUDOR COMPLETE ANALYSIS WORKFLOW (OLD)")
        print("="*80)
        print(f"\nMatch: {match_string}\n")

        # Generate match ID
        parts = match_string.split(",")
        teams = parts[0].strip().replace(" vs ", "vs").replace(" ", "")
        date = parts[2].strip().replace("/", "")
        match_id = f"{teams}_{date}"

        # Stage 1: Scrape URLs
        urls_json = self.run_scraper(match_string)

        # Load match info
        with open(urls_json) as f:
            urls_data = json.load(f)

        # Get the match data (there should be one match)
        match_data = next(iter(urls_data.values()))
        match_info = match_data["match_info"]

        # Stage 2: Extract data
        extracted_data = self.extract_data(urls_json)

        # Stage 3: Yudor analysis (blind pricing)
        analysis = self.analyze_match(extracted_data, match_id, use_integrated=False)

        # Stage 4: Save to Airtable
        self.save_to_airtable(match_id, match_info, analysis)
        
        # Stage 5: Interactive edge calculation
        bet_decision = self.calculate_edge_interactive(analysis)
        
        # Save bet decision if entered
        if bet_decision and bet_decision.get("entered") and self.airtable:
            try:
                bets_table = self.base.table(AirtableSchema.TABLES["bets"])
                bets_table.create({
                    "match_id": match_id,
                    "entry_timestamp": datetime.now().isoformat(),
                    "market_ah_line": bet_decision["market_line"],
                    "market_ah_odds": bet_decision["market_odds"],
                    "edge_pct": bet_decision["edge_pct"],
                    "stake": bet_decision.get("stake", 0)
                })
                print("\n✅ Bet recorded in Airtable")
            except Exception as e:
                print(f"\n⚠️  Failed to save bet: {e}")
        
        print("\n" + "="*80)
        print("✅ WORKFLOW COMPLETE")
        print("="*80)
        print(f"\n📁 Analysis saved in: {self.config.ANALYSIS_DIR}")
        print(f"💾 Airtable updated")
        print(f"\nNext: Track results after the match!")

    # =========================
    # COMMAND 3: LOSS-ANALYSIS
    # =========================

    def loss_analysis(self, auto: bool = False, match_id: Optional[str] = None):
        """
        Post-match loss analysis using LOSS_LEDGER_ANALYSIS_PROMPT

        Process:
        1. Query Airtable Results table for losses without analysis (auto mode)
           OR analyze specific match_id (manual mode)
        2. For each loss:
           a. Load original analysis from analysis_history/
           b. Gather post-match data
           c. Run LOSS_LEDGER_ANALYSIS_PROMPT for root cause analysis
           d. Classify error type (Model Error, Data Error, Variance)
           e. Identify failed Q-IDs
           f. Save to loss_ledger/
           g. Update Airtable Results with error classification

        Args:
            auto: If True, automatically find losses from Airtable
            match_id: Specific match_id to analyze (manual mode)
        """
        print("\n" + "="*80)
        print("🎯 COMMAND: LOSS-ANALYSIS")
        print("="*80)

        # Load LOSS_LEDGER prompt
        loss_ledger_prompt = self.load_prompt("LOSS_LEDGER_ANALYSIS_PROMPT_v1.0.md")

        losses_to_analyze = []

        if auto:
            # Query Airtable for losses without analysis
            if not self.airtable:
                print("❌ Airtable not configured. Cannot use auto mode.")
                print("💡 Use manual mode: --match-id MATCH_ID")
                sys.exit(1)

            print("🔍 Querying Airtable for unanalyzed losses...")

            try:
                results_table = self.base.table(AirtableSchema.TABLES["results"])
                # Get all losses without error_category
                losses = results_table.all(formula="AND({ah_result}='LOSS', {error_category}='')")

                for loss_record in losses:
                    fields = loss_record['fields']
                    losses_to_analyze.append({
                        "airtable_id": loss_record['id'],
                        "match_id": fields.get('match_id', ''),
                        "final_score": fields.get('final_score', ''),
                        "profit_loss": fields.get('profit_loss', 0),
                        "notes": fields.get('notes', '')
                    })

                print(f"✅ Found {len(losses_to_analyze)} unanalyzed losses")

            except Exception as e:
                print(f"❌ Failed to query Airtable: {e}")
                sys.exit(1)

        else:
            # Manual mode - analyze specific match
            if not match_id:
                print("❌ No match_id provided")
                print("💡 Usage: python scripts/master_orchestrator.py loss-analysis --match-id MATCH_ID")
                sys.exit(1)

            # Prompt user for result info
            print(f"\nAnalyzing loss for: {match_id}")
            final_score = input("Final score (e.g., '1-2'): ").strip()
            notes = input("Additional notes (optional): ").strip()

            losses_to_analyze.append({
                "match_id": match_id,
                "final_score": final_score,
                "notes": notes
            })

        if not losses_to_analyze:
            print("✅ No losses to analyze")
            return

        # Analyze each loss
        for idx, loss in enumerate(losses_to_analyze, 1):
            print("\n" + "="*80)
            print(f"[{idx}/{len(losses_to_analyze)}] ANALYZING LOSS: {loss['match_id']}")
            print("="*80)

            match_id = loss['match_id']

            # Load original analysis
            analysis_file = self.config.ANALYSIS_DIR / f"{match_id}_analysis.json"

            if not analysis_file.exists():
                print(f"⚠️  Original analysis not found: {analysis_file}")
                print("   Skipping...")
                continue

            with open(analysis_file, encoding="utf-8") as f:
                original_analysis = json.load(f)

            print(f"✅ Loaded original analysis")

            # Extract key info
            yudor_analysis = original_analysis.get("yudor_analysis", {})
            consolidated_data = original_analysis.get("consolidated_data", {})

            print(f"\n📊 ORIGINAL PREDICTION:")
            print(f"   Decision: {yudor_analysis.get('decision', 'N/A')}")
            print(f"   Fair Line: {yudor_analysis.get('yudor_ah_fair', 'N/A')}")
            print(f"   CS_final: {yudor_analysis.get('cs_final', 0)}")
            print(f"   R-Score: {yudor_analysis.get('r_score', 0)}")

            print(f"\n📉 ACTUAL RESULT:")
            print(f"   Score: {loss.get('final_score', 'Unknown')}")
            print(f"   Outcome: LOSS")

            # Run loss analysis
            print("\n" + "-"*80)
            print("🔍 RUNNING ROOT CAUSE ANALYSIS")
            print("-"*80)

            user_message = f"""
Perform root cause analysis for this losing bet.

ORIGINAL ANALYSIS:
{json.dumps(original_analysis, indent=2)}

ACTUAL RESULT:
- Final Score: {loss.get('final_score', 'Unknown')}
- Outcome: LOSS
- Notes: {loss.get('notes', 'None')}

INSTRUCTIONS:
1. Retrieve original Q1-Q19 scores and predictions
2. Compare predictions vs actual match outcome
3. Identify which Q-IDs failed (where prediction was wrong)
4. Classify error type:
   - Model Error: Q-ID weight/criteria is wrong
   - Data Error: Scraped data was incorrect/incomplete
   - Variance: Correct prediction, unlucky outcome (e.g., high xG but lost)
5. Provide recommendations for improvement

Output complete JSON with:
- failed_q_ids: List of Q-IDs that failed with explanations
- error_type: "Model Error" | "Data Error" | "Variance"
- error_category: Brief description (e.g., "Q6: Tactics - Formation matchup failed")
- recommendations: Specific suggestions for system improvement
- root_cause_summary: Concise explanation of why bet lost
"""

            try:
                print("🤖 Calling Claude for loss analysis...")
                loss_response = self.call_claude(
                    loss_ledger_prompt,
                    user_message,
                    max_tokens=8000
                )

                loss_analysis_result = self.extract_json_from_response(loss_response)

                # Save to loss_ledger
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                loss_file = self.config.LOSS_LEDGER_DIR / f"{match_id}_loss_{timestamp}.json"

                loss_record = {
                    "match_id": match_id,
                    "timestamp": datetime.now().isoformat(),
                    "final_score": loss.get('final_score', ''),
                    "original_analysis": original_analysis,
                    "loss_analysis": loss_analysis_result
                }

                with open(loss_file, "w", encoding="utf-8") as f:
                    json.dump(loss_record, f, indent=2, ensure_ascii=False)

                print(f"✅ Loss analysis saved to: {loss_file}")

                # Display results
                print(f"\n📊 ANALYSIS RESULTS:")
                print(f"   Error Type: {loss_analysis_result.get('error_type', 'Unknown')}")
                print(f"   Error Category: {loss_analysis_result.get('error_category', 'Unknown')}")
                print(f"   Failed Q-IDs: {', '.join([str(q) for q in loss_analysis_result.get('failed_q_ids', [])])}")
                print(f"\n   Root Cause: {loss_analysis_result.get('root_cause_summary', 'See JSON for details')}")

                # Update Airtable if in auto mode
                if auto and "airtable_id" in loss:
                    try:
                        results_table = self.base.table(AirtableSchema.TABLES["results"])
                        results_table.update(loss["airtable_id"], {
                            "error_category": loss_analysis_result.get('error_category', ''),
                            "error_type": loss_analysis_result.get('error_type', ''),
                            "notes": loss_analysis_result.get('root_cause_summary', '')
                        })
                        print("✅ Updated Airtable Results table")
                    except Exception as e:
                        print(f"⚠️  Failed to update Airtable: {e}")

            except Exception as e:
                print(f"❌ Loss analysis failed: {e}")

        # Summary
        print("\n" + "="*80)
        print("✅ LOSS ANALYSIS COMPLETE")
        print("="*80)
        print(f"\n📊 SUMMARY:")
        print(f"   Total losses analyzed: {len(losses_to_analyze)}")
        print(f"\n📁 Loss analyses saved in: {self.config.LOSS_LEDGER_DIR}")

        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Review loss patterns after 30 losses")
        print(f"   2. Run: python scripts/master_orchestrator.py audit --mode ml")
        print(f"   3. System will recommend weight adjustments")


# =========================
# CLI INTERFACE
# =========================

def main():
    """Main CLI interface"""

    if len(sys.argv) < 2:
        print("""
🎯 YUDOR MASTER ORCHESTRATOR v5.3 (FBref Integrated)

Usage:
  python master_orchestrator.py analyze-fbref "Barcelona vs Athletic Club, La Liga, 22/11/2025"
  python master_orchestrator.py analyze "Flamengo vs Bragantino, Brasileirão, 25/11/2025"
  python master_orchestrator.py pre-filter [--input matches_all.txt]
  python master_orchestrator.py analyze-batch [--input matches_priority.txt]
  python master_orchestrator.py loss-analysis --auto
  python master_orchestrator.py loss-analysis --match-id MATCH_ID

Commands:
  analyze-fbref "match"   - 🆕 Analyze with FBref integration (Q7, Q8, Q14 from real data)
  analyze "match"         - Analyze single match (old workflow)
  pre-filter              - Filter 30-40 games by data quality (creates matches_priority.txt)
  analyze-batch           - Run v5.3 analysis on priority games (full automation)
  loss-analysis --auto    - Analyze all unanalyzed losses from Airtable
  loss-analysis --match-id - Analyze specific loss manually

Options:
  --input FILE            - Specify input file (default: matches_all.txt or matches_priority.txt)
  --auto                  - Auto-detect losses from Airtable
  --match-id MATCH_ID     - Specify match ID for manual loss analysis

Examples:
  # 🆕 NEW WORKFLOW with FBref:
  python master_orchestrator.py analyze-fbref "Barcelona vs Athletic Club, La Liga, 22/11/2025"

  # Complete workflow for weekend betting:
  1. python master_orchestrator.py pre-filter
  2. python master_orchestrator.py analyze-batch
  3. (Check Betfair, enter bets, wait for results)
  4. python master_orchestrator.py loss-analysis --auto

  # Manual loss analysis:
  python master_orchestrator.py loss-analysis --match-id Mainz05vsHoffenheim_21112025
        """)
        sys.exit(1)

    command = sys.argv[1]
    orchestrator = YudorOrchestrator()

    # Parse arguments
    input_file = None
    auto = False
    match_id = None

    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg == "--input" and i + 1 < len(sys.argv):
            input_file = sys.argv[i + 1]
        elif arg == "--auto":
            auto = True
        elif arg == "--match-id" and i + 1 < len(sys.argv):
            match_id = sys.argv[i + 1]

    # Execute commands
    if command == "analyze-fbref":
        # NEW: Integrated workflow with FBref
        if len(sys.argv) < 3:
            print("❌ Usage: python master_orchestrator.py analyze-fbref \"match string\"")
            print("   Example: python master_orchestrator.py analyze-fbref \"Barcelona vs Athletic Club, La Liga, 22/11/2025\"")
            sys.exit(1)

        match_string = sys.argv[2]
        orchestrator.analyze_complete_integrated(match_string)

    elif command == "pre-filter":
        orchestrator.pre_filter(input_file=input_file)

    elif command == "analyze-batch":
        orchestrator.analyze_batch(input_file=input_file)

    elif command == "loss-analysis":
        orchestrator.loss_analysis(auto=auto, match_id=match_id)

    elif command == "analyze":
        # Legacy single match analysis
        if len(sys.argv) < 3:
            print("❌ Usage: python master_orchestrator.py analyze \"match string\"")
            sys.exit(1)

        match_string = sys.argv[2]
        orchestrator.analyze_complete(match_string)

    elif command == "batch":
        # Legacy batch command - redirect to analyze-batch
        print("💡 This command has been renamed to 'analyze-batch'")
        print("   Run: python master_orchestrator.py analyze-batch")

    elif command == "review":
        # TODO: Implement review
        print("🚧 Review mode - coming soon!")
        print("💡 For now, check files in analysis_history/ directory")

    elif command == "track":
        # TODO: Implement result tracking
        print("🚧 Track mode - coming soon!")
        print("💡 For now, update Airtable Results table manually")

    else:
        print(f"❌ Unknown command: {command}")
        print("💡 Run without arguments to see usage help")
        sys.exit(1)


if __name__ == "__main__":
    main()
