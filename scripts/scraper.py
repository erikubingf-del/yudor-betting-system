#!/usr/bin/env python3
"""
YUDOR INTERNATIONAL SCRAPER V29 (TeamStatistics Fix)

Objective:
- Use Google Search via SerpApi for maximum accuracy.
- ECONOMY MODE: Executes ONLY ONE search query per item to save API credits.
- URL Cleaning: Forces WhoScored links to '/teamstatistics/', replacing '/betting/' or '/betbuilder/'.

Usage:
1. Add SERPAPI_KEY to your .env
2. Run the script.
"""

import argparse
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# =========================
# CONFIGURATION
# =========================

@dataclass
class Config:
    MATCHES_INPUT_FILE: str = "matches.txt"
    OUTPUT_FILE: str = "match_data_v29.json"
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "9fd24b439c206f3773506ab8eb39fabbd445c70a")

    SITES = {
        "sportsmole": "sportsmole.co.uk",
        "sofascore": "sofascore.com",
        "whoscored": "whoscored.com",
        "flashscore": "flashscore.com.br",
        "transfermarkt": "transfermarkt.com.br",
        "globoesporte": "ge.globo.com",
        "gazzetta": "gazzetta.it",
        "marca": "marca.com",
        "skysports": "skysports.com",
        "bulinews": "bulinews.com"
    }

# =========================
# FAIL-SAFE DICTIONARIES (Full)
# =========================
KNOWN_NEWS_URLS = {
    # === PREMIER LEAGUE (skysports) ===
    "arsenal": "https://www.skysports.com/arsenal",
    "aston villa": "https://www.skysports.com/aston-villa",
    "bournemouth": "https://www.skysports.com/bournemouth",
    "brentford": "https://www.skysports.com/brentford",
    "brighton": "https://www.skysports.com/brighton-and-hove-albion",
    "brighton & hove albion": "https://www.skysports.com/brighton-and-hove-albion",
    "chelsea": "https://www.skysports.com/chelsea",
    "crystal palace": "https://www.skysports.com/crystal-palace",
    "everton": "https://www.skysports.com/everton",
    "fulham": "https://www.skysports.com/fulham",
    "ipswich": "https://www.skysports.com/ipswich-town",
    "ipswich town": "https://www.skysports.com/ipswich-town",
    "leicester": "https://www.skysports.com/leicester-city",
    "leicester city": "https://www.skysports.com/leicester-city",
    "liverpool": "https://www.skysports.com/liverpool",
    "man city": "https://www.skysports.com/manchester-city",
    "manchester city": "https://www.skysports.com/manchester-city",
    "man utd": "https://www.skysports.com/manchester-united",
    "manchester united": "https://www.skysports.com/manchester-united",
    "newcastle": "https://www.skysports.com/newcastle-united",
    "newcastle united": "https://www.skysports.com/newcastle-united",
    "nottingham forest": "https://www.skysports.com/nottingham-forest",
    "southampton": "https://www.skysports.com/southampton",
    "tottenham": "https://www.skysports.com/tottenham-hotspur",
    "tottenham hotspur": "https://www.skysports.com/tottenham-hotspur",
    "spurs": "https://www.skysports.com/tottenham-hotspur",
    "west ham": "https://www.skysports.com/west-ham-united",
    "west ham united": "https://www.skysports.com/west-ham-united",
    "wolves": "https://www.skysports.com/wolverhampton-wanderers",
    "wolverhampton": "https://www.skysports.com/wolverhampton-wanderers",
    "wolverhampton wanderers": "https://www.skysports.com/wolverhampton-wanderers",
    # Championship
    "watford": "https://www.skysports.com/watford",
    "plymouth": "https://www.skysports.com/plymouth-argyle",
    "plymouth argyle": "https://www.skysports.com/plymouth-argyle",
    "leeds": "https://www.skysports.com/leeds-united",
    "leeds united": "https://www.skysports.com/leeds-united",
    "burnley": "https://www.skysports.com/burnley",
    "sheffield united": "https://www.skysports.com/sheffield-united",
    "sunderland": "https://www.skysports.com/sunderland",

    # === BUNDESLIGA (bulinews) ===
    "bayern munich": "https://bulinews.com/bayern-munich",
    "bayern": "https://bulinews.com/bayern-munich",
    "bayern münchen": "https://bulinews.com/bayern-munich",
    "fc bayern münchen": "https://bulinews.com/bayern-munich",
    "borussia dortmund": "https://bulinews.com/borussia-dortmund",
    "dortmund": "https://bulinews.com/borussia-dortmund",
    "bvb": "https://bulinews.com/borussia-dortmund",
    "rb leipzig": "https://bulinews.com/rb-leipzig",
    "leipzig": "https://bulinews.com/rb-leipzig",
    "bayer leverkusen": "https://bulinews.com/bayer-leverkusen",
    "leverkusen": "https://bulinews.com/bayer-leverkusen",
    "eintracht frankfurt": "https://bulinews.com/eintracht-frankfurt",
    "frankfurt": "https://bulinews.com/eintracht-frankfurt",
    "vfb stuttgart": "https://bulinews.com/vfb-stuttgart",
    "stuttgart": "https://bulinews.com/vfb-stuttgart",
    "wolfsburg": "https://bulinews.com/wolfsburg",
    "vfl wolfsburg": "https://bulinews.com/wolfsburg",
    "borussia mönchengladbach": "https://bulinews.com/gladbach",
    "borussia monchengladbach": "https://bulinews.com/gladbach",
    "gladbach": "https://bulinews.com/gladbach",
    "mönchengladbach": "https://bulinews.com/gladbach",
    "monchengladbach": "https://bulinews.com/gladbach",
    "union berlin": "https://bulinews.com/union-berlin",
    "freiburg": "https://bulinews.com/freiburg",
    "sc freiburg": "https://bulinews.com/freiburg",
    "werder bremen": "https://bulinews.com/werder-bremen",
    "bremen": "https://bulinews.com/werder-bremen",
    "mainz": "https://bulinews.com/mainz",
    "mainz 05": "https://bulinews.com/mainz",
    "1. fsv mainz 05": "https://bulinews.com/mainz",
    "hoffenheim": "https://bulinews.com/hoffenheim",
    "tsg hoffenheim": "https://bulinews.com/hoffenheim",
    "augsburg": "https://bulinews.com/augsburg",
    "fc augsburg": "https://bulinews.com/augsburg",
    "heidenheim": "https://bulinews.com/heidenheim",
    "fc heidenheim": "https://bulinews.com/heidenheim",
    "st. pauli": "https://bulinews.com/st-pauli",
    "fc st. pauli": "https://bulinews.com/st-pauli",
    "st pauli": "https://bulinews.com/st-pauli",
    "holstein kiel": "https://bulinews.com/holstein-kiel",
    "kiel": "https://bulinews.com/holstein-kiel",
    "bochum": "https://bulinews.com/bochum",
    "vfl bochum": "https://bulinews.com/bochum",

    # === LA LIGA (marca) ===
    "real madrid": "https://www.marca.com/futbol/real-madrid.html",
    "barcelona": "https://www.marca.com/futbol/barcelona.html",
    "atletico madrid": "https://www.marca.com/futbol/atletico-madrid.html",
    "atlético madrid": "https://www.marca.com/futbol/atletico-madrid.html",
    "atletico de madrid": "https://www.marca.com/futbol/atletico-madrid.html",
    "athletic bilbao": "https://www.marca.com/futbol/athletic-bilbao.html",
    "athletic club": "https://www.marca.com/futbol/athletic-bilbao.html",
    "villarreal": "https://www.marca.com/futbol/villarreal.html",
    "real sociedad": "https://www.marca.com/futbol/real-sociedad.html",
    "real betis": "https://www.marca.com/futbol/real-betis.html",
    "betis": "https://www.marca.com/futbol/real-betis.html",
    "sevilla": "https://www.marca.com/futbol/sevilla.html",
    "valencia": "https://www.marca.com/futbol/valencia.html",
    "osasuna": "https://www.marca.com/futbol/osasuna.html",
    "rayo vallecano": "https://www.marca.com/futbol/rayo-vallecano.html",
    "celta vigo": "https://www.marca.com/futbol/celta.html",
    "celta": "https://www.marca.com/futbol/celta.html",
    "mallorca": "https://www.marca.com/futbol/mallorca.html",
    "getafe": "https://www.marca.com/futbol/getafe.html",
    "girona": "https://www.marca.com/futbol/girona.html",
    "las palmas": "https://www.marca.com/futbol/las-palmas.html",
    "alaves": "https://www.marca.com/futbol/alaves.html",
    "alavés": "https://www.marca.com/futbol/alaves.html",
    "espanyol": "https://www.marca.com/futbol/espanyol.html",
    "leganes": "https://www.marca.com/futbol/leganes.html",
    "leganés": "https://www.marca.com/futbol/leganes.html",
    "valladolid": "https://www.marca.com/futbol/valladolid.html",
    "real valladolid": "https://www.marca.com/futbol/valladolid.html",
    "levante": "https://www.marca.com/futbol/levante.html",

    # === SERIE A (gazzetta) ===
    "inter": "https://www.gazzetta.it/calcio/squadre/inter/",
    "inter milan": "https://www.gazzetta.it/calcio/squadre/inter/",
    "internazionale": "https://www.gazzetta.it/calcio/squadre/inter/",
    "ac milan": "https://www.gazzetta.it/calcio/squadre/milan/",
    "milan": "https://www.gazzetta.it/calcio/squadre/milan/",
    "juventus": "https://www.gazzetta.it/calcio/squadre/juventus/",
    "napoli": "https://www.gazzetta.it/calcio/squadre/napoli/",
    "roma": "https://www.gazzetta.it/calcio/squadre/roma/",
    "as roma": "https://www.gazzetta.it/calcio/squadre/roma/",
    "lazio": "https://www.gazzetta.it/calcio/squadre/lazio/",
    "atalanta": "https://www.gazzetta.it/calcio/squadre/atalanta/",
    "fiorentina": "https://www.gazzetta.it/calcio/squadre/fiorentina/",
    "bologna": "https://www.gazzetta.it/calcio/squadre/bologna/",
    "torino": "https://www.gazzetta.it/calcio/squadre/torino/",
    "udinese": "https://www.gazzetta.it/calcio/squadre/udinese/",
    "genoa": "https://www.gazzetta.it/calcio/squadre/genoa/",
    "cagliari": "https://www.gazzetta.it/calcio/squadre/cagliari/",
    "empoli": "https://www.gazzetta.it/calcio/squadre/empoli/",
    "parma": "https://www.gazzetta.it/calcio/squadre/parma/",
    "como": "https://www.gazzetta.it/calcio/squadre/como/",
    "verona": "https://www.gazzetta.it/calcio/squadre/verona/",
    "hellas verona": "https://www.gazzetta.it/calcio/squadre/verona/",
    "lecce": "https://www.gazzetta.it/calcio/squadre/lecce/",
    "monza": "https://www.gazzetta.it/calcio/squadre/monza/",
    "venezia": "https://www.gazzetta.it/calcio/squadre/venezia/",

    # === BRASILEIRÃO (globoesporte) ===
    "flamengo": "https://ge.globo.com/futebol/times/flamengo/",
    "palmeiras": "https://ge.globo.com/futebol/times/palmeiras/",
    "botafogo": "https://ge.globo.com/futebol/times/botafogo/",
    "fortaleza": "https://ge.globo.com/futebol/times/fortaleza/",
    "internacional": "https://ge.globo.com/futebol/times/internacional/",
    "sao paulo": "https://ge.globo.com/futebol/times/sao-paulo/",
    "são paulo": "https://ge.globo.com/futebol/times/sao-paulo/",
    "corinthians": "https://ge.globo.com/futebol/times/corinthians/",
    "bahia": "https://ge.globo.com/futebol/times/bahia/",
    "cruzeiro": "https://ge.globo.com/futebol/times/cruzeiro/",
    "vasco": "https://ge.globo.com/futebol/times/vasco/",
    "vasco da gama": "https://ge.globo.com/futebol/times/vasco/",
    "atletico-mg": "https://ge.globo.com/futebol/times/atletico-mg/",
    "atlético-mg": "https://ge.globo.com/futebol/times/atletico-mg/",
    "atletico mineiro": "https://ge.globo.com/futebol/times/atletico-mg/",
    "gremio": "https://ge.globo.com/futebol/times/gremio/",
    "grêmio": "https://ge.globo.com/futebol/times/gremio/",
    "fluminense": "https://ge.globo.com/futebol/times/fluminense/",
    "vitoria": "https://ge.globo.com/futebol/times/vitoria/",
    "vitória": "https://ge.globo.com/futebol/times/vitoria/",
    "athletico": "https://ge.globo.com/futebol/times/athletico-pr/",
    "athletico-pr": "https://ge.globo.com/futebol/times/athletico-pr/",
    "sport": "https://ge.globo.com/pe/futebol/times/sport/",
    "sport recife": "https://ge.globo.com/pe/futebol/times/sport/",
    "ceara": "https://ge.globo.com/futebol/times/ceara/",
    "ceará": "https://ge.globo.com/futebol/times/ceara/",
    "santos": "https://ge.globo.com/futebol/times/santos/",
}

KNOWN_TM_URLS = {
     "flamengo": "https://www.transfermarkt.com.br/clube-de-regatas-do-flamengo/startseite/verein/614",
     "mainz 05": "https://www.transfermarkt.com.br/1-fsv-mainz-05/startseite/verein/39",
     "hoffenheim": "https://www.transfermarkt.com.br/tsg-1899-hoffenheim/startseite/verein/533",
     "valencia": "https://www.transfermarkt.com.br/fc-valencia/startseite/verein/1049",
     "levante": "https://www.transfermarkt.com.br/ud-levante/startseite/verein/3368",
     "arsenal": "https://www.transfermarkt.com.br/fc-arsenal/startseite/verein/11",
     "real madrid": "https://www.transfermarkt.com.br/real-madrid/startseite/verein/418"
     # ... (Assuming full list from V22 is present)
}

# =========================
# UTILS
# =========================

import unicodedata

def normalize_team_name(name: str) -> str:
    """Normalize team name: lowercase, remove accents, strip whitespace"""
    name = name.lower().strip()
    # Remove accents (ö -> o, é -> e, etc.)
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    return name

def determine_news_source(league: str) -> str:
    l = league.lower()
    if "brasileir" in l or "brazil" in l: return "globoesporte"
    if "serie a" in l or "italy" in l: return "gazzetta"
    if "la liga" in l or "spain" in l: return "marca"
    if "premier" in l or "england" in l: return "skysports"
    if "bundesliga" in l or "germany" in l: return "bulinews"
    return "globoesporte"

def get_common_name(name: str) -> str:
    """Get common name for search queries (especially SportsMole)"""
    n = name.lower().strip()

    # Team name aliases for better search results
    aliases = {
        "sport": "Sport Recife",
        "athletico": "Athletico-PR",
        "athletic club": "Athletic Bilbao",  # SportsMole uses "Athletic Bilbao"
        "atletico madrid": "Atletico Madrid",
        "atlético madrid": "Atletico Madrid",
        "borussia mönchengladbach": "Gladbach",
        "borussia monchengladbach": "Gladbach",
        "inter milan": "Inter",
        "ac milan": "Milan",
        "tottenham hotspur": "Tottenham",
        "manchester united": "Man Utd",
        "manchester city": "Man City",
        "wolverhampton wanderers": "Wolves",
        "wolverhampton": "Wolves",
        "brighton & hove albion": "Brighton",
        "west ham united": "West Ham",
        "newcastle united": "Newcastle",
        "nottingham forest": "Nottingham Forest",
        "rb leipzig": "Leipzig",
        "bayer leverkusen": "Leverkusen",
        "eintracht frankfurt": "Frankfurt",
        "real sociedad": "Real Sociedad",
        "real betis": "Real Betis",
        "celta vigo": "Celta",
    }

    if n in aliases:
        return aliases[n]
    return name

def format_search_date(date_str: str) -> str:
    """Converts 21/11/2025 -> Nov 21 2025"""
    try:
        dt = datetime.strptime(date_str, "%d/%m/%Y")
        return dt.strftime("%b %d %Y")
    except: return date_str

def clean_whoscored_url(url: str) -> str:
    """
    Fixes 'betting', 'betbuilder', or 'show' links to point to 'teamstatistics'.
    Example: /matches/1910756/betting/ -> /matches/1910756/teamstatistics/
    """
    if "whoscored.com/matches/" not in url: return url

    # Replace undesirable segments with 'teamstatistics'
    # Pattern: /matches/{ID}/{SEGMENT}/{Slug}
    # We explicitly target segments we want to replace to avoid breaking valid URLs
    new_url = re.sub(r"/matches/(\d+)/(?:betting|betbuilder|show|live|matchreport|preview)/", r"/matches/\1/teamstatistics/", url)

    return new_url

def serper_search(query: str, count: int = 10) -> List[str]:
    """
    Uses Serper.dev (Google Engine) to find results.
    Cheaper alternative to SerpApi.
    """
    if not Config.SERPER_API_KEY:
        print("   ⚠️ SERPER_API_KEY is empty! Please set it in your .env file.")
        return []

    print(f"   🔎 Google Searching (Serper): {query}")

    headers = {
        "X-API-KEY": Config.SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "q": query,
        "num": count
    }

    try:
        resp = requests.post("https://google.serper.dev/search", headers=headers, json=payload, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("organic", [])
            return [r.get("link") for r in results if r.get("link")]
        else:
            print(f"   ⚠️ Serper Error: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"   ⚠️ Connection Error: {e}")

    return []

# =========================
# SCRAPER
# =========================

def scrape_news_content(url: str, source: str) -> List[Dict]:
    news_items = []
    if "NOT_FOUND" in url: return news_items
    print(f"   📰 Scraping ({source}): {url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200: return news_items
        soup = BeautifulSoup(resp.text, "html.parser")
        links_found = []

        if source == "globoesporte":
            cards = soup.find_all("div", class_=["feed-post-body", "bastian-feed-item", "hui-premium__item"])
            for c in cards:
                a = c.find("a", href=True)
                if a: links_found.append(a)
        elif source == "bulinews":
            main = soup.find("div", id="content") or soup
            links_found = main.find_all("a", href=True)
        elif source == "marca":
            main = soup.find("main") or soup
            for art in main.find_all("article"):
                a = art.find("a", href=True)
                if a: links_found.append(a)
        elif source == "skysports":
            news_list = soup.find("div", class_="news-list") or soup.find("div", class_="sdc-site-tiles__group") or soup
            links_found = news_list.find_all("a", href=True)
        elif source == "gazzetta":
            main = soup.find("section", class_="squadre-notizie") or soup.find("main") or soup
            links_found = main.find_all("a", href=True)

        seen = set()
        for link_tag in links_found:
            title = link_tag.get_text().strip()
            href = link_tag['href']
            if not title or len(title) < 10: continue
            if not href.startswith("http"):
                base = "https://" + Config.SITES.get(source, "")
                href = base + href if href.startswith("/") else base + "/" + href

            if source == "globoesporte" and "/noticia/" not in href: continue
            if source == "bulinews" and href.count("-") < 2: continue

            if href not in seen:
                news_items.append({"title": title, "link": href})
                seen.add(href)
            if len(news_items) >= 10: break
    except: pass
    return news_items

def find_best_link(match: Dict, site_key: str, scope: str = "match") -> str:
    domain = Config.SITES.get(site_key, "")
    home_common = get_common_name(match["home"])
    away_common = get_common_name(match["away"])
    search_date = format_search_date(match["date"])

    # --- FAIL-SAFE DICTIONARY CHECK (No API Cost) ---
    if "team" in scope:
        team_raw = match["home"].lower() if scope == "home_team" else match["away"].lower()
        team_normalized = normalize_team_name(team_raw)

        # Check Transfermarkt dictionary
        if site_key == "transfermarkt":
            if team_raw in KNOWN_TM_URLS: return KNOWN_TM_URLS[team_raw]
            if team_normalized in KNOWN_TM_URLS: return KNOWN_TM_URLS[team_normalized]

        # Check News dictionaries (priority: exact match first)
        if site_key in ["globoesporte", "gazzetta", "marca", "skysports", "bulinews"]:
            # Try exact match first
            if team_raw in KNOWN_NEWS_URLS: return KNOWN_NEWS_URLS[team_raw]
            # Try normalized match
            if team_normalized in KNOWN_NEWS_URLS: return KNOWN_NEWS_URLS[team_normalized]
            # Try partial match (both directions)
            for k in KNOWN_NEWS_URLS:
                k_normalized = normalize_team_name(k)
                if k_normalized in team_normalized or team_normalized in k_normalized:
                    if abs(len(k_normalized) - len(team_normalized)) < 8: return KNOWN_NEWS_URLS[k]

    # --- ECONOMY SEARCH: ONE QUERY ONLY ---
    query = ""

    if scope == "match":
        if site_key == "whoscored":
            # The "Magic" query that works on Google
            query = f'site:{domain} "{home_common} vs {away_common}" Preview {search_date}'
        elif site_key == "sportsmole":
            # SportsMole: Use flexible query without strict quotes/date (finds previews better)
            query = f'site:{domain} {home_common} {away_common} preview prediction'
        else:
            # Standard date query for others
            query = f'site:{domain} "{home_common} vs {away_common}" {search_date}'

    elif "team" in scope:
        team = home_common if scope == "home_team" else away_common
        if site_key == "transfermarkt": query = f'site:{domain} "{team}" startseite verein'
        elif site_key == "globoesporte": query = f'globoesporte {team}'
        elif site_key == "marca": query = f'site:marca.com/futbol "{team}"'
        elif site_key == "bulinews": query = f'site:bulinews.com "{team}"'
        elif site_key == "gazzetta": query = f'site:gazzetta.it/calcio/squadre "{team}" notizie'
        elif site_key == "skysports": query = f'site:skysports.com/football/teams "{team}"'

    # Execute Single Search
    urls = serper_search(query, count=10)

    # --- FILTERING ---
    for url in urls:
        if domain not in url: continue

        if scope == "match" and site_key == "whoscored":
            # 1. Clean the URL (betting/preview -> teamstatistics)
            url = clean_whoscored_url(url)

            # 2. Verify Season (Simple Year Check)
            # Since query included Date, Google usually ranks the correct one #1.
            if re.search(r"20\d\d", url):
                 current_year = search_date.split()[-1] # 2025
                 if current_year in url: return url
                 # Also accept if it says 2025-2026
                 if f"{int(current_year)}-{int(current_year)+1}" in url: return url
            else:
                # If no year in URL, trust Google ranking
                return url

        # Other Sites Logic
        if site_key == "transfermarkt" and "/startseite/verein/" not in url: continue
        if site_key == "globoesporte" and ("/times/" not in url or len(url.split("/times/")[1]) > 40): continue
        if site_key == "marca" and ("/cronica/" in url or "/opinion/" in url): continue
        if site_key == "bulinews" and url.replace("https://bulinews.com/", "").count("-") > 1: continue
        if site_key == "skysports" and "/football/teams/" not in url: continue

        if site_key != "whoscored": return url

    return "NOT_FOUND"

# =========================
# RUNNER
# =========================

def load_matches(matches_file: str) -> List[Dict]:
    matches = []
    try:
        with open(matches_file, "r") as f:
            for line in f:
                if "," in line and not line.startswith("#"):
                    parts = [p.strip() for p in line.split(",")]
                    matches.append({
                        "id": f"{parts[0].replace(' ', '')}_{parts[2].replace('/', '')}",
                        "home": parts[0].split(" vs ")[0],
                        "away": parts[0].split(" vs ")[1],
                        "league": parts[1],
                        "date": parts[2]
                    })
    except FileNotFoundError:
        print(f"❌ Input file not found: {matches_file}")
        return []
    return matches

def run(matches_file: str = Config.MATCHES_INPUT_FILE, output_file: str = Config.OUTPUT_FILE):
    matches = load_matches(matches_file)
    if not matches:
        return

    all_data = {}
    print(f"🚀 Starting International Scraper (V29 - SerpApi Economy) for {len(matches)} matches...")

    for m in matches:
        print(f"\n⚽ {m['home']} vs {m['away']} ({m['league']})")
        news_source = determine_news_source(m["league"])

        entry = {"match_info": m, "urls": {}, "news": {}}

        # NOTE: SofaScore, WhoScored, FlashScore are DISABLED (blocked/403)
        # FootyStats API now provides stats (xG, PPG, goals, form)
        # Only SportsMole is needed for qualitative data (lineups, injuries, context)
        for site in ["sportsmole"]:  # Disabled: "sofascore", "whoscored", "flashscore"
            entry["urls"][site] = find_best_link(m, site, scope="match")
            time.sleep(0.1)

        entry["urls"]["tm_home"] = find_best_link(m, "transfermarkt", scope="home_team")
        entry["urls"]["tm_away"] = find_best_link(m, "transfermarkt", scope="away_team")

        url_h = find_best_link(m, news_source, scope="home_team")
        entry["urls"]["news_home"] = url_h
        entry["news"]["home"] = scrape_news_content(url_h, news_source)

        url_a = find_best_link(m, news_source, scope="away_team")
        entry["urls"]["news_away"] = url_a
        entry["news"]["away"] = scrape_news_content(url_a, news_source)

        all_data[m["id"]] = entry

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print(f"\n✅ Data saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yudor Scraper (V29)")
    parser.add_argument("--input", default=Config.MATCHES_INPUT_FILE, help="Path to matches file (default: matches.txt)")
    parser.add_argument("--output", default=Config.OUTPUT_FILE, help="Path to output JSON (default: match_data_v29.json)")
    args = parser.parse_args()

    run(matches_file=args.input, output_file=args.output)
