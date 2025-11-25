# Data Extraction Template for Yudor v5.3

**Purpose**: Ensure consistent, structured data extraction from all sources
**Used by**: Claude AI during analysis consolidation
**Updates**: This template improves over time as we identify data gaps

---

## 📋 Data Source Checklist

For each match analysis, Claude must extract data from these **controlled sources**:

### Source 1: FootyStats (Primary Match Data)
**URL**: `https://footystats.org/...`
**Data Points**:
- [ ] Team form (last 5 games)
- [ ] Head-to-head history
- [ ] Expected goals (xG) recent trend
- [ ] Home/Away performance splits
- [ ] Goals scored/conceded averages
- [ ] Clean sheet percentage
- [ ] BTTS (Both Teams To Score) percentage

**Extraction Format**:
```json
{
  "source": "footystats",
  "team": "Barcelona",
  "form_last_5": "W-W-D-W-L",
  "xg_trend": "increasing",
  "home_record": {"W": 8, "D": 2, "L": 1},
  "goals_per_game": 2.3,
  "clean_sheets_pct": 45.5
}
```

---

### Source 2: FBref (Advanced Statistics)
**Accessed via**: `soccerdata` library
**Data Points**:
- [ ] Defensive actions (tackles + interceptions)
- [ ] Pressing intensity (PPDA proxy)
- [ ] Corner kicks per game
- [ ] Aerial duels won percentage
- [ ] Per-player xG (top 5 players)
- [ ] Pass completion percentage
- [ ] Shots on target ratio

**Extraction Format**:
```json
{
  "source": "fbref",
  "team": "Barcelona",
  "defensive_actions_per_game": 168.3,
  "corners_per_game": 6.5,
  "aerials_won_pct": 56.0,
  "top_players_xg": [8.5, 6.2, 4.1, 3.8, 2.9],
  "pressing_level": "high"
}
```

---

### Source 3: SofaScore/FlashScore (Lineups - Manual Entry)
**URL**: `https://www.sofascore.com/...` or `https://www.flashscore.com/...`
**Data Points**:
- [ ] Confirmed starting XI (1-2 hours before kickoff)
- [ ] Key player availability
- [ ] Injury updates
- [ ] Tactical formation (manually verified)

**Extraction Format**:
```json
{
  "source": "sofascore_manual",
  "team": "Barcelona",
  "lineup_confirmed": true,
  "key_players_starting": ["Lewandowski", "Pedri", "Gavi"],
  "injuries": ["Araujo (out)"],
  "formation": "4-3-3",
  "formation_verified": true
}
```

---

### Source 4: Betting Odds (Market Consensus)
**URLs**:
- Odds Portal: `https://www.oddsportal.com/...`
- Betfair: `https://www.betfair.com/...`

**Data Points**:
- [ ] Asian Handicap market line
- [ ] Market movement (opening vs current)
- [ ] Overround percentage
- [ ] Pinnacle odds (sharp bookmaker)

**Extraction Format**:
```json
{
  "source": "odds_portal",
  "market_ah_line": -1.0,
  "opening_odds": 1.95,
  "current_odds": 1.87,
  "market_movement": "down",
  "overround": 103.2,
  "pinnacle_line": -1.0
}
```

---

## 🔍 Data Quality Scoring

Claude must evaluate each data source on a 5-point scale:

```json
{
  "data_quality": {
    "footystats": 5,  // Complete, recent data
    "fbref": 5,       // Full season stats available
    "lineups": 5,     // Confirmed 90 min before kickoff
    "odds": 4,        // Available but moving
    "overall_score": 4.75
  }
}
```

**Quality Criteria**:
- 5/5: Complete, verified, recent (< 24 hours)
- 4/5: Complete but may be 1-2 days old
- 3/5: Mostly complete, some estimates
- 2/5: Significant gaps, using defaults
- 1/5: Minimal data, mostly defaults

---

## 📊 Structured Output Format

Claude must organize extracted data into this structure:

```json
{
  "match_id": "BarcelonavsAthleticClub_22112025",
  "extraction_timestamp": "2025-11-22T10:30:00Z",
  "data_sources": {
    "footystats": { /* extracted data */ },
    "fbref": { /* extracted data */ },
    "lineups": { /* extracted data */ },
    "odds": { /* extracted data */ }
  },
  "data_quality": {
    "overall_score": 4.75,
    "breakdown": { /* per-source scores */ },
    "missing_critical": [],
    "proceed": true
  },
  "q_score_inputs": {
    "Q1": { /* inputs for Q1 scoring */ },
    "Q2": { /* inputs for Q2 scoring */ },
    // ... Q3-Q19
  }
}
```

---

## 🎯 Q-Score Input Mapping

### Q7 (Pressing Intensity) - FBref Data
```json
{
  "Q7_inputs": {
    "home_defensive_actions": 168.3,
    "away_defensive_actions": 142.1,
    "home_pressing_level": "high",
    "away_pressing_level": "medium",
    "source": "fbref",
    "confidence": 5
  }
}
```

### Q8 (Set-Piece Quality) - FBref Data
```json
{
  "Q8_inputs": {
    "home_corners_per_game": 6.5,
    "home_aerials_won_pct": 56.0,
    "away_corners_per_game": 4.2,
    "away_aerials_won_pct": 48.5,
    "source": "fbref",
    "confidence": 5
  }
}
```

### Q14 (Player Form) - FBref Data
```json
{
  "Q14_inputs": {
    "home_in_form_count": 4,
    "home_top_xg": [8.5, 6.2, 4.1],
    "away_in_form_count": 2,
    "away_top_xg": [5.1, 3.8],
    "source": "fbref",
    "confidence": 5
  }
}
```

---

## 🧠 Reasoning Documentation

For each Q-score, Claude must provide:
1. **Data used**: Which sources contributed
2. **Calculation**: How the score was derived
3. **Confidence**: Data quality assessment
4. **Reasoning**: Why this score makes sense

**Example**:
```json
{
  "Q7": {
    "home_score": 5,
    "away_score": 3,
    "home_reasoning": "High press (168.3 def actions/game from FBref) → +5",
    "away_reasoning": "Medium press (142.1 def actions/game from FBref) → +3",
    "data_sources": ["fbref"],
    "confidence": 5,
    "calculation": "actions_per_game > 160 → score 5, 120-160 → score 3"
  }
}
```

---

## ✅ Consistency Checks

Before finalizing analysis, Claude must verify:

- [ ] All 19 Q-scores calculated
- [ ] Each Q-score has reasoning
- [ ] Data sources documented
- [ ] Data quality >= 3.0 (or flag for manual review)
- [ ] No placeholder values remain
- [ ] Calculations match documented formulas
- [ ] Edge cases handled (missing data, outliers)

---

## 🔄 Continuous Improvement

**After each match result**:
1. Compare predicted Q-scores vs actual match outcome
2. Identify Q-scores that were inaccurate
3. Update extraction logic or scoring formulas
4. Document learnings in `.claude/improvements/`

**Example Learning**:
```markdown
# 2025-11-22: Q7 Improvement
- Found: High PPDA teams underperforming against low blocks
- Action: Adjusted Q7 scoring to penalize high press vs defensive teams
- Formula change: Added Q7_opponent_adjustment factor
- Expected impact: +1-2% win rate
```

---

**Version**: 1.0
**Last Updated**: 2025-11-23
**Next Review**: After 50 matches analyzed
