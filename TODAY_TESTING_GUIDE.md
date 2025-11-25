# 🧪 TODAY'S TESTING GUIDE - Loss Ledger Validation

**Date:** 2024-11-24
**Goal:** Validate loss ledger system before production use
**Time Required:** ~30 minutes

---

## ✅ Pre-Test Validation (COMPLETED)

```bash
python3 scripts/validate_loss_ledger.py
```

**Result:** All systems operational ✅
- Prompt files exist
- API keys configured
- Claude API accessible
- Airtable connected
- Directories writable

---

## 📋 Step-by-Step Testing

### STEP 1: Prepare Airtable (5 minutes)

#### A. Check if "Bets Entered" table exists
1. Open Airtable base
2. Look for "Bets Entered" table
3. If missing, create it

#### B. Add required columns (if missing)
| Column Name | Type | Options |
|-------------|------|---------|
| match_id | Link to "Match Analyses" | - |
| Bets Entered | Checkbox | - |
| Score | Single line text | Example: "1-2" |
| Result | Single select | Win, Loss, Half Win, Half Loss, Refund |
| Market AH | Number | Example: -0.75 |
| Market AH Odds | Number | Example: 1.95 |
| P/L | Number | Example: -100 (negative = loss) |
| stake | Number | Example: 100 |

#### C. Add 2-3 test records (past losses)
Example:
```
match_id: "ManchesterUnited_vs_Everton_20241124"
Bets Entered: ✓ (checked)
Score: "1-2"  (actual match result)
Result: "Loss"
Market AH: -0.75
P/L: -100
```

**CRITICAL:** match_id must match EXACTLY with "Match Analyses" table!

---

### STEP 2: Test Manual Mode (10 minutes)

```bash
# Replace with your actual match_id from Airtable
python3 scripts/master_orchestrator.py loss-analysis --match-id ManchesterUnited_vs_Everton_20241124
```

**What to expect:**
1. System loads original YUDOR prediction
2. Shows Q1-Q19 scores that were used
3. Claude analyzes what went wrong
4. Identifies failed Q-IDs
5. Classifies error type
6. Saves to `loss_ledger/` folder

**Check outputs:**
```bash
# View generated analysis
ls -lh loss_ledger/

# Read the analysis (replace with actual filename)
cat loss_ledger/ManchesterUnited_vs_Everton_20241124_loss_*.json | python3 -m json.tool
```

**Verify the analysis includes:**
- [ ] Failed Q-IDs (e.g., "Q6: Tactics was overestimated")
- [ ] Error category (Model Error / Data Error / Variance)
- [ ] Root cause explanation
- [ ] Specific recommendations

---

### STEP 3: Verify Airtable Update (5 minutes)

1. Open Airtable "Results" table
2. Find the record with your match_id
3. Check these fields are populated:
   - [ ] error_category (e.g., "Q6: Tactics, Q11: Form")
   - [ ] error_type (e.g., "Model Error")
   - [ ] failed_q_ids (e.g., "Q6, Q11, Q17")
   - [ ] loss_ledger_analysis (full JSON)

**If fields are missing:**
- Check master_orchestrator.py has correct table name
- Verify Airtable API permissions
- Check console output for errors

---

### STEP 4: Test Auto Mode (10 minutes)

```bash
# Process ALL unanalyzed losses automatically
python3 scripts/master_orchestrator.py loss-analysis --auto
```

**What to expect:**
1. System queries Airtable for all losses
2. Processes each one sequentially
3. Saves all analyses to `loss_ledger/`
4. Updates Airtable Results table

**Check outputs:**
```bash
# Count how many losses were analyzed
ls loss_ledger/*.json | wc -l

# Review all error categories
grep -h "error_category" loss_ledger/*.json
```

---

### STEP 5: Learning Review (10 minutes)

#### A. Pattern Detection
Look for recurring failed Q-IDs across multiple losses:

```bash
# Extract all failed Q-IDs
grep -h "failed_q_ids" loss_ledger/*.json | sort | uniq -c | sort -rn
```

**Questions to ask:**
- Is Q6 (Tactics) failing repeatedly? → Maybe formation data is critical
- Is Q11 (Form) failing repeatedly? → Maybe recent form weighting is wrong
- Is Q17 (Home/Away) failing repeatedly? → Maybe home advantage is overestimated

#### B. Error Type Distribution
```bash
# Count error types
grep -h "error_type" loss_ledger/*.json | sort | uniq -c
```

**Interpretation:**
- **Model Error:** YUDOR methodology needs adjustment (weights, formulas)
- **Data Error:** Scraped data was incomplete/wrong (need better sources)
- **Variance:** Prediction was correct, just unlucky (no action needed)

#### C. Actionable Insights
From the analyses, identify:
1. Which data sources are most critical? (Q-IDs with most failures)
2. Which Q-IDs have consistently good performance? (never fail)
3. Are there systematic biases? (always overestimate home team?)

---

## ✅ Success Criteria

### Minimum Requirements
- [ ] Manual mode processes 1 loss successfully
- [ ] Analysis file created in `loss_ledger/` folder
- [ ] Failed Q-IDs identified correctly
- [ ] Airtable Results table updated
- [ ] Error makes logical sense

### Ideal Outcome
- [ ] Auto mode processes all past losses
- [ ] Pattern detection reveals insights
- [ ] Clear action items identified
- [ ] No system errors or crashes
- [ ] Airtable schema working perfectly

---

## 🚨 Troubleshooting

### Error: "No match_id provided"
**Fix:** Check command syntax
```bash
# Wrong
python3 scripts/master_orchestrator.py loss-analysis --match-id

# Right
python3 scripts/master_orchestrator.py loss-analysis --match-id YOUR_MATCH_ID
```

### Error: "Match not found in Airtable"
**Fix:** Verify match_id spelling
```bash
# Check what match_ids exist
# (manually check Airtable "Match Analyses" table)
```

### Error: "Bets Entered table not found"
**Fix:** Create table in Airtable with required columns (see Step 1)

### Error: "No losses found"
**Fix:** Check "Bets Entered" table has:
- Result = "Loss" (exact spelling)
- P/L < 0 (negative number)
- match_id links to existing analysis

### Analysis seems wrong
**Fix:** Check original prediction quality
```bash
# Find original analysis
ls analysis_history/*YOUR_MATCH*

# Check data quality score
grep "data_quality" analysis_history/*YOUR_MATCH*.json
```

If data quality was low (< 60%), the loss might be due to insufficient data, not methodology error.

---

## 📊 Expected Results

### Example Good Analysis
```json
{
  "match_id": "Barcelona_vs_RealMadrid_20241123",
  "actual_result": "1-2",
  "yudor_prediction": {
    "ah_line": -0.25,
    "ah_team": "Barcelona",
    "decision": "CORE"
  },
  "failed_q_ids": ["Q6", "Q11"],
  "error_category": "Q6: Tactics underestimated Real Madrid's formation advantage",
  "error_type": "Model Error",
  "reasoning": "Q6 gave equal tactical scores, but Real Madrid's 4-3-3 exploited Barcelona's high line. Q11 form data was outdated. Recommend increasing Q6 weight and using last 3 games instead of 5.",
  "recommendations": [
    "Add formation matchup analysis to Q6",
    "Weight recent games (last 3) more heavily in Q11",
    "Consider Q6 as critical veto condition"
  ]
}
```

### Example Pattern (Multiple Losses)
```
Failed Q-IDs Summary:
- Q6 (Tactics): 4 losses
- Q11 (Form): 3 losses
- Q17 (Home/Away): 2 losses
- Q2 (Attack xG): 1 loss

Error Types:
- Model Error: 6 (need methodology adjustment)
- Data Error: 3 (need better data sources)
- Variance: 1 (unlucky, no action)

Recommendation: Focus on improving Q6 tactical analysis and Q11 form weighting.
```

---

## 🎯 Next Steps After Testing

### If All Tests Pass:
1. ✅ Mark system as production-ready
2. Use loss ledger after every weekend
3. Review patterns monthly
4. Adjust methodology based on learnings

### If Issues Found:
1. Document specific errors
2. Check logs in console output
3. Verify Airtable schema matches docs
4. Re-run validation script
5. Contact for debugging assistance

---

## 📞 Quick Reference Commands

```bash
# Validation (run first)
python3 scripts/validate_loss_ledger.py

# Manual loss analysis
python3 scripts/master_orchestrator.py loss-analysis --match-id MATCH_ID

# Auto loss analysis (all unanalyzed losses)
python3 scripts/master_orchestrator.py loss-analysis --auto

# View generated analyses
ls -lh loss_ledger/

# Check for patterns
grep -h "failed_q_ids" loss_ledger/*.json | sort | uniq -c | sort -rn

# View specific analysis
cat loss_ledger/MATCH_ID_loss_*.json | python3 -m json.tool
```

---

**Ready to test? Start with STEP 1! 🚀**
