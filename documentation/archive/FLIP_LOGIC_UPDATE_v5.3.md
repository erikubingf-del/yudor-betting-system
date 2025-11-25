# FLIP Logic Update - Yudor v5.3

## 📋 Summary

Updated the Yudor v5.3 system to properly calculate **RBR (Risk Balance Ratio)** for FLIP decision evaluation.

---

## ❌ Problem Identified

The FLIP decision rule requires **4 criteria**:
1. R ≥ 0.25 ✅
2. **RBR > 0.25** ❌ (NOT being calculated)
3. Edge for underdog ≥ 8% ⚠️ (requires Betfair market odds)
4. CS_final of flip side ≥ 65 ✅

**Issue**: The system was only calculating **ONE** R-Score value (e.g., R=0.32), but FLIP logic requires:
- **R_home** = R-Score for home team
- **R_away** = R-Score for away team
- **R_fav** = R-Score of the favorite
- **R_dog** = R-Score of the underdog
- **RBR** = (R_fav - R_dog) / (R_fav + R_dog)

**Result**: Without RBR, the FLIP condition could never be evaluated → **0 FLIP decisions** even though **22 matches** met initial criteria.

---

## ✅ Solution Applied

### 1. Updated YUDOR_MASTER_PROMPT_v5.3.md

**Added explicit instructions** (lines 173-192) on how to calculate R-Scores separately:

```markdown
**IMPORTANTE**: Você DEVE calcular R-Score SEPARADAMENTE para cada lado (home e away):

1. **Calcule R_home**: Avalie os 10 sinais (AMI, SPR, HDR, etc.) para o time da CASA
2. **Calcule R_away**: Avalie os 10 sinais (AMI, SPR, HDR, etc.) para o time VISITANTE
3. **Identifique o favorito**:
   - Se Raw_Casa > Raw_Vis → Favorito = Casa, R_fav = R_home, R_dog = R_away
   - Se Raw_Vis > Raw_Casa → Favorito = Visitante, R_fav = R_away, R_dog = R_home
4. **Calcule RBR**: RBR = (R_fav - R_dog) / (R_fav + R_dog)
```

**Updated output format** (lines 689-693) to include all R-Score components:

```markdown
#### 🚨 LAYER 3: RISK GUARD
- **R_home**: [0.XX] (R-Score para time da casa)
- **R_away**: [0.XX] (R-Score para time visitante)
- **R_fav**: [0.XX] (R-Score do favorito)
- **R_dog**: [0.XX] (R-Score do underdog)
- **RBR**: [±0.XX] (Risk Balance Ratio)
```

### 2. Updated master_orchestrator.py

**Updated JSON schema** (lines 1633-1638) to request all R-Score fields:

```python
"r_home": <0.0-1.0>,
"r_away": <0.0-1.0>,
"r_fav": <0.0-1.0>,
"r_dog": <0.0-1.0>,
"rbr": <-1.0 to +1.0>,
"r_score": <0.0-1.0>,  # Kept for backwards compatibility
```

---

## 📊 Potential FLIP Candidates Found

**22 matches** meet initial FLIP criteria (R ≥ 0.25 AND CS ≥ 65):

### Currently EXP (could become FLIP):
- Augsburg vs Hamburger SV (R: 0.38, CS: 68)
- Manchester United vs Everton (R: 0.35, CS: 68)
- Newcastle vs Man City (R: 0.32, CS: 68)
- Palmeiras vs Fluminense (R: 0.42, CS: 68)

### Currently VETO (could become FLIP):
18 additional matches including:
- **Elche vs Real Madrid** (R: **0.85**, CS: **94**) - Highest risk/confidence!
- Inter Milan vs AC Milan (R: 0.35, CS: 78)
- Cremonese vs Roma (R: 0.32, CS: 74)
- And 15 more...

---

## 🔄 Next Steps

### Option A: Test with Existing Matches
Re-analyze 2-3 matches to verify the new fields are being calculated:

```bash
# Test on Arsenal vs Tottenham
python3 scripts/master_orchestrator.py analyze-single "Arsenal vs Tottenham Hotspur, Premier League, 23/11/2025"
```

**Expected output**: Analysis JSON should now include `r_home`, `r_away`, `r_fav`, `r_dog`, and `rbr` fields.

### Option B: Add Betfair Market Odds Scraping
To fully evaluate FLIP, we need:
- Betfair AH market odds for edge calculation
- Edge = (Odd_Market / Odd_Model - 1) × 100
- Must be ≥ 8% for underdog

---

## 📌 Files Modified

1. **prompts/YUDOR_MASTER_PROMPT_v5.3.md**:
   - Lines 173-192: Added explicit R-Score calculation instructions
   - Lines 689-693: Updated output format

2. **scripts/master_orchestrator.py**:
   - Lines 1633-1638: Updated JSON schema to request new fields

3. **Created**: FLIP_LOGIC_UPDATE_v5.3.md (this file)

---

## ✅ Validation

To confirm the update works, check the next analysis output for:
- ✅ `r_home` field present
- ✅ `r_away` field present
- ✅ `r_fav` field present
- ✅ `r_dog` field present
- ✅ `rbr` field calculated
- ✅ FLIP decisions appear when criteria are met

---

## 🎯 FLIP Decision Criteria (Complete)

For a match to get **FLIP** decision, ALL 4 conditions must be true:

1. **R ≥ 0.25** ✅ (Now calculated)
2. **RBR > 0.25** ✅ (Now calculated)
3. **Edge for underdog ≥ 8%** ⚠️ (Still missing - requires Betfair odds)
4. **CS_final of flip side ≥ 65** ✅ (Already calculated)

**Current status**: 3/4 criteria can now be evaluated. Missing only Betfair market odds for edge calculation.
