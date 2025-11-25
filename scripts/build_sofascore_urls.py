#!/usr/bin/env python3
"""
Build SofaScore team URLs database
Strategy: Search Google for SofaScore team pages, extract team IDs
"""
import sys
sys.path.insert(0, '/tmp/soccerdata')

import json
import time
import requests
from typing import Dict, List
import soccerdata as sd

SERPER_API_KEY = "9fd24b439c206f3773506ab8eb39fabbd445c70a"

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
        stats = fb.read_team_season_stats(stat_type='standard')
        teams = stats.index.get_level_values('team').unique().tolist()

        print(f"✅ Found {len(teams)} teams in {league}")
        return teams

    except Exception as e:
        print(f"❌ Error fetching teams from {league}: {e}")
        return []


def search_sofascore_team_url(team: str, league: str) -> Dict:
    """Search for SofaScore team page URL"""

    # Add league context to query for better accuracy
    league_keywords = {
        'La Liga': 'spain laliga',
        'Premier League': 'england premier',
        'Serie A': 'italy serie',
        'Bundesliga': 'germany bundesliga',
        'Ligue 1': 'france ligue',
        'Brasileirão': 'brazil serie'
    }

    league_ctx = league_keywords.get(league, '')

    # SofaScore team page pattern: sofascore.com/team/football/TEAMNAME/ID
    # IMPORTANT: Add "/football/" to filter out other sports (basketball, tennis, etc.)
    query = f'site:sofascore.com/team/football/ "{team}" {league_ctx}'

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
            return {"url": "NOT_FOUND", "team_id": None}

        results = resp.json().get('organic', [])

        # Find team page URL (not match pages)
        for result in results:
            url = result.get('link', '')

            # SofaScore team pages: sofascore.com/team/NAME/ID
            if 'sofascore.com/team/' in url and '/tournament/' not in url:
                # Extract team ID from URL
                # Example: https://www.sofascore.com/team/football/barcelona/2817
                parts = url.split('/')
                if len(parts) >= 2:
                    team_id = parts[-1].split('#')[0].split('?')[0]  # Remove anchors/params
                    print(f"  ✅ {team}: {url} (ID: {team_id})")
                    return {"url": url, "team_id": team_id}

        # Fallback: return first sofascore.com result
        for result in results:
            url = result.get('link', '')
            if 'sofascore.com' in url:
                print(f"  ⚠️  {team}: {url} (fallback - no ID)")
                return {"url": url, "team_id": None}

        print(f"  ❌ {team}: No SofaScore URL found")
        return {"url": "NOT_FOUND", "team_id": None}

    except Exception as e:
        print(f"  ❌ Error searching for {team}: {e}")
        return {"url": "NOT_FOUND", "team_id": None}


def build_league_sofascore_urls(league: str, season: str = '2425') -> Dict:
    """Build SofaScore URL database for all teams in a league"""
    teams = get_teams_from_fbref(league, season)

    if not teams:
        return {}

    print(f"\n{'='*80}")
    print(f"Searching SofaScore URLs for {len(teams)} teams in {league}...")
    print('='*80 + "\n")

    team_data = {}

    for i, team in enumerate(teams, 1):
        print(f"[{i}/{len(teams)}] {team}")
        data = search_sofascore_team_url(team, league)
        team_data[team.lower()] = data

        # Rate limit: 1 request per second
        if i < len(teams):
            time.sleep(1.2)

    return team_data


def build_all_leagues_sofascore_database(leagues: List[str], output_file: str = 'sofascore_team_urls.json'):
    """Build comprehensive SofaScore database for all leagues"""
    print("\n" + "="*80)
    print("BUILDING COMPREHENSIVE SOFASCORE TEAM URLS DATABASE")
    print("="*80)

    all_data = {}

    for league in leagues:
        league_data = build_league_sofascore_urls(league)
        all_data[league] = league_data

        successful = sum(1 for d in league_data.values() if d['url'] != "NOT_FOUND")
        with_ids = sum(1 for d in league_data.values() if d['team_id'] is not None)

        print(f"\n✅ {league}: {successful}/{len(league_data)} URLs found ({with_ids} with team IDs)")

    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"✅ Database saved to {output_file}")
    print('='*80)

    # Summary
    total_teams = sum(len(data) for data in all_data.values())
    total_found = sum(
        sum(1 for d in data.values() if d['url'] != "NOT_FOUND")
        for data in all_data.values()
    )
    total_ids = sum(
        sum(1 for d in data.values() if d['team_id'] is not None)
        for data in all_data.values()
    )

    print(f"\n📊 SUMMARY:")
    print(f"   Total teams: {total_teams}")
    print(f"   URLs found: {total_found} ({total_found/total_teams*100:.1f}%)")
    print(f"   Team IDs extracted: {total_ids} ({total_ids/total_teams*100:.1f}%)")
    print(f"   Missing: {total_teams - total_found}")

    return all_data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Build SofaScore team URLs database')
    parser.add_argument('--league', type=str, help='Single league to process')
    parser.add_argument('--all', action='store_true', help='Process all leagues')
    parser.add_argument('--output', type=str, default='sofascore_team_urls.json',
                       help='Output JSON file')

    args = parser.parse_args()

    if args.all:
        leagues = ['La Liga', 'Premier League', 'Serie A', 'Bundesliga', 'Ligue 1', 'Brasileirão']
        build_all_leagues_sofascore_database(leagues, args.output)
    elif args.league:
        league_data = build_league_sofascore_urls(args.league)
        print(f"\n✅ Found {len(league_data)} teams")

        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({args.league: league_data}, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved to {args.output}")
    else:
        print("Usage:")
        print("  python build_sofascore_urls.py --all")
        print("  python build_sofascore_urls.py --league 'La Liga'")
