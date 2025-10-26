# 🧪 Jak Przetestować Naprawy GitHub Actions

## Przygotowanie

1. **Commit i Push zmian:**
```bash
git add .
git commit -m "Naprawa GitHub Actions: timezone, kursy, osobne maile, tennis scoring"
git push origin main
```

2. **Czekaj na automatyczne uruchomienie** (o 22:00 UTC = 00:00 Polski czas) lub:

3. **Uruchom ręcznie:**
- Idź na GitHub → Actions
- Wybierz workflow (np. "Midnight Auto Scraping")
- Kliknij "Run workflow"

---

## 🕐 Test 1: Timezone (Data Scrappingu)

### Czego szukać w logach GitHub Actions:

```
🗓️ Scraping Football dla daty: 2025-10-26
```

**✅ SUKCES:** Data jest dzisiejsza (polska)
**❌ BŁĄD:** Data jest wczorajsza (UTC)

### Gdzie sprawdzić:
- GitHub → Actions → Wybierz run → Kliknij na job (np. "football")
- Szukaj sekcji "Run Football Scraping"

---

## 💰 Test 2: Kursy Bukmacherskie

### Czego szukać w logach:

```
💰 TRYB: Pomijam mecze BEZ KURSÓW bukmacherskich
   Pominięto X meczów bez kursów
```

### W emailu:

**✅ SUKCES:**
```
🎲 Kursy: Team A 1.85 | Team B 2.10
```

**❌ BŁĄD:**
```
🎲 Kursy: Team A nan | Team B nan
```

### Gdzie sprawdzić:
1. Logi GitHub Actions - sekcja "Run Football Scraping"
2. Email inbox - sprawdź kursy w HTML

---

## 📧 Test 3: Osobne Maile

### Dla każdego sportu (oprócz tennis) powinieneś dostać **2 MAILE:**

#### Mail 1: Przewaga Formy
```
Temat: "X meczów (🔥 PRZEWAGA FORMY + 💰 Z KURSAMI) - 2025-10-26"
```
- Zawiera tylko mecze z przewagą formy gospodarzy/gości
- Wszystkie mają kursy

#### Mail 2: Wszystkie Kwalifikujące
```
Temat: "Y meczów (💰 Z KURSAMI) - 2025-10-26"
```
- Zawiera wszystkie mecze kwalifikujące się (≥60% H2H)
- Wszystkie mają kursy

### Dla Tennis: **1 MAIL**
```
Temat: "Z meczów (💰 Z KURSAMI) - 2025-10-26"
```
- Tennis nie używa filtra "przewaga formy"
- Wszystkie mają kursy

### Czego szukać w logach:

```bash
# Mail 1
📧 Wysyłam mail 1/2: Zdarzenia z PRZEWAGĄ FORMY...
🔥 TRYB: Tylko mecze z PRZEWAGĄ FORMY (gospodarzy/gości)
💰 TRYB: Pomijam mecze BEZ KURSÓW bukmacherskich
✅ Email wysłany pomyślnie!

# Poczekaj 5 sekund
sleep 5

# Mail 2
📧 Wysyłam mail 2/2: Wszystkie kwalifikujące się...
💰 TRYB: Pomijam mecze BEZ KURSÓW bukmacherskich
✅ Email wysłany pomyślnie!
```

### Gdzie sprawdzić:
1. **Logi:** GitHub Actions → job → sekcja "Run [Sport] Scraping"
2. **Inbox:** Sprawdź czy dostałeś 2 maile dla każdego sportu

---

## 🎾 Test 4: Tennis Scoring

### Czego szukać w emailu:

**✅ SUKCES:**
```html
🎾 Score: 52.5/100 | Faworytem: Carlos Alcaraz
```

**❌ BŁĄD (przed naprawą):**
```html
🎾 Score: 0.0/100 | Faworytem: Równi
```

### Scenariusze:

#### Scenariusz A: Advanced Scoring Działa
- Score > 0 (np. 45-70/100)
- Faworytem: [Nazwisko zawodnika z wyższym scoring]

#### Scenariusz B: Advanced Scoring Rzucił Wyjątek
- Score = 0.0
- Faworytem: [Zawodnik z większą liczbą wygranych H2H]
  - **NIE** "Równi" (chyba że naprawdę H2H jest 50/50)

### Czego szukać w logach:

**Sukces:**
```
✅ Advanced scoring: 52.5/100
✅ Favorite: player_a
✅ Qualifies: True
```

**Fallback (błąd analysis):**
```
⚠️ Advanced analysis error: [treść błędu]
   📋 Full traceback: [szczegóły]
```

### Gdzie sprawdzić:
1. **Logi:** GitHub Actions → tennis job → szukaj "Advanced scoring" lub "Advanced analysis error"
2. **Email:** Sprawdź sekcję scoring dla każdego meczu tenisowego

---

## 🐛 Jeśli Coś Nie Działa

### Problem: Data nadal z poprzedniego dnia

**Diagnoza:**
```bash
# Sprawdź w logach:
TODAY=$(date +%Y-%m-%d)  # ❌ To źle
TODAY=$(TZ=Europe/Warsaw date +%Y-%m-%d)  # ✅ To dobrze
```

**Rozwiązanie:**
- Sprawdź czy commit zawiera zmiany w workflow files
- Upewnij się że push był na branch `main`

---

### Problem: Nadal są mecze bez kursów w mailach

**Diagnoza:**
```bash
# Sprawdź czy w komendzie jest:
--skip-no-odds  # Musi być!
```

**Rozwiązanie:**
- Sprawdź pliki workflow - czy dodano `--skip-no-odds`
- Uruchom ponownie workflow po commicie

---

### Problem: Tylko 1 mail zamiast 2

**Diagnoza:**
```bash
# Powinno być:
# Mail 1:
python scrape_and_notify.py ... --only-form-advantage --skip-no-odds
sleep 5
# Mail 2:
python scrape_and_notify.py ... --skip-no-odds
```

**Rozwiązanie:**
- Sprawdź workflow files - czy są 2 wywołania scrape_and_notify.py
- Upewnij się że sleep 5 jest między nimi

---

### Problem: Tennis scoring nadal 0.0

**Debug:**
1. **Włącz verbose mode:**
   - Edytuj `livesport_h2h_scraper.py`
   - Zmień linię 65: `VERBOSE = True`
   - Commit i push

2. **Sprawdź logi:**
   - Szukaj: "🔍 DEBUG Tennis Analysis:"
   - Sprawdź czy są dane H2H, forma, surface

3. **Szukaj błędów:**
   - Szukaj: "⚠️ Advanced analysis error:"
   - Sprawdź full traceback

**Możliwe przyczyny:**
- Brak danych H2H (pusty H2H)
- Błąd w `tennis_advanced_v3.py`
- Problem z importem modułu

---

## 📊 Checklist Weryfikacji

Po uruchomieniu GitHub Actions, sprawdź:

- [ ] **Timezone:** Data jest polska (nie UTC)
- [ ] **Kursy:** Wszystkie mecze w mailach mają kursy (nie "nan")
- [ ] **Maile:** 2 maile dla każdego sportu (oprócz tennis)
  - [ ] Mail 1: "PRZEWAGA FORMY + Z KURSAMI"
  - [ ] Mail 2: "Z KURSAMI"
- [ ] **Tennis:** 
  - [ ] Scoring > 0 (jeśli advanced analysis działa)
  - [ ] Faworyt określony (nie "Równi" jeśli H2H jest wyraźne)
  - [ ] Kursy nie są "nan"

---

## 🎉 Jeśli Wszystko Działa

**Gratulacje! 🚀**

Możesz teraz cieszyć się:
- Poprawną datą scrappingu (polska timezone)
- Mailami tylko z meczami z kursami
- Osobnymi mailami dla "przewagi formy" i "wszystkich kwalifikujących"
- Poprawnym tennis scoring z określonym faworytem

---

## 📞 Support

Jeśli napotkasz problemy:
1. Sprawdź logi GitHub Actions (szczegółowe błędy)
2. Włącz `VERBOSE = True` dla więcej informacji
3. Sprawdź dokumentację: `NAPRAWY_GITHUB_ACTIONS.md`

Data stworzenia: 26 października 2025

