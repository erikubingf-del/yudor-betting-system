#!/usr/bin/env python3
"""
Build comprehensive team URLs database for all teams in each league
Strategy: Get teams from FBref, then search for news URLs for each team
"""
import sys
sys.path.insert(0, '/tmp/soccerdata')

import json
import time
import requests
from typing import Dict, List
import soccerdata as sd

# Serper API for Google search
SERPER_API_KEY = "9fd24b439c206f3773506ab8eb39fabbd445c70a"

# League-specific news sources
LEAGUE_NEWS_SOURCES = {
    'La Liga': {
        'source': 'marca.com',
        'team_path': '/futbol/',
        'query_template': 'site:marca.com/futbol "{team}"'
    },
    'Premier League': {
        'source': 'skysports.com',
        'team_path': '/football/teams/',
        'query_template': 'site:skysports.com/football/teams "{team}"'
    },
    'Serie A': {
        'source': 'gazzetta.it',
        'team_path': '/calcio/squadre/',
        'query_template': 'site:gazzetta.it/calcio/squadre "{team}"'
    },
    'Bundesliga': {
        'source': 'bulinews.com',
        'team_path': '/',
        'query_template': 'site:bulinews.com "{team}"'
    },
    'Ligue 1': {
        'source': 'lequipe.fr',
        'team_path': '/football/football/',
        'query_template': 'site:lequipe.fr/football "{team}"'
    },
    'Brasileirão': {
        'source': 'ge.globo.com',
        'team_path': '/futebol/times/',
        'query_template': 'globoesporte "{team}"'
    },
}

LEAGUE_MAP = {
    'La Liga': 'ESP-La Liga',
    'Premier League': 'ENG-Premier League',
    'Serie A': 'ITA-Serie A',
    'Bundesliga': 'GER-Bundesliga',
    'Ligue 1': 'FRA-Ligue 1',
    'Brasileirão': 'BRA-Serie A',
}


def get_teams_from_fbref(league: str, season: str = '2425') -> List[str]:
    """Get all teams in a league from FBref"""
    print(f"\n{'='*80}")
    print(f"Fetching teams from {league}...")
    print('='*80)

    try:
        fbref_league = LEAGUE_MAP.get(league, league)
        fb = sd.FBref(leagues=fbref_league, seasons=season)

        # Get team season stats to extract team names
        stats = fb.read_team_season_stats(stat_type='standard')
        teams = stats.index.get_level_values('team').unique().tolist()

        print(f"✅ Found {len(teams)} teams in {league}")
        for i, team in enumerate(teams, 1):
            print(f"   {i:2d}. {team}")

        return teams

    except Exception as e:
        print(f"❌ Error fetching teams from {league}: {e}")
        return []


def search_team_news_url(team: str, league: str) -> str:
    """Search for team news page URL using Google"""
    news_config = LEAGUE_NEWS_SOURCES.get(league)
    if not news_config:
        print(f"  ⚠️  No news source configured for {league}")
        return "NOT_FOUND"

    query = news_config['query_template'].format(team=team)

    try:
        resp = requests.post(
            'https://google.serper.dev/search',
            headers={
                'X-API-KEY': SERPER_API_KEY,
                'Content-Type': 'application/json'
            },
            json={'q': query, 'num': 5},
            timeout=10
        )

        if resp.status_code != 200:
            print(f"  ❌ Search failed (status {resp.status_code})")
            return "NOT_FOUND"

        results = resp.json().get('organic', [])

        # Filter results by team path
        source = news_config['source']
        team_path = news_config['team_path']

        for result in results:
            url = result.get('link', '')
            # Check if URL contains the source and team path
            if source in url and team_path in url:
                print(f"  ✅ {team}: {url}")
                return url

        # If no perfect match, return first result from source
        for result in results:
            url = result.get('link', '')
            if source in url:
                print(f"  ⚠️  {team}: {url} (fallback)")
                return url

        print(f"  ❌ {team}: No URL found")
        return "NOT_FOUND"

    except Exception as e:
        print(f"  ❌ Error searching for {team}: {e}")
        return "NOT_FOUND"


def build_league_urls(league: str, season: str = '2425') -> Dict:
    """Build URL database for all teams in a league"""
    teams = get_teams_from_fbref(league, season)

    if not teams:
        return {}

    print(f"\n{'='*80}")
    print(f"Searching news URLs for {len(teams)} teams in {league}...")
    print('='*80 + "\n")

    team_urls = {}

    for i, team in enumerate(teams, 1):
        print(f"[{i}/{len(teams)}] {team}")
        url = search_team_news_url(team, league)
        team_urls[team.lower()] = url

        # Rate limit: 1 request per second
        if i < len(teams):
            time.sleep(1.2)

    return team_urls


def build_all_leagues_database(leagues: List[str], output_file: str = 'team_news_urls.json'):
    """Build comprehensive database for all leagues"""
    print("\n" + "="*80)
    print("BUILDING COMPREHENSIVE TEAM NEWS URLS DATABASE")
    print("="*80)

    all_data = {}

    for league in leagues:
        league_data = build_league_urls(league)
        all_data[league] = league_data

        successful = sum(1 for url in league_data.values() if url != "NOT_FOUND")
        print(f"\n✅ {league}: {successful}/{len(league_data)} URLs found")

    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"✅ Database saved to {output_file}")
    print('='*80)

    # Summary
    total_teams = sum(len(data) for data in all_data.values())
    total_found = sum(
        sum(1 for url in data.values() if url != "NOT_FOUND")
        for data in all_data.values()
    )

    print(f"\n📊 SUMMARY:")
    print(f"   Total teams: {total_teams}")
    print(f"   URLs found: {total_found} ({total_found/total_teams*100:.1f}%)")
    print(f"   Missing: {total_teams - total_found}")

    return all_data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Build team news URLs database')
    parser.add_argument('--league', type=str, help='Single league to process')
    parser.add_argument('--all', action='store_true', help='Process all leagues')
    parser.add_argument('--output', type=str, default='team_news_urls.json',
                       help='Output JSON file')

    args = parser.parse_args()

    if args.all:
        leagues = ['La Liga', 'Premier League', 'Serie A', 'Bundesliga', 'Ligue 1', 'Brasileirão']
        build_all_leagues_database(leagues, args.output)
    elif args.league:
        league_data = build_league_urls(args.league)
        print(f"\n✅ Found {len(league_data)} teams")

        # Save to JSON
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({args.league: league_data}, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved to {args.output}")
    else:
        print("Usage:")
        print("  python build_team_urls_database.py --all")
        print("  python build_team_urls_database.py --league 'La Liga'")
