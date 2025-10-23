# 🎾 TENIS - Specjalna logika kwalifikacji

## 🎯 **DLACZEGO INNA LOGIKA?**

Tennis to **sport indywidualny** - nie ma "gospodarza" i "gościa" w tradycyjnym sensie sportów drużynowych. Dlatego potrzebuje **innej logiki kwalifikacji**.

---

## ⚽ **SPORTY DRUŻYNOWE (Football, Basketball, etc.):**

### **Kryterium kwalifikacji:**
```
✅ KWALIFIKUJE SIĘ = Gospodarz wygrał ≥2 z ostatnich 5 H2H meczów
```

### **Przykład:**
```
Newcastle (u siebie) vs Nottingham (na wyjeździe)

H2H ostatnie 5 meczów:
1. Newcastle 2-1 Nottingham ✅ (Newcastle wygrał)
2. Nottingham 0-3 Newcastle ✅ (Newcastle wygrał)  
3. Newcastle 1-1 Nottingham ❌ (remis)
4. Nottingham 2-1 Newcastle ❌ (Nottingham wygrał)
5. Newcastle 3-0 Nottingham ✅ (Newcastle wygrał)

Wynik: Newcastle wygrał 3/5 meczów
✅ KWALIFIKUJE SIĘ (≥2 wygrane)
```

---

## 🎾 **TENIS (Sport indywidualny):**

### **Kryterium kwalifikacji:**
```
✅ KWALIFIKUJE SIĘ = Zawodnik A:
   1. Wygrał co najmniej 1 mecz przeciwko B w historii H2H
   2. MA WIĘCEJ wygranych niż B w bezpośrednich pojedynkach
```

### **Przykład 1: Djokovic vs Nadal**
```
H2H historia (wszystkie mecze):
1. Djokovic 3-1 Nadal ✅ (Djokovic wygrał)
2. Nadal 3-2 Djokovic ❌ (Nadal wygrał)
3. Djokovic 2-0 Nadal ✅ (Djokovic wygrał)
4. Djokovic 3-1 Nadal ✅ (Djokovic wygrał)
5. Nadal 3-2 Djokovic ❌ (Nadal wygrał)

H2H Bilans: Djokovic 3-2 Nadal

✅ KWALIFIKUJE SIĘ!
   - Djokovic wygrał ≥1 mecz ✅
   - Djokovic ma więcej wygranych (3 > 2) ✅
```

### **Przykład 2: Murray vs Federer**
```
H2H historia:
1. Federer 3-0 Murray ❌ (Federer wygrał)
2. Murray 2-1 Federer ✅ (Murray wygrał)
3. Federer 3-1 Murray ❌ (Federer wygrał)
4. Federer 3-2 Murray ❌ (Federer wygrał)

H2H Bilans: Murray 1-3 Federer

❌ NIE KWALIFIKUJE SIĘ
   - Murray wygrał ≥1 mecz ✅
   - Murray ma MNIEJ wygranych (1 < 3) ❌
```

### **Przykład 3: Alcaraz vs Sinner (brak H2H)**
```
H2H historia: BRAK MECZÓW

❌ NIE KWALIFIKUJE SIĘ
   - Alcaraz wygrał 0 meczów ❌
```

---

## 📊 **PORÓWNANIE:**

| Aspekt | Sporty drużynowe | Tenis |
|--------|------------------|-------|
| **Format meczu** | Gospodarz vs Gość | Zawodnik A vs Zawodnik B |
| **Rola miejsca** | Ważna (home advantage) | Mniejsza (neutralny kort w większości) |
| **Kryterium** | ≥2 wygrane gospodarza w ostatnich 5 | Więcej wygranych ogólnie w H2H |
| **Minimum wygranych** | 2 | 1 |
| **Zakres H2H** | Ostatnie 5 meczów | Wszystkie mecze w historii |
| **Przykład** | `Newcastle 3/5 ✅` | `Djokovic 15-12 Nadal ✅` |

---

## 🤔 **DLACZEGO TA LOGIKA?**

### **1. Brak "gospodarza" w tenisie**
W tenisie nie ma home advantage jak w piłce nożnej. Zawodnicy grają na neutralnych kortach (poza turniejami poza ATP).

### **2. Historia H2H jest kluczowa**
W tenisie, jeśli zawodnik A wygrywał z B w przeszłości, **przewaga psychologiczna** jest ogromna. Bilans 10-2 oznacza dominację.

### **3. Styl gry ma znaczenie**
Niektórzy zawodnicy mają "przewagę stylu" nad innymi. Np.:
- Nadal dominuje Djokovica na ziemi (clay)
- Federer ma przewagę nad Murray na trawie (grass)

### **4. Przykłady z rzeczywistości:**
```
Nadal vs Djokovic (wszystkie powierzchnie): 29-30 dla Djokovica
→ Djokovic ma lekką przewagę

Nadal vs Djokovic (tylko clay): 20-8 dla Nadala
→ Nadal DOMINUJE na ziemi!
```

---

## 🎮 **JAK TO DZIAŁA W KODZIE?**

### **Funkcja: `process_match_tennis()`**

```python
# 1. Pobierz H2H historię
h2h = parse_h2h_from_soup(soup, player_a)

# 2. Policz wygrane każdego zawodnika
player_a_wins = 0  # Zawodnik A
player_b_wins = 0  # Zawodnik B

for match in h2h:
    if match['winner'] == player_a:
        player_a_wins += 1
    elif match['winner'] == player_b:
        player_b_wins += 1

# 3. KRYTERIA KWALIFIKACJI
qualifies = (
    player_a_wins >= 1  AND  # Wygrał minimum 1 mecz
    player_a_wins > player_b_wins  # Ma więcej wygranych
)
```

### **Output:**
```python
{
    'home_team': 'Novak Djokovic',
    'away_team': 'Rafael Nadal',
    'match_time': '05.10.2025 18:00',
    'home_wins_in_h2h_last5': 15,  # Wygrane Djokovica
    'away_wins_in_h2h': 12,         # Wygrane Nadala
    'h2h_count': 27,                # Łącznie meczów
    'qualifies': True               # 15 > 12 ✅
}
```

---

## 📧 **EMAIL - JAK TO WYGLĄDA?**

### **Football (sport drużynowy):**
```
⚽ PIŁKA NOŻNA (5 meczów)

🕐 15:00  Newcastle vs Nottingham
   📊 H2H: 5/5 wygranych gospodarzy
```

### **Tennis (sport indywidualny):**
```
🎾 TENIS (3 mecze)

🕐 18:00  Novak Djokovic vs Rafael Nadal
   📊 H2H: 15-12 dla Djokovica (przewaga)
   
🕐 20:00  Carlos Alcaraz vs Jannik Sinner
   📊 H2H: 8-5 dla Alcaraza (przewaga)
```

---

## 🚀 **UŻYCIE:**

### **Tylko tennis:**
```bash
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports tennis \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "app_password" \
  --headless
```

### **Tennis + Football:**
```bash
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports football tennis \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "app_password" \
  --headless
```

### **Wszystkie sporty (+ tennis):**
```bash
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports football basketball volleyball handball rugby hockey tennis \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "app_password" \
  --headless
```

---

## 💡 **MOŻLIWE ROZSZERZENIA:**

### **1. Filtrowanie po powierzchni (tennis):**
```python
# Tylko mecze na ziemi (clay)
if 'clay' in match_info or 'Roland Garros' in tournament:
    ...
```

### **2. Wagowanie ostatnich meczów:**
```python
# Nowsze mecze mają większą wagę
recent_matches_weight = 2.0
older_matches_weight = 1.0
```

### **3. Minimalny próg meczów:**
```python
# Kwalifikuj tylko jeśli ≥5 meczów w historii
if h2h_count >= 5 and player_a_wins > player_b_wins:
    qualifies = True
```

---

## 🎯 **PODSUMOWANIE:**

| | Drużynowe | Tenis |
|---|---|---|
| **Kryterium** | ≥2/5 wygranych gospodarza | Więcej wygranych w H2H + ≥1 wygrana |
| **Przewaga** | Home advantage | Styl gry + psychologia |
| **Zakres** | Ostatnie 5 | Cała historia |
| **Przykład** | `Newcastle 3/5` | `Djokovic 15-12 Nadal` |

**✅ Tennis teraz działa z dedykowaną logiką!** 🎾

---

**Pytania? Chcesz dodać inne sporty indywidualne? (badminton, squash, etc.) Daj znać!** 😊


