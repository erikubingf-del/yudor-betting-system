# ML System - Quick Start Guide

## ✅ What's Been Created

Three powerful machine learning tools for continuous system improvement:

### 1. **Loss Ledger** (`scripts/loss_ledger.py`)
Deep analysis of each betting loss using Claude AI

### 2. **Post-Match Analysis** (`scripts/post_match_analysis.py`)
Automated statistics from your Airtable results

### 3. **ML Calibration** (`scripts/ml_calibration.py`)
Statistical proposals for system improvements (after 30+ losses)

---

## 🚀 Quick Commands

### Log a Loss (Manual)
```bash
python3 scripts/loss_ledger.py "MatchID_DDMMYYYY" "2-1" "Team -1.0" -1.0 full
```

### Update Statistics (Daily)
```bash
python3 scripts/post_match_analysis.py
```

### Run ML Calibration (After 30+ losses)
```bash
python3 scripts/ml_calibration.py
```

---

## 📋 Required Airtable Fields

Add these to your "Match Analyses" table:

| Field Name | Type | Example |
|------------|------|---------|
| Match Result | Text | "2-1" |
| Bet Result | Single Select | WIN, LOSS, HALF_LOSS, PUSH |
| Units Won/Lost | Number | -1.0 |
| Market AH | Number | -0.75 |
| Bet Entered | Checkbox | TRUE |

---

## 🎯 Workflow

### After Each Loss
1. Note: Match ID, final score, bet placed, loss type
2. Run: `python3 scripts/loss_ledger.py ...`
3. Review: Claude's analysis of what went wrong

### Daily (After Matches Finish)
1. Enter: Match results in Airtable
2. Run: `python3 scripts/post_match_analysis.py`
3. Review: Win rates, ROI, statistics

### After 30 Losses (or 100 Matches)
1. Run: `python3 scripts/ml_calibration.py`
2. Review: Statistical proposals
3. Implement: Changes to prompts/thresholds
4. Monitor: Next 50 matches
5. Revert: If performance drops

---

## 📊 What Gets Analyzed

### Loss Categories
- **BAD_LUCK**: Tight loss, analysis was correct
- **RISK_SIGNAL_MISSED**: R-Score too optimistic
- **Q_SCORE_OVERWEIGHT**: Specific Q-scores overestimated
- **DATA_QUALITY_ISSUE**: Missing critical info
- **MARKET_WAS_RIGHT**: Fair line was wrong

### Statistical Tests
- **Chi-Square**: Q-score presence in wins vs losses
- **T-Test**: R-Score, CS differences
- **P-Value**: < 0.05 required for proposals
- **Effect Size**: Practical significance

### Proposed Changes
- Q-Score weight adjustments (e.g., reduce Q9 influence)
- R-Score threshold tightening (e.g., CORE: R < 0.12)
- CS threshold raising (e.g., minimum CS = 75)
- Data source value (e.g., boost CS when local news present)

---

## ⚠️ Important Principles

### 1. Minimum Samples
- **100+ total matches** before major changes
- **30+ losses** for reliable loss analysis
- **50+ matches** to monitor each change

### 2. Conservative Approach
- Only implement changes with p < 0.05
- Never reduce bet volume below 50/month
- Prefer small adjustments over radical changes

### 3. Continuous Learning
- Re-calibrate after every 100 matches
- Track all changes in version control
- Document reasoning for all adjustments

---

## 📁 Files Generated

- `loss_ledger.json` - All losses with detailed analysis
- `match_results.json` - Complete statistics
- `calibration_reports/calibration_*.json` - ML proposals

---

## 🎓 Example Output

### Loss Ledger
```
Category: Q_SCORE_OVERWEIGHT
Q-Scores Overestimated: Q9, Q5
CS Delta: -12 (should have been 60, not 72)
R-Score Delta: +0.08 (should have been 0.30, not 0.22)
Market was closer: True
```

### Post-Match Analysis
```
CORE: 45 matches, 66.7% win rate, +12.5 units, +27.8% ROI
EXP: 18 matches, 58.8% win rate, +2.5 units, +13.9% ROI
```

### ML Calibration
```
PROPOSAL: Q9_OVERWEIGHT
- Cap Q9 influence at +5 CS (currently +15)
- p-value: 0.01 (highly significant)
- Expected: +3-4% win rate, -5% volume
- Recommendation: IMPLEMENT
```

---

## 📞 Need Help?

See full documentation: [ML_SYSTEM_GUIDE.md](ML_SYSTEM_GUIDE.md)

---

**Remember**: This system learns from YOUR data. Be honest when logging losses, and the AI will identify patterns and propose improvements automatically.
