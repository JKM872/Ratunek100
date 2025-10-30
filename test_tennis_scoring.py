#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎾 TEST: Tennis Scoring - Dlaczego pokazuje 0?

Ten skrypt testuje dokładnie co się dzieje z tennis scoring.
"""

import sys

print("=" * 60)
print("🎾 TEST: TENNIS SCORING ANALYSIS")
print("=" * 60)

# Test 1: Sprawdź czy moduł tennis_advanced_v3 istnieje
print("\n[Test 1] Sprawdzanie modułu tennis_advanced_v3...")
try:
    from tennis_advanced_v3 import TennisMatchAnalyzerV3
    print("✅ Moduł tennis_advanced_v3 zaimportowany pomyślnie")
    analyzer = TennisMatchAnalyzerV3()
    print(f"✅ Analyzer utworzony: {type(analyzer)}")
except ImportError as e:
    print(f"❌ BŁĄD: Nie można zaimportować modułu: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ BŁĄD przy tworzeniu analyzera: {e}")
    sys.exit(1)

# Test 2: Przykładowe dane H2H (jak w prawdziwym scrapingu)
print("\n[Test 2] Symulacja analizy meczu tenisowego...")
h2h_matches = [
    {'date': '2025-09-15', 'winner': 'player_a', 'score': '6-4, 6-2', 'surface': 'hard'},
    {'date': '2025-08-20', 'winner': 'player_a', 'score': '7-5, 6-3', 'surface': 'hard'},
    {'date': '2025-07-10', 'winner': 'player_b', 'score': '6-7, 6-3, 7-6', 'surface': 'clay'},
]

form_a = [
    {'result': 'W', 'date': '2025-10-25', 'opponent_rank': 50},
    {'result': 'W', 'date': '2025-10-20', 'opponent_rank': 45},
    {'result': 'L', 'date': '2025-10-15', 'opponent_rank': 30},
]

form_b = [
    {'result': 'L', 'date': '2025-10-26', 'opponent_rank': 40},
    {'result': 'W', 'date': '2025-10-21', 'opponent_rank': 60},
    {'result': 'L', 'date': '2025-10-16', 'opponent_rank': 35},
]

surface_stats_a = {
    'hard': {'wins': 15, 'losses': 5, 'win_rate': 0.75}
}

surface_stats_b = {
    'hard': {'wins': 10, 'losses': 10, 'win_rate': 0.50}
}

print(f"   H2H matches: {len(h2h_matches)}")
print(f"   Form A: {len(form_a)} matches")
print(f"   Form B: {len(form_b)} matches")
print(f"   Surface: hard")

try:
    analysis = analyzer.analyze_match(
        player_a="Novak Djokovic",
        player_b="Roger Federer",
        h2h_matches=h2h_matches,
        form_a=form_a,
        form_b=form_b,
        surface='hard',
        surface_stats_a=surface_stats_a,
        surface_stats_b=surface_stats_b,
        tournament_info="ATP Masters 1000"
    )
    
    print("\n✅ ANALIZA ZAKOŃCZONA SUKCESEM!")
    print(f"   Total Score: {analysis.get('total_score', 'N/A')}")
    print(f"   Qualifies: {analysis.get('qualifies', False)}")
    print(f"   Favorite: {analysis.get('details', {}).get('favorite', 'unknown')}")
    print(f"   Breakdown: {analysis.get('breakdown', {})}")
    
    if analysis.get('total_score', 0) == 0:
        print("\n⚠️  PROBLEM: Scoring = 0!")
        print("   Sprawdzam breakdown...")
        breakdown = analysis.get('breakdown', {})
        for key, value in breakdown.items():
            print(f"      {key}: {value}")
    else:
        print(f"\n✅ Scoring działa! Wartość: {analysis['total_score']}")

except Exception as e:
    print(f"\n❌ BŁĄD podczas analyze_match: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Sprawdź edge cases
print("\n[Test 3] Edge case - brak danych H2H...")
try:
    analysis_empty = analyzer.analyze_match(
        player_a="Player X",
        player_b="Player Y",
        h2h_matches=[],  # PUSTE H2H
        form_a=[],
        form_b=[],
        surface=None,
        surface_stats_a={},
        surface_stats_b={},
        tournament_info=""
    )
    
    score = analysis_empty.get('total_score', 0)
    print(f"   Score (empty H2H): {score}")
    
    if score == 0:
        print("   ⚠️  PRAWDOPODOBNA PRZYCZYNA: Brak danych H2H = scoring 0")
    
except Exception as e:
    print(f"   ❌ Błąd: {e}")

print("\n" + "=" * 60)
print("🎯 PODSUMOWANIE:")
print("=" * 60)
print("1. Sprawdź czy prawdziwe mecze mają dane H2H")
print("2. Sprawdź format danych przekazywanych do analyzera")
print("3. Sprawdź czy tennis_advanced_v3 prawidłowo liczy scoring")
print("=" * 60)
