#!/usr/bin/env python3
"""
Process existing match_data_v29.json and create matches_priority.txt
This bypasses the scraping step and goes directly to data quality analysis.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from master_orchestrator import YudorOrchestrator

def main():
    orchestrator = YudorOrchestrator()

    print("\n" + "="*80)
    print("🎯 PROCESSING EXISTING SCRAPE DATA")
    print("="*80)

    # Load scraped data
    scraped_data_file = orchestrator.config.BASE_DIR / "match_data_v29.json"
    if not scraped_data_file.exists():
        print(f"❌ Scraper output not found: {scraped_data_file}")
        sys.exit(1)

    with open(scraped_data_file, encoding="utf-8") as f:
        scraped_data = json.load(f)

    print(f"✅ Loaded {len(scraped_data)} games from match_data_v29.json")

    # Step 2: Calculate data quality for each game
    print("\n" + "-"*80)
    print("📊 CALCULATING DATA QUALITY SCORES")
    print("-"*80)

    # Load DATA_CONSOLIDATION_PROMPT
    data_consolidation_prompt = orchestrator.load_prompt("DATA_CONSOLIDATION_PROMPT_v1.0.md")

    quality_results = []

    for idx, (match_id, match_data) in enumerate(scraped_data.items(), 1):
        print(f"\n[{idx}/{len(scraped_data)}] Analyzing: {match_id}")

        try:
            # Call Claude for data quality calculation
            user_message = f"""
Calculate data quality score for this match.

Match Data:
{json.dumps(match_data, indent=2)}

Return ONLY the data_quality section as JSON:
{{
  "data_quality": {{
    "score": 85,
    "assessment": "Excellent",
    "proceed": true
  }}
}}
"""

            response = orchestrator.call_claude(
                data_consolidation_prompt,
                user_message,
                max_tokens=2000
            )

            # Extract JSON from response
            data_quality_json = orchestrator.extract_json_from_response(response)

            # Get quality score
            quality_score = data_quality_json.get("data_quality", {}).get("score", 0)
            assessment = data_quality_json.get("data_quality", {}).get("assessment", "Unknown")
            proceed = data_quality_json.get("data_quality", {}).get("proceed", False)

            print(f"   Quality Score: {quality_score}/100 ({assessment})")

            quality_results.append({
                "match_id": match_id,
                "match_info": match_data["match_info"],
                "quality_score": quality_score,
                "assessment": assessment,
                "proceed": proceed,
                "urls": match_data["urls"]
            })

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            quality_results.append({
                "match_id": match_id,
                "match_info": match_data["match_info"],
                "quality_score": 0,
                "assessment": "Error",
                "proceed": False,
                "urls": match_data.get("urls", {})
            })

    # Step 3: Filter by threshold
    print("\n" + "-"*80)
    print("🎯 STEP 3: FILTERING BY QUALITY THRESHOLD")
    print("-"*80)

    threshold = orchestrator.config.DATA_QUALITY_THRESHOLD
    priority_games = [g for g in quality_results if g["quality_score"] >= threshold]

    print(f"✅ {len(priority_games)}/{len(quality_results)} games meet threshold (≥{threshold})")

    # Step 4: Create matches_priority.txt
    print("\n" + "-"*80)
    print("📝 STEP 4: CREATING PRIORITY MATCHES FILE")
    print("-"*80)

    priority_file = orchestrator.config.BASE_DIR / "matches_priority.txt"

    if priority_games:
        with open(priority_file, "w", encoding="utf-8") as f:
            for game in priority_games:
                m = game["match_info"]
                line = f"{m['home']} vs {m['away']}, {m['league']}, {m['date']}"
                f.write(line + "\n")

        print(f"✅ Created {priority_file} with {len(priority_games)} priority games")
        print("\n📋 Priority Games:")
        for game in priority_games:
            m = game["match_info"]
            print(f"   • {m['home']} vs {m['away']} ({m['league']}) - Score: {game['quality_score']}")
    else:
        print("⚠️  No games met the quality threshold")
        print(f"💡 Consider lowering threshold (current: {threshold})")
        print("\n📊 Score Distribution:")
        scores = sorted([g["quality_score"] for g in quality_results], reverse=True)
        print(f"   Highest: {scores[0]}")
        print(f"   Top 5: {scores[:5]}")
        print(f"   Median: {scores[len(scores)//2]}")

    # Step 5: Save pre-filter history
    print("\n" + "-"*80)
    print("💾 STEP 5: SAVING PRE-FILTER HISTORY")
    print("-"*80)

    orchestrator.config.PRE_FILTER_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_file = orchestrator.config.PRE_FILTER_DIR / f"pre_filter_{timestamp}.json"

    history_data = {
        "timestamp": datetime.now().isoformat(),
        "input_file": "match_data_v29.json",
        "total_games": len(scraped_data),
        "scraped_games": len(scraped_data),
        "threshold": threshold,
        "priority_games": len(priority_games),
        "filtered_out": len(quality_results) - len(priority_games),
        "results": quality_results
    }

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved history to {history_file}")

    # Summary
    print("\n" + "="*80)
    print("✅ PRE-FILTER COMPLETE")
    print("="*80)
    print(f"📊 Total Games Analyzed: {len(scraped_data)}")
    print(f"🎯 Priority Games: {len(priority_games)}")
    print(f"📝 Priority File: {priority_file}")
    print(f"💾 History: {history_file}")

    if priority_games:
        print(f"\n▶️  Next Step: Run analysis on priority games")
        print(f"   python3 scripts/master_orchestrator.py analyze-batch")
    else:
        print(f"\n⚠️  No priority games found. Review quality scores in history file.")

if __name__ == "__main__":
    main()
