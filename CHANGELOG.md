# Changelog

Wszystkie istotne zmiany w projekcie będą dokumentowane w tym pliku.

## [2.0.0] - 2025-10-05

### ✨ Dodano (Multi-Sport Edition)
- **Wsparcie dla 6 sportów**: piłka nożna, koszykówka, siatkówka, piłka ręczna, rugby, hokej
- **Automatyczne zbieranie linków** (`--mode auto`) z filtr owaniem po sportach
- **Filtrowanie po ligach** (`--leagues`) - możliwość zawężenia do konkretnych rozgrywek
- **Zaawansowany tryb zbierania** (`--advanced`) dla lepszej niezawodności
- **Predefined ligi** - słownik popularnych lig dla każdego sportu
- **Kolorowe logi** z emoji dla lepszej czytelności
- **Szczegółowe podsumowanie** po zakończeniu scrapowania
- **Adaptacyjny rate limiting** - inteligentne opóźnienia między requestami
- **Generator URLi** (`generate_urls.py`) - pomocniczy skrypt do tworzenia szablonów
- **Quick launch scripts** - `.bat` dla Windows, `.sh` dla Linux/Mac
- **Rozbudowana dokumentacja**:
  - README.md - pełna dokumentacja
  - QUICKSTART.md - szybki start w 5 minut
  - CHANGELOG.md - historia zmian
- **Przykładowe pliki**:
  - match_urls.txt - szablon z przykładami
  - .gitignore - ignorowane pliki

### 🔧 Zmieniono
- Ulepszone parsowanie H2H - więcej heurystyk
- Lepsza normalizacja URLi
- Wsparcie dla różnych formatów daty w URLach
- Ulepszona obsługa błędów z informacyjnymi komunikatami

### 🐛 Naprawiono
- Problem z duplikatami URLi
- Lepsza obsługa meczów bez danych H2H
- Encoding UTF-8-BOM dla poprawnego wyświetlania polskich znaków w Excel

---

## [1.0.0] - 2025-10-04 (Wersja bazowa)

### ✨ Dodano
- Podstawowy scraper dla Livesport.com
- Tryb `urls` - przetwarzanie z pliku
- Tryb `auto` - automatyczne zbieranie linków
- Parsowanie H2H (bezpośrednie spotkania)
- Filtrowanie meczów gdzie gospodarze wygrali ≥2/5 H2H
- Export do CSV
- Selenium WebDriver z Chrome
- Podstawowa dokumentacja

### 📋 Wymagania
- Python 3.9+
- selenium, beautifulsoup4, pandas, webdriver-manager
- Chrome + Chromedriver

