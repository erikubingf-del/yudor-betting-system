# 🤖 YUDOR v5.3 - AUTOMATION GUIDE

## ✅ **YOU NOW HAVE FULL AUTOMATION!**

All 3 commands are implemented and ready to use THIS WEEKEND.

---

## 🚀 **COMPLETE AUTOMATED WORKFLOW**

### **Thursday Evening: Pre-Filter (5 minutes)**

```bash
# 1. Create matches_all.txt with 30-40 weekend games
# Format: Team1 vs Team2, League, DD/MM/YYYY, HH:MM

# 2. Run pre-filter command
python scripts/master_orchestrator.py pre-filter
```

**What it does:**
- ✅ Scrapes URLs for all 30-40 games
- ✅ Calculates data quality score (0-100) for each game
- ✅ Filters games by quality threshold (≥70/100)
- ✅ Creates `matches_priority.txt` with top 15-20 games
- ✅ Saves pre-filter history for learning

**Output:**
- `matches_priority.txt` - Ready for analysis
- `match_data_v29.json` - Scraped URLs
- `pre_filter_history/pre_filter_TIMESTAMP.json` - Full report

**Time:** ~5 minutes (automatic scraping + quality calculation)

---

### **Friday Morning: Batch Analysis (10-15 minutes)**

```bash
# Run complete v5.3 analysis on priority games
python scripts/master_orchestrator.py analyze-batch
```

**What it does:**
- ✅ Loads priority games from `matches_priority.txt`
- ✅ For each game:
  - Runs DATA_CONSOLIDATION_PROMPT (fills Q1-Q19 with deterministic rules)
  - Runs YUDOR_MASTER_PROMPT_v5.3 (3-layer analysis: Pricing → Confidence → RG Guard)
  - Calculates fair AH line, CS_final, R-Score
  - Applies decision logic (CORE/EXP/VETO/FLIP/IGNORAR)
  - Saves consolidated data + analysis
  - Saves to Airtable automatically

**Output:**
- `consolidated_data/MATCH_ID_consolidated.json` - Data with Q1-Q19 scores
- `analysis_history/MATCH_ID_analysis.json` - Complete v5.3 analysis
- Airtable "Match Analyses" table - Updated automatically

**Time:** ~10-15 minutes for 15-20 games (fully automated, just wait)

**Terminal Output:**
```
[1/15] ANALYZING: Mainz 05 vs Hoffenheim
  📊 RESULTS:
     Fair AH Line: -0.75
     Fair Odds: 2.01
     Decision: CORE
     CS_final: 82
     R-Score: 0.14
     Tier: 1
  ✅ Saved to Airtable

[2/15] ANALYZING: Valencia vs Levante
...
```

---

### **Friday Afternoon: Edge Calculation (Manual - 30 minutes)**

```bash
# Check each game in Airtable and compare to Betfair odds
# Calculate edge% manually for now
```

**Process:**
1. Open Airtable "Match Analyses" table
2. For each game, see Yudor's fair line (e.g., -0.75)
3. Check Betfair for market line (e.g., -0.50)
4. Calculate edge: If market offers better line = POSITIVE edge
5. Enter bets with ≥8% edge

**Time:** ~2 minutes per game (30 minutes for 15 games)

---

### **Monday After Weekend: Loss Analysis (5 minutes)**

```bash
# Automatically analyze all losses from weekend
python scripts/master_orchestrator.py loss-analysis --auto
```

**What it does:**
- ✅ Queries Airtable "Results" table for losses without analysis
- ✅ For each loss:
  - Loads original analysis from `analysis_history/`
  - Runs LOSS_LEDGER_ANALYSIS_PROMPT for root cause analysis
  - Identifies which Q-IDs failed
  - Classifies error type (Model Error, Data Error, Variance)
  - Saves to `loss_ledger/`
  - Updates Airtable Results table automatically

**Output:**
- `loss_ledger/MATCH_ID_loss_TIMESTAMP.json` - Complete forensic analysis
- Airtable "Results" table - Updated with error_category, error_type, notes

**Time:** ~5 minutes (fully automated)

**Terminal Output:**
```
[1/3] ANALYZING LOSS: Mainz05vsHoffenheim_21112025
  📊 ORIGINAL PREDICTION:
     Decision: CORE
     Fair Line: -0.75
     CS_final: 82
     R-Score: 0.14

  📉 ACTUAL RESULT:
     Score: 1-2
     Outcome: LOSS

  📊 ANALYSIS RESULTS:
     Error Type: Model Error
     Error Category: Q6: Tactics - Formation matchup failed
     Failed Q-IDs: Q6, Q9
     Root Cause: Mainz's 4-3-3 didn't dominate as predicted...
  ✅ Updated Airtable Results table
```

---

## 📊 **AUTOMATION SUMMARY**

| Phase | Command | Automation | Time | Manual Work |
|:---|:---|:---:|---:|:---|
| **Thursday: Pre-filter** | `pre-filter` | 95% | 5 min | Create matches_all.txt |
| **Friday: Analysis** | `analyze-batch` | 100% | 10-15 min | None - fully automated! |
| **Friday: Edge calc** | Manual | 0% | 30 min | Check Betfair, calculate edge |
| **Saturday: Bet entry** | Manual | 0% | 15 min | Enter bets on Betfair |
| **Sunday: Results** | Manual | 0% | 10 min | Update Airtable Results |
| **Monday: Loss analysis** | `loss-analysis --auto` | 100% | 5 min | None - fully automated! |
| **TOTAL** | | **80%** | **1.5 hours** | vs 6-8 hours manual |

**Time saved: 5-6 hours per weekend!**

---

## 🎯 **COMMAND REFERENCE**

### **1. pre-filter**

```bash
# Default (uses matches_all.txt)
python scripts/master_orchestrator.py pre-filter

# Custom input file
python scripts/master_orchestrator.py pre-filter --input my_matches.txt
```

**Options:**
- `--input FILE` - Specify input file (default: `matches_all.txt`)

**Requirements:**
- Input file must exist with match format:
  ```
  Mainz 05 vs Hoffenheim, Bundesliga, 21/11/2025, 20:30
  Valencia vs Levante, La Liga, 21/11/2025, 21:00
  ```

**Output:**
- `matches_priority.txt` - Filtered priority games
- `match_data_v29.json` - Scraped URLs
- `pre_filter_history/` - History logs

---

### **2. analyze-batch**

```bash
# Default (uses matches_priority.txt)
python scripts/master_orchestrator.py analyze-batch

# Custom input file
python scripts/master_orchestrator.py analyze-batch --input custom_priority.txt
```

**Options:**
- `--input FILE` - Specify input file (default: `matches_priority.txt`)

**Requirements:**
- Input file must exist (created by `pre-filter`)
- `match_data_v29.json` must exist (created by `pre-filter`)

**Output:**
- `consolidated_data/MATCH_ID_consolidated.json` - Data with Q1-Q19
- `analysis_history/MATCH_ID_analysis.json` - Full v5.3 analysis
- Airtable "Match Analyses" table - Updated

---

### **3. loss-analysis**

```bash
# Auto mode (queries Airtable for unanalyzed losses)
python scripts/master_orchestrator.py loss-analysis --auto

# Manual mode (analyze specific match)
python scripts/master_orchestrator.py loss-analysis --match-id Mainz05vsHoffenheim_21112025
```

**Options:**
- `--auto` - Query Airtable for losses without analysis
- `--match-id MATCH_ID` - Analyze specific match manually

**Requirements:**
- Original analysis must exist in `analysis_history/`
- For `--auto`: Airtable must be configured

**Output:**
- `loss_ledger/MATCH_ID_loss_TIMESTAMP.json` - Forensic analysis
- Airtable "Results" table - Updated with error classification

---

## 🔧 **CONFIGURATION**

### **Environment Variables (.env)**

```env
ANTHROPIC_API_KEY=sk-ant-...
AIRTABLE_API_KEY=pat...
AIRTABLE_BASE_ID=app...
```

### **Settings (in master_orchestrator.py)**

```python
# Data quality threshold (0-100)
DATA_QUALITY_THRESHOLD = 70  # Only analyze games with ≥70 quality

# Claude model
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Max tokens per API call
MAX_TOKENS = 8000
```

---

## 📁 **FILE STRUCTURE**

```
yudor-betting-system/
├── matches_all.txt              # YOU create (30-40 games)
├── matches_priority.txt         # AUTO-GENERATED by pre-filter
├── match_data_v29.json          # AUTO-GENERATED by pre-filter
│
├── consolidated_data/           # AUTO-GENERATED by analyze-batch
│   └── MATCH_ID_consolidated.json
│
├── analysis_history/            # AUTO-GENERATED by analyze-batch
│   └── MATCH_ID_analysis.json
│
├── pre_filter_history/          # AUTO-GENERATED by pre-filter
│   └── pre_filter_TIMESTAMP.json
│
├── loss_ledger/                 # AUTO-GENERATED by loss-analysis
│   └── MATCH_ID_loss_TIMESTAMP.json
│
└── scripts/
    └── master_orchestrator.py   # Main script
```

---

## ⚠️ **TROUBLESHOOTING**

### **Problem: "Prompt not found"**

**Solution:** Ensure all prompts exist:
```bash
ls prompts/DATA_CONSOLIDATION_PROMPT_v1.0.md
ls prompts/YUDOR_MASTER_PROMPT_v5.3.md
ls prompts/LOSS_LEDGER_ANALYSIS_PROMPT_v1.0.md
```

### **Problem: "Airtable 403 Forbidden"**

**Solution:** Check table names in Airtable:
- Table 1: "Match Analyses" (with space, not underscore)
- Table 2: "Bets_Entered" (with underscore)
- Table 3: "Results"

### **Problem: "Match not found in scraped data"**

**Solution:** Check match format in `matches_priority.txt`:
```
# Correct:
Mainz 05 vs Hoffenheim, Bundesliga, 21/11/2025, 20:30

# Wrong:
Mainz vs Hoffenheim  # Missing league and date
```

### **Problem: Claude API timeout**

**Solution:** Increase `MAX_TOKENS` or analyze fewer games:
```python
# In master_orchestrator.py
MAX_TOKENS = 16000  # Increase if needed
```

---

## 💡 **TIPS FOR BEST RESULTS**

### **1. Pre-Filter Strategy**

- Start with 30-40 games to get good coverage
- Only analyze games with quality ≥70/100
- Check `pre_filter_history/` to see which sources are missing

### **2. Batch Analysis**

- Run `analyze-batch` on Friday morning when odds are stable
- Review results in Airtable before calculating edge
- Check CS_final and R-Score for confidence

### **3. Edge Calculation**

- Minimum 8% edge to bet
- Re-check lines on Saturday before entering
- Don't chase reduced edges

### **4. Loss Analysis**

- Run `loss-analysis --auto` every Monday
- Look for Q-ID patterns after 10+ losses
- Wait for 30 losses before changing weights

---

## 🎉 **YOU'RE READY FOR THIS WEEKEND!**

**Complete workflow:**

```bash
# Thursday (5 min)
python scripts/master_orchestrator.py pre-filter

# Friday (10-15 min)
python scripts/master_orchestrator.py analyze-batch

# Friday afternoon (30 min)
# Check Betfair, calculate edge, enter bets manually

# Monday (5 min)
python scripts/master_orchestrator.py loss-analysis --auto
```

**Total automated time: ~20 minutes**
**Total time including manual edge calc: ~50 minutes**
**vs Manual process: 6-8 hours**

**Time saved: 5+ hours per weekend! 🚀**

---

*Automation Guide - Full v5.3 implementation*
*All commands tested and ready to use*
*No more manual Claude web copy-pasting!*
