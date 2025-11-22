#!/usr/bin/env python3
"""
YUDOR INTERNATIONAL SCRAPER V29 (TeamStatistics Fix)

Objective:
- Use Google Search via SerpApi for maximum accuracy.
- ECONOMY MODE: Executes ONLY ONE search query per item to save API credits.
- URL Cleaning: Forces WhoScored links to '/teamstatistics/', replacing '/betting/' or '/betbuilder/'.

Usage:
1. Paste your SerpApi Key in the Config class.
2. Run the script.
"""

import json
import time
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Dict, List

# =========================
# CONFIGURATION
# =========================

@dataclass
class Config:
    MATCHES_INPUT_FILE: str = "matches.txt"
    OUTPUT_FILE: str = "match_data_v29.json"
    
    # 🔑 PASTE YOUR KEY HERE
    SERPAPI_KEY: str = "6b3749e77d08a9ce26cfbe806282ec6f5326349fc3af54f46bb4e26227ab50cf" 
    
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
    "flamengo": "https://ge.globo.com/futebol/times/flamengo/",
    "sport": "https://ge.globo.com/pe/futebol/times/sport/",
    "palmeiras": "https://ge.globo.com/futebol/times/palmeiras/",
    "mainz 05": "https://bulinews.com/mainz",
    "hoffenheim": "https://bulinews.com/hoffenheim",
    "valencia": "https://www.marca.com/futbol/valencia.html",
    "levante": "https://www.marca.com/futbol/levante.html",
    "watford": "https://www.skysports.com/watford",
    "plymouth": "https://www.skysports.com/plymouth-argyle",
    "arsenal": "https://www.skysports.com/arsenal",
    "man city": "https://www.skysports.com/manchester-city",
    "liverpool": "https://www.skysports.com/liverpool",
    "real madrid": "https://www.marca.com/futbol/real-madrid.html",
    "barcelona": "https://www.marca.com/futbol/barcelona.html",
    "bayern munich": "https://bulinews.com/bayern-munich",
    "dortmund": "https://bulinews.com/borussia-dortmund"
    # ... (Assuming full list from V22 is present)
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

def determine_news_source(league: str) -> str:
    l = league.lower()
    if "brasileir" in l or "brazil" in l: return "globoesporte"
    if "serie a" in l or "italy" in l: return "gazzetta"
    if "la liga" in l or "spain" in l: return "marca"
    if "premier" in l or "england" in l: return "skysports"
    if "bundesliga" in l or "germany" in l: return "bulinews"
    return "globoesporte"

def get_common_name(name: str) -> str:
    n = name.lower().strip()
    if n == "sport": return "Sport Recife"
    if n == "athletico": return "Athletico-PR"
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

def serpapi_search(query: str, count: int = 10) -> List[str]:
    """
    Uses SerpApi (Google Engine) to find results.
    """
    if not Config.SERPAPI_KEY:
        print("   ⚠️ SERPAPI_KEY is empty! Please add your key in Config.")
        return []
        
    print(f"   🔎 Google Searching (Economy): {query}")
    params = {
        "engine": "google",
        "q": query,
        "api_key": Config.SERPAPI_KEY,
        "num": count
    }
    
    try:
        resp = requests.get("https://serpapi.com/search", params=params, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("organic_results", [])
            return [r.get("link") for r in results if r.get("link")]
        else:
            print(f"   ⚠️ SerpApi Error: {resp.status_code} - {resp.text}")
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
        if site_key == "transfermarkt" and team_raw in KNOWN_TM_URLS: return KNOWN_TM_URLS[team_raw]
        if site_key in ["globoesporte", "gazzetta", "marca", "skysports", "bulinews"]:
            if team_raw in KNOWN_NEWS_URLS: return KNOWN_NEWS_URLS[team_raw]
            for k in KNOWN_NEWS_URLS: 
                if k in team_raw or team_raw in k: 
                    if abs(len(k) - len(team_raw)) < 8: return KNOWN_NEWS_URLS[k]

    # --- ECONOMY SEARCH: ONE QUERY ONLY ---
    query = ""
    
    if scope == "match":
        if site_key == "whoscored":
            # The "Magic" query that works on Google
            query = f'site:{domain} "{home_common} vs {away_common}" Preview {search_date}'
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
    urls = serpapi_search(query, count=10)
    
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

def run():
    matches = []
    try:
        with open(Config.MATCHES_INPUT_FILE, "r") as f:
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
    except: return

    all_data = {}
    print(f"🚀 Starting International Scraper (V29 - SerpApi Economy) for {len(matches)} matches...")

    for m in matches:
        print(f"\n⚽ {m['home']} vs {m['away']} ({m['league']})")
        news_source = determine_news_source(m["league"])
        
        entry = {"match_info": m, "urls": {}, "news": {}}

        for site in ["sofascore", "whoscored", "flashscore", "sportsmole"]:
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

    with open(Config.OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print(f"\n✅ Data saved to {Config.OUTPUT_FILE}")

if __name__ == "__main__":
    run()
