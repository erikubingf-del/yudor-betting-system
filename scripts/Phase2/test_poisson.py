import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.Phase2.phase2_orchestrator import Phase2Orchestrator

def test_poisson():
    print("🚀 Testing Poisson Model Integration")
    
    # Initialize Orchestrator
    orchestrator = Phase2Orchestrator(league="Brasileirão", season="2025")
    
    # Define Match
    matches = [
        {"home": "Fluminense", "away": "Sao Paulo", "date": "2025-11-27"}
    ]
    
    # Run
    results = orchestrator.process_matches(matches)
    
    # Check results
    res = results[0]
    poisson = res.get("analysis", {}).get("poisson", {})
    medallion = res.get("analysis", {}).get("medallion", {})
    
    if poisson:
        print("\n✅ Poisson Model Calculated Successfully!")
        print(poisson.get("summary", "No Summary"))
    else:
        print("\n❌ Poisson Model Missing!")
        
    if medallion:
        print("\n✅ Medallion Engine Calculated Successfully!")
        print(medallion.get("summary", "No Summary"))
    else:
        print("\n❌ Medallion Engine Missing!")
        
    consensus = res.get("analysis", {}).get("consensus", {})
    if consensus:
        print("\n⚖️ Consensus & Veto Check:")
        print(json.dumps(consensus, indent=2))
    else:
        print("\n❌ Consensus Data Missing!")

if __name__ == "__main__":
    test_poisson()
