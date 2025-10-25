# 🔧 FIX: Brak meczów na GitHub Actions

## 🐛 PROBLEM

GitHub Actions zwraca:
```
✓ Znaleziono 0 meczów dla football
```

## ✅ CO ZOSTAŁO NAPRAWIONE

### 1. **Zwiększone timeouty dla GitHub Actions**

**Przed:**
- Football: 1.2s ładowania strony
- 2x scroll po 0.3s

**Po fix:**
- Football na GitHub: **2.5s ładowania** (2x dłużej)
- 3x scroll po 0.5s (więcej czasu)
- Lokalnie nadal szybko (1.2s)

### 2. **Lepsze debugowanie**

Teraz gdy nie znajdzie meczów, pokaże:
- Ile linków znalazło ogółem
- Przykładowe 5 linków
- Możliwe przyczyny problemu

---

## 🕵️ JAK ZDIAGNOZOWAĆ PROBLEM

### Krok 1: Sprawdź datę

W logach GitHub Actions szukaj:
```
📅 Data: 2025-10-25  ← SPRAWDŹ CZY TO DZISIAJ!
```

**Problem:** Data może być **z przyszłości** (2025 zamiast 2024)

**Rozwiązanie:**
1. Przy uruchamianiu workflow **zostaw pole "Date" PUSTE**
2. System użyje dzisiejszej daty automatycznie

---

### Krok 2: Sprawdź logi DEBUG

Nowe logi pokażą:
```
⚠️  BRAK MECZÓW dla football - DEBUG:
⚠️  Wzorce znalezione: {'/match/': 0, '/mecz/': 0, ...}
⚠️  Wszystkich linków na stronie: 245
⚠️  Przykładowe hrefs (pierwsze 5):
   1. /pilka-nozna/anglia/premier-league/
   2. /pilka-nozna/hiszpania/laliga/
   ...
```

**Analiza:**
- Jeśli `Wszystkich linków: 0` → Strona się nie załadowała
- Jeśli `Wszystkich linków: >100` ale `0 meczów` → Brak meczów na ten dzień lub selektory nie działają

---

## 🚀 JAK PRZETESTOWAĆ FIX

### Test 1: Ręczne uruchomienie z DZISIEJSZĄ datą

1. GitHub → **Actions**
2. Wybierz **"⚽ Football (Manual)"**
3. **"Run workflow"**
4. **ZOSTAW POLE "DATE" PUSTE!** ← WAŻNE
5. Kliknij **"Run workflow"**

**Oczekiwany wynik:**
```
📅 Data: 2024-10-24  (lub dzisiejsza)
🔧 Wykryto GitHub Actions - używam 2.5s timeoutu
🔍 Zbieranie linków...
   URL: https://www.livesport.com/pl/pilka-nozna/?date=2024-10-24
   ✓ Znaleziono 50+ meczów dla football  ← POWINNO BYĆ >0!
```

---

### Test 2: Sprawdź konkretną datę ręcznie

**Najpierw sprawdź na Livesport.com:**
1. Idź na: https://www.livesport.com/pl/pilka-nozna/
2. Wybierz dzisiejszą datę w kalendarzu
3. Zobacz ile meczów jest

**Potem uruchom workflow:**
- Jeśli Livesport pokazuje 50 meczów → GitHub też powinien znaleźć ~50
- Jeśli Livesport pokazuje 0 meczów → normalnie że GitHub też 0

---

## 🔄 JAK WYPCHNĄĆ FIX NA GITHUB

```bash
git add livesport_h2h_scraper.py FIX_BRAK_MECZOW_GITHUB_ACTIONS.md
git commit -m "🔧 Fix: Zwiększone timeouty dla GitHub Actions + lepsze debugowanie"
git push origin main
```

**Potem przetestuj** (Test 1 powyżej).

---

## 🎯 MOŻLIWE PRZYCZYNY "0 MECZÓW"

### Przyczyna 1: ❌ Data w przyszłości

**Problem:** Workflow używał daty **2025-10-25** (przyszłość!)

**Rozwiązanie:**
- **ZOSTAW POLE DATE PUSTE** przy uruchamianiu
- System użyje `$(date +%Y-%m-%d)` = dzisiejsza data

---

### Przyczyna 2: ❌ Za krótki timeout

**Problem:** Strona wymaga 2-3s na załadowanie na GitHub Actions (wolniejsze niż lokalnie)

**Rozwiązanie:** ✅ **NAPRAWIONE!**
- Zwiększono timeout z 1.2s na 2.5s dla GitHub Actions
- Lokalnie nadal szybko (1.2s)

---

### Przyczyna 3: ❌ Dzień bez meczów

**Problem:** Naprawdę nie ma meczów na ten dzień (np. przerwa sezonowa)

**Sprawdź:**
- Wejdź ręcznie na https://www.livesport.com/pl/pilka-nozna/
- Jeśli tam też 0 meczów → to normalne

**Rozwiązanie:**
- Uruchom na inny dzień (np. jutro, w weekend)
- Lub inny sport (basketball, volleyball)

---

### Przyczyna 4: ❌ Livesport zablokował GitHub IP

**Problem:** Livesport wykrył automatyczny scraping i blokuje

**Objawy:**
- Lokalnie działa (50+ meczów)
- GitHub Actions: 0 meczów
- Logi pokazują 0 linków na stronie

**Rozwiązanie:**
- Rate limiting (już jest: 1.0-1.7s między meczami)
- User-agent (już jest: Mozilla/5.0...)
- Poczekaj kilka godzin i spróbuj ponownie

---

## 📊 OCZEKIWANE WYNIKI PO FIX

### Dla Football (dzień tygodnia):
```
✓ Znaleziono 30-80 meczów dla football
```

### Dla Football (weekend):
```
✓ Znaleziono 100-300 meczów dla football
```

### Dla Basketball:
```
✓ Znaleziono 20-100 meczów dla basketball
```

### Dla Volleyball:
```
✓ Znaleziono 10-50 meczów dla volleyball
```

**Jeśli nadal 0 meczów:**
- Zobacz logi DEBUG (pokazują przykładowe linki)
- Sprawdź czy data jest dzisiejsza
- Sprawdź ręcznie na Livesport.com

---

## ✅ CHECKLIST

- [ ] Wypchnięto fix na GitHub (`git push`)
- [ ] Uruchomiono Test 1 (zostaw datę pustą)
- [ ] Sprawdzono logi - czy timeout wynosi 2.5s?
- [ ] Sprawdzono logi DEBUG - czy pokazuje linki?
- [ ] Sprawdzono datę - czy to dzisiejsza (2024)?
- [ ] Sprawdzono ręcznie na Livesport - czy są mecze?

---

**Data:** 24.10.2025  
**Status:** ✅ FIX GOTOWY DO TESTU  
**Next:** Wypchnij i przetestuj Test 1

