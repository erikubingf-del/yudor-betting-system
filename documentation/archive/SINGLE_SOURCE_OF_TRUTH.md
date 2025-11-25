# YUDOR System - Single Source of Truth

**Last Updated:** November 24, 2025
**Status:** Production Ready ✅

---

## The ONE Command You Need

For **weekend betting workflow**, use ONLY this:

```bash
python3 scripts/master_orchestrator.py analyze-fbref "Team A vs Team B, League, DD/MM/YYYY"
```

**This is the CANONICAL entrypoint.** All other scripts are either:
- Development/testing tools
- Deprecated workflows
- Sub-components called by master_orchestrator

---

## Complete Weekend Workflow

### Friday Evening: Identify Matches
```bash
# 1. Check upcoming matches (manual step - use sofascore.com or similar)
# 2. List potential targets based on league coverage
```

### Saturday Morning: Analyze Matches
```bash
# For each match:
python3 scripts/master_orchestrator.py analyze-fbref "Brighton vs Brentford, Premier League, 22/11/2025"

# This will:
# ✅ Scrape all data sources
# ✅ Run Q1-Q19 consolidation
# ✅ Calculate YUDOR AH Fair + Fair Odds (CORRECT formula)
# ✅ Determine CORE/EXP/VETO decision
# ✅ Save to Airtable automatically
```

### Saturday Afternoon: Review & Bet
```bash
# 1. Open Airtable → "Match Analyses" table
# 2. Filter by: Status = "ANALYZED", Decision = "CORE"
# 3. For each CORE bet:
#    - Yudor AH Team: Who to bet on
#    - Yudor AH Fair: Fair handicap line
#    - Yudor Fair Odds: Fair odds at that line
#    - Compare with market odds
#    - Calculate edge: (Fair Odds / Market Odds - 1) × 100
# 4. If edge > 5%: Place bet in Bet Records table
```

### Sunday Evening: Record Results
```bash
# 1. Open Airtable → "Bet Records"
# 2. For each bet:
#    - Final Score: "2-1"
#    - AH Result: WIN/LOSS/PUSH/HALF
#    - P/L: Actual profit/loss
# 3. Formulas auto-calculate: CLV %, ROI %
```

### Monday: Learning Analysis
```bash
# Analyze losses (and wins for patterns)
python3 scripts/master_orchestrator.py analyze-loss --match-id "MatchID_DDMMYYYY"

# This will:
# ✅ Identify which Q-IDs failed
# ✅ Classify error type (Model/Data/Variance)
# ✅ Save to Learning Ledger
# ✅ Suggest methodology improvements
```

---

## Other Scripts - When to Use Them

### ⚠️ DO NOT USE (Deprecated/Testing Only)

| Script | Status | Use Master Orchestrator Instead |
|--------|--------|-------------------------------|
| `yudor_integrated_workflow.py` | Deprecated | ✅ `master_orchestrator.py analyze-fbref` |
| `complete_match_analyzer.py` | Sub-component | Called internally by master_orchestrator |
| `run_q1_q19_analysis.py` | Development | ✅ `master_orchestrator.py analyze-fbref` |
| `manual_quick_start_workflow.py` | Obsolete | ✅ `master_orchestrator.py analyze-fbref` |

### ✅ UTILITY SCRIPTS (Safe to Use)

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `fix_yudor_fair_odds_final.py` | Fix odds calculation | One-time migration (already done) |
| `extract_q_scores_from_archived.py` | Extract Q scores | One-time migration (already done) |
| `backfill_airtable_fields.py` | Backfill missing fields | One-time migration (already done) |

---

## System Architecture - Simple View

```
User Input: "Brighton vs Brentford, Premier League, 22/11/2025"
      ↓
master_orchestrator.py (ONLY ENTRYPOINT)
      ↓
├─ Phase 1: complete_match_analyzer.py (scrape data)
├─ Phase 2: Q1-Q19 consolidation (via Claude API)
├─ Phase 3: YUDOR analysis (calculate AH, decision)
└─ Phase 4: Save to Airtable
      ↓
Airtable: Match Analyses table
      ↓
User: Review, decide, place bets
      ↓
Airtable: Bet Records table
      ↓
After results: analyze-loss (learning)
      ↓
Airtable: Learning Ledger table
```

---

## Fair Odds Formula - Current Implementation

### ⚠️ WARNING: Two Different Formulas Exist

**OLD (WRONG) - in backfill_airtable_fields.py line 117:**
```python
yudor_fair_odds = 2.0 - (ah_fair * 0.4)  # Approximation, not accurate
```

**NEW (CORRECT) - in fix_yudor_fair_odds_final.py:**
```python
# 1. Get probabilities as percentages (e.g., 36.2%)
# 2. Moneyline odds = 100 / favorite_percentage
# 3. At line -0.5: odds = moneyline
# 4. For each +0.25 step: multiply by 0.85
# 5. For each -0.25 step: multiply by 1.15
# 6. Result: Actual odds at specific AH line
```

**Status:** All 35 matches now use CORRECT formula (fixed 2025-11-24)

**Action Required:** Update master_orchestrator.py to use CORRECT formula for future analyses

---

## Data Quality Validation - Quantified Thresholds

### Minimum Requirements (Enforced)

```python
# In master_orchestrator.py (already implemented)
MIN_SOURCES = 5  # Minimum data sources required
MIN_DATA_QUALITY = 60  # Minimum quality score (0-100)

# Quality score calculation:
# - 5+ sources = 100%
# - 4 sources = 80%
# - 3 sources = 60%
# - 2 sources = 40% (VETO)
# - 1 source = 20% (VETO)
```

### Auto-VETO Triggers

1. **Data Quality < 60%**: Not enough sources
2. **R-Score > 0.4**: Too many risk signals
3. **Tier 3**: Low confidence prediction
4. **Missing key data**: Formation, injury, recent form

---

## Error Handling - Current Status

### ⚠️ NEEDS IMPROVEMENT: Claude API Calls

**Current:** No retry logic, rate limiting, or fallback

**Recommended Addition:**
```python
# Add to master_orchestrator.py
import time
from anthropic import APIError, RateLimitError

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def call_claude_with_retry(prompt, max_retries=MAX_RETRIES):
    for attempt in range(max_retries):
        try:
            response = client.messages.create(...)
            return response
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                print(f"⚠️  Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
        except APIError as e:
            print(f"❌ API Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise
```

**Action Required:** Add this to master_orchestrator.py

---

## Testing - Documented Test Plan

### Current Gap: No automated tests for core workflows

**Recommended Test Suite:**

```bash
# Create tests/test_master_orchestrator.py

# Test 1: End-to-end analysis
python3 -m pytest tests/test_master_orchestrator.py::test_analyze_match

# Test 2: Fair odds calculation
python3 -m pytest tests/test_fair_odds_calculation.py

# Test 3: Data quality validation
python3 -m pytest tests/test_data_quality.py

# Test 4: Airtable integration
python3 -m pytest tests/test_airtable_save.py
```

**Action Required:** Create test suite (not critical for production use, but important for maintenance)

---

## Airtable Schema - Version Control

### Current Risk: Schema drift without validation

**Recommended Solution:**

```bash
# Create scripts/validate_airtable_schema.py
# Run before each analysis to ensure schema matches expectations

python3 scripts/validate_airtable_schema.py

# Expected output:
# ✅ Match Analyses: 22 fields (all present)
# ✅ Bet Records: 19 fields (all present)
# ✅ Learning Ledger: 8 fields (all present)
# ✅ All formulas valid
# ✅ All links configured correctly
```

**Action Required:** Create schema validation script

---

## Documentation - Consolidation Plan

### Current: Scattered across 10+ files

**Recommended Structure:**

```
/docs
├── 01_GETTING_STARTED.md (← Consolidate README + QUICK_START)
├── 02_WEEKEND_WORKFLOW.md (← THIS FILE - single source of truth)
├── 03_AIRTABLE_SETUP.md (← Existing AIRTABLE_SETUP_GUIDE.md)
├── 04_FAIR_ODDS_EXPLAINED.md (← Existing YUDOR_FAIR_ODDS_EXPLANATION.md)
├── 05_LEARNING_SYSTEM.md (← Consolidate loss ledger guides)
└── 06_TROUBLESHOOTING.md (← Common issues + solutions)

/archive (move old docs here)
├── FINAL_SYSTEM_SUMMARY.md
├── PRODUCTION_READY_CHECKLIST.md
├── SYSTEM_STATUS_READY.md
└── ... (other legacy docs)
```

**Action Required:** Consolidate documentation

---

## Summary - Priority Actions

### 🔴 CRITICAL (Do Before Next Analysis)
1. ✅ Use only `master_orchestrator.py analyze-fbref` (already the standard)
2. ⚠️ Update master_orchestrator.py to use CORRECT fair odds formula
3. ⚠️ Add Claude API retry logic

### 🟡 HIGH PRIORITY (Do This Week)
4. Create schema validation script
5. Document quantified data quality thresholds
6. Consolidate documentation into /docs folder

### 🟢 MEDIUM PRIORITY (Do This Month)
7. Create automated test suite
8. Add batch analysis retry logic
9. Create troubleshooting guide

### ⚪ LOW PRIORITY (Nice to Have)
10. Archive deprecated scripts
11. Add logging/monitoring
12. Create performance benchmarks

---

## The ONE Rule

**When in doubt, use:**
```bash
python3 scripts/master_orchestrator.py analyze-fbref "Team A vs Team B, League, DD/MM/YYYY"
```

Everything else is either a sub-component or a utility script.

---

**Questions? Check:**
1. This file (SINGLE_SOURCE_OF_TRUTH.md)
2. YUDOR_FAIR_ODDS_EXPLANATION.md (for odds methodology)
3. AIRTABLE_SETUP_GUIDE.md (for Airtable structure)

**For issues:** Open GitHub issue or check master_orchestrator.py code
