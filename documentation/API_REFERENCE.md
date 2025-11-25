# YUDOR System - API Reference

Complete reference for all external APIs and integrations used in the YUDOR betting analysis system.

---

## 🔑 Required API Keys

All API keys are stored in `.env` file at project root.

```bash
ANTHROPIC_API_KEY=sk-ant-...
AIRTABLE_API_KEY=pat...
AIRTABLE_BASE_ID=app...
FOOTYSTATS_API_KEY=c715e230a56b394e01389862fd3bb752e3f9d5e174b2ec86de081c6740a2fcd2
```

See [ENVIRONMENT.md](ENVIRONMENT.md) for setup instructions.

---

## 1. Anthropic Claude API

### Purpose
Q1-Q19 analysis, YUDOR decision logic, data consolidation

### Configuration
- **Model:** `claude-sonnet-4-20250514`
- **Max Tokens:** 8000
- **Usage:** LLM prompts for match analysis

### Key Operations
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=8000,
    messages=[{
        "role": "user",
        "content": prompt_text
    }]
)
```

### Rate Limits
- Check Anthropic documentation for current limits
- System implements automatic retries on rate limit errors

### Error Handling
- `APIError`: General API errors
- `RateLimitError`: Rate limit exceeded (automatic retry)

---

## 2. Airtable API

### Purpose
Data storage, match tracking, results recording

### Configuration
- **Base ID:** Stored in `AIRTABLE_BASE_ID`
- **API Key:** Personal Access Token in `AIRTABLE_API_KEY`

### Tables

#### Table 1: Match Analyses
Primary match data and analysis results.

**Fields:**
- `match_id` (text, primary key)
- `date` (date)
- `home_team` (text)
- `away_team` (text)
- `league` (text)
- `analysis_timestamp` (datetime)
- `Yudor AH Fair` (number) - Calculated fair Asian Handicap line
- `Yudor Fair Odds` (number) - Fair odds at that line
- `Yudor AH Team` (text) - Team to bet on
- `Decision` (select): CORE, EXP, FLIP, VETO
- `cs_final` (number) - Confidence score
- `r_score` (number) - Risk score
- `tier` (number) - Match tier (1-3)
- `full_analysis` (long text) - Complete JSON analysis
- `data_quality` (number) - Data quality score (0-100)
- `Q1-Q19 Scores` (long text) - JSON of all Q scores

#### Table 2: Bets Entered
Tracking actual bets placed.

**Fields:**
- `match_id` (link to Match Analyses)
- `entry_timestamp` (datetime)
- `market_ah_line` (number)
- `market_ah_odds` (number)
- `edge_pct` (number) - Calculated edge
- `stake` (number)
- `notes` (long text)

#### Table 3: Results
Match outcomes and P&L.

**Fields:**
- `match_id` (link to Match Analyses)
- `final_score` (text)
- `result` (select): WIN, LOSS, PUSH
- `profit_loss` (number)
- `result_timestamp` (datetime)

### Key Operations

**Create Record:**
```python
from pyairtable import Api

api = Api(os.getenv('AIRTABLE_API_KEY'))
table = api.table(os.getenv('AIRTABLE_BASE_ID'), 'Match Analyses')

record = table.create({
    'match_id': 'TeamAvsTeamB_25112025',
    'date': '2025-11-25',
    'home_team': 'Team A',
    'away_team': 'Team B',
    'Yudor AH Fair': -0.75,
    'Yudor Fair Odds': 2.13,
    'Decision': 'CORE'
})
```

**Read Records:**
```python
# Get all
records = table.all()

# Get specific
record = table.get('rec123abc')

# Query
records = table.all(formula="{Decision}='CORE'")
```

**Update Record:**
```python
table.update('rec123abc', {
    'Yudor Fair Odds': 2.00
})
```

### Rate Limits
- 5 requests per second per base
- System implements automatic delays

---

## 3. FootyStats API

### Purpose
Odds data, team statistics, draw probability

### Configuration
- **API Key:** `c715e230a56b394e01389862fd3bb752e3f9d5e174b2ec86de081c6740a2fcd2`
- **Base URL:** Various endpoints (odds, stats, fixtures)

### Key Endpoints

**Get Match Odds:**
```python
url = f"https://api.footystats.org/league-odds?key={API_KEY}&league={league}"
response = requests.get(url)
odds_data = response.json()
```

**Get Team Stats:**
```python
url = f"https://api.footystats.org/team-stats?key={API_KEY}&team={team_name}"
response = requests.get(url)
stats = response.json()
```

### Data Extracted
- Match odds (home, away, draw)
- xG (expected goals) statistics
- Form data (wins, losses, draws)
- Home/away splits

### Rate Limits
- Check current plan limits
- Free tier: Limited requests per day

---

## 4. FBRef (via soccerdata library)

### Purpose
Team statistics, player values, xG data

### Configuration
- **Library:** `soccerdata` Python package
- **No API key required**

### Usage
```python
import soccerdata as sd

# Get team stats
fbref = sd.FBref(leagues='ENG-Premier League', seasons='2425')
stats = fbref.read_team_season_stats()

# Get player values
tm = sd.Transfermarkt('ENG-Premier League', '2425')
values = tm.read_player_values()
```

### Data Extracted
- Team stats (goals, xG, possession)
- Player market values (Transfermarkt integration)
- Match results
- League tables

### Rate Limits
- Respectful scraping (delays built into library)
- No hard limits

---

## 5. SportsMole (Web Scraping)

### Purpose
Team news, injury reports, match previews

### Configuration
- **URL Database:** `data/urls/team_news_urls_complete.json`
- **Method:** Web scraping with requests/BeautifulSoup

### URL Structure
```json
{
  "Premier League": {
    "Arsenal": "https://www.sportsmole.co.uk/football/arsenal/",
    "Chelsea": "https://www.sportsmole.co.uk/football/chelsea/"
  }
}
```

### Data Extracted
- Injury news
- Team news
- Manager comments
- Match previews

### Implementation
```python
import requests
from bs4 import BeautifulSoup

url = team_urls[league][team]
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract team news sections
team_news = soup.find('div', class_='team-news')
```

### Rate Limits
- 1-2 second delay between requests
- Respectful scraping

---

## 6. SofaScore (Web Scraping)

### Purpose
Formation data, tactical info

### Configuration
- **URL Database:** `data/urls/sofascore_team_urls.json`
- **Method:** Web scraping (Playwright for JavaScript-heavy pages)

### Status
- ⚠️ Partially implemented
- Formation data available but limited

### Implementation
See `scripts/scrapers/formation_scraper_playwright.py`

---

## 🔧 Integration Points

### Data Flow
```
1. FBRef → Team stats, xG, player values
2. FootyStats → Odds, draw probability
3. SportsMole → Injuries, team news
4. SofaScore → Formations (limited)
5. Claude API → Q1-Q19 analysis
6. Airtable → Storage & tracking
```

### Critical Scripts
- `scripts/production/master_orchestrator.py` - Uses all APIs
- `scripts/scrapers/comprehensive_stats_scraper.py` - Data collection
- `scripts/production/recalculate_all_yudor_fair_odds_CORRECT.py` - Airtable integration

---

## 🛡️ Security Best Practices

1. **Never commit `.env` file**
   - Use `.env.example` template only

2. **Rotate API keys regularly**
   - Especially Airtable PATs

3. **Monitor API usage**
   - Check rate limits and costs

4. **Use read-only keys where possible**
   - Minimize permissions

5. **Implement error handling**
   - Graceful degradation on API failures

---

## 📊 API Health Monitoring

Check API status:
```bash
python scripts/development/test_airtable_access.py
python scripts/development/test_fetch.py
```

---

**Last Updated:** 2025-11-25
**Maintained By:** System
