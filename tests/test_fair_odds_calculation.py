#!/usr/bin/env python3
"""
Test Fair Odds Calculation

Validates that the CORRECT Yudor Fair Odds formula is working properly
"""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

def calculate_odds_at_line(pr_casa_pct: float, pr_vis_pct: float, ah_line: float) -> float:
    """CORRECT formula (from fix_yudor_fair_odds_final.py)"""
    fav_prob_pct = max(pr_casa_pct, pr_vis_pct)
    odd_ml = 100 / fav_prob_pct
    steps = (ah_line + 0.5) / 0.25

    if steps > 0:
        odds = odd_ml * (0.85 ** steps)
    elif steps < 0:
        odds = odd_ml * (1.15 ** abs(steps))
    else:
        odds = odd_ml

    return round(odds, 2)


def test_balanced_match():
    """Test balanced match (36.2% vs 33.5%)"""
    pr_casa_pct = 33.5
    pr_vis_pct = 36.2
    ah_line = -0.25

    result = calculate_odds_at_line(pr_casa_pct, pr_vis_pct, ah_line)
    expected = 2.35  # 100/36.2 * 0.85

    assert abs(result - expected) < 0.01, f"Expected {expected}, got {result}"
    print(f"✅ test_balanced_match: {result}")


def test_strong_favorite():
    """Test strong favorite (60.8% vs 20%)"""
    pr_casa_pct = 60.8
    pr_vis_pct = 20.0
    ah_line = -1.25

    result = calculate_odds_at_line(pr_casa_pct, pr_vis_pct, ah_line)
    # Moneyline: 100/60.8 = 1.64
    # Steps from -0.5 to -1.25: -3 steps
    # 1.64 * 1.15^3 = 2.49
    expected = 2.49

    assert abs(result - expected) < 0.05, f"Expected ~{expected}, got {result}"
    print(f"✅ test_strong_favorite: {result}")


def test_even_match():
    """Test even match (33% vs 33%)"""
    pr_casa_pct = 33.0
    pr_vis_pct = 33.0
    ah_line = 0.0

    result = calculate_odds_at_line(pr_casa_pct, pr_vis_pct, ah_line)
    # Moneyline: 100/33 = 3.03
    # Steps from -0.5 to 0.0: +2 steps
    # 3.03 * 0.85^2 = 2.19
    expected = 2.19

    assert abs(result - expected) < 0.05, f"Expected ~{expected}, got {result}"
    print(f"✅ test_even_match: {result}")


def test_weak_favorite():
    """Test weak favorite (35% vs 30%)"""
    pr_casa_pct = 35.0
    pr_vis_pct = 30.0
    ah_line = -0.5

    result = calculate_odds_at_line(pr_casa_pct, pr_vis_pct, ah_line)
    # At -0.5, odds = moneyline
    expected = 100 / 35.0  # 2.86

    assert abs(result - expected) < 0.05, f"Expected ~{expected}, got {result}"
    print(f"✅ test_weak_favorite: {result}")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING FAIR ODDS CALCULATION")
    print("=" * 60)

    try:
        test_balanced_match()
        test_strong_favorite()
        test_even_match()
        test_weak_favorite()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
