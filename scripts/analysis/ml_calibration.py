#!/usr/bin/env python3
"""
ML Calibration - Machine learning analysis after 30+ losses
Proposes statistically significant changes to improve win rate
"""

import json
import os
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
from scipy import stats
import numpy as np

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
LEDGER_FILE = BASE_DIR / "loss_ledger.json"
RESULTS_FILE = BASE_DIR / "match_results.json"
CALIBRATION_DIR = BASE_DIR / "calibration_reports"

ML_CALIBRATION_PROMPT = """You are a statistical analyst tasked with improving a sports betting system.

# YOUR TASK
Analyze the loss patterns and match results to propose STATISTICALLY SIGNIFICANT changes.

# IMPORTANT CONSTRAINTS
1. **Minimum Sample Size**: Only propose changes if sample size ≥ 100 total matches
2. **Statistical Significance**: Changes must have p-value < 0.05
3. **Practical Significance**: Changes must not reduce bet volume below 50 matches/month
4. **Conservative Approach**: When in doubt, don't change

# DATA PROVIDED

## Loss Ledger Summary
{loss_ledger_summary}

## Match Results Statistics
{match_results_stats}

## Detailed Loss Patterns
{loss_patterns}

# ANALYSIS CATEGORIES

## 1. Q-SCORE RECALIBRATION
Identify Q-scores (Q1-Q19) that are systematically overestimated:
- Which Q-scores appear in >50% of losses?
- Is there statistical significance (chi-square test)?
- What weight adjustment would improve accuracy?

## 2. RISK THRESHOLD ADJUSTMENT
Analyze R-Score performance:
- Current thresholds: CORE R < 0.15, EXP 0.15-0.25
- Are losses clustered near threshold boundaries?
- Would stricter thresholds improve win rate significantly?

## 3. CS THRESHOLD TUNING
Analyze Confidence Score performance:
- Current threshold: CS ≥ 70 for CORE
- Is there a CS range with significantly better/worse performance?
- Should threshold be raised to CS ≥ 75 or higher?

## 4. DATA SOURCE VALUE ASSESSMENT
Evaluate impact of different data sources:
- Local news vs no local news
- SportsMole lineups vs no lineups
- Is the difference statistically significant?

## 5. TIER SYSTEM VALIDATION
Check if Tier 1/2/3 accurately predicts success:
- Win rate by tier
- Should tier definitions be adjusted?

# STATISTICAL TESTS TO PERFORM

1. **Chi-Square Test**: For categorical variables (Q-score presence, data source availability)
2. **T-Test**: For continuous variables (R-Score, CS differences between wins/losses)
3. **Sample Size Check**: Ensure n ≥ 30 for each proposed change
4. **Effect Size**: Calculate Cohen's d or similar to ensure practical significance

# OUTPUT FORMAT

Return a JSON object with this structure:

```json
{{
  "analysis_date": "2025-11-21",
  "sample_size": {{
    "total_matches": 120,
    "total_losses": 35,
    "total_wins": 75,
    "sufficient_for_ml": true
  }},
  "statistically_significant_findings": [
    {{
      "finding_id": "Q9_OVERWEIGHT",
      "category": "Q_SCORE_RECALIBRATION",
      "description": "Q9 (Lineups) systematically overestimated",
      "evidence": {{
        "present_in_losses_pct": 63,
        "present_in_wins_pct": 35,
        "chi_square_p_value": 0.01,
        "sample_size_losses": 22,
        "sample_size_wins": 26
      }},
      "current_state": "Q9 can boost CS by up to +15",
      "proposed_change": "Cap Q9 influence at +5 CS maximum",
      "expected_impact": {{
        "win_rate_change": "+3-4%",
        "bet_volume_change": "-5%",
        "confidence_level": "high"
      }},
      "recommendation": "IMPLEMENT",
      "reasoning": "Statistically significant (p=0.01), large effect size, minimal volume impact"
    }}
  ],
  "rejected_proposals": [
    {{
      "finding_id": "CS_THRESHOLD_RAISE",
      "category": "CS_THRESHOLD_TUNING",
      "description": "Raising CS threshold to 75",
      "p_value": 0.18,
      "reason_rejected": "Not statistically significant (p > 0.05)",
      "sample_size": 12
    }}
  ],
  "overall_recommendations": {{
    "implement_count": 3,
    "monitor_count": 2,
    "reject_count": 4,
    "expected_win_rate_improvement": "+5-7%",
    "expected_volume_impact": "-10-15%",
    "net_roi_improvement": "+8-12%"
  }},
  "next_steps": [
    "Implement proposals: Q9_OVERWEIGHT, R_THRESHOLD_TIGHTEN, LOCAL_NEWS_BOOST",
    "Monitor for 50 matches",
    "Revert if win rate drops below current baseline",
    "Re-calibrate after 100 additional matches"
  ]
}}
```

Be extremely conservative. Only propose changes with strong statistical evidence.
Reject changes that would reduce sample size too much or lack statistical significance.
"""

def load_ledger():
    """Load loss ledger"""
    if not LEDGER_FILE.exists():
        return None

    with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_results():
    """Load match results"""
    if not RESULTS_FILE.exists():
        return None

    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_loss_patterns(ledger):
    """Analyze patterns in loss ledger"""

    losses = ledger.get("losses", [])

    # Count by category
    categories = {}
    q_scores_in_losses = {}
    risk_signals_in_losses = {}
    cs_deltas = []
    r_deltas = []

    for loss in losses:
        analysis = loss["analysis"]

        # Category
        cat = analysis["loss_category"]
        categories[cat] = categories.get(cat, 0) + 1

        # Q-scores
        for q in analysis.get("q_scores_overestimated", []):
            q_scores_in_losses[q] = q_scores_in_losses.get(q, 0) + 1

        # Risk signals
        for sig in analysis.get("risk_signals_missed", []):
            risk_signals_in_losses[sig] = risk_signals_in_losses.get(sig, 0) + 1

        # Deltas
        cs_deltas.append(analysis.get("cs_delta", 0))
        r_deltas.append(analysis.get("r_score_delta", 0))

    return {
        "total_losses": len(losses),
        "by_category": categories,
        "q_scores_overestimated": q_scores_in_losses,
        "risk_signals_missed": risk_signals_in_losses,
        "avg_cs_delta": sum(cs_deltas) / len(cs_deltas) if cs_deltas else 0,
        "avg_r_delta": sum(r_deltas) / len(r_deltas) if r_deltas else 0
    }

def run_calibration():
    """Main ML calibration function"""

    print("="*80)
    print("🤖 ML CALIBRATION ANALYSIS")
    print("="*80)
    print()

    # Load data
    print("📂 Loading data...")
    ledger = load_ledger()
    results = load_results()

    if not ledger:
        print("❌ Error: No loss ledger found. Run loss_ledger.py first.")
        return

    if not results:
        print("❌ Error: No match results found. Run post_match_analysis.py first.")
        return

    # Check minimum sample size
    total_matches = results["statistics"]["total_matches"]
    total_losses = ledger["summary"]["total_losses"]

    print(f"   Total Matches: {total_matches}")
    print(f"   Total Losses: {total_losses}")
    print()

    if total_matches < 100:
        print("⚠️  WARNING: Sample size too small for ML calibration")
        print(f"   Current: {total_matches} matches")
        print(f"   Required: ≥100 matches")
        print()
        print("   Continue with caution. Results may not be statistically reliable.")
        print()

        response = input("Continue anyway? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return

    if total_losses < 30:
        print("⚠️  WARNING: Too few losses for reliable analysis")
        print(f"   Current: {total_losses} losses")
        print(f"   Recommended: ≥30 losses")
        print()

        response = input("Continue anyway? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return

    # Analyze loss patterns
    print("🔍 Analyzing loss patterns...")
    loss_patterns = analyze_loss_patterns(ledger)
    print(f"   ✅ Analyzed {loss_patterns['total_losses']} losses")
    print()

    # Prepare data for Claude
    loss_ledger_summary = json.dumps(ledger["summary"], indent=2)
    match_results_stats = json.dumps(results["statistics"], indent=2)
    loss_patterns_json = json.dumps(loss_patterns, indent=2)

    prompt = ML_CALIBRATION_PROMPT.format(
        loss_ledger_summary=loss_ledger_summary,
        match_results_stats=match_results_stats,
        loss_patterns=loss_patterns_json
    )

    # Call Claude for ML analysis
    print("🤖 Running machine learning calibration analysis...")
    print("   This may take 30-60 seconds...")
    print()

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        temperature=0,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    # Parse response
    response_text = response.content[0].text

    # Extract JSON
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        json_text = response_text[json_start:json_end].strip()
    else:
        json_text = response_text

    calibration = json.loads(json_text)

    # Save calibration report
    CALIBRATION_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = CALIBRATION_DIR / f"calibration_{timestamp}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(calibration, f, indent=2, ensure_ascii=False)

    # Print report
    print_calibration_report(calibration)

    print(f"📄 Full report saved to: {report_file}")
    print()

def print_calibration_report(cal):
    """Print calibration report in readable format"""

    print()
    print("="*80)
    print("📊 ML CALIBRATION REPORT")
    print("="*80)
    print()

    # Sample size
    sample = cal["sample_size"]
    print(f"Sample Size: {sample['total_matches']} matches ({sample['total_wins']} wins, {sample['total_losses']} losses)")
    print(f"Sufficient for ML: {'✅ Yes' if sample['sufficient_for_ml'] else '❌ No'}")
    print()

    # Statistically significant findings
    findings = cal["statistically_significant_findings"]

    if findings:
        print("-"*80)
        print(f"✅ STATISTICALLY SIGNIFICANT FINDINGS ({len(findings)})")
        print("-"*80)
        print()

        for i, finding in enumerate(findings, 1):
            print(f"{i}. {finding['finding_id']} ({finding['category']})")
            print(f"   Description: {finding['description']}")
            print()
            print(f"   Evidence:")
            evidence = finding["evidence"]
            for key, value in evidence.items():
                print(f"      • {key}: {value}")
            print()
            print(f"   Current State: {finding['current_state']}")
            print(f"   Proposed Change: {finding['proposed_change']}")
            print()
            print(f"   Expected Impact:")
            impact = finding["expected_impact"]
            print(f"      • Win Rate: {impact['win_rate_change']}")
            print(f"      • Bet Volume: {impact['bet_volume_change']}")
            print(f"      • Confidence: {impact['confidence_level']}")
            print()
            print(f"   ✅ Recommendation: {finding['recommendation']}")
            print(f"   Reasoning: {finding['reasoning']}")
            print()

    # Rejected proposals
    rejected = cal["rejected_proposals"]

    if rejected:
        print("-"*80)
        print(f"❌ REJECTED PROPOSALS ({len(rejected)})")
        print("-"*80)
        print()

        for i, reject in enumerate(rejected, 1):
            print(f"{i}. {reject['finding_id']} ({reject['category']})")
            print(f"   Description: {reject['description']}")
            print(f"   P-Value: {reject['p_value']}")
            print(f"   Reason: {reject['reason_rejected']}")
            print()

    # Overall recommendations
    print("-"*80)
    print("🎯 OVERALL RECOMMENDATIONS")
    print("-"*80)
    print()

    recs = cal["overall_recommendations"]
    print(f"   Implement: {recs['implement_count']} proposals")
    print(f"   Monitor: {recs['monitor_count']} proposals")
    print(f"   Reject: {recs['reject_count']} proposals")
    print()
    print(f"   Expected Win Rate Improvement: {recs['expected_win_rate_improvement']}")
    print(f"   Expected Volume Impact: {recs['expected_volume_impact']}")
    print(f"   Net ROI Improvement: {recs['net_roi_improvement']}")
    print()

    # Next steps
    print("-"*80)
    print("📋 NEXT STEPS")
    print("-"*80)
    print()

    for i, step in enumerate(cal["next_steps"], 1):
        print(f"   {i}. {step}")

    print()
    print("="*80)

if __name__ == "__main__":
    run_calibration()
