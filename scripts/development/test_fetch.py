#!/usr/bin/env python3
"""Quick test to verify URL fetching works"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from master_orchestrator import YudorOrchestrator

def main():
    orchestrator = YudorOrchestrator()

    # Load match data
    with open(orchestrator.config.BASE_DIR / "match_data_v29.json") as f:
        data = json.load(f)

    # Test with Valencia vs Levante (has good URLs)
    match_id = "ValenciavsLevante_21112025"
    match_data = data.get(match_id)

    if not match_data:
        print(f"Match {match_id} not found")
        return

    print(f"Testing fetch for: {match_id}")
    print(f"URLs available: {list(match_data.get('urls', {}).keys())}")
    print()

    # Fetch content
    fetched = orchestrator.fetch_all_match_content(match_data)

    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)

    for source, content_data in fetched.items():
        print(f"\n{source}:")
        print(f"  URL: {content_data['url']}")
        print(f"  Content length: {len(content_data['content'])} chars")
        print(f"  Preview: {content_data['content'][:200]}...")

if __name__ == "__main__":
    main()
