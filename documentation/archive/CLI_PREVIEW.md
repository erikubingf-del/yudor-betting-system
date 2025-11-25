# Yudor v5.3 - Unified CLI Preview

## 🚀 Launch Command

```bash
python3 yudor.py
```

---

## 📺 Menu Interface

```
================================================================================
⚽ YUDOR v5.3 - BETTING SYSTEM
================================================================================

📋 MAIN MENU
--------------------------------------------------------------------------------

🔄 DAILY WORKFLOW:
  1. Scrape Match Data
  2. Run Analysis (Batch)
  3. Sync to Airtable
  4. Archive Files
  5. ⚡ RUN ALL (Scrape → Analyze → Sync → Archive)

🤖 MACHINE LEARNING:
  6. Post-Match Analysis (Update Statistics)
  7. ML Calibration (After 30+ Losses)

🔍 UTILITIES:
  8. View Results Summary
  9. Recalculate AH Lines
  10. Clean Up Temp Files

📊 QUICK STATS:
  11. Count Decisions
  12. View Match Analysis

  0. Exit

--------------------------------------------------------------------------------
Select option:
```

---

## 🎯 Key Features

### 1. Run Complete Workflow (Option 5)
One command does everything:
- Scrapes match data
- Runs Yudor v5.3 analysis
- Syncs to Airtable
- Archives files

**Input**: Just specify `matches_all.txt` (or custom file)
**Output**: Complete analysis ready for betting

---

### 2. Machine Learning Integration
- **Option 6**: Update statistics from Airtable results
- **Option 7**: Run ML calibration (after 30+ losses)

**Automatic**: Fetches data, calculates stats, proposes improvements

---

### 3. Quick Stats & View Results
- **Option 8**: View summary (win rates, ROI, losses)
- **Option 11**: Count CORE/EXP/FLIP/VETO decisions
- **Option 12**: View specific match analysis

**No commands to remember**: Just select and view

---

## 📋 Example Session

```
Select option: 5

================================================================================
⚡ RUNNING COMPLETE WORKFLOW
================================================================================

Steps: Scrape → Analyze → Sync → Archive

Match list file [matches_all.txt]: (press Enter)

⚠️  This will run the complete workflow. Continue? (yes/no): yes

================================================================================
STEP 1/4: SCRAPING
================================================================================
🌐 Scraping 48 matches...
✅ Complete

================================================================================
STEP 2/4: ANALYZING
================================================================================
🎯 Running Yudor v5.3 analysis...
✅ Complete - 14 CORE, 5 EXP, 1 FLIP, 28 VETO

================================================================================
STEP 3/4: SYNCING
================================================================================
📤 Syncing to Airtable...
✅ Synced 20 betting opportunities

================================================================================
STEP 4/4: ARCHIVING
================================================================================
📦 Archiving to archived_analyses/2025-11-21/
✅ Complete

================================================================================
✅ COMPLETE WORKFLOW FINISHED
================================================================================

Press Enter to continue...
```

---

## 🎓 Benefits

### ✅ No Command Memorization
- Interactive menu
- Clear descriptions
- Guided inputs

### ✅ Safety Confirmations
- Asks before running heavy operations
- Shows what will happen
- Cancel anytime

### ✅ Integrated ML System
- Post-match analysis built-in
- ML calibration accessible
- View results easily

### ✅ Quick Access to Everything
- View stats without grep
- Count decisions instantly
- Check specific matches

---

## 🔄 Typical Daily Use

```bash
# Morning: Run complete workflow
python3 yudor.py
> Select: 5 (RUN ALL)
> File: matches_all.txt
> Confirm: yes
> Wait 10-20 minutes
> ✅ Done! Check Airtable for bets

# Evening: After matches finish
python3 yudor.py
> Select: 6 (Post-Match Analysis)
> ✅ Statistics updated

# After 30 losses:
python3 yudor.py
> Select: 7 (ML Calibration)
> Review proposals
> Implement changes
```

---

## 📞 Help & Docs

- **Full Documentation**: See [ML_SYSTEM_GUIDE.md](ML_SYSTEM_GUIDE.md)
- **Quick Start**: See [ML_QUICK_START.md](ML_QUICK_START.md)
- **All Commands**: See [CHEATCODE.md](CHEATCODE.md)

---

**Remember**: `python3 yudor.py` is all you need to remember!
