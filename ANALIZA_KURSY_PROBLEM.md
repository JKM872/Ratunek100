# ❌ PROBLEM Z KURSAMI BUKMACHERSKIMI

## 🔍 Diagnoza problemu

### Przykłady "kursów" z danych:
```
Real Sociedad vs Sevilla: 24.1 vs 28.09
AC Milan vs Pisa: 24.1 vs 5.10
Power Dynamos vs Vipers: 24.1 vs 19.09
```

## ⚠️ TO SĄ DATY, NIE KURSY!

- `24.1` = **24 stycznia** (24.01)
- `28.09` = **28 września**
- `5.10` = **5 października**

## 🔧 Przyczyna:

W funkcji `extract_betting_odds_with_selenium` (linia 1043):
```python
odds_match = re.findall(r'\b(\d+\.\d{2})\b', text)
```

Ten regex wyciąga **WSZYSTKIE** liczby z formatem X.XX (dwie cyfry po przecinku), 
co obejmuje:
- ✅ Kursy: 1.85, 2.50, 3.40
- ❌ Daty: 24.10, 5.11, 28.09

## ✅ Rozwiązanie:

1. **Bardziej restrykcyjny filtr** - kursy są zazwyczaj między 1.01 a 20.00 (rzadko wyżej)
2. **Lepsze selektory** - szukać elementów oznaczonych jako "odds" lub "bookmaker"
3. **Sprawdzić strukturę HTML** - Livesport może mieć specjalne klasy dla kursów
4. **Osobna strona** - kursy mogą być na osobnej zakładce (nie na /h2h/)

## 📊 Statystyki z danych:

- Siatkówka: 2/3 meczów ma "kursy" (z czego przynajmniej część to daty)
- Piłka nożna: Wszystkie "kursy" to 24.1 (24 stycznia) + różne daty gości

## 🎯 Konieczne działania:

1. **Poprawić regex** - odfiltrować wartości >20.00
2. **Ulepszyć selektory** - szukać specyficznych elementów z kursami
3. **Sprawdzić czy kursy są na stronie H2H** - może trzeba ładować inną stronę
4. **Dodać walidację** - odrzucić podejrzane wartości


