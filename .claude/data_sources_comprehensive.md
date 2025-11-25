# Comprehensive Data Sources - Yudor v5.3

**Purpose**: Document ALL data sources and their reliability for Claude AI
**Goal**: Maximum information, zero hallucination, high conviction analysis

---

## 🎯 Source Hierarchy

### Tier 1: soccerdata Library (HIGHEST RELIABILITY)

**Why Tier 1:**
- Professional data scrapers maintained by community
- No authentication needed for FBref
- Handles website changes automatically
- Cached for performance

#### 1.1 FBref (Quality: 5/5)

**What it provides:**

```json
{
  "standard": {
    "matches": 12,
    "goals": 28,
    "assists": 15,
    "xG": 26.3,
    "xAG": 14.8,
    "shots": 156,
    "shots_on_target": 67
  },
  "defense": {
    "tackles": 182,
    "interceptions": 143,
    "blocks": 56,
    "clearances": 98,
    "pressures": 2048
  },
  "possession": {
    "touches": 8942,
    "touches_def_pen_area": 234,
    "touches_att_pen_area": 456,
    "dribbles_completed": 89,
    "dribbles_attempted": 145,
    "carries": 1234
  },
  "passing": {
    "passes_completed": 5678,
    "passes": 6543,
    "pass_completion_pct": 86.8,
    "key_passes": 123,
    "passes_into_final_third": 456,
    "through_balls": 23
  },
  "shooting": {
    "shots": 156,
    "shots_on_target": 67,
    "shots_on_target_pct": 42.9,
    "goals_per_shot": 0.18,
    "goals_per_shot_on_target": 0.42
  },
  "misc": {
    "yellow_cards": 23,
    "red_cards": 1,
    "fouls": 145,
    "fouls_drawn": 167,
    "offsides": 34,
    "corners": 78,
    "aerials_won": 234,
    "aerials_won_pct": 56.7
  },
  "top_players": [
    {
      "name": "Lewandowski",
      "minutes": 1080,
      "goals": 12,
      "assists": 5,
      "xG": 11.2,
      "xAG": 4.8
    }
    // ... top 5 players
  ]
}
```

**Use for Q-scores:**
- Q1: Recent form (via schedule)
- Q2: Goals scored (standard.goals)
- Q3: Goals conceded (standard.goals_against)
- Q4: xG (standard.xG, standard.xAG)
- Q5: Home/Away form (schedule filtered by venue)
- Q7: Pressing (defense.tackles + defense.interceptions + defense.pressures)
- Q8: Set pieces (misc.corners + misc.aerials_won_pct)
- Q10: Head-to-head (schedule filtered by opponent)
- Q11: Streak (schedule recent results)
- Q12: Over/Under form (standard.goals trends)
- Q13: Discipline (misc.yellow_cards, misc.red_cards)
- Q14: Player form (top_players xG, xAG)
- Q15: Attack vs Defense (standard.xG vs opponent.defense)
- Q16: Possession (possession.touches, passing.pass_completion_pct)
- Q17: Shots quality (shooting.shots_on_target_pct)
- Q18: Conversion (shooting.goals_per_shot)
- Q19: Clean sheets (via schedule + goals_conceded)

#### 1.2 SofaScore (Quality: 4/5)

**What it provides:**

```json
{
  "league_table": {
    "position": 1,
    "points": 34,
    "wins": 11,
    "draws": 1,
    "losses": 0,
    "goals_for": 33,
    "goals_against": 8
  },
  "recent_form": "WWDWW"  // Last 5 matches
}
```

**Use for Q-scores:**
- Q1: Recent form (recent_form string)
- Q2: Goals scored (league_table.goals_for)
- Q3: Goals conceded (league_table.goals_against)
- Q5: Home/Away form (schedule filtered)
- Q11: Current streak (recent_form analysis)

#### 1.3 FotMob (Quality: 4/5)

**What it provides:**

```json
{
  "league_position": 1
  // Limited compared to FBref/SofaScore
}
```

**Use for Q-scores:**
- Q1: League position as form proxy
- Mainly as fallback for other sources

---

### Tier 2: URL Extraction (MEDIUM RELIABILITY)

**Why Tier 2:**
- Depends on website structure
- May break when sites change
- Requires web_fetch tool or scraping
- Good for news/injuries/lineups

**What it provides:**

```json
{
  "footystats": {
    "form": "WWDWL",
    "goals_scored_trend": "Increasing",
    "xg_trend": "2.1 per game",
    "h2h": "3 wins, 1 draw, 1 loss in last 5",
    "injuries": "Pedri (ankle), out 2 weeks",
    "team_news": "Coach confirmed 4-3-3 formation"
  },
  "other_sources": {
    // News articles
    // Betting forums
    // Official team websites
  }
}
```

**Use for Q-scores:**
- Q1: Recent form (as fallback)
- Q6: Formations (news confirmation)
- Q9: Injuries (news updates)
- Q10: H2H (if FBref unavailable)

---

### Tier 3: Manual Data (HIGH RELIABILITY when available)

**Why Tier 3 (but high quality):**
- Limited to specific data points
- Requires manual effort
- But 100% accurate when verified

**What it provides:**

```json
{
  "formations": {
    "home_formation": "4-3-3",
    "away_formation": "3-5-2",
    "source": "manual",
    "verified": true,
    "confidence": 5
  },
  "lineups": {
    "home_lineup": [...],
    "away_lineup": [...],
    "verified_90min_before": true
  }
}
```

**Use for Q-scores:**
- Q6: Formations (when verified before match)
- Q9: Injuries (cross-verification)

---

### Tier 4: Defaults (FALLBACK ONLY)

**Why Tier 4:**
- No real data available
- Use documented formulas from `.claude/q_score_formulas.md`
- Always flag in reasoning

**When to use:**
- All other sources failed
- MUST state "No data available → using default"
- MUST reduce confidence in analysis

---

## 📋 Complete Q-Score Source Matrix

| Q-Score | Primary Source | Secondary Source | Fallback | Quality |
|---------|---------------|------------------|----------|---------|
| **Q1** - Recent Form | SofaScore recent_form | FBref schedule | League position | 5→4→2 |
| **Q2** - Goals Scored | FBref standard.goals | SofaScore goals_for | League average | 5→4→1 |
| **Q3** - Goals Conceded | FBref standard.goals_against | SofaScore goals_against | League average | 5→4→1 |
| **Q4** - xG | FBref standard.xG | FootyStats xG trend | Goals * 0.95 | 5→3→1 |
| **Q5** - Home/Away | FBref schedule (venue) | SofaScore schedule | Overall form | 5→4→2 |
| **Q6** - Formations | Manual verification | News articles | Default 0/0 | 5→3→1 |
| **Q7** - Pressing | FBref defense actions | FootyStats press stats | Default +2 | 5→3→1 |
| **Q8** - Set Pieces | FBref misc (corners+aerials) | FootyStats corners | Default +2 | 5→3→1 |
| **Q9** - Injuries | URL news + FBref playing_time | FootyStats injuries | Assume healthy | 4→3→1 |
| **Q10** - H2H | FBref schedule (opponent) | FootyStats H2H | No adjustment | 5→3→1 |
| **Q11** - Streak | SofaScore recent_form | FBref recent results | No adjustment | 5→4→1 |
| **Q12** - O/U Form | FBref goals trends | FootyStats O/U | League average | 5→3→1 |
| **Q13** - Discipline | FBref misc (cards) | FootyStats discipline | Default 0 | 5→3→1 |
| **Q14** - Player Form | FBref top_players xG | FootyStats key players | Team xG proxy | 5→3→1 |
| **Q15** - Attack vs Def | FBref xG + opponent defense | FootyStats matchup | No adjustment | 5→3→1 |
| **Q16** - Possession | FBref possession + passing | FootyStats possession | League average | 5→3→1 |
| **Q17** - Shot Quality | FBref shooting.SoT% | FootyStats shots | League average | 5→3→1 |
| **Q18** - Conversion | FBref shooting.goals_per_shot | FootyStats conversion | League average | 5→3→1 |
| **Q19** - Clean Sheets | FBref schedule (0 GA matches) | FootyStats clean sheets | League average | 5→3→1 |

---

## 🚨 Anti-Hallucination Checklist

Before submitting each Q-score, verify:

- [ ] Source is explicitly cited
- [ ] Statistic value is from provided data (not invented)
- [ ] If data missing, fallback is documented
- [ ] Reasoning explains the calculation
- [ ] Data quality score is assigned (5/4/3/2/1)

**Example GOOD Q-score:**
```json
{
  "Q7": {
    "home_score": 5,
    "away_score": 3,
    "home_reasoning": "High press: 168.3 defensive actions/game (182 tackles + 143 interceptions from FBref defense stats, 12 matches) → +5",
    "away_reasoning": "Medium press: 142.1 defensive actions/game (156 tackles + 121 interceptions from FBref defense stats, 12 matches) → +3",
    "sources": ["fbref"],
    "data_quality": 5
  }
}
```

**Example BAD Q-score (DO NOT DO THIS):**
```json
{
  "Q7": {
    "home_score": 5,
    "away_score": 3,
    "home_reasoning": "Team is known for high pressing → +5",  // ❌ NO DATA CITED
    "away_reasoning": "Moderate pressing intensity → +3",      // ❌ VAGUE, NO SOURCE
    "sources": ["analyst_judgment"],                           // ❌ NOT A REAL SOURCE
    "data_quality": 3
  }
}
```

---

## 📊 Data Quality Scoring

Assign quality score for each Q-score based on source used:

| Quality | Source Type | Example | Confidence |
|---------|-------------|---------|------------|
| **5** | soccerdata (FBref) | Actual defensive actions from FBref | Very High |
| **4** | soccerdata (SofaScore/FotMob) | Recent form from SofaScore | High |
| **3** | URL extraction (verified) | Stats from FootyStats scraping | Medium |
| **2** | Proxy calculation | Using league position as form proxy | Low |
| **1** | Default fallback | No data → using default +2 | Very Low |

**Overall analysis quality:**
```python
average_quality = sum(all_q_score_qualities) / 19

if average_quality >= 4.0:
    confidence = "Very High"
elif average_quality >= 3.0:
    confidence = "High"
elif average_quality >= 2.0:
    confidence = "Medium"
else:
    confidence = "Low - Missing critical data"
```

---

## 🎯 Summary: Maximize Information, Minimize Hallucination

**DO:**
- ✅ Use soccerdata (FBref) as primary source
- ✅ Fall back to SofaScore/FotMob if FBref missing
- ✅ Use URL extraction for news/injuries/lineups
- ✅ Cite specific statistics with values
- ✅ Document which source you used
- ✅ Assign data quality scores
- ✅ Flag missing data explicitly

**DON'T:**
- ❌ Invent statistics not in the data
- ❌ Use vague terms like "strong attack" without data
- ❌ Assume information not provided
- ❌ Skip citing sources
- ❌ Ignore fallback chains
- ❌ Give high confidence with low-quality data

**Result**: High-conviction analysis based on real data, no hallucination!
