# 🚀 Quick Start Guide - Livesport H2H Scraper

Szybki start w 5 minut!

## ⚡ Instalacja (1 minuta)

```bash
# Sklonuj/pobierz projekt
cd Flashscore2

# Zainstaluj zależności
pip install -r requirements.txt
```

**Wymagania**: Python 3.9+, Chrome

---

## 🎯 Przykład 1: Wszystkie sporty na dzisiaj (2 minuty)

```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football basketball volleyball handball rugby hockey --headless
```

**Co się stanie:**
- Skrypt automatycznie odwiedzi strony wszystkich 6 sportów
- Zbierze linki do meczów
- Dla każdego meczu sprawdzi H2H
- Zapisze do `outputs/livesport_h2h_2025-10-05.csv` tylko mecze gdzie gospodarze wygrali ≥2 razy w ostatnich 5 H2H

---

## ⚽ Przykład 2: Tylko piłka nożna (najprostszy)

```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --headless
```

---

## 🏀 Przykład 3: Konkretne sporty

```bash
# Tylko piłka i koszykówka
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football basketball --headless

# Tylko siatkówka i piłka ręczna
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports volleyball handball --headless
```

---

## 🏟️ Przykład 4: Konkretne ligi

```bash
# Tylko top ligi europejskie
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --leagues ekstraklasa premier-league la-liga bundesliga --headless

# Tylko polskie ligi
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football volleyball handball --leagues ekstraklasa plusliga superliga --headless
```

---

## 📝 Przykład 5: Z własną listą meczów (najbardziej niezawodny)

### Krok 1: Przygotuj plik z URLami

Utwórz `my_matches.txt`:
```
https://www.livesport.com/pl/pilka-nozna/polska/ekstraklasa/legia-warszawa-cracovia/ABC123/
https://www.livesport.com/pl/koszykowka/usa/nba/lakers-celtics/DEF456/
https://www.livesport.com/pl/siatkowka/polska/plusliga/jastrzebski-wegiel-zaksa/GHI789/
```

### Krok 2: Uruchom

```bash
python livesport_h2h_scraper.py --mode urls --date 2025-10-05 --input my_matches.txt --headless
```

**Jak zdobyć URLe:**
1. Wejdź na https://www.livesport.com/pl/
2. Kliknij na interesujący mecz
3. Skopiuj URL z paska przeglądarki
4. Wklej do pliku

---

## 🔍 Debug Mode (gdy coś nie działa)

```bash
# Uruchom BEZ --headless aby zobaczyć przeglądarkę
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football
```

Zobaczysz co dokładnie robi skrypt w Chrome.

---

## 📊 Gdzie są wyniki?

Wszystkie wyniki w katalogu `outputs/`:

```
outputs/
  ├── livesport_h2h_2025-10-05.csv              # Wszystkie sporty
  ├── livesport_h2h_2025-10-05_football.csv     # Tylko piłka
  └── livesport_h2h_2025-10-05_basketball.csv   # Tylko kosz
```

---

## 📈 Co jest w CSV?

Plik CSV zawiera:

| Kolumna | Opis |
|---------|------|
| `match_url` | Link do meczu |
| `home_team` | Gospodarze |
| `away_team` | Goście |
| `home_wins_in_h2h_last5` | Ile razy gospodarze wygrali w ostatnich 5 H2H |
| `qualifies` | `True` jeśli ≥2 wygrane gospodarzy |

**Filtrowanie w Excelu**: Ustaw filtr na kolumnie `qualifies = True` aby zobaczyć tylko kwalifikujące się mecze!

---

## 🎨 Wszystkie dostępne sporty

```bash
--sports football      # ⚽ Piłka nożna
--sports basketball    # 🏀 Koszykówka
--sports volleyball    # 🏐 Siatkówka
--sports handball      # 🤾 Piłka ręczna
--sports rugby         # 🏉 Rugby
--sports hockey        # 🏒 Hokej
```

Możesz podać wiele naraz!

---

## 💡 Przydatne opcje

```bash
--headless              # Uruchom bez pokazywania przeglądarki (szybciej)
--advanced              # Zaawansowane zbieranie linków (jeśli zwykłe nie działa)
--output-suffix test1   # Dodaj sufiks do nazwy pliku
```

---

## ⚠️ Najczęstsze problemy

### Problem: "Nie znaleziono żadnych meczów"

**Rozwiązanie:**
```bash
# 1. Sprawdź bez --headless
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football

# 2. Użyj trybu urls z ręcznymi linkami
python livesport_h2h_scraper.py --mode urls --date 2025-10-05 --input my_matches.txt
```

### Problem: "Chromedriver error"

**Rozwiązanie:**
```bash
pip install --upgrade selenium webdriver-manager
```

### Problem: "Parsowanie H2H nie działa"

**Przyczyna:** Livesport zmienił strukturę HTML

**Rozwiązanie:** Użyj trybu `urls` z konkretnymi meczami które wiesz że mają H2H

---

## 🎓 Komenda do skopiowania (uniwersalna)

```bash
# Najprostsza - piłka nożna na dzisiaj
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --headless

# Najbardziej kompleksowa - wszystko
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football basketball volleyball handball rugby hockey --headless

# Najbardziej niezawodna - z własnym plikiem
python livesport_h2h_scraper.py --mode urls --date 2025-10-05 --input match_urls.txt --headless
```

**Zmień datę** na właściwą!

---

## 📞 Help

```bash
# Pokaż wszystkie opcje
python livesport_h2h_scraper.py --help
```

---

**Gotowy do startu?** Wybierz jeden z przykładów powyżej i uruchom! 🚀

