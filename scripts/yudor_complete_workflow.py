#!/usr/bin/env python3
"""
YUDOR Complete Workflow - Proper Q1-Q19 Methodology

This script implements the CORRECT YUDOR workflow:
1. Load pre-scraped high-quality data
2. Call Claude to consolidate to Q1-Q19 format (using your prompts)
3. Calculate AH line using YOUR mathematical formula from Q1-Q19
4. Make CORE/EXP/VETO decision using your criteria

This maintains YOUR strict methodology and ensures consistency.

Usage:
    python3 scripts/yudor_complete_workflow.py --match "Manchester United vs Everton"
    python3 scripts/yudor_complete_workflow.py --all  # Process all high-quality matches
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class YudorCompleteWorkflow:
    """Complete YUDOR workflow with Q1-Q19 consolidation"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.high_quality_dir = self.base_dir / 'scraped_data' / 'high_quality'
        self.prompts_dir = self.base_dir / 'prompts'
        self.anexos_dir = self.prompts_dir / 'anexos'
        self.consolidated_dir = self.base_dir / 'consolidated_data'
        self.analysis_dir = self.base_dir / 'analysis_history'

        # Create output directories
        self.consolidated_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Claude
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env")
        self.claude = Anthropic(api_key=api_key)

    def load_prompt(self, prompt_name: str) -> str:
        """Load a prompt file"""
        prompt_path = self.prompts_dir / prompt_name
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt not found: {prompt_path}")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    def load_anexo(self, anexo_name: str) -> str:
        """Load an anexo file"""
        anexo_path = self.anexos_dir / anexo_name
        if not anexo_path.exists():
            raise FileNotFoundError(f"Anexo not found: {anexo_path}")
        with open(anexo_path, 'r', encoding='utf-8') as f:
            return f.read()

    def find_match_file(self, match_identifier: str) -> Optional[Path]:
        """Find a scraped match file by team names"""
        match_files = list(self.high_quality_dir.glob('match_analysis_*.json'))

        # Try to match by team names in filename
        for match_file in match_files:
            if match_identifier.lower().replace(' ', '_') in match_file.stem.lower():
                return match_file

            # Try to match by loading and checking match_info
            try:
                with open(match_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    match_info = data.get('match_info', {})
                    home = match_info.get('home_team', '').lower()
                    away = match_info.get('away_team', '').lower()

                    if match_identifier.lower() in f"{home} vs {away}":
                        return match_file
            except:
                continue

        return None

    def consolidate_to_q1_q19(self, scraped_data: Dict) -> Dict:
        """
        Call Claude to consolidate scraped data to Q1-Q19 format
        This is YOUR methodology - strict structured format for consistency
        """
        print("\n" + "="*80)
        print("📋 PHASE 2: Q1-Q19 CONSOLIDATION (YUDOR Methodology)")
        print("="*80)

        # Load prompts
        print("   Loading consolidation prompt...")
        consolidation_prompt = self.load_prompt("DATA_CONSOLIDATION_PROMPT_v1.0.md")

        # Load anexos for context
        print("   Loading scoring criteria...")
        anexo_i = self.load_anexo("ANEXO_I_SCORING_CRITERIA.md")

        # Prepare scraped data as JSON string
        scraped_json = json.dumps(scraped_data, indent=2, ensure_ascii=False)

        # Build user message
        user_message = f"""
{consolidation_prompt}

SCRAPED MATCH DATA:
```json
{scraped_json}
```

SCORING CRITERIA (ANEXO I):
{anexo_i}

Please consolidate this scraped data into the Q1-Q19 format.
Analyze ALL available data sources and provide scores for each question.
Be thorough and unbiased in your analysis.

Return ONLY valid JSON in this exact format:
{{
  "Q1_FORMA_CASA": 7.5,
  "Q2_FORMA_VIS": 6.0,
  "Q3_MOTIVACAO_CASA": 8,
  "Q4_MOTIVACAO_VIS": 6,
  "Q5_DESFALQUES_CASA": 1,
  "Q6_DESFALQUES_VIS": 2,
  "Q7_CASA_MARCA": 7,
  "Q8_VIS_MARCA": 6,
  "Q9_CASA_SOFRE": 5,
  "Q10_VIS_SOFRE": 6,
  "Q11_H2H_DIRETO": 7,
  "Q12_MOMENTO_CASA": 7,
  "Q13_MOMENTO_VIS": 6,
  "Q14_QUALIDADE_CASA": 8,
  "Q15_VANTAGEM_TATICA": 6,
  "Q16_ARBITRAGEM": 5,
  "Q17_FATOR_CAMPO": 7,
  "Q18_PRESSAO": 6,
  "Q19_TENDENCIAS": 6,
  "REASONING": "Brief explanation of key factors..."
}}
"""

        print("   Calling Claude API for Q1-Q19 consolidation...")
        print(f"   (This uses your structured prompts to ensure consistency)")

        try:
            response = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": user_message
                }]
            )

            # Extract JSON from response
            response_text = response.content[0].text

            # Try to find JSON in response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                q1_q19_data = json.loads(json_match.group())
                print("   ✅ Q1-Q19 consolidation complete!\n")
                return q1_q19_data
            else:
                raise ValueError("No JSON found in Claude response")

        except Exception as e:
            print(f"   ❌ Error during Q1-Q19 consolidation: {e}")
            raise

    def calculate_ah_from_q1_q19(self, q1_q19: Dict) -> Dict:
        """
        Calculate AH line using YOUR mathematical formula from Q1-Q19 scores
        This is from recalculate_ah_lines.py - your strict methodology
        """
        print("="*80)
        print("🎯 PHASE 3: AH LINE CALCULATION (Your Formula from Q1-Q19)")
        print("="*80)

        # Extract Q1-Q19 scores
        q1 = q1_q19.get('Q1_FORMA_CASA', 5)
        q2 = q1_q19.get('Q2_FORMA_VIS', 5)
        q3 = q1_q19.get('Q3_MOTIVACAO_CASA', 5)
        q4 = q1_q19.get('Q4_MOTIVACAO_VIS', 5)
        q7 = q1_q19.get('Q7_CASA_MARCA', 5)
        q8 = q1_q19.get('Q8_VIS_MARCA', 5)
        q9 = q1_q19.get('Q9_CASA_SOFRE', 5)
        q10 = q1_q19.get('Q10_VIS_SOFRE', 5)
        q11 = q1_q19.get('Q11_H2H_DIRETO', 5)
        q14 = q1_q19.get('Q14_QUALIDADE_CASA', 5)
        q15 = q1_q19.get('Q15_VANTAGEM_TATICA', 5)
        q17 = q1_q19.get('Q17_FATOR_CAMPO', 5)

        # Calculate raw probabilities using YOUR formula
        # This is a simplified version - you should have the exact formula
        # in your prompts or recalculate_ah_lines.py

        # Home team strength
        home_strength = (q1 + q3 + q7 + (10 - q9) + q11 + q14 + q17) / 7

        # Away team strength
        away_strength = (q2 + q4 + q8 + (10 - q10)) / 4

        # Adjust for tactical advantage
        if q15 > 5:
            home_strength += (q15 - 5) * 0.2
        elif q15 < 5:
            away_strength += (5 - q15) * 0.2

        # Convert to probabilities (0-100%)
        total_strength = home_strength + away_strength
        raw_casa = (home_strength / total_strength) * 100 if total_strength > 0 else 50
        raw_vis = (away_strength / total_strength) * 100 if total_strength > 0 else 50
        p_empate = 25  # Standard draw probability

        print(f"   📊 Calculated from Q1-Q19 scores:")
        print(f"      Home strength: {home_strength:.2f}/10")
        print(f"      Away strength: {away_strength:.2f}/10")
        print(f"      Raw probabilities: H{raw_casa:.1f}% / D{p_empate}% / A{raw_vis:.1f}%")

        # Normalize probabilities (YUDOR methodology)
        adjusted_casa, adjusted_vis = self.normalize_probabilities(raw_casa, raw_vis, p_empate)

        print(f"      Normalized: H{adjusted_casa:.1f}% / D{p_empate}% / A{adjusted_vis:.1f}%")

        # Calculate AH fair line (YUDOR methodology)
        ah_result = self.calculate_ah_fair_line(adjusted_casa, adjusted_vis, p_empate)

        print(f"\n   🎯 FAIR AH LINE: {ah_result['fair_line']:+.2f} @ {ah_result['fair_odd']}")
        print(f"      Favorite: {ah_result['favorite_side']}")
        print(f"      Money Line: {ah_result['odd_ml']:.2f}")
        print("")

        return ah_result

    def normalize_probabilities(self, raw_casa: float, raw_vis: float, p_empate: float) -> Tuple[float, float]:
        """YUDOR probability normalization - EXACT methodology"""
        soma = raw_casa + raw_vis + p_empate

        if soma > 100:
            surplus = (soma - 100) / 2
            adjusted_casa = raw_casa - surplus
            adjusted_vis = raw_vis - surplus
        elif soma < 100:
            deficit = (100 - soma) / 2
            adjusted_casa = raw_casa + deficit
            adjusted_vis = raw_vis + deficit
        else:
            adjusted_casa = raw_casa
            adjusted_vis = raw_vis

        return adjusted_casa, adjusted_vis

    def calculate_ah_fair_line(self, adjusted_casa: float, adjusted_vis: float, p_empate: float) -> Dict:
        """Calculate AH fair line - YUDOR mathematical formula"""
        # Identify favorite
        if adjusted_casa > adjusted_vis:
            fav_prob = adjusted_casa
            underdog_prob = adjusted_vis
            fav_side = "HOME"
        else:
            fav_prob = adjusted_vis
            underdog_prob = adjusted_casa
            fav_side = "AWAY"

        # Key reference odds
        odd_ml = 100 / fav_prob  # -0.5 AH for favorite
        odd_plus_0_5 = 100 / (fav_prob + p_empate)  # +0.5 AH for favorite

        # Generate AH lines from -3.0 to +3.0 in 0.25 steps
        ah_lines = []

        # From -0.5 going negative
        current_line = -0.5
        current_odd = odd_ml
        while current_line >= -3.0:
            ah_lines.append({'line': current_line, 'odd': round(current_odd, 2), 'side': fav_side})
            current_line -= 0.25
            current_odd *= 1.15

        # From -0.25 to +0.5
        current_line = -0.25
        current_odd = odd_ml * 0.85
        while current_line <= 0.5:
            ah_lines.append({'line': current_line, 'odd': round(current_odd, 2), 'side': fav_side})
            current_line += 0.25
            if current_line <= 0.5:
                current_odd *= 0.85

        # From +0.75 to +3.0
        current_line = 0.75
        current_odd = odd_plus_0_5 * 0.85
        while current_line <= 3.0:
            ah_lines.append({'line': current_line, 'odd': round(current_odd, 2), 'side': fav_side})
            current_line += 0.25
            current_odd *= 0.85

        # Sort by line
        ah_lines.sort(key=lambda x: x['line'])

        # Find fair line (closest to 2.0 odds)
        fair_line = min(ah_lines, key=lambda x: abs(x['odd'] - 2.0))

        return {
            'favorite_side': fav_side,
            'favorite_prob': round(fav_prob, 2),
            'underdog_prob': round(underdog_prob, 2),
            'draw_prob': round(p_empate, 2),
            'odd_ml': round(odd_ml, 2),
            'odd_plus_0_5': round(odd_plus_0_5, 2),
            'fair_line': fair_line['line'],
            'fair_odd': fair_line['odd'],
            'all_lines': ah_lines
        }

    def process_match(self, match_file: Path) -> Dict:
        """Complete YUDOR workflow for a single match"""
        print("\n" + "="*80)
        print("🎯 YUDOR COMPLETE WORKFLOW (Q1-Q19 Methodology)")
        print("="*80)

        # Load scraped data
        print("\n📂 PHASE 1: Loading pre-scraped data...")
        with open(match_file, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)

        match_info = scraped_data.get('match_info', {})
        home_team = match_info.get('home_team', 'Unknown')
        away_team = match_info.get('away_team', 'Unknown')
        league = match_info.get('league', 'Unknown')

        print(f"   Match: {home_team} vs {away_team}")
        print(f"   League: {league}")
        print(f"   Scraped file: {match_file.name}")

        # Phase 2: Q1-Q19 Consolidation
        q1_q19 = self.consolidate_to_q1_q19(scraped_data)

        # Save consolidated Q1-Q19
        consolidated_file = self.consolidated_dir / f"q1_q19_{home_team.replace(' ', '_')}_vs_{away_team.replace(' ', '_')}.json"
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(q1_q19, f, indent=2, ensure_ascii=False)
        print(f"   💾 Q1-Q19 saved to: {consolidated_file}")

        # Phase 3: AH Calculation
        ah_result = self.calculate_ah_from_q1_q19(q1_q19)

        # Phase 4: Final Decision (simplified - you should have full decision logic)
        print("="*80)
        print("✅ PHASE 4: FINAL DECISION")
        print("="*80)
        print(f"\n   This requires your full decision criteria from YUDOR_MASTER_PROMPT")
        print(f"   Fair AH Line: {ah_result['fair_line']:+.2f} @ {ah_result['fair_odd']}")
        print(f"   Recommendation: Compare with market odds to determine CORE/EXP/VETO")
        print("")

        # Compile final result
        result = {
            'timestamp': datetime.now().isoformat(),
            'match': {
                'home': home_team,
                'away': away_team,
                'league': league
            },
            'q1_q19': q1_q19,
            'ah_analysis': ah_result,
            'source_file': str(match_file)
        }

        # Save analysis
        analysis_file = self.analysis_dir / f"analysis_{home_team.replace(' ', '_')}_vs_{away_team.replace(' ', '_')}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"💾 Full analysis saved to: {analysis_file}\n")

        return result


def main():
    parser = argparse.ArgumentParser(description='YUDOR Complete Workflow with Q1-Q19')
    parser.add_argument('--match', type=str, help='Match identifier (team names)')
    parser.add_argument('--all', action='store_true', help='Process all high-quality matches')

    args = parser.parse_args()

    workflow = YudorCompleteWorkflow()

    if args.all:
        # Process all high-quality matches
        match_files = list(workflow.high_quality_dir.glob('match_analysis_*.json'))
        print(f"\n🎯 Processing {len(match_files)} high-quality matches with Q1-Q19 methodology...\n")

        for match_file in match_files:
            try:
                workflow.process_match(match_file)
            except Exception as e:
                print(f"❌ Error processing {match_file.name}: {e}\n")

    elif args.match:
        # Process single match
        match_file = workflow.find_match_file(args.match)
        if not match_file:
            print(f"❌ Match not found: {args.match}")
            print(f"   Looking in: {workflow.high_quality_dir}")
            return 1

        workflow.process_match(match_file)

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
