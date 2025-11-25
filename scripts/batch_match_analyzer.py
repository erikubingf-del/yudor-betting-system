#!/usr/bin/env python3
"""
YUDOR Betting System - Automated Batch Match Analyzer

Complete automation: reads match list, processes all matches, generates reports.
No manual intervention required. MASTER ORCHESTRATOR pattern.

WORKFLOW:
1. Analyzes ALL matches from CSV
2. Saves ALL matches to organized folders:
   - high_quality/ (5+ sources) - Ready for AI predictions
   - low_quality/ (<5 sources) - Saved for learning and analysis
3. Generates batch summary in batch_summaries/

This ensures you can learn from ALL matches, not just perfect ones!

Usage:
    python3 scripts/batch_match_analyzer.py matches.csv

CSV Format:
    Date,League,Home,Away,Stadium
    24/11,Premier League,Manchester United,Everton,Old Trafford
    24/11,La Liga,Espanyol,Sevilla,Stage Front Stadium
"""
import sys
sys.path.insert(0, '/tmp/soccerdata')

import csv
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from complete_match_analyzer import CompleteMatchAnalyzer


class BatchMatchAnalyzer:
    """Automated batch processing for multiple matches"""

    def __init__(self):
        self.results = []
        self.start_time = None

    def read_matches_from_csv(self, csv_file: str) -> List[Dict]:
        """Read matches from CSV file"""
        matches = []

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Extract data
                match = {
                    'date': row['Date'] if 'Date' in row else row['Data'],
                    'league': row['League'] if 'League' in row else row['Torneio'],
                    'home': row['Home'] if 'Home' in row else row['Jogo (Casa vs. Visitante)'].split(' vs. ')[0],
                    'away': row['Away'] if 'Away' in row else row['Jogo (Casa vs. Visitante)'].split(' vs. ')[1],
                    'stadium': row.get('Stadium', row.get('Estádio', 'Unknown'))
                }

                # Clean league name (remove emoji flags)
                match['league'] = self._clean_league_name(match['league'])

                matches.append(match)

        return matches

    def _clean_league_name(self, league: str) -> str:
        """Remove emoji flags and clean league name"""
        # Remove emoji and extra spaces
        import re
        cleaned = re.sub(r'[^\x00-\x7F]+', '', league).strip()
        return cleaned

    def process_all_matches(self, matches: List[Dict]) -> Dict:
        """Process all matches with complete automation"""
        self.start_time = time.time()

        print("\n" + "="*80)
        print("YUDOR BETTING SYSTEM - AUTOMATED BATCH PROCESSING")
        print("="*80)
        print(f"\n📊 Total matches to analyze: {len(matches)}")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print("="*80 + "\n")

        for idx, match in enumerate(matches, 1):
            print(f"\n{'='*80}")
            print(f"MATCH {idx}/{len(matches)}: {match['home']} vs {match['away']}")
            print(f"League: {match['league']} | Date: {match['date']}")
            print('='*80 + "\n")

            try:
                result = self._process_single_match(match)
                self.results.append(result)

                # Show quick summary
                if result['success']:
                    print(f"\n✅ SUCCESS: {result['sources']} sources | Quality: {result['quality']}/5.0")
                    print(f"   H2H: {result['h2h_matches']} matches | File: {result['filename']}")
                else:
                    print(f"\n⚠️  LIMITED DATA: {result['sources']} sources | Quality: {result['quality']}/5.0")

            except Exception as e:
                print(f"\n❌ ERROR: {e}")
                self.results.append({
                    'match': f"{match['home']} vs {match['away']}",
                    'league': match['league'],
                    'success': False,
                    'error': str(e),
                    'sources': 0,
                    'quality': 0.0
                })

            # Brief pause between matches to avoid overload
            if idx < len(matches):
                time.sleep(1)

        # Generate final summary
        return self._generate_summary_report()

    def _process_single_match(self, match: Dict) -> Dict:
        """Process a single match"""
        # Initialize analyzer
        analyzer = CompleteMatchAnalyzer(league=match['league'], season='2425')

        # Run analysis
        match_data = analyzer.analyze_match(match['home'], match['away'])

        # Extract key metrics
        summary = match_data['summary']
        h2h = match_data.get('head_to_head', {})

        # ALWAYS save - let complete_match_analyzer decide which folder
        filename = analyzer.save_analysis(match_data)

        # Determine success based on quality threshold (5+ sources = high quality)
        is_high_quality = summary['total_sources'] >= 5
        quality_tier = "HIGH_QUALITY" if is_high_quality else "LOW_QUALITY"

        if is_high_quality:
            print(f"\n✅ HIGH QUALITY: {summary['total_sources']} sources - saved to high_quality/")
        else:
            print(f"\n⚠️  LOW/MEDIUM QUALITY: {summary['total_sources']} sources - saved to low_quality/ (for learning)")

        return {
            'match': f"{match['home']} vs {match['away']}",
            'league': match['league'],
            'date': match['date'],
            'success': is_high_quality,  # Success = high quality
            'sources': summary['total_sources'],
            'quality': summary['overall_quality'],
            'coverage': summary['coverage_score'],
            'h2h_matches': h2h.get('total_matches', 0),
            'h2h_record': f"{h2h.get('home_wins', 0)}W {h2h.get('draws', 0)}D {h2h.get('away_wins', 0)}L",
            'filename': filename,
            'sportsmole_url': match_data.get('sportsmole_preview_url', 'NOT_FOUND'),
            'quality_tier': quality_tier
        }

    def _generate_summary_report(self) -> Dict:
        """Generate comprehensive summary report"""
        elapsed_time = time.time() - self.start_time

        # Calculate statistics
        total_matches = len(self.results)
        successful = sum(1 for r in self.results if r['success'])  # High quality (5+ sources)
        failed = total_matches - successful  # Low/Medium quality (<5 sources)

        # Calculate average quality for ALL matches
        avg_quality = sum(r['quality'] for r in self.results) / total_matches if total_matches > 0 else 0
        total_sources = sum(r['sources'] for r in self.results)  # Count ALL sources

        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_matches': total_matches,
            'successful': successful,
            'failed': failed,
            'success_rate': f"{successful/total_matches*100:.1f}%" if total_matches > 0 else "0%",
            'average_quality': round(avg_quality, 2),
            'total_sources': total_sources,
            'processing_time': f"{elapsed_time:.1f}s",
            'matches': self.results
        }

        # Print summary
        self._print_summary(summary)

        # Save summary to JSON in batch_summaries folder
        batch_summaries_folder = Path(__file__).parent.parent / 'scraped_data' / 'batch_summaries'
        batch_summaries_folder.mkdir(parents=True, exist_ok=True)
        summary_file = batch_summaries_folder / f"batch_analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Summary saved to: {summary_file}\n")

        return summary

    def _print_summary(self, summary: Dict):
        """Print formatted summary report"""
        print("\n\n" + "="*80)
        print("BATCH PROCESSING COMPLETE - FINAL SUMMARY")
        print("="*80 + "\n")

        print(f"📊 Total Matches Analyzed: {summary['total_matches']}")
        print(f"✅ High Quality (5+ sources): {summary['successful']}")
        print(f"⚠️  Low/Medium Quality (<5 sources): {summary['failed']}")
        print(f"📈 High Quality Rate: {summary['success_rate']}")
        print(f"⭐ Average Quality (All): {summary['average_quality']}/5.0")
        print(f"🔢 Total Data Sources: {summary['total_sources']}")
        print(f"⏱️  Processing Time: {summary['processing_time']}")

        print("\n" + "-"*80)
        print("HIGH QUALITY MATCHES (saved to high_quality/):")
        print("-"*80 + "\n")

        # Show high quality matches (5+ sources)
        high_quality_matches = [r for r in summary['matches'] if r['success']]
        if high_quality_matches:
            for result in high_quality_matches:
                print(f"✅ {result['match']} ({result['league']})")
                print(f"   Sources: {result['sources']} | Quality: {result['quality']}/5.0 | H2H: {result['h2h_matches']} matches")
                print(f"   File: {result['filename']}")
                print()
        else:
            print("   No high quality matches (5+ sources)\n")

        # Show low/medium quality matches
        low_quality_matches = [r for r in summary['matches'] if not r['success']]
        if low_quality_matches:
            print("-"*80)
            print("LOW/MEDIUM QUALITY MATCHES (saved to low_quality/ for learning):")
            print("-"*80 + "\n")
            for result in low_quality_matches:
                print(f"⚠️  {result['match']} ({result['league']})")
                print(f"   Sources: {result['sources']} | Quality: {result['quality']}/5.0 | H2H: {result['h2h_matches']} matches")
                print(f"   File: {result['filename']}")
                print()

        print("="*80)
        print(f"🎯 {summary['total_matches']} MATCHES ANALYZED AND SAVED!")
        print(f"   • {len(high_quality_matches)} HIGH QUALITY (ready for predictions)")
        print(f"   • {len(low_quality_matches)} LOW/MEDIUM QUALITY (saved for learning)")
        print("="*80 + "\n")


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/batch_match_analyzer.py <matches.csv>")
        print("\nCSV Format:")
        print("  Date,League,Home,Away,Stadium")
        print("  24/11,Premier League,Manchester United,Everton,Old Trafford")
        sys.exit(1)

    csv_file = sys.argv[1]

    if not Path(csv_file).exists():
        print(f"❌ Error: File '{csv_file}' not found!")
        sys.exit(1)

    # Run batch processing
    analyzer = BatchMatchAnalyzer()
    matches = analyzer.read_matches_from_csv(csv_file)
    summary = analyzer.process_all_matches(matches)

    # Exit with appropriate code
    sys.exit(0 if summary['failed'] == 0 else 1)


if __name__ == "__main__":
    main()
