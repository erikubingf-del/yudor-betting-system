#!/usr/bin/env python3
"""
Add Brasileirão teams to news URLs database
Since Brasileirão is not in FBref, we'll use a manual list of Serie A teams
"""
import json
import time
import requests

SERPER_API_KEY = "9fd24b439c206f3773506ab8eb39fabbd445c70a"

# Brasileirão Serie A 2024/2025 teams
BRASILEIRAO_TEAMS = [
    "Flamengo", "Palmeiras", "Botafogo", "Fluminense",
    "Grêmio", "Bragantino", "Athletico-PR", "Atlético-MG",
    "Internacional", "São Paulo", "Fortaleza", "Santos",
    "Bahia", "Corinthians", "Vasco", "Cruzeiro",
    "Cuiabá", "Vitória", "Juventude", "Criciúma"
]


def search_globoesporte_team_url(team: str) -> str:
    """Search for GloboEsporte team page URL"""
    query = f'globoesporte "{team}"'

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

        # Filter for team pages (ge.globo.com/futebol/times/)
        for result in results:
            url = result.get('link', '')
            if 'ge.globo.com' in url and '/futebol/times/' in url:
                # Make sure it's not too long (match reports have long URLs)
                if len(url.split('/futebol/times/')[1]) < 50:
                    print(f"  ✅ {team}: {url}")
                    return url

        # Fallback: any ge.globo.com result
        for result in results:
            url = result.get('link', '')
            if 'ge.globo.com' in url:
                print(f"  ⚠️  {team}: {url} (fallback)")
                return url

        print(f"  ❌ {team}: No URL found")
        return "NOT_FOUND"

    except Exception as e:
        print(f"  ❌ Error searching for {team}: {e}")
        return "NOT_FOUND"


def add_brasileirao_to_database(input_file: str = 'team_news_urls_complete.json',
                                 output_file: str = 'team_news_urls_complete.json'):
    """Add Brasileirão teams to existing database"""

    print("\n" + "="*80)
    print("ADDING BRASILEIRÃO TEAMS TO DATABASE")
    print("="*80 + "\n")

    # Load existing database
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded existing database: {len(data)} leagues")
    except FileNotFoundError:
        data = {}
        print("⚠️  No existing database found, creating new one")

    # Search for Brasileirão teams
    print(f"\nSearching GloboEsporte URLs for {len(BRASILEIRAO_TEAMS)} Brasileirão teams...")
    print("="*80 + "\n")

    brasileirao_data = {}

    for i, team in enumerate(BRASILEIRAO_TEAMS, 1):
        print(f"[{i}/{len(BRASILEIRAO_TEAMS)}] {team}")
        url = search_globoesporte_team_url(team)
        brasileirao_data[team.lower()] = url

        # Rate limit
        if i < len(BRASILEIRAO_TEAMS):
            time.sleep(1.2)

    # Add to database
    data['Brasileirão'] = brasileirao_data

    # Save updated database
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Summary
    successful = sum(1 for url in brasileirao_data.values() if url != "NOT_FOUND")

    print(f"\n{'='*80}")
    print(f"✅ Brasileirão added: {successful}/{len(BRASILEIRAO_TEAMS)} URLs found")
    print(f"✅ Database saved to {output_file}")
    print('='*80)

    # Total summary
    total_teams = sum(len(teams) for teams in data.values())
    total_found = sum(
        sum(1 for url in teams.values() if url != "NOT_FOUND")
        for teams in data.values()
    )

    print(f"\n📊 COMPLETE DATABASE SUMMARY:")
    print(f"   Total leagues: {len(data)}")
    print(f"   Total teams: {total_teams}")
    print(f"   URLs found: {total_found} ({total_found/total_teams*100:.1f}%)")
    print(f"   Missing: {total_teams - total_found}")

    return data


if __name__ == "__main__":
    add_brasileirao_to_database()
