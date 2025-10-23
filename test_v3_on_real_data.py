"""
Test Tennis Scoring V3 na prawdziwych danych z CSV
Porównanie V2 vs V3
"""

import csv
import json
from tennis_advanced import TennisMatchAnalyzer
from tennis_advanced_v3 import TennisMatchAnalyzerV3
from datetime import datetime

# Wczytaj dane
with open('outputs/livesport_h2h_2025-10-05_tennis_EMAIL.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    matches = list(reader)

print("🎾 TEST TENNIS SCORING V3 vs V2")
print("=" * 80)
print()

# Wybierz 5 meczów do szczegółowego porównania
test_matches = [
    matches[0],  # Auger-Aliassime vs De Jong (V2: 58 pkt)
    matches[1],  # Majchrzak vs De Minaur (V2: 28 pkt)
    matches[7],  # Zverev vs Rinderknech (V2: 22 pkt)
    matches[8],  # Davydovich vs Miedwiediew (V2: 13 pkt)
    matches[9],  # Jastremska vs Siegemund (V2: 73 pkt)
]

analyzer_v2 = TennisMatchAnalyzer()
analyzer_v3 = TennisMatchAnalyzerV3()

for i, match in enumerate(test_matches, 1):
    print(f"{'='*80}")
    print(f"MECZ #{i}: {match['home_team']} vs {match['away_team']}")
    print(f"{'='*80}")
    print()
    
    # Parsuj dane H2H
    h2h_data_v2 = {
        'player_a_wins': int(match.get('home_wins_in_h2h_last5', 0)),
        'player_b_wins': int(match.get('away_wins_in_h2h', 0)),
        'total': int(match.get('h2h_count', 0))
    }
    
    # Przygotuj dane H2H dla V3 (z datami)
    h2h_matches_v3 = []
    if match['h2h_last5']:
        try:
            h2h_list = json.loads(match['h2h_last5'].replace("'", '"'))
            for h2h in h2h_list:
                winner = 'player_a' if h2h.get('winner') == 'home' else 'player_b'
                h2h_matches_v3.append({
                    'date': h2h.get('date', ''),
                    'winner': winner,
                    'score': h2h.get('score', ''),
                    'surface': match.get('surface', '')
                })
        except:
            pass
    
    # Parsuj formę
    form_a_v2 = []
    form_b_v2 = []
    if match['form_a']:
        try:
            form_a_v2 = json.loads(match['form_a'].replace("'", '"'))
        except:
            pass
    if match['form_b']:
        try:
            form_b_v2 = json.loads(match['form_b'].replace("'", '"'))
        except:
            pass
    
    # Przygotuj formę dla V3 (z dodatkowymi danymi - symulowane)
    form_a_v3 = []
    form_b_v3 = []
    
    # Symuluj rozszerzone dane formy (w prawdziwej implementacji scraper zbierze to)
    for i, result in enumerate(form_a_v2):
        form_a_v3.append({
            'result': result,
            'date': f'0{10-i}.09.25',  # Symulowane daty
            'opponent_rank': 50,  # Symulowany ranking przeciwnika
            'score': '2-0' if result == 'W' else '0-2'
        })
    
    for i, result in enumerate(form_b_v2):
        form_b_v3.append({
            'result': result,
            'date': f'0{10-i}.09.25',
            'opponent_rank': 50,
            'score': '2-0' if result == 'W' else '0-2'
        })
    
    # Ranking (dla V2)
    ranking_a = float(match.get('ranking_a', 0)) if match.get('ranking_a') else None
    ranking_b = float(match.get('ranking_b', 0)) if match.get('ranking_b') else None
    
    # Surface stats (symulowane - w prawdziwej implementacji scraper zbierze to)
    surface = match.get('surface', 'hard')
    
    # Symuluj statystyki nawierzchni na podstawie formy
    wins_a = sum(1 for r in form_a_v2 if r == 'W')
    wins_b = sum(1 for r in form_b_v2 if r == 'W')
    
    win_rate_a = wins_a / len(form_a_v2) if form_a_v2 else 0.5
    win_rate_b = wins_b / len(form_b_v2) if form_b_v2 else 0.5
    
    # Dla V2 - prosty dict z win rate
    surface_stats_a_v2 = {
        surface: win_rate_a
    }
    
    surface_stats_b_v2 = {
        surface: win_rate_b
    }
    
    # Dla V3 - rozszerzony dict z dodatkowymi danymi
    surface_stats_a_v3 = {
        surface: {
            'wins': wins_a * 2,  # Symulacja
            'total': len(form_a_v2) * 2,
            'win_rate': win_rate_a,
            'recent_form': form_a_v2[-5:] if form_a_v2 else []
        }
    }
    
    surface_stats_b_v3 = {
        surface: {
            'wins': wins_b * 2,
            'total': len(form_b_v2) * 2,
            'win_rate': win_rate_b,
            'recent_form': form_b_v2[-5:] if form_b_v2 else []
        }
    }
    
    # =========================================
    # ANALIZA V2
    # =========================================
    print("📊 V2 SCORING (STARY):")
    print("-" * 40)
    
    result_v2 = analyzer_v2.analyze_match(
        player_a=match['home_team'],
        player_b=match['away_team'],
        h2h_data=h2h_data_v2,
        ranking_a=ranking_a,
        ranking_b=ranking_b,
        form_a=form_a_v2,
        form_b=form_b_v2,
        surface=surface,
        surface_stats_a=surface_stats_a_v2,
        surface_stats_b=surface_stats_b_v2
    )
    
    breakdown_v2 = result_v2['breakdown']
    print(f"H2H:        {breakdown_v2['h2h_score']:+6.1f} / 50.0 pkt")
    print(f"Ranking:    {breakdown_v2['ranking_score']:+6.1f} / 25.0 pkt")
    print(f"Forma:      {breakdown_v2['form_score']:+6.1f} / 15.0 pkt")
    print(f"Surface:    {breakdown_v2['surface_score']:+6.1f} / 10.0 pkt")
    print(f"{'-'*40}")
    print(f"RAZEM:      {result_v2['total_score']:+6.1f} / 100.0 pkt")
    print(f"Faworytem:  {result_v2['details']['favorite']}")
    print(f"Kwalifikuje: {'✅ TAK' if result_v2['qualifies'] else '❌ NIE'} (próg: 40)")
    print()
    
    # =========================================
    # ANALIZA V3
    # =========================================
    print("📊 V3 SCORING (NOWY):")
    print("-" * 40)
    
    result_v3 = analyzer_v3.analyze_match(
        player_a=match['home_team'],
        player_b=match['away_team'],
        h2h_matches=h2h_matches_v3,
        form_a=form_a_v3,
        form_b=form_b_v3,
        surface=surface,
        surface_stats_a=surface_stats_a_v3,
        surface_stats_b=surface_stats_b_v3
    )
    
    breakdown_v3 = result_v3['breakdown']
    print(f"H2H (40%):           {breakdown_v3['h2h_score']:+6.1f} / 40.0 pkt")
    print(f"Forma aktualna (30%): {breakdown_v3['current_form_score']:+6.1f} / 30.0 pkt")
    print(f"Forma nawierzchni:    {breakdown_v3['surface_form_score']:+6.1f} / 20.0 pkt")
    print(f"Momentum (10%):       {breakdown_v3['momentum_score']:+6.1f} / 10.0 pkt")
    print(f"{'-'*40}")
    print(f"RAZEM:               {result_v3['total_score']:+6.1f} / 100.0 pkt")
    print(f"Faworytem:  {result_v3['details']['favorite']}")
    print(f"Pewność:    {result_v3['confidence'].upper()}")
    print(f"Kwalifikuje: {'✅ TAK' if result_v3['qualifies'] else '❌ NIE'} (próg: 45)")
    
    # Ostrzeżenia
    warnings = result_v3['details'].get('warnings', [])
    if warnings:
        print(f"⚠️ Ostrzeżenia: {', '.join(warnings)}")
    
    print()
    
    # =========================================
    # PORÓWNANIE
    # =========================================
    print("🔍 PORÓWNANIE:")
    print("-" * 40)
    
    # Różnica w scoringu
    diff = abs(result_v3['total_score']) - abs(result_v2['total_score'])
    print(f"Różnica scoringu: {diff:+.1f} pkt")
    
    # Czy zmienił się faworytem?
    if result_v2['details']['favorite'] != result_v3['details']['favorite']:
        print(f"⚠️ ZMIANA FAWORYTA!")
        print(f"   V2: {result_v2['details']['favorite']}")
        print(f"   V3: {result_v3['details']['favorite']}")
    else:
        print(f"✅ Zgodność: obydwa wskazują {result_v3['details']['favorite']}")
    
    # Czy zmienił się status kwalifikacji?
    if result_v2['qualifies'] != result_v3['qualifies']:
        print(f"⚠️ ZMIANA KWALIFIKACJI!")
        print(f"   V2: {'kwalifikuje' if result_v2['qualifies'] else 'nie kwalifikuje'}")
        print(f"   V3: {'kwalifikuje' if result_v3['qualifies'] else 'nie kwalifikuje'}")
    
    # Kluczowe różnice
    print(f"\n📌 Kluczowe różnice:")
    if ranking_a and ranking_b:
        print(f"   - V2 używał rankingu ({ranking_a:.0f} vs {ranking_b:.0f}) = {breakdown_v2['ranking_score']:+.1f} pkt")
        print(f"   - V3 IGNORUJE ranking")
    
    # Forma
    form_diff = breakdown_v3['current_form_score'] - breakdown_v2['form_score']
    if abs(form_diff) > 3:
        print(f"   - Forma: V3 widzi większą różnicę ({form_diff:+.1f} pkt)")
    
    # Nawierzchnia
    surface_diff = breakdown_v3['surface_form_score'] - breakdown_v2['surface_score']
    if abs(surface_diff) > 3:
        print(f"   - Nawierzchnia: V3 wykrył większą przewagę ({surface_diff:+.1f} pkt)")
    
    print()
    print()

print("=" * 80)
print("📈 PODSUMOWANIE TESTÓW")
print("=" * 80)
print()
print("✅ Test zakończony pomyślnie!")
print()
print("📊 Wnioski:")
print("- V3 lepiej analizuje formę (30% vs 15%)")
print("- V3 ignoruje ranking (może dawać inne wyniki)")
print("- V3 ma wyższy próg (45 vs 40) - mniej kwalifikacji")
print("- V3 dodaje analizę momentum")
print()
print("⚠️ UWAGA: Dane są częściowo symulowane!")
print("   Aby V3 działał optymalnie, scraper musi zbierać:")
print("   - Daty meczów H2H")
print("   - Rankingi przeciwników w formie")
print("   - Wyniki setowe (2-0, 2-1)")
print("   - Formę NA konkretnej nawierzchni")

