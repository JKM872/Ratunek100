# 📁 Struktura Projektu

## Przegląd plików

```
Flashscore2/
│
├── 📄 livesport_h2h_scraper.py    ⭐ GŁÓWNY SKRYPT
├── 📄 generate_urls.py             🔧 Generator szablonów URLi
├── 📄 requirements.txt             📦 Zależności Python
├── 📄 match_urls.txt               📝 Szablon URLi do meczów
│
├── 🚀 run_all_sports.bat           ⚡ Quick launch (Windows) - wszystkie sporty
├── 🚀 run_football_only.bat        ⚡ Quick launch (Windows) - tylko piłka
├── 🚀 run_all_sports.sh            ⚡ Quick launch (Linux/Mac)
│
├── 📖 README.md                    📚 Pełna dokumentacja
├── 📖 QUICKSTART.md                🎯 Szybki start (5 minut)
├── 📖 FAQ.md                       ❓ Często zadawane pytania
├── 📖 EXAMPLE_OUTPUT.md            💡 Przykłady wyników
├── 📖 CHANGELOG.md                 📝 Historia zmian
├── 📖 PROJECT_STRUCTURE.md         📁 Ten plik
│
├── 📂 outputs/                     📊 Katalog z wynikami (tworzony automatycznie)
│   └── livesport_h2h_*.csv
│
└── 📄 .gitignore                   🚫 Ignorowane pliki

```

---

## 📄 Opis plików

### Pliki wykonywalne

#### `livesport_h2h_scraper.py` ⭐
**Główny skrypt scrapera.**

**Co robi:**
- Odwiedza strony meczów na Livesport.com
- Zbiera dane H2H (bezpośrednie spotkania)
- Filtruje mecze gdzie gospodarze wygrali ≥2/5 H2H
- Zapisuje wyniki do CSV

**Jak używać:**
```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --headless
```

**Funkcje:**
- Wsparcie 6 sportów (piłka nożna, koszykówka, siatkówka, piłka ręczna, rugby, hokej)
- Dwa tryby: `urls` (z pliku) i `auto` (automatyczne)
- Filtrowanie po ligach
- Rate limiting i error handling
- Szczegółowe logi

---

#### `generate_urls.py` 🔧
**Pomocniczy skrypt do generowania szablonów.**

**Co robi:**
- Tworzy szablon pliku `match_urls.txt`
- Zawiera przykłady URLi dla różnych sportów
- Pomaga w szybkim starcie

**Jak używać:**
```bash
python generate_urls.py --sports football basketball --output my_template.txt
```

---

### Pliki konfiguracyjne

#### `requirements.txt` 📦
**Lista zależności Python.**

Zawiera:
- selenium (WebDriver)
- beautifulsoup4 (parsing HTML)
- pandas (data processing)
- webdriver-manager (auto-install ChromeDriver)

**Instalacja:**
```bash
pip install -r requirements.txt
```

---

#### `match_urls.txt` 📝
**Szablon pliku z URLami meczów.**

**Format:**
```
# Komentarze zaczynają się od #
https://www.livesport.com/pl/pilka-nozna/.../mecz1
https://www.livesport.com/pl/koszykowka/.../mecz2
```

**Użycie:** Tryb `--mode urls`

---

### Skrypty Quick Launch

#### `run_all_sports.bat` (Windows)
Uruchamia scraper dla wszystkich 6 sportów.

**Edytuj:**
```batch
SET DATE=2025-10-05  # Zmień datę tutaj
```

**Uruchom:** Kliknij dwukrotnie lub `run_all_sports.bat`

---

#### `run_football_only.bat` (Windows)
Uruchamia scraper tylko dla piłki nożnej.

---

#### `run_all_sports.sh` (Linux/Mac)
Odpowiednik `.bat` dla systemów Unix.

**Uruchom:**
```bash
chmod +x run_all_sports.sh
./run_all_sports.sh
```

---

### Dokumentacja

#### `README.md` 📚
**Kompletna dokumentacja projektu.**

Zawiera:
- Opis projektu i cel
- Pełna lista funkcji
- Wszystkie parametry CLI
- Przykłady użycia
- Troubleshooting
- Informacje o licencji

**Dla kogo:** Wszyscy użytkownicy

---

#### `QUICKSTART.md` 🎯
**Szybki start dla niecierpliwych.**

Zawiera:
- 5 gotowych przykładów do skopiowania
- Minimalną teorię
- Quick wins

**Dla kogo:** Początkujący, osoby które chcą szybko zacząć

---

#### `FAQ.md` ❓
**Często zadawane pytania.**

Zawiera:
- Odpowiedzi na typowe problemy
- Troubleshooting
- Tips & Tricks
- Zaawansowane customizacje

**Dla kogo:** Osoby które napotkały problem

---

#### `EXAMPLE_OUTPUT.md` 💡
**Przykłady wyników i ich interpretacja.**

Zawiera:
- Struktura pliku CSV
- Przykładowe dane
- Jak przetwarzać wyniki (Excel, Python, Google Sheets)
- Statystyki

**Dla kogo:** Osoby które chcą zrozumieć output

---

#### `CHANGELOG.md` 📝
**Historia zmian w projekcie.**

Zawiera:
- Wersje i daty
- Nowe funkcje
- Poprawki bugów
- Breaking changes

**Dla kogo:** Developerzy, osoby śledzące rozwój

---

#### `PROJECT_STRUCTURE.md` 📁
**Ten plik - przewodnik po strukturze.**

---

### Inne pliki

#### `.gitignore` 🚫
**Lista ignorowanych plików dla Git.**

Ignoruje:
- `__pycache__/`
- `outputs/*.csv`
- `*.log`
- Chrome driver
- Virtual environments

---

## 📂 Katalogi

### `outputs/` 📊
**Katalog z wynikami (tworzony automatycznie).**

Struktura:
```
outputs/
├── livesport_h2h_2025-10-05.csv              # Wszystkie sporty
├── livesport_h2h_2025-10-05_football.csv     # Tylko piłka
├── livesport_h2h_2025-10-05_basketball.csv   # Tylko kosz
└── ...
```

**Uwaga:** Ten katalog jest w `.gitignore` - wyniki nie są commitowane do repo.

---

## 🎯 Gdzie zacząć?

### Dla początkujących:
1. ✅ Przeczytaj `QUICKSTART.md`
2. ✅ Uruchom `run_football_only.bat` (Windows) lub odpowiednik
3. ✅ Sprawdź wyniki w `outputs/`

### Dla zaawansowanych:
1. ✅ Przeczytaj `README.md`
2. ✅ Eksperymentuj z parametrami CLI
3. ✅ Customizuj skrypt według potrzeb

### Gdy napotkasz problem:
1. ✅ Sprawdź `FAQ.md`
2. ✅ Uruchom z `--help`
3. ✅ Zobacz `EXAMPLE_OUTPUT.md` dla przykładów

---

## 🔄 Workflow typowego użycia

### Scenariusz 1: Quick test
```
1. Edytuj run_football_only.bat (ustaw datę)
2. Kliknij dwukrotnie
3. Sprawdź outputs/livesport_h2h_*.csv
```

### Scenariusz 2: Ręczny wybór meczów
```
1. Otwórz Livesport.com w przeglądarce
2. Skopiuj URLe interesujących meczów
3. Wklej do match_urls.txt
4. python livesport_h2h_scraper.py --mode urls --date 2025-10-05 --input match_urls.txt --headless
5. Sprawdź outputs/
```

### Scenariusz 3: Analiza wielu sportów
```
1. python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football basketball volleyball --headless
2. Poczekaj (może zająć 5-15 minut)
3. Otwórz outputs/livesport_h2h_2025-10-05.csv w Excelu
4. Filtruj qualifies=TRUE
5. Analizuj!
```

---

## 📊 Rozmiary plików (przybliżone)

| Plik | Rozmiar | Linie kodu |
|------|---------|------------|
| `livesport_h2h_scraper.py` | ~23 KB | ~590 linii |
| `generate_urls.py` | ~4 KB | ~120 linii |
| `README.md` | ~18 KB | ~220 linii |
| `QUICKSTART.md` | ~5 KB | ~160 linii |
| `FAQ.md` | ~12 KB | ~350 linii |
| `EXAMPLE_OUTPUT.md` | ~10 KB | ~250 linii |

**Łącznie:** ~72 KB dokumentacji + kodu

---

## 🚀 Rozwój projektu

### Planowane funkcje (roadmap):
- [ ] Wsparcie dla Playwright (alternatywa dla Selenium)
- [ ] GUI (graficzny interfejs)
- [ ] Automatyczne schedulowanie (cron/scheduled tasks)
- [ ] Export do innych formatów (JSON, Excel, SQLite)
- [ ] Email notifications o znalezionych meczach
- [ ] Dashboard analytics
- [ ] Wsparcie dla proxy

### Jak pomóc:
1. Fork repozytorium
2. Utwórz branch z nową funkcją
3. Submit Pull Request
4. Opisz zmiany w CHANGELOG.md

---

**Wersja dokumentacji**: 2.0  
**Ostatnia aktualizacja**: 2025-10-05  
**Język**: Polski/English

---

## 📞 Quick Reference

| Chcę... | Plik |
|---------|------|
| Szybko zacząć | `QUICKSTART.md` |
| Rozwiązać problem | `FAQ.md` |
| Zrozumieć output | `EXAMPLE_OUTPUT.md` |
| Wszystko wiedzieć | `README.md` |
| Zobaczyć zmiany | `CHANGELOG.md` |
| Uruchomić teraz | `run_all_sports.bat` / `.sh` |

**Enjoy!** 🎉

