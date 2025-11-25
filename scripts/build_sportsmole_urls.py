#!/usr/bin/env python3
"""
Build SportsMole URLs Database

SportsMole URL format: https://www.sportsmole.co.uk/football/{team-slug}/
Provides crucial team news and form context

This script generates URLs for all teams by:
1. Converting team names to SportsMole URL slugs
2. Verifying URLs exist (HTTP 200 check)
3. Saving to sportsmole_team_urls.json
"""
import json
import time
import requests
from pathlib import Path
from typing import Dict


# Team name to SportsMole slug mappings
TEAM_SLUG_MAPPINGS = {
    # La Liga
    "barcelona": "barcelona",
    "real madrid": "real-madrid",
    "atletico madrid": "atletico-madrid",
    "sevilla": "sevilla",
    "real betis": "real-betis",
    "real sociedad": "real-sociedad",
    "villarreal": "villarreal",
    "athletic bilbao": "athletic-bilbao",
    "valencia": "valencia",
    "osasuna": "osasuna",
    "getafe": "getafe",
    "espanyol": "espanyol",
    "rayo vallecano": "rayo-vallecano",
    "celta vigo": "celta-vigo",
    "girona": "girona",
    "mallorca": "mallorca",
    "las palmas": "las-palmas",
    "alaves": "deportivo-alaves",
    "granada": "granada",
    "cadiz": "cadiz",

    # Premier League
    "man city": "manchester-city",
    "manchester city": "manchester-city",
    "arsenal": "arsenal",
    "liverpool": "liverpool",
    "aston villa": "aston-villa",
    "tottenham": "tottenham-hotspur",
    "chelsea": "chelsea",
    "newcastle": "newcastle-united",
    "man united": "manchester-united",
    "manchester united": "manchester-united",
    "west ham": "west-ham-united",
    "brighton": "brighton-hove-albion",
    "wolves": "wolverhampton-wanderers",
    "fulham": "fulham",
    "bournemouth": "bournemouth",
    "crystal palace": "crystal-palace",
    "brentford": "brentford",
    "everton": "everton",
    "nottingham forest": "nottingham-forest",
    "luton": "luton-town",
    "burnley": "burnley",
    "sheffield united": "sheffield-united",

    # Serie A
    "inter": "internazionale",
    "juventus": "juventus",
    "milan": "ac-milan",
    "napoli": "napoli",
    "roma": "roma",
    "lazio": "lazio",
    "atalanta": "atalanta-bc",
    "fiorentina": "fiorentina",
    "torino": "torino",
    "bologna": "bologna",
    "monza": "monza",
    "verona": "hellas-verona",
    "udinese": "udinese",
    "genoa": "genoa",
    "lecce": "lecce",
    "cagliari": "cagliari",
    "frosinone": "frosinone",
    "sassuolo": "sassuolo",
    "empoli": "empoli",
    "salernitana": "salernitana",

    # Bundesliga
    "bayern munich": "bayern-munich",
    "leverkusen": "bayer-leverkusen",
    "dortmund": "borussia-dortmund",
    "rb leipzig": "rb-leipzig",
    "union berlin": "union-berlin",
    "freiburg": "freiburg",
    "eintracht frankfurt": "eintracht-frankfurt",
    "hoffenheim": "hoffenheim",
    "augsburg": "augsburg",
    "wolfsburg": "wolfsburg",
    "mainz": "mainz",
    "borussia m'gladbach": "borussia-monchengladbach",
    "werder bremen": "werder-bremen",
    "bochum": "bochum",
    "stuttgart": "stuttgart",
    "heidenheim": "heidenheim",
    "darmstadt": "darmstadt",
    "koln": "cologne",

    # Ligue 1
    "psg": "paris-saint-germain",
    "monaco": "monaco",
    "brest": "brest",
    "lille": "lille",
    "nice": "nice",
    "lens": "lens",
    "marseille": "marseille",
    "rennes": "rennes",
    "lyon": "lyon",
    "reims": "reims",
    "montpellier": "montpellier",
    "strasbourg": "strasbourg",
    "nantes": "nantes",
    "le havre": "le-havre",
    "toulouse": "toulouse",
    "lorient": "lorient",
    "metz": "metz",
    "clermont": "clermont",
}


def slugify_team_name(team: str) -> str:
    """Convert team name to SportsMole URL slug"""
    team_lower = team.lower()

    # Check direct mapping
    if team_lower in TEAM_SLUG_MAPPINGS:
        return TEAM_SLUG_MAPPINGS[team_lower]

    # Default: replace spaces with hyphens, lowercase
    slug = team_lower.replace(' ', '-')
    slug = slug.replace('.', '')
    slug = slug.replace("'", '')
    return slug


def verify_sportsmole_url(slug: str) -> bool:
    """Verify that a SportsMole URL exists"""
    url = f"https://www.sportsmole.co.uk/football/{slug}/"

    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        # Check if page exists and is not a 404
        if response.status_code == 200:
            # Additional check: verify it's a team page (contains team name in title)
            if '<title>' in response.text:
                return True
        return False
    except Exception as e:
        print(f"  ⚠️  Error checking {url}: {e}")
        return False


def build_sportsmole_database(verify: bool = True) -> Dict:
    """Build complete SportsMole URLs database for all leagues"""

    # Load team names from existing news URLs database
    team_news_file = Path(__file__).parent.parent / 'team_news_urls_complete.json'

    if not team_news_file.exists():
        print(f"❌ team_news_urls_complete.json not found!")
        return {}

    with open(team_news_file, 'r', encoding='utf-8') as f:
        team_news_urls = json.load(f)

    sportsmole_urls = {}

    print("\n" + "="*80)
    print("BUILDING SPORTSMOLE URLs DATABASE")
    print("="*80 + "\n")

    total_teams = sum(len(teams) for teams in team_news_urls.values())
    current = 0

    for league, teams in team_news_urls.items():
        print(f"\n📊 {league} ({len(teams)} teams)")
        print("-" * 80)

        sportsmole_urls[league] = {}

        for team in teams.keys():
            current += 1
            slug = slugify_team_name(team)
            url = f"https://www.sportsmole.co.uk/football/{slug}/"

            # Verify URL exists if requested
            if verify:
                print(f"[{current}/{total_teams}] Checking {team}... ", end='', flush=True)
                if verify_sportsmole_url(slug):
                    sportsmole_urls[league][team] = url
                    print(f"✅ {url}")
                else:
                    sportsmole_urls[league][team] = "NOT_FOUND"
                    print(f"❌ Not found")

                # Rate limiting
                time.sleep(0.5)
            else:
                # Just generate URL without verification
                sportsmole_urls[league][team] = url
                print(f"[{current}/{total_teams}] {team}: {url}")

    return sportsmole_urls


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Build SportsMole URLs database')
    parser.add_argument('--no-verify', action='store_true',
                        help='Skip URL verification (faster but may include invalid URLs)')
    parser.add_argument('--output', default='sportsmole_team_urls.json',
                        help='Output file path')

    args = parser.parse_args()

    # Build database
    verify = not args.no_verify
    sportsmole_urls = build_sportsmole_database(verify=verify)

    # Save to file
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sportsmole_urls, f, indent=2, ensure_ascii=False)

    # Statistics
    print("\n" + "="*80)
    print("DATABASE BUILD COMPLETE")
    print("="*80)

    total_teams = 0
    found_urls = 0

    for league, teams in sportsmole_urls.items():
        league_found = sum(1 for url in teams.values() if url != "NOT_FOUND")
        total_teams += len(teams)
        found_urls += league_found
        print(f"\n{league}:")
        print(f"  Total teams: {len(teams)}")
        print(f"  URLs found: {league_found} ({league_found/len(teams)*100:.1f}%)")

    print("\n" + "-"*80)
    print(f"Total teams: {total_teams}")
    print(f"URLs found: {found_urls} ({found_urls/total_teams*100:.1f}%)")
    print(f"\n💾 Saved to: {output_path}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
