# 📊 AIRTABLE QUICK REFERENCE

## 3-TABLE STRUCTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│  TABLE 1: MATCH ANALYSES (Primary - Automated by YUDOR)        │
├─────────────────────────────────────────────────────────────────┤
│  Purpose: Store all predictions                                 │
│  Updated: Automatically by master_orchestrator.py               │
│  Key Fields: match_id, Yudor AH Fair, Yudor AH Team            │
└─────────────────────────────────────────────────────────────────┘
                              ↓ links to
┌─────────────────────────────────────────────────────────────────┐
│  TABLE 2: BET RECORDS (Hybrid - Auto + Manual)                 │
├─────────────────────────────────────────────────────────────────┤
│  Purpose: Track bets, market odds, results, ROI                 │
│  Updated: You manually add market data & results                │
│  Key Fields: Market AH Odds, Stake, P/L, CLV %, ROI %          │
│  Auto-calculates: Edge %, Expected Value, CLV, ROI              │
└─────────────────────────────────────────────────────────────────┘
                              ↓ triggers
┌─────────────────────────────────────────────────────────────────┐
│  TABLE 3: LEARNING LEDGER (Automated Analysis)                 │
├─────────────────────────────────────────────────────────────────┤
│  Purpose: Learn from wins AND losses                            │
│  Updated: Automatically by learning-analysis command            │
│  Key Fields: failed_q_ids, success_q_ids, pattern_tags         │
│  Tracks: What worked, what failed, systematic patterns          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 TABLE 1: MATCH ANALYSES (16 columns)

| Column | Name | Type |
|--------|------|------|
| 1 | match_id | Text |
| 2 | match_date | Date |
| 3 | Home Team | Text |
| 4 | Away Team | Text |
| 5 | League | Text |
| 6 | Yudor AH Fair | Number |
| 7 | Yudor AH Team | Text |
| 8 | Yudor Fair Odds | Number |
| 9 | Yudor Decision | Select (CORE/EXP/VETO/FLIP) |
| 10 | CS Final | Number |
| 11 | R Score | Number |
| 12 | Tier | Number |
| 13 | Data Quality | Number |
| 14 | Q1-Q19 Scores | Long text |
| 15 | Full Analysis | Long text |
| 16 | Status | Select (ANALYZED/BET_PLACED/COMPLETED) |

**Plus reverse links (auto-created):**
- Bet Records (from Table 2)
- Learning Records (from Table 3)

---

## 💰 TABLE 2: BET RECORDS (26 columns)

### Core Columns
| Column | Name | Type | Filled by |
|--------|------|------|-----------|
| 1 | Record ID | Autonumber | Auto |
| 2 | Match Analyses | Link | Manual (you link) |

### Auto-filled from Link (Lookup)
| Column | Name | Type |
|--------|------|------|
| 3 | match_id | Lookup |
| 4 | Home Team | Lookup |
| 5 | Away Team | Lookup |
| 6 | Yudor AH Fair | Lookup |
| 7 | Yudor AH Team | Lookup |
| 8 | Yudor Fair Odds | Lookup |

### Bet Placement
| Column | Name | Type | Filled by |
|--------|------|------|-----------|
| 9 | bet_timestamp | Created time | Auto |
| 10 | Bet Placed | Checkbox | Manual |

### Market Data (YOU enter)
| Column | Name | Type | Filled by |
|--------|------|------|-----------|
| 11 | Market AH Line | Number | Manual |
| 12 | Market AH Odds | Number | Manual |
| 13 | Closing AH Odds | Number | Manual |
| 14 | Stake | Currency | Manual |

### Auto-calculated Metrics
| Column | Name | Type |
|--------|------|------|
| 15 | Edge % | Formula |
| 16 | Expected Value (EV) | Formula |

### Post-Match Results (YOU enter)
| Column | Name | Type | Filled by |
|--------|------|------|-----------|
| 17 | Final Score | Text | Manual |
| 18 | AH Result | Select | Manual |
| 19 | P/L | Currency | Manual |

### Auto-calculated Performance
| Column | Name | Type |
|--------|------|------|
| 20 | CLV % | Formula |
| 21 | ROI % | Formula |

### Tracking
| Column | Name | Type | Filled by |
|--------|------|------|-----------|
| 22 | Analysis Completed | Checkbox | Code |
| 23 | Notes | Long text | Manual |

---

## 📚 TABLE 3: LEARNING LEDGER (21 columns)

### Core
| Column | Name | Type | Filled by |
|--------|------|------|-----------|
| 1 | Analysis ID | Autonumber | Auto |
| 2 | Match Analyses | Link | Code |
| 3 | match_id | Lookup | Auto |
| 4 | analysis_timestamp | Created time | Auto |
| 5 | outcome_type | Select (WIN/LOSS/PUSH) | Code |
| 6 | final_score | Text | Code |
| 7 | yudor_correct | Checkbox | Code |

### Loss Analysis
| Column | Name | Type | Filled by |
|--------|------|------|-----------|
| 8 | failed_q_ids | Long text | Code |
| 9 | error_category | Text | Code |
| 10 | error_type | Select | Code |
| 11 | loss_root_cause | Long text | Code |
| 12 | loss_recommendations | Long text | Code |

### Win Analysis
| Column | Name | Type | Filled by |
|--------|------|------|-----------|
| 13 | success_q_ids | Long text | Code |
| 14 | edge_accuracy | Number | Code |
| 15 | win_factors | Long text | Code |

### Continuous Learning
| Column | Name | Type | Filled by |
|--------|------|------|-----------|
| 16 | pattern_tags | Multiple select | Code |
| 17 | data_quality_actual | Number | Code |
| 18 | lessons_learned | Long text | Manual + Code |

---

## 🔗 LINKING FLOW

```
1. Code runs analysis
   ↓
   Creates record in Table 1 (Match Analyses)
   match_id: "Barcelona_vs_RealMadrid_20241201"

2. You check market odds
   ↓
   Create record in Table 2 (Bet Records)
   Link to Match Analyses → Select "Barcelona_vs_RealMadrid_20241201"
   ↓
   Lookup fields auto-fill: Home Team, Yudor AH Fair, etc.

3. You enter manual data
   ↓
   Market AH Odds: 1.95
   Stake: 100
   ↓
   Edge % auto-calculates: 5.1%
   EV auto-calculates: 5.1

4. Match finishes
   ↓
   You enter: Final Score "2-1", AH Result "WIN", P/L "+95"
   ↓
   ROI % auto-calculates: 95%

5. You run learning analysis
   ↓
   Code creates record in Table 3 (Learning Ledger)
   Links to Match Analyses
   ↓
   Analyzes: success_q_ids "Q6, Q17"
   Tags: "Tactical_Advantage", "High_Q6"
```

---

## ⚡ FORMULAS CHEAT SHEET

### Edge %
```javascript
IF(
  AND({Yudor Fair Odds}, {Market AH Odds}),
  ROUND(({Yudor Fair Odds} / {Market AH Odds} - 1) * 100, 2),
  BLANK()
)
```

### Expected Value
```javascript
IF(
  AND({Stake}, {Edge %}),
  ROUND({Stake} * ({Edge %} / 100), 2),
  BLANK()
)
```

### CLV %
```javascript
IF(
  AND({Closing AH Odds}, {Market AH Odds}),
  ROUND(({Closing AH Odds} / {Market AH Odds} - 1) * 100, 2),
  BLANK()
)
```

### ROI %
```javascript
IF(
  {Stake},
  ROUND(({P/L} / {Stake}) * 100, 2),
  BLANK()
)
```

---

## 🎯 YOUR DAILY WORKFLOW

### Morning: New Matches
```bash
# 1. Run YUDOR analysis
python3 scripts/master_orchestrator.py analyze-fbref "Barcelona vs Real Madrid, La Liga, 01/12/2024"

# 2. Check Table 1 in Airtable
#    → See: Yudor AH Fair = -0.25, Yudor AH Team = Barcelona

# 3. Check market (Betfair/Pinnacle)
#    → Market offers: -0.25 @ 1.95

# 4. Create Bet Record in Table 2
#    → Link to match
#    → Enter: Market AH Odds = 1.95, Stake = 100
#    → See auto-calculated Edge % = 5.1%

# 5. Before kickoff
#    → Update: Closing AH Odds = 1.92
#    → See auto-calculated CLV % = -1.5% (market moved against you)
```

### Evening: After Matches
```bash
# 1. Update Table 2 for finished matches
#    → Final Score: "2-1"
#    → AH Result: "WIN"
#    → P/L: +95
#    → ROI % auto-calculates: 95%

# 2. Run learning analysis
python3 scripts/master_orchestrator.py learning-analysis --auto

# 3. Check Table 3 for insights
#    → See which Q-IDs were crucial
#    → See pattern tags
#    → Read recommendations
```

### Weekly: Review Patterns
```bash
# In Airtable:
# 1. Go to Table 3 "Learning Ledger"
# 2. Group by "pattern_tags"
# 3. Look for:
#    → Which tags appear in wins vs losses?
#    → Is "High_Q6" more often in wins?
#    → Is "Low_Data_Quality" more often in losses?

# 4. Adjust YUDOR methodology based on patterns
```

---

## 📈 KEY METRICS TO TRACK

### Daily
- **Edge %** - Are you finding value? (Target: >3%)
- **EV** - Expected value per bet (guides bet sizing)

### Weekly
- **CLV %** - Are you beating closing line? (Target: >0% average)
- **ROI %** - Actual return on investment

### Monthly
- **Win Rate** - % of bets won
- **Average CLV** - Long-term profitability indicator
- **Failed Q-IDs** - Which Q-IDs need adjustment?
- **Success Q-IDs** - Which Q-IDs are most reliable?

### Quarterly
- **Pattern Analysis** - Systematic biases
- **Edge Accuracy** - Is your edge calculation accurate?
- **Methodology Adjustments** - Update Q-weights based on learnings

---

## ✅ QUICK CHECKS

### Is Table 2 setup correct?
1. Create a test Bet Record
2. Link it to any Match Analysis
3. Check: Do lookup fields auto-fill? ✅
4. Enter test numbers in Market AH Odds and Stake
5. Check: Does Edge % calculate? ✅

### Are formulas working?
- Edge %: Should show percentage (e.g., 5.1%)
- EV: Should show currency (e.g., 5.1)
- CLV %: Should show percentage (e.g., -1.5%)
- ROI %: Should show percentage (e.g., 95%)

### Is linking correct?
- Table 1 should show count of linked Bet Records
- Table 1 should show count of linked Learning Records
- When you open a Bet Record, you should see linked Match Analysis

---

**This structure optimizes for long-term profitability through:**
1. ✅ CLV tracking (proves you beat the market)
2. ✅ Edge accuracy validation (improves bet sizing)
3. ✅ Win AND loss analysis (comprehensive learning)
4. ✅ Pattern detection (finds systematic edges/biases)
5. ✅ Continuous improvement (data-driven methodology updates)
