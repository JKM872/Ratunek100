"""
Weryfikuje kursy w istniejących plikach CSV - pokazuje czy są prawidłowe czy to daty
"""

import pandas as pd
import glob
import os

def analyze_odds_in_csv(csv_file: str):
    """Analizuje kursy w pliku CSV"""
    
    print(f"\n📄 Plik: {os.path.basename(csv_file)}")
    print("="*70)
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        
        # Podstawowe statystyki
        total_matches = len(df)
        qualified_matches = len(df[df['qualifies'] == True])
        
        print(f"  📊 Mecze ogółem: {total_matches}")
        print(f"  ✅ Kwalifikujące się: {qualified_matches}")
        
        # Kursy
        if 'home_odds' in df.columns and 'away_odds' in df.columns:
            # Mecze z kursami
            with_odds = df[(df['home_odds'].notna()) & (df['away_odds'].notna())]
            without_odds = total_matches - len(with_odds)
            
            print(f"\n  💰 KURSY:")
            print(f"     Z kursami: {len(with_odds)}/{total_matches} ({len(with_odds)/total_matches*100:.1f}%)")
            print(f"     Bez kursów: {without_odds}")
            
            if len(with_odds) > 0:
                # Sprawdź zakresy
                min_home = with_odds['home_odds'].min()
                max_home = with_odds['home_odds'].max()
                min_away = with_odds['away_odds'].min()
                max_away = with_odds['away_odds'].max()
                
                print(f"\n  📈 Zakresy kursów:")
                print(f"     Home: {min_home:.2f} - {max_home:.2f}")
                print(f"     Away: {min_away:.2f} - {max_away:.2f}")
                
                # Sprawdź podejrzane wartości (>20 = prawdopodobnie daty)
                suspicious_home = with_odds[with_odds['home_odds'] > 20.0]
                suspicious_away = with_odds[with_odds['away_odds'] > 20.0]
                suspicious = with_odds[(with_odds['home_odds'] > 20.0) | (with_odds['away_odds'] > 20.0)]
                
                if len(suspicious) > 0:
                    print(f"\n  ⚠️  PROBLEM: Znaleziono {len(suspicious)} podejrzanych wartości (>20.00):")
                    print(f"     Home >20: {len(suspicious_home)}")
                    print(f"     Away >20: {len(suspicious_away)}")
                    print(f"\n     Przykłady:")
                    for idx, row in suspicious.head(5).iterrows():
                        print(f"       • {row['home_team']} vs {row['away_team']}: "
                              f"{row['home_odds']:.2f} - {row['away_odds']:.2f}")
                    print(f"\n     ❌ To są prawdopodobnie DATY, nie kursy!")
                    print(f"     💡 Uruchom poprawiony scraper aby naprawić")
                    return False
                else:
                    print(f"\n  ✅ Wszystkie kursy są w prawidłowym zakresie (≤20.00)")
                    print(f"\n  📋 Przykładowe kursy (pierwsze 5):")
                    for idx, row in with_odds.head(5).iterrows():
                        home_odds = row['home_odds']
                        away_odds = row['away_odds']
                        if pd.notna(home_odds) and pd.notna(away_odds):
                            print(f"     • {row['home_team']} vs {row['away_team']}: "
                                  f"{home_odds:.2f} - {away_odds:.2f}")
                    return True
            else:
                print(f"\n  ⚠️  Brak meczów z kursami w tym pliku")
                return None
        else:
            print(f"\n  ⚠️  Brak kolumn z kursami w tym pliku")
            return None
            
    except Exception as e:
        print(f"  ❌ Błąd wczytywania pliku: {e}")
        return None


def main():
    """Główna funkcja - analizuje wszystkie CSV w outputs/"""
    
    print("="*70)
    print("🔍 WERYFIKACJA KURSÓW BUKMACHERSKICH W PLIKACH CSV")
    print("="*70)
    
    # Znajdź wszystkie pliki CSV
    csv_files = glob.glob('outputs/livesport_h2h_*.csv')
    
    if not csv_files:
        print("\n⚠️  Nie znaleziono żadnych plików CSV w folderze outputs/")
        print("   Uruchom najpierw scraper!")
        return
    
    print(f"\nZnaleziono {len(csv_files)} plików CSV")
    
    # Analizuj każdy plik
    results = {}
    for csv_file in sorted(csv_files):
        result = analyze_odds_in_csv(csv_file)
        results[csv_file] = result
    
    # Podsumowanie
    print("\n" + "="*70)
    print("📊 PODSUMOWANIE")
    print("="*70)
    
    ok_count = sum(1 for r in results.values() if r == True)
    bad_count = sum(1 for r in results.values() if r == False)
    no_odds_count = sum(1 for r in results.values() if r is None)
    
    print(f"\n  ✅ Pliki z poprawnymi kursami: {ok_count}")
    print(f"  ❌ Pliki z błędnymi kursami (daty): {bad_count}")
    print(f"  ⚠️  Pliki bez kursów: {no_odds_count}")
    
    if bad_count > 0:
        print(f"\n" + "="*70)
        print("🔧 AKCJA WYMAGANA:")
        print("="*70)
        print(f"\n  Znaleziono pliki z błędnymi kursami (daty zamiast kursów)!")
        print(f"\n  ✅ POPRAWKA ZOSTAŁA DODANA DO KODU!")
        print(f"\n  Aby naprawić:")
        print(f"     1. Uruchom scraper ponownie z tą samą datą")
        print(f"     2. Nowy plik nadpisze stary z poprawnymi kursami")
        print(f"\n  Przykład:")
        print(f"     python livesport_h2h_scraper.py --mode auto \\")
        print(f"       --date 2025-10-06 --sports football --headless")
    elif ok_count > 0:
        print(f"\n  ✨ Wszystkie kursy wyglądają poprawnie!")
    else:
        print(f"\n  ℹ️  Żaden plik nie zawiera kursów")
        print(f"     To normalne jeśli Livesport nie pokazuje kursów dla tych meczów")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    main()

