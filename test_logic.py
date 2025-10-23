"""
Test logiki H2H - sprawdzenie czy poprawnie liczymy wygrane aktualnego gospodarza
"""

# Test case 1: Prosty przykład
print("="*60)
print("TEST CASE 1: Legia vs Cracovia")
print("="*60)

current_home = "Legia Warszawa"
current_away = "Cracovia"

h2h_matches = [
    {"home": "Legia Warszawa", "away": "Cracovia", "score": "3-1"},      # Legia u siebie wygrała
    {"home": "Cracovia", "away": "Legia Warszawa", "score": "0-2"},      # Legia na wyjeździe wygrała  
    {"home": "Legia Warszawa", "away": "Cracovia", "score": "1-1"},      # Remis
    {"home": "Cracovia", "away": "Legia Warszawa", "score": "2-0"},      # Cracovia wygrała
    {"home": "Legia Warszawa", "away": "Cracovia", "score": "2-1"},      # Legia u siebie wygrała
]

print(f"\nDzisiejszy mecz: {current_home} (H) vs {current_away} (A)")
print(f"\nH2H (ostatnie 5):")

cnt = 0
for idx, match in enumerate(h2h_matches, 1):
    h2h_home = match['home']
    h2h_away = match['away']
    score = match['score']
    
    # Parsuj wynik
    goals_h, goals_a = map(int, score.split('-'))
    
    # Kto wygrał?
    if goals_h > goals_a:
        winner = h2h_home
        result_symbol = "✓" if winner == current_home else "✗"
    elif goals_a > goals_h:
        winner = h2h_away
        result_symbol = "✓" if winner == current_home else "✗"
    else:
        winner = "Remis"
        result_symbol = "○"
    
    # Czy wygrał aktualny gospodarz?
    if winner == current_home:
        cnt += 1
    
    print(f"  {idx}. {h2h_home} {score} {h2h_away} → Wygrał: {winner} {result_symbol}")

print(f"\n📊 WYNIK: {current_home} wygrał {cnt}/5 ostatnich H2H")
print(f"❓ Kwalifikuje się? {'✅ TAK' if cnt >= 2 else '❌ NIE'} (wymaga ≥2)")

# Test case 2: Wszystkie wygrane gospodarza
print("\n" + "="*60)
print("TEST CASE 2: Barcelona vs Real Madryt (wszystkie wygrane Barcy)")
print("="*60)

current_home = "Barcelona"
current_away = "Real Madryt"

h2h_matches = [
    {"home": "Barcelona", "away": "Real Madryt", "score": "3-0"},        # Barca u siebie
    {"home": "Real Madryt", "away": "Barcelona", "score": "1-2"},        # Barca na wyjeździe
    {"home": "Barcelona", "away": "Real Madryt", "score": "5-1"},        # Barca u siebie
    {"home": "Real Madryt", "away": "Barcelona", "score": "0-4"},        # Barca na wyjeździe
    {"home": "Barcelona", "away": "Real Madryt", "score": "2-1"},        # Barca u siebie
]

print(f"\nDzisiejszy mecz: {current_home} (H) vs {current_away} (A)")
print(f"\nH2H (ostatnie 5):")

cnt = 0
for idx, match in enumerate(h2h_matches, 1):
    h2h_home = match['home']
    h2h_away = match['away']
    score = match['score']
    
    goals_h, goals_a = map(int, score.split('-'))
    
    if goals_h > goals_a:
        winner = h2h_home
    elif goals_a > goals_h:
        winner = h2h_away
    else:
        winner = "Remis"
    
    result_symbol = "✓" if winner == current_home else ("✗" if winner != "Remis" else "○")
    
    if winner == current_home:
        cnt += 1
    
    print(f"  {idx}. {h2h_home} {score} {h2h_away} → Wygrał: {winner} {result_symbol}")

print(f"\n📊 WYNIK: {current_home} wygrał {cnt}/5 ostatnich H2H")
print(f"❓ Kwalifikuje się? {'✅ TAK' if cnt >= 2 else '❌ NIE'} (wymaga ≥2)")

# Test case 3: Edge case - różne nazwy drużyn
print("\n" + "="*60)
print("TEST CASE 3: Różne warianty nazw (Legia vs Legia Warszawa)")
print("="*60)

current_home = "Legia Warszawa"
current_away = "Wisła Kraków"

h2h_matches = [
    {"home": "Legia", "away": "Wisła", "score": "2-0"},                  # Skrócona nazwa
    {"home": "Wisła Kraków", "away": "Legia", "score": "1-3"},           # Pełna nazwa
    {"home": "Legia Warszawa", "away": "Wisła Kraków", "score": "1-1"},  # Remis
]

print(f"\nDzisiejszy mecz: {current_home} (H) vs {current_away} (A)")
print(f"\nH2H (ostatnie 3):")

cnt = 0
for idx, match in enumerate(h2h_matches, 1):
    h2h_home = match['home']
    h2h_away = match['away']
    score = match['score']
    
    goals_h, goals_a = map(int, score.split('-'))
    
    if goals_h > goals_a:
        winner = h2h_home
    elif goals_a > goals_h:
        winner = h2h_away
    else:
        winner = "Remis"
    
    # Sprawdzenie z normalizacją (jak w naszym kodzie)
    winner_normalized = winner.lower().strip()
    current_home_normalized = current_home.lower().strip()
    
    is_current_home_winner = (
        winner_normalized == current_home_normalized or
        winner_normalized in current_home_normalized or
        current_home_normalized in winner_normalized
    )
    
    result_symbol = "✓" if is_current_home_winner else ("✗" if winner != "Remis" else "○")
    
    if is_current_home_winner and winner != "Remis":
        cnt += 1
    
    print(f"  {idx}. {h2h_home} {score} {h2h_away} → Wygrał: {winner} {result_symbol}")

print(f"\n📊 WYNIK: {current_home} wygrał {cnt}/3 ostatnich H2H")
print(f"❓ Kwalifikuje się? {'✅ TAK' if cnt >= 2 else '❌ NIE'} (wymaga ≥2)")

print("\n" + "="*60)
print("✅ Testy zakończone!")
print("="*60)


