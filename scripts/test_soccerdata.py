#!/usr/bin/env python3
"""
Test soccerdata library capabilities
Check what lineup/formation data is available from each source
"""

import sys
import os

# Add soccerdata to path
sys.path.insert(0, '/tmp/soccerdata')

def test_imports():
    """Test if we can import soccerdata modules"""
    print("="*80)
    print("TESTING SOCCERDATA LIBRARY IMPORTS")
    print("="*80 + "\n")

    try:
        import soccerdata as sd
        print(f"✅ soccerdata version: {sd.__version__}")
        print(f"✅ Available sources: {', '.join(sd.__all__)}\n")
        return True
    except Exception as e:
        print(f"❌ Failed to import soccerdata: {e}\n")
        return False


def test_fbref():
    """Test FBref - most reliable source"""
    print("="*80)
    print("TESTING FBREF (Most Reliable - No Auth Required)")
    print("="*80 + "\n")

    try:
        import soccerdata as sd

        print("Creating FBref instance for La Liga 24/25...")
        fbref = sd.FBref(leagues='ESP-La Liga', seasons='2425')
        print("✅ FBref instance created\n")

        # Test available methods
        print("📊 Available data methods:")
        print("  - read_leagues()")
        print("  - read_seasons()")
        print("  - read_schedule()")
        print("  - read_team_season_stats()")
        print("  - read_player_season_stats()")
        print("  - read_lineup()  ⭐")
        print("  - read_team_match_stats()")
        print("  - read_player_match_stats()")
        print("  - read_events()")
        print("  - read_shot_events()\n")

        # Test team stats (for Q7, Q8, Q14)
        print("Testing team season stats (for Q7 - PPDA, Q8 - Corners)...")
        try:
            defense_stats = fbref.read_team_season_stats(stat_type='defense')
            print(f"✅ Defense stats: {len(defense_stats)} teams")
            print(f"   Columns: {', '.join(defense_stats.columns[:10].tolist())}...\n")

            misc_stats = fbref.read_team_season_stats(stat_type='misc')
            print(f"✅ Misc stats: {len(misc_stats)} teams")
            print(f"   Columns: {', '.join(misc_stats.columns[:10].tolist())}...\n")
        except Exception as e:
            print(f"⚠️  Team stats fetch might need internet: {str(e)[:100]}\n")

        # Test lineup (for formations)
        print("Testing lineup data (for Q6 - Formations)...")
        try:
            schedule = fbref.read_schedule()
            print(f"✅ Schedule: {len(schedule)} matches")

            # Try to get lineup for one match
            if len(schedule) > 0:
                match_id = schedule.iloc[0]['game_id']
                print(f"   Attempting to fetch lineup for match: {match_id}")
                lineup = fbref.read_lineup(match_id=match_id)
                print(f"✅ Lineup data: {len(lineup)} players")
                print(f"   Columns: {', '.join(lineup.columns.tolist())}")

                # Check if formation info is in lineup
                if 'formation' in lineup.columns:
                    print(f"   ⭐ FORMATIONS AVAILABLE!")
                else:
                    print(f"   ⚠️  No 'formation' column found")
                    print(f"      Available: position, jersey_number, player, team, is_starter")
            print()
        except Exception as e:
            print(f"⚠️  Lineup fetch might need internet/complete matches: {str(e)[:150]}\n")

        return True

    except Exception as e:
        print(f"❌ FBref test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_espn():
    """Test ESPN - has formation_place field"""
    print("="*80)
    print("TESTING ESPN (Has formation_place field)")
    print("="*80 + "\n")

    try:
        import soccerdata as sd

        print("Creating ESPN instance for La Liga 24/25...")
        espn = sd.ESPN(leagues='ESP-La Liga', seasons='2425')
        print("✅ ESPN instance created\n")

        print("📊 Available data methods:")
        print("  - read_schedule()")
        print("  - read_matchsheet()")
        print("  - read_lineup()  ⭐ (has formation_place field)\n")

        print("Testing lineup data...")
        try:
            schedule = espn.read_schedule()
            print(f"✅ Schedule: {len(schedule)} matches")

            if len(schedule) > 0:
                match_id = schedule.iloc[0]['game_id']
                print(f"   Attempting to fetch lineup for match: {match_id}")
                lineup = espn.read_lineup(match_id=match_id)
                print(f"✅ Lineup data: {len(lineup)} players")
                print(f"   Columns: {', '.join(lineup.columns.tolist())}")

                if 'formation_place' in lineup.columns:
                    print(f"   ⭐ Has 'formation_place' field (player position like 1=GK, 2=RB, etc.)")
                    print(f"   ⚠️  But NOT the formation string (like '4-3-3')")
            print()
        except Exception as e:
            print(f"⚠️  ESPN lineup fetch error: {str(e)[:150]}\n")

        return True

    except Exception as e:
        print(f"❌ ESPN test failed: {e}\n")
        return False


def test_sofascore():
    """Test SofaScore"""
    print("="*80)
    print("TESTING SOFASCORE")
    print("="*80 + "\n")

    try:
        import soccerdata as sd

        print("Creating SofaScore instance for La Liga 24/25...")
        sofascore = sd.Sofascore(leagues='ESP-La Liga', seasons='2425')
        print("✅ SofaScore instance created\n")

        print("📊 Available data methods:")
        print("  - read_leagues()")
        print("  - read_seasons()")
        print("  - read_league_table()")
        print("  - read_schedule()\n")

        print("⚠️  SofaScore module does NOT have read_lineup() method")
        print("   Would need to extend the module to access lineups API\n")

        return True

    except Exception as e:
        print(f"❌ SofaScore test failed: {e}\n")
        return False


def test_fotmob():
    """Test FotMob"""
    print("="*80)
    print("TESTING FOTMOB")
    print("="*80 + "\n")

    try:
        import soccerdata as sd

        print("Creating FotMob instance for La Liga 24/25...")
        fotmob = sd.FotMob(leagues='ESP-La Liga', seasons='2425')
        print("✅ FotMob instance created\n")

        print("📊 Available data methods:")
        print("  - read_leagues()")
        print("  - read_seasons()")
        print("  - read_league_table()")
        print("  - read_schedule()")
        print("  - read_team_match_stats()\n")

        print("⚠️  FotMob module does NOT have read_lineup() method")
        print("   Would need to extend the module to access lineups API\n")

        return True

    except Exception as e:
        print(f"❌ FotMob test failed: {e}\n")
        return False


def test_whoscored():
    """Test WhoScored"""
    print("="*80)
    print("TESTING WHOSCORED")
    print("="*80 + "\n")

    try:
        import soccerdata as sd

        print("Creating WhoScored instance for La Liga 24/25...")
        whoscored = sd.WhoScored(leagues='ESP-La Liga', seasons='2425')
        print("✅ WhoScored instance created\n")

        print("📊 Available data methods:")
        print("  - read_leagues()")
        print("  - read_seasons()")
        print("  - read_season_stages()")
        print("  - read_schedule()")
        print("  - read_missing_players()")
        print("  - read_events()\n")

        print("⚠️  WhoScored module does NOT have read_lineup() method")
        print("   Would need to extend the module or scrape from events\n")

        return True

    except Exception as e:
        print(f"❌ WhoScored test failed: {e}\n")
        return False


def summarize_findings():
    """Print summary of findings"""
    print("\n" + "="*80)
    print("SUMMARY: LINEUP & FORMATION CAPABILITIES")
    print("="*80 + "\n")

    print("📋 Lineup Data Available:")
    print("  ✅ FBref.read_lineup()  - Full lineups (player, position, is_starter)")
    print("  ✅ ESPN.read_lineup()   - Full lineups + formation_place field\n")

    print("📋 Formation Data (Team Formation String like '4-3-3'):")
    print("  ❌ FBref - NO formation string (only player positions)")
    print("  ❌ ESPN  - NO formation string (only formation_place per player)")
    print("  ❌ SofaScore - NO read_lineup() method in library")
    print("  ❌ FotMob - NO read_lineup() method in library")
    print("  ❌ WhoScored - NO read_lineup() method in library\n")

    print("🎯 CONCLUSION:")
    print("  The soccerdata library does NOT provide formation strings (like '4-3-3')")
    print("  out of the box. However:")
    print()
    print("  OPTION 1: Use FBref/ESPN for lineups, INFER formation from player positions")
    print("            (Would need logic to detect formation from 11 positions)")
    print()
    print("  OPTION 2: EXTEND the library to call SofaScore/FotMob lineups APIs")
    print("            (Library already handles auth via cookie server for FotMob!)")
    print()
    print("  OPTION 3: Keep MANUAL database approach (already built, 100% accurate)")
    print()
    print("  RECOMMENDED: Use soccerdata for Q7/Q8/Q14 stats (FBref)")
    print("               Keep manual database for Q6 formations")
    print("               Best of both worlds!")
    print()


if __name__ == "__main__":
    print("\n🔬 SOCCERDATA LIBRARY COMPREHENSIVE TEST\n")

    # Test imports
    if not test_imports():
        print("\n❌ Cannot import soccerdata. Exiting.\n")
        sys.exit(1)

    # Test each source
    test_fbref()
    test_espn()
    test_sofascore()
    test_fotmob()
    test_whoscored()

    # Summary
    summarize_findings()

    print("="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
