# 🚀 GitHub Actions Test Guide - FINAL STEP

## ✅ UKOŃCZONE:
- [x] Performance optimization (parallel mode + retry logic)
- [x] GitHub Secrets dodane (APP_URL, APP_API_KEY)
- [x] Workflow updated (midnight-auto-scraping.yml)
- [x] Commit & Push do GitHub

---

## 🎯 TERAZ: Przetestuj GitHub Actions!

### **KROK 1: Otwórz GitHub Actions**

Wejdź tutaj: https://github.com/JKM872/Ratunek100/actions

---

### **KROK 2: Wybierz Workflow**

Kliknij na: **"Midnight Auto Scraping (All Sports)"**

---

### **KROK 3: Uruchom ręcznie**

1. Kliknij przycisk: **"Run workflow"** (po prawej stronie)
2. Zostaw domyślne ustawienia (branch: `main`)
3. Kliknij: **"Run workflow"** (zielony przycisk)

---

### **KROK 4: Obserwuj Logi**

Po uruchomieniu:

1. Kliknij na workflow run (pojawi się na liście)
2. Kliknij na job (np. "football")
3. Rozwiń sekcję: **"⚽ Run Football Scraping"**

**Oczekiwane logi:**
```
🗓️ Scraping Football dla daty: 2025-11-03
═══════════════════════════════════════════════════════════
📧 MAIL 1/2: Zdarzenia z PRZEWAGĄ FORMY + KURSY (PARALLEL)
═══════════════════════════════════════════════════════════

🚀 TRYB RÓWNOLEGŁY: Przetwarzam 5 meczów jednocześnie...
   ⚡ To przyspieszy proces 3-4x!

[1/214] ✅ Team A vs Team B
[2/214] ✅ Team C vs Team D
...

✅ Przetworzono 214 meczów równolegle!
💾 Zapisywanie finalnych wyników...
✅ Zapisano do: outputs/livesport_h2h_2025-11-03_football_EMAIL.csv

📊 PODSUMOWANIE SCRAPINGU:
   Przetworzono: 214 meczów
   Kwalifikujących się: X

📧 Wysyłanie powiadomienia email...
✅ SUKCES! Email wysłany.

🔗 Wysyłanie danych do aplikacji UI...
   URL: https://livesport-scraper-ui-0393f6f2096e.herokuapp.com
   ✅ Sukces! Status: 200
   📨 Odpowiedź: {'success': True, 'received': 214, 'saved': X}
```

---

### **KROK 5: Sprawdź Rezultaty**

#### 1. **Email** ✉️
Sprawdź: jakub.majka.zg@gmail.com

Powinieneś dostać **2 maile** dla każdego sportu:
- Mail 1: Przewaga formy + kursy
- Mail 2: Wszystkie kwalifikujące + kursy

**Razem: 10 maili** (5 sportów × 2 maile)

#### 2. **Dashboard** 🖥️
Otwórz: https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/

Powinieneś zobaczyć:
- ✅ Nowe mecze w tabeli
- ✅ Zaktualizowane statystyki
- ✅ "Ostatnia aktualizacja" = dzisiejsza data

#### 3. **API Test** 🔗
Otwórz w przeglądarce:
```
https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/api/matches
```

Powinieneś zobaczyć JSON z meczami:
```json
{
  "matches": [
    {
      "id": 1,
      "sport": "football",
      "home_team": "...",
      "away_team": "...",
      "home_odds": 1.85,
      "away_odds": 2.10,
      ...
    }
  ]
}
```

---

## 📊 OCZEKIWANE WYNIKI:

| Sport | Czas (bez --parallel) | Czas (z --parallel) | Przyspieszenie |
|-------|----------------------|---------------------|----------------|
| Football | ~40-50 min | ~12-15 min | **3-4x** ⚡ |
| Basketball | ~15-20 min | ~5-7 min | **3x** ⚡ |
| Handball | ~10-15 min | ~3-5 min | **3x** ⚡ |
| Volleyball | ~10-15 min | ~3-5 min | **3x** ⚡ |
| Hockey | ~10-15 min | ~3-5 min | **3x** ⚡ |
| Tennis | ~20-30 min | ~7-10 min | **3x** ⚡ |

**TOTAL**: ~100-140 min → **~30-45 min** 🎉

---

## 🐛 Troubleshooting:

### Problem: Workflow nie widzi --parallel
**Rozwiązanie**: Pull najnowsze zmiany z GitHub i uruchom ponownie

### Problem: APP_URL lub APP_API_KEY nie działa
**Rozwiązanie**: Sprawdź GitHub Secrets:
1. Wejdź: https://github.com/JKM872/Ratunek100/settings/secrets/actions
2. Sprawdź czy są:
   - `APP_URL` = `https://livesport-scraper-ui-0393f6f2096e.herokuapp.com`
   - `APP_API_KEY` = `super-secret-key-12345`

### Problem: Email nie przychodzi
**Rozwiązanie**: Sprawdź:
1. `EMAIL_PASSWORD` secret jest ustawiony
2. Hasło to App Password (nie zwykłe hasło Gmail)
3. Link: https://myaccount.google.com/apppasswords

### Problem: Timeout (6 hours exceeded)
**Rozwiązanie**: To normalne dla 2500+ meczów. Workflow działa, GitHub Actions ma limit 6h.
Jeśli przekracza limit, zmniejsz liczbę sportów lub podziel na osobne runnery.

---

## 🎉 SUCCESS CRITERIA:

Workflow jest **SUKCES** jeśli:

✅ Wszystkie 5 sportów zakończone (football, basketball, handball, volleyball, hockey, tennis)  
✅ Każdy sport wysłał 2 maile (10 maili total)  
✅ Dashboard pokazuje nowe mecze  
✅ API zwraca dane JSON  
✅ Czas total: 30-45 min (zamiast 100-140 min)  
✅ Exit Code: 0 dla wszystkich jobów  

---

## 📅 AUTOMATYZACJA:

Po pomyślnym teście, workflow będzie uruchamiany automatycznie:

**Codziennie o 00:00 UTC (01:00 CET)**

Możesz zmienić czas w `.github/workflows/midnight-auto-scraping.yml`:
```yaml
on:
  schedule:
  - cron: '0 0 * * *'  # ← TUTAJ ZMIEŃ
```

Przykłady:
- `0 0 * * *` = 00:00 UTC (01:00 CET)
- `0 11 * * *` = 11:00 UTC (12:00 CET)
- `30 10 * * *` = 10:30 UTC (11:30 CET)

---

## 🚀 NEXT STEPS (po sukcesie):

1. **Monitoruj przez tydzień** - sprawdzaj czy maile przychodzą codziennie
2. **Sprawdź success rate** - czy kursy są pobierane (95%+ expected)
3. **Optymalizuj Bundle Size** (opcjonalnie) - 826KB → 500-600KB
4. **Dodaj więcej sportów** (opcjonalnie) - rugby, baseball, etc.

---

## 📞 SUPPORT:

Jeśli coś nie działa:

1. **Sprawdź logi** w GitHub Actions
2. **Sprawdź Dashboard** - czy dane się zapisują
3. **Sprawdź Email** - czy przychodzą
4. **Uruchom lokalnie** z `--max-matches 5` dla testu

---

**Status**: ✅ GOTOWE DO TESTU  
**Następny krok**: Uruchom workflow na GitHub Actions!  
**Link**: https://github.com/JKM872/Ratunek100/actions

---

🎯 **DZIAŁAJ TERAZ!** Kliknij link powyżej i "Run workflow"! 🚀
