# 🚀 Szybki Start: Fokus na Drużynach Gości

## ⚡ Najszybszy sposób (Windows)

### Krok 1: Edytuj datę
Otwórz plik `run_all_sports_away_focus.bat` i zmień datę:
```batch
SET DATE=2025-10-12
```

### Krok 2: Uruchom
Kliknij dwukrotnie na plik:
```
run_all_sports_away_focus.bat
```

### Krok 3: Sprawdź wyniki
Wyniki w folderze: `outputs/livesport_h2h_2025-10-12_*_AWAY_FOCUS.csv`

---

## 💻 Z wiersza poleceń

### Wszystkie sporty
```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football basketball volleyball handball rugby hockey --away-team-focus --headless
```

### Tylko piłka nożna
```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football --away-team-focus --headless
```

---

## 📊 Co otrzymujesz?

### Przykładowy wynik w konsoli:
```
[1/150] 🔍 Przetwarzam: https://www.livesport.com/...
   📊 Podstawowo kwalifikuje (GOŚCIE: Liverpool, H2H: 80%) - sprawdzam formę...
   ✅ KWALIFIKUJE + PRZEWAGA FORMY GOŚCI! 🔥
      Zespół fokusowany: Liverpool
      H2H: 4/5 (80%)
      Forma: Arsenal [L-L-D-W-L] | Liverpool [W-W-W-W-D]
```

### Plik CSV:
```csv
match_url,home_team,away_team,home_wins,away_wins,win_rate,qualifies,focus_team
https://...,Arsenal,Liverpool,1,4,0.80,True,away
```

---

## 🔥 Najlepsze typy

Łącz filtry dla TOP meczów:

### Goście + konkretne ligi
```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football --leagues premier-league la-liga bundesliga --away-team-focus --headless
```

### Goście + wszystkie sporty
```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football basketball volleyball handball rugby hockey --away-team-focus --headless
```

---

## 📖 Więcej informacji

- **Pełny przewodnik:** [AWAY_TEAM_FOCUS_GUIDE.md](AWAY_TEAM_FOCUS_GUIDE.md)
- **Główna dokumentacja:** [README.md](README.md)
- **Email setup:** [EMAIL_SETUP.md](EMAIL_SETUP.md)

---

**Gotowe! Rozpocznij teraz analizę meczów gdzie goście mają przewagę!** 🚀

