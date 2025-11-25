#!/usr/bin/env python3
"""
Check for potential FLIP candidates in existing analyses
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ANALYSIS_DIR = BASE_DIR / "analysis_history"
CONSOLIDATED_DIR = BASE_DIR / "consolidated_data"

print("="*80)
print("🔍 CHECKING FOR FLIP CANDIDATES")
print("="*80)
print()

# FLIP Criteria:
# 1. R ≥ 0.25
# 2. RBR > 0.25 (we'll skip this for now as it's not calculated)
# 3. Edge for underdog ≥ 8% (need market odds - skip for now)
# 4. CS_final of flip side ≥ 65

analysis_files = sorted(ANALYSIS_DIR.glob("*_analysis.json"))

print(f"📋 Analyzing {len(analysis_files)} matches...\n")

potential_flips = []

for analysis_file in analysis_files:
    with open(analysis_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    yudor = data.get("yudor_analysis", {})
    match_info = data.get("match_info", {})
    
    r_score = yudor.get("r_score", 0)
    cs_final = yudor.get("cs_final", 0)
    decision = yudor.get("decision", "")
    ah_line = yudor.get("yudor_ah_fair", 0)
    
    raw_casa = yudor.get("raw_casa", 0)
    raw_vis = yudor.get("raw_vis", 0)
    
    # Determine favorite and underdog
    if raw_casa > raw_vis:
        favorite = "home"
        underdog = "away"
        favorite_team = match_info.get("home", "")
        underdog_team = match_info.get("away", "")
    else:
        favorite = "away"
        underdog = "home"
        favorite_team = match_info.get("away", "")
        underdog_team = match_info.get("home", "")
    
    # Check criteria 1 and 4
    if r_score >= 0.25 and cs_final >= 65:
        potential_flips.append({
            "match": f"{match_info.get('home')} vs {match_info.get('away')}",
            "league": match_info.get("league"),
            "date": match_info.get("date"),
            "r_score": r_score,
            "cs_final": cs_final,
            "ah_line": ah_line,
            "decision": decision,
            "favorite": favorite_team,
            "underdog": underdog_team,
            "raw_casa": raw_casa,
            "raw_vis": raw_vis,
            "match_id": yudor.get("match_id", "")
        })

print(f"🎯 POTENTIAL FLIP CANDIDATES: {len(potential_flips)}")
print("="*80)
print()

if potential_flips:
    print("Matches meeting criteria (R ≥ 0.25, CS ≥ 65):\n")
    for idx, match in enumerate(potential_flips, 1):
        print(f"{idx}. {match['match']} ({match['league']})")
        print(f"   Date: {match['date']}")
        print(f"   Current Decision: {match['decision']}")
        print(f"   R-Score: {match['r_score']:.3f} ✅ (≥ 0.25)")
        print(f"   CS Final: {match['cs_final']} ✅ (≥ 65)")
        print(f"   AH Line: {match['ah_line']}")
        print(f"   Favorite: {match['favorite']} (Raw: {match['raw_casa'] if match['favorite'] == match['match'].split(' vs ')[0] else match['raw_vis']}%)")
        print(f"   Underdog: {match['underdog']} (Raw: {match['raw_vis'] if match['underdog'] == match['match'].split(' vs ')[1] else match['raw_casa']}%)")
        print(f"   ⚠️  Missing: RBR calculation, Market odds for edge check")
        print()
else:
    print("✅ No matches meet the initial FLIP criteria (R ≥ 0.25 AND CS ≥ 65)")
    print()

# Summary by current decision
print("="*80)
print("📊 SUMMARY")
print("="*80)
decisions = {}
for match in potential_flips:
    dec = match['decision']
    if dec not in decisions:
        decisions[dec] = []
    decisions[dec].append(match)

if decisions:
    for decision, matches in sorted(decisions.items()):
        print(f"\n{decision}: {len(matches)} potential FLIP candidates")
        for m in matches:
            print(f"  • {m['match']}")
