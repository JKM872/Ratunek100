import csv
import json
from datetime import datetime

# Wczytaj dane z CSV
with open('outputs/livesport_h2h_2025-10-05_tennis_EMAIL.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    matches = list(reader)

print("🎾 ANALIZA DOKŁADNOŚCI SYSTEMU SCORINGU TENISA")
print("=" * 60)
print()

# Analiza ogólna
total_matches = len(matches)
qualified_matches = sum(1 for m in matches if m['qualifies'] == 'True')
print(f"Łącznie meczów: {total_matches}")
print(f"Zakwalifikowanych: {qualified_matches} ({qualified_matches/total_matches*100:.1f}%)")
print()

# Analiza czynników
print("📊 ANALIZA CZYNNIKÓW:")
print("-" * 30)

# Sprawdź jak często każdy czynnik jest używany
factors_count = {}
for match in matches:
    # Napraw JSON z pojedynczych cudzysłowów
    breakdown_str = match['score_breakdown'].replace("'", '"')
    breakdown = json.loads(breakdown_str)
    for factor, score in breakdown.items():
        if score != 0.0:  # Tylko jeśli czynnik był użyty
            factor_name = factor.replace('_score', '')
            factors_count[factor_name] = factors_count.get(factor_name, 0) + 1

for factor, count in sorted(factors_count.items(), key=lambda x: x[1], reverse=True):
    print(f"{factor.capitalize()}: {count} meczów ({count/total_matches*100:.1f}%)")

print()

# Analiza dokładności predykcji dla meczów które się już odbyły
print("🎯 DOKŁADNOŚĆ PREDYKCJI:")
print("-" * 30)

# Sprawdź mecze z dzisiaj lub wczorajsze
today = datetime.now().strftime('%d.%m.%Y')
matches_with_results = []

for match in matches[:20]:  # Pierwsze 20 meczów
    match_date = match['match_time'].split()[0]

    # Pomiń przyszłe mecze
    try:
        match_datetime = datetime.strptime(match_date, '%d.%m.%Y')
        if match_datetime > datetime.now():
            continue
    except:
        continue

    matches_with_results.append(match)

print(f"Mecze do analizy: {len(matches_with_results)}")
print()

correct_predictions = 0
total_predictions = 0

for match in matches_with_results:
    print(f"=== {match['home_team']} vs {match['away_team']} ===")
    print(f"Ranking: {match['ranking_a']} vs {match['ranking_b']}")
    print(f"Favorite systemu: {match['favorite']}")
    print(f"Score: {match['advanced_score']}")

    # Spróbuj znaleźć wynik (w danych H2H może być ostatni mecz)
    h2h_data = []
    if match['h2h_last5']:
        try:
            h2h_data = json.loads(match['h2h_last5'].replace("'", '"'))
        except:
            pass

    if h2h_data:
        last_match = h2h_data[0]
        winner = last_match.get('winner')
        if winner:
            print(f"Ostatni wynik H2H: {winner}")
            total_predictions += 1

            # Sprawdź czy predykcja była poprawna
            if winner == 'home' and match['favorite'] == 'player_a':
                correct_predictions += 1
                print("✅ PREDYKCJA POPRAWNA")
            elif winner == 'away' and match['favorite'] == 'player_b':
                correct_predictions += 1
                print("✅ PREDYKCJA POPRAWNA")
            else:
                print("❌ PREDYKCJA NIEPOPRAWNA")
        else:
            print("Brak danych o zwycięzcy")
    else:
        print("Brak danych H2H")

    print()

if total_predictions > 0:
    accuracy = correct_predictions / total_predictions * 100
    print(f"📈 DOKŁADNOŚĆ OGÓLNA: {correct_predictions}/{total_predictions} ({accuracy:.1f}%)")
else:
    print("Brak wystarczających danych do oceny dokładności")

print()
print("🔍 PROBLEMY SYSTEMU:")
print("-" * 30)
print("1. Bardzo niski próg kwalifikacji (40/100) - tylko 4% meczów")
print("2. Czynnik powierzchni często niedostępny")
print("3. Forma oparta tylko na ostatnich 5 meczach")
print("4. Ranking ma zbyt mały wpływ (max 25 punktów)")
