# YUDOR BETTING SYSTEM - AI Context & System Overview

> **For AI Agents:** This document is the single source of truth for understanding the YUDOR system architecture, methodology, and operational rules.

**Last Updated:** 2025-11-25
**System Version:** Production v1.0
**Status:** Operational

---

## 1. System Philosophy

The YUDOR (Yield Under Diversified Odds Reasoning) system is an **Asian Handicap (AH) betting analysis engine** that combines:

1. **Quantitative Analysis:** Statistical data (xG, form, rankings)
2. **Qualitative Reasoning:** LLM-powered analysis of news, injuries, tactics
3. **Mathematical Precision:** Fair odds calculation to find market value

**Core Principle:** We don't predict winners—we identify **mispriced Asian Handicap lines** where our calculated fair odds exceed market odds.

---

## 2. The Mathematical Foundation

### 2.1 Probability Normalization

All probabilities MUST sum to 100%:

```
raw_casa + raw_vis + pr_empate = should be 100%

If not 100%:
  difference = 100 - (raw_casa + raw_vis + pr_empate)
  pr_casa_normalized = raw_casa + (difference / 2)
  pr_vis_normalized = raw_vis + (difference / 2)
```

**Critical Rule:** ALWAYS distribute the difference EQUALLY between casa and vis. The draw probability (pr_empate) is fixed from market odds.

### 2.2 Fair Odds Calculation

The system uses a **step-based scaling approach**:

```python
# Baseline: Moneyline odds at AH -0.5
moneyline_odds = 100 / favorite_probability_pct

# Scaling factors per 0.25 AH step:
- Harder (negative): multiply by 1.15 per step
- Easier (positive): multiply by 0.85 per step

# Examples:
AH -0.5: moneyline_odds × 1.15⁰ = baseline
AH -0.75: moneyline_odds × 1.15¹
AH -1.0: moneyline_odds × 1.15²
AH -0.25: moneyline_odds × 0.85¹
AH 0.0: moneyline_odds × 0.85²
```

**Target:** Find the AH line where fair odds are **closest to 2.0** (50% implied probability with balanced risk/reward).

### 2.3 The Value Equation

```
Expected Value (EV) = (Fair_Odds / Market_Odds) - 1

Bet if: EV > 0 (our odds higher than market)
```

---

## 3. System Architecture

### 3.1 Directory Structure

```
yudor-betting-system/
├── scripts/                              # All operational scripts
│   ├── master_orchestrator.py           # Main workflow orchestrator
│   ├── recalculate_all_yudor_fair_odds_CORRECT.py  # Fair odds recalculation
│   ├── comprehensive_stats_scraper.py   # FBRef + FootyStats scraper
│   ├── validate_airtable_schema.py      # Schema validation
│   └── [other utilities]
├── archived_analyses/                    # Historical analysis JSON files
│   └── YYYY-MM-DD/
│       └── {match_id}_analysis.json     # Single source of truth for each match
├── documentation/                        # System documentation (this folder)
├── .env                                 # API keys and credentials
└── requirements.txt                     # Python dependencies
```

### 3.2 Data Flow

```
1. Scraper → Gather stats (xG, form, injuries)
2. LLM Analysis → Q1-Q19 scoring (techniques, tactics, motivation)
3. Consolidation → Combine into raw_casa, raw_vis scores
4. Normalization → Ensure probabilities sum to 100%
5. Fair Odds Calc → Find optimal AH line closest to 2.0
6. Airtable Update → Store results for analysis
7. Archival → Save complete JSON to archived_analyses/
```

---

## 4. The Q1-Q19 Scoring System

**Purpose:** Convert subjective factors into quantitative scores.

### Categories & Weights

| Category | Questions | Focus |
|----------|-----------|-------|
| **Technique** | Q1-Q4 | Player quality, offensive/defensive capability |
| **Tactics** | Q5-Q8 | Manager quality, formations, pressing, set pieces |
| **Motivation** | Q9-Q10 | League position pressure, derby/revenge factors |
| **Form** | Q11-Q12 | Recent results, opponent quality context |
| **Performance** | Q13-Q14 | xG delta (luck), overall performance ratings |
| **Injuries** | Q15-Q16 | Key player absences, defensive cluster injuries |
| **Home/Away** | Q17-Q19 | Home advantage, H2H record |

**Output:**
- `raw_casa` = sum of home team scores
- `raw_vis` = sum of away team scores

These are NOT percentages—they are absolute scores that get normalized later.

---

## 5. Decision Logic

### 5.1 Normal Scenarios (CORE, EXP, VETO)

**CORE:** Standard confidence bet
- R-Score < 0.25
- Clear favorite
- AH line: Negative or zero for favorite
- Bet on favorite with calculated AH line

**EXP (Experimental):** Lower confidence
- Marginal differences
- Data quality issues
- Still bet on favorite but with caution

**VETO:** Do not bet
- High risk detected
- Insufficient data
- Conflicting signals

### 5.2 FLIP Scenarios

**When it happens:**
- R-Score ≥ 0.25 (high risk in favorite)
- Severe injuries to favorite
- Critical tactical mismatches
- Favorite has structural issues despite market odds

**Action:**
- System "flips" from recommending favorite to underdog
- AH line becomes **positive** (underdog receives advantage)
- Bet on underdog instead of favorite

**Example:**
```
FC Köln vs Eintracht Frankfurt
- Frankfurt favorite (50.35% vs 23.35%)
- BUT: Köln missing both starting center-backs
- R-Score = 0.25 (threshold)
- Decision: FLIP
- Result: Bet on FC Köln (underdog) with AH +1.25
```

---

## 6. Airtable Schema

### Match Analyses Table

| Field | Type | Purpose |
|-------|------|---------|
| match_id | Text | Unique identifier (TeamAvsTeamB_DDMMYYYY) |
| Home Team | Text | Home team name |
| Away Team | Text | Away team name |
| League | Text | Competition name |
| match_date | Date | Match date |
| **Yudor AH Fair** | Number | Calculated optimal AH line |
| **Yudor Fair Odds** | Number | Fair odds at that AH line |
| **Yudor AH Team** | Text | Which team to bet on |
| **Yudor Decision** | Select | CORE / EXP / FLIP / VETO |
| CS Final | Number | Confidence score (0-100) |
| R Score | Number | Risk score (0-1, threshold 0.25) |
| Tier | Number | League quality tier |
| Data Quality | Number | % of data completeness |
| Q1-Q19 Scores | Long Text | JSON of all Q scores |
| Full Analysis | Long Text | Complete analysis JSON |

### Bet Records Table

Links to Match Analyses for actual betting tracking.

### Learning Ledger Table

Tracks outcomes to improve future predictions.

---

## 7. Critical Operational Rules

### 7.1 The Golden Rules

1. **Single Source of Truth:** `archived_analyses/*.json` files are canonical. Airtable is a view.
2. **Never Skip Normalization:** Always normalize probabilities to 100% before calculations.
3. **FLIP Scenarios are Sacred:** When Decision=FLIP, preserve the archived AH line (it contains complex R-Score logic).
4. **Check All AH Lines:** The algorithm MUST check AH -3.0 to 0.0 in 0.25 increments to find closest to 2.0.
5. **Positive AH = Underdog Only:** Positive AH lines should NEVER be assigned to favorites (except in FLIP scenarios).

### 7.2 Common Pitfalls to Avoid

❌ **Using archived probabilities directly** → They may be wrong
✅ **Recalculate from raw_casa, raw_vis, pr_empate**

❌ **Skipping AH -0.25 in search** → Will miss optimal lines
✅ **Check all lines from -3.0 to 0.0 in 0.25 steps**

❌ **Assigning positive AH to favorites** → Logic error
✅ **Negative/zero for favorites, positive only for underdogs in FLIP**

❌ **Forgetting to distribute normalization equally** → Skewed probabilities
✅ **Add (100 - sum) / 2 to BOTH casa and vis**

---

## 8. Key Scripts & Their Purposes

### 8.1 Production Scripts

**[master_orchestrator.py](../scripts/master_orchestrator.py)**
- Main workflow engine
- Coordinates scraping → analysis → Airtable update
- Entry point for new match analyses

**[recalculate_all_yudor_fair_odds_CORRECT.py](../scripts/recalculate_all_yudor_fair_odds_CORRECT.py)**
- Recalculates fair odds for all matches
- Uses correct normalization methodology
- Preserves FLIP scenarios from archived data
- **Critical functions:**
  - `calculate_correct_probabilities()` - Normalize to 100%
  - `find_ah_line_closest_to_2()` - Find optimal AH
  - `calculate_odds_at_line()` - Calculate odds at specific AH
  - `determine_yudor_ah_team()` - Assign team based on AH sign

**[comprehensive_stats_scraper.py](../scripts/comprehensive_stats_scraper.py)**
- Scrapes FBRef and FootyStats
- Gathers xG, form, rankings
- Handles multiple leagues

**[validate_airtable_schema.py](../scripts/validate_airtable_schema.py)**
- Ensures Airtable schema matches expectations
- Validates field types and presence
- Run before major updates

### 8.2 Utility Scripts

See [SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md) for complete listing.

---

## 9. Workflow Examples

### 9.1 Analyzing a New Match

```bash
# Step 1: Run master orchestrator
python3 scripts/master_orchestrator.py analyze-fbref "Team A vs Team B, League, DD/MM/YYYY"

# Step 2: Review in Airtable
# - Check Yudor AH Fair, Fair Odds, Decision
# - Verify Data Quality score
# - Read Full Analysis for reasoning

# Step 3: If odds calculation seems off, recalculate
python3 scripts/recalculate_all_yudor_fair_odds_CORRECT.py
```

### 9.2 Fixing Incorrect Fair Odds

```bash
# Recalculate all matches with correct methodology
python3 scripts/recalculate_all_yudor_fair_odds_CORRECT.py

# Script will:
# 1. Read from archived_analyses/*.json
# 2. Recalculate normalized probabilities
# 3. Find AH line closest to 2.0
# 4. Update Airtable automatically
# 5. Show before/after comparison
```

---

## 10. For AI Agents: Best Practices

### When Reading Code
1. **Always check normalization logic first** - This is where most bugs occur
2. **Trace probability flow** - From raw scores → normalized % → fair odds
3. **Verify AH line search** - Must check -3.0 to 0.0 in 0.25 steps
4. **Understand FLIP vs normal** - Different logic paths

### When Writing Code
1. **Use existing functions** - Don't reinvent probability normalization
2. **Add verbose logging** - Print intermediate calculations
3. **Validate inputs** - Check probabilities sum to 100%
4. **Test edge cases** - Very strong favorites, even matches, FLIP scenarios

### When Debugging
1. **Start with archived JSON** - It's the source of truth
2. **Manual calculation first** - Verify math by hand
3. **Compare to working examples** - Use Real Betis or Inter Milan as references
4. **Check Airtable last** - It's the output, not the source

---

## 11. Future Enhancements

**Potential areas for improvement:**
- Automated market odds scraping from Betfair API
- Real-time bet placement integration
- Machine learning weight optimization for Q1-Q19
- Historical performance tracking and ROI analysis
- Telegram/Discord notifications for high-value bets

**DO NOT implement** until core system is stable and profitable.

---

## 12. Quick Reference

### Fair Odds Formula Cheat Sheet
```python
# For favorite with 54% probability:
moneyline = 100 / 54 = 1.85

# AH lines and odds:
AH -1.0:  1.85 × 1.15² = 2.45
AH -0.75: 1.85 × 1.15¹ = 2.13  ← Example: Real Betis
AH -0.5:  1.85 × 1.15⁰ = 1.85
AH -0.25: 1.85 × 0.85¹ = 1.57  ← Example: Brighton (was wrong at -0.5)
AH 0.0:   1.85 × 0.85² = 1.34
```

### Decision Tree
```
Is favorite probability > 50%?
├─ Yes → Is R-Score < 0.25?
│         ├─ Yes → CORE (bet on favorite, negative AH)
│         └─ No → FLIP (bet on underdog, positive AH)
└─ No → Is match close (within 10%)?
          ├─ Yes → EXP (experimental, be cautious)
          └─ No → VETO (don't bet, unclear favorite)
```

---

**Document Maintained By:** System Architect
**Contact:** See repository issues for questions
**License:** Proprietary - Do not distribute
