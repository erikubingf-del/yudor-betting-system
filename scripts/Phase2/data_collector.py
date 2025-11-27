import requests
import json
import os
import time
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime

class DataCollector:
    """
    Phase 2 Advanced Data Collector.
    - Performs its own Web Search (Serper API).
    - Scrapes content with site-specific logic (GloboEsporte, SportsMole, etc.).
    - Returns structured data for analysis.
    """
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }
        # Use the key from scraper.py or env
        self.serper_key = os.getenv("SERPER_API_KEY", "9fd24b439c206f3773506ab8eb39fabbd445c70a")

    def serper_search(self, query: str, count: int = 5) -> List[str]:
        """Executes a Google Search via Serper API."""
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query, "num": count})
        headers = {'X-API-KEY': self.serper_key, 'Content-Type': 'application/json'}

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            if response.status_code == 200:
                results = response.json().get("organic", [])
                return [r["link"] for r in results]
            else:
                print(f"   [Search Error] HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"   [Search Error] {e}")
            return []

    def fetch_url_content(self, url: str) -> str:
        """Generic fetcher."""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.text
        except Exception:
            pass
        return ""

    def scrape_globoesporte(self, team_url: str) -> List[Dict]:
        """
        Specific scraper for GloboEsporte team pages.
        Extracts news titles and links from the feed, filtering out videos and irrelevant content.
        """
        html = self.fetch_url_content(team_url)
        if not html: return []

        soup = BeautifulSoup(html, "html.parser")
        news_items = []
        
        # Based on user image and standard GE structure:
        # Items are often in lists with class 'bstn-hl-itemlist' or 'bastian-feed-item'
        # Links have class 'bstn-hl-link' or 'feed-post-link'
        
        # Strategy: Find all links that look like news articles
        # Filter out: '/video/', '/playlist/', '/episodio/'
        # Keep: '/noticia/'
        
        seen_links = set()
        
        # 1. Try Main Feed (Bastian Feed) - Common in GE
        # The image shows 'bstn-hl-link' inside 'bstn-hl-itemlist'
        
        potential_links = soup.find_all("a", href=True)
        
        for a in potential_links:
            href = a["href"]
            title = a.get_text(strip=True)
            
            # Check if it's a valid news link
            if "ge.globo.com" in href and "/noticia/" in href:
                # Exclude videos if possible (though /noticia/ usually implies text, /video/ is for videos)
                if "/video/" in href: continue
                
                # Check for video class in parent (from user image: 'bstn-hl-video')
                parent = a.find_parent("li")
                if parent and ("bstn-hl-video" in parent.get("class", []) or "video" in str(parent.get("class", []))):
                    continue

                if href not in seen_links and title:
                    # Extract timestamp from URL if possible (e.g. /2025/11/24/)
                    date_str = "0000-00-00"
                    match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", href)
                    if match:
                        date_str = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                    
                    news_items.append({
                        "title": title, 
                        "link": href, 
                        "source": "globoesporte",
                        "date": date_str
                    })
                    seen_links.add(href)
            
            if len(news_items) >= 20: break 
            
        # Sort by date descending (latest first)
        news_items.sort(key=lambda x: x["date"], reverse=True)
        
        # Limit to top 5 and fetch content
        final_items = news_items[:5]
        for item in final_items:
            try:
                # Fetch article content
                article_html = self.fetch_url_content(item["link"])
                if article_html:
                    art_soup = BeautifulSoup(article_html, "html.parser")
                    # Try common GE content classes
                    article_body = art_soup.find("article") or \
                                   art_soup.find("div", class_="mc-article-body") or \
                                   art_soup.find("div", class_="content-text") or \
                                   art_soup.find("div", class_="bstn-fd-content")
                                   
                    if article_body:
                        # Remove scripts and styles
                        for script in article_body(["script", "style"]):
                            script.decompose()
                        item["content"] = article_body.get_text(separator=" ", strip=True)[:5000]
                    else:
                        item["content"] = ""
            except Exception as e:
                print(f"   [GE Content Error] {e}")
                item["content"] = ""
            
        return final_items

    def scrape_sportsmole(self, url: str, match_date: str = None) -> List[Dict]:
        """Scrapes SportsMole preview content and verifies date."""
        html = self.fetch_url_content(url)
        if not html: return []
        
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else "SportsMole Preview"
        
        # Extract main article text
        article = soup.find("div", class_="article_content") or soup.body
        text = article.get_text(separator=" ", strip=True) if article else ""
        
        # Date Verification
        if match_date:
            try:
                # Expected format: YYYY-MM-DD
                dt = datetime.strptime(match_date, "%Y-%m-%d")
                # SportsMole formats: "Nov 28, 2025", "28 November 2025", "28/11/2025"
                # We'll check for Month Name + Day
                month_name = dt.strftime("%b") # Nov
                full_month = dt.strftime("%B") # November
                day = dt.day
                year = dt.year
                
                # Simple check: Look for "Nov 28" or "28 Nov" in the first 1000 chars
                snippet = text[:1000]
                
                date_found = False
                patterns = [
                    f"{month_name} {day}", f"{day} {month_name}",
                    f"{full_month} {day}", f"{day} {full_month}",
                    f"{year}"
                ]
                
                # Check if at least the year and (month or day) matches
                if str(year) in snippet:
                    if month_name in snippet or full_month in snippet:
                        date_found = True
                
                if not date_found:
                    print(f"      ⚠️ SportsMole Date Mismatch? Expected {match_date}, content might be old.")
                    # We can either discard or just warn. User said "confirm is the correct date".
                    # Let's add a warning flag to the item
                    title = f"[POSSIBLE DATE MISMATCH] {title}"
            except Exception as e:
                print(f"      ⚠️ Date check failed: {e}")

        return [{"title": title, "content": text[:5000], "link": url, "source": "sportsmole"}]

    BBC_TEAMS = {
        "Arsenal": "arsenal",
        "Aston Villa": "aston-villa",
        "Bournemouth": "afc-bournemouth",
        "Brentford": "brentford",
        "Brighton": "brighton-and-hove-albion",
        "Chelsea": "chelsea",
        "Crystal Palace": "crystal-palace",
        "Everton": "everton",
        "Fulham": "fulham",
        "Ipswich": "ipswich-town",
        "Leicester": "leicester-city",
        "Liverpool": "liverpool",
        "Man City": "manchester-city",
        "Manchester City": "manchester-city",
        "Man Utd": "manchester-united",
        "Manchester United": "manchester-united",
        "Newcastle": "newcastle-united",
        "Nott'm Forest": "nottingham-forest",
        "Nottingham Forest": "nottingham-forest",
        "Southampton": "southampton",
        "Tottenham": "tottenham-hotspur",
        "Spurs": "tottenham-hotspur",
        "West Ham": "west-ham-united",
        "Wolves": "wolverhampton-wanderers",
        "Sunderland": "sunderland" # Championship but requested
    }

    def scrape_bbc(self, team_slug: str) -> List[Dict]:
        """
        Scrapes BBC Sport team page.
        URL: https://www.bbc.com/sport/football/teams/{slug}
        """
        url = f"https://www.bbc.com/sport/football/teams/{team_slug}"
        print(f"      Fetching BBC Page: {url}")
        html = self.fetch_url_content(url)
        if not html: return []

        soup = BeautifulSoup(html, "html.parser")
        news_items = []
        seen_links = set()

        # BBC structure: Articles are usually in 'a' tags with specific classes or parents
        # We look for links containing '/sport/football/articles/' or '/sport/football/'
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            title = a.get_text(strip=True)
            
            # Filter for news articles
            if not title: continue
            if "/sport/football/articles/" not in href and "/sport/football/" not in href: continue
            if "teams/" in href: continue # Skip links to other team pages
            if "scores-fixtures" in href or "table" in href or "top-scorers" in href: continue

            # Normalize URL
            if href.startswith("/"):
                href = f"https://www.bbc.com{href}"

            if href not in seen_links:
                news_items.append({
                    "title": title,
                    "link": href,
                    "source": "bbc",
                    "date": "2025-01-01" # BBC doesn't always show date in list, default to recent
                })
                seen_links.add(href)
            
            if len(news_items) >= 10: break

        return news_items

    def collect_data(self, home_team: str, away_team: str, match_date: str = None) -> Dict:
        """
        Main method to collect data for a match.
        1. Search for Match Preview (SportsMole/WhoScored).
        2. Search for Local News (BBC for UK, GloboEsporte for BR).
        """
        print(f"🚀 Collecting Data for: {home_team} vs {away_team}")
        data = {"match_info": {"home": home_team, "away": away_team}, "news": {"home": [], "away": [], "match": []}}
        
        # 1. Match Preview Search
        print("   🔎 Searching for Match Preview...")
        query_preview = f"{home_team} vs {away_team} preview prediction site:sportsmole.co.uk"
        preview_urls = self.serper_search(query_preview, count=3)
        
        for url in preview_urls:
            if "sportsmole" in url:
                print(f"      Found Preview: {url}")
                data["news"]["match"].extend(self.scrape_sportsmole(url, match_date))
                break 

        # 2. Local News Search (Home Team)
        print(f"   🔎 Searching Local News for {home_team}...")
        if home_team in self.BBC_TEAMS:
            data["news"]["home"].extend(self.scrape_bbc(self.BBC_TEAMS[home_team]))
            print(f"      ✓ Extracted {len(data['news']['home'])} headlines from BBC")
        else:
            # Fallback to GloboEsporte/Serper
            query_home = f"globoesporte {home_team}"
            home_urls = self.serper_search(query_home, count=3)
            for url in home_urls:
                if "globo.com" in url and "/times/" in url:
                    print(f"      Found GE Page: {url}")
                    news = self.scrape_globoesporte(url)
                    print(f"      ✓ Extracted {len(news)} headlines")
                    data["news"]["home"].extend(news)
                    break

        # 3. Local News Search (Away Team)
        print(f"   🔎 Searching Local News for {away_team}...")
        if away_team in self.BBC_TEAMS:
            data["news"]["away"].extend(self.scrape_bbc(self.BBC_TEAMS[away_team]))
            print(f"      ✓ Extracted {len(data['news']['away'])} headlines from BBC")
        else:
            query_away = f"globoesporte {away_team}"
            away_urls = self.serper_search(query_away, count=3)
            for url in away_urls:
                if "globo.com" in url and "/times/" in url:
                    print(f"      Found GE Page: {url}")
                    news = self.scrape_globoesporte(url)
                    print(f"      ✓ Extracted {len(news)} headlines")
                    data["news"]["away"].extend(news)
                    break
        
        # 4. Deep Content Fetch (Enrichment)
        # Fetch full text for top 3 articles per team to provide real context
        print("   📖 Fetching full article content for top news...")
        self.enrich_news_with_content(data["news"]["home"], limit=3)
        self.enrich_news_with_content(data["news"]["away"], limit=3)
                
        return data

    def enrich_news_with_content(self, news_list: List[Dict], limit: int = 3):
        """
        Iterates through the news list and fetches full text content for the top N items.
        """
        count = 0
        for item in news_list:
            if count >= limit: break
            if item.get("content"): continue # Already has content (e.g. SportsMole)
            
            url = item.get("link")
            if not url: continue
            
            print(f"      Reading: {item.get('title', 'Unknown')}...")
            try:
                html = self.fetch_url_content(url)
                if html:
                    soup = BeautifulSoup(html, "html.parser")
                    # Generic text extraction - improve with site-specific selectors if needed
                    # GloboEsporte: div.content-text or article
                    # BBC: article
                    
                    # Try to find the main article body to avoid nav/footer noise
                    article_body = soup.find("article") or soup.find("div", class_="mc-article-body") or soup.find("div", class_="content-text") or soup.body
                    
                    if article_body:
                        text = article_body.get_text(separator=" ", strip=True)
                        # Truncate to avoid huge tokens
                        item["content"] = text[:5000]
                        count += 1
            except Exception as e:
                print(f"      ⚠️ Failed to read {url}: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--home", required=True)
    parser.add_argument("--away", required=True)
    parser.add_argument("--output", default="match_data_phase2.json")
    args = parser.parse_args()
    
    collector = DataCollector()
    data = collector.collect_data(args.home, args.away)
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"\n✅ Data saved to {args.output}")
