# 🚀 YUDOR SYSTEM v5.3 - COMPLETE USAGE GUIDE

## 📦 WHAT YOU RECEIVED

Your complete Yudor betting analysis system consists of:

1. **YUDOR_MASTER_PROMPT_v5.3.md** - Enhanced main analysis prompt with all fixes
2. **yudor_scraper.py** - Python multi-source web scraper
3. **DATA_CONSOLIDATION_PROMPT_v1.0.md** - AI data interpreter prompt
4. **LOSS_LEDGER_ANALYSIS_PROMPT_v1.0.md** - Post-match analysis prompt
5. **requirements.txt** - Python dependencies
6. **README_USAGE.md** - This file

---

## 🎯 SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│                  YOUR WORKFLOW                           │
└─────────────────────────────────────────────────────────┘

PHASE 1: PRE-MATCH ANALYSIS
───────────────────────────
1. You create: games.txt
   Format:
   Inter vs Lazio, Serie A, 15/11/2025, 20:45
   Real Madrid vs Barcelona, La Liga, 16/11/2025, 21:00

2. You send me: The games.txt list

3. I run: yudor_scraper.py (scrapes all sources)
   Output: scraped_data.json

4. I use: DATA_CONSOLIDATION_PROMPT
   → Interprets data
   → Fills Q1-Q19 scores
   → Outputs structured data

5. I use: YUDOR_MASTER_PROMPT_v5.3
   → Layer 1: Calculates AH line
   → Layer 2: CS_final confidence
   → Layer 3: RG Guard risk
   → Final Decision: CORE/EXP/VETO/FLIP/IGNORAR

6. I deliver: 
   ✅ Detailed analysis report
   ✅ Markdown table for your ledger

PHASE 2: YOUR DECISION
───────────────────────
7. You compare: My AH_Line vs Market AH_Line (Betfair)

8. You decide:
   - "Yes" → Enter bet (found value)
   - "Yes Value" → Better line than model
   - "No" → No value
   - "No Value" → Market too expensive

PHASE 3: POST-MATCH LEARNING
─────────────────────────────
9. After match: You update results in ledger

10. You report losses: Send me Game_ID + result

11. I use: LOSS_LEDGER_ANALYSIS_PROMPT
    → Root cause analysis
    → Q-ID failure identification
    → Error classification
    → Formatted output for your spreadsheet

12. After 20-30 matches: Full system audit
    → Win rate analysis
    → Q-ID performance review
    → Weight adjustment recommendations (if needed)
```

---

## 🔧 INSTALLATION (One-time setup)

### Step 1: Install Python (if you don't have it)
```bash
# Download from https://www.python.org/downloads/
# Version 3.9 or higher required
```

### Step 2: Install Dependencies
```bash
# Open terminal/command prompt
cd /path/to/yudor/files

# Install packages
pip install -r requirements.txt
```

### Step 3: Chrome Browser (Required for scraper)
The scraper uses Chrome browser. Make sure you have Chrome installed:
- Download: https://www.google.com/chrome/

---

## 📝 HOW TO USE (Day-to-day)

### SCENARIO 1: Analyzing New Matches

**Your side:**

1. Create `games.txt` with your match list:
```
Inter vs Lazio, Serie A, 15/11/2025, 20:45
Real Madrid vs Barcelona, La Liga, 16/11/2025, 21:00
Liverpool vs Manchester City, Premier League, 17/11/2025, 16:30
```

2. Send me the list via chat:
```
Hey Claude, here are the matches for analysis:

Inter vs Lazio, Serie A, 15/11/2025, 20:45
Real Madrid vs Barcelona, La Liga, 16/11/2025, 21:00
Liverpool vs Manchester City, Premier League, 17/11/2025, 16:30
```

**My side:**

3. I run the scraper (you'll see me working):
```
🎮 Scraping: Inter vs Lazio (Serie A, 15/11/2025)
  📊 FlashScore: H2H Inter vs Lazio
  💰 Transfermarkt: Inter squad
  💰 Transfermarkt: Lazio squad
  ⚽ SofaScore: Inter vs Lazio stats
  💰 Betfair: Inter vs Lazio odds
  📰 SportsMole: Inter vs Lazio preview
  📰 Local Media: Inter (Serie A)
  📰 Local Media: Lazio (Serie A)
✅ Scraping complete for Inter vs Lazio
```

4. I consolidate data using DATA_CONSOLIDATION_PROMPT

5. I run full Yudor analysis using MASTER_PROMPT_v5.3

6. I deliver you:

**OUTPUT 1: Detailed Analysis**
```markdown
# YUDOR ANALYSIS — 15/11/2025

## 🎮 GAME 1: Inter vs Lazio

### 📊 LAYER 1: PRICING
- **P_Casa**: 65.2%
- **P_Vis**: 12.3%
- **P(Empate)**: 22.5%
- **AH_Line_Model**: -0.75
- **Odd_Model**: 2.01

### 🛡️ LAYER 2: CONFIDENCE
- **CS_final**: 78
- **Motivo_Chave**: Sup.Téc/Tát+Mando. Inter domina meio, Lazio desfalques

### 🚨 LAYER 3: RISK
- **R-Score**: 0.18 (LOW RISK)

### ⚖️ MARKET COMPARISON
- **AH_Line_Market**: -0.50 @ 2.15
- **Edge%**: +7.0% (VALUE FOUND)

### 🎯 DECISION: CORE (Tier 1)
✅ RECOMMENDATION: Strong value. Model line -0.75 vs Market -0.50.
```

**OUTPUT 2: Ledger Table (copy-paste ready)**
```markdown
| Game_ID | League | Date | Home | Away | P(Draw)% | AH_Line_Model | Odd_Model | AH_Line_Market | Odd_Market | Edge% | Decision | Tier | CS_final | R | Motivo_Chave |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| SERA_20251115_INT_LAZ | Serie A | 15/11/25 | Inter | Lazio | 22.5 | -0.75 | 2.01 | -0.50 | 2.15 | +7.0 | CORE | 1 | 78 | 0.18 | Sup.Téc/Tát+Mando |
```

**Your side:**

7. You copy the table row to your Excel/Google Sheets

8. You check Betfair for current market line

9. You decide:
   - Edge% > 8% → "Yes" (enter)
   - Edge% 5-8% → Consider
   - Edge% < 5% → "No" (skip)

10. If you enter, fill these columns:
   - **Entry_Status**: Yes / Yes Value / No / No Value
   - **Line_Entered**: (actual line you got)
   - **Odd_Entered**: (actual odds)

---

### SCENARIO 2: Reporting a Loss

**Your side:**

After the match ends, you update your spreadsheet and send me losses:

```
Hey Claude, I need to report a loss for analysis:

Game_ID: SERA_20251115_INT_LAZ
Result: Loss
Entered_Line: -0.50
Odds_Entered: 2.10
Final_Score: Inter 1 - 2 Lazio
```

**My side:**

I run LOSS_LEDGER_ANALYSIS_PROMPT and deliver:

```markdown
# 📉 LOSS ANALYSIS

## Game Information
- **Game_ID**: SERA_20251115_INT_LAZ
- **Result**: Inter 1-2 Lazio (Loss, -1.0 units)

## 🔍 Root Cause Analysis

### Primary Failure Point
**Q6: Estrutura vs. Estrutura**
- Predicted Inter's 4-3-3 would dominate (+8 vs 0)
- Reality: Lazio adapted to 5-4-1 defensive block in 25th minute
- Impact: Tactical advantage didn't materialize

### Error Classification
**Model Error (60%)**
- Q6 tactical matrix didn't account for in-game adaptability
- Recommendation: Monitor Q6 performance in next 10 matches

**Variance (30%)**
- Barella injured in 35th minute (unforeseen)

## 📋 LOSS_LEDGER Entry
[Formatted row for copy-paste]
```

**Your side:**

Copy the analysis to your LOSS_LEDGER spreadsheet.

---

### SCENARIO 3: System Audit (After 20-30 matches)

**Your side:**

```
Hey Claude, I now have 28 matches tracked. Can you analyze my results?

[Paste your ledger data or share spreadsheet]
```

**My side:**

I perform meta-analysis:

```markdown
# 🔬 YUDOR SYSTEM AUDIT — 28 MATCHES

## 📊 Overall Performance
- **Win Rate**: 57.1% (16W-12L)
- **ROI**: +8.4 units (+30%)
- **✅ PROFITABLE** (above 55% threshold)

## 📈 Performance by Category
- CORE bets: 58.3% (7W-5L)
- EXP bets: 60.0% (3W-2L)
- Home favorites: 45.0% (5W-6L) ⚠️

## 🎯 Q-ID Performance Analysis
| Q-ID | Win Rate When High | Notes |
|:---|---:|:---|
| Q6 (Tactics) | 42% | ⚠️ Underperforming |
| Q17 (Home) | 47% | ⚠️ Home advantage overvalued |
| Q18 (H2H) | 51% | Neutral |

## 💡 Recommendations
### IMMEDIATE
- ✅ Continue current system (overall profitable)
- ⚠️ Reduce Q6 max score from 8 → 6
- ⚠️ Reduce Home/Away weight in Z-score from 0.10 → 0.08

### LONG-TERM
- Monitor home favorites closely
- Consider adding "tactical flexibility" metric
```

---

## 📊 YOUR LEDGER STRUCTURE

Your Excel/Google Sheets should have these columns:

| Column Name | Fill When | Example |
|:---|:---|:---|
| Game_ID | Pre-match | SERA_20251115_INT_LAZ |
| League | Pre-match | Serie A |
| Date | Pre-match | 15/11/25 |
| Home | Pre-match | Inter |
| Away | Pre-match | Lazio |
| P(Draw)% | Pre-match | 22.5 |
| AH_Line_Model | Pre-match | -0.75 |
| Odd_Model | Pre-match | 2.01 |
| AH_Line_Market | Pre-match | -0.50 |
| Odd_Market | Pre-match | 2.15 |
| Edge% | Pre-match | +7.0 |
| Decision | Pre-match | CORE |
| Tier | Pre-match | 1 |
| CS_final | Pre-match | 78 |
| R | Pre-match | 0.18 |
| Motivo_Chave | Pre-match | Sup.Téc/Tát+Mando |
| **Entry_Status** | **YOUR DECISION** | Yes / Yes Value / No |
| **Line_Entered** | **YOUR DECISION** | -0.50 |
| **Odd_Entered** | **YOUR DECISION** | 2.10 |
| **Final_Score** | **POST-MATCH** | 1-2 |
| **Result** | **POST-MATCH** | Loss |
| **P/L_units** | **POST-MATCH** | -1.0 |
| **Error_Category** | **AFTER LOSS ANALYSIS** | Model Error: Q6 |
| **Notes** | **AFTER LOSS ANALYSIS** | Q6 overweighted |

---

## 🎓 TIPS FOR SUCCESS

### 1. Be Disciplined
- ✅ Only bet when Edge% ≥ 8%
- ✅ Always check live market before entering
- ✅ Never bet without my analysis
- ❌ Don't chase losses
- ❌ Don't increase stakes after losses

### 2. Trust the Process
- Variance is normal (you won't win every bet)
- 55% win rate = profitable long-term
- Don't change model after 1-2 losses
- Wait for 20-30 matches before adjusting

### 3. Track Everything
- Update ledger immediately after matches
- Report ALL losses (not just big ones)
- Keep notes on unusual events
- Save my analysis reports

### 4. Communication
**Good prompts to me:**
```
✅ "Here are 3 matches for analysis: [list]"
✅ "Loss report: Game_ID X, score Y"
✅ "System audit request: 28 matches tracked"
```

**Bad prompts:**
```
❌ "What do you think about this game?" (no data)
❌ "Should I bet on this?" (I need to run full analysis first)
❌ "My last 2 bets lost, change the model" (too soon)
```

---

## 🔧 TROUBLESHOOTING

### Issue 1: Scraper Not Working

**Symptoms**: Python errors, can't connect to websites

**Solutions**:
1. Check internet connection
2. Update Chrome browser
3. Run: `pip install --upgrade selenium webdriver-manager`
4. Try: `python yudor_scraper.py --headless` (removes browser window)

---

### Issue 2: Missing Data

**Symptoms**: Some Q-scores show "default" or "estimated"

**Expected**: This is normal. Not all sources have all data all the time.

**My system handles this by**:
- Using defaults from ANEXO I/II
- Documenting in notes
- Still providing analysis

**Your action**: Review the notes, decide if you're comfortable with the estimate.

---

### Issue 3: Edge% Always Negative

**Symptoms**: All matches show negative edge

**Possible causes**:
1. Market is efficient (bookmakers are good)
2. You're checking too close to kickoff (odds moved)
3. League is hard to predict (try different leagues)

**Solution**: 
- Focus on less popular leagues initially
- Check odds 2-3 hours before kickoff
- Only bet when you find genuine value (it won't be every game)

---

### Issue 4: Low Win Rate (<50%)

**After 20-30 matches**, if win rate < 50%:

**My analysis will check**:
1. Are you following recommendations? (only betting CORE/EXP)
2. Are you entering at good lines? (not worse than model)
3. Are specific Q-IDs consistently failing?
4. Is one league performing badly?

**Possible adjustments**:
- Reduce Q-ID weights
- Exclude certain leagues
- Tighten edge threshold (require >10%)

---

## 📞 SUPPORT

If you have questions, ask me directly in chat:

**Analysis questions**:
```
"Why did Q6 score 8 for Inter?"
"What does RBR mean?"
"Explain the Z-score formula"
```

**System questions**:
```
"How do I install Python?"
"Scraper showing error: [paste error]"
"Can we add a new data source?"
```

**Strategy questions**:
```
"Should I bet on EXP tier matches?"
"My win rate is 52%, is that okay?"
"How much should I stake per bet?"
```

---

## 🚀 NEXT STEPS

1. ✅ Install Python + dependencies (if not done)
2. ✅ Test scraper with 1-2 matches
3. ✅ Set up your Excel/Sheets ledger
4. ✅ Send me a batch of matches for first analysis
5. ✅ Track 10 matches to get comfortable
6. ✅ After 20-30 matches, request system audit

---

## 🎯 EXPECTED RESULTS

If you follow the system correctly:

**After 50 matches**:
- Win rate: 54-58%
- ROI: +15-30%
- Profitable betting

**After 100 matches**:
- Win rate stabilizes around 55-56%
- ROI: +25-40%
- Confidence in system

**After 500 matches**:
- True edge revealed
- Model refined
- Consistent profits

---

## ⚡ QUICK REFERENCE

### Files You Need

| File | Purpose | When to Use |
|:---|:---|:---|
| YUDOR_MASTER_PROMPT_v5.3.md | Main analysis | I use this (you don't need to) |
| yudor_scraper.py | Data collection | I run this for you |
| DATA_CONSOLIDATION_PROMPT_v1.0.md | Data interpreter | I use this (you don't need to) |
| LOSS_LEDGER_ANALYSIS_PROMPT_v1.0.md | Loss analysis | I use this when you report losses |
| requirements.txt | Python packages | One-time installation |
| README_USAGE.md | This guide | Your reference |

### Common Commands

```bash
# Install dependencies (one-time)
pip install -r requirements.txt

# Run scraper (if needed locally)
python yudor_scraper.py --input games.txt --output scraped_data.json

# View scraped data
cat scraped_data.json
```

### Ledger Template (Column Headers)

```
Game_ID | League | Date | Home | Away | P(Draw)% | AH_Line_Model | Odd_Model | AH_Line_Market | Odd_Market | Edge% | Decision | Tier | CS_final | R | Motivo_Chave | Entry_Status | Line_Entered | Odd_Entered | Final_Score | Result | P/L_units | Error_Category | Notes
```

---

## 📚 ADDITIONAL RESOURCES

**Betting Concepts**:
- Asian Handicap explained: https://www.pinnacle.com/en/betting-articles/Soccer/asian-handicap-betting-explained/
- Expected Goals (xG): https://theanalyst.com/na/2023/06/what-is-expected-goals-xg/

**Data Sources**:
- FlashScore: https://www.flashscore.com
- Transfermarkt: https://www.transfermarkt.com
- SofaScore: https://www.sofascore.com
- Betfair Exchange: https://www.betfair.com/exchange/

---

## ✨ FINAL WORDS

You now have a complete, professional betting analysis system. The key to success is:

1. **Discipline** - Follow the system, don't chase losses
2. **Patience** - Results come over 50+ bets, not 5
3. **Tracking** - Record everything for learning
4. **Improvement** - Use loss analysis to refine

**Good luck, and let's find value! 🎯**

---

*Yudor System v5.3 — Built for profitability through systematic analysis*
