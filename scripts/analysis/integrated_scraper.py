#!/usr/bin/env python3
"""
Integrated Scraper for Yudor v5.3
Combines: URL scraping (FootyStats) + FBref statistics + Manual lineups

This is the SINGLE SOURCE OF TRUTH for all match data
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Import existing scrapers
from scraper import scrape_match_data  # FootyStats URL scraper

# Import FBref integration
try:
    from fbref_stats_integration import FBrefStatsIntegration, SOCCERDATA_AVAILABLE
except ImportError:
    SOCCERDATA_AVAILABLE = False
    print("⚠️  FBref integration not available")

# Import manual formation scraper
try:
    from formation_scraper import FormationScraper
except ImportError:
    FormationScraper = None
    print("⚠️  Formation scraper not available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegratedDataScraper:
    """
    Unified data scraper combining all sources:
    1. FootyStats (via URL scraping)
    2. FBref (via soccerdata library)
    3. Manual lineups (via formation database)

    Ensures consistent, complete data for all Q-scores
    """

    def __init__(self, league: str = 'La Liga', season: str = '2425'):
        """
        Initialize integrated scraper

        Args:
            league: League name
            season: Season code
        """
        self.league = league
        self.season = season

        # Initialize comprehensive stats scraper (FBref + SofaScore + FotMob)
        self.comprehensive_scraper = None
        if SOCCERDATA_AVAILABLE:
            try:
                from comprehensive_stats_scraper import ComprehensiveStatsScraper
                self.comprehensive_scraper = ComprehensiveStatsScraper(league=league, season=season)
                logger.info("✅ Comprehensive stats scraper initialized (FBref + SofaScore + FotMob)")
            except Exception as e:
                logger.warning(f"Comprehensive scraper initialization failed: {e}")
                # Fallback to basic FBref only
                try:
                    self.fbref = FBrefStatsIntegration(league=league, season=season)
                    logger.info("✅ FBref integration initialized (fallback)")
                except Exception as e2:
                    logger.warning(f"FBref initialization failed: {e2}")
                    self.fbref = None

        # Initialize formation scraper if available
        self.formation_scraper = None
        if FormationScraper:
            try:
                self.formation_scraper = FormationScraper()
                logger.info("✅ Formation scraper initialized")
            except Exception as e:
                logger.warning(f"Formation scraper initialization failed: {e}")

    def scrape_complete_match_data(
        self,
        match_id: str,
        home_team: str,
        away_team: str,
        league: str,
        date: str,
        footystats_url: str
    ) -> Dict:
        """
        Complete data scraping workflow for a match

        Args:
            match_id: Match identifier
            home_team: Home team name
            away_team: Away team name
            league: League name
            date: Match date (DD/MM/YYYY)
            footystats_url: FootyStats URL for match

        Returns:
            Complete structured data with all sources
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"INTEGRATED SCRAPING: {home_team} vs {away_team}")
        logger.info(f"{'='*80}\n")

        result = {
            "match_id": match_id,
            "home_team": home_team,
            "away_team": away_team,
            "league": league,
            "date": date,
            "extraction_timestamp": datetime.now().isoformat(),
            "data_sources": {},
            "data_quality": {},
            "q_score_inputs": {}
        }

        # Step 1: Scrape FootyStats (Primary source)
        logger.info("Step 1: Scraping FootyStats...")
        footystats_data = self._scrape_footystats(footystats_url, home_team, away_team)
        result["data_sources"]["footystats"] = footystats_data
        result["data_quality"]["footystats"] = self._assess_footystats_quality(footystats_data)

        # Step 2: Get FBref statistics
        logger.info("\nStep 2: Fetching FBref statistics...")
        fbref_data = self._get_fbref_data(home_team, away_team)
        result["data_sources"]["fbref"] = fbref_data
        result["data_quality"]["fbref"] = self._assess_fbref_quality(fbref_data)

        # Step 3: Get formations (manual or database)
        logger.info("\nStep 3: Getting formations...")
        formations = self._get_formations(match_id, home_team, away_team, league, date)
        result["data_sources"]["formations"] = formations
        result["data_quality"]["formations"] = 5 if formations['home_formation'] != '0' else 1

        # Step 4: Calculate overall data quality
        result["data_quality"]["overall_score"] = self._calculate_overall_quality(result["data_quality"])
        result["data_quality"]["proceed"] = result["data_quality"]["overall_score"] >= 3.0

        # Step 5: Prepare Q-score inputs
        logger.info("\nStep 4: Preparing Q-score inputs...")
        result["q_score_inputs"] = self._prepare_q_score_inputs(
            footystats_data,
            fbref_data,
            formations,
            home_team,
            away_team
        )

        logger.info(f"\n{'='*80}")
        logger.info(f"DATA QUALITY SCORE: {result['data_quality']['overall_score']:.1f}/5.0")
        logger.info(f"PROCEED WITH ANALYSIS: {result['data_quality']['proceed']}")
        logger.info(f"{'='*80}\n")

        return result

    def _scrape_footystats(self, url: str, home_team: str, away_team: str) -> Dict:
        """Scrape FootyStats data using existing scraper"""
        try:
            # Use existing scraper.py
            data = scrape_match_data(url, home_team, away_team)
            logger.info("✅ FootyStats data scraped")
            return data
        except Exception as e:
            logger.error(f"❌ FootyStats scraping failed: {e}")
            return {"error": str(e), "available": False}

    def _get_fbref_data(self, home_team: str, away_team: str) -> Dict:
        """Get comprehensive statistics for both teams (FBref + SofaScore + FotMob)"""

        # Try comprehensive scraper first (ALL sources)
        if self.comprehensive_scraper:
            logger.info("Using comprehensive scraper (FBref + SofaScore + FotMob)")
            try:
                match_data = self.comprehensive_scraper.get_comprehensive_match_data(
                    home_team=home_team,
                    away_team=away_team
                )

                data = {
                    "available": True,
                    "comprehensive": True,
                    "home": match_data['home_stats'],
                    "away": match_data['away_stats'],
                    "data_completeness": match_data['data_completeness']
                }

                logger.info("✅ Comprehensive data retrieved")
                logger.info(f"   Home sources: {len(match_data['home_stats']['sources_available'])}")
                logger.info(f"   Away sources: {len(match_data['away_stats']['sources_available'])}")
                logger.info(f"   Quality: {match_data['data_completeness']['quality_score']}/5.0")

                return data

            except Exception as e:
                logger.warning(f"⚠️  Comprehensive scraper failed: {e}")
                logger.info("   Falling back to basic FBref...")

        # Fallback to basic FBref (Q7, Q8, Q14 only)
        if hasattr(self, 'fbref') and self.fbref:
            logger.info("Using basic FBref integration")
            try:
                home_scores = self.fbref.get_all_scores(home_team)
                away_scores = self.fbref.get_all_scores(away_team)

                data = {
                    "available": True,
                    "comprehensive": False,
                    "home": {
                        "Q7": home_scores['Q7'],
                        "Q8": home_scores['Q8'],
                        "Q14": home_scores['Q14']
                    },
                    "away": {
                        "Q7": away_scores['Q7'],
                        "Q8": away_scores['Q8'],
                        "Q14": away_scores['Q14']
                    }
                }

                logger.info("✅ FBref data retrieved (basic)")
                logger.info(f"   Home Q7: +{home_scores['Q7']['score']}")
                logger.info(f"   Home Q8: +{home_scores['Q8']['score']}")
                logger.info(f"   Home Q14: +{home_scores['Q14']['score']}")

                return data

            except Exception as e:
                logger.error(f"❌ FBref retrieval failed: {e}")
                return {"available": False, "error": str(e)}

        # No data sources available
        logger.warning("⚠️  No soccerdata sources available, using defaults")
        return {"available": False}

    def _get_formations(self, match_id: str, home_team: str, away_team: str, league: str, date: str) -> Dict:
        """Get formations from database or prompt for manual entry"""
        if not self.formation_scraper:
            logger.warning("⚠️  Formation scraper not available, using defaults")
            return {
                "home_formation": "0",
                "away_formation": "0",
                "source": "default",
                "from_database": False
            }

        try:
            formations = self.formation_scraper.get_formations(
                match_id=match_id,
                home_team=home_team,
                away_team=away_team,
                league=league,
                date=date,
                interactive=True  # Allow manual entry if not in database
            )

            if formations['home_formation'] != '0':
                logger.info(f"✅ Formations: {formations['home_formation']} vs {formations['away_formation']}")
            else:
                logger.warning("⚠️  Formations not available yet (check closer to kickoff)")

            return formations

        except Exception as e:
            logger.error(f"❌ Formation retrieval failed: {e}")
            return {
                "home_formation": "0",
                "away_formation": "0",
                "source": "error",
                "from_database": False
            }

    def _assess_footystats_quality(self, data: Dict) -> float:
        """Assess FootyStats data quality (1-5)"""
        if not data.get("available", True):
            return 1.0

        # Check completeness
        required_fields = ['form', 'goals_scored', 'goals_conceded', 'xg']
        present = sum(1 for field in required_fields if field in str(data))
        quality = (present / len(required_fields)) * 5

        return round(quality, 1)

    def _assess_fbref_quality(self, data: Dict) -> float:
        """Assess FBref data quality (1-5)"""
        if not data.get("available", False):
            return 1.0

        # If all Q-scores have 'fbref' source, quality is 5
        try:
            sources = [
                data['home']['Q7'].get('source', 'default'),
                data['home']['Q8'].get('source', 'default'),
                data['home']['Q14'].get('source', 'default')
            ]
            fbref_count = sum(1 for s in sources if s == 'fbref')
            quality = (fbref_count / 3) * 5
            return round(quality, 1)
        except:
            return 1.0

    def _calculate_overall_quality(self, quality_dict: Dict) -> float:
        """Calculate overall data quality score"""
        scores = [
            quality_dict.get('footystats', 1.0),
            quality_dict.get('fbref', 1.0),
            quality_dict.get('formations', 1.0)
        ]

        # Weighted average (FootyStats most important, FBref bonus, formations nice-to-have)
        weights = [0.5, 0.3, 0.2]
        weighted_score = sum(s * w for s, w in zip(scores, weights))

        return round(weighted_score, 1)

    def _prepare_q_score_inputs(
        self,
        footystats_data: Dict,
        fbref_data: Dict,
        formations: Dict,
        home_team: str,
        away_team: str
    ) -> Dict:
        """
        Prepare structured inputs for Q-score calculation

        This creates the SINGLE SOURCE OF TRUTH for Claude AI analysis
        """
        inputs = {}

        # Q7 - Pressing (FBref if available, else default)
        if fbref_data.get('available', False):
            inputs['Q7'] = {
                "home_score": fbref_data['home']['Q7']['score'],
                "away_score": fbref_data['away']['Q7']['score'],
                "home_reasoning": fbref_data['home']['Q7']['reasoning'],
                "away_reasoning": fbref_data['away']['Q7']['reasoning'],
                "sources": [fbref_data['home']['Q7']['source']],
                "confidence": 5
            }
        else:
            inputs['Q7'] = {
                "home_score": 2,
                "away_score": 2,
                "home_reasoning": f"No FBref data for {home_team} → default +2",
                "away_reasoning": f"No FBref data for {away_team} → default +2",
                "sources": ["default"],
                "confidence": 1
            }

        # Q8 - Set Pieces (FBref if available, else default)
        if fbref_data.get('available', False):
            inputs['Q8'] = {
                "home_score": fbref_data['home']['Q8']['score'],
                "away_score": fbref_data['away']['Q8']['score'],
                "home_reasoning": fbref_data['home']['Q8']['reasoning'],
                "away_reasoning": fbref_data['away']['Q8']['reasoning'],
                "sources": [fbref_data['home']['Q8']['source']],
                "confidence": 5
            }
        else:
            inputs['Q8'] = {
                "home_score": 2,
                "away_score": 2,
                "home_reasoning": f"No FBref data for {home_team} → default +2",
                "away_reasoning": f"No FBref data for {away_team} → default +2",
                "sources": ["default"],
                "confidence": 1
            }

        # Q14 - Player Form (FBref if available, else default)
        if fbref_data.get('available', False):
            inputs['Q14'] = {
                "home_score": fbref_data['home']['Q14']['score'],
                "away_score": fbref_data['away']['Q14']['score'],
                "home_reasoning": fbref_data['home']['Q14']['reasoning'],
                "away_reasoning": fbref_data['away']['Q14']['reasoning'],
                "sources": [fbref_data['home']['Q14']['source']],
                "confidence": 5
            }
        else:
            inputs['Q14'] = {
                "home_score": 2,
                "away_score": 2,
                "home_reasoning": f"No FBref data for {home_team} → default +2",
                "away_reasoning": f"No FBref data for {away_team} → default +2",
                "sources": ["default"],
                "confidence": 1
            }

        # Q6 - Formations (Manual/Database)
        inputs['Q6'] = {
            "home_formation": formations['home_formation'],
            "away_formation": formations['away_formation'],
            "sources": [formations['source']],
            "confidence": 5 if formations['home_formation'] != '0' else 1
        }

        # Q1-Q5, Q9-Q13, Q15-Q19 will be calculated by Claude from FootyStats data
        # (Existing logic remains)

        return inputs


def test_integrated_scraper():
    """Test the integrated scraper"""
    print("\n" + "="*80)
    print("TESTING INTEGRATED DATA SCRAPER")
    print("="*80 + "\n")

    # Initialize
    scraper = IntegratedDataScraper(league='La Liga', season='2425')

    # Test match (you'll need to provide real URL)
    test_data = scraper.scrape_complete_match_data(
        match_id="TEST_BarcelonavsAthleticClub_22112025",
        home_team="Barcelona",
        away_team="Athletic Club",
        league="La Liga",
        date="22/11/2025",
        footystats_url="https://footystats.org/spain/la-liga/barcelona-vs-athletic-club-h2h-stats"
    )

    # Print summary
    print("\n" + "="*80)
    print("SCRAPING SUMMARY")
    print("="*80)
    print(f"\nData Quality Scores:")
    print(f"  FootyStats: {test_data['data_quality'].get('footystats', 'N/A')}/5")
    print(f"  FBref: {test_data['data_quality'].get('fbref', 'N/A')}/5")
    print(f"  Formations: {test_data['data_quality'].get('formations', 'N/A')}/5")
    print(f"  Overall: {test_data['data_quality']['overall_score']}/5")
    print(f"\nProceed: {test_data['data_quality']['proceed']}")

    print(f"\nQ-Score Inputs Prepared:")
    print(f"  Q7 (Pressing): Home +{test_data['q_score_inputs']['Q7']['home_score']}, Away +{test_data['q_score_inputs']['Q7']['away_score']}")
    print(f"  Q8 (Set Pieces): Home +{test_data['q_score_inputs']['Q8']['home_score']}, Away +{test_data['q_score_inputs']['Q8']['away_score']}")
    print(f"  Q14 (Player Form): Home +{test_data['q_score_inputs']['Q14']['home_score']}, Away +{test_data['q_score_inputs']['Q14']['away_score']}")
    print(f"  Q6 (Formations): {test_data['q_score_inputs']['Q6']['home_formation']} vs {test_data['q_score_inputs']['Q6']['away_formation']}")

    print("\n" + "="*80 + "\n")

    return test_data


if __name__ == "__main__":
    test_integrated_scraper()
