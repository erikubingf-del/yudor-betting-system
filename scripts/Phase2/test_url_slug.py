import requests
from bs4 import BeautifulSoup
import json

def check_url(url):
    print(f"Checking: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    resp = requests.get(url, headers=headers, allow_redirects=True)
    print(f"Status: {resp.status_code}")
    print(f"Final URL: {resp.url}")
    if resp.history:
        print(f"Redirects: {[r.url for r in resp.history]}")
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    next_data = soup.find('script', {'id': '__NEXT_DATA__'})
    if next_data:
        data = json.loads(next_data.string)
        props = data.get('props', {}).get('pageProps', {})
        print(f"Keys: {list(props.keys())}")
        if 'content' in props:
            print("✅ Content found!")
        else:
            print("❌ Content missing.")
    else:
        print("❌ NEXT_DATA not found.")

check_url("https://www.fotmob.com/matches/4732809")
check_url("https://www.fotmob.com/matches/red-bull-bragantino-vs-fortaleza/4732809")
