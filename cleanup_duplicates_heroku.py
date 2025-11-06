"""
Skrypt do czyszczenia duplikatów na Heroku przez API
Pobiera wszystkie mecze, identyfikuje duplikaty i usuwa je zachowując tylko najnowsze
"""

import requests
import json
from collections import defaultdict

# Heroku API URL
HEROKU_APP_URL = "https://livesport-scraper-ui-0393f6f2096e.herokuapp.com"

def get_all_matches():
    """Pobierz wszystkie mecze z API"""
    response = requests.get(f"{HEROKU_APP_URL}/api/matches")
    response.raise_for_status()
    return response.json()

def find_duplicates(matches):
    """Znajdź duplikaty - grupuj po sport, home_team, away_team, match_time"""
    grouped = defaultdict(list)
    
    for match in matches:
        key = (
            match.get('sport'),
            match.get('home_team'),
            match.get('away_team'),
            match.get('match_time')
        )
        grouped[key].append(match)
    
    return grouped

def identify_ids_to_delete(grouped):
    """Dla każdej grupy duplikatów, zachowaj najnowszy (max ID) i usuń resztę"""
    to_delete = []
    to_keep = []
    
    for key, matches in grouped.items():
        if len(matches) > 1:
            # Sortuj po ID (najwyższy = najnowszy)
            sorted_matches = sorted(matches, key=lambda x: x['id'], reverse=True)
            
            # Zachowaj pierwszy (najnowszy)
            to_keep.append(sorted_matches[0]['id'])
            
            # Reszta do usunięcia
            for match in sorted_matches[1:]:
                to_delete.append(match['id'])
                
            print(f"🔍 Duplikat: {key[1]} vs {key[2]}")
            print(f"   Zachowuję ID {sorted_matches[0]['id']}, usuwam {len(sorted_matches)-1} duplikatów")
        else:
            # Unikalny mecz
            to_keep.append(matches[0]['id'])
    
    return to_delete, to_keep

def main():
    print("📊 Pobieranie wszystkich meczów z Heroku...")
    matches = get_all_matches()
    print(f"✅ Pobrano {len(matches)} rekordów")
    
    print("\n🔍 Szukam duplikatów...")
    grouped = find_duplicates(matches)
    
    unique_matches = len(grouped)
    total_records = len(matches)
    duplicates_count = total_records - unique_matches
    
    print(f"\n📈 Statystyki:")
    print(f"   Wszystkich rekordów: {total_records}")
    print(f"   Unikalnych meczów: {unique_matches}")
    print(f"   Duplikatów do usunięcia: {duplicates_count}")
    
    if duplicates_count == 0:
        print("✅ Brak duplikatów! Baza jest czysta.")
        return
    
    print(f"\n🗑️  Identyfikuję rekordy do usunięcia...")
    to_delete, to_keep = identify_ids_to_delete(grouped)
    
    print(f"\n📋 Plan czyszczenia:")
    print(f"   IDs do zachowania: {len(to_keep)}")
    print(f"   IDs do usunięcia: {len(to_delete)}")
    print(f"   Pierwsze 10 IDs do usunięcia: {to_delete[:10]}")
    
    # Zapisz IDs do pliku żeby można było użyć w SQL
    with open('ids_to_delete.txt', 'w') as f:
        f.write(','.join(map(str, to_delete)))
    
    print(f"\n✅ Zapisano IDs do usunięcia w ids_to_delete.txt")
    print(f"\n⚠️  UWAGA: Ten skrypt tylko identyfikuje duplikaty.")
    print(f"   Aby usunąć, potrzebujemy dodać DELETE endpoint do API")
    print(f"   lub użyć heroku pg:psql (jeśli byłaby PostgreSQL)")
    
    return to_delete, to_keep

if __name__ == "__main__":
    to_delete, to_keep = main()
