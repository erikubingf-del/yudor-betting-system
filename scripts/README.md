# Scripts Directory - Overview

Organized collection of all YUDOR system scripts, categorized by function.

---

## 📁 Directory Structure

```
scripts/
├── production/       # Production-ready analysis scripts
├── scrapers/         # Data collection from external sources
├── utilities/        # Helper scripts and tools
├── airtable/         # Airtable database operations
├── analysis/         # Analysis workflows and engines
├── development/      # Testing and development tools
└── archive/          # Legacy/deprecated scripts
```

---

## 🎯 Production Scripts

**Location:** `production/`
**Purpose:** Core system functionality

### master_orchestrator.py
Complete betting analysis orchestrator.
```bash
python scripts/production/master_orchestrator.py analyze "Team A vs Team B, League, DD/MM/YYYY"
```

### recalculate_all_yudor_fair_odds_CORRECT.py
Recalculate fair odds for all Airtable records.
```bash
python scripts/production/recalculate_all_yudor_fair_odds_CORRECT.py
```

---

## 🌐 Scraper Scripts

**Location:** `scrapers/`
**Purpose:** Collect data from external sources

- **scraper.py** - Main data scraping orchestrator
- **comprehensive_stats_scraper.py** - Team statistics scraper
- **fbref_stats_integration.py** - FBRef integration
- **formation_scraper.py** - Formation data (basic)
- **formation_scraper_playwright.py** - Formation data (JavaScript-heavy)
- **fotmob_scraper.py** - FotMob data scraper

---

## 🔧 Utility Scripts

**Location:** `utilities/`
**Purpose:** Helper tools and setup

- **build_team_urls_database.py** - Build URL database for teams
- **build_sportsmole_urls.py** - SportsMole URL builder
- **build_sofascore_urls.py** - SofaScore URL builder
- **add_brasileirao_urls.py** - Add Brazilian league URLs
- **validate_airtable_schema.py** - Validate Airtable structure
- **organize_analyses.py** - Organize archived analyses

---

## 📊 Airtable Scripts

**Location:** `airtable/`
**Purpose:** Database operations

- **check_airtable_status.py** - Check connection status
- **check_airtable_fields.py** - Verify field structure
- **discover_airtable_schema.py** - Auto-discover schema
- **sync_all_betting_opportunities.py** - Sync betting data
- **sync_reanalysis_to_airtable.py** - Sync reanalysis results
- **backfill_airtable_fields.py** - Backfill missing data
- **cleanup_veto_airtable.py** - Clean VETO decisions

---

## 🧮 Analysis Scripts

**Location:** `analysis/`
**Purpose:** Analysis workflows and engines

- **batch_match_analyzer.py** - Batch analysis from CSV
- **complete_match_analyzer.py** - Complete single match analysis
- **integrated_scraper.py** - Integrated scraping workflow
- **process_existing_scrape.py** - Process pre-scraped data
- **post_match_analysis.py** - Post-match result analysis
- **loss_ledger.py** - Track losses and patterns
- **ml_calibration.py** - Machine learning calibration
- **q6_formation_scoring.py** - Q6 formation scoring

---

## 🧪 Development Scripts

**Location:** `development/`
**Purpose:** Testing and validation

- **test_soccerdata.py** - Test soccerdata library
- **test_airtable_access.py** - Test Airtable connection
- **test_fetch.py** - Test web fetching
- **test_q1q19_field.py** - Test Q1-Q19 fields
- **sportsmole_match_finder.py** - Find SportsMole matches
- **team_urls_helper.py** - URL helper utilities
- **check_flip_candidates.py** - Check FLIP scenarios
- **extract_q_scores_from_archived.py** - Extract Q scores
- **validate_loss_ledger.py** - Validate loss tracking

---

## 🗄️ Archive Scripts

**Location:** `archive/`
**Purpose:** Legacy/deprecated scripts (DO NOT USE)

- ❌ recalculate_yudor_fair_odds.py (OLD - use CORRECT version)
- ❌ recalculate_ah_lines.py (OLD)
- ❌ fix_yudor_fair_odds_final.py (ONE-TIME FIX)
- ❌ simple_ah_calculator.py (LEGACY)
- ❌ yudor_complete_workflow.py (SUPERSEDED)
- ❌ yudor_integrated_workflow.py (SUPERSEDED)
- ❌ quick_filter.py (LEGACY)
- ⚠️ reset_airtable.py (DANGEROUS - deletes all data)

---

## 🚀 Common Workflows

### Analyze New Match
```bash
python scripts/production/master_orchestrator.py analyze "Flamengo vs Bragantino, Brasileirão, 25/11/2025"
```

### Batch Analysis
```bash
# Create CSV with matches
python scripts/analysis/batch_match_analyzer.py matches.csv
```

### Recalculate Fair Odds
```bash
python scripts/production/recalculate_all_yudor_fair_odds_CORRECT.py
```

### Build URL Database
```bash
python scripts/utilities/build_team_urls_database.py --league "Premier League"
```

### Validate Airtable
```bash
python scripts/utilities/validate_airtable_schema.py
```

---

## 📝 Development Guidelines

### Adding New Scripts

1. **Choose Correct Directory**
   - Production: Core functionality, used regularly
   - Scrapers: Data collection
   - Utilities: One-time setup or helpers
   - Airtable: Database operations
   - Analysis: Workflows and engines
   - Development: Testing only

2. **Naming Convention**
   - Use snake_case: `my_new_script.py`
   - Be descriptive: `build_premier_league_urls.py` not `script.py`

3. **Add Docstring**
   ```python
   #!/usr/bin/env python3
   """
   Brief description of what script does

   Usage:
       python scripts/category/my_script.py [args]
   """
   ```

4. **Update Documentation**
   - Add entry to this README
   - Update [SCRIPTS_REFERENCE.md](../documentation/SCRIPTS_REFERENCE.md)

### Path Handling

Scripts in subdirectories must navigate to project root:
```python
from pathlib import Path

# For scripts in scripts/production/
ROOT = Path(__file__).parent.parent.parent
env_file = ROOT / '.env'
archived_dir = ROOT / 'archived_analyses'

# For scripts in scripts/utilities/
ROOT = Path(__file__).parent.parent.parent
```

---

## 🔍 Finding Scripts

**By Function:**
- Need to analyze? → `production/`
- Need to scrape? → `scrapers/`
- Need to test? → `development/`
- Need Airtable ops? → `airtable/`

**By Name:**
```bash
# Search all scripts
find scripts/ -name "*pattern*.py"

# List all in category
ls scripts/production/
```

---

## ⚠️ Important Notes

1. **Always use production/recalculate_all_yudor_fair_odds_CORRECT.py**
   - NOT the one in archive/
   - The CORRECT version has the right probability normalization

2. **Don't run archive/ scripts**
   - They're kept for reference only
   - May break current system

3. **Test with development/ first**
   - Before running production scripts
   - Especially for Airtable operations

---

For detailed documentation on each script, see [SCRIPTS_REFERENCE.md](../documentation/SCRIPTS_REFERENCE.md)

**Last Updated:** 2025-11-25
**Version:** 2.0.0
