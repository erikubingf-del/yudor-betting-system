# 🚀 YUDOR v5.3 - QUICK START GUIDE

## START USING THIS WEEKEND (Manual + Semi-Automated)

Since full automation is still in development, here's how to use the v5.3 system **RIGHT NOW** with your existing setup.

---

## ✅ **WHAT'S READY TO USE**

1. ✅ **Scraper** - Extracts URLs (you have `match_data_v29.json` example)
2. ✅ **All v5.3 Prompts** - Complete analysis framework
3. ✅ **ANEXO References** - Deterministic scoring rules
4. ✅ **Airtable** - Connected and working
5. ✅ **Data Quality Scoring** - Added to DATA_CONSOLIDATION_PROMPT

---

## 📅 **WORKFLOW FOR THIS WEEKEND**

### **THURSDAY EVENING: Pre-Filter (Manual)**

#### **Step 1: Create Match List**
Create `matches_all.txt`:
```
Mainz 05 vs Hoffenheim, Bundesliga, 21/11/2025, 20:30
Valencia vs Levante, La Liga, 21/11/2025, 21:00
Flamengo vs Bragantino, Brasileirão, 22/11/2025, 19:00
... (30-40 games)
```

#### **Step 2: Run Scraper**
```bash
python scripts/scraper.py
```

This creates `match_data_v29.json` with all URLs (like your example).

#### **Step 3: Quick Data Quality Check (Manual)**

For each game in `match_data_v29.json`, check:
- ✅ Do we have SportsMole URL? (tactical preview)
- ✅ Do we have Transfermarkt URLs? (squad values)
- ✅ Do we have SofaScore/WhoScored? (xG data)
- ✅ Do we have News URLs? (local media)

**Create `matches_priority.txt` with top 15-20 games that have most URLs.**

Example:
```
# PRIORITY GAMES (Good data quality)
Mainz 05 vs Hoffenheim, Bundesliga, 21/11/2025, 20:30  # Has all sources
Valencia vs Levante, La Liga, 21/11/2025, 21:00  # Has all sources
... (15-20 games with complete data)
```

**Time:** ~30 minutes

---

### **FRIDAY MORNING: Deep Analysis (Semi-Automated with Claude Web)**

For each game in `matches_priority.txt`:

#### **Step 1: Data Consolidation**

**Open Claude.ai web interface** and use this prompt template:

```
I need you to act as the Data Consolidation AI for the Yudor betting system.

Your task: Extract and consolidate data from these URLs for match analysis.

MATCH: Mainz 05 vs Hoffenheim (Bundesliga, 21/11/2025)

URLS:
- SportsMole: https://www.sportsmole.co.uk/football/mainz-05/preview/mainz-vs-hoffenheim-prediction-team-news-lineups_585985.html
- SofaScore: https://www.sofascore.com/football/match/tsg-hoffenheim-1-fsv-mainz-05/gbbsubb
- WhoScored: https://www.whoscored.com/matches/1910756/teamstatistics/germany-bundesliga-2025-2026-mainz-05-hoffenheim
- Transfermarkt Home: https://www.transfermarkt.com.br/1-fsv-mainz-05/startseite/verein/39
- Transfermarkt Away: https://www.transfermarkt.com.br/tsg-1899-hoffenheim/startseite/verein/533
- Local News: [URLs from match_data_v29.json]

INSTRUCTIONS:
Follow the DATA_CONSOLIDATION_PROMPT_v1.0 to:
1. Extract all data from these URLs
2. Fill Q1-Q19 scores deterministically using ANEXO I criteria
3. Calculate data quality score (0-100)
4. Output structured JSON

[Then paste the full DATA_CONSOLIDATION_PROMPT_v1.0.md content]
```

**Claude will:**
- Visit all URLs (using web fetch)
- Extract data
- Fill Q1-Q19
- Calculate data quality
- Output consolidated JSON

**Save output as:** `consolidated_data/MAIvsHOF_21112025_consolidated.json`

**Time:** ~5-10 minutes per game

---

#### **Step 2: Yudor Analysis (Using v5.3 Prompt)**

**Continue in Claude web interface:**

```
Now run the Yudor v5.3 analysis on this consolidated data.

CONSOLIDATED DATA:
[Paste the JSON from Step 1]

INSTRUCTIONS:
Follow YUDOR_MASTER_PROMPT_v5.3 to:
1. LAYER 1: Calculate fair AH line (blind pricing)
2. LAYER 2: Calculate CS_final confidence
3. LAYER 3: Calculate R-Score risk
4. Apply decision logic (CORE/EXP/VETO/FLIP/IGNORAR)
5. Output complete analysis

[Then paste YUDOR_MASTER_PROMPT_v5.3.md content]

CRITICAL: Use BLIND PRICING - do NOT reference market odds.
```

**Claude will:**
- Run 3-layer analysis
- Calculate fair line
- Output decision + confidence + risk

**Save output as:** `analysis_history/MAIvsHOF_21112025_analysis.json`

**Time:** ~5-10 minutes per game

---

#### **Step 3: Save to Airtable (Manual)**

Open Airtable → "Match Analyses" table → Create new record:

**Copy from Claude's output:**
- match_id: MAIvsHOF_21112025
- home_team: Mainz 05
- away_team: Hoffenheim
- league: Bundesliga
- date: 21/11/2025
- yudor_ah_fair: -0.75 (Claude's fair line)
- yudor_decision: CORE
- cs_final: 82
- r_score: 0.14
- tier: 1
- data_quality: 88
- status: ANALYZED

**Time:** ~2 minutes per game

---

### **FRIDAY AFTERNOON: Edge Calculation (Manual)**

For each analyzed game:

#### **Step 1: Check Betfair**

Go to Betfair Exchange → Find match → Check Asian Handicap market

**Example:**
- Betfair offers: Mainz -0.50 @ 2.10

#### **Step 2: Calculate Edge**

```
Model Fair Line: -0.75
Market Line: -0.50
Difference: +0.25 lines in your favor

Rough edge = 0.25 × 10% = ~2.5% per quarter line
OR
Model Odds: 2.01
Market Odds: 2.10
Odds edge = (2.10 / 2.01 - 1) × 100 = +4.5%

Combined estimate: ~6-7% edge
```

#### **Step 3: Decision**

Update Airtable "Match Analyses":
- Edge%: 6.5
- AH_Line_Market: -0.50
- Odd_Market: 2.10

**If edge ≥ 8%:**
- Entry_Status: "Yes - Value Found"
- Create record in "Bets_Entered" table

**If edge < 8%:**
- Entry_Status: "No - Insufficient Edge"

**Time:** ~5 minutes per game

---

### **SATURDAY: Monitor & Enter Bets**

2-3 hours before kickoff, re-check lines and enter bets for games with edge ≥8%.

---

### **SUNDAY: Update Results**

After matches finish, update Airtable "Results" table:
- match_id: (link to Match Analyses)
- final_score: "2-1"
- ah_result: WIN/LOSS/PUSH
- profit_loss: +95 or -100

---

### **MONDAY: Loss Analysis (Manual with Claude)**

For any losses, use Claude web interface:

```
I need post-match loss analysis using the LOSS_LEDGER_ANALYSIS_PROMPT.

ORIGINAL ANALYSIS:
[Paste analysis_history/MAIvsHOF_21112025_analysis.json]

ACTUAL RESULT:
Match: Mainz 05 vs Hoffenheim
Final Score: 1-2
Our Bet: Mainz -0.50 (LOSS)

INSTRUCTIONS:
[Paste LOSS_LEDGER_ANALYSIS_PROMPT_v1.0.md]

Identify:
1. Which Q-IDs failed?
2. Error type (Model/Data/Variance)?
3. Recommendations
```

**Save output as:** `loss_ledger/MAIvsHOF_21112025_loss.json`

**Update Airtable Results:**
- error_category: "Model Error: Q6 Tactics"
- notes: [Summary from Claude]

---

## 📊 **SUMMARY: TIME PER WEEKEND**

| Phase | Time | Automation Level |
|:---|---:|:---|
| Thursday: Scraper + Pre-filter | 30 min | Semi-auto (scraper auto, filter manual) |
| Friday: Analysis (15-20 games) | 3-4 hours | Manual with Claude web |
| Friday: Edge calc (15-20 games) | 1-2 hours | Manual |
| Saturday: Monitor + Enter | 30 min | Manual |
| Sunday: Update results | 15 min | Manual |
| Monday: Loss analysis | 30 min | Manual with Claude |
| **TOTAL** | **6-8 hours** | **~40% automated** |

---

## 🎯 **NEXT STEPS FOR FULL AUTOMATION**

After this weekend, I'll implement:

**Week 1:**
- `pre-filter` command (auto data quality scoring)
- `analyze-batch` command (auto v5.3 analysis)
- → Saves you ~4 hours per weekend

**Week 2:**
- `loss-analysis` command (auto loss forensics)
- Improved Airtable integration
- → Saves you ~1 hour per weekend

**Week 3-4:**
- ML audit system (after 30 matches)
- Complete automation
- → System fully autonomous

---

## 💡 **TIPS FOR THIS WEEKEND**

### **Tip 1: Start Small**
Don't analyze all 30-40 games manually. Start with 5-10 priority games to test the workflow.

### **Tip 2: Use Templates**
Create prompt templates in a text file so you can copy-paste quickly for each game.

### **Tip 3: Track Time**
Note how long each step takes so we can optimize automation priorities.

### **Tip 4: Document Issues**
If any prompt doesn't work well or data is missing, note it down for improvements.

### **Tip 5: Focus on Quality**
Better to deeply analyze 10 games than rush through 30.

---

## 📁 **FILE ORGANIZATION**

```
yudor-betting-system/
│
├── matches_all.txt (YOU create)
├── matches_priority.txt (YOU create after checking data quality)
├── match_data_v29.json (scraper output)
│
├── consolidated_data/
│   ├── MAIvsHOF_21112025_consolidated.json
│   ├── VALvsLEV_21112025_consolidated.json
│   └── ... (save Claude's data consolidation outputs)
│
├── analysis_history/
│   ├── MAIvsHOF_21112025_analysis.json
│   ├── VALvsLEV_21112025_analysis.json
│   └── ... (save Claude's Yudor analysis outputs)
│
├── loss_ledger/
│   └── (save loss analyses here)
│
└── prompts/ (reference these in Claude web)
    ├── DATA_CONSOLIDATION_PROMPT_v1.0.md
    ├── YUDOR_MASTER_PROMPT_v5.3.md
    ├── LOSS_LEDGER_ANALYSIS_PROMPT_v1.0.md
    └── anexos/
        ├── ANEXO_I_SCORING_CRITERIA.md
        ├── ANEXO_II_RG_GUARD.md
        └── ANEXO_III_TACTICAL_EXAMPLES.md
```

---

## ✅ **PRE-FLIGHT CHECKLIST**

Before starting this weekend:

- [ ] Scraper works and generates match_data_v29.json ✅ (you have example)
- [ ] Airtable tables exist (Match Analyses, Bets_Entered, Results) ✅
- [ ] You can access Claude.ai web interface ✅
- [ ] You have Betfair account for checking odds ✅
- [ ] You've read DATA_CONSOLIDATION_PROMPT_v1.0.md
- [ ] You've read YUDOR_MASTER_PROMPT_v5.3.md
- [ ] You've read ANEXO I, II, III
- [ ] Directories created (consolidated_data/, analysis_history/, loss_ledger/)

---

## ❓ **QUESTIONS TO RESOLVE**

### **Q1: Does your scraper accept a file input?**
Current code shows it might read `matches.txt`. Confirm:
```bash
python scripts/scraper.py --input matches_all.txt --output match_data_v29.json
```

If not, we may need to update scraper to accept parameters.

### **Q2: Betfair API or Manual Check?**
Do you have Betfair API access, or will you manually check odds?
- Manual: Copy-paste from website
- API: We can automate this later

### **Q3: How many games can you realistically analyze manually?**
This weekend, aim for 5-10 games to test the system, or push for 15-20?

---

## 🎉 **YOU'RE READY!**

With this guide, you can:
✅ Start using v5.3 THIS WEEKEND
✅ Test the complete methodology
✅ Begin building historical data
✅ Identify any improvements needed

Next session, I'll automate the repetitive parts based on your feedback!

---

*Quick Start Guide - Manual/Semi-Automated Workflow*
*Full automation coming in next implementation phase*
*Start analyzing matches and finding value!*
