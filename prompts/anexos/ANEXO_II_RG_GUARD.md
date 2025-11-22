# ANEXO II — RG GUARD RISK SIGNALS (v2.2)

## Risk Guard System: 10 Signal Framework

The RG Guard is a risk assessment layer that evaluates 10 independent signals to detect potential "trap games" or high-variance scenarios where the favorite may underperform despite favorable technical/tactical metrics.

---

## EVALUATION SCALE

Each signal is evaluated on a **0.0 to 1.0 scale**:

- **0.0-0.3**: Low risk (green light)
- **0.4-0.6**: Moderate risk (yellow light)
- **0.7-0.9**: High risk (orange light)
- **1.0**: Critical risk (red light)

---

## R-SCORE FORMULA

```
R = 0.20·AMI + 0.12·SPR + 0.08·HDR + 0.10·RZQ + 0.08·DV + 0.15·KIP + 0.10·TCG + 0.05·WP + 0.07·HF5 + 0.05·HH2
```

**Interpretation**:
- **R < 0.15**: Low risk → CORE tier eligible
- **0.15 ≤ R < 0.25**: Moderate risk → EXP tier
- **R ≥ 0.25**: High risk → Consider VETO or FLIP

---

## THE 10 SIGNALS

### 1. AMI (Análise de Mídia/Imprensa) — Weight: 0.20

**What it measures**: Media pressure on the team/manager

**How to evaluate**:
- **0.8-1.0**: Crisis mode
  - Manager under threat ("sack", "fired", "protests")
  - Team under intense criticism
  - Locker room issues reported
- **0.5**: Normal pressure
  - Standard match preview
  - Minor criticism after recent loss
- **0.1**: Stable climate
  - Positive media sentiment
  - Manager secure
  - Team morale high

**Sources**: Local media (Gazzetta, Marca, AS, Bild, L'Équipe), Sports Mole

**Keywords to search**:
- 🚨 High risk: "crisis", "sack", "fired", "protests", "pressure"
- ⚠️ Moderate: "criticism", "disappointing", "concerns"
- ✅ Low risk: "confident", "stable", "optimistic"

**Default if no data**: **0.30**

---

### 2. SPR (Sentimento Público/Redes Sociais) — Weight: 0.12

**What it measures**: Fan sentiment and social media mood

**How to evaluate**:
- **0.8-1.0**: Fan revolt
  - Negative trending hashtags
  - Protests announced
  - Stadium boycott threats
- **0.5**: Normal criticism
  - Mixed reactions after loss
  - Typical fan complaints
- **0.1**: Fan support
  - Positive sentiment
  - Rally behind team messages
  - Sold out stadium

**Sources**: Twitter/X, fan forums, local news

**Keywords to search**:
- 🚨 High risk: "#[team]out", "protest", "boycott"
- ⚠️ Moderate: Criticism without extremes
- ✅ Low risk: "#[team]in", "support", "rally"

**Default if no data**: **0.20**

---

### 3. HDR (Histórico de Desempenho Recente) — Weight: 0.08

**What it measures**: Recent form streak (negative momentum)

**How to evaluate**:
- **0.7-0.9**: Poor streak
  - 3+ games without win
  - 2+ consecutive losses
  - Winless in 5 games
- **0.4**: Mixed form
  - Alternating W/D/L
  - Inconsistent results
- **0.1**: Strong form
  - 3+ consecutive wins
  - 4+ games unbeaten

**Sources**: Flashscore (last 5 results)

**Calculation**:
```
Wins in last 5 = W
HDR = (4 - W) / 4

Examples:
- 0W in 5 → HDR = 1.0
- 1W in 5 → HDR = 0.75
- 2W in 5 → HDR = 0.5
- 3W in 5 → HDR = 0.25
- 4+W in 5 → HDR = 0.0
```

**Default if no data**: **0.20**

---

### 4. RZQ (Risco de "Zona de Conforto") — Weight: 0.10

**What it measures**: Motivation asymmetry between teams

**How to evaluate**:
- **0.8-1.0**: Extreme asymmetry
  - Comfortable mid-table team vs desperate team (relegation/title race)
  - Team already qualified vs team fighting for qualification
- **0.5**: Both have goals
  - Both fighting for same position
  - Both mid-table
- **0.1**: Both desperate
  - Both in title race
  - Both in relegation battle

**Sources**: League table, league context

**Calculation logic**:
```
If one team mid-table (8th-14th) AND other in top 4 or bottom 4:
  RZQ = 0.8

If both mid-table OR both desperate:
  RZQ = 0.1

Else:
  RZQ = 0.4
```

**Default if no data**: **0.40**

---

### 5. DV (Desgaste por Viagem/Calendário) — Weight: 0.08

**What it measures**: Fatigue from travel or fixture congestion

**How to evaluate**:
- **0.7-0.9**: Heavy load
  - Long-distance travel (>1000km)
  - Match 2-3 days ago
  - Midweek European game
- **0.5**: Moderate load
  - Medium travel (500-1000km)
  - Match 4-5 days ago
- **0.1**: Fresh
  - Full week rest (7+ days)
  - No travel
  - Home training week

**Sources**: Fixture calendar, distance calculator

**Calculation**:
```
Base = 0
If travel >1000km: Base += 0.4
If travel 500-1000km: Base += 0.2
If days since last match ≤3: Base += 0.3
If days since last match 4-5: Base += 0.2
If European midweek game: Base += 0.2

DV = min(Base, 0.9)
```

**Default if no data**: **0.25**

---

### 6. KIP (Key Information Path) — Weight: 0.15

**What it measures**: Uncertainty about key lineup information

**How to evaluate**:
- **0.9-1.0**: Major uncertainty
  - Key player injury status unknown ("doubtful")
  - Starting XI completely unconfirmed
  - Late injury news (< 24h before match)
- **0.5**: Normal uncertainty
  - Minor doubts about 1-2 rotation players
  - Expected lineup with 1-2 question marks
- **0.1**: Full clarity
  - Official lineup announced
  - All key players confirmed fit
  - No surprises expected

**Sources**: Sports Mole (team news), official team Twitter, press conferences

**Keywords to search**:
- 🚨 High risk: "doubtful", "late fitness test", "might not start"
- ⚠️ Moderate: "rotation expected", "may rest"
- ✅ Low risk: "confirmed", "fit", "starts"

**Default if no data**: **0.30**

---

### 7. TCG (Troca de Comando/Gestão) — Weight: 0.10

**What it measures**: Manager stability and job security

**How to evaluate**:
- **0.8-1.0**: Manager at risk
  - 3+ consecutive losses
  - Reports of imminent sacking
  - "Next 2 games crucial" headlines
- **0.5**: Normal pressure
  - Recent loss but job secure
  - Mid-season evaluation
- **0.1**: Secure manager
  - Long-term contract
  - Recent success
  - Fan/board support

**Sources**: Local media, transfermarkt manager page

**Keywords to search**:
- 🚨 High risk: "under pressure", "sack", "crisis meeting"
- ⚠️ Moderate: "pressure mounting"
- ✅ Low risk: "backing", "confident", "secure"

**Default if no data**: **0.25**

---

### 8. WP (Weather/Pitch) — Weight: 0.05

**What it measures**: Weather and pitch conditions affecting play style

**How to evaluate**:
- **0.6-0.8**: Adverse conditions
  - Heavy rain forecast
  - Snow/freezing conditions
  - Pitch in poor state (reported)
- **0.3**: Mild conditions
  - Light rain
  - Cold but playable
- **0.1**: Ideal conditions
  - Clear weather
  - Good pitch
  - Favorable temperature

**Sources**: Weather.com, stadium reports, Sports Mole

**Impact consideration**:
- Technical teams more affected by poor conditions
- Physical teams less affected

**Default if no data**: **0.15**

---

### 9. HF5 (Home Form Last 5) — Weight: 0.07

**What it measures**: Home team's recent home form

**How to evaluate** (for home team only):
- **0.9**: 0 home wins in last 5 home games
- **0.6**: 1 home win
- **0.3**: 2 home wins
- **0.1**: 3+ home wins

**Sources**: Flashscore (home/away split)

**Calculation**:
```
Home_Wins_5 = W (at home in last 5 home games)
HF5 = (3 - W) / 3.33

Examples:
- 0W → HF5 = 0.9
- 1W → HF5 = 0.6
- 2W → HF5 = 0.3
- 3+W → HF5 = 0.0
```

**Default if no data**: **0.25**

---

### 10. HH2 (Home H2H Last 2) — Weight: 0.05

**What it measures**: Home team's H2H record at home vs this opponent

**How to evaluate**:
- **0.9**: Away team won last 2 H2H games at this venue
- **0.5**: Split (1-1)
- **0.1**: Home team won both last 2 H2H games at home

**Sources**: Flashscore (H2H tab, filter by venue)

**Calculation**:
```
Home_Wins = Number of wins by home team in last 2 H2H at home
HH2 = (2 - Home_Wins) / 2.22

Examples:
- 0 wins → HH2 = 0.9
- 1 win → HH2 = 0.45
- 2 wins → HH2 = 0.0
```

**Default if no data**: **0.20**

---

## RISK BALANCE RATIO (RBR)

The RBR measures the **risk asymmetry** between favorite and underdog:

```
RBR = (R_fav - R_dog) / (R_fav + R_dog)
```

**Interpretation**:
- **RBR > 0.25**: Favorite has significantly more risk → Consider FLIP
- **RBR ≈ 0**: Balanced risk
- **RBR < -0.25**: Underdog has more risk → Favorite bet more reliable

---

## DECISION LOGIC INTEGRATION

### VETO Trigger
```
If R ≥ 0.25 AND RBR ≤ 0.25:
  Decision = VETO (too risky, no flip opportunity)
```

### FLIP Trigger
```
If R ≥ 0.25 AND RBR > 0.25 AND Edge_underdog ≥ 8%:
  Decision = FLIP (favorite risky, underdog has value)
```

### EXP Trigger
```
If 0.15 ≤ R < 0.25:
  Decision = EXP (moderate risk, experimental tier)
```

### CORE Eligibility
```
If R < 0.15:
  Decision = CORE (low risk, core tier eligible)
```

---

## PRACTICAL EXAMPLES

### Example 1: Low Risk (R = 0.12)
```
AMI: 0.20 (stable media)
SPR: 0.10 (fan support)
HDR: 0.15 (3W in last 5)
RZQ: 0.10 (both desperate)
DV: 0.20 (moderate travel)
KIP: 0.20 (XI confirmed)
TCG: 0.10 (manager secure)
WP: 0.10 (good weather)
HF5: 0.10 (4W at home)
HH2: 0.10 (won last 2 H2H)

R = 0.20(0.20) + 0.12(0.10) + 0.08(0.15) + 0.10(0.10) + 0.08(0.20) + 0.15(0.20) + 0.10(0.10) + 0.05(0.10) + 0.07(0.10) + 0.05(0.10)
R = 0.040 + 0.012 + 0.012 + 0.010 + 0.016 + 0.030 + 0.010 + 0.005 + 0.007 + 0.005
R = 0.147 → CORE tier
```

### Example 2: High Risk (R = 0.28)
```
AMI: 0.80 (manager crisis)
SPR: 0.60 (fan protests)
HDR: 0.50 (mixed form)
RZQ: 0.80 (mid-table vs desperate)
DV: 0.30 (midweek game)
KIP: 0.40 (injury doubts)
TCG: 0.70 (under pressure)
WP: 0.20 (rain)
HF5: 0.60 (1W at home)
HH2: 0.45 (split H2H)

R = 0.20(0.80) + 0.12(0.60) + 0.08(0.50) + 0.10(0.80) + 0.08(0.30) + 0.15(0.40) + 0.10(0.70) + 0.05(0.20) + 0.07(0.60) + 0.05(0.45)
R = 0.160 + 0.072 + 0.040 + 0.080 + 0.024 + 0.060 + 0.070 + 0.010 + 0.042 + 0.023
R = 0.581 → VETO or FLIP consideration
```

---

## DOCUMENTATION REQUIREMENTS

When outputting RG Guard analysis, always include:

1. **All 10 signal values** with sources or "default"
2. **R-Score calculation** (show the math)
3. **RBR calculation** (if applicable)
4. **Risk interpretation** (low/moderate/high)
5. **Decision impact** (CORE/EXP/VETO/FLIP)

**Example output format**:
```markdown
### RG GUARD SIGNALS

| Signal | Value | Source/Reasoning |
|:---|---:|:---|
| AMI | 0.30 | Default - local media not found |
| SPR | 0.50 | Moderate criticism on Twitter after last loss |
| HDR | 0.25 | 3W in last 5 games |
| RZQ | 0.10 | Both teams desperate (title race) |
| DV | 0.40 | 800km travel + match 3 days ago |
| KIP | 0.20 | Sports Mole confirms expected XI |
| TCG | 0.10 | Manager secure, recent extension |
| WP | 0.15 | Default - weather forecast unavailable |
| HF5 | 0.10 | 4W in last 5 home games |
| HH2 | 0.00 | Won both last H2H at home |

**R-Score**: 0.184
**Interpretation**: Moderate risk → EXP tier
**RBR**: -0.08 (underdog slightly more risk) → Favorite bet valid
```

---

*ANEXO II — Yudor System v5.3*
*RG Guard Risk Assessment Framework*
