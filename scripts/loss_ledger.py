#!/usr/bin/env python3
"""
Loss Ledger - Manual logging and analysis of betting losses
Analyzes what went wrong and categorizes the loss type
"""

import json
import os
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
ANALYSIS_DIR = BASE_DIR / "analysis_history"
LEDGER_FILE = BASE_DIR / "loss_ledger.json"

LOSS_LEDGER_PROMPT = """You are analyzing a betting loss to understand what went wrong.

# YOUR TASK
Analyze this match result and betting loss to identify:
1. What was overestimated in the analysis
2. Which Q-scores (Q1-Q19) gave false confidence
3. Whether risk signals were missed
4. What could have been done differently

# MATCH DATA
{match_data}

# ACTUAL RESULT
- Final Score: {final_score}
- Bet Placed: {bet_placed}
- AH Line: {ah_line}
- Loss Type: {loss_type} (full loss = -1.0 unit, half loss = -0.5 unit)

# ANALYSIS CATEGORIES
Classify this loss into ONE primary category:

1. **BAD_LUCK**: Loss was within expected variance
   - Lost by 1 goal on tight AH line (-0.25, -0.5)
   - All analysis was correct, just unlucky outcome
   - Example: Bet -0.5, lost 0-1 (extremely close)

2. **RISK_SIGNAL_MISSED**: R-Score was too optimistic
   - Actual risk was higher than calculated
   - Specific risk signals (injuries, fatigue, etc.) were underweighted
   - Should have been VETO

3. **Q_SCORE_OVERWEIGHT**: Specific Q-scores were overestimated
   - Q5 (Technique) overestimated team quality
   - Q9 (Lineups) gave false confidence
   - Q10 (Local News) missed key context
   - CS_final was inflated

4. **DATA_QUALITY_ISSUE**: Missing critical information
   - Late lineup changes not captured
   - Key injury news missed
   - Weather/pitch conditions not considered

5. **MARKET_WAS_RIGHT**: Our fair line was significantly wrong
   - Market AH was more accurate than Yudor AH
   - Fundamental pricing error in Q1-Q19 calculation
   - AH calculation methodology issue

# OUTPUT FORMAT
Return a JSON object with this structure:
```json
{{
  "loss_category": "BAD_LUCK|RISK_SIGNAL_MISSED|Q_SCORE_OVERWEIGHT|DATA_QUALITY_ISSUE|MARKET_WAS_RIGHT",
  "primary_issue": "Brief description of main issue",
  "q_scores_overestimated": ["Q5", "Q9"],  // List which Q-scores were too optimistic
  "risk_signals_missed": ["Key injury", "Fatigue"],  // List what risk signals were missed
  "cs_delta": -15,  // How much CS should have been lower (negative number)
  "r_score_delta": +0.08,  // How much R-Score should have been higher (positive number)
  "market_accuracy": {{
    "market_ah": -0.75,
    "yudor_ah": -1.25,
    "market_was_closer": true
  }},
  "what_was_overestimated": "Detailed explanation of what was overestimated",
  "lesson_learned": "Specific lesson for future matches",
  "proposed_adjustment": "What could be changed to avoid this in future"
}}
```

Be brutally honest. The goal is to improve the system, not to justify the bet.
"""

def load_match_analysis(match_id):
    """Load the original analysis for this match"""
    analysis_file = ANALYSIS_DIR / f"{match_id}_analysis.json"

    if not analysis_file.exists():
        raise FileNotFoundError(f"Analysis file not found: {analysis_file}")

    with open(analysis_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_ledger():
    """Load existing loss ledger"""
    if LEDGER_FILE.exists():
        with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"losses": [], "summary": {}}

def save_ledger(ledger):
    """Save loss ledger"""
    with open(LEDGER_FILE, 'w', encoding='utf-8') as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)

def analyze_loss(match_id, final_score, bet_placed, ah_line, loss_type):
    """
    Analyze a betting loss using Claude

    Args:
        match_id: Match identifier (e.g., "BarcelonavsAthleticClub_22112025")
        final_score: Final score (e.g., "2-1")
        bet_placed: Which side was bet (e.g., "Barcelona -1.0")
        ah_line: The AH line bet (e.g., -1.0)
        loss_type: "full" or "half"
    """

    print("="*80)
    print("📉 LOSS LEDGER ANALYSIS")
    print("="*80)
    print()

    # Load match analysis
    print(f"📂 Loading analysis for: {match_id}")
    analysis = load_match_analysis(match_id)

    match_info = analysis.get("match_info", {})
    yudor_analysis = analysis.get("yudor_analysis", {})
    consolidated = analysis.get("consolidated_data", {})

    print(f"   Match: {match_info.get('home')} vs {match_info.get('away')}")
    print(f"   Date: {match_info.get('date')}")
    print(f"   Result: {final_score}")
    print(f"   Bet: {bet_placed}")
    print(f"   Loss: {loss_type}")
    print()

    # Prepare data for Claude
    match_data = {
        "match_info": match_info,
        "yudor_analysis": yudor_analysis,
        "q_scores": consolidated.get("layer1_pricing", {}),
        "data_quality": consolidated.get("data_quality", {})
    }

    loss_units = -1.0 if loss_type == "full" else -0.5

    prompt = LOSS_LEDGER_PROMPT.format(
        match_data=json.dumps(match_data, indent=2),
        final_score=final_score,
        bet_placed=bet_placed,
        ah_line=ah_line,
        loss_type=f"{loss_type} loss ({loss_units} units)"
    )

    # Call Claude for analysis
    print("🤖 Calling Claude for loss analysis...")
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        temperature=0,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    # Parse response
    response_text = response.content[0].text

    # Extract JSON from response
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        json_text = response_text[json_start:json_end].strip()
    else:
        json_text = response_text

    loss_analysis = json.loads(json_text)

    # Add metadata
    loss_entry = {
        "timestamp": datetime.now().isoformat(),
        "match_id": match_id,
        "match_info": match_info,
        "final_score": final_score,
        "bet_placed": bet_placed,
        "ah_line": ah_line,
        "loss_type": loss_type,
        "loss_units": loss_units,
        "yudor_decision": yudor_analysis.get("decision"),
        "yudor_ah_fair": yudor_analysis.get("yudor_ah_fair"),
        "cs_final": yudor_analysis.get("cs_final"),
        "r_score": yudor_analysis.get("r_score"),
        "tier": yudor_analysis.get("tier"),
        "analysis": loss_analysis
    }

    # Load ledger and add entry
    ledger = load_ledger()
    ledger["losses"].append(loss_entry)

    # Update summary stats
    total_losses = len(ledger["losses"])
    total_units_lost = sum(l["loss_units"] for l in ledger["losses"])

    categories = {}
    for loss in ledger["losses"]:
        cat = loss["analysis"]["loss_category"]
        categories[cat] = categories.get(cat, 0) + 1

    ledger["summary"] = {
        "total_losses": total_losses,
        "total_units_lost": total_units_lost,
        "by_category": categories,
        "last_updated": datetime.now().isoformat()
    }

    save_ledger(ledger)

    # Print results
    print()
    print("="*80)
    print("📊 LOSS ANALYSIS COMPLETE")
    print("="*80)
    print()
    print(f"Category: {loss_analysis['loss_category']}")
    print(f"Primary Issue: {loss_analysis['primary_issue']}")
    print()
    print(f"Q-Scores Overestimated: {', '.join(loss_analysis['q_scores_overestimated']) if loss_analysis['q_scores_overestimated'] else 'None'}")
    print(f"Risk Signals Missed: {', '.join(loss_analysis['risk_signals_missed']) if loss_analysis['risk_signals_missed'] else 'None'}")
    print()
    print(f"CS Delta: {loss_analysis['cs_delta']:+d} (CS should have been {yudor_analysis.get('cs_final', 0) + loss_analysis['cs_delta']})")
    print(f"R-Score Delta: {loss_analysis['r_score_delta']:+.2f} (R should have been {yudor_analysis.get('r_score', 0) + loss_analysis['r_score_delta']:.2f})")
    print()
    print("Market Accuracy:")
    print(f"   Market AH: {loss_analysis['market_accuracy']['market_ah']}")
    print(f"   Yudor AH: {loss_analysis['market_accuracy']['yudor_ah']}")
    print(f"   Market was closer: {loss_analysis['market_accuracy']['market_was_closer']}")
    print()
    print("What Was Overestimated:")
    print(f"   {loss_analysis['what_was_overestimated']}")
    print()
    print("Lesson Learned:")
    print(f"   {loss_analysis['lesson_learned']}")
    print()
    print("Proposed Adjustment:")
    print(f"   {loss_analysis['proposed_adjustment']}")
    print()
    print("="*80)
    print("📋 LEDGER SUMMARY")
    print("="*80)
    print(f"Total Losses: {total_losses}")
    print(f"Total Units Lost: {total_units_lost:.2f}")
    print()
    print("By Category:")
    for cat, count in categories.items():
        pct = (count / total_losses) * 100
        print(f"   {cat}: {count} ({pct:.1f}%)")
    print()
    print(f"✅ Loss logged to: {LEDGER_FILE}")
    print()

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 6:
        print("Usage: python3 scripts/loss_ledger.py <match_id> <final_score> <bet_placed> <ah_line> <loss_type>")
        print()
        print("Examples:")
        print('  python3 scripts/loss_ledger.py "BarcelonavsAthleticClub_22112025" "2-1" "Barcelona -1.0" -1.0 full')
        print('  python3 scripts/loss_ledger.py "LiverpoolvsChelsea_23112025" "1-1" "Liverpool -0.25" -0.25 half')
        print()
        print("loss_type: 'full' (lost 1.0 unit) or 'half' (lost 0.5 unit)")
        sys.exit(1)

    match_id = sys.argv[1]
    final_score = sys.argv[2]
    bet_placed = sys.argv[3]
    ah_line = float(sys.argv[4])
    loss_type = sys.argv[5]

    analyze_loss(match_id, final_score, bet_placed, ah_line, loss_type)
