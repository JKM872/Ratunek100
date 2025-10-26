# 🚀 JAK PRZETESTOWAĆ PROBLEM Z KURSAMI GOŚCI

## 🎯 Szybki Start

Masz rację - problem polega na tym że:
- ✅ Kursy **gospodarzy** są OK
- ❌ Kursy **gości** nie są znajdowane (lub źle)

---

## ⚡ KROK 1: Znajdź mecz który miał problem

Przykład z Twojego emaila:
```
🎲 Kursy: Ziraat Bankasi 1.23 | Fenerbahce 1.23 ❌
```

1. Otwórz Livesport.com
2. Znajdź ten mecz (Ziraat Bankasi vs Fenerbahce)
3. Skopiuj URL meczu

---

## ⚡ KROK 2: Uruchom test debug

```bash
python test_away_odds_debug.py "WKLEJ_URL_TUTAJ"
```

**Przykład:**
```bash
python test_away_odds_debug.py "https://www.livesport.com/pl/koszykowka/turcja/tbsl/ziraat-bankasi-fenerbahce/xxx/"
```

---

## ⚡ KROK 3: Czytaj output

### Jeśli zobaczysz:

#### ✅ Scenariusz A - FIX DZIAŁA:
```
🏠 DEBUG: Znaleziono kurs gospodarzy: 1.23
✈️  DEBUG: Znaleziono kurs gości: 4.50
💰 Znaleziono kursy (dedykowana metoda): 1.23 - 4.50

✅ SUKCES! Kursy wyglądają poprawnie
```

**Znaczy:** Problem naprawiony! Scraper teraz znajduje oba kursy. 🎉

---

#### ⚠️ Scenariusz B - LIVESPORT NIE MA KURSU GOŚCI:
```
🏠 DEBUG: Znaleziono kurs gospodarzy: 1.23
❌ DEBUG: Nie znaleziono kursu gości
⚠️  Znaleziono tylko 1 kurs: 1.23 - brak kursu dla gości!

Możliwe przyczyny:
   1. Livesport nie pokazuje kursu gości na tej stronie
   2. Kurs gości ma inną strukturę HTML
```

**Znaczy:** Livesport prawdopodobnie nie pokazuje kursu gości na stronie H2H.

**Co zrobić:**
- Otwórz mecz ręcznie na Livesport
- Przejdź do zakładki "H2H"
- **Czy widzisz OBA kursy tam?**
  - Jeśli NIE → to wyjaśnia problem
  - Jeśli TAK → prześlij mi screenshot

---

#### 🔍 Scenariusz C - ROZPOZNANIE KONTEKSTU:
```
🔍 DEBUG: Znalezione kursy (unikalne, fallback): [1.23, 4.50]
🏠 Kandydaci HOME: [1.23]
✈️  Kandydaci AWAY: [4.50]
💰 Znaleziono kursy (rozpoznanie kontekstu): 1.23 - 4.50
```

**Znaczy:** Dedykowana metoda nie zadziałała, ale rozpoznanie kontekstu pomogło!

---

## ⚡ KROK 4: Pełny test z scrapingiem

Jeśli test pokazał że fix działa, przetestuj na prawdziwych danych:

```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-25 --sports basketball --headless
```

Sprawdź logi - zobaczysz debug dla każdego meczu!

---

## ⚡ KROK 5: Weryfikacja

```bash
python verify_identical_odds.py
```

**Oczekiwane:**
```
✅ Wszystkie kursy są RÓŻNE (home != away)

Przykładowe kursy:
  • Ziraat Bankasi vs Fenerbahce: 1.23 vs 4.50 ✓
  • Lleida vs Granada: 1.38 vs 2.85 ✓
```

---

## 💡 CO JEŚLI NADAL PROBLEM?

### Prześlij mi:

1. **URL meczu** który testowałeś
2. **Pełny output** z `test_away_odds_debug.py`
3. **Screenshot** strony H2H tego meczu (czy kursy są widoczne?)

Znajdę dokładny selektor HTML dla kursów gości!

---

## 🎯 NAJCZĘSTSZE PYTANIA

**Q: Czy muszę testować każdy mecz?**  
A: Nie! Test jeden mecz który miał problem. Jeśli fix działa - będzie działać wszędzie.

**Q: Co jeśli Livesport nie pokazuje kursu gości na H2H?**  
A: To wyjaśnia problem. Możemy albo:
- Ładować główną stronę meczu dla kursów
- Akceptować brak kursów gości (kursy są opcjonalne)

**Q: Ile czasu zajmie test?**  
A: 30 sekund. Przeglądarka otworzy się, załaduje stronę, scraper spróbuje znaleźć kursy.

**Q: Co jeśli test pokazuje sukces ale w emailu nadal identyczne?**  
A: Uruchom pełny scraping ponownie - stare pliki CSV nie zostaną automatycznie naprawione.

---

## ✅ CHECKLIST

- [ ] 1. Znajdź mecz który miał problem (np. z emaila)
- [ ] 2. Skopiuj URL tego meczu z Livesport
- [ ] 3. Uruchom `python test_away_odds_debug.py "URL"`
- [ ] 4. Przeczytaj debug messages
- [ ] 5. Jeśli sukces - uruchom pełny scraping
- [ ] 6. Sprawdź `python verify_identical_odds.py`
- [ ] 7. Jeśli problem - prześlij output + screenshot

---

**Gotowe! Przetestuj i daj znać co pokazał test!** 🚀

**Plik z pełną dokumentacją:** `PROBLEM_KURSY_GOSCI.md`



