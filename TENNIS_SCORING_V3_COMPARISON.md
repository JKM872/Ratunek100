# 🎾 Tennis Scoring V3 - Nowa Metodologia

## 📅 Data: 2025-10-07

---

## 🎯 **CEL:**

Przeprojektować system scoringu aby:
- ✅ **Zwiększyć dokładność predykcji** (obecnie 61.5%)
- ✅ **Fokus na formę**, nie ranking
- ✅ **Uwzględniać nawierzchnię** jako kluczowy czynnik
- ✅ **Wykrywać momentum** i pewność siebie zawodników
- ❌ **NIE obniżać progu** - chcemy JAKOŚĆ, nie ilość

---

## 📊 **PORÓWNANIE: V2 vs V3**

### **Wagi czynników:**

| Czynnik | V2 (stary) | V3 (nowy) | Zmiana |
|---------|-----------|-----------|---------|
| **H2H** | 50% (50 pkt) | 40% (40 pkt) | -10% ⬇️ |
| **Ranking** | 25% (25 pkt) | ~~0%~~ | **USUNIĘTY** ❌ |
| **Forma ogólna** | 15% (15 pkt) | 30% (30 pkt) | +15% ⬆️ |
| **Forma na nawierzchni** | 10% (10 pkt) | 20% (20 pkt) | +10% ⬆️ |
| **Momentum** | - | **10% (10 pkt)** | **NOWY** ✨ |
| **PRÓG** | 40 pkt | **45 pkt** | +5 pkt (wyższy) ⬆️ |

---

## 🔍 **SZCZEGÓŁY ZMIAN:**

### 1. **H2H z wagą czasową (40%)**

#### V2 (stary):
```python
# Każda wygrana = 10 pkt, bez względu na datę
points = wins_difference * 10
```

#### V3 (nowy):
```python
# Nowsze mecze liczą się BARDZIEJ
if mecz_z_ostatnich_6_miesięcy:
    points *= 2.0  # Podwójna waga
elif mecz_z_ostatnich_12_miesięcy:
    points *= 1.5  # 1.5x waga
elif mecz_sprzed_2_lat:
    points *= 0.5  # Połowa wagi
```

**Przykład:**
- Mecz sprzed miesiąca: **16 pkt**
- Mecz sprzed roku: **12 pkt**
- Mecz sprzed 3 lat: **4 pkt**

---

### 2. **Ranking USUNIĘTY** ❌

**Powód:** Ranking często nie odzwierciedla aktualnej formy:
- Zawodnik #50 w świetnej formie > Zawodnik #10 w kryzysie
- Ranking uwzględnia cały rok, nie ostatnie tygodnie
- **Forma jest ważniejsza niż pozycja w rankingu**

**Zastąpiony przez:** Jakość wygranych (z kim wygrywał ostatnio)

---

### 3. **Forma aktualna (30%) - znacznie rozbudowana**

#### V2 (stary):
```python
# Tylko ostatnie 5 meczów, proste liczenie W vs L
wins_a = 4, wins_b = 2
points = (4 - 2) * 3 = 6 pkt
```

#### V3 (nowy):
```python
# Ostatnie 10 meczów + analiza trendów
1. Bazowe punkty: wins_difference * 3
2. Ostatnie 3 mecze liczą się BARDZIEJ (+5 pkt bonus)
3. Seria 5+ zwycięstw: +8 pkt
4. Jakość przeciwników: +5 pkt za wygrane z top zawodnikami
5. Trend: +2 pkt jeśli forma się poprawia
```

**Przykład:**
```
Zawodnik A: W-W-W-L-W-W-W-W-L-W (8/10, seria 3, trend ↑)
Zawodnik B: W-L-W-L-L-L-W-L-W-L (4/10, brak serii)

V2: (8-4) * 3 = 12 pkt
V3: 12 (bazowe) + 5 (ostatnie 3) + 8 (seria) + 2 (trend) = 27 pkt ✅
```

---

### 4. **Forma na nawierzchni (20%) - KLUCZOWA**

#### V2 (stary):
```python
# Tylko procentowa różnica win rate
advantage = 0.82 - 0.64 = 0.18
points = 0.18 * 50 = 9 pkt
```

#### V3 (nowy):
```python
1. Bazowe punkty: różnica_win_rate * 25
2. Specjalista (>80% WR + duża przewaga): +8 pkt
3. Doświadczenie (10+ meczów na nawierzchni): +5 pkt
4. Aktualna forma NA TEJ nawierzchni: +0 do +10 pkt
```

**Przykład:**
```
Zawodnik A na hard court:
- Win rate: 82% (45/55)
- Ostatnie 5 na hard: W-W-W-L-W (80%)
- Doświadczenie: 55 meczów

Zawodnik B na hard court:
- Win rate: 64% (32/50)
- Ostatnie 5 na hard: L-W-L-W-L (40%)
- Doświadczenie: 50 meczów

V2: (0.82-0.64) * 50 = 9 pkt
V3: 4.5 (base) + 8 (specjalista) + 4 (aktualna forma) = 16.5 pkt ✅
```

---

### 5. **Momentum (10%) - NOWY CZYNNIK** ✨

Wykrywa:
- **Serie zwycięstw** (3+ z rzędu): +5 pkt
- **Pewność siebie** (łatwość wygranych 2-0 vs trudne 2-1): +5 pkt

**Przykład:**
```
Zawodnik A: 
- Aktualna seria: 6 zwycięstw z rzędu ✅
- Ostatnie wygrane: 2-0, 2-0, 2-0 (łatwe) ✅
Bonus: +10 pkt

Zawodnik B:
- Aktualna seria: 0 (przegrał ostatni mecz)
- Ostatnie wygrane: 2-1, 2-1 (trudne)
Bonus: 0 pkt
```

---

## 📈 **OCZEKIWANE REZULTATY:**

### Scenariusz 1: **Mocne H2H + Świetna forma**
```
H2H: 3-0 (ostatnie 6 miesięcy) → +36 pkt
Forma: 9/10 W, seria 5 → +27 pkt  
Nawierzchnia: 85% vs 65% → +17 pkt
Momentum: seria 5, pewne wygrane → +10 pkt
─────────────────────────────────────
RAZEM: +90 pkt ✅ BARDZO WYSOKA PEWNOŚĆ
```

### Scenariusz 2: **Brak H2H, dobra forma na nawierzchni**
```
H2H: brak danych → 0 pkt
Forma: 7/10 vs 5/10 → +6 pkt
Nawierzchnia: 78% vs 68%, specjalista → +15 pkt
Momentum: seria 3 → +5 pkt
─────────────────────────────────────
RAZEM: +26 pkt ❌ NIE KWALIFIKUJE (próg 45)
```

### Scenariusz 3: **Stary ranking #10 vs #50 w złej formie**
```
V2 (z rankingiem):
Ranking: +20 pkt (znacząca różnica)
Forma: +3 pkt (obie słabe)
H2H: 0 pkt
Nawierzchnia: +2 pkt
────────────
RAZEM: +25 pkt → NIE KWALIFIKUJE, ale ranking sugerował przewagę ❌

V3 (bez rankingu):
Forma: -3 pkt (#10 gra gorzej niż #50!)
H2H: 0 pkt
Nawierzchnia: -5 pkt (#50 lepszy na hard)
Momentum: -5 pkt (#50 ma serię)
────────────
RAZEM: -13 pkt → Faworytem #50! ✅ PRAWIDŁOWA PREDYKCJA
```

---

## 🎯 **KLUCZOWE ULEPSZENIA:**

### ✅ **1. Waga czasowa w H2H**
- Mecz sprzed miesiąca jest **4x ważniejszy** niż sprzed 3 lat
- Obecna forma liczy się bardziej niż historia

### ✅ **2. Ranking nie ma wpływu**
- System nie patrzy na pozycję w tabeli
- Liczy się tylko **aktualna forma** i **wyniki**

### ✅ **3. Szczegółowa analiza formy**
- 10 meczów zamiast 5
- Trendy (poprawia się vs pogarsza)
- Jakość przeciwników
- Serie zwycięstw

### ✅ **4. Nawierzchnia jako kluczowy czynnik**
- 20% wagi (było 10%)
- Uwzględnia specjalizację
- Analizuje aktualną formę **NA TEJ** nawierzchni

### ✅ **5. Momentum i mental game**
- Wykrywa zawodników "w formie"
- Pewność siebie (łatwość wygranych)
- Serie zwycięstw

---

## 🚀 **IMPLEMENTACJA:**

### Krok 1: Utworzenie nowego pliku
```bash
tennis_advanced_v3.py  # Nowa wersja
```

### Krok 2: Integracja z scraperem
```python
# W livesport_h2h_scraper.py zmień:
from tennis_advanced import TennisMatchAnalyzer  # STARY
from tennis_advanced_v3 import TennisMatchAnalyzerV3  # NOWY
```

### Krok 3: Dostosowanie danych wejściowych
Scraper musi teraz zbierać:
- ✅ Daty meczów H2H (dla wagi czasowej)
- ✅ Ostatnie 10 meczów zamiast 5
- ✅ Rankingi przeciwników (dla jakości formy)
- ✅ Wyniki setowe (2-0, 2-1, dla momentum)
- ✅ Więcej danych o nawierzchni (ostatnie 5 meczów na danej nawierzchni)

---

## 📊 **OCZEKIWANA SKUTECZNOŚĆ:**

| Metryka | V2 (stary) | V3 (cel) |
|---------|-----------|----------|
| **Dokładność predykcji** | 61.5% | **75-80%** 🎯 |
| **Procent kwalifikowanych** | 7.5% | **5-8%** (tylko pewne) |
| **False positives** | Średnio | **Niski** |
| **Pewność high/very_high** | - | **>90% accuracy** |

---

## ⚠️ **WYMAGANIA DO SCRAPERA:**

Aby V3 działał optymalnie, scraper musi zbierać:

1. **H2H z datami:**
```python
h2h_matches = [
    {'date': '15.08.24', 'winner': 'player_a', 'score': '2-0'},
    {'date': '20.05.24', 'winner': 'player_a', 'score': '2-1'},
]
```

2. **Forma z rankingami przeciwników:**
```python
form_a = [
    {'result': 'W', 'date': '01.10.25', 'opponent_rank': 15, 'score': '2-0'},
    {'result': 'W', 'date': '28.09.25', 'opponent_rank': 22, 'score': '2-0'},
]
```

3. **Statystyki nawierzchni z aktualną formą:**
```python
surface_stats_a = {
    'hard': {
        'wins': 45,
        'total': 55,
        'win_rate': 0.82,
        'recent_form': ['W', 'W', 'W', 'L', 'W']  # Ostatnie 5 NA HARD
    }
}
```

---

## ✅ **WNIOSKI:**

1. ✅ **V3 ignoruje ranking** - focus na formę
2. ✅ **Waga czasowa w H2H** - nowsze mecze ważniejsze
3. ✅ **Szczegółowa analiza formy** - 10 meczów + trendy
4. ✅ **Nawierzchnia jako kluczowy czynnik** - 20% wagi
5. ✅ **Momentum** - wykrywa zawodników "w gazie"
6. ✅ **Wyższy próg** (45 pkt) - tylko pewne typy
7. ✅ **Poziomy pewności** - very_high, high, medium, low

---

## 🎯 **NASTĘPNE KROKI:**

1. ✅ Utworzenie `tennis_advanced_v3.py` - **GOTOWE**
2. ⏳ Modyfikacja scrapera aby zbierał dodatkowe dane
3. ⏳ Test na prawdziwych danych z Livesport
4. ⏳ Porównanie skuteczności V2 vs V3
5. ⏳ Fine-tuning progów i bonusów

---

**Data aktualizacji:** 2025-10-07  
**Wersja:** 3.0  
**Status:** ✅ GOTOWE DO TESTÓW


