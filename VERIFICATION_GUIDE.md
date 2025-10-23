# 🎯 Przewodnik Weryfikacji Przewidywań

## Wprowadzenie

System weryfikacji automatycznie sprawdza trafność przewidywań z poprzednich dni i generuje szczegółowe raporty ze statystykami.

---

## 🚀 Jak to działa?

### Krok 1: Scraping z zapisem przewidywań

Gdy uruchamiasz standardowy scraping:

```bash
python scrape_and_notify.py --date 2025-10-07 --sports tennis football --to email@example.com --headless
```

System automatycznie:
- ✅ Scrapuje mecze i znajduje kwalifikujące się
- ✅ Wysyła email z typami
- ✅ **ZAPISUJE przewidywania do JSON** → `outputs/football_basketball_tennis_2025-10-07_predictions.json`

### Krok 2: Weryfikacja wyników (następnego dnia)

Gdy mecze się zakończą, uruchom weryfikację:

```bash
python verify_predictions.py --date 2025-10-07 --headless
```

System automatycznie:
- ✅ Wczytuje przewidywania z JSON
- ✅ Scrapuje wyniki zakończonych meczów
- ✅ Porównuje z przewidywaniami
- ✅ Generuje raport HTML → `outputs/verification_report_2025-10-07.html`

---

## 📊 Co zawiera raport?

### 1. Ogólne statystyki
- **Trafność ogólna** (%)
- **Trafność Tennis** vs **Trafność Team Sports**
- **ROI** (gdyby grać kursy po 100 PLN/mecz)

### 2. Szczegółowe tabele
- Top 5 najlepszych typów
- Top 5 najgorszych typów
- Pełna lista wyników

### 3. Analiza finansowa
- Zysk/Strata przy grze kursami
- Procent zwrotu (ROI)

---

## 🎯 Przykładowe użycie

### Scenariusz A: Weryfikacja wczorajszych typów

```bash
# Windows - automatyczny skrypt
verify_yesterday.bat

# Linux/Mac
python verify_predictions.py --date 2025-10-06 --headless
```

### Scenariusz B: Weryfikacja + wysłanie raportu emailem

```bash
python verify_predictions.py --date 2025-10-06 --headless --send-email --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx"
```

### Scenariusz C: Weryfikacja z widoczną przeglądarką (debugging)

```bash
python verify_predictions.py --date 2025-10-06
```

---

## 📈 Interpretacja wyników

### Trafność ogólna
- **>60%** - Bardzo dobry wynik! 🔥
- **50-60%** - Solidny wynik ✅
- **40-50%** - Wynik poniżej oczekiwań ⚠️
- **<40%** - Coś jest nie tak, przeanalizuj kryteria 🔴

### ROI (Return on Investment)
- **>10%** - Świetny zwrot! 💰
- **0-10%** - Pozytywny, ale mały zwrot 📈
- **-10-0%** - Niewielka strata 📉
- **<-10%** - Znaczna strata 🔴

### Tennis vs Team Sports
Porównaj trafność obu kategorii:
- Jeśli **Tennis >> Team Sports** → Zwiększ próg dla sportów drużynowych
- Jeśli **Team Sports >> Tennis** → Zwiększ próg dla tenisa
- Jeśli **podobne** → System działa poprawnie! ✅

---

## 🗂️ Struktura plików

```
outputs/
├── football_basketball_tennis_2025-10-07.csv          # Wszystkie mecze
├── football_basketball_tennis_2025-10-07_predictions.json  # PRZEWIDYWANIA
└── verification_report_2025-10-07.html                # RAPORT WERYFIKACJI
```

### Przykład predictions.json:

```json
[
  {
    "match_url": "https://www.livesport.com/pl/...",
    "home_team": "Manchester United",
    "away_team": "Liverpool",
    "match_time": "20:00",
    "qualifies": true,
    "win_rate": 0.80,
    "home_odds": 2.15,
    "away_odds": 3.40,
    "home_form": ["W", "W", "D", "W", "L"],
    "away_form": ["L", "W", "L", "L", "D"]
  },
  {
    "match_url": "https://www.livesport.com/pl/...",
    "player_a": "Novak Djokovic",
    "player_b": "Rafael Nadal",
    "advanced_score": 58.5,
    "favorite": "A",
    "home_odds": 1.85,
    "away_odds": 2.05
  }
]
```

---

## ⚙️ Parametry weryfikacji

```bash
python verify_predictions.py [OPTIONS]

Wymagane:
  --date YYYY-MM-DD          Data do weryfikacji

Opcjonalne:
  --headless                 Tryb bez widocznej przeglądarki
  --send-email              Wyślij raport emailem
  --to EMAIL                Email odbiorcy raportu
  --from-email EMAIL        Email nadawcy
  --password PASSWORD       Hasło aplikacji email
```

---

## 🔧 Troubleshooting

### Problem: "Brak pliku z przewidywaniami"

**Rozwiązanie:**
- Upewnij się, że najpierw uruchomiłeś scraping dla danej daty
- Sprawdź czy w folderze `outputs/` istnieje plik `*_predictions.json`

### Problem: "Żaden mecz się jeszcze nie zakończył"

**Rozwiązanie:**
- Zaczekaj aż mecze się zakończą (zazwyczaj wieczorem/nocą)
- Weryfikację uruchamiaj następnego dnia

### Problem: "Błąd scrapingu wyniku"

**Rozwiązanie:**
- Niektóre mecze mogą mieć niestandardowy format wyniku
- Sprawdź raport HTML - zawiera informacje o błędach
- Mecze z błędami są pomijane w statystykach

---

## 📅 Workflow typowego dnia

### Rano (np. 8:00)
```bash
# 1. Weryfikuj wczorajsze typy
verify_yesterday.bat
```

### Wieczorem (np. 17:00)
```bash
# 2. Scrapuj jutrzejsze mecze
python scrape_and_notify.py --date 2025-10-08 --sports football basketball tennis --to email@example.com --headless
```

### Następny wieczór (np. 21:00)
```bash
# 3. Weryfikuj dzisiejsze typy
python verify_predictions.py --date 2025-10-08 --headless --send-email --to email@example.com
```

---

## 🎓 Zaawansowane użycie

### Analiza długoterminowa

Możesz zbierać raporty z wielu dni i analizować:
- Trendy trafności
- Średni ROI
- Najlepsze dni tygodnia
- Najlepsze sporty/ligi

### Automatyzacja

Użyj **Task Scheduler** (Windows) lub **cron** (Linux) aby:
1. Codziennie rano weryfikować wczorajsze typy
2. Codziennie wieczorem scrapować jutrzejsze mecze
3. Wysyłać raporty emailem

---

## 📧 Format raportu email

Temat:
```
🎯 Raport Weryfikacji - 2025-10-07 (15/20 = 75.0%)
```

Zawartość:
- 📊 Karty ze statystykami
- ✅ Top 5 najlepszych typów
- ❌ Top 5 najgorszych typów
- 💰 Analiza ROI
- 📈 Porównanie Tennis vs Team Sports

---

## 💡 Wskazówki

1. **Regularność** - Weryfikuj każdego dnia dla lepszego obrazu
2. **Dokumentacja** - Zapisuj raporty HTML i analizuj trendy
3. **Dostosowanie** - Jeśli trafność <50%, zwiększ progi kwalifikacji
4. **ROI** - Nie graj kursów poniżej wartości (low odds = niski value)
5. **Forma** - Zwracaj uwagę na formę drużyn/zawodników w raportach

---

## 🚀 Quick Start

```bash
# Dzień 1 - Scrapuj mecze na jutro
python scrape_and_notify.py --date 2025-10-08 --sports football tennis --to email@example.com --headless

# Dzień 2 - Weryfikuj wyniki
python verify_predictions.py --date 2025-10-08 --headless --send-email --to email@example.com

# Gotowe! 📊
```

---

**Powodzenia w typowaniu! 🍀**

