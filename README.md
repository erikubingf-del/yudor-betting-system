# YUDOR Betting Analysis System

Professional football betting analysis using Q1-Q19 scoring, Asian Handicap calculations, and machine learning calibration.

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Analyze
python scripts/production/master_orchestrator.py analyze "Team A vs Team B, League, DD/MM/YYYY"
```

## Documentation

- [System Overview](documentation/SYSTEM_OVERVIEW.md) - Complete system guide
- [Scripts Reference](documentation/SCRIPTS_REFERENCE.md) - All scripts explained
- [API Reference](documentation/API_REFERENCE.md) - External APIs
- [Fair Odds Explanation](documentation/YUDOR_FAIR_ODDS_EXPLANATION.md) - Math

## Project Structure

```
scripts/production/     # Main analysis
scripts/scrapers/       # Data collection
data/analyses/          # Match analyses
documentation/          # All guides
```

**Version:** 2.0.0 | **Status:** Production | **Last Updated:** 2025-11-25