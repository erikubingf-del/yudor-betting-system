# 🔄 COMPLETE YUDOR SYSTEM WORKFLOW v5.3

## End-to-End Process with Full Automation & Learning

---

## 📅 **PHASE 1: THURSDAY EVENING (Pre-Match Preparation)**

### **Step 1.1: You Create Match List**

**Action:** You create `matches_all.txt`

**Format:**
```
Flamengo vs Bragantino, Brasileirão, 25/11/2025, 19:00
Inter vs Lazio, Serie A, 25/11/2025, 20:45
Real Madrid vs Barcelona, La Liga, 26/11/2025, 21:00
... (30-40 games)
```

**Time:** 15 minutes

---

### **Step 1.2: System Runs Pre-Filter (Automatic)**

**Command:**
```bash
python scripts/master_orchestrator.py pre-filter --input matches_all.txt
```

**What Happens:**

```
STAGE 1: Scraping (30-40 min for 30-40 games)
├─ For EACH game in matches_all.txt:
│  ├─ scraper.py extracts URLs (SportsMole, WhoScored, etc.)
│  ├─ Fetches basic data from each source
│  └─ Saves: scraped_data/[game_id]_raw.json
│
└─ Output: All games scraped

STAGE 2: Data Quality Assessment (10-15 min)
├─ For EACH game:
│  ├─ Runs DATA_CONSOLIDATION_PROMPT (light mode)
│  ├─ Checks which Q-IDs have complete data
│  ├─ Calculates Data Quality Score (0-100)
│  └─ Flags missing critical data
│
└─ Output: Quality scores for all games

STAGE 3: Filtering & Selection (instant)
├─ Ranks games by data_quality_score
├─ Applies threshold (default: ≥70)
├─ Selects top 15-20 games
├─ Creates: matches_priority.txt
└─ Saves: pre_filter_history/2025-11-22_prefilter.json

STAGE 4: Report Generation (instant)
└─ Shows you:
    ├─ "38 games considered"
    ├─ "18 games selected for deep analysis"
    ├─ "20 games filtered out (insufficient data)"
    └─ List of selected games with quality scores
```

**Files Created:**
```
✅ matches_priority.txt (15-20 games for deep analysis)
✅ pre_filter_history/2025-11-22_prefilter.json (learning data)
✅ scraped_data/[game_id]_raw.json (raw scraped data, 30-40 files)
```

**Time:** ~45-60 minutes (automatic)

---

## 📅 **PHASE 2: FRIDAY MORNING (Deep Analysis)**

### **Step 2.1: System Runs Deep Analysis (Automatic)**

**Command:**
```bash
python scripts/master_orchestrator.py analyze-batch --input matches_priority.txt
```

**What Happens:**

```
For EACH game in matches_priority.txt (15-20 games):

  STAGE 1: Data Consolidation (3-5 min/game)
  ├─ Loads: scraped_data/[game_id]_raw.json
  ├─ Runs: DATA_CONSOLIDATION_PROMPT (full mode)
  ├─ Fills Q1-Q19 deterministically using ANEXO I
  ├─ Handles missing data with defaults
  ├─ Outputs: consolidated_data/[game_id]_consolidated.json
  └─ Contains: All Q-scores, data quality report

  STAGE 2: Yudor Analysis - Layer 1 (Pricing) (2-3 min/game)
  ├─ Loads: consolidated_data/[game_id]_consolidated.json
  ├─ Runs: YUDOR_MASTER_PROMPT_v5.3 - Layer 1
  ├─ Calculates Raw_Casa, Raw_Vis
  ├─ Calculates P(Empate) from Betfair
  ├─ Calculates AH fair line (iterative ±0.25)
  └─ Outputs: AH_Line_Model, Odd_Model

  STAGE 3: Yudor Analysis - Layer 2 (Confidence) (1-2 min/game)
  ├─ Calculates Z-Score from 7 categories
  ├─ Applies penalties (injuries, travel)
  ├─ Calculates CS_final (0-100)
  └─ Outputs: CS_final, Motivo_Chave

  STAGE 4: Yudor Analysis - Layer 3 (Risk Guard) (2-3 min/game)
  ├─ Evaluates 10 risk signals using ANEXO II
  ├─ Calculates R-Score (weighted sum)
  ├─ Calculates RBR (risk asymmetry)
  └─ Outputs: R-Score, RBR

  STAGE 5: Decision Logic (instant)
  ├─ Applies CORE/EXP/VETO/FLIP/IGNORAR rules
  ├─ Fetches Betfair market line (AH_Line_Market)
  ├─ Calculates Edge% = (Odd_Market / Odd_Model - 1) × 100
  └─ Outputs: Decision, Tier, Edge%

  STAGE 6: Save to Airtable (instant)
  ├─ Connects to Airtable API
  ├─ Creates record in "Match Analyses" table:
  │  ├─ game_id, date, home, away, league
  │  ├─ AH_Line_Model, Odd_Model
  │  ├─ AH_Line_Market, Odd_Market (from Betfair)
  │  ├─ Edge%
  │  ├─ Decision, Tier
  │  ├─ CS_final, R_Score
  │  ├─ Motivo_Chave
  │  ├─ Data_Quality_Score
  │  ├─ Full analysis JSON
  │  └─ Status: "ANALYZED"
  └─ Also saves: analysis_history/[game_id]_[timestamp].json

TOTAL TIME: ~10-15 min × 15-20 games = 2.5-5 hours
```

**Files Created:**
```
✅ consolidated_data/[game_id]_consolidated.json (15-20 files)
✅ analysis_history/[game_id]_[timestamp].json (15-20 files)
✅ Airtable "Match Analyses" table (15-20 records)
```

**Time:** 2.5-5 hours (automatic, you can do other things)

---

### **Step 2.2: You Review Analysis (Manual)**

**Action:** Open Airtable → "Match Analyses" table

**View:** "Pending Decisions" (Status = "ANALYZED")

**What You See:**

| game_id | Home | Away | AH_Model | AH_Market | Edge% | Decision | Tier | CS | R | Quality | Status |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| FLA_BRA_1125 | Flamengo | Bragantino | -0.75 | -0.50 | +12.3% | CORE | 1 | 82 | 0.14 | 92 | ANALYZED |
| INT_LAZ_1125 | Inter | Lazio | -1.00 | -0.75 | +8.5% | CORE | 1 | 78 | 0.18 | 88 | ANALYZED |
| RMA_BAR_1126 | Real Madrid | Barcelona | -0.25 | -0.50 | -8.2% | IGNORAR | - | 72 | 0.22 | 85 | ANALYZED |

**Your Analysis:**
- ✅ Flamengo: +12.3% edge, CORE, high CS → **Consider betting**
- ✅ Inter: +8.5% edge, CORE, good CS → **Consider betting**
- ❌ Real Madrid: Negative edge → **Skip**

**Time:** 30 minutes

---

## 📅 **PHASE 3: FRIDAY AFTERNOON / SATURDAY MORNING (Pre-Match Check)**

### **Step 3.1: Final Line Check (Manual)**

**2-3 hours before each kickoff:**

**Action:** Check Betfair for current market lines

**Process:**
```
For games you're considering:
1. Open Betfair Exchange
2. Check current AH line & odds
3. Compare to model:
   ├─ Model: Flamengo -0.75 @ 2.01
   ├─ Market: Flamengo -0.50 @ 2.15
   └─ Edge still +12.3% → ✅ GOOD

4. If edge still ≥8% → ENTER BET
5. If edge now <8% → SKIP (line moved)
```

**Update Airtable:**

For games you **DECIDE TO ENTER**:
```
In "Match Analyses" table:
├─ Entry_Status: "Yes - Value Found"
├─ Line_Entered: -0.50 (actual line you got)
├─ Odd_Entered: 2.15 (actual odds)
├─ Edge_Actual: +12.3%
├─ Stake: 100 (units)
└─ Status: "BET_ENTERED"

System automatically creates record in "Bets_Entered" table:
├─ match_id: Links to Match Analyses
├─ entry_timestamp: 2025-11-25 17:30
├─ market_ah_line: -0.50
├─ market_ah_odds: 2.15
├─ edge_pct: 12.3
├─ stake: 100
└─ expected_value: 100 × 0.123 = +12.3
```

For games you **DECIDE NOT TO ENTER**:
```
In "Match Analyses" table:
├─ Entry_Status: One of:
│  ├─ "No - Line Moved" (edge disappeared)
│  ├─ "No - Not Confident" (CS too low, you don't trust it)
│  ├─ "No - Forgot" (missed the deadline)
│  └─ "No - Market More Expensive" (line worse than model)
├─ Market_AH_Entered: -1.00 (what market actually offered)
├─ Market_Odd_Entered: 1.85
├─ Notes: "Market moved from -0.50 to -1.00, edge disappeared"
└─ Status: "SKIPPED"
```

**Why Track Non-Entries?**
- **Learning:** Did we miss value? Was the model wrong?
- **Line movement analysis:** Are our lines accurate early or do they always move?
- **Pattern recognition:** Which leagues/games have stable lines?

**Time:** 10-15 minutes per game

---

## 📅 **PHASE 4: POST-MATCH (Sunday Evening / Monday)**

### **Step 4.1: You Update Results (Manual)**

**Action:** For each game you tracked (bet or not), update in Airtable

**For GAMES YOU BET ON:**

```
In "Results" table (or update Bets_Entered):
├─ match_id: FLA_BRA_1125
├─ final_score: "3-1"
├─ ah_result: "WIN" / "LOSS" / "PUSH" / "HALF_WIN" / "HALF_LOSS"
├─ profit_loss: +95 (won) or -100 (lost)
├─ yudor_correct: ✅ (if predicted winner won)
├─ fair_line_accuracy: "Model -0.75 vs actual -1.5 goal margin = accurate"
└─ Status: "RESULT_RECORDED"
```

**For GAMES YOU DIDN'T BET BUT TRACKED:**

```
In "Match Analyses" table:
├─ Actual_Score: "3-1"
├─ Actual_AH_Result: "WIN" (if we had bet)
├─ Missed_Opportunity: true (if we skipped but would have won)
├─ Notes: "Skipped due to line movement, would have won"
└─ Status: "RESULT_RECORDED_NO_BET"
```

**Why Track Non-Bet Results?**
- **Regret analysis:** Did we skip games we should have bet?
- **Model validation:** Are our lines accurate even when we don't bet?
- **Filter validation:** Did pre-filter exclude winners?

**Time:** 15-20 minutes for all games

---

## 📅 **PHASE 5: LOSS ANALYSIS (Monday Evening - Automatic)**

### **Step 5.1: System Detects Losses**

**Trigger:** After you update results, system checks Airtable

**Command (or runs automatically):**
```bash
python scripts/master_orchestrator.py loss-analysis --auto
```

**What Happens:**

```
STAGE 1: Query Airtable
├─ Finds: All records in "Results" where:
│  ├─ ah_result = "LOSS"
│  └─ loss_analysis_complete = false
│
└─ Found: 3 losses this weekend

STAGE 2: For EACH loss, run LOSS_LEDGER_ANALYSIS
├─ Loads: Original analysis from analysis_history/
├─ Loads: Actual match result from Airtable
├─ Runs: LOSS_LEDGER_ANALYSIS_PROMPT_v1.0
│
├─ Process:
│  ├─ Retrieves Q1-Q19 original predictions
│  ├─ Fetches post-match data (actual xG, ratings, events)
│  ├─ Compares prediction vs reality for EACH Q-ID
│  ├─ Identifies primary failure point:
│  │  ├─ "Q6 (Tactics): Inter's 4-3-3 didn't dominate as predicted"
│  │  ├─ "Q9 (Motivation): Must-win pressure didn't materialize"
│  │  └─ "Q15 (Injuries): Barella injured in 35th min (unforeseen)"
│  │
│  ├─ Classifies error type:
│  │  ├─ Model Error (60%): Q6 matrix wrong
│  │  ├─ Variance (30%): Barella injury unforeseen
│  │  └─ Data Error (10%): Didn't catch Lazio's tactical flexibility
│  │
│  ├─ Generates Q-Score breakdown table
│  └─ Provides recommendations
│
└─ Outputs: Loss analysis report

STAGE 3: Save Loss Analysis
├─ Updates "Results" table in Airtable:
│  ├─ error_category: "Model Error: Q6 Tactics"
│  ├─ primary_failure: "Q6: Tactical matrix overestimated Inter advantage"
│  ├─ q_score_breakdown: JSON with all Q-IDs success/fail
│  ├─ recommendations: "Monitor Q6 performance next 10 matches"
│  └─ loss_analysis_complete: true
│
└─ Saves: loss_ledger/[game_id]_loss_analysis.json
```

**Files Created:**
```
✅ loss_ledger/FLA_BRA_1125_loss_analysis.json
✅ loss_ledger/INT_LAZ_1125_loss_analysis.json
✅ loss_ledger/RMA_BAR_1126_loss_analysis.json
✅ Airtable "Results" table updated with analysis
```

**Time:** ~5-10 minutes per loss (automatic)

---

## 📅 **PHASE 6: SYSTEM AUDIT (After 30 Losses - Automatic)**

### **Step 6.1: System Detects Threshold**

**Trigger:** When loss_ledger/ contains 30 loss analyses

**Command (or runs automatically):**
```bash
python scripts/master_orchestrator.py audit --mode ml
```

**What Happens:**

```
STAGE 1: Data Collection
├─ Loads: ALL loss analyses from loss_ledger/
├─ Loads: ALL win analyses from analysis_history/
├─ Loads: ALL bet tracking from Airtable
│
└─ Dataset: 30 losses + 30-40 wins = ~60-70 matches

STAGE 2: Statistical Analysis (Python ML, NOT prompt-based)
├─ Q-ID Performance Analysis:
│  ├─ For EACH Q-ID (Q1-Q19):
│  │  ├─ Win rate when Q-ID score high
│  │  ├─ Win rate when Q-ID score low
│  │  ├─ Correlation: Q-ID score vs actual outcome
│  │  └─ Identify: Which Q-IDs failed most often?
│  │
│  └─ Example findings:
│     ├─ Q6 (Tactics): 42% win rate when scored high (expected 55%+)
│     ├─ Q17 (Home Advantage): 47% win rate (expected 55%+)
│     └─ Q13 (xG Delta): 62% win rate (working well!)
│
├─ Category Performance:
│  ├─ Technique (Q1-Q4): 58% win rate ✅
│  ├─ Tactics (Q5-Q8): 45% win rate ⚠️
│  ├─ Motivation (Q9-Q10): 52% win rate ⚠️
│  ├─ Form (Q11-Q12): 61% win rate ✅
│  ├─ Performance (Q13-Q14): 64% win rate ✅
│  ├─ Injuries (Q15-Q16): N/A (penalty only)
│  └─ Home/Away (Q17-Q19): 48% win rate ⚠️
│
├─ Decision Tier Performance:
│  ├─ CORE bets: 56% win rate ✅
│  ├─ EXP bets: 48% win rate ⚠️
│  └─ FLIP bets: 3 samples (insufficient data)
│
├─ League Performance:
│  ├─ Serie A: 62% win rate (12W-7L) ✅
│  ├─ Premier League: 54% win rate (7W-6L) ✅
│  ├─ Brasileirão: 48% win rate (6W-6L) ⚠️
│  └─ La Liga: 45% win rate (5W-6L) ⚠️
│
├─ Data Quality vs Outcome:
│  ├─ Games with quality ≥85: 58% win rate ✅
│  ├─ Games with quality 70-84: 52% win rate ✅
│  └─ Games with quality 60-69: 44% win rate ⚠️
│
└─ Pre-Filter Effectiveness:
   ├─ Games selected (priority): 54% win rate
   ├─ Games filtered out: (Track if we later got results) 51% win rate
   └─ Analysis: "Pre-filter working, but not huge difference"

STAGE 3: Machine Learning Recommendations
├─ Uses: Logistic Regression / Random Forest
├─ Trains: Predict win/loss from Q1-Q19 scores
├─ Identifies: Which Q-ID weights should change
│
└─ Example output:
   ├─ Q6 (Tactics) current max: 8 points
   ├─ Q6 actual importance: 0.42 coefficient
   ├─ Recommendation: Reduce Q6 from 8 → 6 max
   │
   ├─ Q17 (Home Advantage) current max: 10 points
   ├─ Q17 actual importance: 0.38 coefficient
   ├─ Recommendation: Reduce Q17 from 10 → 8 max
   │
   └─ Z-Score weights:
      ├─ Current: Technique=0.25, Tactics=0.25, Home/Away=0.10
      ├─ Optimal (ML): Technique=0.28, Tactics=0.18, Home/Away=0.08
      └─ Recommendation: Rebalance Z-Score formula

STAGE 4: Generate Audit Report
├─ Creates: audit_reports/audit_30_losses_[date].pdf
├─ Contains:
│  ├─ Overall performance metrics
│  ├─ Q-ID by Q-ID breakdown
│  ├─ Category performance
│  ├─ League/tier analysis
│  ├─ Pre-filter effectiveness
│  ├─ ML recommendations (with confidence scores)
│  └─ Suggested changes (YOU DECIDE)
│
└─ Saves: audit_reports/audit_30_losses_[date].json

STAGE 5: Notification
└─ Sends you: "System Audit Complete - 30 losses analyzed. Review recommendations."
```

**Key Point: YOU DECIDE**
```
The audit provides RECOMMENDATIONS, not automatic changes.

YOU review the report and decide:
├─ "Yes, reduce Q6 from 8 to 6" → You manually update ANEXO I
├─ "Yes, reduce Home/Away Z-Score weight" → You update YUDOR_MASTER_PROMPT
├─ "No, keep current weights" → Need more data
└─ "Let's test Q6=6 for next 20 matches" → A/B test

Then you can run:
python scripts/master_orchestrator.py update-weights --anexo-i --q6-max 6
```

**Files Created:**
```
✅ audit_reports/audit_30_losses_2025-12-15.pdf
✅ audit_reports/audit_30_losses_2025-12-15.json
✅ audit_reports/ml_model_2025-12-15.pkl (trained model)
```

**Time:** ~10-15 minutes (automatic)

---

## 🔄 **CONTINUOUS LOOP**

After the first audit (30 losses), the cycle continues:

```
Every Weekend:
├─ Pre-Filter (Thursday)
├─ Deep Analysis (Friday)
├─ Bet Decisions (Saturday)
├─ Results Update (Sunday/Monday)
└─ Loss Analysis (Monday)

Every 30 Losses (~every 6-8 weeks at 55% win rate):
└─ System Audit + ML Recommendations
```

---

## 📊 **COMPLETE FILE STRUCTURE AFTER ONE CYCLE**

```
yudor-betting-system/
│
├── matches_all.txt (YOU create weekly)
├── matches_priority.txt (SYSTEM creates)
│
├── scraped_data/
│   ├── FLA_BRA_1125_raw.json (30-40 files per week)
│   ├── INT_LAZ_1125_raw.json
│   └── ...
│
├── consolidated_data/
│   ├── FLA_BRA_1125_consolidated.json (15-20 files per week)
│   ├── INT_LAZ_1125_consolidated.json
│   └── ...
│
├── analysis_history/
│   ├── FLA_BRA_1125_20251122153000.json (15-20 files per week)
│   ├── INT_LAZ_1125_20251122154500.json
│   └── ... (accumulates over time)
│
├── pre_filter_history/
│   ├── 2025-11-22_prefilter.json (1 file per week)
│   ├── 2025-11-29_prefilter.json
│   └── ... (for learning)
│
├── loss_ledger/
│   ├── INT_LAZ_1125_loss_analysis.json (losses only)
│   ├── RMA_BAR_1126_loss_analysis.json
│   └── ... (accumulates until audit)
│
├── audit_reports/
│   ├── audit_30_losses_2025-12-15.pdf
│   ├── audit_30_losses_2025-12-15.json
│   ├── ml_model_2025-12-15.pkl
│   └── ... (every ~6-8 weeks)
│
└── Airtable (cloud):
    ├── Match Analyses table (all games analyzed)
    ├── Bets_Entered table (games you bet on)
    └── Results table (all results + loss analysis)
```

---

## ✅ **VERIFICATION CHECKLIST**

After implementing, verify each connection:

### Data Flow Check
- [ ] matches_all.txt → scraper → scraped_data/ ✅
- [ ] scraped_data/ → data consolidation → consolidated_data/ ✅
- [ ] consolidated_data/ → yudor analysis → analysis_history/ ✅
- [ ] analysis_history/ → Airtable Match Analyses ✅
- [ ] Match Analyses + manual entry → Bets_Entered ✅
- [ ] Bets_Entered + results → Results table ✅
- [ ] Results → loss_ledger/ ✅
- [ ] loss_ledger/ (30 files) → audit_reports/ ✅

### Learning Loop Check
- [ ] Pre-filter history saves all decisions ✅
- [ ] Pre-filter history includes filtered-out games ✅
- [ ] Loss analysis identifies Q-ID failures ✅
- [ ] System audit aggregates all losses ✅
- [ ] ML model trains on historical data ✅
- [ ] Recommendations generated (not auto-applied) ✅

### Long-Term Tracking Check
- [ ] Can query: "Which Q-IDs consistently fail?" ✅
- [ ] Can query: "Was pre-filter threshold optimal?" ✅
- [ ] Can query: "Do filtered-out games have hidden value?" ✅
- [ ] Can query: "Which leagues perform best?" ✅
- [ ] Can query: "Is data quality correlated with win rate?" ✅

---

## 🎯 **ANSWERS TO YOUR SPECIFIC QUESTIONS**

### Q: "Will you save in analysis history?"
**A: YES** - Every analysis saved in `analysis_history/[game_id]_[timestamp].json`

### Q: "What is important for future analysis?"
**A: EVERYTHING** - We save:
1. Original scraped data
2. Data quality scores
3. Pre-filter decisions (selected & rejected)
4. Full Q1-Q19 scores
5. Model predictions
6. Market lines
7. Your bet decisions (entered or not, why)
8. Actual results
9. Loss analysis for losses
10. Pre-filter effectiveness data

### Q: "Saving is important for long term..."
**A: AGREED** - That's why we save:
- `pre_filter_history/` - Track if filter is optimal
- `analysis_history/` - Track all predictions
- `loss_ledger/` - Track all failure modes
- `audit_reports/` - Track system evolution over time

### Q: "Is the system all connected?"
**A: YES** - Complete flow:
```
YOU → matches_all.txt
    ↓
SYSTEM → Pre-filter → matches_priority.txt + history
    ↓
SYSTEM → Deep analysis → Airtable + analysis_history/
    ↓
YOU → Manual bet decisions → Update Airtable
    ↓
YOU → Update results → Airtable Results table
    ↓
SYSTEM → Loss analysis → loss_ledger/ + Airtable
    ↓
SYSTEM (every 30) → Audit → audit_reports/ + recommendations
    ↓
YOU → Review recommendations → Decide to update or not
```

### Q: "System audit would be ML, not prompt-based?"
**A: YES, CORRECT** - The audit uses:
```python
# Python ML (scikit-learn, pandas)
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

# NOT Claude prompt (for accuracy)
# ML can identify:
# - Which Q-IDs actually predict wins
# - Optimal Q-ID weights
# - Category importance
# - Overfitted patterns
```

---

*Complete Workflow v5.3 — Fully Automated with Learning*
