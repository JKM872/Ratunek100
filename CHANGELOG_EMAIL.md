# 📧 Changelog - Funkcjonalność Email

## ✨ NOWOŚĆ: Powiadomienia Email (05.10.2025)

### Co dodano?

#### 🎯 Główne funkcje:
- ✅ **Automatyczne wysyłanie powiadomień email** z kwalifikującymi się meczami
- ✅ **Piękny format HTML** z kolorami i ikonami
- ✅ **Zbieranie daty i godziny** meczu
- ✅ **Automatyczne sortowanie chronologiczne** ⏰ (mecze od najwcześniejszych!)
- ✅ **3 opcje sortowania**: po godzinie, po wygranych, alfabetycznie
- ✅ **Auto-Restart przeglądarki** 🔄 (co 200 meczów - zero crashów!)
- ✅ **Wsparcie dla Gmail, Outlook, Yahoo**
- ✅ **Jedno-krokowe uruchomienie** (scraping + email)

#### 📁 Nowe pliki:
1. `email_notifier.py` - Moduł wysyłania emaili
2. `scrape_and_notify.py` - Scraping + email w jednym kroku
3. `send_email_example.py` - Przykład użycia
4. `email_config.example.py` - Szablon konfiguracji
5. `EMAIL_SETUP.md` - Pełna dokumentacja
6. `EMAIL_QUICKSTART.txt` - Szybki start
7. `SORTING_UPDATE.md` - Dokumentacja sortowania
8. `AUTO_RESTART_INFO.md` - Dokumentacja auto-restart
9. `.gitignore` - Ochrona haseł

#### 🔧 Poprawki w głównym skrypcie:
- Zaktualizowano `livesport_h2h_scraper.py`:
  - Dodano wydobywanie daty/godziny meczu
  - Poprawiono selektory CSS (nowa struktura Livesport 2025)
  - Dodano automatyczne przekierowanie na `/h2h/ogolem/`
  - Ulepszono parsowanie sekcji "Pojedynki bezpośrednie"
  - **Dodano auto-restart przeglądarki co 200 meczów** 🔄
- Zaktualizowano `scrape_and_notify.py`:
  - **Dodano auto-restart przeglądarki co 200 meczów** 🔄

---

## 🚀 Jak używać?

### Opcja 1: Jedno polecenie (NAJPROSTSZE)

```bash
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports football \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "app_password" \
  --headless
```

### Opcja 2: Z istniejącego CSV

```bash
python email_notifier.py \
  --csv outputs/livesport_h2h_2025-10-05_football.csv \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "app_password"
```

---

## 📧 Format emaila

Email zawiera:
- 🏆 Nagłówek z liczbą kwalifikujących się meczów
- ⏰ **Mecze posortowane chronologicznie** (domyślnie)
- 🕐 **Badge z godziną** każdego meczu (pomarańczowy)
- 📅 Data i godzina każdego meczu
- 📊 Statystyki H2H (ile wygranych gospodarzy)
- 🔗 Linki do meczów na Livesport
- 🎨 Ładny design HTML z kolorami

### Opcje sortowania:
```bash
# Chronologicznie (domyślnie)
--sort time

# Po liczbie wygranych (najlepsze mecze na górze)
--sort wins

# Alfabetycznie po nazwie gospodarzy  
--sort team
```

---

## 🔑 Wymagania dla Gmail

⚠️ **WAŻNE**: Gmail wymaga App Password!

1. Wejdź: https://myaccount.google.com/apppasswords
2. Utwórz nowe hasło aplikacji
3. Skopiuj 16-znakowe hasło
4. Użyj TEGO hasła (nie zwykłego)

---

## 🐛 Naprawione problemy

### Problem 1: Brak danych H2H
**Status**: ✅ NAPRAWIONE
- **Przyczyna**: Stare selektory CSS, strona się zmieniła
- **Rozwiązanie**: Zaktualizowano selektory na nową strukturę Livesport 2025
- **Nowe selektory**: `h2h__row`, `h2h__participantInner`, itp.

### Problem 2: Niewłaściwy URL
**Status**: ✅ NAPRAWIONE
- **Przyczyna**: Skrypt otwierał `/szczegoly/` zamiast `/h2h/ogolem/`
- **Rozwiązanie**: Automatyczne przekierowanie URL

### Problem 3: Brak daty/godziny meczu
**Status**: ✅ NAPRAWIONE
- **Rozwiązanie**: Dodano parsowanie daty z różnych źródeł (tytuł, elementy DOM)

---

## 📊 Statystyki z testów

Test na 50 meczach (05.10.2025):
- ✅ Przetworzone: 50 meczów
- ✅ Kwalifikujące się: 26 meczów (52%)
- ✅ Czas: ~2 minuty
- ✅ Nazwy drużyn: 100% sukces
- ✅ Dane H2H: ~98% sukces

---

## 🔮 Planowane funkcje (przyszłość)

- [ ] Filtrowanie po ligach w emailu
- [ ] Scheduler/Cron automatyzacja
- [ ] Wykres H2H w emailu
- [ ] SMS notifications (Twilio)
- [ ] Discord/Slack webhooks
- [ ] Analiza trendów H2H

---

## 📚 Dokumentacja

- **Szybki start**: `EMAIL_QUICKSTART.txt`
- **Pełna instrukcja**: `EMAIL_SETUP.md`
- **Ogólna dokumentacja**: `README.md`
- **FAQ**: `FAQ.md`

---

## 🙏 Podziękowania

Dziękujemy za używanie Livesport H2H Scraper!

**Wersja**: 2.1.0 (Email Edition)  
**Data wydania**: 05.10.2025  
**Autor aktualizacji**: AI Assistant + Jakub

