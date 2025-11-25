#!/usr/bin/env python3
"""
Q6 Formation Scoring Logic
Tactical formation matchup analysis for Yudor v5.3

This module provides intelligent scoring based on formation matchups
"""

from typing import Dict, Tuple


# Formation matchup matrix
# Key: (home_formation, away_formation)
# Value: (home_score, away_score, reasoning)
FORMATION_MATCHUPS = {
    # 4-3-3 matchups
    ('4-3-3', '3-5-2'): (5, 3, "Width advantage exploits wing-backs", "Midfield control partially counters"),
    ('4-3-3', '4-4-2'): (4, 3, "Width and midfield fluidity", "Compact defense limits space"),
    ('4-3-3', '4-2-3-1'): (3, 3, "Balanced matchup", "Balanced matchup"),
    ('4-3-3', '3-4-3'): (3, 4, "Wing battle neutral", "Better midfield coverage"),
    ('4-3-3', '5-3-2'): (5, 2, "Dominates wide areas", "Defensive solidity"),

    # 3-5-2 matchups
    ('3-5-2', '4-4-2'): (5, 3, "Midfield numerical advantage", "Compact shape"),
    ('3-5-2', '4-3-3'): (3, 5, "Midfield control partially counters", "Width advantage exploits wing-backs"),
    ('3-5-2', '4-2-3-1'): (4, 3, "Midfield dominance", "Central control"),
    ('3-5-2', '5-4-1'): (4, 2, "More attacking threat", "Defensive solidity"),

    # 4-4-2 matchups
    ('4-4-2', '4-3-3'): (3, 4, "Compact defense limits space", "Width and midfield fluidity"),
    ('4-4-2', '3-5-2'): (3, 5, "Compact shape", "Midfield numerical advantage"),
    ('4-4-2', '4-2-3-1'): (3, 4, "Traditional stability", "Modern flexibility"),
    ('4-4-2', '4-4-2'): (0, 0, "Mirror matchup", "Mirror matchup"),

    # 4-2-3-1 matchups
    ('4-2-3-1', '4-3-3'): (3, 3, "Balanced matchup", "Balanced matchup"),
    ('4-2-3-1', '3-5-2'): (3, 4, "Central control", "Midfield dominance"),
    ('4-2-3-1', '4-4-2'): (4, 3, "Modern flexibility", "Traditional stability"),
    ('4-2-3-1', '4-2-3-1'): (0, 0, "Mirror matchup", "Mirror matchup"),
    ('4-2-3-1', '5-3-2'): (4, 3, "Attacking creativity", "Defensive numbers"),

    # 3-4-3 matchups
    ('3-4-3', '4-3-3'): (4, 3, "Better midfield coverage", "Wing battle neutral"),
    ('3-4-3', '4-4-2'): (4, 3, "Width and midfield balance", "Compact central defense"),
    ('3-4-3', '5-3-2'): (5, 3, "Attacking intent", "Defensive shell"),

    # 5-3-2 / 5-4-1 matchups (defensive formations)
    ('5-3-2', '4-3-3'): (2, 5, "Defensive solidity", "Dominates wide areas"),
    ('5-3-2', '3-5-2'): (2, 4, "Defensive solidity", "More attacking threat"),
    ('5-4-1', '4-2-3-1'): (2, 4, "Defensive block", "Creative superiority"),
}


def normalize_formation(formation: str) -> str:
    """
    Normalize formation string

    Args:
        formation: Formation string (e.g., "4-3-3", "433", "4-1-2-1-2")

    Returns:
        Normalized formation (e.g., "4-3-3")
    """
    if not formation or formation == '0':
        return '0'

    # Remove spaces
    formation = formation.strip().replace(' ', '')

    # Add dashes if missing
    if '-' not in formation and len(formation) >= 3:
        # Convert "433" to "4-3-3"
        formation = '-'.join(formation)

    # Simplify complex formations to basic shape
    # e.g., "4-1-2-1-2" -> "4-4-2" (4 defenders, 4 midfielders, 2 forwards)
    parts = formation.split('-')
    if len(parts) > 3:
        # Combine middle numbers
        defenders = parts[0]
        midfielders = str(sum(int(x) for x in parts[1:-1]))
        forwards = parts[-1]
        formation = f"{defenders}-{midfielders}-{forwards}"

    return formation


def score_formation_matchup(home_formation: str, away_formation: str) -> Dict:
    """
    Score formation matchup using tactical analysis

    Args:
        home_formation: Home team formation (e.g., "4-3-3")
        away_formation: Away team formation (e.g., "3-5-2")

    Returns:
        Dict with scores and reasoning
    """
    # Normalize formations
    home = normalize_formation(home_formation)
    away = normalize_formation(away_formation)

    # Check for missing formations
    if home == '0' or away == '0':
        return {
            'home_score': 0,
            'away_score': 0,
            'home_reasoning': "No tactical formations confirmed in sources → +0",
            'away_reasoning': "No tactical formations confirmed in sources → +0",
            'sources': ['No formation data available']
        }

    # Check for exact matchup in matrix
    key = (home, away)
    if key in FORMATION_MATCHUPS:
        home_score, away_score, home_reason, away_reason = FORMATION_MATCHUPS[key]
        return {
            'home_score': home_score,
            'away_score': away_score,
            'home_reasoning': f"{home} vs {away}: {home_reason} → +{home_score}",
            'away_reasoning': f"{away} vs {home}: {away_reason} → +{away_score}",
            'sources': ['Formation matchup analysis']
        }

    # Check for reverse matchup
    reverse_key = (away, home)
    if reverse_key in FORMATION_MATCHUPS:
        away_score, home_score, away_reason, home_reason = FORMATION_MATCHUPS[reverse_key]
        return {
            'home_score': home_score,
            'away_score': away_score,
            'home_reasoning': f"{home} vs {away}: {home_reason} → +{home_score}",
            'away_reasoning': f"{away} vs {home}: {away_reason} → +{away_score}",
            'sources': ['Formation matchup analysis']
        }

    # Check for same formation (mirror matchup)
    if home == away:
        return {
            'home_score': 0,
            'away_score': 0,
            'home_reasoning': f"{home} vs {away}: Mirror matchup → +0",
            'away_reasoning': f"{away} vs {home}: Mirror matchup → +0",
            'sources': ['Formation matchup analysis']
        }

    # Default for unknown matchups (both get neutral score)
    return {
        'home_score': 2,
        'away_score': 2,
        'home_reasoning': f"{home} vs {away}: Unknown matchup, neutral → +2",
        'away_reasoning': f"{away} vs {home}: Unknown matchup, neutral → +2",
        'sources': ['Formation matchup analysis (default)']
    }


def get_formation_characteristics(formation: str) -> Dict:
    """
    Get tactical characteristics of a formation

    Args:
        formation: Formation string

    Returns:
        Dict with formation characteristics
    """
    formation = normalize_formation(formation)

    characteristics = {
        '4-3-3': {
            'style': 'Attacking',
            'width': 'High',
            'midfield_control': 'Medium',
            'defensive_solidity': 'Medium',
            'pressing_ability': 'High'
        },
        '3-5-2': {
            'style': 'Balanced',
            'width': 'Medium (wing-backs)',
            'midfield_control': 'High',
            'defensive_solidity': 'High',
            'pressing_ability': 'Medium'
        },
        '4-4-2': {
            'style': 'Traditional',
            'width': 'Low',
            'midfield_control': 'Medium',
            'defensive_solidity': 'High',
            'pressing_ability': 'Medium'
        },
        '4-2-3-1': {
            'style': 'Modern Balanced',
            'width': 'Medium',
            'midfield_control': 'High',
            'defensive_solidity': 'Medium',
            'pressing_ability': 'High'
        },
        '3-4-3': {
            'style': 'Attacking',
            'width': 'High',
            'midfield_control': 'Medium',
            'defensive_solidity': 'Medium',
            'pressing_ability': 'High'
        },
        '5-3-2': {
            'style': 'Defensive',
            'width': 'Low',
            'midfield_control': 'Low',
            'defensive_solidity': 'Very High',
            'pressing_ability': 'Low'
        },
        '5-4-1': {
            'style': 'Very Defensive',
            'width': 'Very Low',
            'midfield_control': 'Medium',
            'defensive_solidity': 'Very High',
            'pressing_ability': 'Very Low'
        }
    }

    return characteristics.get(formation, {
        'style': 'Unknown',
        'width': 'Unknown',
        'midfield_control': 'Unknown',
        'defensive_solidity': 'Unknown',
        'pressing_ability': 'Unknown'
    })


def test_q6_scoring():
    """Test Q6 formation scoring"""
    print("\n" + "="*80)
    print("Testing Q6 Formation Scoring")
    print("="*80)

    test_cases = [
        ("4-3-3", "3-5-2", "Barcelona vs Athletic"),
        ("3-5-2", "4-4-2", "Chelsea vs Man Utd"),
        ("4-2-3-1", "4-2-3-1", "Real Madrid vs Bayern"),
        ("4-3-3", "5-3-2", "Liverpool vs Atletico"),
        ("0", "4-3-3", "Unknown vs Barcelona"),
    ]

    for home_form, away_form, match in test_cases:
        result = score_formation_matchup(home_form, away_form)

        print(f"\n{match}")
        print(f"Formations: {home_form} vs {away_form}")
        print(f"Home Score: +{result['home_score']} - {result['home_reasoning']}")
        print(f"Away Score: +{result['away_score']} - {result['away_reasoning']}")
        print("-" * 80)

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    test_q6_scoring()
