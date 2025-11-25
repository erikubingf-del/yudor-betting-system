# Q-Score Formulas - Yudor v5.3

**Purpose**: Definitive formulas for all 19 Q-scores with FBref integration
**Status**: Living document - improves with data learnings
**Last Updated**: 2025-11-23

---

## 🎯 Scoring Philosophy

**Goal**: Convert raw data into 1-5 scores that predict match outcomes

**Principles**:
1. **Data-driven**: Use real statistics over estimates
2. **Consistent**: Same inputs always produce same scores
3. **Documented**: Every score has clear reasoning
4. **Iterative**: Formulas improve as we learn from results

---

## 📊 Q-Scores with FBref Integration

### Q7: Pressing Intensity (PPDA)

**Data Source**: FBref `read_team_season_stats(stat_type='defense')`

**Formula**:
```python
defensive_actions_per_game = (tackles + interceptions) / matches

if defensive_actions_per_game >= 160:
    score = 5  # High press (Liverpool, Man City level)
elif defensive_actions_per_game >= 140:
    score = 4  # Above average press
elif defensive_actions_per_game >= 120:
    score = 3  # Average press
elif defensive_actions_per_game >= 100:
    score = 2  # Below average
else:
    score = 1  # Low press / deep block

# Opponent adjustment (NEW):
# If opponent is low press (score 1-2), reduce high press advantage
if home_score >= 4 and away_score <= 2:
    home_score -= 1  # Hard to press a team that sits deep
```

**Reasoning Template**:
```
"{team} has {actions} defensive actions/game (FBref) → {press_level} → +{score}"
```

**Confidence**: 5/5 (real data from FBref)

---

### Q8: Set-Piece Quality

**Data Source**: FBref `read_team_season_stats(stat_type='misc')`

**Formula**:
```python
corners_per_game = total_corners / matches
aerials_won_pct = aerials_won_percentage

base_score = 1

# Corners component
if corners_per_game > 6:
    base_score += 2
elif corners_per_game > 4:
    base_score += 1

# Aerial dominance component
if aerials_won_pct > 55:
    base_score += 2
elif aerials_won_pct > 50:
    base_score += 1

score = min(base_score, 5)  # Cap at 5

# Bonus: If both high corners AND high aerials
if corners_per_game > 6 and aerials_won_pct > 55:
    score = 5  # Maximum threat
```

**Reasoning Template**:
```
"{team} creates {corners} corners/game with {aerials}% aerial success (FBref) → +{score}"
```

**Confidence**: 5/5 (real data from FBref)

---

### Q14: Player Form & Individual Quality

**Data Source**: FBref `read_player_season_stats(stat_type='standard')`

**Formula**:
```python
# Get all players for team
team_players = fbref_data[fbref_data['team'] == team_name]

# Calculate median xG for team
median_xg = team_players['xG'].median()

# Count players above median (in form)
in_form_players = team_players[team_players['xG'] > median_xg]
count = len(in_form_players)

# Score based on in-form count
if count >= 4:
    score = 5  # Multiple players firing
elif count == 3:
    score = 4  # Good form depth
elif count == 2:
    score = 3  # Adequate
elif count == 1:
    score = 2  # Relying on one player
else:
    score = 1  # Poor team form

# Star player penalty (NEW):
# If star player (value > €50M or top scorer) has xG < median
star_players = get_star_players(team_players)
for player in star_players:
    if player['xG'] < median_xg:
        score = max(score - 1, 1)  # Key player off form
```

**Reasoning Template**:
```
"{team} has {count} players above median xG (FBref): {top_names} → +{score}"
```

**Confidence**: 5/5 (real per-player data from FBref)

---

### Q6: Tactical Formations ⚠️ Manual Entry Required

**Data Source**: Manual verification (SofaScore/FlashScore 90 min before kickoff)

**Formation Matchup Matrix**:
```python
MATCHUP_SCORES = {
    ('4-3-3', '3-5-2'): (5, 3),  # Width advantage
    ('3-5-2', '4-4-2'): (5, 3),  # Midfield control
    ('4-2-3-1', '4-4-2'): (4, 3),  # Creative advantage
    ('4-3-3', '5-3-2'): (5, 2),  # Attacking vs defensive
    # ... see q6_formation_scoring.py for full matrix
}

# Lookup formation matchup
home_form, away_form = normalize_formations(home, away)
if (home_form, away_form) in MATCHUP_SCORES:
    home_score, away_score = MATCHUP_SCORES[(home_form, away_form)]
elif home_form == away_form:
    home_score, away_score = 0, 0  # Mirror matchup
else:
    home_score, away_score = 2, 2  # Unknown, neutral
```

**Reasoning Template**:
```
"{home_formation} vs {away_formation}: {tactical_reason} → +{score}"
```

**Confidence**: 5/5 (manually verified formations)

---

## 🔄 Q-Scores Using FootyStats (Existing)

### Q1: Recent Form
**Source**: FootyStats form string
**Formula**: Count W/D/L in last 5 games, weight recent higher
**Confidence**: 4/5 (may not reflect latest game)

### Q2: Home/Away Record
**Source**: FootyStats W-D-L splits
**Formula**: Win percentage × goals per game ratio
**Confidence**: 5/5 (full season data)

### Q3: Head-to-Head
**Source**: FootyStats H2H history
**Formula**: Last 5 meetings, recent weighted higher
**Confidence**: 3/5 (sample size small)

### Q4: Goal Scoring Prowess
**Source**: FootyStats goals scored avg
**Formula**: Goals per game percentile
**Confidence**: 5/5 (full season)

### Q5: Defensive Solidity
**Source**: FootyStats goals conceded avg
**Formula**: Inverse of goals conceded per game
**Confidence**: 5/5 (full season)

### Q9-Q13, Q15-Q19
**Source**: FootyStats various metrics
**Formula**: See existing scoring logic
**Confidence**: 3-5/5 depending on metric

---

## 🧮 CS (Confidence Score) Calculation

**Updated Formula** with FBref integration:

```python
# Raw scores (0-100 scale)
raw_casa = sum([Q1-Q19 home scores]) × weight_factor
raw_vis = sum([Q1-Q19 away scores]) × weight_factor

# Quality adjustment (NEW)
fbref_bonus = 0
if Q7_source == 'fbref':
    fbref_bonus += 2  # Higher confidence
if Q8_source == 'fbref':
    fbref_bonus += 1
if Q14_source == 'fbref':
    fbref_bonus += 2

# Apply bonus to stronger team
if raw_casa > raw_vis:
    raw_casa += fbref_bonus
else:
    raw_vis += fbref_bonus

# Final CS
cs_final = max(raw_casa, raw_vis)

# Tier classification
if cs_final >= 70:
    tier = 1  # CORE bet territory
elif cs_final >= 60:
    tier = 2  # EXP bet territory
else:
    tier = 3  # Likely VETO
```

---

## 📈 Continuous Improvement Process

### After Each Match:

```python
# 1. Record actual vs predicted
actual_result = "home_win"  # or "draw" or "away_win"
predicted_favorite = "home" if raw_casa > raw_vis else "away"

# 2. Analyze Q-scores that were wrong
if actual_result != predicted_favorite:
    # Check which Q-scores overestimated favorite
    for q in Q1-Q19:
        if q_score[favorite] >= 4 and actual_performance[q] < expected:
            flag_for_review(q, match_id)

# 3. Update formulas quarterly
# After 50 matches, analyze patterns:
# - Which Q-scores are most predictive?
# - Which need weight adjustments?
# - Which formulas need refinement?
```

### Learning Log Template:

```markdown
## Match: Barcelona vs Athletic Club (22/11/2025)
**Result**: 1-1 Draw
**Prediction**: Barcelona -1.0 (CORE)
**Outcome**: Lost

### Q-Score Analysis:
- Q7 (Pressing): Home +5, Away +3
  → **ISSUE**: High press didn't translate vs compact defense
  → **Action**: Add opponent adjustment to Q7 formula

- Q8 (Set Pieces): Home +4, Away +2
  → **OK**: Barcelona created corners but didn't convert

- Q14 (Player Form): Home +5, Away +2
  → **ISSUE**: In-form players didn't perform
  → **Action**: Consider fatigue factor (3 games in 7 days)

### Formula Updates:
1. Q7: Add deep-block opponent penalty
2. Q14: Add fixture congestion check
```

---

## 🎯 Target Win Rates by Tier

With FBref integration:

**Current** (without FBref):
- Tier 1 (CS ≥ 70): ~55-60% win rate
- Tier 2 (CS 60-69): ~50-55% win rate
- Tier 3 (CS < 60): ~45-50% win rate

**Target** (with FBref):
- Tier 1 (CS ≥ 70): **65-70% win rate** (+10%)
- Tier 2 (CS 60-69): **58-63% win rate** (+8%)
- Tier 3 (CS < 60): **VETO** (don't bet)

**Path to Target**:
1. FBref data improves Q7/Q8/Q14 accuracy
2. Data quality score increases to 85+
3. Formula refinements based on learnings
4. Stricter VETO criteria (avoid Tier 3)

---

## 🔬 Formula Validation

**Every 50 matches, validate**:

```python
# Calculate actual performance vs expected
for q_score in Q1_to_Q19:
    correlation = calculate_correlation(q_score, match_outcomes)
    if correlation < 0.3:
        flag_for_review(q_score)
        suggest_formula_update(q_score)

# Report:
# Q7 (Pressing): 0.62 correlation ✅ Strong predictor
# Q8 (Set Pieces): 0.41 correlation ✅ Moderate predictor
# Q14 (Player Form): 0.58 correlation ✅ Strong predictor
# Q6 (Formations): 0.35 correlation ⚠️ Needs improvement
```

---

**Version**: 2.0 (with FBref integration)
**Next Review**: After 50 matches with new formulas
**Improvement Tracking**: See `.claude/improvements/` folder
