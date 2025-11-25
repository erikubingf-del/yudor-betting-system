# YUDOR Betting System - File Organization (Master Orchestrator Pattern)

## Directory Structure

### Root Directory
**Essential Files Only:**
- `requirements.txt` - Python dependencies
- `team_news_urls_complete.json` - Team news URL database (Marca)
- `sofascore_team_urls.json` - SofaScore team URLs database
- `*.md` - Documentation files

### `/scraped_data/` - Organized Match Analysis Output

#### `/scraped_data/high_quality/`
- **High quality matches (6+ sources)**
- Ready for AI predictions
- These are your best data for YUDOR analysis

#### `/scraped_data/low_quality/`
- **Low/medium quality matches (<6 sources)**
- Saved for learning and analysis
- Helps you understand data gaps and improve the system
- Can identify which leagues/teams have poor coverage

#### `/scraped_data/batch_summaries/`
- **Batch processing summary reports**
- Tracks all matches analyzed in each batch run
- Shows quality distribution and processing stats

## Master Orchestrator Pattern

**"Save everything, organize intelligently, learn from all matches"**

The system follows a master orchestrator pattern where:
1. ✅ ALL matches are analyzed
2. 📁 ALL matches are saved (to appropriate quality folder)
3. 📊 ALL matches are tracked in batch summaries
4. 🎓 Learn from both successes AND failures

### Quality Tiers:
- **HIGH QUALITY (6+ sources):** Best data for AI predictions
- **LOW/MEDIUM QUALITY (<6 sources):** Saved for learning

## Clean Workflow

### For Batch Processing (RECOMMENDED):
```bash
python3 scripts/batch_match_analyzer.py matches.csv
```
Output:
- `scraped_data/high_quality/match_analysis_*.json` (6+ sources)
- `scraped_data/low_quality/match_analysis_*.json` (<6 sources)
- `scraped_data/batch_summaries/batch_analysis_summary_TIMESTAMP.json`

This is the **Master Orchestrator Pattern** in action!
