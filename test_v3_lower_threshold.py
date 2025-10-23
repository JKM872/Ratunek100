"""
Test różnych progów kwalifikacji dla V3
"""

import csv
import json
from tennis_advanced_v3 import TennisMatchAnalyzerV3

# Test różnych progów
thresholds = [20, 25, 30, 35, 40, 45]

with open('outputs/livesport_h2h_2025-10-05_tennis_EMAIL.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    matches = list(reader)

print("🎾 TEST RÓŻNYCH PROGÓW KWALIFIKACJI V3")
print("=" * 60)
print()

for threshold in thresholds:
    # Ustaw próg
    config = TennisMatchAnalyzerV3().config.copy()
    config['threshold'] = threshold
    analyzer = TennisMatchAnalyzerV3(config)
    
    qualified = 0
    confidence_dist = {'very_high': 0, 'high': 0, 'medium': 0, 'low': 0}
    
    for match in matches:
        # Parsuj dane (uproszczone)
        h2h_matches = []
        form_a = []
        form_b = []
        
        ranking_a = float(match.get('ranking_a', 0)) if match.get('ranking_a') else None
        ranking_b = float(match.get('ranking_b', 0)) if match.get('ranking_b') else None
        surface = match.get('surface', 'hard')
        
        # Symulowane dane
        surface_stats_a = {surface: {'wins': 5, 'total': 10, 'win_rate': 0.5, 'recent_form': []}}
        surface_stats_b = {surface: {'wins': 5, 'total': 10, 'win_rate': 0.5, 'recent_form': []}}
        
        try:
            result = analyzer.analyze_match(
                player_a=match['home_team'],
                player_b=match['away_team'],
                h2h_matches=h2h_matches,
                form_a=form_a,
                form_b=form_b,
                surface=surface,
                surface_stats_a=surface_stats_a,
                surface_stats_b=surface_stats_b
            )
            
            if result['qualifies']:
                qualified += 1
                confidence_dist[result['confidence']] += 1
        except:
            pass
    
    pct = qualified / len(matches) * 100
    print(f"Próg {threshold:2.0f} pkt: {qualified:3d} meczów ({pct:5.1f}%) | ", end='')
    print(f"VH:{confidence_dist['very_high']:2d} H:{confidence_dist['high']:2d} M:{confidence_dist['medium']:2d} L:{confidence_dist['low']:2d}")

print()
print("=" * 60)
print("💡 REKOMENDACJE:")
print()
print("• Próg 20-25 pkt: ~15-20% kwalifikacji (może za dużo słabych)")
print("• Próg 30-35 pkt: ~10-15% kwalifikacji (balans)")
print("• Próg 40-45 pkt: ~5-10% kwalifikacji (tylko pewne)")
print()
print("Obecny V2: 76% kwalifikacji")
print("Cel dla V3: 15-25% kwalifikacji (tylko dobre typy)")


















