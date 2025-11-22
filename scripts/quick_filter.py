#!/usr/bin/env python3
"""
Quick data quality calculation based on URL availability.
No Claude API calls - just counts available URLs.

PRIORITY (as per user request):
1. SportsMole (preview with context) - HIGHEST PRIORITY
2. Local news (news_home, news_away) - HIGH PRIORITY
3. Everything else is supplemented by FootyStats API
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

with open(BASE_DIR / 'match_data_v29.json') as f:
    data = json.load(f)

results = []
for match_id, match_data in data.items():
    urls = match_data.get('urls', {})
    news = match_data.get('news', {})

    # Calculate score based on found URLs
    # PRIORITY: SportsMole + Local News are most important
    # FootyStats API will fill in stats (xG, form, goals)
    score = 0
    has_sportsmole = urls.get('sportsmole') and urls.get('sportsmole') != 'NOT_FOUND'
    has_local_news = (
        (urls.get('news_home') and urls.get('news_home') != 'NOT_FOUND') or
        (urls.get('news_away') and urls.get('news_away') != 'NOT_FOUND')
    )

    # SportsMole - HIGHEST PRIORITY (preview, team news, context)
    if has_sportsmole:
        score += 35

    # Local news - HIGH PRIORITY (derby context, injuries, motivation)
    if urls.get('news_home') and urls.get('news_home') != 'NOT_FOUND':
        score += 15
    if urls.get('news_away') and urls.get('news_away') != 'NOT_FOUND':
        score += 15

    # Transfermarkt - Squad values (useful for Q1)
    if urls.get('tm_home') and urls.get('tm_home') != 'NOT_FOUND':
        score += 10
    if urls.get('tm_away') and urls.get('tm_away') != 'NOT_FOUND':
        score += 10

    # SofaScore/FlashScore/WhoScored - NOW OPTIONAL (FootyStats provides stats)
    if urls.get('sofascore') and urls.get('sofascore') != 'NOT_FOUND':
        score += 5
    if urls.get('whoscored') and urls.get('whoscored') != 'NOT_FOUND':
        score += 5
    if urls.get('flashscore') and urls.get('flashscore') != 'NOT_FOUND':
        score += 5

    # Bonus: Has BOTH SportsMole AND local news
    if has_sportsmole and has_local_news:
        score += 10  # Bonus for having both primary sources

    info = match_data.get('match_info', {})
    results.append({
        'match_id': match_id,
        'home': info.get('home'),
        'away': info.get('away'),
        'league': info.get('league'),
        'date': info.get('date'),
        'score': score
    })

# Sort by score
results.sort(key=lambda x: x['score'], reverse=True)

print('TOP MATCHES BY DATA QUALITY:')
print('='*60)
for r in results[:15]:
    print(f"{r['score']:3d} | {r['home']} vs {r['away']} ({r['league']})")

# Show how many pass threshold 70
passing = [r for r in results if r['score'] >= 70]
print(f'\n{len(passing)} matches pass threshold 70')

# Create matches_priority.txt with top games
threshold = 50  # Lower threshold since we only have URL-based scoring
priority = [r for r in results if r['score'] >= threshold]

with open(BASE_DIR / 'matches_priority.txt', 'w') as f:
    for r in priority:
        line = f"{r['home']} vs {r['away']}, {r['league']}, {r['date']}"
        f.write(line + '\n')

print(f'\n{len(priority)} matches pass threshold {threshold}')
print(f'Saved to matches_priority.txt')
