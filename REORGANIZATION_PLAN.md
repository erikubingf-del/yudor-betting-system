# YUDOR SYSTEM - COMPLETE REORGANIZATION PLAN

**Date:** 2025-11-25
**Status:** AWAITING APPROVAL
**Estimated Time:** 90 minutes
**Risk Level:** LOW (all changes are reversible, no code modifications)

---

## 🎯 OBJECTIVES

1. **Eliminate Root Clutter:** Move 60+ legacy .md files to organized archive
2. **Clarify Data Flow:** Rename and organize all data directories with clear purposes
3. **Organize Scripts:** Separate production, utilities, development, and legacy
4. **Single Source of Truth:** Consolidate documentation into `documentation/`
5. **Professional Structure:** GitHub-ready, easy to navigate, zero confusion

---

## 📊 CURRENT STATE ANALYSIS

### Critical Issues
- ✅ 62 markdown files in root (vs industry standard: 3-5)
- ✅ 47 scripts with no organization
- ✅ 11+ data directories with unclear purposes
- ✅ Duplicate/conflicting documentation
- ✅ No READMEs in subdirectories
- ✅ Legacy files mixed with production

### What Works (DON'T BREAK)
- ✅ `master_orchestrator.py` - Main analysis workflow
- ✅ `recalculate_all_yudor_fair_odds_CORRECT.py` - Fair odds calculator
- ✅ Airtable integration (Match Analyses table)
- ✅ `archived_analyses/YYYY-MM-DD/*.json` structure
- ✅ `documentation/` directory (recently created)

---

## 🏗️ PROPOSED NEW STRUCTURE

```
yudor-betting-system/
│
├── README.md                          # Single entry point
├── .env                               # Environment variables
├── .gitignore                         # Git ignore rules
├── requirements.txt                   # Python dependencies
│
├── documentation/                     # ALL user docs here
│   ├── README.md                      # Navigation
│   ├── SYSTEM_OVERVIEW.md             # Complete system guide
│   ├── SCRIPTS_REFERENCE.md           # All scripts explained
│   ├── API_REFERENCE.md               # NEW: API endpoints
│   ├── DATA_FLOW.md                   # NEW: Data pipeline
│   ├── ENVIRONMENT.md                 # NEW: .env setup
│   └── archive/                       # OLD: Legacy docs (60 files)
│
├── scripts/                           # All Python scripts
│   ├── README.md                      # Scripts overview
│   │
│   ├── production/                    # Production-ready scripts
│   │   ├── master_orchestrator.py
│   │   └── recalculate_all_yudor_fair_odds_CORRECT.py
│   │
│   ├── scrapers/                      # Data collection
│   │   ├── scraper.py
│   │   ├── comprehensive_stats_scraper.py
│   │   ├── fbref_stats_integration.py
│   │   ├── formation_scraper.py
│   │   ├── formation_scraper_playwright.py
│   │   └── fotmob_scraper.py
│   │
│   ├── utilities/                     # Helper scripts
│   │   ├── build_team_urls_database.py
│   │   ├── build_sportsmole_urls.py
│   │   ├── build_sofascore_urls.py
│   │   ├── add_brasileirao_urls.py
│   │   ├── validate_airtable_schema.py
│   │   └── organize_analyses.py
│   │
│   ├── airtable/                      # Airtable operations
│   │   ├── check_airtable_status.py
│   │   ├── check_airtable_fields.py
│   │   ├── discover_airtable_schema.py
│   │   ├── sync_all_betting_opportunities.py
│   │   ├── sync_reanalysis_to_airtable.py
│   │   ├── backfill_airtable_fields.py
│   │   └── cleanup_veto_airtable.py
│   │
│   ├── analysis/                      # Analysis workflows
│   │   ├── batch_match_analyzer.py
│   │   ├── complete_match_analyzer.py
│   │   ├── integrated_scraper.py
│   │   ├── process_existing_scrape.py
│   │   ├── post_match_analysis.py
│   │   ├── loss_ledger.py
│   │   ├── ml_calibration.py
│   │   └── q6_formation_scoring.py
│   │
│   ├── development/                   # Testing/development
│   │   ├── test_soccerdata.py
│   │   ├── test_airtable_access.py
│   │   ├── test_fetch.py
│   │   ├── test_q1q19_field.py
│   │   ├── sportsmole_match_finder.py
│   │   ├── team_urls_helper.py
│   │   ├── check_flip_candidates.py
│   │   ├── extract_q_scores_from_archived.py
│   │   └── validate_loss_ledger.py
│   │
│   └── archive/                       # Legacy/one-time scripts
│       ├── recalculate_yudor_fair_odds.py        # OLD version
│       ├── recalculate_ah_lines.py                # OLD version
│       ├── fix_yudor_fair_odds_final.py           # One-time fix
│       ├── simple_ah_calculator.py                 # Legacy
│       ├── yudor_complete_workflow.py             # Superseded
│       ├── yudor_integrated_workflow.py           # Superseded
│       ├── quick_filter.py                        # Legacy
│       └── reset_airtable.py                      # Dangerous
│
├── data/                              # All data files (NEW structure)
│   ├── README.md                      # Data flow explained
│   │
│   ├── raw/                           # Raw scraped data
│   │   └── YYYY-MM-DD/                # Date-organized
│   │       └── {match_id}_raw.json
│   │
│   ├── consolidated/                  # Q1-Q19 processed
│   │   └── YYYY-MM-DD/
│   │       └── {match_id}_consolidated.json
│   │
│   ├── analyses/                      # Complete analyses
│   │   └── YYYY-MM-DD/
│   │       └── {match_id}_analysis.json
│   │
│   ├── archived_analyses/             # OLD structure (keep for recalc script)
│   │   └── 2025-11-21/
│   │       └── {match_id}_analysis.json
│   │
│   └── urls/                          # URL databases
│       ├── team_news_urls_complete.json
│       └── sofascore_team_urls.json
│
├── prompts/                           # LLM prompts
│   ├── YUDOR_MASTER_PROMPT_v5.3.md
│   ├── DATA_CONSOLIDATION_PROMPT_v1.0.md
│   ├── EXTRACTION_PROMPT.md
│   ├── LOSS_LEDGER_ANALYSIS_PROMPT_v1.0.md
│   ├── YUDOR_ANALYSIS_PROMPT.md
│   └── anexos/
│       ├── ANEXO_I_SCORING_CRITERIA.md
│       ├── ANEXO_II_RG_GUARD.md
│       └── ANEXO_III_TACTICAL_EXAMPLES.md
│
├── tests/                             # Unit tests
│   └── test_fair_odds_calculation.py
│
├── config/                            # Configuration files
│   └── (empty - for future use)
│
└── .claude/                           # Claude Code config
    └── (existing files)
```

---

## 📋 EXECUTION PLAN

### PHASE 1: Documentation Cleanup (20 min)
**Goal:** Clean root directory, consolidate docs

**Actions:**
1. Create `documentation/archive/` directory
2. Move 59 legacy .md files to `documentation/archive/`
3. Keep in root:
   - `README.md` (update to point to documentation/)
   - `.env`
   - `.gitignore`
   - `requirements.txt`
4. Create new documentation files:
   - `documentation/API_REFERENCE.md`
   - `documentation/DATA_FLOW.md`
   - `documentation/ENVIRONMENT.md`

**Files to Archive:**
```
AIRTABLE_AUDIT_AND_FIXES.md
AIRTABLE_QUICK_REFERENCE.md
AIRTABLE_RECALCULATION_COMPLETE.md
AIRTABLE_SETUP_GUIDE.md
AUTOMATION_GUIDE.md
CHEATCODE.md
CLI_PREVIEW.md
COMPLETE_AUTOMATION_GUIDE.md
COMPLETE_SYSTEM_ARCHITECTURE.md
COMPLETE_WORKFLOW_SETUP.md
COMPLETE_WORKFLOW_v5.3.md
COMPREHENSIVE_SOURCES_READY.md
DATA_GAPS_AND_IMPROVEMENTS.md
EXECUTIVE_SUMMARY_FINAL.md
FBREF_INTEGRATION_READY.md
FILE_ORGANIZATION.md
FINAL_AIRTABLE_CORRECTION.md
FINAL_STATUS_NOVEMBER_24.md
FINAL_SYSTEM_STATUS.md
FINAL_SYSTEM_SUMMARY.md
FIXES_APPLIED_v5.3.md
FLIP_LOGIC_UPDATE_v5.3.md
FLIP_SYNTHETIC_EDGE_v5.3.md
FORMATION_DATA_SOLUTION.md
FORMATION_INTEGRATION_GUIDE.md
IMPLEMENTATION_STATUS.md
IMPROVEMENTS_IMPLEMENTED.md
INTEGRATION_COMPLETE_GUIDE.md
MASTER_ORCHESTRATOR_SETUP.md
ML_QUICK_START.md
ML_SYSTEM_GUIDE.md
NEW_SOURCES_IMPLEMENTATION_COMPLETE.md
PHASE1_FORMATION_SUMMARY.md
PRODUCTION_READY_CHECKLIST.md
Q1_Q19_STATUS_AND_NEXT_STEPS.md
QUICK_REFERENCE.md
QUICK_START_FORMATIONS.md
QUICK_START_GUIDE.md
QUICK_START_SOCCERDATA.md
README_MASTER.md
README_QUICK_START.md
REANALYSIS_RESULTS_v5.3.md
RISK_MITIGATION_COMPLETED.md
SETUP_CHECKLIST.md
SINGLE_SOURCE_OF_TRUTH.md
SOCCERDATA_ALL_SOURCES.md
SOCCERDATA_FINAL_ANALYSIS.md
SOCCERDATA_IMPLEMENTATION_SUMMARY.md
SOCCERDATA_LIBRARY_ANALYSIS.md
SOFASCORE_INTEGRATION_ANALYSIS.md
SOFASCORE_STATUS.md
START_HERE.md
SYSTEM_STATUS_READY.md
SYSTEM_v5.3_COMPLETE.md
TEST_RESULTS_ESPANYOL_SEVILLA.md
TODAY_TESTING_GUIDE.md
URL_DATABASE_INTEGRATION_GUIDE.md
WHATS_NEW.md
WORKFLOW_SUMMARY.md
YUDOR_FAIR_ODDS_EXPLANATION.md
data_points.md
```

### PHASE 2: Scripts Organization (25 min)
**Goal:** Organize 47 scripts into logical categories

**Actions:**
1. Create script subdirectories
2. Move scripts to appropriate categories
3. Update imports in master_orchestrator.py if needed
4. Create `scripts/README.md`

**Script Categorization:**

**Production (2):**
- `master_orchestrator.py`
- `recalculate_all_yudor_fair_odds_CORRECT.py`

**Scrapers (6):**
- `scraper.py`
- `comprehensive_stats_scraper.py`
- `fbref_stats_integration.py`
- `formation_scraper.py`
- `formation_scraper_playwright.py`
- `fotmob_scraper.py`

**Utilities (6):**
- `build_team_urls_database.py`
- `build_sportsmole_urls.py`
- `build_sofascore_urls.py`
- `add_brasileirao_urls.py`
- `validate_airtable_schema.py`
- `organize_analyses.py`

**Airtable (7):**
- `check_airtable_status.py`
- `check_airtable_fields.py`
- `discover_airtable_schema.py`
- `sync_all_betting_opportunities.py`
- `sync_reanalysis_to_airtable.py`
- `backfill_airtable_fields.py`
- `cleanup_veto_airtable.py`

**Analysis (9):**
- `batch_match_analyzer.py`
- `complete_match_analyzer.py`
- `integrated_scraper.py`
- `process_existing_scrape.py`
- `post_match_analysis.py`
- `loss_ledger.py`
- `ml_calibration.py`
- `q6_formation_scoring.py`

**Development (9):**
- `test_soccerdata.py`
- `test_airtable_access.py`
- `test_fetch.py`
- `test_q1q19_field.py`
- `sportsmole_match_finder.py`
- `team_urls_helper.py`
- `check_flip_candidates.py`
- `extract_q_scores_from_archived.py`
- `validate_loss_ledger.py`

**Archive (8):**
- `recalculate_yudor_fair_odds.py`
- `recalculate_ah_lines.py`
- `fix_yudor_fair_odds_final.py`
- `simple_ah_calculator.py`
- `yudor_complete_workflow.py`
- `yudor_integrated_workflow.py`
- `quick_filter.py`
- `reset_airtable.py`

### PHASE 3: Data Directory Reorganization (20 min)
**Goal:** Clear, logical data organization

**Actions:**
1. Create `data/` directory structure
2. Move/symlink existing data
3. Create `data/README.md` with flow diagram
4. Keep `archived_analyses/` as-is (critical for recalc script)

**Directory Mapping:**
```
OLD → NEW
scraped_data/ → data/raw/
consolidated_data/ → data/consolidated/
analysis_history/ → DELETE (legacy format)
ah_calculations/ → DELETE (superseded by archived_analyses)
archived_analyses/ → KEEP AS-IS (used by recalc script)
team_news_urls_complete.json → data/urls/
sofascore_team_urls.json → data/urls/
```

### PHASE 4: New Documentation (15 min)
**Goal:** Complete, professional documentation

**Create These Files:**

**1. `documentation/API_REFERENCE.md`**
- Anthropic Claude API
- Airtable API (schema, endpoints)
- FootyStats API
- FBRef/soccerdata
- SportsMole/SofaScore scraping

**2. `documentation/DATA_FLOW.md`**
- Complete pipeline diagram
- Directory purposes
- File naming conventions
- Data retention policy

**3. `documentation/ENVIRONMENT.md`**
- All environment variables
- .env.example template
- API key setup instructions
- Security best practices

**4. `scripts/README.md`**
- Production scripts usage
- Utility scripts reference
- Development workflows
- Archive explanations

**5. `data/README.md`**
- Data flow diagram
- Directory structure
- File formats
- Cleanup procedures

**6. Root `README.md` (rewrite)**
```markdown
# YUDOR Betting Analysis System

Professional football betting analysis using Q1-Q19 scoring, Asian Handicap calculations, and machine learning calibration.

## Quick Start
1. Install: `pip install -r requirements.txt`
2. Configure: Copy `.env.example` to `.env` and add API keys
3. Analyze: `python scripts/production/master_orchestrator.py analyze "Team A vs Team B, League, DD/MM/YYYY"`

## Documentation
- [System Overview](documentation/SYSTEM_OVERVIEW.md) - Complete system guide
- [Scripts Reference](documentation/SCRIPTS_REFERENCE.md) - All scripts explained
- [API Reference](documentation/API_REFERENCE.md) - External APIs
- [Data Flow](documentation/DATA_FLOW.md) - Data pipeline
- [Environment Setup](documentation/ENVIRONMENT.md) - Configuration

## Project Structure
- `scripts/production/` - Main analysis scripts
- `scripts/scrapers/` - Data collection
- `scripts/utilities/` - Helper tools
- `data/analyses/` - Match analyses (organized by date)
- `prompts/` - LLM prompts
- `documentation/` - All guides and references

See [documentation/README.md](documentation/README.md) for full navigation.
```

### PHASE 5: Testing & Validation (10 min)
**Goal:** Ensure nothing broke

**Tests:**
1. Run `python scripts/production/master_orchestrator.py --help`
2. Run `python scripts/production/recalculate_all_yudor_fair_odds_CORRECT.py` (dry run)
3. Check Airtable connection
4. Verify `archived_analyses/` still accessible
5. Test one full analysis workflow

---

## ⚠️ SAFETY MEASURES

### Backup Strategy
```bash
# Before starting, create backup
cd /Users/erikfigueiredo/Documents/GitHub/yudor-betting-system
tar -czf ../yudor_backup_$(date +%Y%m%d_%H%M%S).tar.gz .
```

### Rollback Plan
If anything breaks:
1. Stop immediately
2. Extract backup: `tar -xzf ../yudor_backup_*.tar.gz`
3. Report issue
4. Fix and retry

### No-Modification Rule
- Zero changes to Python code logic
- Zero changes to existing JSON data
- Only move/rename/organize files
- All imports updated carefully

---

## 📊 EXPECTED RESULTS

### Before
```
Root directory: 90+ files (cluttered, confusing)
Scripts: 47 files mixed together
Documentation: Scattered, duplicated, outdated
Data: 11 directories with unclear purposes
```

### After
```
Root directory: 5 files (clean, professional)
Scripts: Organized into 7 logical categories
Documentation: Single source of truth in documentation/
Data: Clear flow from raw → consolidated → analyses
```

### Benefits
1. ✅ **Onboarding:** New developers understand structure in 5 minutes
2. ✅ **Maintenance:** Easy to find and update files
3. ✅ **Professional:** GitHub-ready, investor-presentable
4. ✅ **Scalable:** Clear patterns for adding new features
5. ✅ **Safe:** Zero risk to production workflows

---

## 🚦 APPROVAL CHECKLIST

Before proceeding, confirm:
- [ ] Backup created
- [ ] Critical workflows identified (master_orchestrator, recalculation)
- [ ] Understand all changes are file movements, not code edits
- [ ] Ready to test after each phase
- [ ] Have 90 minutes for full execution

---

## ✅ NEXT STEPS

1. **REVIEW THIS PLAN** - Confirm structure makes sense
2. **APPROVE EXECUTION** - Give go-ahead to proceed
3. **EXECUTE PHASES 1-5** - Complete reorganization
4. **VALIDATE WORKFLOWS** - Test everything works
5. **COMMIT CHANGES** - Git commit with clear message

**Estimated Total Time:** 90 minutes
**Risk Level:** LOW (reversible, no code changes)
**Impact:** HIGH (professional, maintainable codebase)
