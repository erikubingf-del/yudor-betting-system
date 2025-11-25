# YUDOR System Documentation

Welcome to the YUDOR (Yield Under Diversified Odds Reasoning) betting analysis system documentation.

## 📚 Documentation Structure

### For First-Time Users
Start here to understand the system:

1. **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** ⭐ START HERE
   - System philosophy and goals
   - Mathematical foundations
   - Architecture overview
   - Q1-Q19 scoring system
   - Decision logic (CORE, EXP, FLIP, VETO)
   - Operational rules and best practices

### For Developers & AI Agents

2. **[SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md)**
   - Complete script catalog
   - Usage examples
   - Dependencies
   - Common workflows

### Additional Resources

3. **Root Directory Documents:**
   - [YUDOR_FAIR_ODDS_EXPLANATION.md](../YUDOR_FAIR_ODDS_EXPLANATION.md) - Deep dive into odds math
   - [FINAL_AIRTABLE_CORRECTION.md](../FINAL_AIRTABLE_CORRECTION.md) - Recent bug fixes explained
   - [AIRTABLE_RECALCULATION_COMPLETE.md](../AIRTABLE_RECALCULATION_COMPLETE.md) - Recalculation summary

---

## 🚀 Quick Start

### Analyzing a New Match

```bash
# Step 1: Run analysis
python3 scripts/master_orchestrator.py analyze-fbref "Team A vs Team B, League, DD/MM/YYYY"

# Step 2: Check results in Airtable
# Look for: Yudor AH Fair, Fair Odds, Decision

# Step 3: If odds seem incorrect
python3 scripts/recalculate_all_yudor_fair_odds_CORRECT.py
```

### Validating the System

```bash
# Check Airtable schema
python3 scripts/validate_airtable_schema.py

# Recalculate all fair odds
python3 scripts/recalculate_all_yudor_fair_odds_CORRECT.py
```

---

## 📊 System Status (as of 2025-11-25)

### ✅ Working Components
- Fair odds calculation (correct methodology implemented)
- FLIP scenario detection and preservation
- Airtable integration
- Q1-Q19 scoring system
- Probability normalization

### 🔄 Recent Fixes
- **2025-11-25:** Fixed AH -0.25 missing from search (Inter Milan bug)
- **2025-11-25:** FLIP scenarios now preserved (FC Köln)
- **2025-11-25:** Correct probability normalization implemented

### 🎯 Current Focus
- Documentation improvement
- System validation
- Edge case testing

---

## 🧮 Key Concepts

### The Fair Odds Formula

```python
# 1. Normalize probabilities to 100%
normalized_prob = raw_score + (100 - total_sum) / 2

# 2. Calculate moneyline odds
moneyline = 100 / favorite_probability

# 3. Find AH line closest to 2.0
# Scale by ±15% per 0.25 step
odds_at_ah = moneyline × (0.85 or 1.15) ^ steps
```

### Decision Types

| Type | Meaning | Action |
|------|---------|--------|
| **CORE** | High confidence | Bet on favorite (negative AH) |
| **EXP** | Experimental | Bet cautiously on favorite |
| **FLIP** | Risk detected | Bet on underdog (positive AH) |
| **VETO** | Don't bet | Skip this match |

---

## 🎓 Learning Path

### For Beginners
1. Read [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) sections 1-3
2. Understand probability normalization (section 2.1)
3. Learn fair odds calculation (section 2.2)
4. Study one example match (section 9)

### For Developers
1. Complete beginner path
2. Read [SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md)
3. Study `recalculate_all_yudor_fair_odds_CORRECT.py`
4. Review [YUDOR_FAIR_ODDS_EXPLANATION.md](../YUDOR_FAIR_ODDS_EXPLANATION.md)

### For AI Agents
1. Read [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) section 10 ("For AI Agents")
2. Study section 7 ("Critical Operational Rules")
3. Review recent bug fixes in [FINAL_AIRTABLE_CORRECTION.md](../FINAL_AIRTABLE_CORRECTION.md)
4. Check section 12 ("Quick Reference") for formulas

---

## 🔗 External Resources

### Data Sources
- **FBRef:** Team stats, xG, player values
- **FootyStats:** Form, rankings, odds
- **Transfermarkt:** Player market values
- **SportsMole:** Team news, previews

### Tools Used
- **Python 3.x:** Core language
- **Airtable API:** Data storage
- **LLM (Claude/GPT):** Q1-Q19 analysis
- **soccerdata library:** FBRef scraping

---

## 🐛 Troubleshooting

### Common Issues

**Problem:** Fair odds don't match expected values
**Solution:** Run `recalculate_all_yudor_fair_odds_CORRECT.py`

**Problem:** FLIP scenario shows negative AH
**Solution:** Check if archived data has FLIP decision, script should preserve it

**Problem:** Probabilities don't sum to 100%
**Solution:** Verify normalization logic distributes difference equally

**Problem:** Missing AH -0.25 optimal line
**Solution:** This was fixed 2025-11-25, pull latest code

---

## 📝 Contributing

### Before Making Changes
1. Read relevant documentation
2. Test on sample data first
3. Keep backups of working code
4. Update documentation

### When Adding Features
1. Follow existing code style
2. Add docstrings
3. Update [SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md)
4. Test thoroughly

### When Fixing Bugs
1. Document the bug in code comments
2. Add example in documentation
3. Create test case if possible
4. Update [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) if it affects methodology

---

## 📞 Support

For questions or issues:
1. Check documentation first
2. Review recent changes in root directory `.md` files
3. Look for similar issues in past fixes
4. Create detailed issue report with:
   - What you tried
   - Expected vs actual results
   - Relevant code/data excerpts

---

## 📜 Document History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-25 | Created comprehensive documentation structure | Claude |
| 2025-11-25 | Added SYSTEM_OVERVIEW.md | Claude |
| 2025-11-25 | Added SCRIPTS_REFERENCE.md | Claude |

---

**Last Updated:** 2025-11-25
**Version:** 1.0.0
**Status:** Production Documentation
