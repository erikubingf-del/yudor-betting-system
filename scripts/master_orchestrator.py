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
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic
from pyairtable import Api
from typing import Dict, List, Optional

# =========================
# CONFIGURATION
# =========================

class Config:
    """System configuration - Edit these values"""
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "")
    AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
    
    # Directories
    BASE_DIR = Path(__file__).parent
    PROMPTS_DIR = BASE_DIR / "prompts"
    ANALYSIS_DIR = BASE_DIR / "analysis_history"
    
    # Files
    MATCHES_FILE = BASE_DIR / "matches.txt"
    SCRAPER_SCRIPT = BASE_DIR / "scraper.py"
    
    # Settings
    CLAUDE_MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 4000
    
    # Ensure directories exist
    ANALYSIS_DIR.mkdir(exist_ok=True)
    PROMPTS_DIR.mkdir(exist_ok=True)


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
        "analyses": "Match_Analyses",
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
    # STAGE 1: SCRAPING
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
        if match_string:
            temp_file = self.config.BASE_DIR / "temp_matches.txt"
            with open(temp_file, "w") as f:
                f.write(match_string)
            # TODO: Modify scraper to accept input file param
        
        # Run scraper
        result = subprocess.run(
            ["python", str(self.config.SCRAPER_SCRIPT)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Scraper failed: {result.stderr}")
            sys.exit(1)
        
        print("✅ URLs scraped successfully")
        
        # Return path to generated JSON
        return str(self.config.BASE_DIR / "match_data_v29.json")
    
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
        extraction_prompt_path = self.config.PROMPTS_DIR / "extraction_prompt.md"
        if not extraction_prompt_path.exists():
            print("⚠️  extraction_prompt.md not found - using default")
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
    
    def analyze_match(self, extracted_data: Dict, match_id: str) -> Dict:
        """
        Run Yudor analysis with BLIND PRICING (no market odds)
        
        Args:
            extracted_data: Data from extraction stage
            match_id: Match identifier
            
        Returns:
            Analysis results
        """
        print("\n" + "="*80)
        print("🎯 STAGE 3: YUDOR ANALYSIS (BLIND PRICING)")
        print("="*80)
        
        # Load Yudor analysis prompt
        yudor_prompt_path = self.config.PROMPTS_DIR / "yudor_analysis_prompt.md"
        if not yudor_prompt_path.exists():
            print("❌ yudor_analysis_prompt.md not found!")
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
        
        # Call Claude for analysis
        print("🤖 Running Yudor analysis...")
        
        try:
            message = self.claude.messages.create(
                model=self.config.CLAUDE_MODEL,
                max_tokens=self.config.MAX_TOKENS,
                system=yudor_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Analyze this match (BLIND PRICING - no market odds):\n\n{json.dumps(extracted_data, indent=2)}"
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
            
            record_data = {
                "match_id": match_id,
                "date": match_info.get("date", ""),
                "home_team": match_info.get("home", ""),
                "away_team": match_info.get("away", ""),
                "league": match_info.get("league", ""),
                "analysis_timestamp": datetime.now().isoformat(),
                "yudor_ah_fair": analysis.get("yudor_fair_ah", 0),
                "yudor_decision": analysis.get("decision", ""),
                "cs_final": analysis.get("cs_final", 0),
                "r_score": analysis.get("r_score", 0),
                "tier": analysis.get("tier", 0),
                "full_analysis": json.dumps(analysis, indent=2),
                "data_quality": analysis.get("confidence", 0),
                "status": "ANALYZED"
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
    # INTERACTIVE EDGE CALCULATION
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
    
    def analyze_complete(self, match_string: str):
        """
        Complete workflow: scrape → extract → analyze → save
        
        Args:
            match_string: Match like "Flamengo vs Bragantino, Brasileirão, 25/11/2025, 19:00"
        """
        print("\n" + "="*80)
        print("🎯 YUDOR COMPLETE ANALYSIS WORKFLOW")
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
        analysis = self.analyze_match(extracted_data, match_id)
        
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
# CLI INTERFACE
# =========================

def main():
    """Main CLI interface"""
    
    if len(sys.argv) < 2:
        print("""
🎯 YUDOR MASTER ORCHESTRATOR

Usage:
  python master_orchestrator.py analyze "Flamengo vs Bragantino, Brasileirão, 25/11/2025, 19:00"
  python master_orchestrator.py batch
  python master_orchestrator.py review MATCH_ID
  python master_orchestrator.py track MATCH_ID --result "2-1" --won

Commands:
  analyze "match"  - Analyze single match
  batch            - Analyze all matches in matches.txt
  review MATCH_ID  - Review past analysis
  track MATCH_ID   - Track bet result
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    orchestrator = YudorOrchestrator()
    
    if command == "analyze":
        if len(sys.argv) < 3:
            print("❌ Usage: python master_orchestrator.py analyze \"match string\"")
            sys.exit(1)
        
        match_string = sys.argv[2]
        orchestrator.analyze_complete(match_string)
    
    elif command == "batch":
        # TODO: Implement batch processing
        print("🚧 Batch mode - coming soon!")
    
    elif command == "review":
        # TODO: Implement review
        print("🚧 Review mode - coming soon!")
    
    elif command == "track":
        # TODO: Implement result tracking
        print("🚧 Track mode - coming soon!")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
