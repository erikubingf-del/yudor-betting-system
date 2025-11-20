# ✅ SETUP CHECKLIST
## Get Your Professional Yudor System Running in 30 Minutes

---

## 🎯 WHAT YOU'RE BUILDING

A professional betting system where you simply say:

```
"Analyze Flamengo vs Bragantino"
```

And get back:
- Complete match analysis
- Claude's fair Asian Handicap line (blind pricing)
- You manually calculate edge vs market
- Everything saved to Airtable automatically
- Persistent memory of all analyses

---

## ✅ STEP 1: AIRTABLE SETUP (10 minutes)

### 1.1 Create Account
- [ ] Go to airtable.com
- [ ] Sign up (free plan is fine to start)

### 1.2 Create Base
- [ ] Click "Add a base"
- [ ] Name it: "Yudor Betting System"

### 1.3 Create Table 1: Match_Analyses
- [ ] Rename Table 1 to "Match_Analyses"
- [ ] Add these fields:

| Field Name | Type | Options |
|------------|------|---------|
| match_id | Single line text | (Primary field) |
| date | Date | Include time: No |
| home_team | Single line text | - |
| away_team | Single line text | - |
| league | Single line text | - |
| analysis_timestamp | Date | Include time: Yes |
| yudor_ah_fair | Number | Precision: 2 decimals |
| yudor_fair_odds | Number | Precision: 2 decimals |
| yudor_decision | Single select | Options: CORE, EXP, VETO, FLIP, IGNORAR |
| cs_final | Number | Precision: 0 decimals |
| r_score | Number | Precision: 2 decimals |
| tier | Number | Precision: 0 decimals |
| full_analysis | Long text | - |
| data_quality | Number | Precision: 0 decimals |
| status | Single select | Options: ANALYZED, BET_ENTERED, RESULT_RECORDED |

### 1.4 Create Table 2: Bets_Entered
- [ ] Add new table: "Bets_Entered"
- [ ] Add these fields:

| Field Name | Type | Options |
|------------|------|---------|
| match_id | Link to Match_Analyses | - |
| entry_timestamp | Date | Include time: Yes |
| market_ah_line | Number | Precision: 2 decimals |
| market_ah_odds | Number | Precision: 2 decimals |
| edge_pct | Number | Precision: 1 decimal |
| stake | Currency | $ |
| notes | Long text | - |

### 1.5 Create Table 3: Results
- [ ] Add new table: "Results"
- [ ] Add these fields:

| Field Name | Type | Options |
|------------|------|---------|
| match_id | Link to Match_Analyses | - |
| result_timestamp | Date | Include time: Yes |
| final_score | Single line text | - |
| ah_result | Single select | Options: WIN, PUSH, LOSS |
| profit_loss | Currency | $ |
| yudor_correct | Checkbox | - |
| lessons_learned | Long text | - |

### 1.6 Get API Credentials
- [ ] Click your profile icon → Developer Hub
- [ ] Create personal access token
- [ ] Name: "Yudor System"
- [ ] Scopes: Select "data.records:read" and "data.records:write"
- [ ] Copy token → Save securely

- [ ] Go back to your base
- [ ] Help → API Documentation
- [ ] Copy Base ID (starts with "app") → Save securely

---

## ✅ STEP 2: GITHUB SETUP (5 minutes)

### 2.1 Create Repository
- [ ] Go to github.com
- [ ] New repository
- [ ] Name: "yudor-betting-system"
- [ ] Private repository
- [ ] Initialize with README

### 2.2 Clone to Your Computer
```bash
git clone https://github.com/yourusername/yudor-betting-system.git
cd yudor-betting-system
```

### 2.3 Create Directory Structure
```bash
mkdir prompts scripts config analysis_history
touch .gitignore .env
```

### 2.4 Create .gitignore
```bash
cat > .gitignore << EOF
.env
config/config.json
*.pyc
__pycache__/
analysis_history/*.json
match_data*.json
*.xlsx
.DS_Store
EOF
```

---

## ✅ STEP 3: COPY FILES (5 minutes)

### 3.1 Download Files from Claude
From this conversation, download:
- [ ] master_orchestrator.py → scripts/
- [ ] CLAUDE_URL_EXTRACTION_PROMPT.md → prompts/extraction_prompt.md
- [ ] scraper.py (your existing) → scripts/
- [ ] YUDOR_API_SYSTEM_PROMPT.md (your existing) → prompts/yudor_analysis_prompt.md

### 3.2 Create .env File
```bash
cat > .env << EOF
ANTHROPIC_API_KEY=your_claude_api_key_here
AIRTABLE_API_KEY=your_airtable_token_here
AIRTABLE_BASE_ID=your_airtable_base_id_here
SERPAPI_KEY=your_serpapi_key_here
EOF
```

Replace with your actual keys!

### 3.3 Create requirements.txt
```bash
cat > requirements.txt << EOF
anthropic>=0.18.0
pyairtable>=2.0.0
python-dotenv>=1.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
EOF
```

---

## ✅ STEP 4: INSTALL DEPENDENCIES (2 minutes)

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

---

## ✅ STEP 5: TEST SETUP (5 minutes)

### 5.1 Test Scraper
```bash
# Create test match
echo "Flamengo vs Bragantino, Brasileirão, 25/11/2025, 19:00" > matches.txt

# Run scraper
cd scripts
python scraper.py

# Check output
ls ../match_data_v29.json  # Should exist
```

### 5.2 Test Orchestrator (Dry Run)
```bash
# Test without running full analysis
python master_orchestrator.py

# Should show help message
```

---

## ✅ STEP 6: FIRST REAL ANALYSIS (10 minutes)

### 6.1 Analyze a Match
```bash
python scripts/master_orchestrator.py analyze "Flamengo vs Bragantino, Brasileirão, 25/11/2025, 19:00"
```

**Watch it work:**
```
🔍 STAGE 1: Scraping URLs
  → Finding SportsMole, Transfermarkt, News...
  → ✅ URLs found

🔍 STAGE 2: Extracting data
  → Claude visiting each URL...
  → Extracting: form, injuries, values...
  → ✅ Data extracted

🎯 STAGE 3: Yudor Analysis (BLIND)
  → Running Q1-Q19...
  → ✅ Analysis complete
  
  📊 RESULTS:
     Fair AH Line: -1.25
     Decision: CORE
     Confidence: 85%
     CS Final: 82
     R-Score: 0.12

💾 STAGE 4: Saved to Airtable
  → ✅ Record created

📊 STAGE 5: Edge Calculation
   Yudor's Fair Line: -1.25
   
   Now check Betfair/market for actual lines:
   What's the market AH line? (e.g., -1.0): 
```

### 6.2 Enter Market Line
```
What's the market AH line? (e.g., -1.0): -0.75
What are the odds? (e.g., 1.95): 1.95

📊 EDGE ANALYSIS:
   Fair Line: -1.25
   Market Line: -0.75
   Difference: +0.50
   Estimated Edge: 12.5%

✅ POSITIVE EDGE (≥8%) - Consider betting!

Enter this bet? (y/n): y
Stake amount: 100

✅ Bet recorded in Airtable
```

### 6.3 Verify in Airtable
- [ ] Open Airtable base
- [ ] Check Match_Analyses → Should have 1 record
- [ ] Check Bets_Entered → Should have 1 record (if you entered bet)

---

## ✅ STEP 7: COMMIT TO GITHUB (2 minutes)

```bash
git add .
git commit -m "Initial Yudor system setup"
git push origin main
```

---

## 🎉 YOU'RE DONE!

### Your System Can Now:

✅ Analyze any match with one command  
✅ Extract data from 6+ sources automatically  
✅ Provide blind pricing (Claude's fair line)  
✅ Let you calculate edge manually  
✅ Save everything to Airtable  
✅ Track all bets and results  
✅ Learn from outcomes  

---

## 📱 DAILY USAGE

### Every Morning:
```bash
# Analyze today's match
python scripts/master_orchestrator.py analyze "Home vs Away, League, DD/MM/YYYY, HH:MM"

# Review Claude's fair line
# Check Betfair for market line
# Calculate edge
# Decide to bet or not
```

### After Match:
```bash
# Record result
python scripts/master_orchestrator.py track MATCH_ID --result "2-1" --won --profit 95
```

### Monthly:
```bash
# Run audit
python scripts/master_orchestrator.py audit --last-30-days

# Review learning suggestions
# Adjust system if needed
```

---

## 🆘 TROUBLESHOOTING

### "Module not found"
```bash
pip install -r requirements.txt
```

### "API key not found"
```bash
# Check .env file exists
cat .env

# Make sure keys are correct
# Load environment variables:
source .env  # Linux/Mac
# or
set -a; source .env; set +a  # More robust
```

### "Airtable error"
- Check API token has correct scopes
- Check Base ID is correct
- Check table names match exactly

### "Scraper fails"
- Check SERPAPI_KEY in config
- Check internet connection
- Try running scraper.py standalone first

---

## 📚 NEXT STEPS

After your first successful analysis:

1. **Analyze 3-5 test matches** (don't bet yet)
2. **Review data quality** in Airtable
3. **Calibrate edge calculation** (compare Claude vs market)
4. **Start betting small** (1% bankroll max)
5. **Track results religiously**
6. **Request audit after 30 bets**

---

## 🎯 EXPECTED TIMELINE

- **Setup:** 30 minutes
- **First analysis:** 15 minutes
- **Daily usage:** 10-15 minutes per match
- **Weekly review:** 30 minutes
- **Monthly audit:** 1 hour

**ROI:** Finding just 2-3 value bets per month pays for entire system!

---

## ✅ FINAL CHECKLIST

Before going live:

- [ ] Airtable base created with all 3 tables
- [ ] API keys in .env file
- [ ] GitHub repository set up
- [ ] Python dependencies installed
- [ ] Test analysis completed successfully
- [ ] Record shows in Airtable
- [ ] Understood blind pricing methodology
- [ ] Know how to calculate edge manually
- [ ] Bankroll management plan in place
- [ ] Ready to track all bets

---

## 🚀 YOU'RE READY!

Welcome to professional betting analysis!

**Your advantages:**
- ✅ Data-driven decisions
- ✅ No emotional betting
- ✅ Systematic approach
- ✅ Continuous learning
- ✅ Complete records

**Remember:**
- Bet only with 8%+ edge
- Trust the system
- Track everything
- Learn from losses
- Be patient

---

*Setup Checklist v1.0*  
*30 minutes to professional betting*  
*"From setup to profit"*
