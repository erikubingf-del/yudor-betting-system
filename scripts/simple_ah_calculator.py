#!/usr/bin/env python3
"""
YUDOR Betting System - Simplified AH Line Calculator

Processes high-quality match data and calculates Asian Handicap lines
without requiring Claude API or full consolidation workflow.

Usage:
    python3 scripts/simple_ah_calculator.py

Features:
- Loads all high-quality matches (5+ sources)
- Calculates AH fair lines using YUDOR methodology
- Generates probability distributions
- Saves results to ah_calculations/ folder
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, List


class SimpleAHCalculator:
    """Calculate AH lines from scraped match data"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.high_quality_dir = self.base_dir / 'scraped_data' / 'high_quality'
        self.output_dir = self.base_dir / 'ah_calculations'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def normalize_probabilities(self, raw_casa: float, raw_vis: float, p_empate: float) -> Tuple[float, float]:
        """
        YUDOR METHODOLOGY:
        - If sum > 100: Remove surplus equally from both teams
        - If sum < 100: Add deficit equally to both teams
        - P(Empate) ALWAYS stays unchanged
        """
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
        """
        Calculate Fair AH Line using 0.25 intervals with ±15% odds progression

        YUDOR METHODOLOGY:
        1. Favorite = max(adjusted_casa, adjusted_vis)
        2. Odd_ML = 100 / Favorite → This is -0.5 AH for favorite
        3. Reference: +0.5 AH = 100 / (Favorite + P_Empate)
        4. Iterate with 0.25 steps:
           - Each -0.25: odds *= 1.15
           - Each +0.25: odds *= 0.85
        5. Target: odds ~2.0 [1.97, 2.03]
        """
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

        # Start from -0.5 (odd_ml) and go negative (stronger handicap)
        current_line = -0.5
        current_odd = odd_ml
        while current_line >= -3.0:
            ah_lines.append({
                'line': current_line,
                'odd': round(current_odd, 2),
                'side': fav_side
            })
            current_line -= 0.25
            current_odd *= 1.15  # Each -0.25 increases odds by 15%

        # Start from -0.25 and go to +0.5
        current_line = -0.25
        current_odd = odd_ml * 0.85
        while current_line <= 0.5:
            ah_lines.append({
                'line': current_line,
                'odd': round(current_odd, 2),
                'side': fav_side
            })
            current_line += 0.25
            if current_line <= 0.5:
                current_odd *= 0.85  # Each +0.25 decreases odds by 15%

        # Continue from +0.75 to +3.0
        current_line = 0.75
        current_odd = odd_plus_0_5 * 0.85
        while current_line <= 3.0:
            ah_lines.append({
                'line': current_line,
                'odd': round(current_odd, 2),
                'side': fav_side
            })
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

    def extract_probabilities_from_match(self, match_data: Dict) -> Dict:
        """Extract win/draw probabilities from match data"""

        # Try to get probabilities from multiple sources
        home_win_probs = []
        away_win_probs = []
        sources_used = []

        # Extract xG from FBref
        home_data = match_data.get('home_team_data', {})
        away_data = match_data.get('away_team_data', {})

        # FBref xG data
        if 'fbref' in home_data and 'fbref' in away_data:
            home_fbref = home_data['fbref']
            away_fbref = away_data['fbref']

            # Try to get xG from standard stats
            if 'standard' in home_fbref and 'standard' in away_fbref:
                try:
                    home_xg = float(home_fbref['standard'].get("('Expected', 'xG')", 0))
                    away_xg = float(away_fbref['standard'].get("('Expected', 'xG')", 0))

                    if home_xg > 0 and away_xg > 0:
                        # Convert season xG to per-match average
                        home_matches = float(home_fbref['standard'].get("('Playing Time', 'MP')", 38))
                        away_matches = float(away_fbref['standard'].get("('Playing Time', 'MP')", 38))

                        home_xg_per_match = home_xg / home_matches if home_matches > 0 else 0
                        away_xg_per_match = away_xg / away_matches if away_matches > 0 else 0

                        # Use xG as proxy for scoring probability
                        total_xg = home_xg_per_match + away_xg_per_match
                        if total_xg > 0:
                            home_win_probs.append((home_xg_per_match / total_xg) * 100)
                            away_win_probs.append((away_xg_per_match / total_xg) * 100)
                            sources_used.append('fbref_xg')
                except (ValueError, TypeError):
                    pass

        # Understat xG data
        if 'understat' in home_data and 'understat' in away_data:
            home_understat = home_data['understat']
            away_understat = away_data['understat']

            if 'team_xg' in home_understat and 'team_xg' in away_understat:
                try:
                    home_xg_avg = float(home_understat['team_xg'].get('xG_avg', 0))
                    away_xg_avg = float(away_understat['team_xg'].get('xG_avg', 0))

                    if home_xg_avg > 0 and away_xg_avg > 0:
                        total_xg = home_xg_avg + away_xg_avg
                        home_win_probs.append((home_xg_avg / total_xg) * 100)
                        away_win_probs.append((away_xg_avg / total_xg) * 100)
                        sources_used.append('understat_xg')
                except (ValueError, TypeError):
                    pass

        # ClubElo ratings
        if 'clubelo' in home_data and 'clubelo' in away_data:
            home_elo_data = home_data['clubelo']
            away_elo_data = away_data['clubelo']

            if 'elo_rating' in home_elo_data and 'elo_rating' in away_elo_data:
                try:
                    home_elo = float(home_elo_data['elo_rating'])
                    away_elo = float(away_elo_data['elo_rating'])

                    # Convert Elo to win probability
                    elo_diff = home_elo - away_elo
                    home_win_prob = 1 / (1 + 10 ** (-elo_diff / 400))
                    home_win_probs.append(home_win_prob * 100)
                    away_win_probs.append((1 - home_win_prob) * 100)
                    sources_used.append('clubelo')
                except (ValueError, TypeError, KeyError):
                    pass

        # If we have some data, calculate averages
        if home_win_probs and away_win_probs:
            avg_home = sum(home_win_probs) / len(home_win_probs)
            avg_away = sum(away_win_probs) / len(away_win_probs)

            # Estimate draw probability (typically 25-30% in soccer)
            # Use remaining probability space, but cap at reasonable range
            total_win_prob = avg_home + avg_away
            if total_win_prob < 100:
                draw_prob = 100 - total_win_prob
                # Cap draw probability at 35%
                if draw_prob > 35:
                    excess = draw_prob - 35
                    draw_prob = 35
                    avg_home += excess / 2
                    avg_away += excess / 2
            else:
                # If win probs sum to >100, assume 25% draw and normalize
                draw_prob = 25
                total_with_draw = total_win_prob + draw_prob
                avg_home = (avg_home / total_with_draw) * 100
                avg_away = (avg_away / total_with_draw) * 100
                draw_prob = 25

            return {
                'raw_casa': round(avg_home, 2),
                'raw_vis': round(avg_away, 2),
                'p_empate': round(draw_prob, 2),
                'sources_used': len(sources_used),
                'sources': sources_used
            }

        # Fallback: use basic form-based estimation
        return self._estimate_from_form(match_data)

    def _estimate_from_form(self, match_data: Dict) -> Dict:
        """Estimate probabilities from team form if no other data available"""

        # Try to get form from FBref or other sources
        home_form = 50  # Default neutral
        away_form = 50

        if 'fbref' in match_data and match_data['fbref'].get('success'):
            fbref = match_data['fbref']
            if 'season_stats' in fbref:
                home_stats = fbref['season_stats'].get('home', {})
                away_stats = fbref['season_stats'].get('away', {})

                # Use points per game as form indicator
                home_ppg = home_stats.get('points_per_game', 1.5)
                away_ppg = away_stats.get('points_per_game', 1.5)

                total_ppg = home_ppg + away_ppg
                if total_ppg > 0:
                    home_form = (home_ppg / total_ppg) * 100
                    away_form = (away_ppg / total_ppg) * 100

        # Assume 25% draw probability
        draw_prob = 25

        # Normalize to 100%
        total = home_form + away_form + draw_prob
        home_form = (home_form / total) * 100
        away_form = (away_form / total) * 100
        draw_prob = 25

        return {
            'raw_casa': round(home_form, 2),
            'raw_vis': round(away_form, 2),
            'p_empate': round(draw_prob, 2),
            'sources_used': 0,
            'estimated': True
        }

    def process_match_file(self, match_file: Path) -> Dict:
        """Process a single match file and calculate AH lines"""

        print(f"\n{'='*80}")
        print(f"Processing: {match_file.name}")
        print('='*80)

        # Load match data
        with open(match_file, 'r', encoding='utf-8') as f:
            match_data = json.load(f)

        # Extract match info
        match_info = match_data.get('match_info', {})
        home_team = match_info.get('home_team', 'Unknown')
        away_team = match_info.get('away_team', 'Unknown')
        league = match_info.get('league', 'Unknown')

        # Count total sources
        home_sources = match_data.get('home_team_data', {}).get('sources_available', [])
        away_sources = match_data.get('away_team_data', {}).get('sources_available', [])
        total_sources = len(set(home_sources + away_sources))

        print(f"\n📊 Match: {home_team} vs {away_team}")
        print(f"   League: {league}")
        print(f"   Sources: {total_sources}")

        # Extract probabilities
        probs = self.extract_probabilities_from_match(match_data)

        print(f"\n🎲 Raw Probabilities:")
        print(f"   Home Win: {probs['raw_casa']}%")
        print(f"   Away Win: {probs['raw_vis']}%")
        print(f"   Draw: {probs['p_empate']}%")
        print(f"   (Based on {probs['sources_used']} probability sources)")

        # Normalize probabilities
        adj_casa, adj_vis = self.normalize_probabilities(
            probs['raw_casa'],
            probs['raw_vis'],
            probs['p_empate']
        )

        print(f"\n✅ Normalized Probabilities:")
        print(f"   Home Win: {adj_casa:.2f}%")
        print(f"   Away Win: {adj_vis:.2f}%")
        print(f"   Draw: {probs['p_empate']:.2f}%")
        print(f"   Total: {adj_casa + adj_vis + probs['p_empate']:.2f}%")

        # Calculate AH lines
        ah_result = self.calculate_ah_fair_line(adj_casa, adj_vis, probs['p_empate'])

        print(f"\n🎯 Asian Handicap Analysis:")
        print(f"   Favorite: {ah_result['favorite_side']} ({ah_result['favorite_prob']}%)")
        print(f"   Underdog: {ah_result['underdog_prob']}%")
        print(f"\n   Fair AH Line: {ah_result['fair_line']:+.2f} @ {ah_result['fair_odd']}")
        print(f"   Money Line Odd: {ah_result['odd_ml']:.2f}")
        print(f"   +0.5 AH Odd: {ah_result['odd_plus_0_5']:.2f}")

        # Show key AH lines around fair value
        print(f"\n📈 Key AH Lines:")
        fair_idx = next(i for i, line in enumerate(ah_result['all_lines']) if line['line'] == ah_result['fair_line'])
        start_idx = max(0, fair_idx - 3)
        end_idx = min(len(ah_result['all_lines']), fair_idx + 4)

        for line in ah_result['all_lines'][start_idx:end_idx]:
            marker = " ⭐ FAIR" if line['line'] == ah_result['fair_line'] else ""
            print(f"   {line['line']:+.2f}: {line['odd']:.2f}{marker}")

        # Compile result
        result = {
            'timestamp': datetime.now().isoformat(),
            'match': {
                'home': home_team,
                'away': away_team,
                'league': league,
                'sources': total_sources
            },
            'probabilities': {
                'raw': probs,
                'normalized': {
                    'home_win': round(adj_casa, 2),
                    'away_win': round(adj_vis, 2),
                    'draw': round(probs['p_empate'], 2)
                }
            },
            'ah_analysis': ah_result,
            'source_file': str(match_file.name)
        }

        return result

    def process_all_matches(self) -> List[Dict]:
        """Process all high-quality matches"""

        print("\n" + "="*80)
        print("YUDOR BETTING SYSTEM - ASIAN HANDICAP CALCULATOR")
        print("="*80)
        print(f"\n📂 Loading high-quality matches from: {self.high_quality_dir}")

        # Find all match files
        match_files = list(self.high_quality_dir.glob('match_analysis_*.json'))

        if not match_files:
            print("\n❌ No high-quality matches found!")
            print(f"   Expected location: {self.high_quality_dir}")
            return []

        print(f"✅ Found {len(match_files)} high-quality matches\n")

        results = []

        for idx, match_file in enumerate(match_files, 1):
            try:
                result = self.process_match_file(match_file)
                results.append(result)

                # Save individual result
                output_file = self.output_dir / f"ah_{match_file.stem}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)

                print(f"\n💾 Saved to: {output_file.name}")

            except Exception as e:
                print(f"\n❌ ERROR processing {match_file.name}: {e}")
                import traceback
                traceback.print_exc()

        # Generate summary report
        if results:
            self._generate_summary_report(results)

        return results

    def _generate_summary_report(self, results: List[Dict]):
        """Generate summary report for all matches"""

        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_matches': len(results),
            'matches': []
        }

        print("\n\n" + "="*80)
        print("SUMMARY - ALL AH LINE CALCULATIONS")
        print("="*80 + "\n")

        for result in results:
            match_info = result['match']
            ah = result['ah_analysis']

            print(f"🎯 {match_info['home']} vs {match_info['away']}")
            print(f"   League: {match_info['league']} | Sources: {match_info['sources']}")
            print(f"   Fair Line: {ah['fair_line']:+.2f} @ {ah['fair_odd']} ({ah['favorite_side']})")
            print(f"   Probabilities: H{result['probabilities']['normalized']['home_win']}% / "
                  f"D{result['probabilities']['normalized']['draw']}% / "
                  f"A{result['probabilities']['normalized']['away_win']}%")
            print()

            summary['matches'].append({
                'match': f"{match_info['home']} vs {match_info['away']}",
                'league': match_info['league'],
                'fair_line': ah['fair_line'],
                'fair_odd': ah['fair_odd'],
                'favorite': ah['favorite_side']
            })

        # Save summary
        summary_file = self.output_dir / f"ah_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print("="*80)
        print(f"📊 Processed {len(results)} matches")
        print(f"💾 Summary saved to: {summary_file}")
        print("="*80 + "\n")


def main():
    """Main execution"""
    calculator = SimpleAHCalculator()
    results = calculator.process_all_matches()

    if results:
        print(f"\n✅ SUCCESS: Calculated AH lines for {len(results)} matches")
        print(f"📂 Results saved to: {calculator.output_dir}")
        return 0
    else:
        print("\n❌ FAILED: No matches processed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
