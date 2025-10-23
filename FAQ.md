# ❓ FAQ - Często Zadawane Pytania

## 🎯 Ogólne

### Q: Co robi ten skrypt?
**A:** Dla podanej daty znajduje mecze, w których gospodarze wygrali co najmniej 2 razy w ostatnich 5 bezpośrednich spotkaniach (H2H) z przeciwnikiem.

### Q: Jakie sporty są wspierane?
**A:** 6 sportów drużynowych:
- ⚽ Piłka nożna (football)
- 🏀 Koszykówka (basketball)
- 🏐 Siatkówka (volleyball)
- 🤾 Piłka ręczna (handball)
- 🏉 Rugby
- 🏒 Hokej (hockey)

### Q: Czy to legalne?
**A:** Web scraping jest legalny w wielu jurysdykcjach dla danych publicznie dostępnych, ALE:
- ✅ Musisz przestrzegać `robots.txt` serwisu
- ✅ Musisz przestrzegać Terms of Service Livesport
- ✅ Nie możesz przeciążać serwera (rate limiting)
- ✅ Przy komercyjnym/masowym użyciu potrzebujesz zgody właściciela

**Rekomendacja**: Używaj odpowiedzialnie, tylko do analizy osobistej.

---

## 🚀 Instalacja i Uruchomienie

### Q: Jak zainstalować?
**A:**
```bash
pip install -r requirements.txt
```

### Q: Nie mam Chrome, czy mogę użyć Firefox?
**A:** Obecnie skrypt wspiera tylko Chrome. Możesz zmodyfikować kod aby użyć Firefox + geckodriver (podobna zmiana jak ChromeDriver → FirefoxDriver).

### Q: Chromedriver nie działa / błędy instalacji
**A:**
```bash
# Zaktualizuj pakiety
pip install --upgrade selenium webdriver-manager

# Sprawdź wersję Chrome
# Chrome → Pomoc → O Google Chrome
# Upewnij się że masz Chrome 120+
```

### Q: Błąd "Module not found"
**A:**
```bash
# Upewnij się że zainstalowałeś wszystkie zależności:
pip install selenium beautifulsoup4 pandas webdriver-manager

# Sprawdź czy używasz właściwego Pythona:
python --version  # powinno być 3.9+
```

---

## 💻 Użytkowanie

### Q: Który tryb jest lepszy - `urls` czy `auto`?
**A:**
- **`urls`**: Bardziej niezawodny - przetwarzasz tylko mecze które sam wybrałeś
- **`auto`**: Wygodniejszy - automatycznie znajduje mecze, ale może przegapić niektóre

**Rekomendacja**: Dla ważnych analiz użyj `urls`. Dla szybkiego testowania - `auto`.

### Q: Jak zdobyć URLe do meczów?
**A:**
1. Wejdź na https://www.livesport.com/pl/
2. Wybierz sport (np. piłka nożna)
3. Kliknij na konkretny mecz
4. Skopiuj URL z paska przeglądarki (cały!)
5. Wklej do pliku `match_urls.txt`

### Q: Nie znajduje żadnych meczów w trybie `auto`
**A:** Spróbuj:
```bash
# 1. Uruchom bez --headless aby zobaczyć co się dzieje
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football

# 2. Użyj --advanced
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --advanced --headless

# 3. Użyj trybu urls (najbardziej niezawodny)
python livesport_h2h_scraper.py --mode urls --date 2025-10-05 --input match_urls.txt --headless
```

### Q: Jak uruchomić dla wczorajszych/jutrzejszych meczów?
**A:** Po prostu zmień parametr `--date`:
```bash
# Wczoraj
python livesport_h2h_scraper.py --mode auto --date 2025-10-04 --sports football --headless

# Jutro
python livesport_h2h_scraper.py --mode auto --date 2025-10-06 --sports football --headless

# Za tydzień
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football --headless
```

### Q: Czy mogę uruchomić dla wielu dni naraz?
**A:** Nie bezpośrednio, ale możesz użyć pętli:

**Windows (batch)**:
```batch
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --headless
python livesport_h2h_scraper.py --mode auto --date 2025-10-06 --sports football --headless
python livesport_h2h_scraper.py --mode auto --date 2025-10-07 --sports football --headless
```

**Linux/Mac (bash)**:
```bash
for date in 2025-10-05 2025-10-06 2025-10-07; do
    python3 livesport_h2h_scraper.py --mode auto --date $date --sports football --headless
done
```

---

## 🔍 Wyniki i Dane

### Q: Gdzie są zapisywane wyniki?
**A:** W katalogu `outputs/`:
- `outputs/livesport_h2h_2025-10-05.csv` - wszystkie sporty
- `outputs/livesport_h2h_2025-10-05_football.csv` - tylko piłka

### Q: Jak otworzyć CSV w Excelu z polskimi znakami?
**A:** Plik jest zapisany w UTF-8 z BOM, więc:
1. Excel 2016+: Po prostu otwórz (powinno działać)
2. Starsze wersje: Data → Z pliku tekstowego → Wybierz UTF-8

### Q: Jak przefiltrować tylko kwalifikujące się mecze?
**A:** 
- **Excel**: Data → Filtr → `qualifies = TRUE`
- **Google Sheets**: `=FILTER(A:G, G:G=TRUE)`
- **Python**: `df[df['qualifies'] == True]`

### Q: Co oznacza kolumna `h2h_last5`?
**A:** Zawiera listę ostatnich 5 bezpośrednich spotkań jako string. Zobacz `EXAMPLE_OUTPUT.md` dla szczegółów.

### Q: Niektóre mecze mają `home_wins_in_h2h_last5 = 0` - dlaczego?
**A:** Bo gospodarze nie wygrali żadnego z ostatnich 5 H2H (albo dane H2H nie były dostępne).

---

## ⚠️ Problemy i Błędy

### Q: "TimeoutException" / "WebDriverException"
**A:**
```bash
# 1. Sprawdź połączenie internetowe
# 2. Wydłuż opóźnienia w kodzie (zmień time.sleep() na większe wartości)
# 3. Uruchom bez --headless aby zobaczyć co się dzieje
```

### Q: "No such element" / Błędy parsowania
**A:** Livesport zmienił strukturę HTML. Rozwiązania:
1. Użyj trybu `urls` z konkretnymi meczami
2. Sprawdź czy jest aktualizacja skryptu
3. Poczekaj - może być tymczasowy problem z serwerem

### Q: Skrypt "zawieszsa się" / nie reaguje
**A:**
- To normalne - przetwarzanie jednego meczu zajmuje 2-5 sekund
- Sprawdź logi w konsoli - powinieneś widzieć postęp `[X/Y]`
- Jeśli naprawdę się zawiesił - Ctrl+C i uruchom ponownie

### Q: "UnicodeDecodeError" / problemy z polskimi znakami
**A:**
```bash
# Upewnij się że używasz UTF-8:
python livesport_h2h_scraper.py ... 

# W skrypcie jest już ustawione encoding='utf-8-sig'
# Jeśli nadal problem - otwórz issue na GitHubie
```

---

## 🎛️ Zaawansowane

### Q: Jak zmienić kryterium z "≥2 wygrane" na "≥3 wygrane"?
**A:** Edytuj `livesport_h2h_scraper.py`:
```python
# Linia ~316
out['qualifies'] = cnt >= 3  # zmień 2 na 3
```

### Q: Jak zapisać więcej niż 5 ostatnich H2H?
**A:** Edytuj `livesport_h2h_scraper.py`:
```python
# Linia ~222 w funkcji parse_h2h_from_soup
if len(results) >= 10:  # zmień 5 na 10
    break
```

### Q: Jak dodać własne ligi?
**A:** Edytuj `livesport_h2h_scraper.py`:
```python
# Linia ~71-103
POPULAR_LEAGUES = {
    'football': {
        'ekstraklasa': 'Ekstraklasa',
        'moja-liga': 'Moja Liga',  # dodaj tutaj
        # ...
    },
}
```

### Q: Jak uruchomić scraper w chmurze (AWS/GCP/Azure)?
**A:**
1. Użyj instancji z Ubuntu
2. Zainstaluj Chrome: `sudo apt-get install google-chrome-stable`
3. Zainstaluj Python 3.9+
4. Uruchom zawsze z `--headless`
5. Opcjonalnie: użyj `screen` lub `tmux` dla długich sesji

### Q: Czy mogę zrównoleglić (parallel processing)?
**A:** Tak, ale ostrożnie:
```python
# Możesz użyć ThreadPoolExecutor dla wielu URLi
# ALE: respektuj rate limiting!
# Rekomendacja: max 2-3 równoległe requesty
```

---

## 🤝 Contributing

### Q: Jak mogę pomóc w rozwoju projektu?
**A:**
1. Zgłaszaj bugi na GitHubie
2. Testuj na różnych sportach/ligach
3. Udostępniaj pull requesty z ulepszeniami
4. Uzupełniaj dokumentację

### Q: Gdzie zgłaszać bugi?
**A:** Utwórz Issue na GitHubie z:
- Opisem problemu
- Komendą którą uruchomiłeś
- Logami błędów
- Wersją Pythona i Chrome

---

## 📞 Kontakt i Pomoc

### Q: Nie znalazłem odpowiedzi na moje pytanie
**A:** Sprawdź:
1. `README.md` - pełna dokumentacja
2. `QUICKSTART.md` - szybki start
3. `EXAMPLE_OUTPUT.md` - przykłady wyników
4. `--help`: `python livesport_h2h_scraper.py --help`

### Q: Potrzebuję komercyjnego wsparcia
**A:** To open-source projekt bez oficjalnego wsparcia komercyjnego. Możesz:
- Zatrudnić freelancera do customizacji
- Rozważyć oficjalne API Livesport (jeśli dostępne)

---

**Ostatnia aktualizacja**: 2025-10-05  
**Wersja**: 2.0 (Multi-Sport Edition)

