# ⚡ QUICK START - Scraper → Aplikacja UI

## 5 minut do pełnej integracji! 🚀

---

## 📋 CO BĘDZIESZ POTRZEBOWAĆ

- [x] Konto GitHub (już masz ✅)
- [x] Konto Railway/Render (darmowe)
- [x] Node.js 16+ zainstalowany lokalnie (do testów)

---

## 🚀 KROK 1: DEPLOYMENT APLIKACJI (2 minuty)

### Railway (najszybsze):

1. **Wejdź:** https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. **Wybierz:** `Ratunek100`
4. **Root Directory:** `example_ui_app`
5. **Dodaj zmienną:**
   ```
   SCRAPER_API_KEY=tajny-klucz-12345
   ```
6. **Deploy!** ✅
7. **Skopiuj URL:** `https://twoja-app.up.railway.app`

---

## 🔑 KROK 2: GITHUB SECRETS (1 minuta)

1. **GitHub** → Twoje repo → **Settings** → **Secrets and variables** → **Actions**
2. **Dodaj 2 secrets:**

```
Name: APP_URL
Secret: https://twoja-app.up.railway.app

Name: APP_API_KEY
Secret: tajny-klucz-12345
```

⚠️ **WAŻNE:** Ten sam klucz co w Railway!

---

## ✅ KROK 3: TEST (2 minuty)

### Test 1: Health Check

```bash
curl https://twoja-app.up.railway.app/api/health
```

Oczekiwana odpowiedź:
```json
{"status": "ok", "message": "Aplikacja UI działa!"}
```

### Test 2: GitHub Actions (ręcznie)

1. **GitHub** → **Actions**
2. **Midnight Auto Scraping (All Sports)**
3. **Run workflow** → **Run workflow**
4. **Poczekaj 5 minut**
5. **Sprawdź logi** - powinieneś zobaczyć:

```
✅ Sukces! Status: 200
```

### Test 3: Sprawdź dane

```bash
curl https://twoja-app.up.railway.app/api/stats
```

Powinieneś zobaczyć zapisane mecze! 🎉

---

## 🎉 GOTOWE!

Teraz scraper będzie codziennie o północy:
- ✅ Scrapować mecze
- ✅ Wysyłać do Twojej aplikacji
- ✅ Zapisywać do bazy
- ✅ Wysyłać email

**Wszystko automatycznie!** 🚀

---

## 📚 WIĘCEJ INFO

- **Pełna instrukcja:** `INSTRUKCJA_WDROZENIA_KOMPLETNA.md`
- **Dokumentacja API:** `example_ui_app/README.md`
- **Troubleshooting:** `INSTRUKCJA_WDROZENIA_KOMPLETNA.md` → sekcja "Troubleshooting"

---

## 🐛 POMOC

**Problem?**

1. Sprawdź logi Railway: Dashboard → Logs
2. Sprawdź logi GitHub Actions
3. Test lokalnie: `cd example_ui_app && npm test`

---

**Pytania?** Sprawdź pełną instrukcję! 📖
