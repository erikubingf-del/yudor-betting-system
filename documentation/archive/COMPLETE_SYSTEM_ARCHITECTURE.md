# 🏗️ COMPLETE YUDOR SYSTEM ARCHITECTURE
## Professional Betting Analysis with Persistent Memory

---

## 🎯 WHAT YOU'LL HAVE

A **professional-grade betting system** with:

✅ **Persistent memory** - Every analysis saved forever  
✅ **Blind pricing** - Claude sets fair lines without seeing market  
✅ **Edge calculation** - You compare Claude's line vs market manually  
✅ **Bet tracking** - Airtable database tracks everything  
✅ **Learning system** - Improves from past results  
✅ **One-command operation** - Simple to use daily  

---

## 🏗️ ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────┐
│                 YOU (The User)                           │
│          "Analyze Flamengo vs Bragantino"               │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│           MASTER ORCHESTRATOR (Python)                   │
│                                                          │
│  1. Runs scraper.py → Gets URLs                         │
│  2. Calls Claude API → Extracts data from URLs          │
│  3. Calls Claude API → Yudor analysis (BLIND)           │
│  4. Shows you Claude's fair line                        │
│  5. You manually check market + calculate edge          │
│  6. Saves everything to Airtable + local files          │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  DATA LAYER                              │
│                                                          │
│  • GitHub Repo (prompts, code, history)                 │
│  • Airtable (database for all analyses + bets)          │
│  • Local Files (analysis_history/*.json)                │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 COMPLETE FILE STRUCTURE

```
yudor-betting-system/               ← GitHub Repository
│
├── 📁 prompts/                     ← AI Instructions
│   ├── extraction_prompt.md       ← How to extract from URLs
│   ├── yudor_analysis_prompt.md   ← Yudor Q1-Q19 system
│   ├── audit_prompt.md            ← Learning from losses
│   └── anexos/
│       ├── ANEXO_I.md             ← League defaults
│       ├── ANEXO_II.md            ← Tactical analysis
│       └── ANEXO_III.md           ← Examples
│
├── 📁 scripts/                     ← Automation
│   ├── master_orchestrator.py     ⭐ MAIN SCRIPT
│   ├── scraper.py                 ← URL finder
│   └── airtable_utils.py          ← Database helper
│
├── 📁 config/                      ← Settings
│   ├── config.json                ← API keys, settings
│   └── requirements.txt           ← Python dependencies
│
├── 📁 analysis_history/            ← All Past Analyses
│   ├── FLAvsBRA_25112025_<timestamp>.json
│   ├── MAIvsHOF_21112025_<timestamp>.json
│   └── ... (every analysis ever)
│
├── 📄 matches.txt                  ← Input file
├── 📄 README.md                    ← Documentation
└── 📄 .gitignore                   ← Don't commit secrets
```

---

## 🔑 CRITICAL INNOVATION: BLIND PRICING

### The Problem with Traditional Systems
Most betting systems see market odds BEFORE analyzing, which creates:
- ❌ Confirmation bias
- ❌ Anchoring to market
- ❌ Can't find true value

### Your Blind Pricing System
```
STAGE 1-2: Data Collection
├─ Scrape URLs
├─ Extract match data
└─ NO market odds collected

STAGE 3: Claude Analysis (BLIND)
├─ Claude analyzes match objectively
├─ Q1-Q19 factors
├─ Sets FAIR Asian Handicap line
├─ Example: "Flamengo -1.25 is fair"
└─ NO reference to market

STAGE 4: You Calculate Edge (MANUAL)
├─ Claude says: Flamengo -1.25 fair
├─ You check Betfair: Flamengo -0.75 available
├─ Market is 0.5 lines MORE favorable!
├─ YOU calculate: ~15% positive edge
└─ Decision: BET!

STAGE 5: Track Result
└─ Record outcome → System learns
```

### Why This Works
✅ No bias from market consensus  
✅ Pure analytical assessment  
✅ You control edge calculation  
✅ Find TRUE value bets  
✅ Better long-term results  

---

## 🗄️ AIRTABLE DATABASE DESIGN

### Table 1: Match_Analyses (Primary)

| Field | Type | Purpose |
|-------|------|---------|
| match_id | Text (Primary) | FLAvsBRA_25112025 |
| date | Date | 25/11/2025 |
| home_team | Text | Flamengo |
| away_team | Text | Bragantino |
| league | Text | Brasileirão |
| analysis_timestamp | DateTime | When analyzed |
| yudor_ah_fair | Number | Claude's fair line (-1.25) |
| yudor_fair_odds | Number | Fair odds (2.05) |
| yudor_decision | Select | CORE/EXP/VETO/FLIP/IGNORAR |
| cs_final | Number | Confidence Score (0-100) |
| r_score | Number | Risk Score (0-1) |
| tier | Number | 1, 2, or 3 |
| full_analysis | Long Text | Complete JSON analysis |
| data_quality | Number | 0-100 |
| status | Select | ANALYZED/BET_ENTERED/RESULT_RECORDED |

### Table 2: Bets_Entered

| Field | Type | Purpose |
|-------|------|---------|
| match_id | Link | → Match_Analyses |
| entry_timestamp | DateTime | When bet placed |
| market_ah_line | Number | What market offered (-0.75) |
| market_ah_odds | Number | Odds you got (1.95) |
| edge_pct | Number | Your calculated edge (15.2%) |
| stake | Number | Amount bet (100) |
| expected_value | Formula | stake * (edge_pct/100) |
| notes | Long Text | Why you entered |

### Table 3: Results

| Field | Type | Purpose |
|-------|------|---------|
| match_id | Link | → Match_Analyses |
| result_timestamp | DateTime | When result recorded |
| final_score | Text | 2-1 |
| ah_result | Select | WIN/PUSH/LOSS |
| profit_loss | Number | +95 or -100 |
| yudor_correct | Checkbox | Was fair line accurate? |
| fair_line_accuracy | Number | How close was Claude? |
| lessons_learned | Long Text | What to improve |

### View 1: Active Bets
- Filter: status = "BET_ENTERED"
- Sort: date ascending
- Shows: All pending bets

### View 2: Learning Queue
- Filter: status = "RESULT_RECORDED" AND ah_result = "LOSS"
- Sort: date descending
- Shows: Losses to analyze

### View 3: Performance Dashboard
- Grouped by: league, decision tier
- Shows: Win rate, avg edge, ROI

---

## 🚀 DAILY WORKFLOW

### Morning Routine (15 minutes)

```bash
# 1. Analyze today's matches
python master_orchestrator.py analyze "Flamengo vs Bragantino, Brasileirão, 25/11/2025, 19:00"
```

**What happens:**
```
🔍 STAGE 1: Scraping URLs (2 min)
├─ Finds SportsMole, Transfermarkt, News
└─ Creates match_data_v29.json

🔍 STAGE 2: Extracting data (5 min)
├─ Claude visits each URL
├─ Extracts: form, injuries, values, news
└─ Creates match_data_PROCESSED.json

🎯 STAGE 3: Yudor Analysis - BLIND (5 min)
├─ Claude runs Q1-Q19
├─ Calculates fair AH: -1.25
├─ Decision: CORE
├─ Confidence: 85%
└─ Saves to analysis_history/

💾 STAGE 4: Save to Airtable (instant)
└─ Record created in Match_Analyses

📊 STAGE 5: Edge Calculation (3 min)
├─ Shows: Fair AH = -1.25
├─ You check Betfair: -0.75 @ 1.95
├─ You calculate: ~15% edge
├─ You decide: BET
└─ Saves to Bets_Entered table
```

### Pre-Match (2-4 hours before)

```bash
# Check for line movements
# Compare current market to your entry
# Decide if still good value
```

### Post-Match (after result)

```bash
# Record result
python master_orchestrator.py track FLAvsBRA_25112025 --result "2-1" --won

# System updates:
# - Results table
# - Match status → RESULT_RECORDED
# - Calculates profit/loss
# - Checks Claude's accuracy
```

### Weekly Review

```bash
# Analyze losses
# Review learning queue in Airtable
# Identify patterns
# Update system if needed
```

---

## 🔧 SETUP INSTRUCTIONS

### 1. GitHub Repository Setup

```bash
# Create repository
git init yudor-betting-system
cd yudor-betting-system

# Create structure
mkdir prompts scripts config analysis_history
touch README.md .gitignore

# Add files
cp /path/to/master_orchestrator.py scripts/
cp /path/to/scraper.py scripts/
cp /path/to/prompts/* prompts/

# Commit
git add .
git commit -m "Initial Yudor system"

# Push to GitHub
git remote add origin https://github.com/yourusername/yudor-betting-system.git
git push -u origin main
```

### 2. Airtable Setup

**Step 1: Create Base**
1. Go to airtable.com
2. Create new base: "Yudor Betting System"
3. Create 3 tables (see schema above)

**Step 2: Get API Key**
1. Account → Developer Hub
2. Create personal access token
3. Scopes: data.records:read, data.records:write
4. Copy token

**Step 3: Get Base ID**
1. Open your base
2. Help → API Documentation
3. Copy Base ID (starts with "app")

### 3. Environment Setup

```bash
# Install Python dependencies
pip install anthropic pyairtable python-dotenv

# Create .env file
cat > .env << EOF
ANTHROPIC_API_KEY=your_claude_key_here
AIRTABLE_API_KEY=your_airtable_token_here
AIRTABLE_BASE_ID=your_base_id_here
EOF

# Add to .gitignore
echo ".env" >> .gitignore
echo "config/config.json" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
```

### 4. Test Run

```bash
# Test single match
python scripts/master_orchestrator.py analyze "Flamengo vs Bragantino, Brasileirão, 25/11/2025, 19:00"

# Check Airtable
# Verify record created

# Check local files
ls analysis_history/
```

---

## 💡 EDGE CALCULATION METHODOLOGY

### Step 1: Claude Provides Fair Line (Blind)
```
Yudor Fair Line: Flamengo -1.25
Fair Odds: 2.05
Implied Win Probability: 48.8%
```

### Step 2: You Check Market
```
Betfair offers: Flamengo -0.75 @ 1.95
```

### Step 3: Calculate Line Difference
```
Fair Line: -1.25
Market Line: -0.75
Difference: +0.5 lines in your favor
```

### Step 4: Estimate Edge %
```
Each 0.25 line = ~5% edge (rough)
0.5 lines = ~10-15% edge

OR use odds comparison:
Fair odds: 2.05 (48.8% probability)
Market odds: 1.95 (51.3% probability)
If you believe fair is right → ~2.5% edge

COMBINED estimate: ~12% edge
```

### Step 5: Decision Matrix

| Edge % | Decision | Tier | Action |
|--------|----------|------|--------|
| < 5% | No Value | - | Skip |
| 5-8% | Marginal | - | Usually skip |
| 8-12% | Good Value | CORE/EXP | Bet (size based on tier) |
| 12-20% | Strong Value | CORE | Bet (standard size) |
| > 20% | Exceptional | CORE | Bet (max size) |

### Edge Calculation Examples

**Example 1: Standard Value**
- Fair: Palmeiras -1.0
- Market: Palmeiras -0.75
- Difference: +0.25 lines
- Edge: ~6-8%
- Decision: Bet if CORE tier

**Example 2: Strong Value**
- Fair: Inter -0.5
- Market: Inter +0.25
- Difference: +0.75 lines
- Edge: ~18-20%
- Decision: BET! (Even if EXP tier)

**Example 3: Reverse Value**
- Fair: Santos -0.75
- Market: Santos -1.25
- Difference: -0.5 lines (NEGATIVE)
- Edge: NONE (market less favorable)
- Decision: SKIP

---

## 🔄 LEARNING SYSTEM

### How System Learns from Results

```
After each bet:
1. Record actual result
2. Compare to Claude's prediction
3. Analyze what went wrong (if loss)
4. Feed back to system

Monthly audit:
1. Query losses from Airtable
2. Send to Claude with audit_prompt.md
3. Claude identifies patterns
4. Suggests Q-ID weight adjustments
5. You decide whether to implement
```

### Audit Process

```bash
# After 30 bets, run audit
# Claude analyzes all losses
# Identifies:
# - Which Q-scores were most wrong
# - Which leagues/teams underperform
# - Which situations to avoid

# Example output:
"Q7 (Tactical Matchup) was wrong in 8/12 losses.
Recommendation: Reduce weight from 8 to 6.
Also: Serie A away teams overperformed expectations.
Consider +0.25 adjustment for Serie A away."
```

---

## 🎯 COMMANDS REFERENCE

### Analysis Commands

```bash
# Analyze single match
python master_orchestrator.py analyze "Home vs Away, League, DD/MM/YYYY, HH:MM"

# Batch analyze (all in matches.txt)
python master_orchestrator.py batch

# Review past analysis
python master_orchestrator.py review FLAvsBRA_25112025

# Quick check (just fair line, no full analysis)
python master_orchestrator.py quick "Flamengo vs Bragantino"
```

### Tracking Commands

```bash
# Record result - WIN
python master_orchestrator.py track FLAvsBRA_25112025 \
  --result "2-1" \
  --won \
  --profit 95

# Record result - LOSS
python master_orchestrator.py track FLAvsBRA_25112025 \
  --result "1-1" \
  --lost \
  --loss -100 \
  --notes "Drew when needed win"

# Record result - PUSH
python master_orchestrator.py track FLAvsBRA_25112025 \
  --result "2-0" \
  --push
```

### Learning Commands

```bash
# Monthly audit
python master_orchestrator.py audit --last-30-days

# Analyze specific loss
python master_orchestrator.py analyze-loss FLAvsBRA_25112025

# Performance report
python master_orchestrator.py report --month 11 --year 2025
```

---

## 📊 AIRTABLE AUTOMATION IDEAS

### Automations to Set Up

**1. Bet Reminder**
- Trigger: 2 hours before match
- Action: Send email/notification
- Reminder to check lines

**2. Result Reminder**
- Trigger: 2 hours after match end
- Action: Send notification
- Reminder to record result

**3. Weekly Report**
- Trigger: Every Monday 9am
- Action: Generate report email
- Shows: Week's performance

**4. Loss Alert**
- Trigger: New record in Results with "LOSS"
- Action: Add to Learning Queue
- Flags for audit

---

## 🎓 ADVANCED FEATURES (Future)

### Phase 1 (Next 2 weeks)
- [ ] Batch processing
- [ ] Result tracking automation
- [ ] Basic performance dashboard

### Phase 2 (Next month)
- [ ] Automated audit system
- [ ] Line movement tracking
- [ ] Telegram bot interface

### Phase 3 (3 months)
- [ ] Machine learning integration
- [ ] Automatic Q-weight optimization
- [ ] Advanced bankroll management

---

## ✅ SUCCESS METRICS

Track these monthly:

### Analysis Quality
- Extraction success rate: Target 80%+
- Data completeness: Target 85%+
- Analysis time: Target < 15 min/match

### Betting Performance
- Win rate: Target 55%+
- ROI: Target +15%+
- Average edge on entered bets: Target 10%+

### System Accuracy
- Fair line accuracy: ±0.5 lines of actual
- Decision accuracy (CORE): 60%+ win rate
- R-Score effectiveness: VETO games < 45% win rate

---

## 🚨 IMPORTANT REMINDERS

1. **Blind Pricing is Key**
   - Never show market odds to Claude
   - Always calculate edge manually
   - Trust your analysis, not the market

2. **Track Everything**
   - Every analysis saved
   - Every bet recorded
   - Every result documented

3. **Learn from Losses**
   - Monthly audits essential
   - Pattern recognition
   - Continuous improvement

4. **Bankroll Management**
   - Standard unit: 1-2% of bankroll
   - CORE tier: 2% max
   - EXP tier: 1% max
   - Never chase losses

5. **Edge is Everything**
   - Minimum 8% edge to bet
   - Higher edge = higher confidence
   - No edge = no bet

---

## 🎯 YOUR COMPLETE SYSTEM

**You now have:**

✅ Master orchestrator (one command to rule them all)  
✅ Blind pricing methodology (no bias)  
✅ Persistent database (Airtable + files)  
✅ Learning system (improves over time)  
✅ Professional workflow (15 min/day)  
✅ Full documentation (everything explained)  

**Next steps:**
1. Set up GitHub repository
2. Configure Airtable base
3. Test with one match
4. Start tracking bets
5. Watch your edge compound!

---

*Complete System Architecture v1.0*  
*Professional Betting with Intelligence*  
*"Better data → Better analysis → Better bets → Better results"*
