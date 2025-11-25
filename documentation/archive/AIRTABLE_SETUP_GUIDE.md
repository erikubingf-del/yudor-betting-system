# 🎯 AIRTABLE SETUP GUIDE - Final Structure

**Purpose:** Long-term profitability through comprehensive tracking and learning
**Key Metrics:** CLV (Closing Line Value), Edge Accuracy, Win/Loss Analysis

---

## 📋 TABLE CREATION ORDER (IMPORTANT!)

**Create tables in this order to avoid linking issues:**
1. Table 1: Match Analyses (PRIMARY)
2. Table 2: Bet Records
3. Table 3: Learning Ledger

---

## 🔧 TABLE 1: MATCH ANALYSES (Primary Table)

**Purpose:** Automated storage of all YUDOR predictions
**Updated by:** `master_orchestrator.py` automatically

### Column Setup (in order):

| # | Field Name | Field Type | Options/Config | Auto-filled? |
|---|------------|------------|----------------|--------------|
| 1 | **match_id** | Single line text | *Primary field* | ✅ Code |
| 2 | **match_date** | Date | Format: Local (YYYY-MM-DD) | ✅ Code |
| 3 | **Home Team** | Single line text | - | ✅ Code |
| 4 | **Away Team** | Single line text | - | ✅ Code |
| 5 | **League** | Single line text | - | ✅ Code |
| 6 | **Yudor AH Fair** | Number | Precision: 2 decimals, Allow negative | ✅ Code |
| 7 | **Yudor AH Team** | Single line text | - | ✅ Code |
| 8 | **Yudor Fair Odds** | Number | Precision: 2 decimals | ✅ Code |
| 9 | **Yudor Decision** | Single select | Options: CORE, EXP, VETO, FLIP, SKIP | ✅ Code |
| 10 | **CS Final** | Number | Precision: 1 decimal (0-100 range) | ✅ Code |
| 11 | **R Score** | Number | Precision: 1 decimal | ✅ Code |
| 12 | **Tier** | Number | Integer (1-5) | ✅ Code |
| 13 | **Data Quality** | Number | Precision: 0 decimals (0-100 %) | ✅ Code |
| 14 | **Q1-Q19 Scores** | Long text | Enable rich text formatting | ✅ Code |
| 15 | **Full Analysis** | Long text | Enable rich text formatting | ✅ Code |
| 16 | **Status** | Single select | Options: ANALYZED, BET_PLACED, COMPLETED, SKIPPED | ✅ Code |
| 17 | **Bet Records** | Link to another record | Link to "Bet Records" table, Allow linking to multiple records | Auto-link |
| 18 | **Learning Records** | Link to another record | Link to "Learning Ledger" table, Allow linking to multiple records | Auto-link |

**Note:** Columns 17-18 are added AFTER creating Tables 2 and 3.

---

## 💰 TABLE 2: BET RECORDS (Hybrid: Auto + Manual)

**Purpose:** Track bets placed, market odds, results, and ROI
**Updated by:** Code (auto) + You (manual entry of market data)

### Column Setup (in order):

| # | Field Name | Field Type | Options/Config | Filled by |
|---|------------|------------|----------------|-----------|
| 1 | **Record ID** | Autonumber | - | ✅ Airtable |
| 2 | **Match Analyses** | Link to another record | Link to "Match Analyses", Limit to single record | 🔵 Manual |
| 3 | **match_id** | Lookup | Lookup from "Match Analyses" → match_id | ✅ Auto |
| 4 | **Home Team** | Lookup | Lookup from "Match Analyses" → Home Team | ✅ Auto |
| 5 | **Away Team** | Lookup | Lookup from "Match Analyses" → Away Team | ✅ Auto |
| 6 | **Yudor AH Fair** | Lookup | Lookup from "Match Analyses" → Yudor AH Fair | ✅ Auto |
| 7 | **Yudor AH Team** | Lookup | Lookup from "Match Analyses" → Yudor AH Team | ✅ Auto |
| 8 | **Yudor Fair Odds** | Lookup | Lookup from "Match Analyses" → Yudor Fair Odds | ✅ Auto |
| 9 | **bet_timestamp** | Created time | Include time | ✅ Auto |
| 10 | **Bet Placed** | Checkbox | - | 🔵 Manual |
| 11 | --- | --- | **--- MARKET DATA (Manual Entry) ---** | --- |
| 12 | **Market AH Line** | Number | Precision: 2 decimals, Allow negative | 🔵 Manual |
| 13 | **Market AH Odds** | Number | Precision: 2 decimals | 🔵 Manual |
| 14 | **Closing AH Odds** | Number | Precision: 2 decimals | 🔵 Manual |
| 15 | **Stake** | Currency | Currency: EUR/USD (your choice) | 🔵 Manual |
| 16 | --- | --- | **--- AUTO-CALCULATED METRICS ---** | --- |
| 17 | **Edge %** | Formula | See formula below | ✅ Auto |
| 18 | **Expected Value (EV)** | Formula | See formula below | ✅ Auto |
| 19 | --- | --- | **--- POST-MATCH RESULTS ---** | --- |
| 20 | **Final Score** | Single line text | Format: "2-1" | 🔵 Manual |
| 21 | **AH Result** | Single select | Options: WIN, LOSS, HALF_WIN, HALF_LOSS, PUSH | 🔵 Manual |
| 22 | **P/L** | Currency | Same currency as Stake, Allow negative | 🔵 Manual |
| 23 | **CLV %** | Formula | See formula below | ✅ Auto |
| 24 | **ROI %** | Formula | See formula below | ✅ Auto |
| 25 | **Analysis Completed** | Checkbox | Checked by code after learning analysis | ✅ Code |
| 26 | **Notes** | Long text | Your observations | 🔵 Manual |

### FORMULAS FOR TABLE 2:

#### Edge % (Column 17)
```javascript
IF(
  AND({Yudor Fair Odds}, {Market AH Odds}),
  ROUND(({Yudor Fair Odds} / {Market AH Odds} - 1) * 100, 2),
  BLANK()
)
```

#### Expected Value (Column 18)
```javascript
IF(
  AND({Stake}, {Edge %}),
  ROUND({Stake} * ({Edge %} / 100), 2),
  BLANK()
)
```

#### CLV % (Column 23)
```javascript
IF(
  AND({Closing AH Odds}, {Market AH Odds}),
  ROUND(({Closing AH Odds} / {Market AH Odds} - 1) * 100, 2),
  BLANK()
)
```

#### ROI % (Column 24)
```javascript
IF(
  {Stake},
  ROUND(({P/L} / {Stake}) * 100, 2),
  BLANK()
)
```

---

## 📚 TABLE 3: LEARNING LEDGER (Automated)

**Purpose:** Track learning from BOTH wins and losses
**Updated by:** `master_orchestrator.py` via loss-analysis and win-analysis commands

### Column Setup (in order):

| # | Field Name | Field Type | Options/Config | Filled by |
|---|------------|------------|----------------|-----------|
| 1 | **Analysis ID** | Autonumber | - | ✅ Airtable |
| 2 | **Match Analyses** | Link to another record | Link to "Match Analyses", Limit to single record | ✅ Code |
| 3 | **match_id** | Lookup | Lookup from "Match Analyses" → match_id | ✅ Auto |
| 4 | **analysis_timestamp** | Created time | Include time | ✅ Auto |
| 5 | **outcome_type** | Single select | Options: WIN, LOSS, PUSH | ✅ Code |
| 6 | **final_score** | Single line text | - | ✅ Code |
| 7 | **yudor_correct** | Checkbox | Was prediction directionally correct? | ✅ Code |
| 8 | --- | --- | **--- LOSS ANALYSIS ---** | --- |
| 9 | **failed_q_ids** | Long text | List of failed Q-IDs (e.g., "Q6, Q11, Q17") | ✅ Code |
| 10 | **error_category** | Single line text | Summary (e.g., "Q6: Tactics overestimated") | ✅ Code |
| 11 | **error_type** | Single select | Options: Model Error, Data Error, Variance | ✅ Code |
| 12 | **loss_root_cause** | Long text | Detailed root cause analysis | ✅ Code |
| 13 | **loss_recommendations** | Long text | Specific improvement suggestions | ✅ Code |
| 14 | --- | --- | **--- WIN ANALYSIS ---** | --- |
| 15 | **success_q_ids** | Long text | Q-IDs that were crucial (e.g., "Q6, Q17, Q18") | ✅ Code |
| 16 | **edge_accuracy** | Number | Precision: 2 decimals (actual vs predicted edge) | ✅ Code |
| 17 | **win_factors** | Long text | What made this prediction accurate? | ✅ Code |
| 18 | --- | --- | **--- CONTINUOUS LEARNING ---** | --- |
| 19 | **pattern_tags** | Multiple select | Options: High_Q6, Low_Data_Quality, Big_Favorite, Derby, Tactical_Advantage, Form_Driven, H2H_Driven | ✅ Code |
| 20 | **data_quality_actual** | Number | Precision: 0 decimals (reassessed quality after match) | ✅ Code |
| 21 | **lessons_learned** | Long text | Key takeaways and insights | 🔵 Manual + Code |

---

## 🔗 HOW TO LINK TABLES (Step-by-Step)

### Problem: First column can't be a link in Airtable

### Solution: Use Autonumber or Single Line Text as first column, then add links

### STEP-BY-STEP SETUP:

#### 1️⃣ Create Table 1: Match Analyses
1. Create new table "Match Analyses"
2. Rename "Name" → "match_id" (Single line text)
3. Add all other columns as listed above
4. **Leave columns 17-18 empty for now**

#### 2️⃣ Create Table 2: Bet Records
1. Create new table "Bet Records"
2. First column should be "Record ID" (Autonumber)
3. Click "+ Add field" → Choose "Link to another record"
4. Name it: "Match Analyses"
5. Select table: "Match Analyses"
6. **Important:** Check "Allow linking to multiple records" → NO (uncheck)
7. This creates a reverse link in Match Analyses automatically!

#### 3️⃣ Add Lookup Columns in Table 2
After creating the link, add lookup columns:

1. Click "+ Add field" → Choose "Lookup"
2. Name: "match_id"
3. Choose: "Match Analyses" (the link field)
4. Pick field: "match_id"
5. Repeat for: Home Team, Away Team, Yudor AH Fair, Yudor AH Team, Yudor Fair Odds

**Why Lookup?** It auto-fills data from the linked record. When you link a Bet Record to a Match Analysis, these fields populate automatically!

#### 4️⃣ Create Table 3: Learning Ledger
1. Create new table "Learning Ledger"
2. First column: "Analysis ID" (Autonumber)
3. Second column: Link to "Match Analyses"
4. Add lookup for "match_id"
5. Add all other columns as listed

#### 5️⃣ Update Table 1 with Reverse Links
Go back to Match Analyses table:
- Column 17: Should now show "Bet Records" (link created automatically)
- Column 18: Should now show "Learning Ledger" (link created automatically)

If not visible, click "+ Add field" → You'll see these linked fields available.

---

## 🤖 HOW CODE FILLS THE TABLES

### Table 1: Match Analyses (Code fills directly)
```python
# master_orchestrator.py line 1470-1485
record_data = {
    "match_id": "Barcelona_vs_RealMadrid_20241201",
    "match_date": "2024-12-01",
    "Home Team": "Barcelona",
    "Away Team": "Real Madrid",
    "League": "La Liga",
    "Yudor AH Fair": -0.25,
    "Yudor AH Team": "Barcelona",
    "Yudor Fair Odds": 2.05,
    # ... etc
}
table.create(record_data)  # Creates new record
```

### Table 2: Bet Records (YOU create record, link it, fill manual fields)

**Your workflow:**
1. After YUDOR analysis runs, you see match in Table 1
2. You check market odds on Betfair/Pinnacle
3. If you want to bet:
   - Go to Table 2 "Bet Records"
   - Click "+ New record"
   - **Link to Match Analyses** → Search for match_id → Click to link
   - ✅ All lookup fields auto-fill (match_id, teams, Yudor predictions)
   - 🔵 Check "Bet Placed"
   - 🔵 Enter: Market AH Line, Market AH Odds, Stake
   - 🔵 Before kickoff: Enter Closing AH Odds
   - ✅ Edge % and EV calculate automatically
4. After match:
   - 🔵 Enter: Final Score, AH Result, P/L
   - ✅ CLV % and ROI % calculate automatically

### Table 3: Learning Ledger (Code fills automatically)

**Automated workflow:**
```bash
# After matches finish and you updated Table 2
python3 scripts/master_orchestrator.py learning-analysis --auto

# Code does:
# 1. Finds all Bet Records with results (Final Score filled)
# 2. For each bet:
#    - Creates new record in Learning Ledger
#    - Links to Match Analyses (via match_id)
#    - Fills outcome_type (WIN/LOSS)
#    - Runs Claude analysis
#    - Fills failed_q_ids / success_q_ids
#    - Adds pattern_tags
#    - Calculates edge_accuracy
```

---

## 📊 AIRTABLE VIEWS (Recommended)

After setup, create these views for easy analysis:

### View 1: "Bets to Place" (Table 1)
- Filter: Status = "ANALYZED"
- Filter: Yudor Decision = "CORE" or "EXP"
- Sort: Tier (ascending), CS Final (descending)

### View 2: "Active Bets" (Table 2)
- Filter: Bet Placed = ✓
- Filter: Final Score = Empty
- Sort: bet_timestamp (newest first)

### View 3: "Awaiting Analysis" (Table 2)
- Filter: Final Score = Not empty
- Filter: Analysis Completed = ☐ (unchecked)

### View 4: "Loss Patterns" (Table 3)
- Filter: outcome_type = "LOSS"
- Group by: error_type
- Group by: pattern_tags

### View 5: "Win Patterns" (Table 3)
- Filter: outcome_type = "WIN"
- Group by: pattern_tags

### View 6: "CLV Tracking" (Table 2)
- Filter: Bet Placed = ✓
- Sort: CLV % (descending)
- Show: Positive CLV in green, Negative in red

---

## ✅ VALIDATION CHECKLIST

After setup, verify:

### Table 1: Match Analyses
- [ ] match_id is first column (text)
- [ ] All 16 main columns exist
- [ ] Reverse links to Bet Records and Learning Ledger visible

### Table 2: Bet Records
- [ ] Record ID is first column (autonumber)
- [ ] Match Analyses link exists (column 2)
- [ ] Lookup fields auto-fill when you link a record
- [ ] Edge % formula works
- [ ] Expected Value formula works
- [ ] CLV % formula works
- [ ] ROI % formula works

### Table 3: Learning Ledger
- [ ] Analysis ID is first column (autonumber)
- [ ] Match Analyses link exists
- [ ] match_id lookup auto-fills
- [ ] All columns created

### Test Linking
1. Create a test record in Table 1 manually
2. Create a test record in Table 2
3. Link it to the Table 1 record
4. Verify lookup fields auto-populate
5. Enter some numbers in formulas
6. Verify calculations work

---

## 🎯 SUMMARY

**Key Points:**
1. ✅ First column must be Autonumber or Text (cannot be Link)
2. ✅ Use Lookup fields to auto-fill data from linked records
3. ✅ Formulas calculate Edge %, EV, CLV, ROI automatically
4. ✅ Code fills Table 1 and Table 3 automatically
5. 🔵 You manually fill market data in Table 2
6. ✅ Linking a Bet Record to Match Analysis auto-fills YUDOR predictions

**Your Workflow:**
1. Run analysis → Table 1 fills automatically
2. Check market → Create Bet Record in Table 2, link it, enter odds
3. After match → Update Final Score and P/L in Table 2
4. Run learning analysis → Table 3 fills automatically
5. Review patterns → Improve YUDOR methodology

**This structure enables:**
- 📈 Track CLV (prove you beat the market)
- 🎯 Validate edge accuracy (improve bet sizing)
- 📊 Learn from wins AND losses
- 🔍 Detect systematic patterns
- 💰 Optimize for long-term profitability

---

**Need help?** Run validation: `python3 scripts/validate_loss_ledger.py`
