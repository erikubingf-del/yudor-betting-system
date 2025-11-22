# Yudor v5.3 Betting System - Command Cheatcode

**Last Updated**: November 21, 2025
**System Version**: Yudor v5.3 with FLIP Synthetic Edge Logic

---

## 🚀 **EASIEST WAY: Unified CLI**

**Just run this and use the interactive menu:**

```bash
python3 yudor.py
```

**Features:**
- ✅ Interactive menu for all operations
- ✅ Daily workflow (Scrape → Analyze → Sync → Archive)
- ✅ ML System (Post-Match Analysis, Calibration)
- ✅ Utilities (View Results, Count Decisions, etc.)
- ✅ No need to remember commands!

---

## 📁 Folder Structure

```
yudor-betting-system/
├── archived_analyses/          # Historical analyses organized by date
│   └── YYYY-MM-DD/            # Each analysis run gets its own date folder
│       └── *_analysis.json     # Analysis results (only)
├── consolidated_data/          # Temp data (deleted on archive)
├── analysis_history/           # Current run analyses (temp)
├── scripts/                    # All Python scripts
├── prompts/                    # System prompts
│   └── YUDOR_MASTER_PROMPT_v5.3.md
├── matches_all.txt            # Master list of all matches (KEEP)
└── match_data_vXX.json        # Scraped data (versioned)
```

**Important**:
- `analysis_history/` → archived to `archived_analyses/YYYY-MM-DD/` (by file creation date)
- `consolidated_data/` → **deleted** (can be regenerated from scraped data)
- Only keep `matches_all.txt` and `requirements.txt`
- **Archive date**: Files are organized by when they were created, not when archived

---

## 🔄 Complete Workflow (Start to Finish)

### Step 1: Scrape Match URLs and Data
```bash
# Scrape all matches from matches_all.txt
python3 scripts/scraper.py --input matches_all.txt --output match_data_v$(date +%Y%m%d).json
```

**Duration**: ~5-10 minutes for 50 matches

**What it scrapes**:
- 8 URL sources per match (SportsMole, Transfermarkt, Local News, etc.)
- FootyStats API data (xG, form, league positions)

---

### Step 2: Run Yudor v5.3 Analysis
```bash
# Analyze all matches with complete Yudor v5.3 system
python3 scripts/master_orchestrator.py analyze-batch --input matches_all.txt
```

**Duration**: ~1-2 minutes per match

**What it analyzes**:
- Layer 1: Pricing (Q1-Q19)
- Layer 2: Confidence (CS_final, Tier)
- Layer 3: Risk Guard (R-scores, RBR)
- FLIP Logic with Synthetic Edge

---

### Step 3: Sync to Airtable
```bash
# Sync ALL CORE, EXP, and FLIP matches (skips VETO)
python3 scripts/sync_all_betting_opportunities.py
```

**What it syncs**:
- ✅ CORE bets (R < 0.15, CS ≥ 70)
- ✅ EXP bets (0.15 ≤ R < 0.25)
- ✅ FLIP bets (R ≥ 0.25, RBR > 0.25, Edge ≥ 8%, CS ≥ 65)
- ❌ VETO (skipped)

---

### Step 4: Organize and Archive
```bash
# Move files to date-organized archive
python3 scripts/organize_analyses.py
```

**Result**: All files moved to `archived_analyses/YYYY-MM-DD/`

---

## 🎯 Quick Reference

### Daily Workflow (All 4 Steps)
```bash
# 1. Scrape
python3 scripts/scraper.py --input matches_all.txt --output match_data_v$(date +%Y%m%d).json

# 2. Analyze
python3 scripts/master_orchestrator.py analyze-batch --input matches_all.txt

# 3. Sync
python3 scripts/sync_all_betting_opportunities.py

# 4. Archive
python3 scripts/organize_analyses.py
```

---

## 🤖 Machine Learning & Post-Match Workflow

### Daily (After Betting)
```bash
# When you have a loss - Log it manually
# (You'll upload match results to Airtable with: Match Result, Bet Result, Units Won/Lost)

# After matches finish - Update statistics
python3 scripts/post_match_analysis.py
```

### After 30 Losses (ML Calibration)
```bash
# Run machine learning analysis for system improvements
python3 scripts/ml_calibration.py
```

**What the ML System Does**:
- **Post-Match Analysis**: Calculates win rates, ROI, edge accuracy by decision type
- **ML Calibration**: Proposes statistically significant changes (Q-scores, thresholds, etc.)
- **Automated**: Analyzes patterns and suggests improvements based on YOUR results

**Required Airtable Fields** (add to "Match Analyses" table):
- Match Result (Text): "2-1"
- Bet Result (Single Select): WIN, LOSS, HALF_LOSS, PUSH
- Units Won/Lost (Number): +1.0 or -1.0
- Market AH (Number): -0.75

**Documentation**: See [ML_QUICK_START.md](ML_QUICK_START.md) for complete guide

### Check Results
```bash
# Count decisions
grep -r "\"decision\":" analysis_history/*.json | grep -o "CORE\|EXP\|FLIP\|VETO" | sort | uniq -c

# View specific match
cat analysis_history/BarcelonavsAthleticClub_22112025_analysis.json | jq '.yudor_analysis'
```

### Monitor Background Jobs
```bash
jobs                    # List running jobs
tail -f analysis.log    # Watch live progress
tail -50 analysis.log   # Last 50 lines
```

---

## 🔧 Maintenance

### Clean Up Temp Files
```bash
# Remove temporary match lists (keep matches_all.txt)
rm -f matches_priority.txt matches_test*.txt matches_remaining_*.txt
```

### Recalculate AH Lines
```bash
# Recalculate with updated formula
python3 scripts/recalculate_ah_lines.py --sync-airtable
```

---

## 📊 Decision Types

### CORE (Full Stake)
- R < 0.15 (low risk)
- CS ≥ 70 (high confidence)
- Tier 1

### EXP (Reduced Stake)
- 0.15 ≤ R < 0.25
- Edge ≥ 8%
- Tier 2

### FLIP (Bet Underdog)
**All 4 must be true**:
1. R ≥ 0.25 (favorite risky)
2. RBR > 0.25 (significant risk imbalance)
3. Edge_Synthetic ≥ 8%: `(|AH_Line| / 0.25) × 8%`
4. CS_flip ≥ 65 (underdog quality)

### VETO (Don't Bet)
- R ≥ 0.25 AND FLIP not met
- CS < 70
- High risk signals

---

## 🎲 FLIP Synthetic Edge

```
Edge_Synthetic (%) = (|AH_Line| / 0.25) × 8%
```

**Examples**:
| Fair AH | Underdog Gets | Edge % | Meets ≥8%? |
|---------|--------------|--------|------------|
| -2.0 | +2.0 | 64% | ✅ |
| -1.0 | +1.0 | 32% | ✅ |
| -0.25 | +0.25 | 8% | ✅ |
| 0.0 | 0.0 | 0% | ❌ |

---

## 🆕 What's New in v5.3

1. ✅ FLIP Synthetic Edge (no Betfair dependency)
2. ✅ RBR Calculation (R_home, R_away, R_fav, R_dog)
3. ✅ Local News Integration
4. ✅ Corrected AH (0.25 intervals)
5. ✅ Date-Organized Archives
6. ✅ **Machine Learning System** (post-match analysis & calibration)

---

## 📝 File Naming

**Match ID**: `{Home}vs{Away}_{DDMMYYYY}`
- Example: `BarcelonavsAthleticClub_22112025`

**Files**:
- `{MatchID}_consolidated.json` - Raw data
- `{MatchID}_analysis.json` - Full analysis

---

## 🚨 Troubleshooting

### No FLIP Decisions?
FLIP is rare. Requires risky favorite + safe underdog + edge + quality.

### Airtable Sync Fails?
Check `.env` API keys and Airtable schema.

### Missing SportsMole?
Some matches don't have preview pages (expected).

---

## 🎯 Pro Tips

1. **Always archive after analysis**:
   ```bash
   python3 scripts/organize_analyses.py
   ```

2. **Version scraped data**:
   ```bash
   match_data_v$(date +%Y%m%d).json
   ```

3. **Keep only matches_all.txt**, delete temp files

4. **Check data quality**:
   ```bash
   jq '.consolidated_data.data_quality.score' analysis_history/*.json | awk '{sum+=$1; n++} END {print sum/n}'
   ```
   Target: ≥75

---

**Remember**: Only CORE, EXP, and FLIP go to Airtable. VETO = DON'T BET.
