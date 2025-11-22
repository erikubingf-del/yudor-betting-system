# Machine Learning & Loss Analysis System - Complete Guide

**Version**: 5.3
**Date**: November 21, 2025

---

## 🎯 Overview

This system provides **continuous improvement** through three integrated tools:

1. **Loss Ledger** - Manual logging and deep analysis of each loss
2. **Post-Match Analysis** - Automated statistics from Airtable results
3. **ML Calibration** - Statistical proposals after 30+ losses

---

## 📋 Prerequisites

### Airtable Fields Required

Add these fields to your "Match Analyses" table:

| Field Name | Type | Description |
|------------|------|-------------|
| Match Result | Text | Final score (e.g., "2-1") |
| Bet Result | Single Select | WIN, LOSS, HALF_WIN, HALF_LOSS, PUSH |
| Units Won/Lost | Number | +1.0 for win, -1.0 for loss, -0.5 for half loss |
| Market AH | Number | Market's Asian Handicap line |
| Bet Entered | Checkbox | TRUE if you actually placed this bet |

---

## 🔧 Tool 1: Loss Ledger

### Purpose
Manually log each betting loss with deep Claude-powered analysis.

### Usage

```bash
python3 scripts/loss_ledger.py <match_id> <final_score> <bet_placed> <ah_line> <loss_type>
```

### Examples

**Full Loss Example:**
```bash
python3 scripts/loss_ledger.py "BarcelonavsAthleticClub_22112025" "2-1" "Barcelona -1.0" -1.0 full
```

**Half Loss Example:**
```bash
python3 scripts/loss_ledger.py "LiverpoolvsChelsea_23112025" "1-1" "Liverpool -0.25" -0.25 half
```

### What It Does

1. **Loads** your original analysis from `analysis_history/`
2. **Calls Claude** to analyze what went wrong
3. **Categorizes** the loss:
   - **BAD_LUCK**: Within expected variance (tight loss)
   - **RISK_SIGNAL_MISSED**: R-Score was too optimistic
   - **Q_SCORE_OVERWEIGHT**: Specific Q-scores overestimated
   - **DATA_QUALITY_ISSUE**: Missing critical information
   - **MARKET_WAS_RIGHT**: Fair line was wrong

4. **Identifies**:
   - Which Q-scores (Q1-Q19) were overestimated
   - Which risk signals were missed
   - How much CS should have been lower
   - How much R-Score should have been higher
   - Whether market was more accurate

5. **Saves** to `loss_ledger.json`

### Output Example

```
================================================================================
📊 LOSS ANALYSIS COMPLETE
================================================================================

Category: Q_SCORE_OVERWEIGHT
Primary Issue: Q9 (Lineups) overestimated lineup strength despite key injuries

Q-Scores Overestimated: Q9, Q5
Risk Signals Missed: Key injury (midfielder), Fatigue from midweek match

CS Delta: -12 (CS should have been 60 instead of 72)
R-Score Delta: +0.08 (R should have been 0.30 instead of 0.22)

Market Accuracy:
   Market AH: -0.75
   Yudor AH: -1.25
   Market was closer: True

Lesson Learned:
   SportsMole lineup predictions don't always account for fitness levels.
   Cross-reference with local news for injury context.

Proposed Adjustment:
   Reduce Q9 max boost from +15 to +8 CS when injuries present
```

---

## 📊 Tool 2: Post-Match Analysis

### Purpose
Automatically fetch match results from Airtable and calculate comprehensive statistics.

### Usage

```bash
python3 scripts/post_match_analysis.py
```

### What It Does

1. **Fetches** all matches with results from Airtable
2. **Calculates** statistics:
   - Win rate by decision type (CORE, EXP, FLIP, VETO)
   - Win rate by tier (1, 2, 3)
   - ROI by decision type
   - Edge accuracy (Yudor vs Market)
   - R-Score performance

3. **Saves** to `match_results.json`

4. **Alerts** when ready for ML Calibration (≥30 losses)

### Output Example

```
================================================================================
📈 MATCH RESULTS SUMMARY
================================================================================

Total Matches: 120

--------------------------------------------------------------------------------
BY DECISION TYPE:
--------------------------------------------------------------------------------

CORE:
   Matches: 45
   Wins: 28
   Losses: 14
   Pushes: 3
   Win Rate: 66.7%
   Total Units: +12.50
   ROI: +27.8%

EXP:
   Matches: 18
   Wins: 10
   Losses: 7
   Pushes: 1
   Win Rate: 58.8%
   Total Units: +2.50
   ROI: +13.9%

FLIP:
   Matches: 2
   Wins: 1
   Losses: 1
   Win Rate: 50.0%
   Total Units: +0.00
   ROI: 0.0%

VETO:
   Matches: 55
   (Not bet - tracking only)

--------------------------------------------------------------------------------
EDGE ACCURACY (Yudor vs Market):
--------------------------------------------------------------------------------

   Matches with Market AH: 63
   Average Edge: 0.42 AH points
   Win Rate when edge exists: 64.2%

--------------------------------------------------------------------------------
R-SCORE PERFORMANCE:
--------------------------------------------------------------------------------

CORE:
   Average R-Score: 0.11
   Win Rate: 66.7%
   Sample Size: 45

EXP:
   Average R-Score: 0.19
   Win Rate: 58.8%
   Sample Size: 18

================================================================================
🎯 READY FOR ML CALIBRATION
================================================================================
You have 35 losses - enough for machine learning analysis!

Run: python3 scripts/ml_calibration.py
```

---

## 🤖 Tool 3: ML Calibration

### Purpose
After 30+ losses, propose statistically significant system improvements.

### Minimum Requirements

- **100+ total matches** (recommended)
- **30+ losses** (minimum for statistical power)

### Usage

```bash
python3 scripts/ml_calibration.py
```

### What It Analyzes

1. **Q-Score Recalibration**
   - Which Q-scores appear in >50% of losses?
   - Statistical significance (chi-square test)
   - Proposed weight adjustments

2. **Risk Threshold Adjustment**
   - Are losses clustered near R < 0.15 boundary?
   - Should CORE threshold be stricter (R < 0.12)?

3. **CS Threshold Tuning**
   - Win rate by CS range (70-75, 75-80, 80+)
   - Should minimum CS be raised?

4. **Data Source Value**
   - Local news vs no local news: win rate difference
   - SportsMole lineups: significant impact?

5. **Tier Validation**
   - Does Tier 1/2/3 actually predict success?

### Statistical Tests

- **Chi-Square**: For categorical variables (Q-score presence)
- **T-Test**: For continuous variables (R-Score, CS)
- **P-Value Threshold**: < 0.05 (95% confidence)
- **Effect Size**: Cohen's d for practical significance

### Output Example

```
================================================================================
📊 ML CALIBRATION REPORT
================================================================================

Sample Size: 120 matches (75 wins, 35 losses)
Sufficient for ML: ✅ Yes

--------------------------------------------------------------------------------
✅ STATISTICALLY SIGNIFICANT FINDINGS (3)
--------------------------------------------------------------------------------

1. Q9_OVERWEIGHT (Q_SCORE_RECALIBRATION)
   Description: Q9 (Lineups) systematically overestimated

   Evidence:
      • present_in_losses_pct: 63
      • present_in_wins_pct: 35
      • chi_square_p_value: 0.01
      • sample_size_losses: 22
      • sample_size_wins: 26

   Current State: Q9 can boost CS by up to +15
   Proposed Change: Cap Q9 influence at +5 CS maximum

   Expected Impact:
      • Win Rate: +3-4%
      • Bet Volume: -5%
      • Confidence: high

   ✅ Recommendation: IMPLEMENT
   Reasoning: Statistically significant (p=0.01), large effect size, minimal volume impact

2. R_THRESHOLD_TIGHTEN (RISK_THRESHOLD_ADJUSTMENT)
   Description: R-Score threshold too loose for CORE

   Evidence:
      • losses_at_r_012_015: 14
      • losses_at_r_below_012: 3
      • t_test_p_value: 0.03

   Current State: CORE threshold R < 0.15
   Proposed Change: Tighten to R < 0.12

   Expected Impact:
      • Win Rate: +5%
      • Bet Volume: -12%
      • Confidence: high

   ✅ Recommendation: IMPLEMENT
   Reasoning: Clear performance difference, acceptable volume reduction

3. LOCAL_NEWS_BOOST (DATA_SOURCE_VALUE_ASSESSMENT)
   Description: Local news provides significant edge

   Evidence:
      • with_local_news_win_rate: 68
      • without_local_news_win_rate: 54
      • t_test_p_value: 0.02

   Current State: Local news treated same as other sources
   Proposed Change: Boost CS by +3 when local news present

   Expected Impact:
      • Win Rate: +2%
      • Bet Volume: 0%
      • Confidence: medium

   ✅ Recommendation: IMPLEMENT
   Reasoning: Significant edge, no volume impact

--------------------------------------------------------------------------------
❌ REJECTED PROPOSALS (2)
--------------------------------------------------------------------------------

1. CS_THRESHOLD_RAISE (CS_THRESHOLD_TUNING)
   Description: Raising CS threshold to 75
   P-Value: 0.18
   Reason: Not statistically significant (p > 0.05)

2. TIER_REDEFINITION (TIER_SYSTEM_VALIDATION)
   Description: Adjust tier boundaries
   P-Value: 0.22
   Reason: Insufficient evidence, current tiers performing adequately

--------------------------------------------------------------------------------
🎯 OVERALL RECOMMENDATIONS
--------------------------------------------------------------------------------

   Implement: 3 proposals
   Monitor: 0 proposals
   Reject: 2 proposals

   Expected Win Rate Improvement: +5-7%
   Expected Volume Impact: -10-15%
   Net ROI Improvement: +8-12%

--------------------------------------------------------------------------------
📋 NEXT STEPS
--------------------------------------------------------------------------------

   1. Implement proposals: Q9_OVERWEIGHT, R_THRESHOLD_TIGHTEN, LOCAL_NEWS_BOOST
   2. Monitor for 50 matches
   3. Revert if win rate drops below current baseline
   4. Re-calibrate after 100 additional matches

================================================================================

📄 Full report saved to: calibration_reports/calibration_20251121_151230.json
```

---

## 🔄 Complete Workflow

### Step 1: Daily Betting (Existing)
```bash
# 1. Scrape
python3 scripts/scraper.py --input matches_all.txt --output match_data_v$(date +%Y%m%d).json

# 2. Analyze
python3 scripts/master_orchestrator.py analyze-batch --input matches_all.txt

# 3. Sync to Airtable
python3 scripts/sync_all_betting_opportunities.py

# 4. Archive
python3 scripts/organize_analyses.py
```

### Step 2: After Each Loss (Manual)
```bash
# Log the loss with details
python3 scripts/loss_ledger.py "MatchID_DDMMYYYY" "2-1" "Team -1.0" -1.0 full
```

### Step 3: After Each Betting Day (Automated)
```bash
# Update match results from Airtable
python3 scripts/post_match_analysis.py
```

### Step 4: After 30 Losses (ML Calibration)
```bash
# Run machine learning analysis
python3 scripts/ml_calibration.py
```

### Step 5: Implement Changes
- Review calibration report
- Update prompt weights in `YUDOR_MASTER_PROMPT_v5.3.md`
- Update thresholds in `master_orchestrator.py`
- Document changes in version control

### Step 6: Monitor
- Track next 50 matches
- Verify win rate improvement
- Revert if performance drops

---

## 📁 Files Generated

| File | Description |
|------|-------------|
| `loss_ledger.json` | All logged losses with detailed analysis |
| `match_results.json` | Complete match results and statistics |
| `calibration_reports/calibration_YYYYMMDD_HHMMSS.json` | ML calibration report |

---

## 🎯 Key Principles

### 1. Statistical Rigor
- Only propose changes with p < 0.05
- Minimum sample sizes: 30 per category
- Calculate effect sizes, not just significance

### 2. Practical Constraints
- Never reduce bet volume below 50 matches/month
- Prefer small adjustments over radical changes
- Always allow reversion if changes fail

### 3. Conservative Approach
- When in doubt, don't change
- Monitor changes for 50 matches minimum
- Document reasoning for all changes

### 4. Continuous Learning
- Re-calibrate after every 100 matches
- Track calibration history
- Learn from both wins AND losses

---

## 🚨 Important Notes

### Loss Ledger
- **Manual process** - you must run after each loss
- **Be honest** about final score and bet details
- **Review** Claude's analysis - it's learning from your data

### Post-Match Analysis
- **Enter results in Airtable** with all fields
- **Run daily** to track performance
- **Alerts at 30 losses** for ML readiness

### ML Calibration
- **Minimum 100 matches** for reliable analysis
- **Conservative by design** - will reject weak proposals
- **Implement gradually** - one change at a time

---

## 📞 Troubleshooting

### "Analysis file not found"
- Ensure match_id format: `HomevsAway_DDMMYYYY`
- Check `analysis_history/` folder

### "Not enough data for ML"
- Need ≥30 losses and ≥100 total matches
- Continue betting and logging losses

### "All proposals rejected"
- Normal! System is conservative
- May need more data (100+ matches)
- Current system may already be optimized

---

## 🎓 Learning from the System

### Good Signs
- Win rate improving over time
- Fewer BAD_LUCK losses (more accurate pricing)
- Market AH converging with Yudor AH

### Warning Signs
- Win rate declining
- Many Q_SCORE_OVERWEIGHT losses
- Market consistently more accurate

### Actions
- If win rate < 52% after 100 bets → Run ML Calibration
- If specific Q-score appears in >60% losses → Investigate immediately
- If market always beats you → Fundamental pricing issue

---

**Remember**: This system learns from YOUR data. The more losses you log honestly, the better it gets at identifying weaknesses and proposing improvements.
