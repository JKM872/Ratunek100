# Naprawy GitHub Actions - Podsumowanie

## 📋 Problemy które zostały naprawione

### 1. ✅ Problem z Timezone (Godzina/Data)
**Problem:** GitHub Actions używał UTC zamiast czasu polskiego, przez co scraping pobierał mecze z poprzedniego dnia.

**Rozwiązanie:**
- Zmieniono wszystkie wystąpienia `date +%Y-%m-%d` na `TZ=Europe/Warsaw date +%Y-%m-%d`
- Dotyczy wszystkich workflow files:
  - `.github/workflows/midnight-auto-scraping.yml` (wszystkie 6 sportów)
  - `.github/workflows/daily-scraping.yml`
  - `.github/workflows/all-sports-scraping.yml`

**Przykład:**
```bash
# PRZED:
TODAY=$(date +%Y-%m-%d)

# PO:
TODAY=$(TZ=Europe/Warsaw date +%Y-%m-%d)
```

---

### 2. ✅ Problem z Kursami Bukmacherskimi
**Problem:** GitHub Actions nie pomijał meczów bez kursów, co powodowało że w mailach były zdarzenia z kursami "nan".

**Rozwiązanie:**
- Dodano flagę `--skip-no-odds` do wszystkich wywołań `scrape_and_notify.py` w workflow
- Ta flaga pomija mecze które nie mają obu kursów (home_odds i away_odds)
- Implementacja już istniała w kodzie (`email_notifier.py` linie 362-371), trzeba było tylko ją włączyć w workflow

**Efekt:**
- Wszystkie maile będą zawierać TYLKO mecze z dostępnymi kursami bukmacherskimi
- Mecze bez kursów nie będą wysyłane w mailach

---

### 3. ✅ Problem z Osobnymi Mailami
**Problem:** GitHub Actions wysyłał tylko 1 mail dla każdego sportu. Użytkownik chciał 2 osobne maile:
- Mail 1: Zdarzenia z **PRZEWAGĄ FORMY** 🔥
- Mail 2: Wszystkie **kwalifikujące się** zdarzenia

**Rozwiązanie:**
Każdy sport w workflow teraz wysyła 2 maile:

**Mail 1 - Przewaga Formy:**
```bash
python scrape_and_notify.py \
  --date $TODAY \
  --sports <sport> \
  --only-form-advantage \
  --skip-no-odds \
  ...
```

**Mail 2 - Wszystkie Kwalifikujące:**
```bash
python scrape_and_notify.py \
  --date $TODAY \
  --sports <sport> \
  --skip-no-odds \
  ...
```

**Wyjątek - Tennis:**
- Tennis wysyła tylko 1 mail (bez filtra `--only-form-advantage`)
- Działa na advanced scoring, więc przewaga formy nie ma sensu

**Odstęp między mailami:** 5 sekund (`sleep 5`)

---

### 4. ✅ Problem z Tennis Scoring
**Problem:** 
- Scoring pokazywał się jako `0.0/100`
- Faworyt pokazywał się jako "Równi" nawet gdy jeden zawodnik wygrał więcej meczów H2H
- Kursy pokazywały "nan"

**Rozwiązanie:**

#### A) Lepsza Obsługa Błędów w `livesport_h2h_scraper.py`
- Dodano szczegółowe debugowanie (`VERBOSE` mode)
- Dodano fallback logikę gdy advanced analysis rzuca wyjątek
- Dodano określanie faworyta na podstawie H2H gdy scoring = 0 lub favorite = 'even'

**Kod (linie 1855-1892):**
```python
# POPRAWKA: Określ faworyta bardziej precyzyjnie
favorite_key = analysis['details'].get('favorite', 'unknown')

# Jeśli scoring = 0 lub favorite = 'even', określ faworyta na podstawie H2H
if out['advanced_score'] == 0 or favorite_key == 'even':
    if player_a_wins > player_b_wins:
        out['favorite'] = 'player_a'
    elif player_b_wins > player_a_wins:
        out['favorite'] = 'player_b'
    else:
        out['favorite'] = 'even'  # Naprawdę równi
else:
    out['favorite'] = favorite_key
```

#### B) Fallback przy Błędzie
Jeśli advanced analysis rzuci wyjątek:
1. Wypisuje szczegółowy error (z traceback w trybie VERBOSE)
2. Używa prostej logiki: `qualifies = (player_a_wins >= 1 and player_a_wins > player_b_wins)`
3. Ustawia `advanced_score = 0.0`
4. **NOWE:** Określa faworyta na podstawie H2H

**Efekt:**
- Nawet gdy advanced scoring nie działa, system określi faworyta
- W mailach pokaże się który zawodnik jest faworytem (a nie "Równi")
- Lepsze logowanie błędów do debugowania

---

## 📊 Podsumowanie Zmian w Workflow Files

### Zmienione pliki:
1. `.github/workflows/midnight-auto-scraping.yml` - **6 sportów** (football, basketball, handball, volleyball, hockey, tennis)
2. `.github/workflows/daily-scraping.yml` - **volleyball**
3. `.github/workflows/all-sports-scraping.yml` - **multi-sport manual**

### Dla każdego sportu (oprócz tennis):
- ✅ Timezone: `TZ=Europe/Warsaw date +%Y-%m-%d`
- ✅ Mail 1: `--only-form-advantage --skip-no-odds`
- ✅ Mail 2: `--skip-no-odds`
- ✅ Odstęp: `sleep 5` między mailami

### Dla tennis:
- ✅ Timezone: `TZ=Europe/Warsaw date +%Y-%m-%d`
- ✅ Tylko 1 mail: `--skip-no-odds` (bez `--only-form-advantage`)

---

## 🎯 Rezultaty

### Przed naprawami:
- ❌ Scraping z poprzedniego dnia (UTC)
- ❌ Maile z meczami bez kursów ("nan")
- ❌ Tylko 1 mail na sport
- ❌ Tennis: scoring = 0, faworyt = "Równi"

### Po naprawach:
- ✅ Scraping z poprawnej daty (Europe/Warsaw)
- ✅ Maile TYLKO z meczami z kursami
- ✅ 2 osobne maile na sport (forma + wszystkie)
- ✅ Tennis: poprawne określanie faworyta + lepsze error handling

---

## 🚀 Jak Przetestować

### Test 1: Timezone
```bash
# Na GitHub Actions (po pushu)
# Sprawdź czy log pokazuje:
🗓️ Scraping dla daty: 2025-10-26  # (data polska, nie UTC)
```

### Test 2: Kursy
```bash
# Sprawdź czy w mailach wszystkie mecze mają kursy
# W email HTML powinno być:
🎲 Kursy: Team A [X.XX] | Team B [Y.YY]
# NIE powinno być "nan"
```

### Test 3: Osobne Maile
```bash
# Dla każdego sportu (oprócz tennis) powinieneś dostać 2 maile:
# Mail 1: "🔥 PRZEWAGA FORMY + 💰 Z KURSAMI - YYYY-MM-DD"
# Mail 2: "N meczów (💰 Z KURSAMI) - YYYY-MM-DD"
```

### Test 4: Tennis
```bash
# Sprawdź czy tennis pokazuje:
🎾 Score: X.X/100 | Faworytem: [Nazwisko Zawodnika]
# NIE powinno być "Równi" jeśli jeden zawodnik ma przewagę H2H
```

---

## 📝 Dodatkowe Notatki

### Verbose Mode dla Debugowania
Jeśli chcesz więcej szczegółów w logach GitHub Actions:
- Ustaw `VERBOSE = True` w `livesport_h2h_scraper.py` (linia 65)
- Zobaczysz szczegółowe logi tennis analysis

### Próg Tennis Scoring
- Bazowy próg: **45/100 pkt**
- Adaptacyjny próg: **30-50 pkt** (zależnie od dostępności danych)
- Im więcej danych (H2H, forma, surface), tym wyższy próg

### Dokumentacja
- `email_notifier.py` - logika filtrowania kursów (linie 362-371)
- `tennis_advanced_v3.py` - system scoringowy (linia 27-65)
- `livesport_h2h_scraper.py` - główna logika scrapingu

---

## ✅ Status

**Wszystkie problemy naprawione!**

Data naprawy: 26 października 2025

Gotowe do push na GitHub i testowania w GitHub Actions. 🎉

