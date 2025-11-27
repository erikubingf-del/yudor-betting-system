import json
import os
from typing import Dict, List

class ContextAnalyzer:
    """
    Analyzes match context from scraped data (news titles, previews).
    Returns a sentiment score (-1.0 to 1.0).
    """
    
    def __init__(self, data_file: str = "match_data_v29.json"):
        self.data_file = data_file
        self.data = self._load_data()
        
        # Simple keyword dictionaries
        self.positive_keywords = [
            "boost", "return", "fit", "ready", "confidence", "strong", 
            "winning streak", "unbeaten", "top form", "key player back"
        ]
        self.negative_keywords = [
            "injury", "injured", "out", "missing", "doubt", "crisis", 
            "suspended", "ban", "loss", "poor form", "struggle", "sacked"
        ]

    def _load_data(self) -> Dict:
        if not os.path.exists(self.data_file):
            # print(f"Warning: Data file {self.data_file} not found.")
            return {}
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}

    def get_context_score(self, home_team: str, away_team: str) -> float:
        """
        Calculates a context score for the match.
        Positive = Favors Home
        Negative = Favors Away
        """
        # Find match in data (naive search by name)
        match_entry = None
        for match_id, entry in self.data.items():
            m_home = entry.get("match_info", {}).get("home", "").lower()
            m_away = entry.get("match_info", {}).get("away", "").lower()
            
            if home_team.lower() in m_home and away_team.lower() in m_away:
                match_entry = entry
                break
        
        if not match_entry:
            return 0.0

        home_news = match_entry.get("news", {}).get("home", [])
        away_news = match_entry.get("news", {}).get("away", [])
        
        home_sentiment = self._analyze_sentiment(home_news)
        away_sentiment = self._analyze_sentiment(away_news)
        
        # Net score: (Home Sentiment - Away Sentiment)
        # Clamped between -1 and 1
        net_score = home_sentiment - away_sentiment
        return max(-1.0, min(1.0, net_score))

    def analyze_text(self, text: str) -> float:
        """
        Analyzes a raw string of text (e.g. from web search) and returns a sentiment score.
        """
        score = 0.0
        text = text.lower()
        
        # Count keyword occurrences
        for word in self.positive_keywords:
            if word in text:
                score += 0.2
        
        for word in self.negative_keywords:
            if word in text:
                score -= 0.2
                
        # Normalize roughly between -1.0 and 1.0
        return max(-1.0, min(1.0, score))

    def _analyze_sentiment(self, news_items: List[Dict]) -> float:
        score = 0.0
        if not news_items:
            return 0.0
            
        for item in news_items:
            # Combine Title and Content for analysis
            text = item.get("title", "") + " " + item.get("content", "")
            text = text.lower()
            
            # Title matches are worth more (0.3), Content matches (0.1)
            # But for simplicity, we'll just scan the whole text with the standard weight
            # Maybe cap the contribution of a single article to avoid skew
            
            article_score = 0
            for word in self.positive_keywords:
                if word in text:
                    article_score += 0.2
            
            for word in self.negative_keywords:
                if word in text:
                    article_score -= 0.2
            
            # Cap single article impact
            article_score = max(-0.6, min(0.6, article_score))
            score += article_score
                    
        # Normalize roughly
        return max(-1.0, min(1.0, score))

if __name__ == "__main__":
    # Test
    analyzer = ContextAnalyzer()
    # Mock data test would go here
    print("ContextAnalyzer ready.")
