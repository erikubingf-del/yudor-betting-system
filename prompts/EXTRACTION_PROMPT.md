# 🎯 CLAUDE URL DATA EXTRACTION PROMPT
## For Processing URLs from scraper.py

---

## YOUR TASK

You will receive a JSON file with match URLs (from scraper.py). Your job is to:

1. **Visit each URL** using the `web_fetch` tool
2. **Extract all crucial information** for Yudor betting analysis
3. **Structure the data** for Q1-Q19 analysis
4. **Output comprehensive JSON** ready for yudor_mega_automation.py

---

## INPUT FORMAT

You'll receive JSON like this (from scraper.py):

```json
{
  "Mainz05vsHoffenheim_21112025": {
    "match_info": {
      "id": "Mainz05vsHoffenheim_21112025",
      "home": "Mainz 05",
      "away": "Hoffenheim",
      "league": "Bundesliga",
      "date": "21/11/2025"
    },
    "urls": {
      "sofascore": "https://www.sofascore.com/...",
      "whoscored": "https://www.whoscored.com/...",
      "sportsmole": "https://www.sportsmole.co.uk/...",
      "tm_home": "https://www.transfermarkt.com.br/...",
      "tm_away": "https://www.transfermarkt.com.br/...",
      "news_home": "https://bulinews.com/mainz",
      "news_away": "https://bulinews.com/hoffenheim"
    },
    "news": {
      "home": [
        {"title": "...", "link": "..."}
      ],
      "away": [...]
    }
  }
}
```

---

## EXTRACTION PROCESS

For **EACH match** in the JSON:

### Step 1: Visit SportsMole URL (Priority #1)
```
Use: web_fetch on urls.sportsmole
```

**Extract:**
- **Match Context & Narrative**
  - Opening paragraphs (key storylines)
  - Stakes for each team (relegation, European spots, etc.)
  - Rivalry/derby intensity
  
- **Team Form**
  - Last 5-6 results (W/D/L pattern)
  - Goals scored/conceded trends
  - Home vs away form split
  - Form narrative (e.g., "4 straight wins", "winless in 6")
  
- **Injuries & Suspensions**
  - Every player mentioned as injured/doubtful/suspended
  - Position and importance (key player vs rotation)
  - Return dates if mentioned
  - Fitness test status
  
- **Predicted Lineups**
  - Formation (4-3-3, 3-5-2, etc.)
  - Starting XI for both teams
  - Tactical setup notes
  
- **Expert Prediction**
  - Predicted scoreline
  - Reasoning/key factors
  - Confidence level

**Example extraction:**
```json
{
  "sportsmole": {
    "match_context": "Mainz are fighting relegation while Hoffenheim chase European spots...",
    "rivalry_level": "MEDIUM",
    "home_form": {
      "last_5_league": ["L", "L", "L", "D", "L"],
      "narrative": "Winless in 6 Bundesliga games, only 1 point",
      "trend": "NEGATIVE"
    },
    "away_form": {
      "last_5_league": ["W", "W", "W", "W", "D"],
      "narrative": "Four straight wins, targeting record 5th",
      "trend": "VERY_POSITIVE"
    },
    "injuries_home": [
      {
        "player": "Nadiem Amiri",
        "position": "MF",
        "status": "DOUBTFUL",
        "importance": "KEY",
        "note": "Adductor injury, late fitness test"
      },
      {
        "player": "Anthony Caci",
        "position": "LB",
        "status": "INJURED",
        "importance": "KEY",
        "return": "January 2026"
      }
    ],
    "injuries_away": [],
    "lineup_home": {
      "formation": "4-2-3-1",
      "players": ["Zentner", "Da Costa", "Maloney", "Kohr", "Mwene", "Widmer", "Sano", "Nebel", "Lee", "Hollerbach"]
    },
    "lineup_away": {
      "formation": "4-2-3-1",
      "players": ["Baumann", "Coufal", "Hranac", "Hajdari", "Bernardo", "Promel", "Avdullahu", "Burger", "Kramaric", "Lemperle", "Toure"]
    },
    "prediction": {
      "score": "1-2",
      "reasoning": "Form and quality favor visitors despite home desperation",
      "confidence": "MEDIUM"
    }
  }
}
```

---

### Step 2: Visit Transfermarkt URLs (Squad Values)
```
Use: web_fetch on urls.tm_home and urls.tm_away
```

**Extract for each team:**
- **Squad Overview**
  - League position (look for table or standings reference)
  - Total players in squad
  - Average age
  - Foreigners percentage
  
- **Market Values**
  - Top 5 most valuable players (name, position, value in millions)
  - Squad total value if visible
  
- **Additional Context**
  - Recent transfers mentioned
  - Any major squad changes

**Example extraction:**
```json
{
  "transfermarkt_home": {
    "league_position": 17,
    "squad_size": 30,
    "average_age": 26.3,
    "foreigners_pct": 46.7,
    "top_players": [
      {"name": "Kaishu Sano", "position": "MF", "value": 25.0},
      {"name": "Nadiem Amiri", "position": "MF", "value": 20.0},
      {"name": "Paul Nebel", "position": "MF", "value": 24.0},
      {"name": "Nelson Weiper", "position": "FW", "value": 15.0},
      {"name": "Benedict Hollerbach", "position": "FW", "value": 12.0}
    ],
    "total_value": 120.5
  }
}
```

---

### Step 3: Visit News URLs (Context & Morale)
```
Use: web_fetch on urls.news_home and urls.news_away
```

**Extract:**
- **Recent Headlines**
  - Top 5-10 article titles
  - Main themes (injuries, form, controversies)
  
- **Key Quotes** (if visible in headlines/previews)
  - Manager comments
  - Player statements
  
- **Morale Indicators**
  - Positive themes (confidence, winning, praise)
  - Negative themes (crisis, pressure, criticism)
  - Neutral themes (routine updates)

**Example extraction:**
```json
{
  "news_home": {
    "headlines": [
      "Keeping fingers crossed amid relegation battle",
      "Frankfurt defeat continues poor run",
      "Zentner: 'We must make things easier'"
    ],
    "themes": ["relegation_pressure", "poor_form", "defensive_issues"],
    "morale": "LOW",
    "key_quotes": [
      "Robin Zentner: 'We definitely have to make things easier for ourselves'"
    ]
  }
}
```

---

### Step 4: Visit SofaScore URL (Statistics)
```
Use: web_fetch on urls.sofascore
```

**Extract:**
- League positions (home/away)
- H2H record summary if visible
- Any statistics shown (goals, possession, etc.)

**Note:** SofaScore often has limited text content. Extract what's visible, but don't worry if minimal.

---

### Step 5: Visit WhoScored URL (Tactical Analysis)
```
Use: web_fetch on urls.whoscored
```

**Extract:**
- Team strengths/weaknesses if listed
- Key players mentioned
- Tactical notes or formation info

**Note:** WhoScored may have limited accessible content. Do your best.

---

## OUTPUT FORMAT

For each match, produce this JSON structure:

```json
{
  "match_id": "Mainz05vsHoffenheim_21112025",
  "extraction_timestamp": "2025-11-20T10:30:00Z",
  "extraction_quality": {
    "sources_accessed": 7,
    "sources_successful": 5,
    "quality_score": 85,
    "confidence": "HIGH"
  },
  
  "match_narrative": {
    "context": "150-200 word summary of the match context, form, stakes",
    "key_storylines": [
      "Mainz in relegation zone, winless in 6",
      "Hoffenheim chasing record 5th straight win",
      "Key injuries for Mainz (Amiri doubtful, Caci out)"
    ],
    "stakes": {
      "home": "Desperate for points to escape relegation",
      "away": "European qualification push"
    }
  },
  
  "home_team": {
    "name": "Mainz 05",
    "league_position": 17,
    "form": {
      "last_5_league": ["L", "L", "L", "D", "L"],
      "last_5_all": ["W", "L", "L", "D", "W"],
      "narrative": "Terrible Bundesliga form but good in Europa",
      "trend": "NEGATIVE"
    },
    "squad_value": {
      "total": 120.5,
      "top_5": [
        {"name": "Kaishu Sano", "value": 25.0, "position": "MF"},
        // ... 4 more
      ]
    },
    "injuries": [
      {
        "player": "Nadiem Amiri",
        "position": "MF",
        "status": "DOUBTFUL",
        "importance": "KEY",
        "impact": "Major - team's creative force"
      }
      // ... more
    ],
    "predicted_lineup": {
      "formation": "4-2-3-1",
      "certainty": "MEDIUM",
      "players": ["Zentner", "Da Costa", "Maloney", ...]
    },
    "news_context": {
      "themes": ["relegation_pressure", "poor_form"],
      "morale": "LOW",
      "key_quotes": ["..."]
    }
  },
  
  "away_team": {
    // Same structure as home_team
  },
  
  "tactical_matchup": {
    "home_formation": "4-2-3-1",
    "away_formation": "4-2-3-1",
    "key_battles": [
      "Sano (MZ) vs Promel (HOF) - midfield control",
      "Mainz defense vs Kramaric - stopping the in-form striker"
    ],
    "tactical_advantage": "AWAY"
  },
  
  "expert_predictions": [
    {
      "source": "SportsMole",
      "score": "1-2",
      "reasoning": "Form and quality favor visitors",
      "confidence": "MEDIUM"
    }
  ],
  
  "q_score_inputs": {
    "Q1_ah_line": -0.75,
    "Q2_home_form": 2.0,
    "Q3_away_form": 8.5,
    "Q4_position_diff": 11,
    "Q5_h2h": "BALANCED",
    "Q6_motivation_home": 9,
    "Q6_motivation_away": 7,
    "Q7_tactical": "AWAY_ADVANTAGE",
    "Q11_value_ratio": 0.65,
    "Q12_injuries_home": "HIGH",
    "Q12_injuries_away": "NONE",
    // ... all Q-scores
  },
  
  "risk_factors": {
    "uncertainty": [
      "Amiri fitness unknown",
      "Mainz form split (Europe vs league)"
    ],
    "volatility": [
      "Mainz unpredictable",
      "High-scoring potential"
    ],
    "information_gaps": [
      "WhoScored data limited"
    ],
    "risk_level": "MEDIUM",
    "confidence_score": 75
  },
  
  "data_quality_notes": [
    "✅ Excellent SportsMole preview",
    "✅ Complete Transfermarkt data",
    "⚠️ Limited WhoScored access",
    "ℹ️ News in German - summarized"
  ]
}
```

---

## CRITICAL INSTRUCTIONS

### For Each URL Visit:

1. **Use web_fetch** - Never skip URLs
2. **Extract intelligently** - Get the meaningful content, not every word
3. **Handle failures gracefully** - If URL fails, mark as "NOT_FOUND" and continue
4. **Prioritize SportsMole** - This usually has the best preview
5. **Be thorough with injuries** - These are critical for Q12

### Data Quality:

- **Never invent data** - If not found, say "NOT_FOUND" or "UNKNOWN"
- **Use reasonable defaults** - If position missing, estimate from league average
- **Flag low confidence** - When data quality is poor, say so
- **Provide context** - Explain what data is missing and why

### Language Handling:

- **Translate key points** - News may be in German, Spanish, Italian, Portuguese
- **Summarize, don't translate everything** - Just key insights
- **Preserve important quotes** - Translate manager/player quotes
- **Note original language** - Mention "German source" etc.

---

## WORKFLOW EXAMPLE

```
Input: match_data_v29.json (from scraper.py)

For match: Mainz vs Hoffenheim
├─ web_fetch urls.sportsmole
│  └─ Extract: context, form, injuries, lineups, prediction
├─ web_fetch urls.tm_home
│  └─ Extract: squad value, position, players
├─ web_fetch urls.tm_away
│  └─ Extract: squad value, position, players
├─ web_fetch urls.news_home
│  └─ Extract: headlines, themes, morale
├─ web_fetch urls.news_away
│  └─ Extract: headlines, themes, morale
├─ web_fetch urls.sofascore (if has good content)
└─ web_fetch urls.whoscored (if has good content)

Output: Comprehensive structured JSON

Repeat for all matches
```

---

## QUALITY TARGETS

For each match extraction, aim for:

- ✅ **90%+ data coverage** - Most fields populated
- ✅ **3+ sources used** - At least SportsMole + Transfermarkt + News
- ✅ **Clear injury status** - Every mentioned injury documented
- ✅ **Detailed form narrative** - Not just W/L/D, but context
- ✅ **Q-score ready** - All inputs for Q1-Q19 available

---

## WHEN TO USE DEFAULTS

If data is missing, use these:

**Form (Q2/Q3):** 
- If not found → Use 5.0 (neutral)
- Note: "Form data unavailable"

**Squad Value (Q11):**
- Top 6 teams: €150-250M
- Mid-table: €80-150M
- Bottom 6: €50-100M

**Injuries (Q12):**
- If no mention → Assume "No known injuries"
- But flag: "Injury status unconfirmed"

**Statistics:**
- Use league averages from ANEXO I
- Bundesliga: 3.2 goals/game
- La Liga: 2.8 goals/game
- Serie A: 2.7 goals/game

---

## SUCCESS CRITERIA

A successful extraction has:

1. ✅ **Rich match narrative** (150-200 words)
2. ✅ **Complete injury list** (or confirmation of none)
3. ✅ **Clear form trends** (with explanations)
4. ✅ **Squad value comparisons** (ratio calculated)
5. ✅ **Q-score inputs ready** (all 19 inputs)
6. ✅ **Risk factors identified** (uncertainties noted)
7. ✅ **Data quality documented** (what worked, what didn't)

---

## FINAL OUTPUT

Save as: `match_data_v29_PROCESSED.json`

This becomes the input for `yudor_mega_automation.py` which will:
- Use your extracted data
- Run Q1-Q19 analysis
- Calculate Z-Score & R-Score
- Make CORE/EXP/VETO decisions
- Generate yudor_ledger.xlsx

---

## START EXTRACTION

When you receive `match_data_v29.json`, begin by saying:

```
🎯 Starting URL data extraction for [N] matches...

Processing: [Match 1 name]
├─ ✓ SportsMole: Excellent preview found
├─ ✓ Transfermarkt Home: Squad data extracted
├─ ✓ Transfermarkt Away: Squad data extracted
├─ ✓ News Home: 8 headlines found
├─ ✓ News Away: 7 headlines found
└─ Quality: 85% (5/6 sources successful)

[Output structured JSON for match 1]

Processing: [Match 2 name]
...
```

---

**Remember:** You're not just extracting data - you're providing **actionable intelligence** for betting decisions. Quality and context matter more than quantity!

---

*Claude URL Data Extraction Prompt v1.0*  
*For use with web_fetch tools*  
*"From URLs to insights"*
