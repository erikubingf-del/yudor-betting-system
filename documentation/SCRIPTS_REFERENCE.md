# YUDOR Scripts Reference Guide

Complete reference for all operational scripts in the system.

---

## Core Production Scripts

### master_orchestrator.py
**Location:** `scripts/master_orchestrator.py`
**Purpose:** Main workflow orchestrator for match analysis
**Status:** Production

**Usage:**
```bash
python3 scripts/master_orchestrator.py analyze-fbref "Team A vs Team B, League, DD/MM/YYYY"
```

**Functions:**
- Coordinates entire analysis pipeline
- Calls scrapers → LLM analysis → consolidation → Airtable update
- Saves results to archived_analyses/

**Key Parameters:**
- Match string format: "Home vs Away, League, DD/MM/YYYY"
- Automatically detects league and fetches appropriate data sources

---

### recalculate_all_yudor_fair_odds_CORRECT.py
**Location:** `scripts/recalculate_all_yudor_fair_odds_CORRECT.py`
**Purpose:** Recalculate fair odds for all matches using correct methodology
**Status:** Production ✅ (Recently fixed - 2025-11-25)

**Usage:**
```bash
python3 scripts/recalculate_all_yudor_fair_odds_CORRECT.py
```

**What it does:**
1. Reads all records from Airtable "Match Analyses"
2. Extracts raw data from `archived_analyses/*.json`
3. Recalculates normalized probabilities (correct formula)
4. Finds AH line closest to odds 2.0
5. Preserves FLIP scenarios from archived data
6. Updates Airtable with corrected values

**Critical Functions:**
```python
calculate_correct_probabilities(raw_casa, raw_vis, pr_empate)
# → Normalizes to 100%, distributes difference equally

find_ah_line_closest_to_2(fav_prob_pct)
# → Searches AH -3.0 to 0.0 for line closest to 2.0 odds

calculate_odds_at_line(fav_prob_pct, ah_line)
# → Calculates odds at specific AH using ±15% scaling

determine_yudor_ah_team(home, away, pr_casa, pr_vis, ah_line)
# → Determines which team to bet on based on AH sign
```

**Recent Fixes:**
- ✅ Now checks AH -0.25 (was missing, causing Inter Milan bug)
- ✅ Preserves FLIP scenarios (FC Köln +1.25)
- ✅ Correct probability normalization

---

## Data Collection Scripts

### comprehensive_stats_scraper.py
**Location:** `scripts/comprehensive_stats_scraper.py`
**Purpose:** Scrape stats from FBRef and FootyStats
**Status:** Production

**Data Sources:**
- FBRef: Team stats, xG, xGA, player values
- FootyStats: Form, rankings, odds

**Supported Leagues:**
- Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Brasileirão

---

### fbref_stats_integration.py
**Location:** `scripts/fbref_stats_integration.py`
**Purpose:** FBRef-specific scraping and integration
**Status:** Utility

**Features:**
- Season-specific data extraction
- Match-by-match stats
- Player performance metrics

---

### formation_scraper.py
**Location:** `scripts/formation_scraper.py`
**Purpose:** Scrape team formations and tactical setups
**Status:** Experimental

**Note:** Formation data often unavailable pre-match, used for Q6 scoring when available.

---

## Validation & Maintenance Scripts

### validate_airtable_schema.py
**Location:** `scripts/validate_airtable_schema.py`
**Purpose:** Validate Airtable schema matches code expectations
**Status:** Production

**Usage:**
```bash
python3 scripts/validate_airtable_schema.py
```

**Checks:**
- All 3 tables exist (Match Analyses, Bet Records, Learning Ledger)
- Required fields present
- Field types match expectations
- Links between tables valid

**Expected Schema:**
```python
"Match Analyses": {
    "Yudor AH Fair", "Yudor Fair Odds", "Yudor AH Team",
    "Yudor Decision", "CS Final", "R Score", "Tier",
    "Data Quality", "Q1-Q19 Scores", "Full Analysis"
}
```

---

### backfill_airtable_fields.py
**Location:** `scripts/backfill_airtable_fields.py`
**Purpose:** Add missing fields to existing Airtable records
**Status:** Maintenance utility

**Use cases:**
- Adding new calculated fields to old records
- Updating schema after field additions
- Data migration

---

### reset_airtable.py
**Location:** `scripts/reset_airtable.py`
**Purpose:** Clear Airtable for fresh start
**Status:** Dangerous - use with caution ⚠️

**Warning:** Deletes all records. Only use for testing/development.

---

## Analysis & Calculation Scripts

### simple_ah_calculator.py
**Location:** `scripts/simple_ah_calculator.py`
**Purpose:** Standalone AH odds calculator
**Status:** Utility

**Usage:**
```bash
python3 scripts/simple_ah_calculator.py
```

**Features:**
- Interactive calculator
- Test fair odds formulas
- Verify manual calculations

---

### q6_formation_scoring.py
**Location:** `scripts/q6_formation_scoring.py`
**Purpose:** Score formations for Q6 (tactical matchups)
**Status:** Specialized utility

**Logic:**
- Compares home vs away formations
- Identifies tactical advantages
- Returns Q6 score differential

---

## Legacy/Deprecated Scripts

### yudor_complete_workflow.py
**Status:** Deprecated
**Replaced by:** master_orchestrator.py
**Note:** Keep for reference only

### recalculate_yudor_fair_odds.py (without CORRECT suffix)
**Status:** Deprecated ❌
**Replaced by:** recalculate_all_yudor_fair_odds_CORRECT.py
**Note:** Had wrong normalization logic - DO NOT USE

---

## Experimental Scripts

### loss_ledger.py
**Location:** `scripts/loss_ledger.py`
**Purpose:** Track bet outcomes for learning
**Status:** In development

**Future use:**
- Record actual match results
- Calculate ROI
- Identify patterns in losses

### validate_loss_ledger.py
**Purpose:** Validate loss ledger data integrity
**Status:** Companion to loss_ledger.py

---

## Utility Scripts

### build_team_urls_database.py
**Purpose:** Build database of team news URLs
**Status:** Development helper

### add_brasileirao_urls.py
**Purpose:** Add Brasileirão team URLs to database
**Status:** League-specific utility

### batch_match_analyzer.py
**Purpose:** Analyze multiple matches from CSV
**Status:** Batch processing utility

---

## Script Dependency Map

```
master_orchestrator.py
├── comprehensive_stats_scraper.py
├── fbref_stats_integration.py
├── formation_scraper.py (optional)
└── [Airtable update functions]

recalculate_all_yudor_fair_odds_CORRECT.py
├── Reads: archived_analyses/*.json
├── Reads: Airtable "Match Analyses"
└── Updates: Airtable "Match Analyses"

validate_airtable_schema.py
└── Reads: Airtable schema only
```

---

## Common Workflows

### New Match Analysis
```bash
# 1. Run full analysis
python3 scripts/master_orchestrator.py analyze-fbref "Real Madrid vs Barcelona, La Liga, 25/11/2025"

# 2. Verify in Airtable
# Check: Yudor AH Fair, Fair Odds, Decision

# 3. If odds seem wrong, recalculate
python3 scripts/recalculate_all_yudor_fair_odds_CORRECT.py
```

### System Validation
```bash
# 1. Validate Airtable schema
python3 scripts/validate_airtable_schema.py

# 2. Recalculate all fair odds
python3 scripts/recalculate_all_yudor_fair_odds_CORRECT.py

# 3. Check for errors in output
```

### Testing Fair Odds Calculation
```bash
# Manual calculation testing
python3 scripts/simple_ah_calculator.py

# Or use test script
python3 tests/test_fair_odds_calculation.py
```

---

## Development Guidelines

### Before Running Production Scripts:
1. ✅ Check `.env` has API keys
2. ✅ Validate Airtable schema
3. ✅ Test on single match first
4. ✅ Review archived_analyses/ exists

### When Creating New Scripts:
1. Follow naming convention: `verb_noun.py`
2. Add docstring with purpose and usage
3. Include error handling
4. Log to console with clear messages
5. Add to this reference document

### When Modifying Existing Scripts:
1. Test locally first
2. Keep backup of original
3. Update this documentation
4. Add migration notes if breaking changes

---

**Last Updated:** 2025-11-25
**Maintained By:** System Architect
