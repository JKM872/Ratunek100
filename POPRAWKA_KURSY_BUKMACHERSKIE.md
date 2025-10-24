# ✅ POPRAWKA: Kursy bukmacherskie - filtrowanie dat

## 📋 Problem który został naprawiony

### ❌ Przed poprawką:
Scraper wyciągał **DATY zamiast kursów bukmacherskich**:
- Real Sociedad vs Sevilla: `24.1` vs `28.09` ❌ (to są daty: 24 stycznia i 28 września!)
- AC Milan vs Pisa: `24.1` vs `5.10` ❌ (24 stycznia i 5 października!)
- Power Dynamos vs Vipers: `24.1` vs `19.09` ❌

### ✅ Po poprawce:
- Kursy są filtrowane do zakresu **1.01 - 20.00** (typowy zakres kursów sportowych)
- Wartości >20 są odrzucane jako **potencjalne daty**
- Dodano lepsze selektory HTML dla elementów z kursami
- Dodano wsparcie dla europejskiego formatu (przecinek zamiast kropki)

---

## 🔧 Zmiany w kodzie

### 1. **Funkcja `extract_betting_odds_with_selenium`** (główna metoda)

**Przed:**
```python
# Filtruj tylko wartości typowe dla kursów (1.01 - 50.00)
if 1.01 <= odd_val <= 50.0:
    odds_values.append(odd_val)
```

**Po:**
```python
# KLUCZOWA ZMIANA: Filtruj wartości typowe dla kursów (1.01 - 20.00)
# Wartości >20 to prawdopodobnie DATY (np. 24.10 = 24 października)
# Wartości <1 to błędy
if 1.01 <= odd_val <= 20.0:
    odds_values.append(odd_val)
```

### 2. **Funkcja `extract_betting_odds`** (fallback BeautifulSoup)

Dodano identyczną filtrację do metody fallback.

### 3. **Lepsze selektory**

Dodano dodatkowe klasy do wyszukiwania:
```python
odds_elements = driver.find_elements(By.XPATH, 
    "//*[contains(@class, 'odds') or contains(@class, 'Odds') or "
    "contains(@class, 'bookmaker') or contains(@class, 'bet')]")
```

---

## 🧪 Jak przetestować poprawkę

### Opcja 1: Test pojedynczego meczu

```bash
python test_odds_fix.py "https://www.livesport.com/pl/pilka-nozna/[URL_MECZU]"
```

Przykład:
```bash
python test_odds_fix.py "https://www.livesport.com/pl/pilka-nozna/polska/ekstraklasa/legia-warszawa-rakow-czestochowa/ABCXYZ/"
```

### Opcja 2: Pełny scraping z testowymi danymi

```bash
# Scrapuj kilka meczów i sprawdź kursy
python livesport_h2h_scraper.py --mode auto --date 2025-10-25 --sports football --headless
```

Następnie sprawdź plik CSV:
```bash
python -c "import pandas as pd; df = pd.read_csv('outputs/livesport_h2h_2025-10-25_football.csv'); print(df[['home_team', 'away_team', 'home_odds', 'away_odds']].head(10))"
```

### Opcja 3: Test z emailem (opcja `--skip-no-odds`)

```bash
python scrape_and_notify.py --date 2025-10-25 --sports football \
  --to twoj@email.com --from twoj@email.com --password "haslo" \
  --skip-no-odds --headless
```

Flaga `--skip-no-odds` pominie mecze **bez kursów**, więc w emailu zobaczysz tylko mecze z prawidłowymi kursami.

---

## ⚠️ **WAŻNE: Ograniczenia**

### 1. **Livesport może nie pokazywać kursów na stronie H2H**

Scraper otwiera stronę `/h2h/ogolem/` aby pobrać H2H. **Kursy mogą nie być dostępne na tej stronie!**

**Możliwe rozwiązania:**
- ✅ Scraper próbuje różne metody (Selenium + BeautifulSoup)
- ⚠️ Jeśli Livesport nie pokazuje kursów na /h2h/, scraper zwróci `None`
- 💡 Rozważyć ładowanie głównej strony meczu zamiast /h2h/ dla kursów

### 2. **Nie wszystkie mecze mają kursy**

- Mecze bardzo wcześnie (>7 dni przed) mogą nie mieć kursów
- Mecze bardzo późno (po rozpoczęciu) mogą mieć ukryte kursy
- Mniejsze ligi mogą nie być obsługiwane przez bukmacherów

### 3. **Kursy są opcjonalne**

Zgodnie z dokumentacją:
> ⚠️ Kursy są wyłącznie informacją dodatkową, **nie wpływają na scoring**

Mecz może się kwalifikować **bez kursów** (tylko na podstawie H2H + formy).

---

## 📊 Sprawdź czy poprawka działa

### Polecenia weryfikacyjne:

#### 1. Sprawdź statystyki kursów w danych:
```python
import pandas as pd

df = pd.read_csv('outputs/livesport_h2h_2025-10-25_football.csv')

# Kursy które są dostępne
with_odds = df[(df['home_odds'].notna()) & (df['away_odds'].notna())]
print(f"Meczów z kursami: {len(with_odds)}/{len(df)}")

# Sprawdź zakresy
if len(with_odds) > 0:
    print(f"Zakres home_odds: {with_odds['home_odds'].min():.2f} - {with_odds['home_odds'].max():.2f}")
    print(f"Zakres away_odds: {with_odds['away_odds'].min():.2f} - {with_odds['away_odds'].max():.2f}")
    
    # Sprawdź czy są podejrzane wartości (>20 = prawdopodobnie daty)
    suspicious = with_odds[(with_odds['home_odds'] > 20) | (with_odds['away_odds'] > 20)]
    if len(suspicious) > 0:
        print(f"⚠️  Znaleziono {len(suspicious)} podejrzanych wartości (>20.00):")
        print(suspicious[['home_team', 'away_team', 'home_odds', 'away_odds']])
    else:
        print("✅ Wszystkie kursy są w prawidłowym zakresie (1.01-20.00)")
```

#### 2. Sprawdź przykładowe kursy:
```bash
python -c "import pandas as pd; df = pd.read_csv('outputs/livesport_h2h_2025-10-25_football.csv'); q = df[(df['home_odds'].notna()) & (df['away_odds'].notna())]; print(q[['home_team', 'away_team', 'home_odds', 'away_odds']].head(10))"
```

**Oczekiwany wynik:**
```
             home_team        away_team  home_odds  away_odds
0        Leeds United         West Ham       2.10       3.40
1              PSG               Lyon       1.50       5.20
2      Real Madrid          Barcelona       1.85       4.10
```

---

## 🎯 Co dalej?

### Jeśli kursy nadal nie są poprawne:

1. **Sprawdź czy Livesport pokazuje kursy na stronie H2H**
   - Otwórz ręcznie stronę meczu na Livesport
   - Przejdź do zakładki H2H
   - Sprawdź czy tam są widoczne kursy

2. **Może trzeba ładować inną stronę**
   - Kursy mogą być tylko na głównej stronie meczu (nie /h2h/)
   - Rozważ dodanie osobnego requesta dla kursów

3. **Użyj opcji `--skip-no-odds`**
   - W emailu otrzymasz tylko mecze które **mają** kursy
   - To pozwoli skupić się na meczach z pełnymi danymi

---

## 📧 Email - jak kursy są wyświetlane

W emailu kursy są pokazane w dedykowanej sekcji:

```
🎲 Kursy: Real Madrid 1.85 | Barcelona 4.10
⚠️ Kursy są wyłącznie informacją dodatkową, nie wpływają na scoring
```

**Flagi emaila:**
- `--skip-no-odds`: Wysyła tylko mecze z kursami 💰
- `--only-form-advantage`: Wysyła tylko mecze z przewagą formy 🔥
- Można łączyć: `--skip-no-odds --only-form-advantage` 🔥💰

---

## 📞 Wsparcie

Jeśli kursy nadal nie działają prawidłowo:
1. Uruchom `python test_odds_fix.py [URL]` z prawdziwym URLem meczu
2. Sprawdź sekcję DEBUG w outputcie
3. Sprawdź czy Livesport pokazuje kursy dla danego meczu
4. Rozważ użycie `--skip-no-odds` aby pomijać mecze bez kursów

