# 🏐 Volleyball H2H Scraper - GitHub Actions Edition

Automatyczny scraper meczów siatkówki z Livesport.com, działający 24/7 w chmurze GitHub.

## ✨ Co robi?

- 🔍 Scrapuje mecze siatkówki gdzie **gospodarze** wygrali ≥2/5 ostatnich H2H
- 📧 Wysyła email z wynikami
- ⏰ Działa automatycznie codziennie o 11:00
- ☁️ Nie wymaga laptopa (działa w GitHub Actions)

## 🚀 Quick Start

**Zobacz:** `GITHUB_QUICK_START.md`

1. Stwórz repo na GitHub
2. Upload plików
3. Dodaj secret EMAIL_PASSWORD
4. Gotowe!

## 📚 Dokumentacja

- **`GITHUB_QUICK_START.md`** - Start w 5 minut ⚡
- **`GITHUB_ACTIONS_SETUP.md`** - Pełna instrukcja 📖
- **`QUICKSTART.md`** - Uruchamianie lokalne

## 🎓 GitHub Student Pack

Z Student Pack masz:
- ✅ 3000 minut/miesiąc (zamiast 2000)
- ✅ 7 GB RAM
- ✅ Całkowicie za darmo
- ✅ Prywatne repozytoria

## 📊 Workflows

### **Daily Volleyball Scraping** (automatyczny)
- ⏰ Uruchamia się codziennie o 11:00
- 🏐 Scraping tylko volleyball
- 📧 Email z wynikami

### **All Sports Scraping** (ręczny)
- 🎯 Uruchamiasz kiedy chcesz
- 🏀 Wszystkie sporty: volleyball, basketball, handball
- 📅 Możesz wybrać datę

## 🔧 Wymagania

- Python 3.11+
- Chrome/Chromium (automatycznie instalowane w GitHub Actions)
- Gmail App Password (dla email)

## 💡 Przykłady użycia

### Lokalne uruchomienie
```bash
python scrape_and_notify.py \
  --date 2025-10-24 \
  --sports volleyball \
  --to twoj@email.com \
  --from-email twoj@email.com \
  --password "xxxx xxxx xxxx xxxx" \
  --headless
```

### GitHub Actions
1. Zakładka: **Actions**
2. Wybierz workflow
3. **Run workflow**

## 📁 Struktura

```
volleyball-scraper/
├── .github/
│   └── workflows/
│       ├── daily-scraping.yml       # Automatyczny (11:00)
│       └── all-sports-scraping.yml  # Ręczny
├── livesport_h2h_scraper.py        # Główny scraper
├── scrape_and_notify.py            # Automatyzacja + email
├── email_notifier.py               # Wysyłanie emaili
├── requirements.txt                # Zależności Python
├── .gitignore                      # Git ignore
├── GITHUB_QUICK_START.md           # Quick start
├── GITHUB_ACTIONS_SETUP.md         # Pełna instrukcja
└── README_GITHUB.md                # Ten plik
```

## ⚙️ Konfiguracja

### Zmień godzinę scrapingu
Edytuj: `.github/workflows/daily-scraping.yml`
```yaml
cron: '0 9 * * *'  # 11:00 PL (09:00 UTC)
```

### Dodaj więcej sportów
```yaml
--sports volleyball basketball handball football \
```

### Zmień email
```yaml
--to twoj.nowy@email.com \
```

## 📊 Monitoring

- **Actions** - historia uruchomień
- **Artifacts** - pobierz pliki CSV
- **Email** - automatyczne powiadomienia

## 🐛 Troubleshooting

**Email nie przychodzi?**
- Sprawdź SPAM
- Sprawdź logi w Actions
- Sprawdź czy EMAIL_PASSWORD jest dodany w Secrets

**Workflow nie uruchamia się?**
- Actions → Enable workflow
- Sprawdź czy repo ma aktywność (nie starsze niż 60 dni)

**Szczegóły:** `GITHUB_ACTIONS_SETUP.md`

## 📝 License

Do użytku osobistego. Szanuj Terms of Service Livesport.com.

## 🤝 Support

Pytania? Zobacz dokumentację:
- `GITHUB_QUICK_START.md` - szybki start
- `GITHUB_ACTIONS_SETUP.md` - pełna instrukcja
- `TROUBLESHOOTING.md` - rozwiązywanie problemów

---

**Działa 24/7 za darmo dzięki GitHub Student Pack! 🎓🚀**

