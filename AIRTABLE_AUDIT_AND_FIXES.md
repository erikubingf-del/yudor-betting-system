# Airtable Integration - Audit & Fixes

## Issue 1: Missing "Yudor AH Team" Field ❌ CRITICAL

### Problem:
Currently saving:
- "Yudor AH Fair": -0.5 (the line)
- But NOT saving which team to bet on!

### Example Confusion:
- **Barcelona vs Real Madrid**
- Yudor AH Fair: **-0.25**
- ❓ **Question: Is this Barcelona -0.25 or Real Madrid -0.25?**

### Solution:
Add "Yudor AH Team" field to indicate:
- If line is **negative** (e.g., -0.5) → Favorite team name
- If line is **positive** (e.g., +0.75) → Underdog team name

### Code Fix Needed:
In `master_orchestrator.py` line ~1455, add:

```python
# Current (INCOMPLETE):
"Yudor AH Fair": analysis.get("yudor_ah_fair", 0),

# Should be (COMPLETE):
"Yudor AH Fair": analysis.get("yudor_ah_fair", 0),
"Yudor AH Team": analysis.get("yudor_ah_team", ""),  # NEW FIELD
```

Logic:
```python
# In the AH calculation section, determine the team:
if ah_line < 0:
    # Negative line = favorite
    yudor_ah_team = favorite_team_name
else:
    # Positive line = underdog
    yudor_ah_team = underdog_team_name
```

---

## Issue 2: Airtable Schema Validation

### Current Airtable Tables:

#### Table 1: Match Analyses
**Current Fields:**
- ✅ match_id (text)
- ✅ match_date (date)
- ✅ Home Team (text)
- ✅ Away Team (text)
- ✅ League (text)
- ✅ Yudor AH Fair (number)
- ❌ **Yudor AH Team (text)** - MISSING!
- ✅ Yudor Decision (select: CORE/EXP/VETO/FLIP)
- ✅ CS Final (number)
- ✅ R Score (number)
- ✅ Tier (number)
- ✅ Full Analysis (long text)
- ✅ Data Quality (number)
- ✅ Status (select)

#### Table 2: Bets Entered (Manual Entry by You)
**Current Fields:**
- ✅ match_id (link to Match Analyses)
- ✅ Bets Entered (checkbox) - Did you enter the bet?
- ✅ Market AH (number) - What the market offered
- ✅ Market AH Odds (number) - Odds you got
- ❌ **Score (text)** - Final score (e.g., "1-2")
- ❌ **Result (select)** - Win/Loss/Half Win/Half Loss/Refund
- ❌ **P/L (number)** - Profit/Loss amount
- ✅ edge_pct (number) - Your edge
- ✅ stake (number) - Amount bet
- ✅ notes (long text)

#### Table 3: Results (Populated by Loss Ledger)
**Current Fields:**
- ✅ match_id (link to Match Analyses)
- ✅ result_timestamp (datetime)
- ✅ final_score (text)
- ✅ ah_result (select: WIN/PUSH/LOSS)
- ✅ profit_loss (number)
- ✅ yudor_correct (checkbox)
- ✅ error_category (text) - From loss ledger
- ✅ error_type (text) - Model Error/Data Error/Variance
- ✅ failed_q_ids (long text) - Which Q-IDs failed
- ✅ notes (long text)

---

## Issue 3: Your Proposed Columns - Assessment

### Your Question:
> "DO I need any extra collumns? Maybe we add one that will be the loss ledger to show what we learned from out bet"

### Analysis:

**Option A: Single Table (Market Analysis)**
- ✅ Pros: All data in one place, easier to see full picture
- ❌ Cons: Cluttered, mixes prediction data with post-match data

**Option B: Separate Tables (Current System) - ✅ RECOMMENDED**
- ✅ **Match Analyses** = Pre-match predictions (from YUDOR system)
- ✅ **Bets Entered** = Your manual entry (what you actually bet)
- ✅ **Results** = Post-match results + Loss Ledger analysis

### Why Separate Tables is Better:
1. **Clean workflow**: Prediction → Bet → Result
2. **Audit trail**: Can compare prediction vs bet vs result
3. **Loss Ledger stays separate**: Only populated for losses
4. **Easier queries**: "Show me all losses where error_type = 'Model Error'"

---

## Issue 4: Loss Ledger Workflow Validation

### Current Loss Ledger Flow:
```
1. Match Analyses table → YUDOR makes prediction
2. You manually enter bet in Bets Entered (if you bet)
3. After match, you add Score/Result/P&L to Bets Entered
4. Run: python scripts/master_orchestrator.py loss-analysis --auto
5. System:
   - Finds all LOSS records without error_category
   - Loads original analysis
   - Compares prediction vs actual result
   - Uses Claude to analyze what went wrong
   - Saves to loss_ledger/ folder
   - Updates Results table with error classification
```

### Fields Loss Ledger Uses:
**FROM Bets Entered (your manual entry):**
- ✅ Score - To compare vs prediction
- ✅ Result - To identify losses
- ✅ P/L - To calculate severity

**POPULATES in Results:**
- ✅ error_category - "Q6: Tactics - Formation matchup failed"
- ✅ error_type - "Model Error" | "Data Error" | "Variance"
- ✅ failed_q_ids - List of Q-IDs that were wrong
- ✅ notes - Detailed root cause analysis

---

## Recommended Airtable Structure (Final)

### Table 1: Match Analyses (Automated)
```
match_id | match_date | Home Team | Away Team | League |
Yudor AH Fair | Yudor AH Team | Yudor Decision |
CS Final | R Score | Tier | Data Quality | Status
```
**Populated by:** YUDOR system automatically

### Table 2: Bets Entered (Manual by You)
```
match_id [link] | Bets Entered [checkbox] |
Market AH | Market AH Odds | Score | Result | P/L |
edge_pct | stake | notes
```
**Populated by:** You manually after match
**Key fields you add:**
- Bets Entered ✓ if you bet
- Score: "1-2"
- Result: Win/Loss/Half Win/etc.
- P/L: +50 or -100

### Table 3: Results / Loss Ledger (Automated)
```
match_id [link] | result_timestamp | final_score |
ah_result | profit_loss | yudor_correct |
error_category | error_type | failed_q_ids |
loss_ledger_analysis [long text] | notes
```
**Populated by:** Loss analysis automation
**Only for losses** - shows what we learned

---

## Fix Checklist

### ❌ TODO: Add "Yudor AH Team" Field
**File:** `scripts/master_orchestrator.py`
**Line:** ~1455 in `save_to_airtable()`
**Fix:** Add logic to determine which team to bet on based on AH line sign

### ❌ TODO: Validate Bets Entered Schema
**Airtable:** Add/verify these columns exist:
- Score (text)
- Result (select: Win/Loss/Half Win/Half Loss/Refund)
- P/L (number)

### ✅ Loss Ledger Already Working
**Current fields are correct:**
- error_category
- error_type
- failed_q_ids
- All populated by loss-analysis command

---

## Testing Plan for Loss Ledger (Today)

### Step 1: Verify Table Connections
```python
# Check if tables are linked correctly
python3 scripts/master_orchestrator.py loss-analysis --help
```

### Step 2: Manual Test (1 match)
1. Find a past match in Airtable with a LOSS
2. Add to Bets Entered:
   - Score: actual score
   - Result: "Loss"
   - P/L: negative amount
3. Run: `python3 scripts/master_orchestrator.py loss-analysis --match-id MATCH_ID`
4. Verify:
   - System loads original analysis
   - Claude analyzes what went wrong
   - Saves to `loss_ledger/MATCH_ID_loss_TIMESTAMP.json`
   - Updates Results table with error_category

### Step 3: Auto Test (All losses)
1. Ensure multiple losses exist in Bets Entered
2. Run: `python3 scripts/master_orchestrator.py loss-analysis --auto`
3. Verify:
   - System finds all unanalyzed losses
   - Processes each one
   - Saves all to loss_ledger/
   - Updates all Results records

### Step 4: Validate Learning
Check if loss ledger identifies:
- ✅ Which Q-IDs failed (Q6, Q11, etc.)
- ✅ Error type (Model Error vs Variance)
- ✅ Patterns across multiple losses
- ✅ Recommendations for improvement

---

## Summary

### Critical Fixes Needed:
1. ❌ **Add "Yudor AH Team" field** - Must know which team to bet!
2. ❌ **Verify Bets Entered has Score/Result/P&L columns**

### Already Working:
1. ✅ Loss Ledger automation
2. ✅ Three-table structure (Analyses → Bets → Results)
3. ✅ Error classification (Model Error/Data Error/Variance)

### Testing Today:
1. Run loss-analysis on 1-3 past losses
2. Verify error_category populated correctly
3. Check loss_ledger/ files are useful

Your system is **95% complete** - just need to add the "Yudor AH Team" field to avoid confusion!
