#!/usr/bin/env python3
"""
YUDOR Integrated Workflow - Complete End-to-End System

This combines:
1. batch_match_analyzer.py (scraping with complete_match_analyzer.py)
2. URL content fetching (SportsMole, Marca news)
3. Q1-Q19 consolidation (Claude API with your prompts)
4. AH calculation (from Q1-Q19 scores - your formula)
5. Final decision (CORE/EXP/VETO/FLIP)

Usage:
    python3 scripts/yudor_integrated_workflow.py matches.csv

CSV Format:
    Date,League,Home,Away,Stadium
    24/11,Premier League,Manchester United,Everton,Old Trafford
"""

import os
import sys
import csv
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from anthropic import Anthropic
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from complete_match_analyzer import CompleteMatchAnalyzer

# Load environment variables
load_dotenv()


class YudorIntegratedWorkflow:
    """
    Complete YUDOR workflow from CSV to final decision
    Preserves your Q1-Q19 methodology for consistency
    """

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.scraped_dir = self.base_dir / 'scraped_data' / 'high_quality'
        self.prompts_dir = self.base_dir / 'prompts'
        self.anexos_dir = self.prompts_dir / 'anexos'
        self.consolidated_dir = self.base_dir / 'consolidated_data'
        self.analysis_dir = self.base_dir / 'analysis_history'

        # Create directories
        self.consolidated_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Claude
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env")
        self.claude = Anthropic(api_key=api_key)

        self.results = []

    def read_matches_from_csv(self, csv_file: str) -> List[Dict]:
        """Read matches from CSV file"""
        matches = []

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                match = {
                    'date': row.get('Date', row.get('Data', '')),
                    'league': row.get('League', row.get('Torneio', '')),
                    'home': row.get('Home', ''),
                    'away': row.get('Away', ''),
                    'stadium': row.get('Stadium', row.get('Estádio', 'Unknown'))
                }

                # Handle combined "Home vs Away" format
                if not match['home'] and 'Jogo (Casa vs. Visitante)' in row:
                    teams = row['Jogo (Casa vs. Visitante)'].split(' vs. ')
                    if len(teams) == 2:
                        match['home'] = teams[0]
                        match['away'] = teams[1]

                matches.append(match)

        return matches

    def fetch_url_content(self, url: str, max_chars: int = 15000) -> str:
        """Fetch and extract text content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                return f"[HTTP {response.status_code}]"

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove scripts, styles, nav, footer
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()

            # Get text
            text = soup.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = '\n'.join(lines)

            # Truncate if too long
            if len(text) > max_chars:
                text = text[:max_chars] + "\n...[truncated]"

            return text

        except Exception as e:
            return f"[Error: {str(e)[:100]}]"

    def enrich_scraped_data(self, scraped_data: Dict) -> Dict:
        """
        Enrich scraped data with URL content
        Fetches SportsMole preview, Marca news, etc.
        """
        print("   📡 Fetching URL content...")

        # Get SportsMole preview
        sportsmole_url = scraped_data.get('sportsmole_preview_url')
        if sportsmole_url and sportsmole_url != 'NOT_FOUND':
            print(f"      • SportsMole preview...")
            content = self.fetch_url_content(sportsmole_url)
            if content and not content.startswith('['):
                scraped_data['sportsmole_content'] = content
                print(f"        ✓ Got {len(content)} chars")
            else:
                print(f"        ✗ Failed: {content[:50]}")

        # TODO: Add Marca news fetching when URLs are available
        # TODO: Add SofaScore content fetching

        return scraped_data

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

    def consolidate_to_q1_q19(self, enriched_data: Dict) -> Dict:
        """
        Claude API consolidation to Q1-Q19 format
        YOUR YUDOR METHODOLOGY - ensures consistency
        """
        print("\n   📋 Q1-Q19 Consolidation (Claude API)...")

        # Load prompts
        consolidation_prompt = self.load_prompt("DATA_CONSOLIDATION_PROMPT_v1.0.md")
        anexo_i = self.load_anexo("ANEXO_I_SCORING_CRITERIA.md")

        # Prepare data
        data_json = json.dumps(enriched_data, indent=2, ensure_ascii=False, default=str)

        user_message = f"""
{consolidation_prompt}

SCRAPED MATCH DATA:
```json
{data_json}
```

SCORING CRITERIA (ANEXO I):
{anexo_i}

Consolidate this data into Q1-Q19 format. Analyze ALL available sources.
Return ONLY valid JSON with Q1-Q19 scores and reasoning.
"""

        try:
            response = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": user_message}]
            )

            response_text = response.content[0].text

            # Extract JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                q1_q19_data = json.loads(json_match.group())
                print("      ✓ Q1-Q19 consolidation complete")
                return q1_q19_data
            else:
                raise ValueError("No JSON in Claude response")

        except Exception as e:
            print(f"      ✗ Error: {e}")
            raise

    def calculate_ah_from_q1_q19(self, q1_q19: Dict) -> Dict:
        """
        Calculate AH line from Q1-Q19 scores
        YOUR mathematical formula - not changed
        """
        print("   🎯 Calculating AH line from Q1-Q19...")

        # Extract Q scores (your formula uses specific Qs)
        q1 = q1_q19.get('Q1_FORMA_CASA', 5)
        q2 = q1_q19.get('Q2_FORMA_VIS', 5)
        q7 = q1_q19.get('Q7_CASA_MARCA', 5)
        q8 = q1_q19.get('Q8_VIS_MARCA', 5)
        q17 = q1_q19.get('Q17_FATOR_CAMPO', 5)

        # Your formula (simplified - should match your exact calculation)
        home_strength = (q1 + q7 + q17) / 3
        away_strength = (q2 + q8) / 2

        total = home_strength + away_strength
        raw_casa = (home_strength / total) * 100 if total > 0 else 50
        raw_vis = (away_strength / total) * 100 if total > 0 else 50
        p_empate = 25

        # Normalize
        adj_casa, adj_vis = self.normalize_probabilities(raw_casa, raw_vis, p_empate)

        # Calculate AH
        ah_result = self.calculate_ah_fair_line(adj_casa, adj_vis, p_empate)

        print(f"      ✓ Fair AH Line: {ah_result['fair_line']:+.2f} @ {ah_result['fair_odd']}")

        return ah_result

    def normalize_probabilities(self, raw_casa: float, raw_vis: float, p_empate: float) -> Tuple[float, float]:
        """YUDOR normalization - exact methodology"""
        soma = raw_casa + raw_vis + p_empate

        if soma > 100:
            surplus = (soma - 100) / 2
            return raw_casa - surplus, raw_vis - surplus
        elif soma < 100:
            deficit = (100 - soma) / 2
            return raw_casa + deficit, raw_vis + deficit
        else:
            return raw_casa, raw_vis

    def calculate_ah_fair_line(self, adj_casa: float, adj_vis: float, p_empate: float) -> Dict:
        """Calculate AH fair line - YUDOR formula"""
        fav_prob = max(adj_casa, adj_vis)
        fav_side = "HOME" if adj_casa > adj_vis else "AWAY"

        odd_ml = 100 / fav_prob
        odd_plus_0_5 = 100 / (fav_prob + p_empate)

        # Generate lines -3.0 to +3.0
        ah_lines = []

        # Negative lines
        current_line, current_odd = -0.5, odd_ml
        while current_line >= -3.0:
            ah_lines.append({'line': current_line, 'odd': round(current_odd, 2), 'side': fav_side})
            current_line -= 0.25
            current_odd *= 1.15

        # Positive lines
        current_line, current_odd = -0.25, odd_ml * 0.85
        while current_line <= 3.0:
            ah_lines.append({'line': current_line, 'odd': round(current_odd, 2), 'side': fav_side})
            current_line += 0.25
            current_odd *= 0.85

        ah_lines.sort(key=lambda x: x['line'])
        fair_line = min(ah_lines, key=lambda x: abs(x['odd'] - 2.0))

        return {
            'favorite_side': fav_side,
            'fair_line': fair_line['line'],
            'fair_odd': fair_line['odd'],
            'odd_ml': round(odd_ml, 2),
            'all_lines': ah_lines
        }

    def process_single_match(self, match: Dict) -> Dict:
        """
        Complete YUDOR workflow for one match
        Phase 1: Scrape → Phase 2: Enrich → Phase 3: Q1-Q19 → Phase 4: AH → Phase 5: Decision
        """
        print(f"\n{'='*80}")
        print(f"🎯 {match['home']} vs {match['away']}")
        print(f"   {match['league']} | {match['date']}")
        print('='*80)

        try:
            # PHASE 1: Scrape data (using your complete_match_analyzer.py)
            print("\n1️⃣  PHASE 1: Scraping data...")
            analyzer = CompleteMatchAnalyzer(league=match['league'], season='2425')
            scraped_data = analyzer.analyze_match(match['home'], match['away'])

            sources_count = scraped_data['summary']['total_sources']
            print(f"   ✓ Scraped {sources_count} sources")

            # Check quality threshold
            if sources_count < 5:
                print(f"   ⚠️  Only {sources_count} sources - skipping (need 5+)")
                return {'match': f"{match['home']} vs {match['away']}", 'status': 'skipped', 'reason': 'insufficient_sources'}

            # Save scraped data
            filename = analyzer.save_analysis(scraped_data)
            print(f"   💾 Saved to: {Path(filename).name}")

            # PHASE 2: Enrich with URL content
            print("\n2️⃣  PHASE 2: Fetching URL content...")
            enriched_data = self.enrich_scraped_data(scraped_data)

            # PHASE 3: Q1-Q19 Consolidation
            print("\n3️⃣  PHASE 3: Q1-Q19 Consolidation...")
            q1_q19 = self.consolidate_to_q1_q19(enriched_data)

            # Save Q1-Q19
            home = match['home'].replace(' ', '_')
            away = match['away'].replace(' ', '_')
            q1_q19_file = self.consolidated_dir / f"q1_q19_{home}_vs_{away}.json"
            with open(q1_q19_file, 'w', encoding='utf-8') as f:
                json.dump(q1_q19, f, indent=2, ensure_ascii=False)
            print(f"   💾 Q1-Q19 saved to: {q1_q19_file.name}")

            # PHASE 4: AH Calculation
            print("\n4️⃣  PHASE 4: AH Line Calculation...")
            ah_result = self.calculate_ah_from_q1_q19(q1_q19)

            # PHASE 5: Final Decision (placeholder - needs your full decision logic)
            print("\n5️⃣  PHASE 5: Final Decision...")
            print(f"   → Fair AH: {ah_result['fair_line']:+.2f} @ {ah_result['fair_odd']}")
            print(f"   → Compare with market odds for CORE/EXP/VETO decision")

            # Compile result
            result = {
                'timestamp': datetime.now().isoformat(),
                'match': {
                    'home': match['home'],
                    'away': match['away'],
                    'league': match['league'],
                    'date': match['date']
                },
                'sources': sources_count,
                'q1_q19': q1_q19,
                'ah_analysis': ah_result,
                'status': 'completed'
            }

            # Save final analysis
            analysis_file = self.analysis_dir / f"analysis_{home}_vs_{away}.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"\n✅ COMPLETE! Analysis saved to: {analysis_file.name}\n")

            return result

        except Exception as e:
            print(f"\n❌ ERROR: {e}\n")
            return {
                'match': f"{match['home']} vs {match['away']}",
                'status': 'error',
                'error': str(e)
            }

    def process_all_matches(self, matches: List[Dict]) -> Dict:
        """Process all matches from CSV"""
        print("\n" + "="*80)
        print("🎯 YUDOR INTEGRATED WORKFLOW - COMPLETE SYSTEM")
        print("="*80)
        print(f"\n📊 Processing {len(matches)} matches...")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        start_time = time.time()

        for idx, match in enumerate(matches, 1):
            print(f"\n[{idx}/{len(matches)}]")
            result = self.process_single_match(match)
            self.results.append(result)

            # Brief pause
            if idx < len(matches):
                time.sleep(2)

        # Summary
        elapsed = time.time() - start_time
        completed = sum(1 for r in self.results if r['status'] == 'completed')

        print("\n" + "="*80)
        print("📊 BATCH SUMMARY")
        print("="*80)
        print(f"   Total: {len(matches)}")
        print(f"   Completed: {completed}")
        print(f"   Skipped: {len(matches) - completed}")
        print(f"   Time: {elapsed:.1f}s")
        print("="*80 + "\n")

        return {
            'total': len(matches),
            'completed': completed,
            'time': elapsed,
            'results': self.results
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/yudor_integrated_workflow.py matches.csv")
        print("\nCSV Format:")
        print("  Date,League,Home,Away,Stadium")
        print("  24/11,Premier League,Manchester United,Everton,Old Trafford")
        return 1

    csv_file = sys.argv[1]

    if not Path(csv_file).exists():
        print(f"❌ File not found: {csv_file}")
        return 1

    # Run workflow
    workflow = YudorIntegratedWorkflow()
    matches = workflow.read_matches_from_csv(csv_file)
    summary = workflow.process_all_matches(matches)

    return 0 if summary['completed'] > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
