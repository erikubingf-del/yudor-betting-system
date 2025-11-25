# Data Gaps & System Improvements Analysis

**Date**: November 21, 2025
**Current System**: Yudor v5.3
**Current Data Quality**: 76.3 average (Target: ≥85)
**Goal**: Achieve 60-65%+ win rate through data-driven improvements

---

## 📊 Current Data Analysis

### ✅ What We Have (Strong Foundation)
1. **Player Values** (Q1): Transfermarkt data - 100% coverage
2. **xG/xGA Data** (Q2, Q4, Q13): FootyStats API - Complete
3. **Injury Data** (Q15, Q16): SportsMole + Local News - Good coverage
4. **Form Data** (Q11, Q17): FootyStats - Complete
5. **H2H History** (Q18, Q19): SportsMole - Complete
6. **League Position** (Q9): FootyStats - Complete
7. **Local News**: 90%+ match coverage - Excellent

---

## ❌ Critical Data Gaps (Fixing These = +5-10% Win Rate)

### 1. **Tactical Formations** (Q6) - ⚠️ CRITICAL GAP
**Current**: 0/0 default (missing 100%)
**Impact**: Missing 10-15% edge on tactical mismatches
**Solution**: Add formation scraper

**Sources to Add**:
- **SofaScore API**: Real-time lineups + formations (paid)
- **FotMob**: Free formations data
- **Flashscore**: Lineups 1-2 hours before kickoff
- **FootyStats Formations**: Available in premium tier

**Implementation**:
```python
# Add to scraper.py
def scrape_formations(match_url):
    """
    Priority order:
    1. SofaScore API (most reliable)
    2. FotMob (free backup)
    3. Flashscore scraper
    """
    # Returns: {"home_formation": "4-3-3", "away_formation": "3-5-2"}
```

**Q6 Scoring Logic Improvement**:
- 4-3-3 vs 3-5-2: +5 home (width advantage)
- 3-5-2 vs 4-4-2: +4 away (midfield control)
- Mismatches: ±5 to ±8 points
- Same formation: 0/0

**Expected Impact**: +3-4% win rate

---

### 2. **Pressing Intensity** (Q7) - ⚠️ MAJOR GAP
**Current**: Default +2/+2 (missing 100%)
**Impact**: Missing 5-10% edge on tired/pressing-vulnerable teams
**Solution**: Add PPDA (Passes Allowed Per Defensive Action)

**Sources to Add**:
- **FBref**: Free PPDA stats (pressing intensity)
- **Understat**: xG + PPDA data
- **WhoScored**: Defensive actions per game

**Q7 Scoring Logic**:
- PPDA < 9: High press → +6 (forces errors)
- PPDA 9-12: Medium press → +3
- PPDA > 12: Low press → +1
- **Opponent tired** (midweek game): +3 bonus to pressing team

**Expected Impact**: +2-3% win rate

---

### 3. **Set-Piece Quality** (Q8) - MODERATE GAP
**Current**: Default +2/+2 (80% estimated)
**Impact**: 15-20% of goals come from set pieces
**Solution**: Scrape set-piece conversion rates

**Sources to Add**:
- **FBref**: Set-piece goals/attempts
- **Transfermarkt**: Corner/FK conversion %
- **FootyStats Premium**: Set-piece stats

**Q8 Scoring Logic**:
- Goals from set pieces > 25%: +5
- 15-25%: +3
- < 15%: +1
- **Tall team** (avg height > 185cm): +2 bonus

**Expected Impact**: +1-2% win rate

---

### 4. **Player Ratings/Form** (Q14) - ⚠️ MAJOR GAP
**Current**: Estimated from xG (60% estimated)
**Impact**: Missing recent individual form changes
**Solution**: Add player ratings from last 3 games

**Sources to Add**:
- **WhoScored**: Player ratings (7.0+ = good form)
- **SofaScore**: Player ratings + momentum
- **FotMob**: Individual performance scores

**Q14 Scoring Logic**:
- 3+ players rated 7.5+ in last 3 games: +5
- 2 players rated 7.5+: +3
- 1-0 players rated 7.5+: +1
- **Star player** (€20M+) in bad form (<6.5): -4 penalty

**Expected Impact**: +3-4% win rate

---

### 5. **Betfair Odds** (P_Empate, Market AH) - CRITICAL FOR FLIP
**Current**: N/A for all matches (missing 100%)
**Impact**: Cannot validate edge, FLIP logic uses synthetic edge only
**Solution**: Add Betfair/Pinnacle scraper

**Sources to Add**:
- **Betfair API**: Draw odds, AH lines
- **Pinnacle API**: Sharp market reference
- **Odds Portal**: Historical odds aggregator

**Why Critical**:
1. **Validate Edge**: Compare Yudor AH vs Market AH
2. **FLIP Logic**: Real edge > 8% (not synthetic)
3. **Market Sentiment**: If Market AH = Yudor AH → high confidence
4. **Closing Line Value**: Track if we beat closing odds

**Implementation Priority**: HIGH (needed for accurate edge calculation)

**Expected Impact**: +4-5% win rate (better bet selection)

---

### 6. **Manager Matchup History** (Q5 Enhancement)
**Current**: Manager experience only
**Impact**: Missing tactical familiarity
**Solution**: Add H2H manager record

**Data to Add**:
- Manager A vs Manager B: Win %
- Tactical style: Possession vs Counter
- Average goals in matchups

**Q5 Enhancement**:
- Manager won 3+ of last 5 H2H: +3 bonus
- Known tactical counter: +4
- First-time matchup: 0 (use experience only)

**Expected Impact**: +1-2% win rate

---

### 7. **Referee Impact** - NEW Q-SCORE (Q20)
**Current**: Not tracked
**Impact**: 10-15% variance in cards/penalties
**Solution**: Add referee analysis

**Sources to Add**:
- **Transfermarkt**: Referee stats (cards/game, penalties)
- **WorldFootball**: Referee historical data
- **Sofascore**: Referee strictness rating

**Q20 Scoring Logic** (NEW):
- **Strict referee** (3.5+ yellow/game):
  - Disciplined team: +3
  - Aggressive team: -3
- **Lenient referee** (<2.5 yellow/game):
  - Physical team: +4
  - Soft team: -2
- **Home bias** (home team gets 30%+ fewer cards): +5 home

**Expected Impact**: +2-3% win rate

---

### 8. **Weather Conditions** - NEW Q-SCORE (Q21)
**Current**: Not tracked
**Impact**: Heavy rain/wind affects 5-10% of games significantly
**Solution**: Add weather API

**Sources to Add**:
- **OpenWeather API**: Free weather forecasts
- **Weather Underground**: Stadium-specific
- **Visual Crossing**: Historical + forecast

**Q21 Scoring Logic** (NEW):
- **Heavy rain** (>10mm):
  - Strong aerial team: +4
  - Technical possession team: -4
- **Strong wind** (>25 km/h):
  - Long-ball team: +3
  - Short-passing team: -3
- **Extreme cold** (<5°C):
  - Northern/cold-weather team: +3
  - Southern team: -2

**Expected Impact**: +1-2% win rate (selective application)

---

## 🎯 Priority Implementation Roadmap

### Phase 1: Critical Gaps (Target: +10% Win Rate)
**Timeline**: 2-3 weeks

1. **Betfair/Pinnacle Odds API** (Week 1)
   - Add odds scraper
   - Validate edge calculations
   - Update FLIP logic with real odds
   - **Impact**: +4-5%

2. **Formations Scraper** (Week 1-2)
   - SofaScore API integration
   - FotMob backup scraper
   - Q6 scoring update
   - **Impact**: +3-4%

3. **Player Ratings** (Week 2)
   - WhoScored scraper
   - Q14 scoring update
   - **Impact**: +3-4%

**Total Phase 1 Impact**: +10-13% win rate improvement

---

### Phase 2: Major Enhancements (Target: +5% Win Rate)
**Timeline**: 3-4 weeks

4. **Pressing Intensity (PPDA)** (Week 3)
   - FBref scraper
   - Q7 scoring update
   - Fatigue factor integration
   - **Impact**: +2-3%

5. **Set-Piece Quality** (Week 3-4)
   - FBref set-piece stats
   - Q8 scoring update
   - **Impact**: +1-2%

6. **Referee Analysis (Q20)** (Week 4)
   - Transfermarkt referee scraper
   - New Q-score implementation
   - **Impact**: +2-3%

**Total Phase 2 Impact**: +5-8% win rate improvement

---

### Phase 3: Advanced Features (Target: +3% Win Rate)
**Timeline**: 4-6 weeks

7. **Weather Conditions (Q21)** (Week 5)
   - OpenWeather API integration
   - New Q-score implementation
   - **Impact**: +1-2%

8. **Manager Matchup H2H** (Week 6)
   - Q5 enhancement
   - **Impact**: +1-2%

**Total Phase 3 Impact**: +2-4% win rate improvement

---

## 📈 Expected Cumulative Impact

| Phase | Timeline | Win Rate Gain | Cumulative Win Rate |
|-------|----------|---------------|---------------------|
| Baseline | Current | - | 55% |
| Phase 1 | Week 3 | +10-13% | 65-68% |
| Phase 2 | Week 7 | +5-8% | 70-76% |
| Phase 3 | Week 12 | +2-4% | 72-80% |

**Realistic Target**: 65-70% win rate after Phase 1+2 implementation

---

## 🔧 Technical Implementation Priorities

### Immediate (This Week):
1. **Betfair API Account** - Sign up for Betfair API access
2. **SofaScore API** - Get API key (paid, worth it)
3. **WhoScored Scraper** - Build player ratings scraper

### Short-Term (Weeks 2-4):
4. **FBref Integration** - PPDA + set-piece stats
5. **Referee Database** - Build historical referee stats
6. **Formation Logic** - Implement tactical mismatch scoring

### Medium-Term (Weeks 5-8):
7. **Weather API** - OpenWeather integration
8. **Manager H2H** - Database of manager matchups
9. **ML Recalibration** - After 100+ matches with new data

---

## 🎓 Data Quality Standards (NEW)

### Target Data Quality Score: 85+

**Minimum Requirements for CORE Bets**:
- Formations available: YES (Q6)
- Player ratings: YES (Q14)
- Betfair odds: YES (market validation)
- xG data: YES (Q2, Q4, Q13)
- Injury data: YES (Q15, Q16)

**Minimum Requirements for EXP Bets**:
- xG data: YES
- Injury data: YES
- Form data: YES

**Auto-VETO if**:
- Data quality < 70
- Missing 3+ critical Q-scores
- Betfair edge < 0% (market disagrees)

---

## 🚨 Critical Success Factors

### 1. **Data Consistency**
- Same sources for all matches
- No missing games due to scraping failures
- Automated retries for failed scrapes

### 2. **Real-Time Updates**
- Lineups updated 1-2 hours before kickoff
- Injury news tracked until lineups confirmed
- Weather checked day-of-match

### 3. **Edge Validation**
- Always compare Yudor AH vs Market AH
- Only bet when edge > 5% (conservative)
- Track closing line value (CLV)

### 4. **Continuous Learning**
- ML recalibration after every 100 matches
- Q-score weight adjustments based on loss analysis
- Remove underperforming Q-scores

---

## 💡 Additional Recommendations

### A. **Add Confidence Intervals**
Currently: CS = 78 (point estimate)
Improved: CS = 78 ± 5 (confidence interval)

**Implementation**:
- Bootstrap Q-scores 1000x
- Calculate 95% confidence interval
- Only bet if lower bound CS > 70

**Impact**: Reduces false positives, +2-3% win rate

---

### B. **Add Lineup Confirmation Check**
Currently: Bet placed before lineups
Improved: Re-analyze after lineups confirmed

**Implementation**:
- Get lineups 1 hour before kickoff
- Re-run Q1, Q15, Q16 with actual lineup
- Cancel bet if CS drops > 10 points

**Impact**: Prevents bad bets on surprise rotations, +3-4% win rate

---

### C. **Track Bet Timing**
Currently: No timing tracking
Improved: Track when bet was placed vs kickoff

**Data to Add**:
- Time bet was placed
- Time lineups were confirmed
- Odds movement from bet placement to kickoff

**Insight**: Discover optimal betting window (e.g., 4-6 hours before kickoff)

---

### D. **Add Closing Line Value (CLV) Tracking**
Currently: Not tracked
Improved: Compare bet odds vs closing odds

**Implementation**:
- Save odds when bet placed
- Scrape closing odds (5 min before kickoff)
- Calculate CLV = (Our Odds - Closing Odds) / Closing Odds

**Why Important**:
- Positive CLV = beating the market (long-term profitable)
- Negative CLV = market moved against us (re-evaluate)
- Target: 60%+ bets with positive CLV

**Impact**: Validates system quality, guides improvements

---

## 📝 Summary: Top 5 Priorities

1. **Betfair/Pinnacle Odds API** → Validate edge, improve FLIP (+4-5%)
2. **Formation Scraper (SofaScore)** → Tactical edge (+3-4%)
3. **Player Ratings (WhoScored)** → Recent form (+3-4%)
4. **PPDA/Pressing Stats (FBref)** → Tactical intensity (+2-3%)
5. **Lineup Confirmation Check** → Avoid rotation surprises (+3-4%)

**Total Potential Impact**: +15-20% win rate improvement

**Realistic Target After Phase 1**: 65-68% win rate (from 55%)

---

**Next Steps**:
1. Sign up for Betfair API (£299/year) ← Worth it
2. Get SofaScore API key (€99/month) ← Critical
3. Build WhoScored scraper (free but needs maintenance)
4. Implement Phase 1 over next 2-3 weeks
5. Test on 50 matches before going live
