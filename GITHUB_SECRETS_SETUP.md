# 🔐 GITHUB ACTIONS - SUPABASE SECRETS SETUP

## Krok 1: Idź do GitHub Secrets

Otwórz: **https://github.com/JKM872/Ratunek100/settings/secrets/actions**

Lub ręcznie:
1. GitHub.com → Twoje repo "Ratunek100"
2. Settings (góra)
3. Secrets and variables → Actions (lewy panel)
4. "New repository secret"

---

## Krok 2: Dodaj SUPABASE_URL

**Name:**
```
SUPABASE_URL
```

**Secret:**
```
https://bfslhqnxsgmdyptrqshj.supabase.co
```

Kliknij: **Add secret** ✅

---

## Krok 3: Dodaj SUPABASE_KEY

**Name:**
```
SUPABASE_KEY
```

**Secret:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmc2xocW54c2dtZHlwdHJxc2hqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2MDU3NTYsImV4cCI6MjA3ODE4MTc1Nn0.QMiCdK8L-UFjeTAT9a5sPzXo_A8azpZe3p4SnfM0Fi8
```

Kliknij: **Add secret** ✅

---

## Krok 4: Sprawdź czy działa

Idź: **https://github.com/JKM872/Ratunek100/actions**

1. Wybierz workflow (np. "Midnight Auto Scraping")
2. Kliknij **Run workflow**
3. Wybierz branch: **main**
4. Kliknij **Run workflow** (zielony przycisk)

---

## Krok 5: Monitoruj wykonanie

1. Workflow pojawi się na liście (żółty kółko = running)
2. Kliknij na workflow name
3. Kliknij na job name
4. Zobacz logi w czasie rzeczywistym

**Szukaj w logach:**
```
✅ Supabase client initialized
📤 SUPABASE: Sending matches directly to cloud database
✅ SUPABASE SYNC COMPLETE
```

---

## Krok 6: Weryfikacja danych

Po zakończeniu workflow:

1. **Supabase Dashboard:**
   - https://supabase.com/dashboard/project/bfslhqnxsgmdyptrqshj/editor
   - Table Editor → matches
   - Powinny być NOWE mecze od dzisiaj

2. **Heroku UI:**
   - https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/
   - Odśwież (Ctrl+F5)
   - Powinny pokazać się nowe mecze

3. **API Check:**
   ```bash
   curl https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/api/stats
   ```
   - `total_matches` powinno wzrosnąć

---

## ✅ CHECKLIST

- [ ] SUPABASE_URL dodany do GitHub secrets
- [ ] SUPABASE_KEY dodany do GitHub secrets
- [ ] Workflow uruchomiony ręcznie
- [ ] Workflow zakończył się sukcesem (zielony checkmark)
- [ ] Dane w Supabase (Table Editor)
- [ ] Dane w Heroku UI (odświeżone)
- [ ] API stats pokazuje nowe dane

---

## 🆘 TROUBLESHOOTING

### Problem: "Supabase not initialized"

**Logi:**
```
❌ Supabase initialization error: ...
```

**Rozwiązanie:**
1. Sprawdź czy secrets są poprawnie wpisane (bez spacji na końcu)
2. Sprawdź czy workflow ma `env:` block z secrets

---

### Problem: "duplicate key value violates unique constraint"

**To jest OK!** ✅

Znaczy że mecz już istnieje w bazie (duplikat). Supabase je pomija.

**W logach:**
```
🔄 Duplicates skipped: 5
```

---

### Problem: Workflow timeout po 6h

**Przyczyna:** Zbyt dużo meczów (>2000)

**Rozwiązanie:**
1. Ogranicz `--max-matches 500` w workflow
2. Uruchom 2x dziennie (rano i wieczór) zamiast 1x
3. Dodaj parallel processing `--parallel`

---

## 🚀 NASTĘPNE KROKI

Po weryfikacji że działa:

1. ✅ **Automatyczny scraping** - workflow będzie działał codziennie o 00:00 UTC
2. ✅ **Persistent data** - dane pozostają po Heroku redeploy
3. ✅ **No duplicates** - UNIQUE constraint zapobiega duplikatom
4. ✅ **Real-time UI** - UI pokazuje najnowsze dane z Supabase

---

## 📊 MONITORING

Regularnie sprawdzaj:

1. **GitHub Actions:**
   - https://github.com/JKM872/Ratunek100/actions
   - Czy workflows się wykonują bez błędów

2. **Supabase Logs:**
   - https://supabase.com/dashboard/project/bfslhqnxsgmdyptrqshj/logs
   - Sprawdź czy są błędy

3. **Heroku UI:**
   - https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/
   - Czy pokazuje aktualne dane

---

🎉 **Gotowe! Teraz masz w pełni automatyczny system z persistent cloud database!**
