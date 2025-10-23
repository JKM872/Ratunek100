# ⚡ OPTYMALIZACJA SZYBKOŚCI SCRAPINGU

## 📊 OBECNA WYDAJNOŚĆ

- **Czas na mecz:** ~10 sekund
- **30 meczów:** ~5 minut
- **100 meczów:** ~17 minut

---

## 🚀 OPTYMALIZACJE (od najłatwiejszych)

### **POZIOM 1: Zmniejsz timeouty (ŁATWE)** ⭐

**Plik:** `livesport_h2h_scraper.py`

**Zmiana 1 (linia 428):**
```python
# BYŁO:
wait = WebDriverWait(driver, 8)
time.sleep(2.0)

# ZMIEŃ NA:
wait = WebDriverWait(driver, 5)  # -3s
time.sleep(1.0)                   # -1s
```

**Zmiana 2 (linia 439-442):**
```python
# BYŁO:
time.sleep(0.3)
time.sleep(0.3)

# ZMIEŃ NA:
time.sleep(0.1)  # -0.2s
time.sleep(0.1)  # -0.2s
```

**Wynik:** ~6-7s na mecz zamiast 10s ✅ **40% szybciej!**

---

### **POZIOM 2: Wyłącz zbędne funkcje (ŚREDNIE)**

**Opcja A: Pomijaj formę gdy nie potrzeba**
```bash
# Jeśli NIE używasz --only-form-advantage, forma jest niepotrzebna
# Można ją wyłączyć dla szybszości
```

**Opcja B: Zmniejsz liczbę H2H**
```python
# Plik: livesport_h2h_scraper.py, linia ~211
# BYŁO:
match_rows[:5]  # Pobiera 5 meczów H2H

# ZMIEŃ NA:
match_rows[:3]  # Pobiera 3 mecze H2H (wystarczy dla 60%)
```

**Wynik:** Dodatkowe 1-2s oszczędności na mecz

---

### **POZIOM 3: Wielowątkowość (TRUDNE)** 🔥

**Przetwarzaj wiele meczów równocześnie!**

**Nowy plik:** `scrape_parallel.py`
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from livesport_h2h_scraper import start_driver, process_match
import time

def process_match_wrapper(url, headless=True):
    """Wrapper dla wielowątkowości - każdy wątek ma własny driver"""
    driver = start_driver(headless=headless)
    try:
        result = process_match(url, driver)
        return result
    finally:
        driver.quit()

def scrape_parallel(urls, max_workers=3):
    """
    Przetwarza mecze równolegle.
    
    Args:
        urls: Lista URL-i meczów
        max_workers: Liczba równoległych przeglądarek (2-4 optymalne)
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Uruchom wszystkie zadania
        future_to_url = {
            executor.submit(process_match_wrapper, url): url 
            for url in urls
        }
        
        # Zbieraj wyniki w miarę ukończenia
        for i, future in enumerate(as_completed(future_to_url), 1):
            url = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
                print(f"[{i}/{len(urls)}] ✅ Ukończono: {url[:60]}...")
            except Exception as e:
                print(f"[{i}/{len(urls)}] ❌ Błąd: {e}")
    
    return results

# Użycie:
# urls = get_match_links_from_day(...)
# results = scrape_parallel(urls, max_workers=3)
```

**Wynik:** **3x szybciej!** (30 meczów w ~2 minuty zamiast 5)

⚠️ **Uwaga:** Wymaga więcej RAM (3-4 przeglądarki naraz)

---

### **POZIOM 4: Cache H2H (ZAAWANSOWANE)**

**Zapisuj H2H do cache aby nie pobierać ponownie**

```python
import json
import hashlib
from datetime import datetime, timedelta

CACHE_FILE = 'outputs/h2h_cache.json'
CACHE_EXPIRY_DAYS = 7  # Cache ważny 7 dni

def get_cache_key(url):
    """Generuj unikalny klucz dla URL"""
    return hashlib.md5(url.encode()).hexdigest()

def load_cache():
    """Załaduj cache z pliku"""
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_cache(cache):
    """Zapisz cache do pliku"""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def get_cached_h2h(url):
    """Pobierz H2H z cache jeśli dostępne i aktualne"""
    cache = load_cache()
    key = get_cache_key(url)
    
    if key in cache:
        cached = cache[key]
        cached_date = datetime.fromisoformat(cached['date'])
        
        # Sprawdź czy cache nie wygasł
        if datetime.now() - cached_date < timedelta(days=CACHE_EXPIRY_DAYS):
            return cached['h2h']
    
    return None
```

**Wynik:** Powtórne scrapowanie tych samych meczów **instant!**

---

## 📊 PODSUMOWANIE OPTYMALIZACJI

| Metoda | Trudność | Przyspieszenie | Czas (30 meczów) |
|--------|----------|----------------|------------------|
| Oryginał | - | - | ~5 min |
| Zmniejsz timeout | ⭐ Łatwe | 40% | ~3 min |
| Pomiń zbędne | ⭐⭐ Średnie | 50% | ~2.5 min |
| Wielowątkowość | ⭐⭐⭐ Trudne | 200% | ~1.5 min |
| Cache | ⭐⭐⭐⭐ Zaawansowane | ∞ (dla powtórek) | ~10 sek |

---

## 🎯 ZALECENIA

### **Dla początkujących:**
Użyj **Poziom 1** (zmniejsz timeouty) - łatwe i bezpieczne

### **Dla średnio zaawansowanych:**
Dodaj **Poziom 2** (pomiń zbędne) + **Poziom 1**

### **Dla zaawansowanych:**
Implementuj **wielowątkowość** (Poziom 3) - największe przyspieszenie!

---

## ⚠️ UWAGI

1. **Za niskie timeouty** mogą powodować błędy (strona nie załaduje się)
2. **Wielowątkowość** wymaga więcej RAM (~500MB na przeglądarkę)
3. **Livesport może zablokować** przy zbyt wielu równoległych requestach (max 3-4)

---

**Autor:** AI Assistant  
**Data:** 23.10.2025

