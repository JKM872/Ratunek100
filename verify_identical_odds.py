"""
Weryfikuje czy w plikach CSV są identyczne kursy (home_odds == away_odds)
"""

import pandas as pd
import glob
import os

def check_identical_odds(csv_file: str):
    """Sprawdza czy w pliku CSV są identyczne kursy"""
    
    print(f"\n📄 Plik: {os.path.basename(csv_file)}")
    print("="*70)
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        
        # Mecze z kursami
        if 'home_odds' in df.columns and 'away_odds' in df.columns:
            with_odds = df[(df['home_odds'].notna()) & (df['away_odds'].notna())]
            
            if len(with_odds) == 0:
                print("  ℹ️  Brak meczów z kursami")
                return None
            
            print(f"  📊 Mecze z kursami: {len(with_odds)}")
            
            # Sprawdź identyczne kursy
            identical = with_odds[with_odds['home_odds'] == with_odds['away_odds']]
            
            if len(identical) > 0:
                print(f"\n  ⚠️  PROBLEM: Znaleziono {len(identical)} meczów z IDENTYCZNYMI kursami!")
                print(f"     To jest {len(identical)/len(with_odds)*100:.1f}% wszystkich meczów z kursami")
                print(f"\n  📋 Przykłady (identyczne kursy):")
                
                for idx, row in identical.head(10).iterrows():
                    home_odds = row['home_odds']
                    away_odds = row['away_odds']
                    print(f"     • {row['home_team']} vs {row['away_team']}: "
                          f"{home_odds:.2f} == {away_odds:.2f} ❌")
                
                if len(identical) > 10:
                    print(f"     ... i {len(identical) - 10} więcej")
                
                print(f"\n  💡 To wskazuje na błąd w scrapowaniu kursów!")
                print(f"     Prawdziwe kursy bukmacherskie prawie NIGDY nie są identyczne.")
                return False
            else:
                print(f"\n  ✅ Wszystkie kursy są RÓŻNE (home != away)")
                
                # Pokaż przykłady POPRAWNYCH kursów
                print(f"\n  📋 Przykładowe kursy (pierwsze 5):")
                for idx, row in with_odds.head(5).iterrows():
                    home_odds = row['home_odds']
                    away_odds = row['away_odds']
                    print(f"     • {row['home_team']} vs {row['away_team']}: "
                          f"{home_odds:.2f} vs {away_odds:.2f} ✓")
                
                return True
        else:
            print(f"  ⚠️  Brak kolumn z kursami")
            return None
            
    except Exception as e:
        print(f"  ❌ Błąd wczytywania pliku: {e}")
        return None


def main():
    """Główna funkcja - sprawdza wszystkie CSV"""
    
    print("="*70)
    print("🔍 WERYFIKACJA IDENTYCZNYCH KURSÓW W PLIKACH CSV")
    print("="*70)
    print("\n❓ Problem: Scraper czasem wyciąga ten sam kurs dla gospodarzy i gości")
    print("   Przykład: Ziraat Bankasi 1.23 | Fenerbahce 1.23 ❌")
    print("   To wskazuje na błąd - kursy bukmacherskie prawie NIGDY nie są identyczne!\n")
    
    # Znajdź wszystkie pliki CSV
    csv_files = glob.glob('outputs/livesport_h2h_*.csv')
    
    if not csv_files:
        print("\n⚠️  Nie znaleziono żadnych plików CSV w folderze outputs/")
        return
    
    print(f"Znaleziono {len(csv_files)} plików CSV")
    
    # Sprawdź każdy plik
    results = {}
    for csv_file in sorted(csv_files):
        result = check_identical_odds(csv_file)
        results[csv_file] = result
    
    # Podsumowanie
    print("\n" + "="*70)
    print("📊 PODSUMOWANIE")
    print("="*70)
    
    ok_count = sum(1 for r in results.values() if r == True)
    bad_count = sum(1 for r in results.values() if r == False)
    no_odds_count = sum(1 for r in results.values() if r is None)
    
    print(f"\n  ✅ Pliki z RÓŻNYMI kursami (OK): {ok_count}")
    print(f"  ❌ Pliki z IDENTYCZNYMI kursami (błąd): {bad_count}")
    print(f"  ℹ️  Pliki bez kursów: {no_odds_count}")
    
    if bad_count > 0:
        print(f"\n" + "="*70)
        print("🔧 AKCJA WYMAGANA:")
        print("="*70)
        print(f"\n  Znaleziono pliki z identycznymi kursami!")
        print(f"\n  ✅ POPRAWKA ZOSTAŁA DODANA DO KODU!")
        print(f"\n  Co zrobiono:")
        print(f"     1. ✅ Dodano deduplikację - usuwa duplikaty kursów")
        print(f"     2. ✅ Dodano walidację - sprawdza czy home_odds != away_odds")
        print(f"     3. ✅ Alternatywna metoda - jeśli identyczne, bierze pierwszy i ostatni")
        print(f"     4. ✅ Jeśli nadal identyczne - odrzuca kursy (lepiej brak niż błędne)")
        print(f"\n  Aby naprawić:")
        print(f"     Uruchom scraper ponownie - kursy będą poprawne!")
        print(f"\n  Przykład:")
        print(f"     python livesport_h2h_scraper.py --mode auto \\")
        print(f"       --date 2025-10-25 --sports basketball --headless")
    elif ok_count > 0:
        print(f"\n  ✨ Wszystkie kursy są poprawnie zróżnicowane!")
    else:
        print(f"\n  ℹ️  Żaden plik nie zawiera kursów")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    main()



